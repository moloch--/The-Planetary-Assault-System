# -*- coding: utf-8 -*-
'''
Created on June 30, 2012

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


import json
import logging

from models import Job, User, Password, Algorithm
from string import ascii_letters, digits
from libs.Form import Form
from libs.Dispatch import Dispatch
from libs.SecurityDecorators import authenticated
from BaseHandlers import BaseHandler


class CreateJobHandler(BaseHandler):

    @authenticated
    def get(self, *args, **kwargs):
        ''' Renders the create job page '''
        self.render("cracking/jobs/create.html", errors=None)

    @authenticated
    def post(self, *args, **kwargs):
        ''' Creates a job based on the parameters '''
        form = Form(
            jobname="Please enter a job name",
            algorithm_uuid="Please select an algorithm",
            hashes="Please provide the target hashes",
        )
        if form.validate(self.request.arguments):
            algo = Algorithm.by_uuid(self.get_argument('algorithm_uuid'))
            user = self.get_current_user()
            if algo is None:
                self.render('cracking/jobs/create.html', 
                    errors=['Invalid algorithm']
                )
            elif Job.by_job_name(self.get_argument('jobname')) is not None:
                self.render('cracking/jobs/create.html', 
                    errors=['Duplicate job name']
                )
            else:
                job = self.create_job(user, algo)
                dispatch = Dispatch.Instance()
                dispatch.refresh()
                self.render("cracking/jobs/created.html", job=job)
        else:
            self.render('cracking/jobs/create.html', errors=form.errors)

    def create_job(self, user, algorithm):
        ''' Creates a job '''
        job = Job(
            user_id=user.id,
            job_name=unicode(self.get_argument('jobname')),
            algorithm_id=algorithm.id,
        )
        self.dbsession.add(job)
        self.dbsession.flush()
        hashes = self.parse_line_seperated(algorithm)
        for passwd in hashes:
            password_hash = Password(
                job_id=job.id,
                algorithm_id=algorithm.id,
                hexdigest=unicode(passwd),
            )
            self.dbsession.add(password_hash)
        self.dbsession.flush()
        return job

    def parse_line_seperated(self, algorithm, remove_duplicates=True):
        ''' Parses the provided hashes '''
        logging.info("Called ls parser....")
        hashes = []
        try:
            for hsh in self.get_argument('hashes').replace('\r', '').split('\n'):
                if len(hsh) == len(algorithm):
                    hashes.append(hsh)
            if remove_duplicates:
                hashes = list(set(hashes))
            return hashes
        except:
            logging.exception("Exception while parsing hashes.")
            self.render("cracking/create_job.html", 
                errors=["Failed to correctly parse hashes"]
            )

    def parse_pwdump(self):
        pass

    def parse_lst(self):
        pass


class QueuedJobsHandler(BaseHandler):

    @authenticated
    def get(self, *args, **kwargs):
        ''' Renders the cracking queue '''
        dispatch = Dispatch.Instance()
        dispatch.refresh()
        self.render("cracking/jobs/queued.html", 
            all_users=User.all_users(), 
            queue_size=Job.qsize()
        )

    @authenticated
    def post(self, *args, **kwargs):
        self.render("public/404.html")


class CompletedJobsHandler(BaseHandler):

    @authenticated
    def get(self, *args, **kwargs):
        ''' Renders the completed jobs page '''
        self.render("cracking/jobs/completed.html", 
            user=self.get_current_user()
        )


class DeleteJobHandler(BaseHandler):

    @authenticated
    def get(self, *args, **kwargs):
        self.render("public/404.html")

    @authenticated
    def post(self, *args, **kwargs):
        ''' Deletes a job from the database '''
        try:
            job_id = self.get_argument("job_id")
        except:
            self.render("cracking/jobs/ajax/error.html", message="Job does not exist")
            return
        job = Job.by_uuid(job_id)
        user = self.get_current_user()
        if job is not None and user is not None and job.user_id == user.id:
            dispather = Dispatch.Instance()
            if job.status == u'IN_PROGRESS':
                self.render("cracking/jobs/ajax/error.html",
                    message="Cannot delete job while it is in progress"
                )
            else:
                job_name = str(job.job_name)
                self.dbsession.delete(job)
                self.dbsession.flush()
                self.render("cracking/jobs/delete.html", job_name=job_name)
        else:
            logging.warn("%s attempted to delete a non-existant job, or a job he/she does not own." % user.username)
            self.render("cracking/jobs/ajax/error.html", message="Job does not exist")


class AjaxJobDetailsHandler(BaseHandler):

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
        job = Job.by_uuid(job_id)
        if job is None or user is None or user.id != job.user_id:
            logging.warn("%s submitted request for non-existant job, or does not own job." % user.username)
            self.render("cracking/jobs/ajax/error.html", 
                message="Job does not exist"
            )
        else:
            self.render("cracking/jobs/ajax/details.html", job=job)


class AjaxJobStatisticsHandler(BaseHandler):

    @authenticated
    def get(self, *args, **kwargs):
        ''' This method is called via ajax, renders job statistics '''
        try:
            job_id = self.get_argument("job_id")
        except:
            logging.warn("Bad argument passed to jobs ajax handler.")
            self.render("blank.html")
            return
        user = self.get_current_user()
        job = Job.by_uuid(job_id)
        if job == None or user == None or user.id != job.user_id:
            logging.warn("%s submitted request for non-existant job, or does not own job." % user.user_name)
            self.render("cracking/jobs/ajax/error.html", message="Job does not exist")
        else:
            self.render("cracking/jobs/ajax/statistics.html", job=job)


class AjaxJobDataHandler(BaseHandler):

    @authenticated
    def get(self, *args, **kwargs):
        ''' Called via AJAX, returns a JSON message containting stats data '''
        try:
            job_id = self.get_argument("job_id")
            job = Job.by_uuid(job_id)
            user = self.get_current_user()
            if job == None or user == None or job.user_id != user.id:
                raise ValueError("Invalid job, user, or the user does not own the job.")
            else:
                stats = job.stats_complexity()
                self.write(stats)
                self.finish()
        except:
            logging.warn("Bad argument passed to job data ajax handler.")
            self.write(json.dumps(['error', 0]))
            self.finish()


class DownloadHandler(BaseHandler):

    @authenticated
    def get(self, *args, **kwargs):
        self.render("public/404.html")
