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

from string import ascii_letters, digits
from tornado.web import RequestHandler
from BaseHandlers import UserBaseHandler
from recaptcha.client import captcha
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

    def get(self, *args, **kwargs):
        ''' Renders the login page '''
        self.render("public/login.html", message="User Authentication")

    def post(self, *args, **kwargs):
        ''' Checks login creds '''
        try:
            user_name = self.get_argument('username')
            user = User.by_user_name(user_name)
        except:
            self.render(
                'public/login.html', message="Type in an account name")
            return
        try:
            password = self.get_argument('password')
        except:
            self.render('public/login.html', message="Type in a password")
            return
        response = None
        try:
            response = captcha.submit(
                self.get_argument('recaptcha_challenge_field'),
                self.get_argument('recaptcha_response_field'),
                self.application.settings['recaptcha_private_key'],
                self.request.remote_ip
            )
        except:
            self.render('public/login.html', 
                        message="Please fill out recaptcha!")
            return
        if response == None or not response.is_valid:
            self.render('public/login.html', message="Invalid captcha")
        elif user != None and user.validate_password(password):
            if not user.approved:
                self.render("public/login.html", 
                            message="Your account must be approved by an administrator.")
            else:
                logging.info("Successful login: %s from %s" %
                             (user.user_name, self.request.remote_ip))
                session_manager = SessionManager.Instance()
                sid, session = session_manager.start_session()
                self.set_secure_cookie(name='auth',
                                       value=str(sid), expires_days=1, HttpOnly=True)
                session.data['user_name'] = str(user.user_name)
                session.data['ip'] = str(self.request.remote_ip)
                if user.has_permission('admin'):
                    session.data['menu'] = "admin"
                else:
                    session.data['menu'] = "user"
                self.redirect('/user')
        else:
            logging.info(
                "Failed login attempt from %s" % self.request.remote_ip)
            self.render('public/login.html',
                        message="Failed login attempt, try again")


class RegistrationHandler(RequestHandler):
    ''' Handles the user registration process (surprise!) '''

    def initialize(self, dbsession):
        self.dbsession = dbsession

    def get(self, *args, **kwargs):
        ''' Renders registration page '''
        self.render("public/registration.html", 
                    message="Fill out the form below")

    def post(self, *args, **kwargs):
        ''' Attempts to create an account, with shitty form validation '''
        # Check user_name parameter
        try:
            user_name = self.get_argument('username')
        except:
            self.render('public/registration.html',
                        message='Please enter a valid account name')
        # Check password parameter
        try:
            password1 = self.get_argument('pass1')
            password2 = self.get_argument('pass2')
            if password1 != password2:
                self.render('public/registration.html',
                            message='Passwords did not match')
            else:
                password = password1
        except:
            self.render('public/registration.html',
                        message='Please enter a password')
        # Get recaptcha results
        try:
            response = captcha.submit(
                self.get_argument('recaptcha_challenge_field'),
                self.get_argument('recaptcha_response_field'),
                self.application.settings['recaptcha_private_key'],
                self.request.remote_ip,)
        except:
            self.render('public/registration.html',
                        message="Please fill out recaptcha")
        # Strip any non-white listed chars
        char_white_list = ascii_letters + digits
        user_name = filter(lambda char: char in char_white_list, user_name)
        # Check parameters
        if not response.is_valid:
            self.render('public/registration.html', 
                        message='Invalid Recaptcha!')
        elif User.by_user_name(user_name) != None:
            self.render('public/registration.html',
                        message='Account name already taken')
        elif len(user_name) < 3 or 15 < len(user_name):
            self.render('public/registration.html',
                        message='Username must be 3-15 characters')
        elif not (12 <= len(password) <= 100):
            self.render('public/registration.html',
                        message='Password must be 12-100 characters')
        else:
            user = User(
                user_name=unicode(user_name),
            )
            # Create user, init class variables
            self.dbsession.add(user)
            self.dbsession.flush()
            # Set password for user
            user.password = password
            self.dbsession.add(user)
            self.dbsession.flush()
            self.render("public/account_created.html", user=user)


class AboutHandler(RequestHandler):

    def get(self, *args, **kwargs):
        ''' Renders the about page '''
        self.render("public/about.html")
