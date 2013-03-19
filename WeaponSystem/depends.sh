#!/bin/bash

# Copyright [2012]
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

if [ "$(id -u)" != "0" ]; then
	echo "[!] This script must be run as root." 1>&2
	exit 1
fi

echo "[*] Installing python, pip, and gcc ..."
# Newer versions of boost should work too, but have not been tested
apt-get install python python-dev python-pip build-essential libboost1.46-all-dev
pip install --upgrade pip

echo "[*] Installing Python libs ..."
/usr/local/bin/pip install rpyc yapsy

echo "[*] Setup Completed."
