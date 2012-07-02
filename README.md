The-Planetary-Assault-System
============================
Automated password cracking and entropy analysis.

Requirements
===============
* Python 2.5.x - 2.7.x
* Debian/Ubuntu recommened, but should run on any Linux/BSD system

Setup
========
* Run /setup/depends.sh (Debian/Ubuntu only)
* Setup MySQL connection string in /models/\_\_init\_\_.py
* Edit PlanetaryAssaultSystem.cfg and set ENVIRONMENT to 'prod' in /setup/bootstrap.py
* Run "python . create bootstrap" to initialize the database, you only need to run this once
* Run "python . serve" to start the server
