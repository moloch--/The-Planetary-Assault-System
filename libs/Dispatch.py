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
        self.isBusy = False
        self.mutex = Lock()

    def __config__(self):
        self.config = ConfigManager.Instance()

    def start(self, job_id):
        ''' Thread safe, starts a job or adds it to the queue '''
        self.mutex.acquire()
        if not self.isBusy:
            self.isBusy = True
            self.mutex.release()
            self.__dispatch__(job_id)
        else:
            self.mutex.release()

    def __dispatch__(self, job_id):
        ''' Spawns a seperate cracking thread '''
        thread.start_new_thread(self.__crack__, (job_id,))

    def __crack__(self, job_id):
        ''' Does the actual password cracking '''
        job = Job.by_id(job_id)
        user = User.by_id(job.user_id)
        if user == None or job == None:
            logging.error("Invalid job passed to dispatcher.")
            raise ValueError
        algo = job.hashes[0].algorithm
        tables_path = self.config.rainbow_tables[algo]
        logging.info("Cracking %d %s hashes for %s" % (len(job.hashes), algo, user.user_name))
        job.started = datetime.now()
        results = RainbowCrack.crack(len(job), job.to_list(), tables_path, maxThreads = self.config.max_threads)
        job.save_results(results)
        job.completed = True
        job.finished = datetime.now()
        dbsession.add(job)
        dbsession.flush()
        if 0 < Job.qsize():
            logging.info("Popping job off queue, %d job(s) remain.")
            next_job = Job.pop()
            self.__dispatch__(next_job.id)
        else:
            logging.info("No jobs remain in queue, cracking thread is stopping.")
            self.mutex.acquire()
            self.isBusy = False
            self.mutex.release()
