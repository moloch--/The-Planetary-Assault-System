# -*- coding: utf-8 -*-
'''
Created on Mar 13, 2012

@author: moloch

    Copyright 2012

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


import bcrypt
import thread
import logging

from models import dbsession, WeaponSystem, Algorithm
from models.User import User, ADMIN_PERMISSION
from handlers.BaseHandlers import BaseHandler
from libs.Form import Form
from libs.SecurityDecorators import *
from string import ascii_letters, digits


class ManageUsersHandler(BaseHandler):

    @authenticated
    @authorized(ADMIN_PERMISSION)
    @restrict_ip_address
    def get(self, *args, **kwargs):
        ''' Renders the manage users page '''
        self.render("admin/manage_users.html", errors=None)
    
    @authenticated
    @authorized(ADMIN_PERMISSION)
    @restrict_ip_address
    def post(self, *args, **kwargs):
        user_uuid = self.get_argument('uuid', '')
        user = User.by_uuid(user_uuid)
        if user is not None:
            errors = []
            username = self.get_argument('username', None)
            password = self.get_argument('password', None)
            if password is not None:
                if 12 <= len(password) <= 100:
                    self.change_user_password(user)
                else:
                    errors.append("Password invalid length (12-100)")
            if username is not None and username != user.username:
                if 3 <= len(username) <= 15:
                    if User.by_username(username) is None:
                        user.username = username
                        dbsession.add(user)
                        dbsession.flush()
                    else:
                        errors.append("Username already exists")
                else:
                    errors.append("Username is an invalid length (3-15)")
            self.render("admin/manage_users.html", errors=errors)
        else:
            self.render("admin/manage_users.html",
                errors=["User does not exist"]
            )

    def change_user_password(user):
        ''' Update user password and salt '''
        user.salt = bcrypt.salt(16)
        dbsession.add(user)
        dbsession.flush()
        user.password = password
        dbsession.add(user)
        dbsession.flush()


class AdminLockHandler(BaseHandler):
    ''' Used to manually lock/unlocked accounts '''

    @authenticated
    @authorized(ADMIN_PERMISSION)
    @restrict_ip_address
    def get(self, *args, **kwargs):
        ''' Toggle account lock '''
        uuid = self.get_argument('uuid', '')
        user = User.by_uuid(uuid)
        if user is not None:
            if user.locked:
                user.locked = False
                dbsession.add(user)
                self.write({'success': 'unlocked'})
            else:
                user.locked = True
                dbsession.add(user)
                self.write({'success': 'locked'})
        else:
            self.write({'error': 'User does not exist'})
        dbsession.flush()
        self.finish()


class AdminAjaxUsersHandler(BaseHandler):
    ''' Handles AJAX data for admin handlers '''

    @restrict_ip_address
    @authenticated
    @authorized(ADMIN_PERMISSION)
    def get(self, *args, **kwargs):
        uuid = self.get_argument('uuid', '')
        user = User.by_uuid(uuid)
        if user is not None:
           self.write({
                'username': user.username,
            })
        else:
            self.write({'Error': 'User does not exist.'})
        self.finish()


class ManageJobsHandler(BaseHandler):

    @authenticated
    @authorized(ADMIN_PERMISSION)
    @restrict_ip_address
    def get(self, *args, **kwargs):
        pass

    @authenticated
    @authorized(ADMIN_PERMISSION)
    @restrict_ip_address
    def post(self, *args, **kwargs):
        pass


class AddWeaponSystemsHandler(BaseHandler):

    @authenticated
    @authorized(ADMIN_PERMISSION)
    @restrict_ip_address
    def get(self, *args, **kwargs):
        ''' Renders the create weapon system page '''
        self.render("admin/weaponsystem/create.html", errors=None)

    @authenticated
    @authorized(ADMIN_PERMISSION)
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
                self.render("admin/weaponsystem/create.html",
                    errors=['That name already exists']
                )
            elif WeaponSystem.by_ip_address(self.get_argument('ip_address')) is not None:
                self.render("admin/weaponsystem/create.html",
                    errors=['IP Address already in use']
                )
            else:
                try:
                    if not 1 <= int(self.get_argument('ssh_port', -1)) < 65535:
                        raise ValueError("SSh port not in range")
                    if not 1 <= int(self.get_argument('service_port', -1)) < 65535:
                        raise ValueError("Service port not in range")
                    weapon_system = self.create_weapon()
                    self.render("admin/weaponsystem/created.html", errors=None)
                except ValueError:
                    self.render("admin/weaponsystem/create.html",
                        errors=["Invalid port number; must be 1-65535"]
                    )
        else:
            self.render("admin/weaponsystem/create.html", errors=form.errors)

    def create_weapon(self):
        ''' Adds parameters to the database '''
        weapon_system = WeaponSystem(
            name=unicode(self.get_argument('name')),
            ssh_user=unicode(self.get_argument('ssh_user')),
            ssh_key=unicode(self.get_argument('ssh_key')),
            ip_address=unicode(self.get_argument('ip_address')),
            ssh_port=int(self.get_argument('ssh_port')),
            service_port=int(self.get_argument('service_port')),
        )
        print 'GOT:', weapon_system
        dbsession.add(weapon_system)
        dbsession.flush()
        return weapon_system


class InitializeHandler(BaseHandler):

    output = ''

    @authenticated
    @authorized(ADMIN_PERMISSION)
    @restrict_ip_address
    def get(self, *args, **kwargs):
        success = False
        try:
            weapon_system = WeaponSystem.by_uuid(self.get_argument('uuid', ''))
            if weapon_system is not None:
                success = self.init_weapon_system(weapon_system)
            else:
                raise ValueError("WeaponSystem uuid does not exist")
        except Exception as error:
            self.output += "\n[!] Error: " + str(error)
            logging.exception("Error while initializing weapon system.")
        finally:
            dbsession.add(weapon_system)
            dbsession.flush()
        self.render("admin/weaponsystem/initialize.html", success=success, output=self.output)

    def init_weapon_system(self, weapon_system):
        success = False
        self.output = '[*] Attempting to obtain rpc connection to %s:%d ... ' % (
            weapon_system.ip_address, weapon_system.ssh_port,
        )
        rpc = weapon_system.get_rpc_connection()
        if rpc is None:
            self.output += "failure\n"
            success = False
        else:
            self.output += "done!\n"
            if not self.query_plugins(weapon_system, rpc):
                success = False
            if not self.query_hardware(weapon_system, rpc):
                success = False
        if success:
            weapon_system.initialized = True
        return success

    def query_plugins(self, weapon_system, rpc):
        self.output += "[*] Attempting to detect remote plugin(s) ...\n"
        for algo in Algorithm.all_names():
            self.output += "[+] Looking for %s plugins ..." % algo
            plugin_names = rpc.root.exposed_get_category_plugins(algo)
            self.output += " found %d\n" % len(plugin_names)
            for plugin_name in plugin_names:
                self.output += "[+] Query info from remote plugin '%s'\n" % plugin_name
                plugin = rpc.root.exposed_get_plugin_details(algo, plugin_name)
                details = PluginDetails(**plugin)
                weapon_system.plugins.append(details)

    def query_hardware(self, weapon_system, rpc):
        self.output += "[*] Detecting CPU core(s) ..."
        weapon_system.cpu_count = rpc.root.exposed_cpu_count()
        self.output += "found %d\n" % weapon_system.cpu_count


class ViewWeaponSystemsHandler(BaseHandler):

    @authenticated
    @authorized(ADMIN_PERMISSION)
    @restrict_ip_address
    def get(self, *args, **kwargs):
        ''' Renders the create weapon system page '''
        self.render("admin/weaponsystem/view.html")


class DetailsWeaponSystemsHandler(BaseHandler):

    @authenticated
    @authorized(ADMIN_PERMISSION)
    @restrict_ip_address
    def get(self, *args, **kwargs):
        ''' Renders the detail weapon system page '''
        uuid = self.get_argument('uuid', '')
        weapon_system = WeaponSystem.by_uuid(uuid)
        self.render("admin/weaponsystem/details.html", wsys=weapon_system)


class EditWeaponSystemsHandler(BaseHandler):

    @authenticated
    @authorized(ADMIN_PERMISSION)
    @restrict_ip_address
    def post(self, *args, **kwargs):
        ''' Renders the create weapon system page '''
        # Do editing 
        self.render("admin/weaponsystem/details.html", wsys=weapon_system)