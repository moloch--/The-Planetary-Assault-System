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
* For the server Debian/Ubuntu recommened, but should run on any Linux, OSX, or BSD system
* The clients can (theoretically) run on Windows, Linux, OSX, or BSD (only tested on Linux)

Setup
=======
See the [wiki](https://github.com/moloch--/The-Planetary-Assault-System/wiki)

Source Code
=============
```
-------------------------------------------------------------------------------
Language                     files          blank        comment           code
-------------------------------------------------------------------------------
C++                             29           1200           1378           8190
CSS                              5            642            124           5850
Python                          37            709            109           3213
HTML                            35             56             25           1116
C/C++ Header                    32            281            773           1043
Javascript                       6             18             19            341
make                             2             66             56            181
Bourne Shell                     4             14             41             37
-------------------------------------------------------------------------------
SUM:                           150           2986           2525          19971
-------------------------------------------------------------------------------
```
