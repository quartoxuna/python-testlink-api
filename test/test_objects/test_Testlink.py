#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@author: Kai Borowiak
@summary: TestSuite for testlink.objects.Testlink
"""

# IMPORTS
import unittest
from mock import Mock, MagicMock, patch

from .. import randput, randict, ServerMock

from testlink.api import Testlink_XML_RPC_API
from testlink.objects import Testlink
from testlink.exceptions import *
from testlink.enums import *

URL = "http://localhost/"
DEVKEY = randput(50)

class TestlinkTests(unittest.TestCase):

	def __init__(self,*args,**kwargs):
		super(TestlinkTests,self).__init__(*args,**kwargs)
		self._testMethodDoc = "Testlink: " + self._testMethodDoc

	def setUp(self):
		"""Needed to connect to a mocked Server endpoint in each test"""
		self._patcher = patch('xmlrpclib.ServerProxy',new=ServerMock,spec=True)
		self._mock_server = self._patcher.start()
		self._api = Testlink_XML_RPC_API(URL + "lib/api/xmlrpc.php")
		self._api._proxy = self._mock_server

	def tearDown(self):
		self._patcher.stop()

	def test_apiType(self):
		"""API Type settings"""
		tl = Testlink(URL,DEVKEY)
		self.assertTrue(isinstance(tl._api,Testlink_XML_RPC_API))
		tl = Testlink(URL,DEVKEY,APIType.XML_RPC)
		self.assertTrue(isinstance(tl._api,Testlink_XML_RPC_API))

	def test_devKeySetting(self):
		"""DevKey Storage"""
		tl = Testlink(URL,DEVKEY)
		self.assertEquals(tl._api._devkey,DEVKEY)

	@patch('testlink.api.Testlink_XML_RPC_API._query')
	def test_getVersion(self,mock):
		"""Version String"""
		mock.return_value = "1.2.3"
		tl = Testlink(URL,DEVKEY)
		self.assertEquals(tl.getVersion(), "1.2.3")
