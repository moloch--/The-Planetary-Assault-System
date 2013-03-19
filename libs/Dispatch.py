# -*- coding: utf-8 -*-
'''
Created on June 30, 2012

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


import rpyc
import thread
import logging
import ConfigParser

from threading import Lock
from datetime import datetime
from tempfile import NamedTemporaryFile
from rpyc.utils.ssh import SshContext
from libs.Singleton import Singleton
from libs.ConfigManager import ConfigManager
from models import dbsession, Job, User, WeaponSystem, Algorithm


@Singleton
class Dispatch(object):
    ''' Dispatcher class, handles queue and RPC calls '''

    def __init__(self):
        self.__config__()
        self.mutex = Lock()

    def __config__(self):
        self.config = ConfigManager.Instance()

    def refresh(self):
        ''' Non-blocking call to check the queue for new jobs '''
        thread.start_new_thread(self.__next__, (None,))

    def __queue__(self):
        ''' Starts a job or leaves it in the queue (thread safe) '''
        logging.debug("Attempting to acquire queue mutex ...")
        self.mutex.acquire()
        logging.debug("Successfully acquired queue mutex.")
        queue = list(Job.queue())  # Create a copy of the queue
        for job in queue:
            logging.info("Dispatching job: %s" % job.job_name)
            if len(job) == 0:
                job.status = u"COMPLETED"
                dbsession.add(job)
                dbsession.flush()
            else:
                algo = Algorithm.by_id(job.algorithm_id)
                weapon_systems = WeaponSystem.system_ready(algo)
                if weapon_systems is not None and 0 < len(weapon_systems):
                    logging.info("Weapon systems available: %d" % (
                        len(weapon_systems),
                    ))
                    thread.start_new_thread(
                        self.__crack__, 
                        (job, weapon_systems[0],)
                    )
                else:
                    logging.info("No available weapon systems at this time.")
        self.mutex.release()

    def __crack__(self, job, weapon_system):
        '''
        Does the actual password cracking, before calling this function you should
        ensure the weapon system is online and not busy
        '''
        results = None
        user = User.by_id(job.user_id)
        if user is None:
            logging.error("Invalid job passed to dispatcher (no user with id %d)." % (
                job.user_id,
            ))
        elif job == None:
            logging.error("Invalid job passed to dispatcher (job is None).")
        else:
            job.started = datetime.now()
            algorithm = Algorithm.by_id(job.algorithm_id)
            try:
                ssh_keyfile = NamedTemporaryFile()
                ssh_keyfile.write(weapon_system.ssh_key)
                ssh_keyfile.seek(0)
                ssh_context = SshContext(
                    weapon_system.ip_address,
                    user=weapon_system.ssh_user, 
                    keyfile=ssh_keyfile.name,
                )
                rpc_connection = rpyc.ssh_connect(
                    ssh_context, 
                    weapon_system.service_port,
                )
                hashes = job.to_list()
                logging.info("Sending %s job to %s for cracking." % (
                    job.job_name, 
                    weapon_system.weapon_system_name,
                ))
                job.status = u"IN_PROGRESS"
                dbsession.add(job)
                dbsession.flush()
                results = rpc_connection.root.exposed_crack_list(
                    job.id, 
                    job.to_list(), 
                    algorithm.algorithm_name,
                )
            except:
                logging.exception("Connection to remote weapon system failed, check parameters.")
            finally:
                ssh_keyfile.close()
            if results is not None:
                job.save_results(results)
            else:
                logging.warn("No results returned from weapon system.")
            job.status = u"COMPLETED"
            job.finished = datetime.now()
            dbsession.add(job)
            dbsession.flush()
            self.__next__()

    def __next__(self, *args, **kwargs):
        ''' Called when a weapon system completes a job '''
        if 0 < Job.qsize():
            self.__queue__()
