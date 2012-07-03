The-Planetary-Assault-System
============================
Automated password cracking and entropy analysis.

Requirements
===============
* Python v2.5.x - v2.7.x
* MySQL v5.x
* Tornado Web v2.x
* SQL Alchemy v0.7.8
* Debian/Ubuntu recommened, but should run on any Linux/BSD system

Setup
========
* Run __/setup/depends.sh__ (Debian/Ubuntu only) to automatically install all required libs
* Setup MySQL connection string in __/models/\_\_init\_\_.py__
* Edit __PlanetaryAssaultSystem.cfg__ be sure to set __debug__ to __false__ for production systems
	* Edit the RainbowTables section to point to your rainbow table directories
	* Edit threads, this is the max number of threads used for cracking
* Run __"python . create bootstrap"__ to initialize the database, you only need to run this once
* Run __"python . serve"__ to start the server
