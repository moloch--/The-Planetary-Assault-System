The-Planetary-Assault-System
============================
Fire and forget password cracking and complexity analysis.

Requirements
===============
* Python v2.5.x - v2.7.x
* MySQL v5.5.x
* Tornado Web v2.x
* SQL Alchemy v0.7.x
* RPyC v3.x
* Debian/Ubuntu recommened, but should run on any Linux or BSD system

Setup
========
* Run __/setup/depends.sh__ (Debian/Ubuntu only) to automatically install all required libs
* Edit __PlanetaryAssaultSystem.cfg__ be sure to set __debug__ to __false__ for production systems
	* Edit the RainbowTables section to point to your rainbow table directories
	* Edit threads, this is the max number of threads used for cracking
	* Edit database settings, set user/pass to __RUNTIME__ for production systems
* Run __"python . create bootstrap"__ to initialize the database, you only need to run this once
* Run __"python . serve"__ to start the server
