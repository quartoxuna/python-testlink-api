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
from testlink.objects import Testlink
from testlink.objects import TestProject
from testlink.exceptions import *
from testlink.enums import *

class TestlinkTests(unittest.TestCase):

	def __init__(self,*args,**kwargs):
		super(TestlinkTests,self).__init__(*args,**kwargs)
		self._testMethodDoc = "Testlink: " + self._testMethodDoc
		self.url = "http://localhost/"
		self.devkey = randput(50)

	def setUp(self):
		"""Needed to connect to a mocked Server endpoint in each test"""
		self._patcher = patch('xmlrpclib.ServerProxy',new=ServerMock,spec=True)
		self._mock_server = self._patcher.start()
		self._api = Testlink_XML_RPC_API(self.url + "lib/api/xmlrpc.php")
		self._api._proxy = self._mock_server

	def tearDown(self):
		self._patcher.stop()

	def test_apiType(self):
		"""Defazlt API Type"""
		tl = Testlink(self.url,self.devkey)
		self.assertTrue(isinstance(tl._api,Testlink_XML_RPC_API))
		tl = Testlink(self.url,self.devkey,APIType.XML_RPC)
		self.assertTrue(isinstance(tl._api,Testlink_XML_RPC_API))
		self.assertRaises(NotImplementedError,Testlink,self.url,self.devkey,APIType.REST)

	def test_devKeySetting(self):
		"""DevKey Storage"""
		tl = Testlink(self.url,self.devkey)
		self.assertEquals(tl._api._devkey,self.devkey)

	def test_getVersion(self):
		"""Version String"""
		test_data = randput()
		tl = Testlink(self.url,self.devkey)
		tl._api._tl_version = test_data
		self.assertEquals(tl.getVersion(), test_data)

	@patch('testlink.objects.Testlink.iterTestProject')
	def test_getTestProject(self,p1):
		"""'getTestProject'"""
		# Generate some test data
		args = randput()
		kwargs = randict("foo","bar")
		return_value = randput()

		# Init Testlink
		tl = Testlink(self.url,self.devkey)

		# Mock the eqivalent iterator
		p1.return_value = generate(return_value)

		# Check for normalize call, because there would
		# be no single return value otherwise
		self.assertEquals(tl.getTestProject(name=args,**kwargs),return_value)

		# Check correct parameter forwarding
		tl.iterTestProject.assert_called_with(args,**kwargs)

	@patch('testlink.api.Testlink_XML_RPC_API.getTestProjectByName')
	@patch('testlink.api.Testlink_XML_RPC_API.getProjects')
	def test_iterTestProject_shortcut(self,getProjects,getTestProjectByName):
		"""'iterTestProject' - Shortcut"""
		# Generate some test data
		test_data = [randict("name","notes"),randict("name","notes"),randict("name","notes")]

		# Init Testlink
		tl = Testlink(self.url,self.devkey)

		# Mock internal methods
		getProjects.return_value = test_data
		getTestProjectByName.return_value = test_data[1]

		# Check calls and result with shortcut usage
		project = tl.iterTestProject(test_data[1]['name']).next()
		getTestProjectByName.assert_called_with(test_data[1]['name'])
		self.assertFalse(getProjects.called)
		self.assertTrue(isinstance(project,TestProject))
		self.assertEqual(project.name, test_data[1]['name'])
		self.assertEqual(project.notes, test_data[1]['notes'])

	@patch('testlink.api.Testlink_XML_RPC_API.getTestProjectByName')
	@patch('testlink.api.Testlink_XML_RPC_API.getProjects')
	def test_iterTestProject_shortcut_no_result(self,getProjects,getTestProjectByName):
		"""'iterTestProject' - Shortcut Empty Result"""
		# Generate some test data
		test_data = [randict("name","notes"),randict("name","notes"),randict("name","notes")]

		# Init Testlink
		tl = Testlink(self.url,self.devkey)

		# Mock internal methods
		getProjects.return_value = ''
		getTestProjectByName.side_effect = APIError(7011,"Test Project (name: ) does not exist")

		# Check with no result
		project_iter = tl.iterTestProject(randput())
		self.assertRaises(StopIteration,project_iter.next)

	@patch('testlink.api.Testlink_XML_RPC_API.getTestProjectByName')
	@patch('testlink.api.Testlink_XML_RPC_API.getProjects')
	def test_iterTestProject(self,getProjects,getTestProjectByName):
		"""'iterTestProject'"""
		# Generate some test data
		test_data = [randict("name","notes"),randict("name","notes"),randict("name","notes")]

		# Init Testlink
		tl = Testlink(self.url,self.devkey)

		# Check with no result
		project_iter = tl.iterTestProject()
		self.assertRaises(StopIteration,project_iter.next)

		# Mock internal methods
		getProjects.return_value = test_data
		getTestProjectByName.return_value = test_data[1]

		project = tl.iterTestProject(**test_data[1]).next()
		getProjects.assert_called_with()
		self.assertFalse(getTestProjectByName.called)
		self.assertTrue(isinstance(project,TestProject))
		self.assertEqual(project.name, test_data[1]['name'])
		self.assertEqual(project.notes, test_data[1]['notes'])

	@patch('testlink.api.Testlink_XML_RPC_API.getTestProjectByName')
	@patch('testlink.api.Testlink_XML_RPC_API.getProjects')
	def test_iterTestProject_no_result(self,getProjects,getTestProjectByName):
		"""'iterTestProject' - Empty Result"""
		# Generate some test data
		test_data = [randict("name","notes"),randict("name","notes"),randict("name","notes")]

		# Init Testlink
		tl = Testlink(self.url,self.devkey)

		# Mock internal methods
		getProjects.return_value = ''
		getTestProjectByName.side_effect = APIError(7011,"Test Project (name: ) does not exist")

		# Check with no result
		project_iter = tl.iterTestProject()
		self.assertRaises(StopIteration,project_iter.next)


class CompatTests(unittest.TestCase):

	def __init__(self,*args,**kwargs):
		super(CompatTests,self).__init__(*args,**kwargs)
		self._testMethodDoc = "CompatTests: " + self._testMethodDoc

	def test_datetime_conversion(self):
		"""Datetime Backwards compatability Python 2.5<"""
		from datetime import datetime
		from testlink.objects import DATETIME_FORMAT
		from testlink.objects import _strptime
		date_string = "2000-12-23 12:34:45"
		datetime_obj = datetime.strptime(date_string,DATETIME_FORMAT)
		strptime_obj = _strptime(date_string,DATETIME_FORMAT)
		self.assertEquals(datetime_obj,strptime_obj)
