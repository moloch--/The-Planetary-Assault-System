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
from string import ascii_letters, digits
from models import dbsession, BaseObject
from models import common_association_table, lower_association_table
from models import upper_association_table, numeric_association_table
from models import mixed_association_table, lower_alpha_association_table
from models import upper_alpha_association_table, mixed_alpha_association_table


class PasswordAnalysis(BaseObject):
    '''
    Complexity analysis of a job
    '''

    job_id = Column(Integer, ForeignKey('job.id'), nullable=False)
    common_passwords = relationship("PasswordHash",
                                    secondary=common_association_table, backref="Analysis")
    lower_case_passwords = relationship("PasswordHash", 
                                    secondary=lower_association_table, backref="Analysis")
    upper_case_passwords = relationship("PasswordHash", 
                                    secondary=upper_association_table, backref="Analysis")
    numeric_passwords = relationship("PasswordHash",
                                    secondary=numeric_association_table, backref="Analysis")
    mixed_case_passwords = relationship("PasswordHash", 
                                    secondary=mixed_association_table, backref="Analysis")
    lower_alpha_numeric_passwords = relationship("PasswordHash",
                                                 secondary=lower_alpha_association_table, backref="Analysis")
    upper_alpha_numeric_passwords = relationship("PasswordHash",
                                                 secondary=upper_alpha_association_table, backref="Analysis")
    mixed_alpha_numeric_passwords = relationship("PasswordHash",
                                                 secondary=mixed_alpha_association_table, backref="Analysis")
    __common__ = ['12345', '123456', '1234567', '12345678', '123456789', '654321', 'password',
                  'abc123', 'nicole', 'daniel', 'babygirl', 'monkey', 'iloveyou', 'princess',
                  'jessica', 'lovely', 'michael', 'ashley', 'qwerty', 'letmein', 'admin', 'fuck',
                  'fuckyou', 'dragon', 'pussy', 'baseball', 'football', '696969', 'mustang', '111111', '2000',
                  'shadow', 'master', 'jennifer', 'jordan', 'superman', 'love', 'sex', 'secret', 'god',
                  ]

    def analyze_all(self, passwords):
        ''' Run all analysis on a list of password objects '''
        for password in passwords:
            self.lower_case_passwords(password)
            self.upper_case_passwords(password)
            self.numeric_passwords(password)
            self.mixed_case_passwords(password)
            self.lower_alpha_numeric(password)
            self.upper_alpha_numeric(password)
            self.mixed_alpha_numeric(password)
        dbsession.add(self)
        dbsession.flush()

    def lower_case_passwords(self, password):
        ''' Returns all lower case passwords in the job '''
        if self.__regex__("^[a-z]*$", password.clear_text):
            self.lower_case.append(password)

    def upper_case_passwords(self, password):
        ''' Returns all upper case passwords in the job '''
        if self.__regex__("^[A-Z]*$", password.clear_text):
            self.upper_case.append(password)

    def numeric_passwords(self, password):
        ''' Returns all upper case passwords in the job '''
        if self.__regex__("^[0-9]*$", password.clear_text):
            self.numeric_passwords.append(password)

    def mixed_case_passwords(self, password):
        ''' Returns all mixed case passwords in the job '''
        contains_cases = self.__regex__(
            "^(?=.*[a-z])(?=.*[A-Z]).+$", password.clear_text
        )
        only_alpha = self.__regex__("^[a-zA-Z]*$", password.clear_text)
        if contains_cases and only_alpha:
            self.mixed_case.append(password)

    def lower_alpha_numeric_passwords(self, password):
        ''' Returns all lower case alpha-numeric passwords in the job '''
        contains_alph_numeric = self.__regex__(
            "^(?=.*[a-z])(?=.*[0-9]).+$", password.clear_text
        )
        only_alpha_numeric = self.__regex__("^[a-z0-9]*$", password.clear_text)
        if contains_alph_numeric and only_alpha_numeric:
            self.lower_alpha_numeric.append(password)

    def upper_alpha_numeric_passwords(self, password):
        ''' Returns all upper case alpha-numeric passwords in the job '''
        contains_alph_numeric = self.__regex__(
            "^(?=.*[A-Z])(?=.*[0-9]).+$", password.clear_text
        )
        only_alpha_numeric = self.__regex__("^[A-Z0-9]*$", password.clear_text)
        if contains_alph_numeric and only_alpha_numeric:
            self.upper_case.append(password)

    def mixed_alpha_numeric_passwords(self, password):
        ''' Returns all mixed case alpha-numeric passwords in the job '''
        contains_mixed_alpha_numeric = self.__regex__(
            "^(?=.*[a-z])(?=.*[A-Z])(?=.*[0-9]).+$", password.clear_text
        )
        only_mixed_alpha_numeric = self.__regex__(
            "^[a-zA-Z0-9]*$", password.clear_text
        )
        if contains_mixed_alpha_numeric and only_mixed_alpha_numeric:
            self.mixed_alpha_numeric.append(password)

    def common_passwords(self, password):
        ''' Returns all common passwords in the job '''
        if passwords.clear_text.lower() in self.__common__:
            self.common.append(password)

    def __regex__(self, expression, string):
        ''' Runs a regex returns a bool '''
        regex = re.compile(expression)
        return bool(regex.match(string))
