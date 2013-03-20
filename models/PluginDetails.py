# -*- coding: utf-8 -*-
'''
Created on Mar 12, 2012

@author: moloch

    Copyright [2012]

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


from sqlalchemy import Column, ForeignKey
from sqlalchemy.orm import synonym, relationship
from sqlalchemy.types import Unicode, Boolean, Integer
from models import dbsession
from models.BaseObject import BaseObject


class PluginDetails(BaseObject):

    name = Column(Unicode(32), nullable=False)
    author = Column(Unicode(32))
    website = Column(Unicode(256))
    description = Column(Unicode(1024))
    copyright = Column(Unicode(32))
    precomputation = Column(Boolean, nullable=False)
    algorithm_id = Column(Integer, ForeignKey('algorithm.id'), nullable=False)

    @classmethod
    def by_id(cls, pid):
        ''' Return the object with an given id '''
        return dbsession.query(cls).filter_by(id=pid).first()

    @classmethod
    def by_uuid(cls, puuid):
        ''' Return the object with a given uuid '''
        return dbsession.query(cls).filter_by(uuid=unicode(puuid)).first()

    @classmethod
    def by_name(cls, pname):
        ''' Return object with a given name '''
        return dbsession.query(cls).filter_by(name=unicode(pname)).first()

    @classmethod
    def get_all(cls):
        ''' Get all WeaponSystem objects that have been initialized '''
        return dbsession.query(cls).all()

    @classmethod
    def get_precomputation_plugins(cls):
        ''' Get all WeaponSystem objects that have been initialized '''
        return dbsession.query(cls).filter_by(precomputation=True).all()

    @classmethod
    def get_computation_plugins(cls):
        ''' Get all WeaponSystem objects that have been initialized '''
        return dbsession.query(cls).filter_by(precomputation=False).all()