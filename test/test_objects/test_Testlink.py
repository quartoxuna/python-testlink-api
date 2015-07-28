#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@author: Kai Borowiak
@summary: TestSuite for testlink.objects.Testlink
"""

# IMPORTS
import unittest
import inspect
from mock import Mock, MagicMock, patch

from .. import *

from testlink.api import Testlink_XML_RPC_API
from testlink.objects import Testlink, TestProject
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

	def test_getVersion(self):
		"""Version String"""
		tl = Testlink(URL,DEVKEY)
		tl._api._tl_version = "1.2.3"
		self.assertEquals(tl.getVersion(), "1.2.3")

	@patch('testlink.objects.Testlink.iterTestProject')
	def test_getTestProject(self,p1):
		"""'getTestProject'"""
		# Generate some test data
		args = randput()
		kwargs = randict("foo","bar")
		return_value = randput()

		# Init Testlink
		tl = Testlink(URL,DEVKEY)

		# Mock the eqivalent iterator
		p1.return_value = generate(return_value)

		# Check for normalize call, because there would
		# be no single return value otherwise
		self.assertEquals(tl.getTestProject(name=args,**kwargs),return_value)

		# Check correct parameter forwarding
		tl.iterTestProject.assert_called_with(args,**kwargs)

	@patch('testlink.api.Testlink_XML_RPC_API.getTestProjectByName')
	@patch('testlink.api.Testlink_XML_RPC_API.getProjects')
	def test_iterTestProject(self,getProjects,getTestProjectByName):
		"""'iterTestProject'"""
		# Generate some test data
		test_data = [randict("name","notes"),randict("name","notes")]

		# Init Testlink
		tl = Testlink(URL,DEVKEY)

		# Mock internal methods
		getProjects.return_value = test_data
		getTestProjectByName.return_value = test_data[1]

		# Check for generator function
		self.assertTrue(inspect.isgeneratorfunction(tl.iterTestProject))

		# Check calls and result with shortcut usage
		project = tl.iterTestProject(test_data[1]['name']).next()
		getTestProjectByName.assert_called_with(test_data[1]['name'])
		self.assertFalse(getProjects.called)
		self.assertTrue(isinstance(project,TestProject))
		self.assertEqual(project.name, test_data[1]['name'])
		self.assertEqual(project.notes, test_data[1]['notes'])

		getProjects.reset_mock()
		getTestProjectByName.reset_mock()

		project = tl.iterTestProject(**test_data[1]).next()
		getProjects.assert_called_with()
		self.assertFalse(getTestProjectByName.called)
		self.assertTrue(isinstance(project,TestProject))
		self.assertEqual(project.name, test_data[1]['name'])
		self.assertEqual(project.notes, test_data[1]['notes'])
