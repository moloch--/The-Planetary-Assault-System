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


import thread
import logging

from models import dbsession, User, WeaponSystem
from handlers.BaseHandlers import AdminBaseHandler
from libs.SecurityDecorators import *
from string import ascii_letters, digits


class ManageUsersHandler(AdminBaseHandler):

    @authenticated
    @authorized('admin')
    @restrict_ip_address
    def get(self, *args, **kwargs):
        ''' Renders the manage users page '''
        self.render("admin/manage_users.html",
                    unapproved_users=User.get_unapproved(),
                    approved_users=User.get_approved(),
                    )

    @authenticated
    @authorized('admin')
    @restrict_ip_address
    def post(self, *args, **kwargs):
        ''' Approves users '''
        try:
            user_name = self.get_argument("username")
        except:
            self.render("admin/error.html", errors=["User does not exist"])
        user = User.by_user_name(user_name)
        user.approved = True
        self.dbsession.add(user)
        self.dbsession.flush()
        self.render("admin/approved_user.html", user=user)


class ManageJobsHandler(AdminBaseHandler):

    @authenticated
    @authorized('admin')
    @restrict_ip_address
    def get(self, *args, **kwargs):
        pass

    @authenticated
    @authorized('admin')
    @restrict_ip_address
    def post(self, *args, **kwargs):
        pass


class AddWeaponSystemsHandler(AdminBaseHandler):

    @authenticated
    @authorized('admin')
    @restrict_ip_address
    def get(self, *args, **kwargs):
        ''' Renders the create weapon system page '''
        self.render(
            "admin/create_weaponsystem.html", errors=None)

    @authenticated
    @authorized('admin')
    @restrict_ip_address
    def post(self, *args, **kwargs):
        ''' Creates a new weapon system, and yes the form validation is shit '''
        form = Form(
            name="Please enter a name",
            ssh_user="Please enter an ssh user name",
            ssh_key="Please enter an ssh key",
            ip_address="Please enter a ip address",
            ssh_port="Please enter an ssh port",
            service_port="Please enter a service port",
        )
        if form.validate():
            weapon_system = WeaponSystem(
                name=unicode(self.name),
                ssh_user=unicode(self.ssh_user),
                ssh_key=unicode(self.ssh_key),
                ip_address=unicode(self.ip_address),
                ssh_port=self.ssh_port,
                service_port=self.listen_port,
            )
            dbsession.add(weapon_system)
            dbsession.flush()
            weapon_system.initialize()
            self.render("admin/created_weaponsystem.html", errors=None)
        else:
            self.render("admin/created_weaponsystem.html", errors=form.errors)

    def filter_string(self, string, extra_chars=""):
        ''' Removes erronious chars from a string '''
        char_white_list = ascii_letters + digits + extra_chars
        return filter(lambda char: char in char_white_list, string)


class InitializeHandler(AdminBaseHandler):

    @authenticated
    @authorized('admin')
    @restrict_ip_address
    def get(self, *args, **kwargs):
        try:
            weapon_system = WeaponSystem.by_uuid(self.get_argument('uuid'))
            success = weapon_system.initialize()
        except:
            self.render("admin/initialize_failure.html")
            return
        if success:
            self.render("admin/initialize_success.html")
        else:
            self.render("admin/initialize_failure.html")


class EditWeaponSystemsHandler(AdminBaseHandler):

    @authenticated
    @authorized('admin')
    @restrict_ip_address
    def get(self, *args, **kwargs):
        ''' Renders the create weapon system page '''
        self.render("admin/edit_weaponsystem.html",
                    uninit_systems=WeaponSystem.get_uninitialized(),
                    weapon_systems=WeaponSystem.get_all())

    @authenticated
    @authorized('admin')
    @restrict_ip_address
    def post(self, *args, **kwargs):
        pass
