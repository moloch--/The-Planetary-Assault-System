# -*- coding: utf-8 -*-
'''
Created on June 30, 2012

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

from models import Job, User, PasswordHash
from string import ascii_letters, digits
from libs.Dispatch import Dispatch
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
            hashes = list(set(hashes)) # Remove any duplicates
            if len(hashes) == 0:
                raise ValueError
        except:
            self.render("user/create_job.html", message = "No Hashes")
            return
        user = self.get_current_user()
        job = Job(
            user_id = user.id,
            name = unicode(job_name),
        )
        self.dbsession.add(job)
        self.dbsession.flush()
        for passwd in hashes:
            if 0 < len(passwd) <= 64:
                password_hash = PasswordHash(
                    job_id = job.id,
                    algorithm = unicode(algorithm),
                    digest = unicode(passwd),
                )
                self.dbsession.add(password_hash)
        self.dbsession.flush()
        self.start_job(job)
        self.render("user/created_job.html", count = len(job))

    def filter_string(self, string):
        ''' Removes erronious chars from a string '''
        char_white_list = ascii_letters + digits
        return filter(lambda char: char in char_white_list, string)

    def start_job(self, job):
        ''' Sends the new job to the dispather '''
        dispather = Dispatch.Instance()
        dispather.start(job.id)

class QueuedJobsHandler(UserBaseHandler):

    @authenticated
    def get(self, *args, **kwargs):
        ''' Renders the cracking queue '''
        self.render("user/queuedjobs.html", all_users = User.get_all(), queue_size = Job.qsize())

class CompletedJobsHandler(UserBaseHandler):

    @authenticated
    def get(self, *args, **kwargs):
        ''' Renders the completed jobs page '''
        self.render("user/completedjobs.html", user = self.get_current_user())

class DeleteJobHandler(UserBaseHandler):

    @authenticated
    def post(self, *args, **kwargs):
        ''' Deletes a job from the database '''
        pass

class AjaxJobDetailsHandler(UserBaseHandler):

    @authenticated
    def get(self, *args, **kwargs):
        ''' This method is called via ajax, renders job details '''
        try:
            job_id = self.get_argument("job_id")
        except:
            logging.warn("Bad argument passed to jobs ajax handler.")
            self.render("blank.html")
            return
        user = self.get_current_user()
        job = Job.by_id(job_id)
        if job == None or user.id != job.user_id:
            logging.warn("%s submitted request for non-existant job, or does not own job." % user.user_name)
            self.render("user/ajax_error.html", message = "Job does not exist")
        else:
            self.render("user/ajax_jobdetails.html", job = job)

class AjaxJobStatisticsHandler(UserBaseHandler):

    @authenticated
    def get(self, *args, **kwargs):
        ''' This method is called via ajax, renders job statistics'''
        try:
            job_id = self.get_argument("job_id")
        except:
            logging.warn("Bad argument passed to jobs ajax handler.")
            self.render("blank.html")
            return
        user = self.get_current_user()
        job = Job.by_id(job_id)
        if job == None or user.id != job.user_id:
            logging.warn("%s submitted request for non-existant job, or does not own job." % user.user_name)
            self.render("user/ajax_error.html", message = "Job does not exist")
        else:
            self.render("user/ajax_jobstatistics.html", job = job)

class DownloadHandler(UserBaseHandler):

    @authenticated
    def post(self, *args, **kwargs):
        '''  '''
        pass