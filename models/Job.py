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
from libs.Memcache import MemoryCache
from models import dbsession
from models.PasswordHash import PasswordHash
from models.BaseObject import BaseObject
from string import ascii_letters, digits


class Job(BaseObject):

    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    _job_name = Column(Unicode(64), unique=True, nullable=False)
    job_name = synonym('_job_name', descriptor=property(
        lambda self: self._job_name,
        lambda self, job_name: setattr(self, '_job_name',
                                       self.__class__._filter_string(job_name, "-_ "))
    ))
    status = Column(Unicode(64), default=u"NOT_STARTED",
                    nullable=False)  # NOT_STARTED / IN_PROGRESS / COMPLETED
    priority = Column(Integer, default=1, nullable=False)
    completed = Column(Boolean, default=False, nullable=False)
    hashes = relationship("PasswordHash", backref=backref(
        "Job", lazy="joined"), cascade="all, delete-orphan")
    algorithm_id = Column(Integer, ForeignKey('algorithm.id'), nullable=False)
    started = Column(DateTime)
    finished = Column(DateTime)

    @classmethod
    def by_id(cls, job_id):
        """ Return the job object whose user id is 'job_id' """
        return dbsession.query(cls).filter_by(id=job_id).first()

    @classmethod
    def by_uuid(cls, job_uuid):
        """ Return the job object whose user uuid is 'job_uuid' """
        return dbsession.query(cls).filter_by(uuid=unicode(job_uuid)).first()

    @classmethod
    def by_job_name(cls, job_name):
        """ Return the job object whose user name is 'job_name' """
        return dbsession.query(cls).filter_by(name=unicode(job_name)).first()

    @classmethod
    def qsize(cls):
        ''' Returns the number of incompelte jobs left in the data base '''
        return dbsession.query(cls).filter_by(status=u"NOT_STARTED").count()

    @classmethod
    def queue(cls):
        ''' Pop a job off the "queue" or return None if not jobs remain '''
        return dbsession.query(cls).filter_by(status=u"NOT_STARTED").order_by(cls.created).all()

    @classmethod
    def _filter_string(cls, string, extra_chars=""):
        char_white_list = ascii_letters + digits + extra_chars
        return filter(lambda char: char in char_white_list, string)

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

    def stats_length(self):
        ''' Returns stats on password length '''
        if self.cached_length_analysis == None:
            results = {}
            for password in self.solved_hashes:
                if len(password.plain_text) in self.results.keys():
                    results[len(password.plain_text)] += 1
                else:
                    results[len(password.plain_text)] = 1
            self.cached_length_analysis = json.dumps(results)
            dbsession.add(self)
            dbsession.flush()
        return self.cached_length_analysis

    def stats_solved(self):
        ''' Returns a stats on how many hases with the job were solved/unsolved '''
        if MemoryCache.get(self.uuid + 'solved') == None:
            solved_analysis = json.dumps([
                {'Solved': len(self.solved_hashes)},
                {'Unsolved': len(self.unsolved_hashes)},
            ])
            MemoryCache.set(self.uuid + 'solved', solved_analysis)
        return MemoryCache.get(self.uuid + 'solved')

    def stats_common(self):
        ''' Returns stats on how many solved hash's plain text was a common password '''
        if MemoryCache.get(self.uuid + 'common') == None:
            common_analysis = json.dumps([
                {'Common': len(self.common_passwords)},
                {'Uncommon': len(self.hashes) - len(self.common_passwords)},
            ])
            MemoryCache.set(self.uuid + 'common', common_analysis)
        return MemoryCache.get(self.uuid + 'common')

    def stats_complexity(self):
        ''' Returns stats on solved hash's plain text complexity '''
        if MemoryCache.get(self.uuid + 'complexity') == None:
            complexity = []
            if 0 < len(self.lower_case_passwords):
                complexity.append(
                    {'Lower Case': len(self.lower_case_passwords)})
            if 0 < len(self.upper_case_passwords):
                complexity.append(
                    {'Upper Case': len(self.upper_case_passwords)})
            if 0 < len(self.numeric_passwords):
                complexity.append({'Numeric': len(self.numeric_passwords)})
            if 0 < len(self.mixed_case_passwords):
                complexity.append(
                    {'Mixed Case': len(self.mixed_case_passwords)})
            if 0 < len(self.lower_alpha_numeric_passwords):
                complexity.append({'Lower Case Alpha-numeric':
                                   len(self.lower_alpha_numeric_passwords)})
            if 0 < len(self.upper_alpha_numeric_passwords):
                complexity.append({'Upper Case Alpha-numeric':
                                   len(self.upper_alpha_numeric_passwords)})
            if 0 < len(self.mixed_alpha_numeric_passwords):
                complexity.append({'Mixed Case Alpha-numeric':
                                   len(self.mixed_alpha_numeric_passwords)})
            MemoryCache.set(self.uuid + 'complexity', json.dumps(complexity))
        return MemoryCache.get(self.uuid + 'complexity')

    def save_results(self, results):
        ''' Save the results of the cracking session to the database '''
        for password in self.hashes:
            try:
                password.plain_text = unicode(results[password.digest])
                if results[password.digest] != "<Not Found>":
                    password.solved = True
                dbsession.add(password)
            except KeyError:
                logging.error("A database hash is missing from the result set (%s)" %
                              (password.digest,))
        dbsession.flush()

    def to_list(self):
        ''' Returns all hash digests as a Python list '''
        return [hsh.cipher_text for hsh in self.hashes]

    def __len__(self):
        ''' Returns the number of hashes in the job '''
        return len(self.hashes)

    def __str__(self):
        ''' Returns name when str() is called '''
        return unicode(self.name)

    def __repr__(self):
        ''' Repr impl '''
        return "<(%d) %s: hashes(%d), completed(%s)>" % (self.id, self.name, len(self), str(self.completed))
