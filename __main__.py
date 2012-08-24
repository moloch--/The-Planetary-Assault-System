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

from os import system
from sys import argv
from time import sleep
from datetime import datetime
from libs.ConsoleColors import *

current_time = lambda: str(datetime.now()).split(' ')[1].split('.')[0]


def serve():
    """ Starts the application """
    from libs.ConfigManager import ConfigManager
    from handlers import start_server
    print(INFO + '%s : Starting application ... ' %
        current_time())
    start_server()


def create():
    """ Creates the database """
    from libs.ConfigManager import ConfigManager
    from models import __create__, boot_strap
    print(INFO + '%s : Creating the database ... ' %
           current_time())
    __create__()
    if len(argv) == 3 and argv[2] == 'bootstrap':
        print(INFO +
               '%s : Bootstrapping the database ... ' % current_time())
        boot_strap()

def recovery():
    ''' Recovery console '''
    from libs.ConfigManager import ConfigManager
    from setup.recovery import RecoveryConsole
    print(INFO + '%s : Starting recovery console ... ' %
           current_time())
    console = RecoveryConsole()
    try:
        console.cmdloop()
    except KeyboardInterrupt:
        print (INFO + "Have a nice day!")
        os._exit(1)

def help():
    ''' Displays a helpful message '''
    print('\n\t\t'+bold+R+"*** "+underline+'The Planetary Assault System'+W+bold+R+" ***"+W)
    #print(underline+'Options'+W)
    print('\t'+bold+'python . help'+W+'             - Display this helpful message')
    print('\t'+bold+'python . serve'+W+'            - Starts the web server')
    print('\t'+bold+'python . create'+W+'           - Inits the database tables only')
    print('\t'+bold+'python . create bootstrap'+W+' - Inits the database tables and creates an admin account')
    print('\t'+bold+'python . recovery'+W+'         - Starts the recovery console')

### Main
if len(argv) == 1:
    help()
options = {
    'help': help,
    'serve': serve,
    'create': create,
    'recovery': recovery,
}
if argv[1] in options:
    options[argv[1]]()
else:
    print(WARN + str('PEBKAC (%s): Command not found, see "python . help"' % argv[1]))
