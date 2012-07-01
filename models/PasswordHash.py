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
from sqlalchemy.types import Unicode, Integer, Boolean
from models import dbsession
from models.BaseObject import BaseObject

class PasswordHash(BaseObject):

    job_id = Column(Integer, ForeignKey('job.id'), nullable = False)
    algorithm = Column(Unicode(16), nullable = False)
    digest = Column(Unicode(128), nullable = False)
    solved = Column(Boolean, default = False, nullable = False)
    plain_text = Column(Unicode(64))

    @classmethod
    def by_id(cls, hash_id):
        """ Return the PasswordHash object whose user id is ``hash_id`` """
        return dbsession.query(cls).filter_by(id = hash_id).first()

    @classmethod
    def by_digest(cls, digest):
        """ Return the PasswordHash object whose user id is ``hash_id`` """
        return dbsession.query(cls).filter_by(digest = digest).all()