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
from handlers.BaseHandlers import BaseHandler
from libs.Form import Form
from libs.SecurityDecorators import *
from string import ascii_letters, digits


class ManageUsersHandler(BaseHandler):

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
        user_name = self.get_argument("username", '')
        user = User.by_user_name(user_name)
        if user is not None:
            user.approved = True
            self.dbsession.add(user)
            self.dbsession.flush()
            self.render("admin/approved_user.html", user=user)
        else:
            self.render("admin/manage_users.html",
                errors=["User does not exist"]
            )


class ManageJobsHandler(BaseHandler):

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


class AddWeaponSystemsHandler(BaseHandler):

    @authenticated
    @authorized('admin')
    @restrict_ip_address
    def get(self, *args, **kwargs):
        ''' Renders the create weapon system page '''
        self.render("admin/create_weaponsystem.html", 
            errors=None
        )

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
        if form.validate(self.request.arguments):
            if WeaponSystem.by_name(self.get_argument('name')) is not None:
                self.render("admin/create_weaponsystem.html",
                    errors=['That name already exists']
                )
            elif WeaponSystem.by_ip_address(self.get_argument('ip_address')) is not None:
                self.render("admin/create_weaponsystem.html",
                    errors=['IP Address already in use']
                )
            else:
                try:
                    if not 1 <= int(self.get_argument('ssh_port')) < 65535:
                        raise ValueError("SSh port not in range")
                    if not 1 <= int(self.get_argument('service_port')) < 65535:
                        raise ValueError("Service port not in range")
                    weapon_system = self.create_weapon()
                    weapon_system.initialize()
                    self.render("admin/created_weaponsystem.html", errors=None)
                except ValueError:
                    self.render("admin/create_weaponsystem.html",
                                errors=["Invalid port number must be 1-65535"])
        else:
            self.render("admin/create_weaponsystem.html", errors=form.errors)

    def create_weapon(self):
        ''' Adds parameters to the database '''
        weapon_system = WeaponSystem(
            weapon_system_name=unicode(self.get_argument('name')),
            ssh_user=unicode(self.get_argument('ssh_user')),
            ssh_key=unicode(self.get_argument('ssh_key')),
            ip_address=unicode(self.get_argument('ip_address')),
            ssh_port=int(self.get_argument('ssh_port')),
            service_port=int(self.get_argument('service_port')),
        )
        dbsession.add(weapon_system)
        dbsession.flush()
        return weapon_system


class InitializeHandler(BaseHandler):

    @authenticated
    @authorized('admin')
    @restrict_ip_address
    def get(self, *args, **kwargs):
        try:
            weapon_system = WeaponSystem.by_uuid(self.get_argument('uuid'))
            success = weapon_system.initialize()
        except:
            logging.exception("Error while initializing weapon system.")
            self.render("admin/initialize_failure.html")
            return
        if success:
            self.render("admin/initialize_success.html")
        else:
            self.render("admin/initialize_failure.html")


class EditWeaponSystemsHandler(BaseHandler):

    @authenticated
    @authorized('admin')
    @restrict_ip_address
    def get(self, *args, **kwargs):
        ''' Renders the create weapon system page '''
        self.render("admin/edit_weaponsystem.html",
            uninit_systems=WeaponSystem.get_uninitialized(),
            weapon_systems=WeaponSystem.get_all()
        )

