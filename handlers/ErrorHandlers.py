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


from tornado.web import RequestHandler
from handlers.BaseHandlers import BaseHandler

class NotFoundHandler(BaseHandler):

    def get(self, *args, **kwargs):
        ''' Renders the "404" page (returns 200 status) '''
        self.render("public/404.html")

    def post(self, *args, **kwargs):
        ''' Renders the "404" page (returns 200 status) '''
        self.render("public/404.html")


class PasswdHandler(BaseHandler):

    def get(self, *args, **kwargs):
        ''' Renders a fake /etc/passwd file '''
        self.render("public/passwd.html")

    def post(self, *args, **kwargs):
        ''' Renders a fake /etc/passwd file '''
        self.render("public/passwd.html")


class UnauthorizedHandler(BaseHandler):

    def get(self, *args, **kwargs):
        ''' Renders the 403 page '''
        self.render("public/403.html")

    def post(self, *args, **kwargs):
        ''' Renders the 403 page '''
        self.render("public/403.html")


class PhpHandler(BaseHandler):

    def get(self, *args, **kwargs):
        ''' Renders the php page '''
        self.render("public/php.html")

    def post(self, *args, **kwargs):
        ''' Same as GET '''
        self.render("public/php.html")


class RobotsHandler(BaseHandler):

    def get(self, *args, **kwargs):
        ''' Renders a fake robots.txt file to screw with people/bots '''
        self.set_header('Content-Type', 'text/plain')
        self.write("# Disallow for extra security\n")  # lol
        self.write("Disallow: /admin\n")
        self.write("Disallow: /admin/modify_privs\n")
        self.write("Disallow: /admin/modify_jobs\n")
        self.write("Disallow: /admin/display_private_keys\n")
        self.write("Disallow: /admin/shells\n")
        self.write("Disallow: /admin/ssh_keys\n")
        self.write("Disallow: /admin/edit_users\n")
        self.write("Disallow: /admin/sql_admin\n")
        self.write("Disallow: /admin/passwords\n")
        self.write("Disallow: /admin/ajax_api\n")
        self.write("Disallow: /admin/rpc_api\n")
        self.write("Disallow: /admin/xmlrpc\n")
        self.write("Disallow: /admin/exec_cmd\n")
        # Never let bots near your db interface!
        self.write("\n# Prevent bots from querying the db\n")
        self.write("Disallow: /ajax/sql\n")
        self.finish()
