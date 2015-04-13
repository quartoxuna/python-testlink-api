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

from .. import randput, randict, generate, ServerMock

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

	@patch('testlink.api.Testlink_XML_RPC_API._query')
	def test_getVersion(self,mock):
		"""Version String"""
		mock.return_value = "1.2.3"
		tl = Testlink(URL,DEVKEY)
		self.assertEquals(tl.getVersion(), "1.2.3")

	def test_getTestProject(self):
		"""'getTestProject'"""
		# Generate some test data
		args = randput()
		kwargs = randict("foo","bar")
		ret = generate(1)

		# Mock the eqivalent iterator
		tl = Testlink(URL,DEVKEY)
		tl.iterTestProject = Mock(return_value=ret)

		# Check for normalize call, because there would
		# be no single return value otherwise
		self.assertEquals(tl.getTestProject(name=args,**kwargs),1)

		# Check correct parameter forwarding
		tl.iterTestProject.assert_called_with(args,**kwargs)

	def test_iterTestProject_ShortCut_By_Name(self):
		"""'iterTestProject' ShortCut by Name"""
		# Generate some test data
		kwargs = randict("name")

		# Mock the raw api calls we want to track
		tl = Testlink(URL,DEVKEY)
		tl._api.getTestProjectByName = Mock(return_value={})
		tl._api.getProjects = Mock()

		# Check
		tl.iterTestProject(**kwargs).next()
		tl._api.getTestProjectByName.assert_called_with(kwargs['name'])
		self.assertFalse(tl._api.getProjects.called)

	def test_iterTestProject(self):
		"""'iterTestProject'"""
		# Generate some test data
		kwargs = randict("name","notes")

		# Mock the raw api calls we want to track
		tl = Testlink(URL,DEVKEY)
		tl._api.getTestProjectByName = Mock()
		tl._api.getProjects = Mock(return_value= [kwargs,randict("name","notes"),randict("name","notes")] )

		# Check for generator function
		self.assertTrue(inspect.isgeneratorfunction(tl.iterTestProject))

		# Check if shortcut is avoided
		project = tl.iterTestProject(**kwargs).next()
		self.assertFalse(tl._api.getTestProjectByName.called)
		tl._api.getProjects.assert_called_with()

		# Check correct filtered return value
		self.assertTrue(isinstance(project,TestProject))
		self.assertEqual(project.name, kwargs['name'])
		self.assertEqual(project.notes, kwargs['notes'])
