# -*- coding: utf-8 -*-
'''
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
-------------

This sets up sqlalchemy.
For more information about sqlalchemy check out http://www.sqlalchemy.org/

'''


from sqlalchemy import create_engine
from sqlalchemy import Column, ForeignKey, Table
from sqlalchemy.types import Integer
from sqlalchemy.orm import sessionmaker
from models.BaseObject import BaseObject
from libs.ConfigManager import ConfigManager

metadata = BaseObject.metadata

config = ConfigManager.Instance()
db_connection = 'mysql://%s:%s@%s/%s' % (
    config.db_user, 
    config.db_password, 
    config.db_server, 
    config.db_name
)

# Setup the database session
engine = create_engine(db_connection)
setattr(engine, 'echo', config.log_sql)
Session = sessionmaker(bind=engine, autocommit=True)
dbsession = Session(autoflush=True)

algorithm_association_table = Table('weapon_system_to_algorithm', BaseObject.metadata,
    Column('weapon_system_id', Integer, ForeignKey('weapon_system.id'), nullable=False),
    Column('algorithm_id', Integer, ForeignKey('algorithm.id'), nullable=False)
)

# Association tables for the analysis
common_association_table = Table('analysis_common_to_password', 
    BaseObject.metadata,
    Column('password_id', Integer, ForeignKey('password.id'), nullable=False),
    Column('analysis_report_id', Integer, ForeignKey('analysis_report.id'), nullable=False)
)

lower_association_table = Table('analysis_lower_to_password', 
    BaseObject.metadata,
    Column('password_id', Integer, ForeignKey('password.id'), nullable=False),
    Column('analysis_report_id', Integer, ForeignKey('analysis_report.id'), nullable=False)
)

upper_association_table = Table('analysis_upper_to_password', 
    BaseObject.metadata,
    Column('password_id', Integer, ForeignKey('password.id'), nullable=False),
    Column('analysis_report_id', Integer, ForeignKey('analysis_report.id'), nullable=False)
)

numeric_association_table = Table('analysis_numeric_to_password', 
    BaseObject.metadata,
    Column('password_id', Integer, ForeignKey('password.id'), nullable=False),
    Column('analysis_report_id', Integer, ForeignKey('analysis_report.id'), nullable=False)
)

mixed_association_table = Table('analysis_mixed_to_password', 
    BaseObject.metadata,
    Column('password_id', Integer, ForeignKey('password.id'), nullable=False),
    Column('analysis_report_id', Integer, ForeignKey('analysis_report.id'), nullable=False)
)

lower_alpha_association_table = Table('analysis_lower_alpha_to_password', 
    BaseObject.metadata,
    Column('password_id', Integer, ForeignKey('password.id'), nullable=False),
    Column('analysis_report_id', Integer, ForeignKey('analysis_report.id'), nullable=False)
)

upper_alpha_association_table = Table('analysis_upper_alpha_to_password', 
    BaseObject.metadata,
    Column('password_id', Integer, ForeignKey('password.id'), nullable=False),
    Column('analysis_report_id', Integer, ForeignKey('analysis_report.id'), nullable=False)
)

mixed_alpha_association_table = Table('analysis_mixed_alpha_to_password', 
    BaseObject.metadata,
    Column('password_id', Integer, ForeignKey('password.id'), nullable=False),
    Column('analysis_report_id', Integer, ForeignKey('analysis_report.id'), nullable=False)
)

# Import the dbsession instance to execute queries
dbsession = Session(autoflush=True)

# Import models (or the tables won't get created)
from models.Job import Job
from models.Password import Password
from models.Permission import Permission
from models.User import User
from models.WeaponSystem import WeaponSystem
from models.Algorithm import Algorithm
from models.AnalysisReport import AnalysisReport
from models.PluginDetails import PluginDetails

# calling this will create the tables at the database
create_tables = lambda: (setattr(engine, 'echo', config.log_sql), metadata.create_all(engine))

# Bootstrap the database with some shit
def boot_strap():
    import setup.bootstrap