# -*- coding: utf-8 -*-
'''
Created on Jul 2, 2012

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


import os
import sys
import getpass

from libs.ConsoleColors import *
from libs.ConfigManager import ConfigManager
from models import dbsession, User, Permission, Algorithm
from models.User import ADMIN_PERMISSION


# Fills the database with some startup data.
config = ConfigManager.Instance()

if config.debug:
    username = 'admin'
    password = 'nimda123'
else:
    username = raw_input(PROMPT + "User name: ")
    sys.stdout.write(PROMPT + "New Admin ")
    sys.stdout.flush()
    password1 = getpass.getpass()
    sys.stdout.write(PROMPT + "Confirm New Admin ")
    sys.stdout.flush()
    password2 = getpass.getpass()
    if password1 == password2 and 12 <= len(password1):
        password = password1
    else:
        print(WARN +
              'Error: Passwords did not match, or were less than 12 chars')
        os._exit(1)

### Initialize algorithms
md5 = Algorithm(
    name=u'MD5',
    length=32,
    chars=u'1234567890ABCDEF',
)
lm = Algorithm(
    name=u'LM',
    length=16,
    chars=u'1234567890ABCDEF',
)
ntlm = Algorithm(
    name=u'NTLM',
    length=16,
    chars=u'1234567890ABCDEF',
)
dbsession.add(md5)
dbsession.add(lm)
dbsession.add(ntlm)
dbsession.flush()

### Create admin account
user = User(
    username=unicode(username),
)
dbsession.add(user)
dbsession.flush()
user.password = password
dbsession.add(user)
dbsession.flush()
permission = Permission(
    permission_name=ADMIN_PERMISSION,
    user_id=user.id
)
dbsession.add(permission)
dbsession.flush()

### Print details for user'
if config.debug:
    environ = bold + R + "Developement boot strap" + W
    details = ", default admin password is '%s'." % password
else:
    environ = bold + "Production boot strap" + W
    details = '.'
print(INFO + '%s complete successfully%s' % (environ, details))
