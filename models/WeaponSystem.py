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
from sqlalchemy.types import Unicode, Boolean, Integer
from models import dbsession
from models.BaseObject import BaseObject

class WeaponSystem(BaseObject):

    name = Column(Unicode(64), unique = True, nullable = False)
    ip_address = Column(Unicode(64), unique = True, nullable = False)
    port = Column(Integer, default = 31337, nullable = False)
    busy = Column(Boolean, default = False, nullable = False)
    lm_capable = Column(Boolean, default = False, nullable = False)
    ntlm_capable = Column(Boolean, default = False, nullable = False)
    md5_capable = Column(Boolean, default = False, nullable = False)

    @classmethod
    def by_id(cls, weapon_id):
        """ Return the WeaponSystem object whose id is 'weapon_id' """
        return dbsession.query(cls).filter_by(id = weapon_id).first()

    @classmethod
    def by_name(cls, weapon_name):
        """ Return the WeaponSystem object whose name is 'weapon_name' """
        return dbsession.query(cls).filter_by(name= weapon_name).first()

    @classmethod
    def by_ip_address(cls, weapon_ip_address):
        """ Return the WeaponSystem object whose ip_address is 'weapon_ip_address' """
        return dbsession.query(cls).filter_by(ip_address = weapon_ip_address).first()

    @classmethod
    def all_lm_capable(cls):
        """ Return all the WeaponSystem objects that are lm capable """
        return dbsession.query(cls).filter_by(lm_capable = True).all()

    @classmethod
    def all_ntlm_capable(cls):
        """ Return all the WeaponSystem objects that are ntlm capable """
        return dbsession.query(cls).filter_by(ntlm_capable = True).all()

    @classmethod
    def all_md5_capable(cls):
        """ Return all the WeaponSystem objects that are md5 capable """
        return dbsession.query(cls).filter_by(md5_capable = True).all()
