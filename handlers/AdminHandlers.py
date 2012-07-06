# -*- coding: utf-8 -*-
'''
Created on Mar 13, 2012

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

import logging

from models import User
from tornado.web import RequestHandler
from libs.SecurityDecorators import *

class ManageUsersHandler(RequestHandler):
    
    def initialize(self, dbsession):
        self.dbsession = dbsession

    @authenticated
    @authorized('admin')
    @restrict_ip_address
    def get(self, *args, **kwargs):
        ''' Renders the manage users page '''
        self.render("admin/manage_users.html", unapproved_users = User.get_unapproved())
    
    @authenticated
    @authorized('admin')
    @restrict_ip_address
    def post(self, *args, **kwargs):
        ''' Approves users '''
        try:
            user_name = self.get_argument("username")
        except:
            self.render("admin/error.html", error = "User does not exist")
        user = User.by_user_name(user_name)
        user.approved = True
        self.dbsession.add(user)
        self.dbsession.flush()
        self.render("admin/approved_user.html", user = user)

class ManageJobsHandler(RequestHandler):

    @authenticated
    @authorized('admin')
    @restrict_ip_address
    def get(self, *args, **kwargs):
        pass

    @authenticated
    @authorized('admin')
    @restrict_ip_address
    def post(sefl, *args, **kwargs):
        pass
