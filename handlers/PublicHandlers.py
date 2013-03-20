# -*- coding: utf-8 -*-
'''
Created on Mar 13, 2012

@author: moloch

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
import logging

from tornado.web import RequestHandler
from recaptcha.client import captcha
from libs.Form import Form
from libs.ConfigManager import ConfigManager
from libs.SecurityDecorators import authenticated
from handlers.BaseHandlers import BaseHandler
from models import User


class WelcomeHandler(BaseHandler):
    ''' Landing page '''

    def get(self, *args, **kwargs):
        ''' Renders the welcome page '''
        self.render("public/welcome.html")


class LoginHandler(BaseHandler):
    ''' Handles the login progress '''

    def get(self, *args, **kwargs):
        ''' Renders the login page '''
        self.render("public/login.html", errors=None)

    def post(self, *args, **kwargs):
        ''' Checks login creds '''
        form = Form(
            username="Please enter a username",
            password="Please enter a password",
        )
        if not form.validate(self.request.arguments):
            self.render("public/login.html", errors=form.errors)
        else:
            user = User.by_username(self.get_argument('username'))
            if user is not None and user.validate_password(self.get_argument('password')):
                if user.locked:
                    self.render("public/login.html",
                        errors=["Your account must be approved by an administrator."]
                    )
                else:
                    self.successful_login(user)
                    self.redirect('/user')
            else:
                self.failed_login()

    def successful_login(self, user):
        ''' Called when a user successfully authenticates '''
        logging.info("Successful login: %s from %s" % (
            user.username, self.request.remote_ip,
        ))
        self.start_session()
        self.session['username'] = str(user.username)
        self.session['remote_ip'] = str(self.request.remote_ip)
        if user.has_permission('admin'):
            self.session.data['menu'] = "admin"
        else:
            self.session.data['menu'] = "user"
        self.session.save()

    def failed_login(self):
        ''' Called when someone fails to login '''
        logging.info("Failed login attempt from %s" % self.request.remote_ip)
        self.render('public/login.html',
            errors=["Failed login attempt, try again"]
        )


class RegistrationHandler(BaseHandler):
    ''' Handles the user registration process '''

    def get(self, *args, **kwargs):
        ''' Renders registration page '''
        self.render("public/registration.html", errors=None)

    def post(self, *args, **kwargs):
        ''' Attempts to create an account '''
        form = Form(
            username="Please enter a username",
            pass1="Please enter a password",
            pass2="Please confirm your password",
        )
        if not form.validate(self.request.arguments):
            self.render("public/registration.html", errors=form.errors)
        elif self.check_recaptcha():
            username = self.get_argument('username')
            if User.by_username(username) is not None:
                self.render('public/registration.html',
                    errors=['Account name already taken']
                )
            elif not 3 <= len(username) <= 15:
                self.render('public/registration.html',
                    errors=['Username must be 3-15 characters']
                )
            elif not self.get_argument('pass1') == self.get_argument('pass2'):
                self.render('public/registration.html',
                    errors=['Passwords do not match']
                )
            elif not (12 <= len(self.get_argument('pass1')) <= 100):
                self.render('public/registration.html',
                    errors=['Password must be 12-100 characters']
                )
            else:
                user = self.create_user(username, self.get_argument('pass1'))
                self.render("public/account_created.html", 
                    username=user.username
                )
        else:
            self.render("public/registration.html", errors=['Invalid captcha'])

    def create_user(self, username, password):
        user = User(username=unicode(username))
        self.dbsession.add(user)
        self.dbsession.flush()
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
                    self.get_argument('recaptcha_challenge_field', ''),
                    self.get_argument('recaptcha_response_field', ''),
                    self.config.recaptcha_private_key,
                    self.request.remote_ip
                )
            except:
                logging.exception("Recaptcha API called failed")
            if response is not None and response.is_valid:
                return True
            else:
                return False
        else:
            return True


class AboutHandler(BaseHandler):

    def get(self, *args, **kwargs):
        ''' Renders the about page '''
        self.render("public/about.html")
