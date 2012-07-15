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


import rpyc
import logging

from sqlalchemy import Column
from sqlalchemy.orm import synonym
from sqlalchemy.types import Unicode, Boolean, Integer
from models import dbsession
from models.BaseObject import BaseObject
from rpyc.utils.ssh import SshContext
from tempfile import NamedTemporaryFile

class WeaponSystem(BaseObject):
    ''' Holds configuration information for remote agents '''

    name = Column(Unicode(64), unique = True, nullable = False)
    initialized = Column(Boolean, default = False, nullable = False)
    ssh_user = Column(Unicode(64), nullable = False)
    ssh_key = Column(Unicode(4096), nullable = False)
    ip_address = Column(Unicode(64), unique = True, nullable = False)
    ssh_port = Column(Integer, default = 22, nullable = False)
    service_port = Column(Integer, default = 31337, nullable = False)
    busy = Column(Boolean, default = False, nullable = False)
    lm_capable = Column(Boolean, default = False, nullable = False)
    ntlm_capable = Column(Boolean, default = False, nullable = False)
    md5_capable = Column(Boolean, default = False, nullable = False)
    cpu_count = Column(Integer, default = 1, nullable = False)

    @classmethod
    def by_id(cls, weapon_id):
        """ Return the WeaponSystem object whose id is 'weapon_id' """
        return dbsession.query(cls).filter_by(id = weapon_id).first()

    @classmethod
    def by_uuid(cls, weapon_uuid):
        """ Return the WeaponSystem object whose uuid is 'weapon_uuid' """
        return dbsession.query(cls).filter_by(uuid = unicode(weapon_uuid)).first()

    @classmethod
    def get_all(cls):
        """ Get all WeaponSystem objects """
        return dbsession.query(cls).all()

    @classmethod
    def by_name(cls, weapon_name):
        """ Return the WeaponSystem object whose name is 'weapon_name' """
        return dbsession.query(cls).filter_by(name = unicode(weapon_name)).first()

    @classmethod
    def by_ip_address(cls, weapon_ip_address):
        """ Return the WeaponSystem object whose ip_address is 'weapon_ip_address' """
        return dbsession.query(cls).filter_by(ip_address = unicode(weapon_ip_address)).first()

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

    @property
    def online(self):
        ''' Checks if a system is online '''
        success = False
        try:
            ssh_keyfile = NamedTemporaryFile()
            ssh_keyfile.write(self.ssh_key)
            ssh_keyfile.seek(0)
            ssh_context = SshContext(self.ip_address, user = self.ssh_user, keyfile = ssh_keyfile.name)
            rpc_connection = rpyc.ssh_connect(ssh_context, self.service_port)
            success = rpc_connection.root.exposed_ping() == "PONG"
        except:
            logging.exception("Connection to remote weapon system failed, check parameters")
        finally:
            ssh_keyfile.close()
        return success

    @property
    def is_busy(self):
        return self.busy

    def initialize(self, *args):
        ''' One time initialization '''
        logging.info("Preforming weapon system initialization, please wait ... ")
        ssh_keyfile = NamedTemporaryFile()
        ssh_keyfile.write(self.ssh_key)
        ssh_keyfile.seek(0)
        try:
            logging.info("Connectiong to remote ssh server at %s:%s" % (self.ip_address, self.ssh_port))
            ssh_context = SshContext(self.ip_address, user = self.ssh_user, keyfile = ssh_keyfile.name)
            rpc_connection = rpyc.ssh_connect(ssh_context, self.service_port)
            capabilities = rpc_connection.root.exposed_get_capabilities()
            self.lm_capable = 'LM' in capabilities
            self.ntlm_capable = 'NTLM' in capabilities
            self.md5_capable = 'MD5' in capabilities
            self.cpu_count = rpc_connection.root.exposed_cpu_count()
            self.initialized = True
            dbsession.add(self)
            dbsession.flush()
        except ValueError:
            logging.info("Failed to initialize weapon system, check parameters")
        finally:
            ssh_keyfile.close()