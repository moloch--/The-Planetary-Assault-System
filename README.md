The-Planetary-Assault-System
============================
Fire and forget password cracking and complexity analysis.  The Planetary assault system is basically a role-you-own password cracking CPU/GPU cluster managerment system.  Additionally it can preform character and word frequency analysis to improve cracking results.  It's a mix of Python, C++, and JavaScript. 

__This is a work in progress, please keep that in mind!__

The “Planetary Assault System” is a software project that aims to allow small organizations to roll their own private password cracking cloud/cluster, which can combine a variety of password cracking methods such as time-memory tradeoff, wordlists, and brute-forcing.  The system can also preform word and character frequency analysis of cracked passwords and leverage that information to crack additional passwords from the same organization.  The idea being that password policies force users to create similar passwords, and by leveraging this information the system automatically can adapt its attack to target the organization’s policy.  The entire system is automated after you submit the hashes.  It’s a work in progress, and is open source.

Requirements
===============
* Python v2.5.x - v2.7.x
* MySQL v5.5.x
* Tornado Web v2.x
* SQL Alchemy v0.7.x
* RPyC v3.x
* Debian/Ubuntu recommened, but should run on any Linux or BSD system

Orbital Control Setup
=====================
* Run __/setup/depends.sh__ (Debian/Ubuntu only) to automatically install all required libs
* Edit __PlanetaryAssaultSystem.cfg__
	* Set __debug__ to __false__ for production systems
	* Edit database settings, set user and/or pass to __RUNTIME__ for production systems
* Run __"python . create bootstrap"__ to initialize the database, you only need to run this once
* Run __"python . serve"__ to start the application
* Run __"python . recovery"__  to start a recovery console (reset account passwords, etc)

Weapon System Setup
====================
* Edit the RainbowTables section to point to your rainbow table directories
	* You can download tables from: http://freerainbowtables.com/en/tables2/
* Setup SSH to allow key auth with a __limited__ user account
	* Recommended that you disable password auth entirely
* Pair with orbital command via admin interface
* Linux only at this point, supports both x86/x64
