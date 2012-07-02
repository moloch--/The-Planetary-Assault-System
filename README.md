The-Planetary-Assault-System
============================
Automated password cracking and entropy analysis.

Requirements
===============
* Python v2.5.x - v2.7.x
* MySQL v5.x
* Tornado Web v1.x
* SQL Alchemy v0.7.8
* Debian/Ubuntu recommened, but should run on any Linux/BSD system

Setup
========
* Run __/setup/depends.sh__ (Debian/Ubuntu only) to automatically install all required libs
* Setup MySQL connection string in __/models/\_\_init\_\_.py__
* Edit __PlanetaryAssaultSystem.cfg__ and set __debug__ to __false__
* Run __"python . create bootstrap"__ to initialize the database, you only need to run this once
* Run __"python . serve"__ to start the server
