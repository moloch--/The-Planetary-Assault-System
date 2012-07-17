# -*- coding: utf-8 -*-
"""
defines a special ApplicationTest class.
inheriate it inorder to write tests for the application
"""

from handlers import application
from libs.form_xcode import form_encode
from tornado.httpclient import HTTPRequest
from tornado.testing import AsyncHTTPTestCase

# ApplicationTest
# ---------------


class ApplicationTest(AsyncHTTPTestCase):
    pass

# -------------------------
#  import your tests here!
# -------------------------
#from tests.rootController import RootTest
