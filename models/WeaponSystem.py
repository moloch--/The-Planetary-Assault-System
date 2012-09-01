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
    ''' 
    Holds configuration information for remote agents
    '''

    name = Column(Unicode(64), unique=True, nullable=False)
    initialized = Column(Boolean, default=False, nullable=False)
    ssh_user = Column(Unicode(64), nullable=False)
    ssh_key = Column(Unicode(4096), nullable=False)
    ip_address = Column(Unicode(64), unique=True, nullable=False)
    ssh_port = Column(Integer, default=22, nullable=False)
    service_port = Column(Integer, default=31337, nullable=False)
    lm_capable = Column(Boolean, default=False, nullable=False)
    ntlm_capable = Column(Boolean, default=False, nullable=False)
    md5_capable = Column(Boolean, default=False, nullable=False)
    cpu_count = Column(Integer, default=1, nullable=False)
    gpu_count = Column(Integer, default=0, nullable=False)

    @classmethod
    def by_id(cls, weapon_id):
        ''' Return the WeaponSystem object whose id is 'weapon_id' '''
        return dbsession.query(cls).filter_by(id=weapon_id).first()

    @classmethod
    def by_uuid(cls, weapon_uuid):
        ''' Return the WeaponSystem object whose uuid is 'weapon_uuid' '''
        return dbsession.query(cls).filter_by(uuid=unicode(weapon_uuid)).first()

    @classmethod
    def get_all(cls):
        ''' Get all WeaponSystem objects that have been initialized '''
        return dbsession.query(cls).filter_by(initialized=True).all()

    @classmethod
    def get_uninitialized(cls):
        ''' Get all WeaponSystem objects that have not been initialized '''
        return dbsession.query(cls).filter_by(initialized=False).all()

    @classmethod
    def by_name(cls, weapon_name):
        ''' Return the WeaponSystem object whose name is 'weapon_name' '''
        return dbsession.query(cls).filter_by(name=unicode(weapon_name)).first()

    @classmethod
    def by_ip_address(cls, weapon_ip_address):
        ''' Return the WeaponSystem object whose ip_address is 'weapon_ip_address' '''
        return dbsession.query(cls).filter_by(ip_address=unicode(weapon_ip_address)).first()

    @classmethod
    def all_lm_capable(cls):
        ''' Return all the WeaponSystem objects that are lm capable '''
        return dbsession.query(cls).filter_by(lm_capable=True).all()

    @classmethod
    def all_ntlm_capable(cls):
        ''' Return all the WeaponSystem objects that are ntlm capable '''
        return dbsession.query(cls).filter_by(ntlm_capable=True).all()

    @classmethod
    def all_md5_capable(cls):
        ''' Return all the WeaponSystem objects that are md5 capable '''
        return dbsession.query(cls).filter_by(md5_capable=True).all()

    @classmethod
    def all_idle(cls):
        ''' Returns a list of systems that are initialized, online and not busy '''
        online_systems = filter(lambda weapon_system:
                                weapon_system.is_online() == True, cls.get_all())
        return filter(lambda weapon_system: weapon_system.is_busy() == False, online_systems)

    @classmethod
    def ready_md5_capable(cls):
        ''' Return all the WeaponSystem objects that are online, not busy and md5 capable '''
        online_systems = filter(lambda weapon_system:
                                weapon_system.is_online() == True, cls.all_md5_capable())
        return filter(lambda weapon_system: weapon_system.is_busy() == False, online_systems)

    @classmethod
    def ready_lm_capable(cls):
        ''' Return all the WeaponSystem objects that are online, not busy and lm capable '''
        online_systems = filter(lambda weapon_system:
                                weapon_system.is_online() == True, cls.all_lm_capable())
        return filter(lambda weapon_system: weapon_system.is_busy() == False, online_systems)

    @classmethod
    def ready_ntlm_capable(cls):
        ''' Return all the WeaponSystem objects that are online, not busy and ntlm capable '''
        online_systems = filter(lambda weapon_system:
                                weapon_system.is_online() == True, cls.all_ntlm_capable())
        return filter(lambda weapon_system: weapon_system.is_busy() == False, online_systems)

    @classmethod
    def ready_systems(cls, algo):
        ''' Pseudo strategy pattern returns ready systems based on algo '''
        ready_funcs = {
            "LM": cls.ready_lm_capable,
            "NTLM": cls.ready_ntlm_capable,
            "MD5": cls.ready_md5_capable,
        }
        return ready_funcs[algo]()

    def initialize(self, *args):
        ''' One time initialization, gathers system information '''
        success = False
        logging.info(
            "Preforming weapon system initialization, please wait ... ")
        ssh_keyfile = NamedTemporaryFile()
        ssh_keyfile.write(self.ssh_key)
        ssh_keyfile.seek(0)
        try:
            logging.info("Connectiong to remote ssh server at %s:%s" %
                         (self.ip_address, self.ssh_port))
            ssh_context = SshContext(self.ip_address,
                                     user=self.ssh_user, keyfile=ssh_keyfile.name)
            rpc_connection = rpyc.ssh_connect(ssh_context, self.service_port)
            capabilities = rpc_connection.root.exposed_get_capabilities()
            self.lm_capable = 'LM' in capabilities
            self.ntlm_capable = 'NTLM' in capabilities
            self.md5_capable = 'MD5' in capabilities
            self.cpu_count = rpc_connection.root.exposed_cpu_count()
            self.initialized = True
            dbsession.add(self)
            dbsession.flush()
            success = True
        except ValueError:
            logging.exception(
                "Failed to initialize weapon system, check parameters (ValueError)")
        except EOFError:
            logging.exception(
                "Failed to initialize weapon system, check parameters (EOF)")
        finally:
            ssh_keyfile.close() # TempFile is deleted upon .close()
            return success

    def is_online(self):
        ''' Checks if a system is online '''
        success = False
        try:
            ssh_keyfile = NamedTemporaryFile()
            ssh_keyfile.write(self.ssh_key)
            ssh_keyfile.seek(0)
            ssh_context = SshContext(self.ip_address,
                                     user=self.ssh_user, keyfile=ssh_keyfile.name)
            rpc_connection = rpyc.ssh_connect(ssh_context, self.service_port)
            success = rpc_connection.root.exposed_ping() == "PONG"
        except:
            logging.exception(
                "Connection to remote weapon system failed, check parameters")
        finally:
            ssh_keyfile.close()
        return success

    def is_busy(self):
        ''' Checks to see if a remote system is busy returns bool or None '''
        try:
            ssh_keyfile = NamedTemporaryFile()
            ssh_keyfile.write(self.ssh_key)
            ssh_keyfile.seek(0)
            ssh_context = SshContext(self.ip_address,
                                     user=self.ssh_user, keyfile=ssh_keyfile.name)
            rpc_connection = rpyc.ssh_connect(ssh_context, self.service_port)
            busy = rpc_connection.root.exposed_is_busy()
        except:
            logging.exception(
                "Connection to remote weapon system failed, check parameters")
        finally:
            ssh_keyfile.close()
        return busy
