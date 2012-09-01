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


from sqlalchemy import Column
from sqlalchemy.types import Unicode, Integer
from models.BaseObject import BaseObject
from models import dbsession

class Algorithm(BaseObject):
    '''
    Holds information about an algorithm, typically
    this is a read-only object but that is not enforced
    '''

    algorithm_name = Column(Unicode(64), nullable=False)
    length = Column(Integer, nullable=False)
    chars = Column(Unicode(64), nullable=False)

    @classmethod
    def all(cls):
        ''' Return a list of all algorithms '''
        return dbsession.query(cls).all()

    @classmethod
    def all_names(cls):
        ''' Returns a list of all algorithm names '''
        return [algo.name for algo in cls.all()]

    @classmethod
    def by_id(cls, algo_id):
        ''' Return the algorithm object whose user id is 'algo_id' '''
        return dbsession.query(cls).filter_by(id=algo_id).first()

    @classmethod
    def by_uuid(cls, uuid):
        ''' Return the algorithm object whose user uuid is 'uuid' '''
        return dbsession.query(cls).filter_by(uuid=unicode(uuid)).first()

    @classmethod
    def by_name(cls, name):
        ''' Return a algorithm object based on name '''
        return dbsession.query(cls).filter_by(algorithm_name=name).first()

    def __len__(self):
        return self.length

    def __str__(self):
        return self.algorithm_name