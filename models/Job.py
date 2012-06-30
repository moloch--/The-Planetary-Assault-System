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

from sqlalchemy import Column, ForeignKey
from sqlalchemy.orm import synonym, relationship, backref
from sqlalchemy.types import Unicode, Integer, Boolean, DateTime
from models import dbsession
from models.PasswordHash import PasswordHash
from models.BaseObject import BaseObject

class Job(BaseObject):

    user_id = Column(Integer, ForeignKey('user.id'), nullable = False)
    name = Column(Unicode(64), nullable = False)
    priority = Column(Integer, default = 1,  nullable = False)
    completed = Column(Boolean, default = False, nullable = False)
    hashes = relationship("PasswordHash", backref = backref("Job", lazy = "joined"), cascade = "all, delete-orphan")
    started = Column(DateTime)
    finished = Column(DateTime)

    @classmethod
    def by_id(cls, job_id):
        """ Return the user object whose user id is ``job_id`` """
        return dbsession.query(cls).filter_by(id = job_id).first()
    
    @classmethod
    def by_job_name(cls, job_name):
        """ Return the user object whose user name is ``user_name`` """
        return dbsession.query(cls).filter_by(name = unicode(job_name)).first()

    @classmethod
    def pop(cls):
        ''' Pop a job off the "queue" or return None if not jobs remain '''
        return dbsession.query(cls).filter_by(completed = False).order_by(created).first()

    @property
    def solved_hashes(self):
        return filter(lambda password_hash: password_hash.sovled == True, self.hashes)

    @property
    def unsolved_hashes(self):
        return filter(lambda password_hash: password_hash.sovled == False, self.hashes)

    def __len__(self):
        return len(self.hashes)