# -*- coding: utf-8 -*-
'''
Created on June 30, 2012

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


import os
import thread
import logging
import ConfigParser
import RainbowCrack

from models import dbsession
from models import Job, User
from threading import Lock
from datetime import datetime
from libs.Singleton import Singleton
from libs.ConfigManager import ConfigManager

@Singleton
class Dispatch(object):

    def __init__(self):
        self.__config__()
        self.is_busy = False
        self.mutex = Lock()

    def __config__(self):
        self.config = ConfigManager.Instance()

    def start(self, job_id):
        ''' Mostly thread safe, starts a job or adds it to the queue '''
        self.mutex.acquire()
        if not self.is_busy:
            self.is_busy = True
            job = Job.by_id(job_id)
            self.current_job_name = str(job)
            self.mutex.release()
            self.__dispatch__(job)
        else:
            self.mutex.release()

    def __dispatch__(self, job):
        ''' Spawns a seperate cracking thread '''
        thread.start_new_thread(self.__crack__, (job,))

    def __crack__(self, job, weapon_system):
        ''' 
        Does the actual password cracking, before calling this function you should
        ensure the weapon system is online and not busy
        '''
        user = User.by_id(job.user_id)
        if user == None or job == None or len(job) == 0:
            logging.error("Invalid job passed to dispatcher.")
        else:
            algo = job.hashes[0].algorithm
            job.started = datetime.now()
            try:
                ssh_keyfile = NamedTemporaryFile()
                ssh_keyfile.write(weapon_system.ssh_key)
                ssh_keyfile.seek(0)
                ssh_context = SshContext(weapon_system.ip_address, user = weapon_system.ssh_user, keyfile = ssh_keyfile.name)
                rpc_connection = rpyc.ssh_connect(ssh_context, self.service_port)
                hashes = job.to_list()
                results = rpc_connection.root.exposed_crack_list(job.id, job.to_list(), algo, weapon_system.cpu_count)
            except:
                logging.exception("Connection to remote weapon system failed, check parameters")
            finally:
                ssh_keyfile.close()
            job.save_results(results)
            job.completed = True
            job.finished = datetime.now()
            dbsession.add(job)
            dbsession.flush()
            self.__next__()

    def __next__(self):
        ''' Determines what to do next depending on queue state '''
        if 0 < Job.qsize():
            logging.info("Popping a job off the queue, %d job(s) remain." % Job.qsize())
            next_job = Job.pop()
            self.__dispatch__(next_job)
        else:
            logging.info("No jobs remain in queue, cracking thread is stopping.")
            self.mutex.acquire()
            self.current_job_name = None
            self.is_busy = False
            self.mutex.release()
