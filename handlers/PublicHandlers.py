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


import os
import logging

from tornado.web import RequestHandler
from BaseHandlers import UserBaseHandler
from recaptcha.client import captcha
from libs.Form import Form
from libs.ConfigManager import ConfigManager
from libs.Session import SessionManager
from libs.SecurityDecorators import authenticated
from models import User


class WelcomeHandler(RequestHandler):
    ''' Landing page '''

    def get(self, *args, **kwargs):
        ''' Renders the welcome page '''
        self.render("public/welcome.html")


class LoginHandler(RequestHandler):
    ''' Handles the login progress '''

    def initialize(self, dbsession):
        self.dbsession = dbsession
        self.config = ConfigManager.Instance()

    def get(self, *args, **kwargs):
        ''' Renders the login page '''
        self.render("public/login.html", errors=None)

    def post(self, *args, **kwargs):
        ''' Checks login creds '''
        form = Form(
            username="Please enter a username",
            password="Please enter a password",
            recaptcha_challenge_field="Invalid captcha",
            recaptcha_response_field="Invalid captcha",
        )
        if not form.validate(self.request.arguments):
            self.render("public/login.html", errors=form.errors)
        elif self.check_recaptcha():
            user = User.by_user_name(self.get_argument('username'))
            if user != None and user.validate_password(self.get_argument('password')):
                if not user.approved:
                    self.render("public/login.html",
                                errors=["Your account must be approved by an administrator."])
                else:
                    self.successful_login(user)
                    self.redirect('/user')
            else:
                self.failed_login()
        else:
            self.render('public/login.html', errors=["Invalid captcha, try again"])

    def check_recaptcha(self):
        ''' Checks recaptcha '''
        if self.config.recaptcha_enable:
            response = None
            try:
                response = captcha.submit(
                    self.get_argument('recaptcha_challenge_field'),
                    self.get_argument('recaptcha_response_field'),
                    self.application.settings['recaptcha_private_key'],
                    self.request.remote_ip
                )
            except:
                logging.exception("Recaptcha API called failed")
            if response != None and response.is_valid:
                return True
            else:
                return False
        else:
            return True

    def successful_login(self, user):
        ''' Called when a user successfully authenticates '''
        logging.info("Successful login: %s from %s" %
                     (user.user_name, self.request.remote_ip))
        session_manager = SessionManager.Instance()
        sid, session = session_manager.start_session()
        self.set_secure_cookie(
            name='auth', value=str(sid), expires_days=1, HttpOnly=True)
        session.data['user_name'] = str(user.user_name)
        session.data['ip'] = str(self.request.remote_ip)
        if user.has_permission('admin'):
            session.data['menu'] = "admin"
        else:
            session.data['menu'] = "user"

    def failed_login(self):
        ''' Called when someone fails to login '''
        logging.info("Failed login attempt from %s" % self.request.remote_ip)
        self.render('public/login.html',
                    errors=["Failed login attempt, try again"])


class RegistrationHandler(RequestHandler):
    ''' Handles the user registration process '''

    def initialize(self, dbsession):
        self.dbsession = dbsession
        self.config = ConfigManager.Instance()

    def get(self, *args, **kwargs):
        ''' Renders registration page '''
        self.render("public/registration.html", errors=None)

    def post(self, *args, **kwargs):
        ''' Attempts to create an account '''
        form = Form(
            username="Please enter a username",
            pass1="Please enter a password",
            pass2="Please confirm your password",
            recaptcha_challenge_field="Invalid captcha",
            recaptcha_response_field="Invalid captcha",
        )
        if not form.validate(self.request.arguments):
            self.render("public/registration.html", errors=form.errors)
        elif self.check_recaptcha():
            user_name = self.get_argument('username')
            if User.by_user_name(user_name) != None:
                self.render('public/registration.html',
                            errors=['Account name already taken'])
            elif len(user_name) < 3 or 15 < len(user_name):
                self.render('public/registration.html',
                            errors=['Username must be 3-15 characters'])
            elif not self.get_argument('pass1') == self.get_argument('pass2'):
                self.render('public/registration.html',
                            errors=['Passwords do not match'])
            elif not (12 <= len(self.get_argument('pass1')) <= 100):
                self.render('public/registration.html',
                            errors=['Password must be 12-100 characters'])
            else:
                user = self.create_user(user_name, self.get_argument('pass1'))
                self.render(
                    "public/account_created.html", user_name=user.user_name)
        else:
            self.render("public/registration.html",
                        errors=['Invalid captcha'])

    def create_user(self, username, password):
        user = User(
            user_name=unicode(username),
        )
        # Create user, init class variables
        self.dbsession.add(user)
        self.dbsession.flush()
        # Set password for user
        user.password = password
        self.dbsession.add(user)
        self.dbsession.flush()
        return user

    def check_recaptcha(self):
        ''' Checks recaptcha '''
        if self.config.recaptcha_enable:
            response = None
            try:
                response = captcha.submit(
                    self.get_argument('recaptcha_challenge_field'),
                    self.get_argument('recaptcha_response_field'),
                    self.application.settings['recaptcha_private_key'],
                    self.request.remote_ip
                )
            except:
                logging.exception("Recaptcha API called failed")
            if response != None and response.is_valid:
                return True
            else:
                return False
        else:
            return True


class AboutHandler(RequestHandler):

    def get(self, *args, **kwargs):
        ''' Renders the about page '''
        self.render("public/about.html")
