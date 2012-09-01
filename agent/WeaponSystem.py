#!/usr/bin/env python
'''
Created on June 23, 2012

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
import platform
import ConfigParser

from sys import argv
from threading import Lock
from os import path, sysconf, _exit
from multiprocessing import cpu_count

### Detect CPU architecture
if platform.architecture()[0] == '64bit':
    import x86_64.RainbowCrack as RainbowCrack
else:
    import x86.RainbowCrack as RainbowCrack

### Logging configuration
logging.basicConfig(format='\r[%(levelname)s] %(asctime)s - %(message)s',
                    level=logging.DEBUG)

### Load configuration file
if len(argv) == 2:
    cfg_path = argv[1]
else:
    cfg_path = path.abspath("WeaponSystem.cfg")
if not (path.exists(cfg_path) and path.isfile(cfg_path)):
    logging.critical(
        "No configuration file found at %s, cannot continue." % cfg_path)
    _exit(1)
logging.info('Loading config from: %s' % cfg_path)
config = ConfigParser.SafeConfigParser()
config.readfp(open(cfg_path, 'r'))


class WeaponSystem(rpyc.Service):
    '''
    RPC Services: This is the code that does the actual password cracking
    and returns the results to orbital control.  Currently only supports
    cracking using rainbow tables (RCrackPy)
    '''

    is_initialized = False
    mutex = Lock()
    rainbow_tables = {'LM': None, 'NTLM': None, 'MD5': None}
    is_busy = False
    debug = config.get("RCrack", 'debug')

    def initialize(self):
        ''' Initializes variables, this should only be called once '''
        logging.info("Weapon system initializing ...")
        self.algorithms = self.rainbow_tables.keys()
        self.__tables__()
        self.__cpu__()
        if config.get("RCrack", 'threads') <= 0:
            self.threads = self.cpu_cores
        else:
            self.threads = config.get("RCrack", 'threads')
        logging.info("Weapon system online, good hunting.")

    def on_connect(self):
        ''' Called when successfully connected '''
        self.mutex.acquire()
        if not self.is_initialized:
            self.initialize()
            self.is_initialized = True
        self.mutex.release()
        logging.info("Uplink to orbital control active")

    def on_disconnect(self):
        ''' Called if the connection is lost/disconnected '''
        logging.info("Disconnected from orbital command server.")

    def exposed_crack_list(self, job_id, hashes, hash_type):
        ''' Cracks a list of hashes '''
        self.mutex.acquire()
        self.is_busy = True
        self.current_job_id = job_id
        self.mutex.release()
        tables = self.rainbow_tables[hash_type]
        logging.info(
            "Recieved new assignment, now targeting %d hashes with %d thread(s)" % (len(hashes), self.threads))
        results = RainbowCrack.hash_list(
            len(hashes), hashes, tables, maxThreads=self.threads, debug=self.debug)
        self.mutex.acquire()
        self.is_busy = False
        self.mutex.release()
        return results

    def exposed_get_capabilities(self):
        ''' Returns what algorithms can be cracked '''
        capabilities = []
        for algo in self.algorithms:
            if self.rainbow_tables[algo] != None:
                capabilities.append(algo)
        return capabilities

    def exposed_ping(self):
        ''' Returns a pong message '''
        return "PONG"

    def exposed_is_busy(self):
        ''' Returns True/False if the current system is busy (thread safe) '''
        self.mutex.acquire()
        busy = self.is_busy
        self.mutex.release()
        return busy

    def exposed_current_job(self):
        ''' Returns the current job id (thread safe) '''
        self.mutex.acquire()
        job = self.current_job_id
        self.mutex.release()
        return job

    def exposed_cpu_count(self):
        ''' Returns the number of detected cpu cores '''
        return self.cpu_cores

    def __cpu__(self):
        ''' Detects the number of CPU cores on a system (including virtual cores) '''
        if cpu_count != None:
            try:
                self.cpu_cores = cpu_count()
                logging.info("Detected %d CPU core(s)" % self.cpu_cores)
            except NotImplementedError:
                logging.error(
                    "Could not detect number of processors; assuming 1")
                self.cpu_cores = 1
        else:
            try:
                self.cpu_cores = sysconf("SC_NPROCESSORS_CONF")
                logging.info("Detected %d CPU core(s)" % self.cpu_cores)
            except ValueError:
                logging.error(
                    "Could not detect number of processors; assuming 1")
                self.cpu_cores = 1

    def __tables__(self):
        ''' Load rainbow table configurations '''
        for algo in self.algorithms:
            try:
                table_path = config.get("RainbowTables", algo)
                if table_path.lower() != 'none':
                    self.rainbow_tables[algo] = table_path
                    if not path.exists(self.rainbow_tables[algo]):
                        logging.warn("%s rainbow table directory not found (%s)" %
                                     (algo, self.rainbow_tables[algo]))
            except:
                logging.exception(
                    "Failed to read %s configuration from file" % algo)

if __name__ == "__main__":
    from rpyc.utils.server import ThreadedServer
    agent = ThreadedServer(WeaponSystem, hostname="localhost",
                           port=config.getint("Network", 'lport'))
    logging.info("Weapon system ready, waiting for orbital control uplink ...")
    agent.start()
