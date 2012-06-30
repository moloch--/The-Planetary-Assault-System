
import os
import logging

from models import Job, User, PasswordHash
from string import ascii_letters, digits
from libs.Session import SessionManager
from libs.SecurityDecorators import authenticated
from BaseHandlers import UserBaseHandler

class CreateJobHandler(UserBaseHandler):

    @authenticated
    def get(self, *args, **kwargs):
        ''' Renders the create jbo page '''
        self.render("user/create_job.html", message = "Create a new job")

    @authenticated
    def post(self, *args, **kwargs):
        ''' Creates a job based on the parameters '''
        # Get job name
        try:
            job_name = self.filter_string(self.get_argument('jobname'))
            if len(job_name) < 3 or 15 < len(job_name):
                raise ValueError
        except:
            self.render("user/create_job.html", message = "Invalid Job Name")
            return
        # Get algorithm
        try:
            algorithm = self.get_argument('algorithm')
            if not algorithm in self.application.settings['rainbow_tables'].keys():
                raise ValueError
        except:
            self.render("user/create_job.html", message = "Invalid algorithm")
            return
        # Get hashes
        try:
            hashes = self.get_argument('hashes').replace('\r', '').split('\n')
        except:
            self.render("user/create_job.html", message = "No Hashes")
            return
        user = self.get_current_user()
        print '[**] Current User', user, type(user)
        job = Job(
            user_id = user.id,
            name = unicode(job_name),
        )
        self.dbsession.add(job)
        self.dbsession.flush()
        for passwd in hashes:
            if len(passwd) != 0:
                password_hash = PasswordHash(
                    job_id = job.id,
                    algorithm = unicode(algorithm),
                    digest = unicode(passwd),
                )
                self.dbsession.add(password_hash)
        self.dbsession.flush()
        self.render("user/created_job.html", count = len(job))

    def filter_string(self, string):
        char_white_list = ascii_letters + digits
        return filter(lambda char: char in char_white_list, string)