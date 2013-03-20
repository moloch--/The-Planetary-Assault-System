#!/usr/bin/env python
'''
Created on June 23, 2012

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
import logging
import platform
import argparse
import functools
import ConfigParser

from sys import argv
from threading import Lock
from os import path, sysconf, _exit
from multiprocessing import cpu_count
from rpyc.utils.server import ThreadedServer
from yapsy.PluginManager import PluginManager
from plugins.PluginBases import *


### Logging configuration
if platform.system().lower() in ['linux', 'darwin']:
    INFO = "\033[1m\033[36m[*]\033[0m "
    WARN = "\033[1m\033[31m[!]\033[0m "
else:
    INFO = "[*] "
    WARN = "[!] "
logging.basicConfig(
    format='\r[%(levelname)s] %(asctime)s - %(message)s',
    level=logging.DEBUG
)

# Always use upper case for algo names
FILTERS = {
    "MD5"   : MD5Plugin,
    "SHA1"  : SHA1Plugin,
    "SHA256": SHA256Plugin,
    "SHA512": SHA256Plugin,
    "LM"    : LMPlugin,
    "NTLM"  : NTLMPlugin,
    "PBKDF2": PBKDF2Plugin,
}

def atomic(method):
    ''' Call function only when we acquire a mutex '''

    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        method_exception = None
        results = None
        self.mutex.acquire()
        try:
            results = method(self, *args, **kwargs)
        except Exception as error:
            method_exception = error
        finally:
            # Always release mutex, even if the method raised 
            # an exception
            self.mutex.release()
            if method_exception is not None:
                raise Exception(method_exception)
        return results
    return wrapper


class WeaponSystem(rpyc.Service):
    '''
    RPC Services: This is the code that does the actual password cracking
    and returns the results to orbital control.  Currently only supports
    cracking using rainbow tables (RCrackPy)
    '''

    is_initialized = False
    mutex = Lock()
    is_busy = False
    job_id = None

    def initialize(self):
        ''' Initializes variables, this should only be called once '''
        logging.info("Weapon system initializing ...")
        self.plugin_manager = PluginManager()
        self.plugin_manager.setPluginPlaces(["plugins/"])
        self.plugin_manager.setCategoriesFilter(FILTERS)
        self.plugin_manager.collectPlugins()
        self.plugins = {} 
        logging.info(
            "Loaded %d plugin(s)" % len(self.plugin_manager.getAllPlugins())
        )
        self.__cpu__()
        logging.info("Weapon system online, good hunting.")

    @atomic
    def on_connect(self):
        ''' Called when successfully connected '''
        if not self.is_initialized:
            self.initialize()
            self.is_initialized = True
        logging.info("Uplink to orbital control active")

    def on_disconnect(self):
        ''' Called if the connection is lost/disconnected '''
        logging.info("Disconnected from orbital command server.")

    def __cpu__(self):
        ''' Detects the number of CPU cores on a system (including virtual cores) '''
        if cpu_count is not None:
            try:
                self.cpu_cores = cpu_count()
                logging.info("Detected %d CPU core(s)" % self.cpu_cores)
            except NotImplementedError:
                logging.error("Could not detect number of processors; assuming 1")
                self.cpu_cores = 1
        else:
            try:
                self.cpu_cores = int(sysconf("SC_NPROCESSORS_CONF"))
                logging.info("Detected %d CPU core(s)" % self.cpu_cores)
            except ValueError:
                logging.error("Could not detect number of processors; assuming 1")
                self.cpu_cores = 1

    ############################ [ EXPOSED METHODS ] ############################
    @atomic
    def exposed_crack(self, plugin_name, job_id, hashes, **kwargs):
        ''' Exposes plugins calls '''
        assert plugin_name in self.plugins
        self.is_busy = True
        self.job_id = job_id
        self.plugin_manager.activatePluginByName(plugin_name)
        plugin = self.plugin_manager.getPluginByName(plugin_name)
        results = plugin.execute(hashes, **kwargs)
        self.plugin_manager.deactivatePluginByName(plugin_name)
        self.job_id = None
        self.is_busy = False
        return results

    def exposed_get_plugin_names(self):
        ''' Returns what algorithms can be cracked '''
        logging.info("Method called: exposed_get_capabilities")
        plugins = self.plugin_manager.getAllPlugins()
        return [plugin.name for plugin in plugins]

    def exposed_get_categories(self):
        ''' Return categories for which we have plugins '''
        categories = []
        for category in self.plugin_manager.getCategories():
            if 0 < len(self.plugin_manager.getPluginsOfCategory(category)):
                categories.append(category)
        return categories

    def exposed_get_category_plugins(self, category):
        ''' Get plugin names for a category '''
        plugins = self.plugin_manager.getPluginsOfCategory(category)
        return [plugin.name for plugin in plugins]

    def exposed_get_plugin_details(self, category, plugin_name):
        ''' Get plugin based on name details '''
        plugin = self.plugin_manager.getPluginByName(plugin_name, category)
        info = {'name': plugin.name}
        info['author'] = plugin.details.get('Documentation', 'author')
        info['website'] = plugin.details.get('Documentation', 'website')
        info['version'] = plugin.details.get('Documentation', 'version')
        info['description'] = plugin.details.get('Documentation', 'description')
        info['copyright'] = plugin.details.get('Documentation', 'copyright')
        info['precomputation'] = plugin.is_precomputation
        return info

    def exposed_ping(self):
        ''' Returns a pong message '''
        return "PONG"

    def exposed_is_busy(self):
        ''' Returns True/False if the current system is busy (thread safe) '''
        return self.is_busy

    def exposed_current_job_id(self):
        ''' Returns the current job id (thread safe) '''
        return self.job_id

    def exposed_cpu_count(self):
        ''' Returns the number of detected cpu cores '''
        return self.cpu_cores


### Start a threaded RPC service
def start_server(config_file):
    defaults = {
        'hostname':'localhost', 
        'lport':'31337',
        'ipv6':'off',
        'backlog':'10',
    }
    config = ConfigParser.SafeConfigParser(defaults)
    config.readfp(open(config_file, 'r'))
    lport = config.getint("Network", 'lport')
    host = config.get("Network", 'hostname').strip()
    agent = ThreadedServer(WeaponSystem, hostname=host, port=lport)
    agent.start()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Planetary Assault System: Weapon System',
    )
    parser.add_argument('--version', 
        action='version', 
        version='%(prog)s v0.1'
    )
    parser.add_argument('--test-mode', '-t',
        help='test weapon system, do NOT start service',
        action='store_true',
        dest='test',
    )
    parser.add_argument('--config-file', '-c',
        help='path to config file (default: WeaponSystem.cfg)',
        dest='cfg',
        default='WeaponSystem.cfg'
    )
    args = parser.parse_args()
    if not args.test:
        if not path.exists(args.cfg) or not path.isfile(args.cfg):
            print(WARN + "Config file does not exist")
            _exit(1)
        else:
            logging.info('Loading config from: %s' % path.abspath(args.cfg))
            start_server(args.cfg)
            _exit(0)
    else:
        print(INFO + "Test mode activated ... ")
        wsys = WeaponSystem(None)
        wsys.on_connect()
        print wsys.exposed_get_plugin_names()
        print wsys.plugin_manager.getCategories()
        for cat in wsys.plugin_manager.getCategories():
            print "Cat: '%s': " % cat,
            print [plug.name for plug in wsys.plugin_manager.getPluginsOfCategory(cat)]