# -*- coding: utf-8 -*-
"""

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
"""


# Make sure to import the config first
from libs.ConfigManager import ConfigManager

from os import system
from sys import argv
from time import sleep
from datetime import datetime
from libs import ConsoleColors
from handlers import start_server
from models import __create__, boot_strap

current_time = lambda: str(datetime.now()).split(' ')[1].split('.')[0]

def serve():
    """ Starts the application """
    start_server()

def create():
    """ Creates the database """
    print (ConsoleColors.INFO+'%s : Creating the database ... ' % current_time())
    __create__()
    if len(argv) == 3 and argv[2] == 'bootstrap':
        print (ConsoleColors.INFO+'%s : Bootstrapping the database ... ' % current_time())
        boot_strap()
    
def help():
    print('Usage:')
    print('\tpython . serve - Starts the web server')
    print('\tpython . create - Inits the database tables')
    print('\tpython . create bootstrap - Inits the database tables and creates an admin account')

### Main
if len(argv) == 1:
    help()
options = {
    'serve': serve, 
    'create': create,
}
if argv[1] in options:
    options[argv[1]]()
else:
    print(ConsoleColors.WARN+'Error: PEBKAC')
