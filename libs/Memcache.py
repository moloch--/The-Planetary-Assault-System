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


import logging
import hashlib
import memcache

from base64 import b64encode


class FileCache(object):
    ''' Caches files in memcached '''

    MAX_FILE_SIZE = 1024 * 1024 * 10 # 10 Mb

    @classmethod
    def get(cls, file_path):
        ''' Loads file from disk or memory cache '''
        mem = memcache.Client(['127.0.0.1:11211'], debug=False)
        key = b64encode(file_path)
        data = mem.get(key)
        if data == None:
            f = open(file_path, 'r')
            data = f.read()
            f.close()
            if len(data) < cls.MAX_FILE_SIZE:
                if mem.set(key, data):
                    logging.info("Cached %s in memory." % file_path)
                else:
                    logging.error("Failed to properly cache image file.")
        return data

    @classmethod
    def delete(cls, file_path):
        ''' Remove file from memory cache '''
        mem = memcache.Client(['127.0.0.1:11211'], debug=False)
        mem.delete(b64encode(file_path))

    @classmethod
    def flush(cls):
        ''' Flush memory cache '''
        mem = memcache.Client(['127.0.0.1:11211'], debug=False)
        mem.flush_all()


class JsonCache(object):
    ''' Caches json objects using memcached '''
    
    @classmethod
    def get(cls, name):
        ''' Retrieves a json object '''
        mem = memcache.Client(['127.0.0.1:11211'], debug=False)
        return mem.get(cls.__key__(name))

    @classmethod
    def set(cls, name, data):
        ''' Saves a json object in memory '''
        mem = memcache.Client(['127.0.0.1:11211'], debug=False)
        mem.set(cls.__key__(name), data)

    @classmethod
    def delete(cls, name):
        ''' Remove file from memory cache '''
        mem = memcache.Client(['127.0.0.1:11211'], debug=False)
        mem.delete(cls.__key__(name))

    @classmethod
    def __key__(cls, data):
        ''' Creates the key '''
        md5 = hashlib.md5()
        md5.update("json-cache:" + str(data))
        return md5.hexdigest()

    @classmethod
    def flush(cls):
        ''' Flush memory cache '''
        mem = memcache.Client(['127.0.0.1:11211'], debug=False)
        mem.flush_all()

