#!/usr/bin/env python
'''
Created on Aug 22, 2012

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
import cmd
import sys
import getpass

from libs.ConsoleColors import *
from libs.ConfigManager import ConfigManager
from models import dbsession, User, Permission


class RecoveryConsole(cmd.Cmd):
    ''' Recovery console for user/passwords '''

    intro  = "\n *** Planetary Assault System Recovery Console ***\n"
    prompt = underline + "Recovery" + W + " > "

    def do_reset(self, username):
        ''' Reset a users password '''
        user = User.by_user_name(username)
        if user == None:
            print WARN + str("%s user not found in database." % username)
        else:
            print INFO + str("Loaded %s from database" % user.user_name)
            sys.stdout.write(PROMPT + "New ")
            sys.stdout.flush()
            new_password = getpass.getpass()
            user.password = new_password
            dbsession.add(user)
            dbsession.flush()
            print INFO + str("Updated %s password successfully." % user.user_name)

    def do_ls(self, *args, **kwargs):
        ''' List all users in the database '''
        users = User.all()
        for user in users:
            print INFO + str("%d. %s" % (user.id, user.user_name))

    def do_exit(self, *args, **kwargs):
        ''' Exit recovery console '''
        print INFO + "Have a nice day!"
        os._exit(0)
