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
import logging
import ConfigParser

from libs.Singleton import Singleton

@Singleton
class ConfigManager(object):
    '''  Central class which handles any user-controlled settings '''

    def __init__(self):
        self.cfg_path = os.path.abspath("PlanetaryAssaultSystem.cfg")
        logging.info('Loading config from %s' % self.cfg_path)
        self.config = ConfigParser.SafeConfigParser()
        self.config.readfp(open(self.cfg_path, 'r'))
        self.__tables__()
        self.__system__()
        self.__network__()

    def __tables__(self):
        ''' Load rainbow table configurations '''
        self.rainbow_tables = {}
        self.rainbow_tables['LM'] = self.config.get("RainbowTables", 'lm')
        self.rainbow_tables['NTLM'] = self.config.get("RainbowTables", 'ntlm')
        self.rainbow_tables['MD5'] = self.config.get("RainbowTables", 'md5')

    def __system__(self):
        ''' Load system configurations '''
        self.max_threads = self.config.getint("System", 'threads')

    def __network__(self):
        ''' Load network configurations '''
        self.listen_port = self.config.getint("Network", 'port')