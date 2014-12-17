#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@author: Kai Borowiak
@summary: TestSuite for testlink.api.Testlink_XML_RPC_API
"""

# IMPORTS
import unittest
from mock import Mock, MagicMock, patch

from testlink.api import Testlink_XML_RPC_API
from testlink.exceptions import *

from distutils.version import LooseVersion as Version
import threading
import SimpleXMLRPCServer
import xmlrpclib

import logging
#logging.basicConfig(level=logging.DEBUG)

class Testlink_XML_RPC_API_Tests(unittest.TestCase):

	def setUp(self):
		self._patcher = patch('xmlrpclib.ServerProxy',spec=True)
		self._mock_server = self._patcher.start()
		self._mock_tl = Mock()
		self._api = Testlink_XML_RPC_API("http://localhost")
		self._api._proxy = self._mock_server

	def tearDown(self):
		self._patcher.stop()

	# We need to patch to the 'real' ServerProxy here to get good results
	@patch('xmlrpclib.ServerProxy')
	def test_invalid_url(self,mock_server):
		mock_server = xmlrpclib.ServerProxy
		self.assertRaises(Exception,Testlink_XML_RPC_API)
		self.assertRaises(ConnectionError,Testlink_XML_RPC_API,"SPAM")
		self.assertRaises(ConnectionError,Testlink_XML_RPC_API,"http://")
		self.assertRaises(ConnectionError,Testlink_XML_RPC_API,"http://127.0.0.2:8080/lib/api/xmlrpc.php")
		self.assertRaises(ConnectionError,Testlink_XML_RPC_API,"http://127.0.0.2:8080/lib/api/xmlrpc/v1/xmlrpc.php")

	def test_query(self):
		# Define mock endpoints
		self._mock_server.passed = Mock(return_value="SPAM!")
		self._mock_server.error = Mock(return_value=[{'code':1337,'message':'SPAM!'}])

		# Check endpoints
		self.assertEqual(self._api._query("passed"),"SPAM!")
		self.assertRaises(APIError,self._api._query,"error")

		# Check correct variable forwarding
		self._api._query("passed",a=1,b=2,c=3)
		self._mock_server.passed.assert_called_with(dict(a=1,b=2,c=3,devKey=None))

		# Check global devkey setting
		self._api._devkey = "SPAM!"
		self._api._query("passed",a=1,b=2,c=3)
		self._mock_server.passed.assert_called_with(dict(a=1,b=2,c=3,devKey="SPAM!"))

	#
	# The following tests have all the same structure:
	#
	# def test_foo(self):
	#
	#     # Mock already tested _query method
	#     result = bar
	#     self._api._query = Mock(return_value = bar)
	#
	#     # Check if version check succeeds
	#     self.assertRaises(NotSupported,self._api.foo,*args,**kwargs)
	#
	#     # Patch Testlink Version if needed to get pass the TLVersion decorator (OPTIONAL)
	#     self._api._tl_version = Version("x.x.x")
	#
	#     # Verify result and passed arguments
	#     self.assertEquals(self._api.foo(), result)
	#     self._api._query.assert_called_with('foo',*args,**kwargs)
	#

	def test_testLinkVersion(self):
		self._api._query = Mock(return_value="1.3.3.7")
		self.assertRaises(NotSupported,self._api.testLinkVersion)
		self._api._tl_version = Version("1.9.9")
		self.assertEquals(self._api.testLinkVersion(),"1.3.3.7")
		self._api._query.assert_called_with('tl.testLinkVersion')

	def test_about(self):
		result = "Testlink API Version: 1.0 initially written by Asial Blumfield"
		self._api._query = Mock(return_value=result)
		self.assertEquals(self._api.about(),result)
		self._api._query.assert_called_with('tl.about')

	def test_sayHello(self):
		result = "Hello!"
		self._api._query = Mock(return_value=result)
		self.assertEquals(self._api.sayHello(),result)
		self._api._query.assert_called_with('tl.sayHello')

	def test_repeat(self):
		result = str(4223)
		self._api._query = Mock(return_value=result)
		self.assertEquals(self._api.repeat(result),result)
		self._api._query.assert_called_with('tl.repeat',str=result)

	def test_checkDevKey(self):
		key = "SPAM"
		self._api._query = Mock(return_value=True)
		self.assertEquals(self._api.checkDevKey(key),True)
		self._api._query.assert_called_with('tl.checkDevKey',devKey = key)

	def test_doesUserExist(self):
		self._api._query = Mock(return_value=True)
		self.assertEquals(self._api.doesUserExist("SPAM"),True)
		self._api._query.assert_called_with('tl.doesUserExist',user="SPAM",devKey=None)

	def test_getUserByLogin(self):
		result = {'name':'SPAM','id':23}
		self._api._query = Mock(return_value=result)
		self.assertRaises(NotSupported,self._api.getUserByLogin,"SPAM")
		self._api._tl_version = Version("1.9.8")
		self.assertEquals(self._api.getUserByLogin("SPAM"),result)
		self._api._query.assert_called_with('tl.getUserByLogin',user="SPAM",devKey=None)
		
	def test_getUserByID(self):
		result = {'name':'SPAM','id':23}
		self._api._query = Mock(return_value=result)
		self.assertRaises(NotSupported,self._api.getUserByID,23)
		self._api._tl_version = Version("1.9.8")
		self.assertEquals(self._api.getUserByID(23),result)
		self._api._query.assert_called_with('tl.getUserByID',userid=23,devKey=None)

	def test_getFullPath(self):
		result = "foo.bar"
		self._api._query = Mock(return_value = result)
		self.assertEquals(self._api.getFullPath(23),result)
		self._api._query.assert_called_with('tl.getFullPath',nodeID=23,devKey=None)

	def test_createTestProject(self):
		result = {'message':'Success!'}
		self._api._query = Mock(return_value = result)

		# Check default params
		defaults = {'name':'Test','prefix':'T'}
		self.assertEquals(self._api.createTestProject(**defaults),result)
		self._api._query.assert_called_with('tl.createTestProject',\
							notes = '',\
							active = True,\
							public = True,\
							options = 	{'requirementsEnabled':False,\
									'testPriorityEnabled':False,\
									'automationEnabled':False,\
									'inventoryEnabled':False},\
							devKey = None,
							**defaults\
						)

		# Check with specified params
		non_defaults = {'name':'Test','prefix':'T','notes':'SPAM','active':False,'public':False,'requirements':True,'priority':True,'automation':True,'inventory':True}
		self.assertEquals(self._api.createTestProject(**non_defaults),result)
		self._api._query.assert_called_with('tl.createTestProject',\
							name = "Test",\
							prefix = "T",\
							notes = 'SPAM',\
							active = False,\
							public = False,\
							options = 	{'requirementsEnabled':True,\
									'testPriorityEnabled':True,\
									'automationEnabled':True,\
									'inventoryEnabled':True},\
							devKey = None\
						)

	def test_getProjects(self):
		result = [{'name':'Project'}]
		self._api._query = Mock(return_value = result)
		self.assertEquals(self._api.getProjects(),result)
		self._api._query.assert_called_with('tl.getProjects',devKey = None)

	def test_getTestProjectByName(self):
		result = [{'name':'SPAM'}]
		self._api._query = Mock(return_value = result)
		self.assertEquals(self._api.getTestProjectByName("SPAM"),result)
		self._api._query.assert_called_with('tl.getTestProjectByName',testprojectname="SPAM",devKey=None)

	def test_createTestPlan(self):
		result = {'message':'Success!'}
		self._api._query = Mock(return_value = result)
		
		# Check default params
		defaults = {'name':'Test','project':'SPAM'}
		self.assertEquals(self._api.createTestPlan(**defaults),result)
		self._api._query.assert_called_with('tl.createTestPlan',\
							testplanname = "Test",\
							testprojectname = "SPAM",\
							notes = '',\
							active = True,\
							public = True,\
							devKey = None\
						)

		# Check with specified params
		non_defaults = {'name':'Test','project':'SPAM','notes':'some notes','active':False,'public':False}
		self.assertEquals(self._api.createTestPlan(**non_defaults),result)
		self._api._query.assert_called_with('tl.createTestPlan',\
							testplanname = "Test",\
							testprojectname = "SPAM",\
							notes = "some notes",\
							active = False,\
							public = False,\
							devKey = None\
						)

	def test_getTestPlanByName(self):
		result = [{'name':'SPAM'}]
		self._api._query = Mock(return_value = result)
		self.assertEquals(self._api.getTestPlanByName("Test","SPAM"),result)
		self._api._query.assert_called_with('tl.getTestPlanByName',testplanname="Test",testprojectname="SPAM",devKey=None)
