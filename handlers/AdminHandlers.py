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
            self.render("admin/error.html", error="User does not exist")
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
            "admin/create_weaponsystem.html", message="Uplink Parameters")

    @authenticated
    @authorized('admin')
    @restrict_ip_address
    def post(self, *args, **kwargs):
        '''  Creates a new weapon system, and yes the form validation is shit '''
        if self.validate_form():
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
            self.render("admin/created_weaponsystem.html")

    def validate_form(self):
        ''' Shitty form validation '''
        # Name
        try:
            self.name = self.filter_string(self.get_argument("name"))
            if WeaponSystem.by_name(self.name) != None:
                raise ValueError("Name already exits")
        except:
            self.render(
                "admin/create_weaponsystem.html", message="Invalid Name")
            return False
        # IP Address
        try:
            self.ip_address = self.filter_string(
                self.get_argument("ipaddress"), extra_chars=".")
            if WeaponSystem.by_ip_address(self.ip_address) != None:
                raise ValueError("IP Address already in use")
        except:
            self.render("admin/create_weaponsystem.html",
                        message="Missing IP Address")
            return False
        # Service Port
        try:
            self.listen_port = int(self.get_argument("srvport"))
            if not 1 < self.listen_port < 65535:
                raise ValueError("Invalid port range, or not a number")
        except:
            self.render("admin/create_weaponsystem.html",
                        message="Invalid Listen Port")
            return False
        # SSH User
        try:
            self.ssh_user = self.filter_string(self.get_argument("sshuser"))
            if self.ssh_user.lower() == 'root':
                raise ValueError("SSH User cannot be 'root'")
        except:
            self.render("admin/create_weaponsystem.html",
                        message="Missing SSH User")
            return False
        # SSH Key
        try:
            self.ssh_key = self.filter_string(
                self.get_argument("sshkey"), extra_chars="+/=- \n")
        except:
            self.render("admin/create_weaponsystem.html",
                        message="Missing SSH Private Key")
            return False
        # SSH Port
        try:
            self.ssh_port = int(self.get_argument("sshport"))
            if not 1 < self.ssh_port < 65535:
                raise ValueError("Invalid port range, or not a number")
        except:
            self.render("admin/create_weaponsystem.html",
                        message="Missing SSH Port")
            return False
        return True

    def filter_string(self, string, extra_chars=""):
        ''' Removes erronious chars from a string '''
        char_white_list = ascii_letters + digits + extra_chars
        return filter(lambda char: char in char_white_list, string)


class EditWeaponSystemsHandler(AdminBaseHandler):

    @authenticated
    @authorized('admin')
    @restrict_ip_address
    def get(self, *args, **kwargs):
        ''' Renders the create weapon system page '''
        self.render("admin/edit_weaponsystem.html",
                    weapon_systems=WeaponSystem.get_all())

    @authenticated
    @authorized('admin')
    @restrict_ip_address
    def post(sefl, *args, **kwargs):
        pass
