The-Planetary-Assault-System
============================
Automated password cracking and entropy analysis.

Requirements
===============
* Python 2.5.x - 2.7.x
* Debian/Ubuntu recommened, but should run on any Linux/BSD system

Setup
========
* Run __/setup/depends.sh__ (Debian/Ubuntu only)
* Setup MySQL connection string in __/models/\_\_init\_\_.py__
* Edit __PlanetaryAssaultSystem.cfg__ and set __ENVIRONMENT__ to __'prod'__ in __/setup/bootstrap.py__
* Run __"python . create bootstrap"__ to initialize the database, you only need to run this once
* Run __"python . serve"__ to start the server
