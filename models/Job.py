# -*- coding: utf-8 -*-
'''
Created on Mar 12, 2012

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


import json
import logging

from sqlalchemy import Column, ForeignKey, and_
from sqlalchemy.orm import synonym, relationship, backref
from sqlalchemy.types import Unicode, Integer, Boolean, DateTime
from models import dbsession
from models.PasswordHash import PasswordHash
from models.BaseObject import BaseObject

class Job(BaseObject):

    user_id = Column(Integer, ForeignKey('user.id'), nullable = False)
    name = Column(Unicode(64), unique = True, nullable = False)
    priority = Column(Integer, default = 1,  nullable = False)
    completed = Column(Boolean, default = False, nullable = False)
    hashes = relationship("PasswordHash", backref = backref("Job", lazy = "joined"), cascade = "all, delete-orphan")
    cached_complexity_analysis = Column(Unicode(256))
    cached_solved_analysis = Column(Unicode(256))
    cached_common_analysis = Column(Unicode(256))
    started = Column(DateTime)
    finished = Column(DateTime)

    @classmethod
    def by_id(cls, job_id):
        """ Return the job object whose user id is 'job_id' """
        return dbsession.query(cls).filter_by(id = job_id).first()
    
    @classmethod
    def by_job_name(cls, job_name):
        """ Return the job object whose user name is 'job_name' """
        return dbsession.query(cls).filter_by(name = unicode(job_name)).first()

    @classmethod
    def qsize(cls):
        ''' Returns the number of incompelte jobs left in the data base '''
        return dbsession.query(cls).filter_by(completed = False).count()

    @classmethod
    def pop(cls):
        ''' Pop a job off the "queue" or return None if not jobs remain '''
        return dbsession.query(cls).filter_by(completed = False).order_by(cls.created).first()

    @property
    def solved_hashes(self):
        ''' Returns only solved hashes in the job '''
        return filter(lambda password_hash: password_hash.solved == True, self.hashes)

    @property
    def unsolved_hashes(self):
        ''' Returns only unsolved hashes in the job '''
        return filter(lambda password_hash: password_hash.solved == False, self.hashes)

    @property
    def lower_case_passwords(self):
        ''' Returns all lower case passwords in the job '''
        return filter(lambda password_hash: password_hash.lower_case == True, self.solved_hashes)

    @property
    def upper_case_passwords(self):
        ''' Returns all upper case passwords in the job '''
        return filter(lambda password_hash: password_hash.upper_case == True, self.solved_hashes)

    @property
    def numeric_passwords(self):
        ''' Returns all upper case passwords in the job '''
        return filter(lambda password_hash: password_hash.numeric == True, self.solved_hashes)

    @property
    def mixed_case_passwords(self):
        ''' Returns all mixed case passwords in the job '''
        return filter(lambda password_hash: password_hash.mixed_case == True, self.solved_hashes)

    @property
    def lower_alpha_numeric_passwords(self):
        ''' Returns all lower case alpha-numeric passwords in the job '''
        return filter(lambda password_hash: password_hash.lower_alpha_numeric == True, self.solved_hashes)

    @property
    def upper_alpha_numeric_passwords(self):
        ''' Returns all upper case alpha-numeric passwords in the job '''
        return filter(lambda password_hash: password_hash.upper_alpha_numeric == True, self.solved_hashes)

    @property
    def mixed_alpha_numeric_passwords(self):
        ''' Returns all mixed case alpha-numeric passwords in the job '''
        return filter(lambda password_hash: password_hash.mixed_alpha_numeric == True, self.solved_hashes)

    @property
    def common_passwords(self):
        ''' Returns all common passwords in the job '''
        return filter(lambda password_hash: password_hash.is_common == True, self.solved_hashes)

    def stats_solved(self):
        ''' Returns a stats on how many hases with the job were solved/unsolved '''
        if self.cached_solved_analysis == None:
            self.cached_solved_analysis = json.dumps([
                {'Solved': len(self.solved_hashes)}, 
                {'Unsolved': len(self.unsolved_hashes)}
            ])
            dbsession.add(self)
            dbsession.flush()
        return self.cached_solved_analysis

    def stats_common(self):
        ''' Returns stats on how many solved hash's plain text was a common password '''
        if self.cached_common_analysis == None:
            self.cached_common_analysis = json.dumps([
                {'Common': len(self.common_passwords)}, 
                {'Uncommon': len(self.hashes) - len(self.common_passwords)}
            ])
            dbsession.add(self)
            dbsession.flush()
        return self.cached_common_analysis

    def stats_complexity(self):
        ''' Returns stats on solved hash's plain text complexity '''
        if self.cached_complexity_analysis == None:
            complexity = []
            if 0 < len(self.lower_case_passwords):
                complexity.append({'Lower Case': len(self.lower_case_passwords)})
            if 0 < len(self.upper_case_passwords):
                complexity.append({'Upper Case': len(self.upper_case_passwords)})
            if 0 < len(self.numeric_passwords):
                complexity.append({'Numeric': len(self.numeric_passwords)})
            if 0 < len(self.mixed_case_passwords):
                complexity.append({'Mixed Case': len(self.mixed_case_passwords)})
            if 0 < len(self.lower_alpha_numeric_passwords):
                complexity.append({'Lower Case Alpha-numeric': len(self.lower_alpha_numeric_passwords)})
            if 0 < len(self.upper_alpha_numeric_passwords):
                complexity.append({'Upper Case Alpha-numeric': len(self.upper_alpha_numeric_passwords)})
            if 0 < len(self.mixed_alpha_numeric_passwords):
                complexity.append({'Mixed Case Alpha-numeric': len(self.mixed_alpha_numeric_passwords)})
            self.cached_complexity_analysis = json.dumps(complexity)
            dbsession.add(self)
            dbsession.flush()
        return self.cached_complexity_analysis

    def save_results(self, results):
        ''' Save the results of the cracking session to the database '''
        for password in self.hashes:
            try:
                password.plain_text = unicode(results[password.digest])
                if results[password.digest] != "<Not Found>":
                    password.solved = True
                dbsession.add(password)
            except KeyError:
                logging.error("A database hash is missing from the result set (%s)" % (password.digest))
        dbsession.flush()

    def to_list(self):
        ''' Returns all hash digests as a Python list '''
        ls = []
        for passwordHash in self.hashes:
            ls.append(passwordHash.digest.encode('ascii', 'ignore'))
        return ls

    def __len__(self):
        ''' Returns the number of hashes in the job '''
        return len(self.hashes)

    def __str__(self):
        ''' Returns name when str() is called '''
        return self.name