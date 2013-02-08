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


import logging

from sqlalchemy import Column, ForeignKey, and_
from sqlalchemy.orm import synonym, relationship, backref
from sqlalchemy.types import Unicode, Integer, Boolean, DateTime
from libs.Memcache import MemoryCache
from models import dbsession, PasswordHash, Algorithm
from models.BaseObject import BaseObject
from string import ascii_letters, digits


class Job(BaseObject):
    '''
    Cracking job, holds refs to all the PasswordHash objects
    '''

    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    _job_name = Column(Unicode(64), unique=True, nullable=False)
    job_name = synonym('_job_name', descriptor=property(
        lambda self: self._job_name,
        lambda self, job_name: setattr(self, '_job_name',
                                       self.__class__._filter_string(job_name, "-_ "))
    ))
    # NOT_STARTED / IN_PROGRESS / COMPLETED
    status = Column(Unicode(64), default=u"NOT_STARTED", nullable=False)
    priority = Column(Integer, default=1, nullable=False)
    completed = Column(Boolean, default=False, nullable=False)
    hashes = relationship("PasswordHash", backref=backref(
        "Job", lazy="joined"), cascade="all, delete-orphan")
    algorithm_id = Column(Integer, ForeignKey('algorithm.id'), nullable=False)
    started = Column(DateTime)
    finished = Column(DateTime)

    @classmethod
    def by_id(cls, job_id):
        ''' Return the job object whose user id is 'job_id' '''
        return dbsession.query(cls).filter_by(id=job_id).first()

    @classmethod
    def by_uuid(cls, job_uuid):
        ''' Return the job object whose user uuid is 'job_uuid' '''
        return dbsession.query(cls).filter_by(uuid=unicode(job_uuid)).first()

    @classmethod
    def by_job_name(cls, job_name):
        ''' Return the job object whose user name is 'job_name' '''
        return dbsession.query(cls).filter_by(job_name=unicode(job_name)).first()

    @classmethod
    def qsize(cls):
        ''' Returns the number of incompelte jobs left in the data base '''
        return dbsession.query(cls).filter_by(status=u"NOT_STARTED").count()

    @classmethod
    def queue(cls):
        ''' Pop a job off the "queue" or return None if not jobs remain '''
        return dbsession.query(cls).filter_by(status=u"NOT_STARTED").order_by(cls.created).all()

    @classmethod
    def _filter_string(cls, string, extra_chars=""):
        char_white_list = ascii_letters + digits + extra_chars
        return filter(lambda char: char in char_white_list, string)

    @property
    def algorithm(self):
        ''' Returns an algorithm object based on self.algorithm_id '''
        return Algorithm.by_id(self.algorithm_id)

    def save_results(self, results):
        ''' Save the results of the cracking session to the database '''
        for password in self.hashes:
            try:
                if results[password.hexdigest] != "<Not Found>":
                    password.preimage = unicode(results[password.hexdigest])
                    dbsession.add(password)
            except KeyError:
                logging.error("A database hash is missing from the result set (%s)" % (
                    password.hexdigest,
                ))
        dbsession.flush()

    def to_list(self):
        ''' Returns all hash digests as a Python list '''
        return [hsh.hexdigest for hsh in self.hashes]

    def __len__(self):
        ''' Returns the number of hashes in the job '''
        return len(self.hashes)

    def __str__(self):
        return self.job_name

    def __repr__(self):
        return "<(%d) %s: hashes(%d), completed(%s)>" % (self.id, self.name, len(self), str(self.completed))
