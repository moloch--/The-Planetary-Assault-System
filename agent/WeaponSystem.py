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


import os
import sys
import rpyc
import logging
import platform
import ConfigParser
import multiprocessing

### Detect CPU architecture
if platform.architecture()[0] == '64bit':
    import x86_64.RainbowCrack as RainbowCrack
else:
    import x86.RainbowCrack as RainbowCrack

### Logging configuration
logging.basicConfig(format = '\r[%(levelname)s] %(asctime)s - %(message)s', level = logging.DEBUG)

### Load configuration file
if len(sys.argv) == 2:
    cfg_path = sys.argv[1]
else:
    cfg_path = os.path.abspath("WeaponSystem.cfg")
if not (os.path.exists(cfg_path) and os.path.isfile(cfg_path)):
    logging.critical("No configuration file found at %s, cannot continue." % cfg_path)
    os._exit(1)
logging.info('Loading config from: %s' % cfg_path)
config = ConfigParser.SafeConfigParser()
config.readfp(open(cfg_path, 'r'))

### RPC Services
class WeaponSystem(rpyc.Service):

    def on_connect(self):
        ''' Called when successfully connected, does all the initialization '''
        logging.info("Uplink to orbital control active; weapon system initializing ...")
        self.is_busy = False
        self.__cpu__()
        self.rainbow_tables = {}
        self.__tables__()
        logging.info("Weapon system online, good hunting.")

    def on_disconnect(self):
        ''' Called if the connection is lost '''
        logging.error("Lost communication with the Planetary Assault System.")
        self.is_busy = False
        self.rainbow_tables = {}

    def exposed_crack_list(self, hashes, hash_type, threads = 0):
        ''' Cracks a list of hashes '''
        if threads <= 0:
            threads = self.cpu_cores
        try:
            tables = self.rainbow_tables[hash_type]
            RainbowCrack.hash_list(len(hashes), hashes, tables, maxThreads = threads)
        except KeyError:
            logging.error("Invalid hash type (%s), cannot crack." % hash_type)

    def exposed_get_capabilities(self):
        ''' Returns what algorithms can be cracked '''
        return self.rainbow_tables

    def exposed_ping(self):
        ''' Returns a pong message '''
        return "pong"

    def exposed_is_busy(self):
        ''' Returns True/False if the current system is busy '''
        return self.is_busy

    def exposed_cpu_count(self):
        ''' Returns the number of detected cpu cores '''
        return self.cpu_cores

    def __cpu__(self):
        ''' Detects the number of CPU cores on a system (including virtual cores) '''
        if multiprocessing is not None:
            try:
                self.cpu_cores = multiprocessing.cpu_count()
                logging.info("Detected %d CPU core(s)." % self.cpu_cores)
            except NotImplementedError:
                logging.error("Could not detect number of processors; assuming 1.")
                self.cpu_cores = 1
        else:
            try:
                self.cpu_cores = os.sysconf("SC_NPROCESSORS_CONF")
                logging.info("Detected %d CPU core(s)." % self.cpu_cores)
            except ValueError:
                logging.error("Could not detect number of processors; assuming 1.")
                self.cpu_cores = 1

    def __tables__(self):
        ''' Load rainbow table configurations '''
        self.rainbow_tables['LM'] = config.get("RainbowTables", 'lm')
        if not os.path.exists(self.rainbow_tables['LM']):
            logging.warn("LM rainbow table directory not found (%s)" % self.rainbow_tables['LM'])
        self.rainbow_tables['NTLM'] = config.get("RainbowTables", 'ntlm')
        if not os.path.exists(self.rainbow_tables['NTLM']):
            logging.warn("NTLM rainbow table directory not found (%s)" % self.rainbow_tables['NTLM'])
        self.rainbow_tables['MD5'] = config.get("RainbowTables", 'md5')
        if not os.path.exists(self.rainbow_tables['MD5']):
            logging.warn("MD5 rainbow table directory not found (%s)" % self.rainbow_tables['MD5'])

if __name__ == "__main__":
    from rpyc.utils.server import ThreadedServer
    agent = ThreadedServer(WeaponSystem, port = config.getint("Network", 'lport'))
    logging.info("Weapon system ready, waiting for orbital control uplink ...")
    agent.start()
