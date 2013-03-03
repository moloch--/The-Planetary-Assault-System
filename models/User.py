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


import bcrypt

from os import urandom
from base64 import b64encode
from sqlalchemy import Column, ForeignKey
from sqlalchemy.orm import synonym, relationship, backref
from sqlalchemy.types import Unicode, Integer, Boolean, String
from string import ascii_letters, digits
from models import dbsession, Job, Permission
from models.BaseObject import BaseObject


### Constants
ADMIN_PERMISSION = u'admin'


class User(BaseObject):
    '''
    User class used for authentication/autorization
    '''

    _username = Column(Unicode(64), unique=True, nullable=False)
    username = synonym('_username', descriptor=property(
        lambda self: self._username,
        lambda self, username: setattr(self, '_username',
            self.__class__._filter_string(username)
        )
    ))
    _locked = Column(Boolean, default=True)
    jobs = relationship("Job", 
        backref=backref("User", lazy="joined"), cascade="all, delete-orphan"
    )
    permissions = relationship("Permission", 
        backref=backref("User", lazy="joined"), cascade="all, delete-orphan"
    )
    salt = Column(String(32), 
        unique=True, 
        nullable=False, 
        default=lambda: bcrypt.gensalt(16)
    )
    _password = Column('password', Unicode(64))
    password = synonym('_password', descriptor=property(
        lambda self: self._password,
        lambda self, password: setattr(self, '_password',
            self.__class__._hash_password(password, self.salt)
        )
    ))

    @classmethod
    def by_id(cls, user_id):
        ''' Return the user object whose user id is user_id '''
        return dbsession.query(cls).filter_by(id=user_id).first()

    @classmethod
    def by_uuid(cls, user_uuid):
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
    def by_username(cls, user_name):
        ''' Return the user object whose user name is 'user_name' '''
        return dbsession.query(cls).filter_by(username=unicode(user_name)).first()

    @classmethod
    def _filter_string(cls, string, extra_chars=""):
        ''' Remove any non-white listed chars from a string '''
        char_white_list = ascii_letters + digits + extra_chars
        return filter(lambda char: char in char_white_list, string)

    @classmethod
    def _hash_password(cls, password, salt):
        ''' BCrypt; return unicode string '''
        hashed = bcrypt.hashpw(password, salt)
        return unicode(hashed)

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

    @property
    def locked(self):
        ''' 
        Determines if an admin has locked an account, accounts with
        administrative permissions cannot be locked.
        '''
        if self.has_permission(ADMIN_PERMISSION):
            return False  # Admin accounts cannot be locked
        else:
            return self._locked

    @locked.setter
    def locked(self, value):
        ''' Setter method for _lock '''
        assert isinstance(value, bool)
        if not self.has_permission(ADMIN_PERMISSION):
            self._locked = value

    def has_permission(self, permission):
        ''' Return True if 'permission' is in permissions_names '''
        return True if permission in self.permissions_names else False

    def validate_password(self, attempt):
        ''' Check the password against existing credentials '''
        return self.password == self._hash_password(attempt, self.salt)

    def __repr__(self):
        return '<User - user_name: %s, jobs: %d>' % (self.user_name, len(self.jobs))

    def __str__(self):
        return self.username
