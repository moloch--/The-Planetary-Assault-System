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
from subprocess import call
from handlers import start_server
from models import __create__, boot_strap
from libs import ConsoleColors

curr_time = lambda: str(datetime.now()).split(' ')[1].split('.')[0]

def serve():
    """ Starts the application """
    if len(argv) == 2:
        start_server()

def create():
    """ Creates the database """
    print (ConsoleColors.INFO+'%s : Creating the database ... ' % curr_time())
    __create__()
    if len(argv) == 3 and argv[2] == 'bootstrap':
        boot_strap()
    
def test():
    """ Run unit tests """
    # usage: python . test
    print '[*] %s : testing the application.' % curr_time()
    # calling nose's nosetests to test the application using the 'tests' module
    call(['nosetests', '-v', 'tests'])
    
def help():
    print 'Usage:'
    print '\tpython . serve - Starts the web server'
    print '\tpython . create (bootstrap) - Inits the database'

### Main
if len(argv) == 1:
    help()
options = {
    'serve': serve, 
    'create': create, 
    'test': test
}
if argv[1] in options:
    options[argv[1]]()
else:
    print(ConsoleColors.WARN+'Error: PEBKAC')
