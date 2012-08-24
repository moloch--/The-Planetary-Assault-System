# -*- coding: utf-8 -*-
'''
Created on Mar 12, 2012

@author: moloch

    Copyright [2012] [Redacted Labs]

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

        http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.
'''


from os import urandom
from base64 import b64encode
from hashlib import sha256
from sqlalchemy import Column, ForeignKey
from sqlalchemy.orm import synonym, relationship, backref
from sqlalchemy.types import Unicode, Integer, Boolean
from string import ascii_letters, digits
from models import dbsession
from models.Job import Job
from models.Permission import Permission
from models.BaseObject import BaseObject


def gen_salt():
    ''' Generate a 24-byte random salt '''
    return unicode(b64encode(urandom(24)))


class User(BaseObject):
    ''' User definition '''

    _user_name = Column(Unicode(64), unique=True, nullable=False)
    user_name = synonym('_user_name', descriptor=property(
        lambda self: self._user_name,
        lambda self, user_name: setattr(self, '_user_name',
                                        self.__class__._filter_string(user_name, ""))
    ))
    approved = Column(Boolean, default=False)
    jobs = relationship("Job", backref=backref(
        "User", lazy="joined"), cascade="all, delete-orphan")
    permissions = relationship("Permission", backref=backref(
        "User", lazy="joined"), cascade="all, delete-orphan")
    salt = Column(
        Unicode(32), unique=True, nullable=False, default=gen_salt)
    _password = Column('password', Unicode(64))
    password = synonym('_password', descriptor=property(
        lambda self: self._password,
        lambda self, password: setattr(self, '_password',
                                       self.__class__._hash_password(password, self.salt))
    ))

    @classmethod
    def by_id(cls, user_id):
        ''' Return the user object whose user id is user_id '''
        return dbsession.query(cls).filter_by(id=user_id).first()

    @classmethod
    def by_id(cls, user_uuid):
        ''' Return the user object whose user uuid is user_uuid '''
        return dbsession.query(cls).filter_by(uuid=unicode(user_uuid)).first()

    @classmethod
    def get_unapproved(cls):
        ''' Return all unapproved user objects '''
        return dbsession.query(cls).filter_by(approved=False).all()

    @classmethod
    def get_approved(cls):
        ''' Return all approved user objects '''
        return dbsession.query(cls).filter_by(approved=True).all()

    @classmethod
    def all(cls):
        ''' Return all non-admin user objects '''
        return dbsession.query(cls).all()

    @classmethod
    def all_users(cls):
        ''' Return all non-admin user objects '''
        return filter(lambda user: user.has_permission('admin') == False, cls.all())


    @classmethod
    def by_user_name(cls, user_name):
        ''' Return the user object whose user name is 'user_name' '''
        return dbsession.query(cls).filter_by(user_name=unicode(user_name)).first()

    @classmethod
    def _filter_string(cls, string, extra_chars=""):
        ''' Remove any non-white listed chars from a string '''
        char_white_list = ascii_letters + digits + extra_chars
        return filter(lambda char: char in char_white_list, string)

    @classmethod
    def _hash_password(cls, password, salt):
        '''
        Hashes the password using 25,001 rounds of salted SHA-256, come at me bro.
        This function will always return a unicode string, but can take an arg of
        any type not just ascii strings, the salt will always be unicode
        '''
        sha = sha256()
        sha.update(password + salt)
        for count in range(0, 25000):
            sha.update(sha.hexdigest() + str(count))
        return unicode(sha.hexdigest())

    @property
    def queued_jobs(self):
        ''' Jobs owned by the user that have not been completed '''
        return filter(lambda job: (job.status != u"COMPLETED"), self.jobs)

    @property
    def completed_jobs(self):
        ''' Jobs owned by the user that have been completed '''
        return filter(lambda job: (job.status == u"COMPLETED"), self.jobs)

    @property
    def permissions(self):
        ''' Return a list with all permissions granted to the user '''
        return dbsession.query(Permission).filter_by(user_id=self.id)

    @property
    def permissions_names(self):
        ''' Return a list with all permissions names granted to the user '''
        return [permission.permission_name for permission in self.permissions]

    def has_permission(self, permission):
        ''' Return True if 'permission' is in permissions_names '''
        return True if permission in self.permissions_names else False

    def validate_password(self, attempt):
        ''' Check the password against existing credentials '''
        return self.password == self._hash_password(attempt, self.salt)

    def __repr__(self):
        return ('<User - user_name: %s>' % (self.user_name,)).encode('utf-8', 'ignore')
