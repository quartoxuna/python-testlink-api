#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@author: Kai Borowiak
@summary: TestSuite for testlink.api.Testlink_XML_RPC_API
"""

# IMPORTS
import unittest
from mock import Mock, MagicMock, patch

from distutils.version import LooseVersion as Version
import xmlrpclib

from .. import input, randict, ServerMock

from testlink.api import Testlink_XML_RPC_API
from testlink.exceptions import NotSupported
from testlink.exceptions import APIError
from testlink.exceptions import ConnectionError
from testlink.enums import ExecutionType
from testlink.enums import ImportanceLevel

class Testlink_XML_RPC_API_Tests(unittest.TestCase):

	def __init__(self,*args,**kwargs):
		super(Testlink_XML_RPC_API_Tests,self).__init__(*args,**kwargs)
		self._testMethodDoc = "Testlink_XML_RPC_API: " + str(self._testMethodDoc)

	def setUp(self):
		"""Needed to connect to a mocked Server endpoint in each test"""
		self._patcher = patch('xmlrpclib.ServerProxy',new=ServerMock,spec=True)
		self._mock_server = self._patcher.start()
		self._api = Testlink_XML_RPC_API("http://localhost/lib/api/xmlrpc.php")
		self._api._proxy = self._mock_server

	def tearDown(self):
		self._patcher.stop()

	# We need to patch to the 'real' ServerProxy here to get good results
	def test_invalid_url(self):
		"""Invalid URL"""
		self.assertRaises(Exception,Testlink_XML_RPC_API)
		self.assertRaises(ConnectionError,Testlink_XML_RPC_API,"")
		self.assertRaises(ConnectionError,Testlink_XML_RPC_API,"foo")
		self.assertRaises(ConnectionError,Testlink_XML_RPC_API,"http://")

	def test_query(self):
		"""Query wrapper"""
		# Define mock endpoints
		self._mock_server.passed = Mock(return_value="SPAM!")
		self._mock_server.error = Mock(return_value=[{'code':1337,'message':'SPAM!'}])

		# Check endpoints
		self.assertEqual(self._api._query("passed"),"SPAM!")
		self.assertRaises(APIError,self._api._query,"error")

		# Check APIError struct
		try:
			self._api._query("error")
		except APIError,ae:
			self.assertEquals(ae.errorCode,1337)
			self.assertEquals(ae.errorString,"SPAM!")

		# Check correct variable forwarding
		data = randict("a","b","c")
		self._api._query("passed",**data)
		self._mock_server.passed.assert_called_with(dict(a=data['a'],b=data['b'],c=data['c'],devKey=None))

	def test_globalDevKey(self):
		"""Global DevKey setting"""
		key = input(20)
		test_data = randict("foo","bar")
		self._api._devkey = key
		self._mock_server.mockMethod = MagicMock()
		self._api._query("mockMethod",**test_data)
		test_data["devKey"] = key
		self._mock_server.mockMethod.assert_called_with(test_data)

	#
	# Since the raw API calls are very simple, some checks can be done
	# together. For each raw call, the following things are checked:
	# 	- Method raises NotSupported if called within wrong API version
	# 	- No manipulation of server response (result of _query method call)
	# 	- Correct naming and forwarding of arguments to internal _query method
	#
	# @patch("testlink.api.Testlink_XML_RPC_API._query")
	# def test_foo(self,query):
	# 	"""'foo' (x.x.x)"""    # <-- Method and TL version
	#
	# 	# Mock query result (since this is checked separaterly)
	# 	query.return_value = input
	#
	# 	# Define test data
	# 	test_data = randict("foo","bar")
	#
	# 	# Version check if api version > 1.0
	# 	self.assertRaises(NotSupported,self._api.foo)
	# 	self._api._tl_version = Version("x.x.x")
	#
	# 	# Verify if result matches with query result (no data manipulation)
	# 	# Also verify passed arguments
	# 	self.assertEquals(self._api.foo(**test_data), query.return_value)
	# 	query.assert_called_with('foo',**test_data)
	#
	# 	# Version check if api version = 1.0
	# 	self._api._tl_version = Version("0.9")
	# 	self.assertRaises(NotSupported,self._api.foo)
	#

	@patch("testlink.api.Testlink_XML_RPC_API._query")
	def test_testLinkVersion(self,query):
		"""'testLinkVersion' (1.9.9)"""
		# First _query fails because NotSupported
		query.return_value = "1.9.9"
		query.side_effect = NotSupported('tl.testLinkVersion')
		self.assertRaises(NotSupported,self._api.testLinkVersion)

		query.side_effect = None
		self._api._tl_version = Version("1.9.9")
		self.assertEquals(self._api.testLinkVersion(),query.return_value)
		query.assert_called_with('tl.testLinkVersion')

	@patch("testlink.api.Testlink_XML_RPC_API._query")
	def test_about(self,query):
		"""'about' (1.0)"""
		query.return_value = input(50)
		self.assertEquals(self._api.about(),query.return_value)
		query.assert_called_with('tl.about')
		self._api._tl_version = Version("0.9")
		self.assertRaises(NotSupported,self._api.about)

	@patch("testlink.api.Testlink_XML_RPC_API._query")
	def test_sayHello(self,query):
		"""'sayHello' (1.0)"""
		query.return_value = input()
		self.assertEquals(self._api.sayHello(),query.return_value)
		query.assert_called_with('tl.sayHello')
		self._api._tl_version = Version("0.9")
		self.assertRaises(NotSupported,self._api.sayHello)

	@patch("testlink.api.Testlink_XML_RPC_API._query")
	def test_repeat(self,query):
		"""'repeat' (1.0)"""
		query.return_value = input(20)
		test_data = query.return_value
		self.assertEquals(self._api.repeat(test_data),query.return_value)
		query.assert_called_with('tl.repeat',str=test_data)
		self._api._tl_version = Version("0.9")
		self.assertRaises(NotSupported,self._api.repeat)

	@patch("testlink.api.Testlink_XML_RPC_API._query")
	def test_checkDevKey(self,query):
		"""'checkDevKey' (1.0)"""
		query.return_value = True
		test_data = input()
		self.assertEquals(self._api.checkDevKey(test_data),query.return_value)
		query.assert_called_with('tl.checkDevKey',devKey = test_data)
		self._api._tl_version = Version("0.9")
		self.assertRaises(NotSupported,self._api.checkDevKey)

	@patch("testlink.api.Testlink_XML_RPC_API._query")
	def test_doesUserExist(self,query):
		"""'doesUserExist' (1.0)"""
		query.return_value = True
		test_data = input()
		self.assertEquals(self._api.doesUserExist(test_data),query.return_value)
		query.assert_called_with('tl.doesUserExist',user=test_data,devKey=None)
		self._api._tl_version = Version("0.9")
		self.assertRaises(NotSupported,self._api.doesUserExist)

	@patch("testlink.api.Testlink_XML_RPC_API._query")
	def test_getUserByLogin(self,query):
		"""'getUserByLogin' (1.9.8)"""
		query.return_value = input()
		test_data = input()
		self.assertRaises(NotSupported,self._api.getUserByLogin)
		self._api._tl_version = Version("1.9.8")
		self.assertEquals(self._api.getUserByLogin(test_data),query.return_value)
		query.assert_called_with('tl.getUserByLogin',user=test_data,devKey=None)

	@patch("testlink.api.Testlink_XML_RPC_API._query")
	def test_getUserByID(self,query):
		"""'getUserByID' (1.9.8)"""
		query.return_value = randict("name","id")
		test_data = input()
		self.assertRaises(NotSupported,self._api.getUserByID)
		self._api._tl_version = Version("1.9.8")
		self.assertEquals(self._api.getUserByID(test_data),query.return_value)
		query.assert_called_with('tl.getUserByID',userid=test_data,devKey=None)

	@patch("testlink.api.Testlink_XML_RPC_API._query")
	def test_getFullPath(self,query):
		"""'getFullPath' (1.0)"""
		query.return_value = input()
		test_data = input()
		self.assertEquals(self._api.getFullPath(test_data),query.return_value)
		query.assert_called_with('tl.getFullPath',nodeID=test_data,devKey=None)
		self._api._tl_version = Version("0.9")
		self.assertRaises(NotSupported,self._api.getFullPath)

	@patch("testlink.api.Testlink_XML_RPC_API._query")
	def test_createTestProject(self,query):
		"""'createTestProject' (1.0)"""
		query.return_value = randict("message")
		# Check default params
		defaults = randict("name","prefix")
		self.assertEquals(self._api.createTestProject(**defaults),query.return_value)
		query.assert_called_with('tl.createTestProject',\
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
		options = randict("requirements","priority","automation","inventory")
		non_defaults = randict("name","prefix","notes","active","public")
		non_defaults.update(options)
		self.assertEquals(self._api.createTestProject(**non_defaults),query.return_value)
		query.assert_called_with('tl.createTestProject',\
							devKey = None,\
							options = 	{'requirementsEnabled':options['requirements'],\
									'testPriorityEnabled':options['priority'],\
									'automationEnabled':options['automation'],\
									'inventoryEnabled':options['inventory']},\
							name = non_defaults['name'],\
							prefix = non_defaults['prefix'],\
							notes = non_defaults['notes'],\
							active = non_defaults['active'],\
							public = non_defaults['public'],\
						)
		self._api._tl_version = Version("0.9")
		self.assertRaises(NotSupported,self._api.createTestProject)

	@patch("testlink.api.Testlink_XML_RPC_API._query")
	def test_getProjects(self,query):
		"""'getProjects' (1.0)"""
		query.return_value = [randict("name")]
		self.assertEquals(self._api.getProjects(),query.return_value)
		query.assert_called_with('tl.getProjects',devKey = None)
		self._api._tl_version = Version("0.9")
		self.assertRaises(NotSupported,self._api.getProjects)

	@patch("testlink.api.Testlink_XML_RPC_API._query")
	def test_getTestProjectByName(self,query):
		"""'getTestProjectByName' (1.0)"""
		test_data = randict("name")
		query.return_value = [test_data]
		self.assertEquals(self._api.getTestProjectByName(test_data['name']),query.return_value)
		query.assert_called_with('tl.getTestProjectByName',testprojectname=test_data['name'],devKey=None)
		self._api._tl_version = Version("0.9")
		self.assertRaises(NotSupported,self._api.getTestProjectByName)

	@patch("testlink.api.Testlink_XML_RPC_API._query")
	def test_createTestPlan(self,query):
		"""'createTestPlan' (1.0)"""
		query.return_value = randict("message")
		# Check default params
		defaults = randict("name","project")
		self.assertEquals(self._api.createTestPlan(**defaults),query.return_value)
		query.assert_called_with('tl.createTestPlan',\
							notes = '',\
							active = True,\
							public = True,\
							devKey = None,\
							testplanname = defaults['name'],\
							testprojectname = defaults['project']\
						)
		# Check with specified params
		non_defaults = randict("name","project","notes","active","public")
		self.assertEquals(self._api.createTestPlan(**non_defaults),query.return_value)
		query.assert_called_with('tl.createTestPlan',\
							devKey = None,\
							active = non_defaults['active'],\
							public = non_defaults['public'],\
							notes = non_defaults['notes'],\
							testplanname = non_defaults['name'],\
							testprojectname = non_defaults['project']\
						)
		self._api._tl_version = Version("0.9")
		self.assertRaises(NotSupported,self._api.createTestPlan)

	@patch("testlink.api.Testlink_XML_RPC_API._query")
	def test_getTestPlanByName(self,query):
		"""'getTestPlanByName' (1.0)"""
		test_data = randict("name","projectname")
		query.return_value = [test_data]
		self.assertEquals(self._api.getTestPlanByName(**test_data),query.return_value)
		query.assert_called_with('tl.getTestPlanByName',testplanname=test_data['name'],testprojectname=test_data['projectname'],devKey=None)
		self._api._tl_version = Version("0.9")
		self.assertRaises(NotSupported,self._api.getTestPlanByName)

	@patch("testlink.api.Testlink_XML_RPC_API._query")
	def test_getProjectTestPlans(self,query):
		"""'getProjectTestPlans' (1.0)"""
		test_data = input()
		query.return_value = [randict("name")]
		self.assertEquals(self._api.getProjectTestPlans(test_data),query.return_value)
		query.assert_called_with('tl.getProjectTestPlans',testprojectid=test_data,devKey=None)
		self._api._tl_version = Version("0.9")
		self.assertRaises(NotSupported,self._api.getProjectTestPlans)

	@patch("testlink.api.Testlink_XML_RPC_API._query")
	def test_getTestPlanCustomFieldValue(self,query):
		"""'getTestPlanCustomFieldValue' (1.9.4)"""
		test_data = randict("testplanid","testprojectid","fieldname")
		query.return_value = input()
		self.assertRaises(NotSupported,self._api.getTestPlanCustomFieldValue)
		self._api._tl_version = Version("1.9.4")
		self.assertEquals(self._api.getTestPlanCustomFieldValue(**test_data),query.return_value)	
		query.assert_called_with('tl.getTestPlanCustomFieldValue',\
							devKey = None,\
							customfieldname = test_data['fieldname'],\
							testprojectid = test_data['testprojectid'],\
							testplanid = test_data['testplanid']\
						)
	
	@patch("testlink.api.Testlink_XML_RPC_API._query")
	def test_createBuild(self,query):
		"""'createBuild' (1.0)"""
		query.return_value = randict("message")
		# Check default params
		defaults = randict("testplanid","name")
		self.assertEquals(self._api.createBuild(**defaults),query.return_value)
		query.assert_called_with('tl.createBuild',\
							devKey = None,\
							buildnotes = '',\
							buildname = defaults['name'],\
							testplanid = defaults['testplanid'],\
						)
		# Check with specified params
		non_defaults =randict("testplanid","name","notes")
		self.assertEquals(self._api.createBuild(**non_defaults),query.return_value)
		query.assert_called_with('tl.createBuild',\
							devKey = None,\
							buildnotes = non_defaults['notes'],\
							buildname = non_defaults['name'],\
							testplanid = non_defaults['testplanid']\
						)
		self._api._tl_version = Version("0.9")
		self.assertRaises(NotSupported,self._api.createBuild)

	@patch("testlink.api.Testlink_XML_RPC_API._query")
	def test_getLatestBuildForTestPlan(self,query):
		"""'getLatestBuildForTestPlan' (1.0)"""
		query.return_value = [randict("name","id")]
		test_data = input()
		self.assertEquals(self._api.getLatestBuildForTestPlan(test_data),query.return_value)
		query.assert_called_with('tl.getLatestBuildForTestPlan',devKey=None,testplanid=test_data)
		self._api._tl_version = Version("0.9")
		self.assertRaises(NotSupported,self._api.getLatestBuildForTestPlan)

	@patch("testlink.api.Testlink_XML_RPC_API._query")
	def test_getBuildsForTestPlan(self,query):
		"""'getBuildsForTestPlan' (1.0)"""
		query.return_value = [randict("name","id"),randict("name","id")]
		test_data = input()
		self.assertEquals(self._api.getBuildsForTestPlan(test_data),query.return_value)
		query.assert_called_with('tl.getBuildsForTestPlan',devKey=None,testplanid=test_data)
		self._api._tl_version = Version("0.9")
		self.assertRaises(NotSupported,self._api.getBuildsForTestPlan)

	@patch("testlink.api.Testlink_XML_RPC_API._query")
	def test_getExecCountersByBuild(self,query):
		"""'getExecCountersByBuild' (1.9.4)"""
		query.return_value = [randict("a","b","c")]
		test_data = input()
		self.assertRaises(NotSupported,self._api.getExecCountersByBuild)
		self._api._tl_version = Version("1.9.4")
		self.assertEquals(self._api.getExecCountersByBuild(test_data),query.return_value)
		query.assert_called_with('tl.getExecCountersByBuild',devKey=None,testplanid=test_data)

	@patch("testlink.api.Testlink_XML_RPC_API._query")
	def test_createPlatform(self,query):
		"""'createPlatform' (1.9.6)"""
		query.return_value = randict("message")
		# Check default params
		defaults = randict("testprojectname","platformname")
		self.assertRaises(NotSupported,self._api.createPlatform)
		self._api._tl_version = Version("1.9.6")
		self.assertEquals(self._api.createPlatform(**defaults),query.return_value)
		query.assert_called_with('tl.createPlatform',\
						devKey = None,\
						notes = '',\
						**defaults\
					)
		# Check with specified parameters
		non_defaults = randict("testprojectname","platformname","notes")
		self.assertEquals(self._api.createPlatform(**non_defaults),query.return_value)
		query.assert_called_with('tl.createPlatform',\
						devKey = None,\
						**non_defaults\
					)

	@patch("testlink.api.Testlink_XML_RPC_API._query")
	def test_getProjectPlatforms(self,query):
		"""'getProjectPlatforms' (1.9.6)"""
		query.return_value = [randict("name","id"),randict("name","id")]
		test_data = input()
		self.assertRaises(NotSupported,self._api.getProjectPlatforms)
		self._api._tl_version = Version("1.9.6")
		self.assertEquals(self._api.getProjectPlatforms(test_data),query.return_value)
		query.assert_called_with('tl.getProjectPlatforms',devKey = None,testprojectid = test_data)

	@patch("testlink.api.Testlink_XML_RPC_API._query")
	def test_getTestPlanPlatforms(self,query):
		"""'getTestPlanPlatforms' (1.0)"""
		query.return_value = [randict("name","id"),randict("name","id")]
		test_data = input()
		self.assertEquals(self._api.getTestPlanPlatforms(test_data),query.return_value)
		query.assert_called_with('tl.getTestPlanPlatforms',devKey=None,testplanid=test_data)
		self._api._tl_version = Version("0.9")
		self.assertRaises(NotSupported,self._api.getTestPlanPlatforms)

	@patch("testlink.api.Testlink_XML_RPC_API._query")
	def test_reportTCResult(self,query):
		"""'reportTCResult' (1.0)"""
		query.return_value = randict("message")
		# Check default params
		defaults = randict("testplanid","status")
		self.assertEquals(self._api.reportTCResult(**defaults),query.return_value)
		query.assert_called_with('tl.reportTCResult',\
						devKey = None,\
						testcaseid = None,\
						testcaseexternalid = None,\
						buildid = None,\
						buildname = None,\
						notes = None,\
						guess = True,\
						bugid = None,\
						platformid = None,\
						platformname = None,\
						customfields = None,\
						overwrite = False,\
						**defaults\
					)
		# Check with specified parameters
		non_defaults = randict("testplanid","status","testcaseid","testcaseexternalid","buildid","buildname","notes","guess","bugid","platformid","platformname","customfields","overwrite")
		self.assertEquals(self._api.reportTCResult(**non_defaults),query.return_value)
		query.assert_called_with('tl.reportTCResult',\
						devKey = None,\
						**non_defaults\
					)
		self._api._tl_version = Version("0.9")
		self.assertRaises(NotSupported,self._api.reportTCResult)

	@patch("testlink.api.Testlink_XML_RPC_API._query")
	def test_getLastExecutionResult(self,query):
		"""'getLastExecutionResult' (1.0)"""
		query.return_value = randict("id","name","status")
		# Check default params
		defaults = randict("testplanid")
		self.assertEquals(self._api.getLastExecutionResult(**defaults),query.return_value)
		query.assert_called_with('tl.getLastExecutionResult',\
						devKey = None,\
						testcaseid = None,\
						testcaseexternalid = None,\
						**defaults\
					)
		# Check with specified parameters
		non_defaults = randict("testplanid","testcaseid","testcaseexternalid")
		self.assertEquals(self._api.getLastExecutionResult(**non_defaults),query.return_value)
		query.assert_called_with('tl.getLastExecutionResult',\
						devKey = None,\
						**non_defaults\
					)
		self._api._tl_version = Version("0.9")
		self.assertRaises(NotSupported,self._api.getLastExecutionResult)
		# Check new arguments since version 1.9.9
		self._api._tl_version = Version("1.9.9")
		self.assertEquals(self._api.getLastExecutionResult(**defaults),query.return_value)
		query.assert_called_with('tl.getLastExecutionResult',\
						devKey = None,\
						testplanid = defaults['testplanid'],\
						testcaseid = None,\
						testcaseexternalid = None,\
						platformid = None,\
						platformname = None,\
						buildid = None,\
						buildname = None,\
						options = {'getBugs':False}\
					)
		non_defaults.update(randict("platformid","platformname","buildid","buildname","bugs"))
		self.assertEquals(self._api.getLastExecutionResult(**non_defaults),query.return_value)
		query.assert_called_with('tl.getLastExecutionResult',\
						devKey = None,\
						testplanid = non_defaults['testplanid'],\
						testcaseid = non_defaults['testcaseid'],\
						testcaseexternalid = non_defaults['testcaseexternalid'],\
						platformid = non_defaults['platformid'],\
						platformname = non_defaults['platformname'],\
						buildid = non_defaults['buildid'],\
						buildname = non_defaults['buildname'],\
						options = {'getBugs':non_defaults['bugs']}\
					)

	@patch("testlink.api.Testlink_XML_RPC_API._query")
	def test_deleteExecution(self,query):
		"""'deleteExecution' (1.0)"""
		query.return_value = randict("message")
		test_data = input()
		self.assertEquals(self._api.deleteExecution(test_data),query.return_value)
		query.assert_called_with('tl.deleteExecution',executionid=test_data,devKey=None)
		self._api._tl_version = Version("0.9")
		self.assertRaises(NotSupported,self._api.deleteExecution)

	@patch("testlink.api.Testlink_XML_RPC_API._query")
	def test_createTestSuite(self,query):
		"""'createTestSuite' (1.0)"""
		query.return_value = randict("message")
		# Check default params
		defaults = randict("testsuitename","testprojectid")
		self.assertEquals(self._api.createTestSuite(**defaults),query.return_value)
		query.assert_called_with('tl.createTestSuite',\
						devKey = None,\
						details = None,\
						parentid = None,\
						order = None,\
						checkduplicatedname = True,\
						actiononduplicatedname = 'block',
						**defaults\
					)
		# Check with specified parameters
		non_defaults = randict("testsuitename","testprojectid","details","parentid","order","checkduplicatedname","actiononduplicatedname")
		self.assertEquals(self._api.createTestSuite(**non_defaults),query.return_value)
		query.assert_called_with('tl.createTestSuite', devKey = None, **non_defaults)
		self._api._tl_version = Version("0.9")
		self.assertRaises(NotSupported,self._api.createTestSuite)

	@patch("testlink.api.Testlink_XML_RPC_API._query")
	def test_getTestSuiteById(self,query):
		"""'getTestSuiteById' (1.0)"""
		query.return_value = randict("name","id")
		test_data = randict("testsuiteid")
		self.assertEquals(self._api.getTestSuiteById(**test_data),query.return_value)
		query.assert_called_with('tl.getTestSuiteByID', devKey=None, **test_data)
		self._api._tl_version = Version("0.9")
		self.assertRaises(NotSupported,self._api.getTestSuiteById)

	@patch("testlink.api.Testlink_XML_RPC_API._query")
	def test_getTestSuitesForTestSuite(self,query):
		"""'getTestSuitesForTestSuite' (1.0)"""
		query.return_value = [randict("name","id"),randict("name","id")]
		test_data = randict("testsuiteid")
		self.assertEquals(self._api.getTestSuitesForTestSuite(**test_data),query.return_value)
		query.assert_called_with('tl.getTestSuitesForTestSuite', devKey=None,**test_data)
		self._api._tl_version = Version("0.9")
		self.assertRaises(NotSupported,self._api.getTestSuitesForTestSuite)

	@patch("testlink.api.Testlink_XML_RPC_API._query")
	def test_getFirstLevelTestSuitesForTestProject(self,query):
		"""'getFirstLevelTestSuitesForTestProject' (1.0)"""
		query.return_value = [randict("name","id"),randict("name","id")]
		test_data = randict("testprojectid")
		self.assertEquals(self._api.getFirstLevelTestSuitesForTestProject(**test_data),query.return_value)
		query.assert_called_with('tl.getFirstLevelTestSuitesForTestProject', devKey=None, **test_data)
		self._api._tl_version = Version("0.9")
		self.assertRaises(NotSupported,self._api.getFirstLevelTestSuitesForTestProject)

	@patch("testlink.api.Testlink_XML_RPC_API._query")
	def test_createTestCase(self,query):
		"""'createTestCase' (1.0)"""
		query.return_value = randict("message")
		# Check default params
		defaults = randict("testcasename","testsuiteid","testprojectid","authorlogin","summary")
		self.assertEquals(self._api.createTestCase(**defaults),query.return_value)
		query.assert_called_with('tl.createTestCase',\
						devKey = None,\
						steps = [],\
						preconditions = None,\
						importance = ImportanceLevel.MEDIUM,\
						executiontype = ExecutionType.MANUAL,\
						order = None,\
						checkduplicatedname = True,\
						actiononduplicatedname = 'block',\
						**defaults\
					)
		# Check with specified parameters
		non_defaults = randict("testcasename","testsuiteid","testprojectid","authorlogin","summary","steps","preconditions","importance","executiontype","order","checkduplicatedname","actiononduplicatedname")
		self.assertEquals(self._api.createTestCase(**non_defaults),query.return_value)
		query.assert_called_with('tl.createTestCase',\
						devKey = None,\
						**non_defaults\
					)
		self._api._tl_version = Version("0.9")
		self.assertRaises(NotSupported,self._api.createTestCase)

	@patch("testlink.api.Testlink_XML_RPC_API._query")
	def test_updateTestCase(self,query):
		"""'updateTestCase' (1.9.8)"""
		query.return_value = randict("message")
		self.assertRaises(NotSupported,self._api.updateTestCase)
		self._api._tl_version = Version("1.9.8")
		# Check default params
		defaults = randict("testcaseexternalid")
		self.assertEquals(self._api.updateTestCase(**defaults),query.return_value)
		query.assert_called_with('tl.updateTestCase',\
						devKey = None,\
						version = None,\
						testcasename = None,\
						summary = None,\
						preconditions = None,\
						steps = None,\
						importance = None,\
						executiontype = None,\
						status = None,\
						estimatedexecduration = None,\
						user = None,\
						**defaults\
					)
		# Check with specified parameters
		non_defaults = randict("testcaseexternalid","version","testcasename","summary","preconditions","steps","importance","executiontype","status","estimatedexecduration","user")
		self.assertEquals(self._api.updateTestCase(**non_defaults),query.return_value)
		query.assert_called_with('tl.updateTestCase',\
						devKey = None,\
						**non_defaults\
					)

	@patch("testlink.api.Testlink_XML_RPC_API._query")
	def test_setTestCaseExecutionType(self,query):
		"""'setTestCaseExecutionType' (1.9.4)"""
		query.return_value = randict("message")
		test_data = randict("testcaseexternalid","version","testprojectid","executiontype")
		self.assertRaises(NotSupported,self._api.setTestCaseExecutionType)
		self._api._tl_version = Version("1.9.4")
		self.assertEquals(self._api.setTestCaseExecutionType(**test_data),query.return_value)
		query.assert_called_with('tl.setTestCaseExecutionType',\
						devKey = None,\
						**test_data\
					)

	@patch("testlink.api.Testlink_XML_RPC_API._query")
	def test_createTestCaseSteps(self,query):
		"""'createTestCaseSteps' (1.9.4)"""
		query.return_value = randict("message")
		self.assertRaises(NotSupported,self._api.createTestCaseSteps)
		self._api._tl_version = Version("1.9.4")
		# Check default params
		defaults = randict("steps","action")
		self.assertEquals(self._api.createTestCaseSteps(**defaults),query.return_value)
		query.assert_called_with('tl.createTestCaseStep',\
						devKey = None,\
						testcaseexternalid = None,\
						testcaseid = None,\
						version = None,\
						**defaults\
					)
		# Check with specified parameters
		non_defaults = randict("steps","action","testcaseid","testcaseexternalid","version")
		self.assertEquals(self._api.createTestCaseSteps(**non_defaults),query.return_value)
		query.assert_called_with('tl.createTestCaseStep',\
						devKey = None,\
						**non_defaults\
					)

	@patch("testlink.api.Testlink_XML_RPC_API._query")
	def test_deleteTestCaseSteps(self,query):
		"""'deleteTestCaseSteps' (1.9.4)"""
		query.return_value = randict("message")
		self.assertRaises(NotSupported,self._api.deleteTestCaseSteps)
		self._api._tl_version = Version("1.9.4")
		# Check default params
		defaults = randict("testcaseexternalid","steps")
		self.assertEquals(self._api.deleteTestCaseSteps(**defaults),query.return_value)
		query.assert_called_with('tl.deleteTestCaseSteps',\
						devKey = None,\
						version = None,\
						**defaults\
					)
		# Check with specified parameters
		non_defaults = randict("testcaseexternalid","steps","version")
		self.assertEquals(self._api.deleteTestCaseSteps(**non_defaults),query.return_value)
		query.assert_called_with('tl.deleteTestCaseSteps',\
						devKey = None,\
						**non_defaults\
					)

	@patch("testlink.api.Testlink_XML_RPC_API._query")
	def test_getTestCase(self,query):
		"""'getTestCase' (1.0)"""
		query.return_value = randict("name","id")
		# Check default params
		self.assertEquals(self._api.getTestCase(),query.return_value)
		query.assert_called_with('tl.getTestCase',\
						devKey = None,\
						testcaseid = None,\
						testcaseexternalid = None,\
						version = None\
					)
		# Check with specified parameters
		non_defaults = randict("testcaseid","testcaseexternalid","version")
		self.assertEquals(self._api.getTestCase(**non_defaults),query.return_value)
		query.assert_called_with('tl.getTestCase',\
						devKey = None,\
						**non_defaults\
					)
		self._api._tl_version = Version("0.9")
		self.assertRaises(NotSupported,self._api.getTestCase)

	@patch("testlink.api.Testlink_XML_RPC_API._query")
	def test_getTestCaseIdByName(self,query):
		"""'getTestCaseIdByName' (1.0)"""
		query.return_value = input()
		# Check default params
		defaults = randict("testcasename")
		self.assertEquals(self._api.getTestCaseIdByName(**defaults),query.return_value)
		query.assert_called_with('tl.getTestCaseIDByName',\
						devKey = None,\
						testsuitename = None,\
						testprojectname = None,\
						testcasepathname = None,\
						**defaults
					)
		# Check with specified parameters
		non_defaults = randict("testcasename","testsuitename","testprojectname","testcasepathname")
		self.assertEquals(self._api.getTestCaseIdByName(**non_defaults),query.return_value)
		query.assert_called_with('tl.getTestCaseIDByName',\
						devKey = None,\
						**non_defaults\
					)
		self._api._tl_version = Version("0.9")
		self.assertRaises(NotSupported,self._api.getTestCaseIdByName)

	@patch("testlink.api.Testlink_XML_RPC_API._query")
	def test_getTestCasesForTestSuite(self,query):
		"""'getTestCasesForTestSuite' (1.0/1.9.10)"""
		query.return_value = [randict("name","id"),randict("name","id"),randict("name","id")]
		# Check default params
		defaults = randict("testsuiteid")
		self.assertEquals(self._api.getTestCasesForTestSuite(**defaults),query.return_value)
		query.assert_called_with('tl.getTestCasesForTestSuite',\
						devKey = None,\
						deep = False,\
						details = 'simple',\
						**defaults\
					)
		# Check with specified parameters
		non_defaults = randict("testsuiteid","deep","details")
		self.assertEquals(self._api.getTestCasesForTestSuite(**non_defaults),query.return_value)
		query.assert_called_with('tl.getTestCasesForTestSuite',\
						devKey = None,\
						**non_defaults\
					)
		self._api._tl_version = Version("0.9")
		self.assertRaises(NotSupported,self._api.getTestCasesForTestSuite)
		# Check new argument 'getkeywords' since version 1.9.10
		self._api._tl_version = Version("1.9.10")
		self.assertEquals(self._api.getTestCasesForTestSuite(**defaults),query.return_value)
		query.assert_called_with('tl.getTestCasesForTestSuite',\
						devKey = None,\
						deep = False,\
						details = 'simple',\
						getkeywords = False,\
						**defaults\
					)
		non_defaults['getkeywords'] = input()
		self.assertEquals(self._api.getTestCasesForTestSuite(**non_defaults),query.return_value)
		query.assert_called_with('tl.getTestCasesForTestSuite',\
						devKey = None,\
						**non_defaults\
					)

	@patch("testlink.api.Testlink_XML_RPC_API._query")
	def test_getTestCasesForTestPlan(self,query):
		"""'getTesTCasesForTestPlan' (1.0 /1.9.4)"""
		query.return_value = [randict("name","id"),randict("name","id"),randict("name","id")]
		# Check default params
		defaults = randict("testplanid")
		self.assertEquals(self._api.getTestCasesForTestPlan(**defaults),query.return_value)
		query.assert_called_with('tl.getTestCasesForTestPlan',\
						devKey = None,\
						testcaseid = None,\
						buildid = None,\
						keywordid = None,\
						keywords = None,\
						executed = None,\
						assignedto = None,\
						executestatus = None,\
						executiontype = None,\
						getstepsinfo = False,\
						**defaults\
					)
		# Check with specified parameters
		non_defaults = randict("testplanid","testcaseid","buildid","keywordid","keywords","executed","assignedto","executestatus","executiontype","getstepsinfo")
		self.assertEquals(self._api.getTestCasesForTestPlan(**non_defaults),query.return_value)
		query.assert_called_with('tl.getTestCasesForTestPlan',\
						devKey = None,\
						**non_defaults\
					)
		self._api._tl_version = Version("0.9")
		self.assertRaises(NotSupported,self._api.getTestCasesForTestPlan)
		# Check new argument 'details' since version 1.9.4
		self._api._tl_version = Version("1.9.4")
		self.assertEquals(self._api.getTestCasesForTestPlan(**defaults),query.return_value)
		query.assert_called_with('tl.getTestCasesForTestPlan',\
						devKey = None,\
						testcaseid = None,\
						buildid = None,\
						keywordid = None,\
						keywords = None,\
						executed = None,\
						assignedto = None,\
						executestatus = None,\
						executiontype = None,\
						getstepsinfo = False,\
						details = 'full',\
						**defaults\
					)
		non_defaults['details'] = input()
		self.assertEquals(self._api.getTestCasesForTestPlan(**non_defaults),query.return_value)
		query.assert_called_with('tl.getTestCasesForTestPlan',\
						devKey = None,\
						**non_defaults\
					)

	@patch("testlink.api.Testlink_XML_RPC_API._query")
	def test_addTestCaseToTestPlan(self,query):
		"""'addTestCaseToTestPlan' (1.0)"""
		query.return_value = randict("message")
		# Check default params
		defaults = randict("testprojectid","testplanid","testcaseexternalid","version")
		self.assertEquals(self._api.addTestCaseToTestPlan(**defaults),query.return_value)
		query.assert_called_with('tl.addTestCaseToTestPlan',\
						devKey = None,\
						platformid = None,\
						executionorder = None,\
						urgency = None,\
						**defaults
					)
		# Check with specified parameters
		non_defaults = randict("testprojectid","testplanid","testcaseexternalid","version","platformid","executionorder","urgency")
		self.assertEquals(self._api.addTestCaseToTestPlan(**non_defaults),query.return_value)
		query.assert_called_with('tl.addTestCaseToTestPlan',\
						devKey = None,\
						**non_defaults\
					)
		self._api._tl_version = Version("0.9")
		self.assertRaises(NotSupported,self._api.addTestCaseToTestPlan)

	@patch("testlink.api.Testlink_XML_RPC_API._query")
	def test_addPlatformToTestPlan(self,query):
		"""'addPlatformToTestPlan' (1.9.6)"""
		query.return_value = randict("message")
		test_data = randict("testplanid","platformname")
		self.assertRaises(NotSupported,self._api.addPlatformToTestPlan)
		self._api._tl_version = Version("1.9.6")
		self.assertEquals(self._api.addPlatformToTestPlan(**test_data),query.return_value)
		query.assert_called_with('tl.addPlatformToTestPlan',\
						devKey = None,\
						**test_data\
					)

	@patch("testlink.api.Testlink_XML_RPC_API._query")
	def test_removePlatformFromTestPlan(self,query):
		"""'removePlatformFromTestPlan' (1.9.6)"""
		query.return_value = randict("message")
		test_data = randict("testplanid","platformname")
		self.assertRaises(NotSupported,self._api.removePlatformFromTestPlan)
		self._api._tl_version = Version("1.9.6")
		self.assertEquals(self._api.removePlatformFromTestPlan(**test_data),query.return_value)
		query.assert_called_with('tl.removePlatformFromTestPlan',\
						devKey = None,\
						**test_data\
					)

	@patch("testlink.api.Testlink_XML_RPC_API._query")
	def test_assignRequirements(self,query):
		"""'assignRequirements' (1.0)"""
		query.return_value = randict("message")
		test_data = randict("testcaseexternalid","testprojectid","requirements")
		self.assertEquals(self._api.assignRequirements(**test_data),query.return_value)
		query.assert_called_with('tl.assignRequirements',\
						devKey = None,\
						**test_data\
					)
		self._api._tl_version = Version("0.9")
		self.assertRaises(NotSupported,self._api.assignRequirements)

	@patch("testlink.api.Testlink_XML_RPC_API._query")
	def test_getReqSpecCustomFieldDesignValue(self,query):
		"""'getReqSpecCustomFieldDesignValue' (1.9.4)"""
		query.return_value = input()
		test_data = randict("reqspecid","testprojectid","customfieldname")
		self.assertRaises(NotSupported,self._api.getReqSpecCustomFieldDesignValue)
		self._api._tl_version = Version("1.9.4")
		self.assertEquals(self._api.getReqSpecCustomFieldDesignValue(**test_data),query.return_value)
		query.assert_called_with('tl.getReqSpecCustomFieldDesignValue',\
						devKey = None,\
						**test_data\
					)

	@patch("testlink.api.Testlink_XML_RPC_API._query")
	def test_getRequirementCustomFieldDesignValue(self,query):
		"""'getRequirementCustomFieldDesignValue' (1.9.4)"""
		query.return_value = input()
		test_data = randict("requirementid","testprojectid","customfieldname")
		self.assertRaises(NotSupported,self._api.getRequirementCustomFieldDesignValue)
		self._api._tl_version = Version("1.9.4")
		self.assertEquals(self._api.getRequirementCustomFieldDesignValue(**test_data),query.return_value)
		query.assert_called_with('tl.getRequirementCustomFieldDesignValue',\
						devKey = None,\
						**test_data\
					)

	@patch("testlink.api.Testlink_XML_RPC_API._query")
	def test_getTestSuiteCustomFieldDesignValue(self,query):
		"""'getTestSuiteCustomFieldDesignValue' (1.9.4)"""
		query.return_value = randict("name","id","value")
		test_data = randict("testsuiteid","testprojectid","customfieldname")
		self.assertRaises(NotSupported,self._api.getTestSuiteCustomFieldDesignValue)
		self._api._tl_version = Version("1.9.4")
		self.assertEquals(self._api.getTestSuiteCustomFieldDesignValue(**test_data),query.return_value)
		query.assert_called_with('tl.getTestSuiteCustomFieldDesignValue',\
						devKey = None,\
						**test_data\
					)

	@patch("testlink.api.Testlink_XML_RPC_API._query")
	def test_getTestCaseCustomFieldDesignValue(self,query):
		"""'getTestCaseCustomFieldDesignValue' (1.0)"""
		query.return_value = randict("name","id","value")
		# Check default params
		defaults = randict("testcaseexternalid","version","testprojectid","customfieldname")
		self.assertEquals(self._api.getTestCaseCustomFieldDesignValue(**defaults),query.return_value)
		query.assert_called_with('tl.getTestCaseCustomFieldDesignValue',\
						devKey = None,\
						details = 'value',\
						**defaults
					)
		# Check with specified parameters
		non_defaults = randict("testcaseexternalid","version","testprojectid","customfieldname","details")
		self.assertEquals(self._api.getTestCaseCustomFieldDesignValue(**non_defaults),query.return_value)
		query.assert_called_with('tl.getTestCaseCustomFieldDesignValue',\
						devKey = None,\
						**non_defaults\
					)
		self._api._tl_version = Version("0.9")
		self.assertRaises(NotSupported,self._api.getTestCaseCustomFieldDesignValue)

	@patch("testlink.api.Testlink_XML_RPC_API._query")
	def test_updateTestCaseCustomFieldDesignValue(self,query):
		"""'updateTestCaseCustomFieldDesignValue' (1.9.4)"""
		query.return_value = randict("message")
		test_data = randict("testcaseexternalid","version","testprojectid","customfields")
		self.assertRaises(NotSupported,self._api.updateTestCaseCustomFieldDesignValue)
		self._api._tl_version = Version("1.9.4")
		self.assertEquals(self._api.updateTestCaseCustomFieldDesignValue(**test_data),query.return_value)
		query.assert_called_with('tl.updateTestCaseCustomFieldDesignValue',\
						devKey = None,\
						**test_data\
					)

	@patch("testlink.api.Testlink_XML_RPC_API._query")
	def test_getTestCaseCustomFieldExecutionValue(self,query):
		"""'getTestCaseCustomFieldExecutionValue' (1.9.4)"""
		query.return_value = randict("name","id","value")
		test_data = randict("executionid","testplanid","version","testprojectid","customfieldname")
		self.assertRaises(NotSupported,self._api.getTestCaseCustomFieldExecutionValue)
		self._api._tl_version = Version("1.9.4")
		self.assertEquals(self._api.getTestCaseCustomFieldExecutionValue(**test_data),query.return_value)
		query.assert_called_with('tl.getTestCaseCustomFieldExecutionValue',\
						devKey = None,\
						**test_data\
					)

	@patch("testlink.api.Testlink_XML_RPC_API._query")
	def test_getTestCaseCustomFieldTestPlanDesignValue(self,query):
		"""'getTestCaseCustomFieldTestPlanDesignValue' (1.9.4)"""
		query.return_value = randict("name","id","value")
		test_data = randict("linkid","testplanid","version","testprojectid","customfieldname")
		self.assertRaises(NotSupported,self._api.getTestCaseCustomFieldTestPlanDesignValue)
		self._api._tl_version = Version("1.9.4")
		self.assertEquals(self._api.getTestCaseCustomFieldTestPlanDesignValue(**test_data),query.return_value)
		query.assert_called_with('tl.getTestCaseCustomFieldTestPlanDesignValue',\
						devKey = None,\
						**test_data\
					)

	@patch("testlink.api.Testlink_XML_RPC_API._query")
	def test_uploadAttachment(self,query):
		"""'uploadAttachment' (1.0)"""
		query.return_value = randict("message")
		# Check default params
		defaults = randict("fkid","fktable","filename","filetype","content")
		self.assertEquals(self._api.uploadAttachment(**defaults),query.return_value)
		query.assert_called_with('tl.uploadAttachment',\
						devKey = None,\
						title = None,\
						description = None,\
						**defaults\
					)
		# Check with specified parameters
		non_defaults = randict("fkid","fktable","filename","filetype","content","title","description")
		self.assertEquals(self._api.uploadAttachment(**non_defaults),query.return_value)
		query.assert_called_with('tl.uploadAttachment',\
						devKey = None,\
						**non_defaults\
					)
		self._api._tl_version = Version("0.9")
		self.assertRaises(NotSupported,self._api.uploadAttachment)

	@patch("testlink.api.Testlink_XML_RPC_API._query")
	def test_uploadRequirementSpecificationAttachment(self,query):
		"""'uploadRequirementSpecificationAttachment' (1.0)"""
		query.return_value = randict("message")
		# Check default params
		defaults = randict("reqspecid","filename","filetype","content")
		self.assertEquals(self._api.uploadRequirementSpecificationAttachment(**defaults),query.return_value)
		query.assert_called_with('tl.uploadRequirementSpecificationAttachment',\
						devKey = None,\
						title = None,\
						description = None,\
						**defaults\
					)
		# Check with specified parameters
		non_defaults = randict("reqspecid","filename","filetype","content","title","description")
		self.assertEquals(self._api.uploadRequirementSpecificationAttachment(**non_defaults),query.return_value)
		query.assert_called_with('tl.uploadRequirementSpecificationAttachment',\
						devKey = None,\
						**non_defaults\
					)
		self._api._tl_version = Version("0.9")
		self.assertRaises(NotSupported,self._api.uploadRequirementSpecificationAttachment)

	@patch("testlink.api.Testlink_XML_RPC_API._query")
	def test_uploadRequirementAttachment(self,query):
		"""'uploadRequirementAttachment' (1.0)"""
		query.return_value = randict("message")
		# Check default params
		defaults = randict("requirementid","filename","filetype","content")
		self.assertEquals(self._api.uploadRequirementAttachment(**defaults),query.return_value)
		query.assert_called_with('tl.uploadRequirementAttachment',\
						devKey = None,\
						title = None,\
						description = None,\
						**defaults\
					)
		# Check with specified parameters
		non_defaults = randict("requirementid","filename","filetype","content","title","description")
		self.assertEquals(self._api.uploadRequirementAttachment(**non_defaults),query.return_value)
		query.assert_called_with('tl.uploadRequirementAttachment',\
						devKey = None,\
						**non_defaults\
					)
		self._api._tl_version = Version("0.9")
		self.assertRaises(NotSupported,self._api.uploadRequirementAttachment)

	@patch("testlink.api.Testlink_XML_RPC_API._query")
	def test_uploadTestProjectAttachment(self,query):
		"""'uploadTestProjectAttachment' (1.0)"""
		query.return_value = randict("message")
		# Check default params
		defaults = randict("testprojectid","filename","filetype","content")
		self.assertEquals(self._api.uploadTestProjectAttachment(**defaults),query.return_value)
		query.assert_called_with('tl.uploadTestProjectAttachment',\
						devKey = None,\
						title = None,\
						description = None,\
						**defaults\
					)
		# Check with specified parameters
		non_defaults = randict("testprojectid","filename","filetype","content","title","description")
		self.assertEquals(self._api.uploadTestProjectAttachment(**non_defaults),query.return_value)
		query.assert_called_with('tl.uploadTestProjectAttachment',\
						devKey = None,\
						**non_defaults\
					)
		self._api._tl_version = Version("0.9")
		self.assertRaises(NotSupported,self._api.uploadTestProjectAttachment)

	@patch("testlink.api.Testlink_XML_RPC_API._query")
	def test_uploadTestSuiteAttachment(self,query):
		"""'uploadTestSuiteAttachment' (1.0)"""
		query.return_value = randict("message")
		# Check default params
		defaults = randict("testsuiteid","filename","filetype","content")
		self.assertEquals(self._api.uploadTestSuiteAttachment(**defaults),query.return_value)
		query.assert_called_with('tl.uploadTestSuiteAttachment',\
						devKey = None,\
						title = None,\
						description = None,\
						**defaults\
					)
		# Check with specified parameters
		non_defaults = randict("testsuiteid","filename","filetype","content","title","description")
		self.assertEquals(self._api.uploadTestSuiteAttachment(**non_defaults),query.return_value)
		query.assert_called_with('tl.uploadTestSuiteAttachment',\
						devKey = None,\
						**non_defaults\
					)
		self._api._tl_version = Version("0.9")
		self.assertRaises(NotSupported,self._api.uploadTestSuiteAttachment)

	@patch("testlink.api.Testlink_XML_RPC_API._query")
	def test_uploadTestCaseAttachment(self,query):
		"""'uploadTestCaseAttachment' (1.0)"""
		query.return_value = randict("message")
		# Check default params
		defaults = randict("testcaseid","filename","filetype","content")
		self.assertEquals(self._api.uploadTestCaseAttachment(**defaults),query.return_value)
		query.assert_called_with('tl.uploadTestCaseAttachment',\
						devKey = None,\
						title = None,\
						description = None,\
						**defaults\
					)
		# Check with specified parameters
		non_defaults = randict("testcaseid","filename","filetype","content","title","description")
		self.assertEquals(self._api.uploadTestCaseAttachment(**non_defaults),query.return_value)
		query.assert_called_with('tl.uploadTestCaseAttachment',\
						devKey = None,\
						**non_defaults\
					)
		self._api._tl_version = Version("0.9")
		self.assertRaises(NotSupported,self._api.uploadTestCaseAttachment)

	@patch("testlink.api.Testlink_XML_RPC_API._query")
	def test_uploadExecutionAttachment(self,query):
		"""'uploadExecutionAttachment' (1.0)"""
		query.return_value = randict("message")
		# Check default params
		defaults = randict("executionid","filename","filetype","content")
		self.assertEquals(self._api.uploadExecutionAttachment(**defaults),query.return_value)
		query.assert_called_with('tl.uploadExecutionAttachment',\
						devKey = None,\
						title = None,\
						description = None,\
						**defaults\
					)
		# Check with specified parameters
		non_defaults = randict("executionid","filename","filetype","content","title","description")
		self.assertEquals(self._api.uploadExecutionAttachment(**non_defaults),query.return_value)
		query.assert_called_with('tl.uploadExecutionAttachment',\
						devKey = None,\
						**non_defaults\
					)
		self._api._tl_version = Version("0.9")
		self.assertRaises(NotSupported,self._api.uploadExecutionAttachment)

	@patch("testlink.api.Testlink_XML_RPC_API._query")
	def test_getTestCaseAttachments(self,query):
		"""'getTestCaseAttachments' (1.0)"""
		query.return_value = randict("name","type","content","title")
		# Check default params
		self.assertEquals(self._api.getTestCaseAttachments(),query.return_value)
		query.assert_called_with('tl.getTestCaseAttachments',\
						devKey = None,\
						testcaseid = None,\
						testcaseexternalid = None\
					)
		# Check with specified parameters
		non_defaults = randict("testcaseid","testcaseexternalid")
		self.assertEquals(self._api.getTestCaseAttachments(**non_defaults),query.return_value)
		query.assert_called_with('tl.getTestCaseAttachments',\
						devKey = None,\
						**non_defaults\
					)
		self._api._tl_version = Version("0.9")
		self.assertRaises(NotSupported,self._api.getTestCaseAttachments)

	@patch("testlink.api.Testlink_XML_RPC_API._query")
	def test_getRequirementSpecificationsForTestProject(self,query):
		"""'getRequirementSpecificationsForTestProject' (1.11-sinaqs)"""
		query.return_value = [randict("name","id"),randict("name","id")]
		test_data = randict("testprojectid")
		self.assertRaises(NotSupported,self._api.getRequirementSpecificationsForTestProject)
		self._api._tl_version = Version("1.11-sinaqs")
		self.assertEquals(self._api.getRequirementSpecificationsForTestProject(**test_data),query.return_value)
		query.assert_called_with('tl.getRequirementSpecificationsForTestProject',\
						devKey = None,\
						**test_data\
					)

	@patch("testlink.api.Testlink_XML_RPC_API._query")
	def test_getRequirementsForRequirementSpecification(self,query):
		"""'getRequirementsForRequirementForRequirementSpecification' (1.11-sinaqs)"""
		query.return_value = [randict("name","id"),randict("name","id")]
		test_data = randict("reqspecid","testprojectid")
		self.assertRaises(NotSupported,self._api.getRequirementsForRequirementSpecification)
		self._api._tl_version = Version("1.11-sinaqs")
		self.assertEquals(self._api.getRequirementsForRequirementSpecification(**test_data),query.return_value)
		query.assert_called_with('tl.getRequirementsForRequirementSpecification',\
						devKey = None,\
						**test_data\
					)

	@patch("testlink.api.Testlink_XML_RPC_API._query")
	def test_getRisksForRequirement(self,query):
		"""'getRisksForRequirement' (1.11-sinaqs)"""
		query.return_value = [randict("name","id"),randict("name","id")]
		test_data = randict("requirementid")
		self.assertRaises(NotSupported,self._api.getRisksForRequirement)
		self._api._tl_version = Version("1.11-sinaqs")
		self.assertEquals(self._api.getRisksForRequirement(**test_data),query.return_value)
		query.assert_called_with('tl.getRisksForRequirement',\
						devKey = None,\
						**test_data\
					)
