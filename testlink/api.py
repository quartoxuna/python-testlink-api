#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@author: Kai Borowiak
@summary: Raw API Wrapper for Testlink
"""

# IMPORTS
import xmlrpclib
from log import log
from exceptions import NotSupported
from exceptions import APIError
from exceptions import InvalidURL

class Testlink_XML_RPC_API(object):
	"""Testlink XML-RPC API
	@cvar RPC_PATHS: Paths to Testlink's XML-RPC endpoint
	@type RPC_PATHS: list
	@ivar _proxy: Used ServerProxy instance
	@type _proxy: xmlrpclib.ServerProxy
	@ivar _devkey: Used Developer Key
	@type _devkey: str
	"""

	RPC_PATHS = ["/lib/api/xmlrpc.php","/lib/api/xmlrpc/v1/xmlrpc.php"]

	def __init__(self,url):
		"""Initialize the TestlinkAPI
		@param url: Testlink URL
		@type url: str
		@raises InvalidURL: The given URL is not valid
		"""
		self._proxy = None
		self._devkey = None
		# Check for each possible RPC path,
		# if a connection can be made
		for path in self.RPC_PATHS:
			tmp = url
			try:
				if not tmp.endswith(path):
					tmp += path
				self._proxy = xmlrpclib.ServerProxy(tmp,encoding='UTF-8',allow_none=True)
				# Check if URL ends on XML-RPC endpoint
				self._proxy.system.listMethods()
				return
			except Exception:
				pass
		raise InvalidURL(url)

	def __str__(self):
		return str(self._proxy)

	def __repr__(self):
		return str(self._proxy)

	def _query(self,method,**kwargs):
		"""Remote calls a method on the server
		@param method: Method to call
		@type method: str
		@raise NotSupported: Called method is not supported by Testlink
		@raise APIError: Testlink API server side error
		"""
		# Use class wide devkey if not given
		if not ('devKey' in kwargs and kwargs['devKey']) or kwargs['devKey'].strip() == "":
			kwargs['devKey'] = self._devkey

		# Check for empty method name
		if not method or method.strip()=="":
			raise NotSupported("Empty method name")

		log.debug("Query: %s(%s)" % (str(method),str(kwargs)) )
		try:
			# Call the actual method
			fn = getattr(self._proxy,method)
			resp = fn(kwargs)
			log.debug("Response: %s" % str(resp))
		except xmlrpclib.Fault,f:
			if (f.faultCode == NotSupported.errorCode):
				raise NotSupported(method)
		else:
			# Check for API error [{'code': 123, 'message': foo}]
			if isinstance(resp,list) and len(resp)==1:
				tmp = resp[0]
				if (('code' in tmp) and ('message' in tmp)):
					raise APIError(tmp['code'],tmp['message'])
			return resp

	#
	# Raw API methods
	#

	def testLinkVersion(self):
		"""Returns Testlink Version String
		@since: Testlink 1.9.9

		@returns: Version String
		@rtype: str
		"""
		return self._query("tl.testLinkVersion")


	def about(self):
		"""Returns informations about the current Testlink API
		@returns: 'Testlink API Version: x.x initially written by Asial Brumfield with contributions by Testlink development Team'
		@rtype: str
		"""
		return self._query("tl.about")


	def sayHello(self):
		"""Returns the string 'Hello!'
		@returns: 'Hello!'
		@rtype: str
		"""
		return self._query("tl.sayHello")
	ping = sayHello


	def repeat(self,value):
		"""Repeats the given value
		@param value: The value to be repeated by the server
		@type value: mixed
		@returns: String 'You said: ' and the given value
		@rtype: mixed
		"""
		return self._query("tl.repeat", str=str(value))


	def checkDevKey(self,devkey=None):
		"""Checks if the specified developer key is valid
		@param devkey: The developer key to be tested
		@type devkey: str
		@returns: True/False
		@rtype: bool
		"""
		return self._query("tl.checkDevKey", devKey=devkey)


	def doesUserExist(self, user, devkey=None):
		"""Checks, if a specified user exists
		@param devkey: Testlink developer key
		@type devkey: str
		@param user: User to be tested
		@type user: str
		@returns: True/False
		@rtype: bool
		"""
		return self._query("tl.doesUserExist", devKey=devkey, user=user)

	def getUserByLogin(self, user, devkey=None):
		"""Returns user information for specified user
		@since: Testlink 1.9.8

		@param devkey: Testlink devloper key
		@type devkey: str
		@param user: Login name
		@type user: str
		@returns: User Information array
		@rtype: dict
		"""
		return self._query("tl.getUserByLogin", \
				devKey = devkey, \
				user = user )

	def getUserByID(self, userid, devkey=None):
		"""Returns user information for specified user
		@since: Testlink 1.9.8

		@param devkey: Testlink developer key
		@type devkey: str
		@param userid: The internal ID of the user
		@type userid: int
		@returns: User Information array
		@rtype: dict
		"""
		return self._query("tl.getUserByID", \
				devKey = devkey, \
				userid = userid )


	def getFullPath(self, nodeid, devkey=None):
		"""Returns the full path of an object
		@param devkey: Testlink developer key
		@type devkey: str
		@param nodeid: The internal ID of the object
		@type nodeid: int
		@returns: Hierarchical path of the object
		@rtype: str
		"""
		return self._query("tl.getFullPath", devKey=devkey, nodeID=nodeid)


	def createTestProject(self, name, prefix, notes='', active=True, public=True, requirements=False, priority=False, automation=False, inventory=False, devkey=None):
		"""Creates a new TestProject
		@param devkey: Testlink developer key
		@type devkey: str
		@param name: Name of the TestProject
		@type name: str
		@param prefix: The prefix for TestCases within the new TestProject
		@type prefix: str
		@param notes: <OPTIONAL> Additional notes of the TestProject (Default is: '')
		@type notes: str
		@param active: <OPTIONAL> The TestProject is marked as active (Default is: True)
		@type active: bool
		@param public: <OPTIONAL> The TestProject is marked as public (Default is: True)
		@type public: bool
		@param requirements: <OPTIONAL> The TestProject supports requirements (Default is: False)
		@type requirements: bool
		@param priority: <OPTIONAL> The TestProject supports test case priority (Default is: False)
		@type priority: bool
		@param automation: <OPTIONAL> The TestProject supports test automation (Default is: False)
		@type automation: bool
		@param inventory: <OPTIONAL> The TestProject supports inventory features (Default is: False)
		@type inventory: bool
		@returns: Server response
		@rtype: dict/list/???

		@todo: Refactor option flags
		@todo: Specify return value
		"""

		opts = {
			'requirementsEnabled': requirements,
			'testPriorityEnabled': priority,
			'automationEnabled': automation,
			'inventoryEnabled': inventory
			}

		return self._query("tl.createTestProject", \
					devKey  = devkey,   \
					name    = name,     \
					prefix  = prefix,   \
					notes   = notes,    \
					active  = active,   \
					public  = public,   \
					options = opts )


	def getProjects(self, devkey=None):
		"""Returns all available TestProjects
		@param devkey: Testlink developer key
		@type devkey: str
		@returns: TestProjects as list of dicts
		@rtype: list
		"""
		return self._query("tl.getProjects", devKey=devkey)


	def getTestProjectByName(self, name, devkey=None):
		"""Returns a single TestProject specified by its name
		@param devkey: Testlink developer key
		@type devkey: str
		@param name: Name of the TestProject
		@type name: str
		@returns: Matching TestProject
		@rtype: dict
		"""
		return self._query("tl.getTestProjectByName", devKey=devkey, testprojectname=name)


	def createTestPlan(self, name, projectname, notes='', active=True, public=True, devkey=None):
		"""Creates a new TestPlan
		@param devkey: Testlink developer key
		@type devkey: str
		@param name: Name of the TestPlan
		@type name: str
		@param projectname: Name of the parent TestProject
		@type projectname: str
		@param notes: <OPTIONAL> Additional notes of the TestPlan (Default is: '')
		@type notes: str
		@param active: <OPTIONAL> The TestPlan is marked as active (Default is: True)
		@type active: bool
		@param public: <OPTIONAL> The TestPlan is marked as public (Default is: True)
		@type public: bool
		@returns: Server response
		@rtype: dict/list/???

		@todo: Refactor optional arguments -> static values?
		@todo: Specify return value
		"""
		return self._query("tl.createTestPlan",              \
					devKey          = devkey,     \
					testplanname    = name,       \
					testprojectname = projectname,\
					notes           = notes,      \
					active          = active,     \
					public          = public )


	def getTestPlanByName(self, name, projectname, devkey=None):
		"""Returns a single TestPlan specified by its name
		@param devkey: Testlink developer key
		@type devkey: str
		@param name: Name of the TestPlan
		@type name: str
		@param projectname: Name of the parent TestProject
		@type projectname: str
		@returns: Matching TestPlan
		@rtype: dict
		"""
		return self._query("tl.getTestPlanByName",       \
					devKey          = devkey, \
					testplanname    = name,   \
					testprojectname = projectname )


	def getProjectTestPlans(self, projectid, devkey=None):
		"""Returns all TestPlans for a specified TestProject
		@param devkey: Testlink developer key
		@type devkey: str
		@param projectid: The internal ID of the TestProject
		@type projectid: int
		@returns: Matching TestPlans
		@rtype: list
		"""
		return self._query("tl.getProjectTestPlans",  \
					devKey       = devkey, \
					testprojectid = projectid )


	def getTestPlanCustomFieldDesignValue(self, testplanid, testprojectid, fieldname, devkey=None):
		"""Returns the value of a specified CustomField for a specified TestPlan
		@since: Testlink 1.9.4

		@param devkey: Testlink developer key
		@type devkey: str
		@param testplanid: The internal ID of the TestPlan
		@type testplanid: int
		@param testprojectid: The internal ID of the TestProject
		@type testprojectid: int
		@param fieldname: The internal name of the CustomField
		@type fieldname: str
		@returns: Server response
		@rtype: list/dict/???
		"""
		return self._query("tl.getTestPlanCustomFieldValue", \
					devKey = devkey, \
					customfieldname = fieldname, \
					testprojectid = testprojectid, \
					testplanid = testplanid )


	def createBuild(self, testplanid, name, notes='', devkey=None):
		"""Creates a new Build for the specified TestPlan
		@param devkey: Testlink developer key
		@type devkey: str
		@param testplanid: The internal ID of the parent TestPlan
		@type testplanid: int
		@param name: The name of the Build
		@type name: str
		@param notes: <OPTIONAL> Additional notes for the Build (Default is: '')
		@type notes: str
		@returns: Server response
		@rtype: list/dict/???

		@todo: Specify return value type
		"""
		return self._query("tl.createBuild",            \
					devKey     = devkey,     \
					testplanid = testplanid, \
					buildname  = name,       \
					buildnotes = notes )


	def getLatestBuildForTestPlan(self, testplanid, devkey=None):
		"""Returns the latest Build for the specified TestPlan
		@param devkey: Testlink developer key
		@type devkey: str
		@param testplanid: The internal ID of the TestPlan
		@type testplanid: int
		@returns: Matching Build
		@rtype: list
		"""
		return self._query("tl.getLatestBuildForTestPlan", \
					devKey     = devkey,        \
					testplanid = testplanid )
	
	
	def getBuildsForTestPlan(self, testplanid, devkey=None):
		"""Returns all Builds for the specified TestPlan
		@param devkey: Testlink developer key
		@type devkey: str
		@param testplanid: The internal ID of the TestPlan
		@type testplanid: int
		@returns: Matching Builds
		@rtype: list
		"""
		return self._query("tl.getBuildsForTestPlan", \
					devKey     = devkey,   \
					testplanid = testplanid )


	def getExecCountersByBuild(self, testplanid, devkey=None):
		"""Returns the execution counters for a specified testplan
		@since: Testlink 1.9.4

		@param devkey: Testlink developer key
		@type devkey: str
		@param testplanid: The internal ID of the TestPlan
		@type testplanid: int
		@returns: Server response
		@rtype: list/dict/???
		"""
		return self._query("tl.getExecCountersByBuild", \
					devKey = devkey, \
					testplanid = testplanid )


	def createPlatform(self, testprojectname, platformname, notes="", devkey=None):
		"""Creates a new Platform for the specified testproject
		@since: Testlink 1.9.6

		@param devkey: Testlink developer key
		@type devkey: str
		@param testprojectname: The Name of the parent TestProject
		@type testprojectname: str
		@param platformname: The Name of the new Platform
		@type platformname: str
		@param notes: <OPTIONAL> Additional notes for the new Platform
		@type notes: str
		@returns: Server response
		@rtype: list/dict/???

		@todo: Normalize return type
		"""
		return self._query("tl.createPlatform", \
					devKey = devkey, \
					testprojectname = testprojectname, \
					platformname = platformname,  \
					notes = notes )

	def getProjectPlatforms(self, testprojectid, devkey=None):
		"""Returns all platforms for a specified TestProject
		@since: Testlink 1.9.6

		@param devkey: Testlink developer key
		@type devkey: str
		@param testprojectid: The internal ID of the TestProject
		@type testprojectid: int
		@returns: Server response
		@rtype: list/dict/???
		"""
		return self._query("tl.getProjectPlatforms", \
					devKey = devkey, \
					testprojectid = testprojectid )
	
	
	def getTestPlanPlatforms(self, testplanid, devkey=None):
		"""Returns all Platforms fot the specified TestPlan
		@param devkey: Testlink developer key
		@type devkey: str
		@param testplanid: The internal ID of the TestPlan
		@type testplanid: int
		@returns: Matching Platforms
		@rtype: list
		"""
		return self._query("tl.getTestPlanPlatforms", \
					devKey     = devkey,  \
					testplanid = testplanid )
	
	
	def reportTCResult(self, testplanid, status, testcaseid=None, testcaseexternalid=None, buildid=None, buildname=None, notes=None, guess=True, bugid=None, platformid=None, platformname=None, customfields=None, overwrite=False, devkey=None):
		"""Sets the execution result for a specified TestCase
		@param devkey: Testlink developer key
		@type devkey: str
		@param testplanid: The internal ID of the TestPlan
		@type testplanid: int
		@param status: The result of the TestCase
		@type status: char
		@param testcaseid: <OPTIONAL> The internal ID of the TestCase. If not given, external ID must be set
		@type testcaseid: int
		@param testcaseexternalid: <OPTIONAL> The external ID of the TestCase. If not given, internal ID must be set
		@type testcaseexternalid: int
		@param buildid: <OPTIONAL> The external ID of the Build. If not given, the name must be set
		@type buildid: int
		@param buildname: <OPTIONAL> The name of the Build. If not given, the internal ID must be set
		@type buildname: str
		@param notes: <OPTIONAL> Additional notes of the execution result
		@type notes: str
		@param guess: <OPTIONAL> If set. API tries to guess missing parameters (Default is: True)
		@type guess: bool
		@param bugid: <OPTIONAL> The Bug ID referenced with the execution
		@type bugid: int
		@param platformid: <OPTIONAL> The internal ID of the Platform. If not given, the name must be set
		@type platformid: int
		@param platformname: <OPTIONAL> The name of the Platform. If not given, the internal ID must be set
		@param customfields: <OPTIONAL> Values for CustomFields
		@type customfields: dict
		@param overwrite: <OPTIONAL> Overwrites the latest result (Default is: False)
		@type overwrite: bool
		@returns: Server response
		@rtype: dict
		"""
		return self._query("tl.reportTCResult",                         \
					devKey             = devkey,             \
					testplanid         = testplanid,         \
					status             = status,             \
					testcaseid         = testcaseid,         \
					testcaseexternalid = testcaseexternalid, \
					buildid            = buildid,            \
					buildname          = buildname,          \
					notes              = notes,              \
					guess              = guess,              \
					bugid              = bugid,              \
					platformid         = platformid,         \
					platformname       = platformname,       \
					customfields       = customfields,       \
					overwrite          = overwrite )
	setTestCaseExecutionResult = reportTCResult

	
	def getLastExecutionResult(self, testplanid, testcaseid=None, testcaseexternalid=None, devkey=None):
		"""Returns the execution result for a specified TestCase and TestPlan
		@param devkey: Testlink developer key
		@type devkey: str
		@param testplanid: The internal ID of the TestPlan
		@type testplanid: int
		@param testcaseid: <OPTIONAL> The internal ID of the TestCase. If not given, the external ID must be set
		@type testcaseid: int
		@param testcaseexternalid: <OPTIONAL> The external ID of the TestCase. If not given, the internal ID must be set
		@type testcaseexternalid: int
		@returns: Matching result
		@rtype: dict
		"""
		return self._query("tl.getLastExecutionResult",         \
					devKey             = devkey,     \
					testplanid         = testplanid, \
					testcaseid         = testcaseid, \
					testcaseexternalid = testcaseexternalid )

	
	def deleteExecution(self, executionid, devkey=None):
		"""Deletes a specific exexution result
		@param devkey: Testlink developer key
		@type devkey: str
		@param executionid: The internal ID of the execution result
		@type executionid: int
		@returns: Server response
		@rtype: dict
		"""
		return self._query("tl.deleteExecution",     \
					devKey      = devkey, \
					executionid = executionid )
	
	
	def createTestSuite(self, name, testprojectid, details=None, parentid=None, order=None, checkduplicates=True, actiononduplicate='block', devkey=None):
		"""Creates a new TestSuite
		@param devkey: Testlink developer key
		@type devkey: str
		@param name: The name of the TestSuite
		@type name: str
		@param testprojectid: The internal ID of the parent TestProject
		@type testprojectid: int
		@param details: <OPTIONAL> Additional notes for the TestSuite
		@type details: str
		@param parentid: <OPTIONAL> The internal ID of the parent TestSuite
		@type parentid: int
		@param order: <OPTIONAL> Ordering withing the parent TestSuite
		@type order: int
		@param checkduplicates: <OPTIONAL> Enables duplicate handling (Default is: True)
		@type checkduplicates: bool
		@param actiononduplicate: <OPTIONAL> Action on duplicate (Default is: 'block')
		@param actiononduplicate: str
		@returns: Server response
		@rtype: dict
		"""
		return self._query("tl.createTestSuite",                         \
					devKey                 = devkey,          \
					testsuitename          = name,            \
					testprojectid          = testprojectid,   \
					details                = details,         \
					parentid               = parentid,        \
					order                  = order,           \
					checkduplicatedname    = checkduplicates, \
					actiononduplicatedname = actiononduplicate )
	
	
	def getTestSuiteById(self, suiteid, devkey=None):
		"""Returns a single TestSuite specified by the internal ID
		@param devkey: Testlink developer key
		@type devkey: str
		@param suiteid: The internal ID of the TestSuite
		@type suiteid: int
		@returns: Matching TestSuite
		@rtype: dict
		"""
		return self._query("tl.getTestSuiteByID",    \
					devKey      = devkey, \
					testsuiteid = suiteid )
	
	
	def getTestSuitesForTestSuite(self, suiteid, devkey=None):
		"""Returns all TestSuites within the specified TestSuite
		@param devkey: Testlink developer key
		@type devkey: str
		@param suiteid: The internal ID of the TestSuite
		@type suiteid: int
		@returns: Matching TestSuites
		@rtype: dict/list/???
		"""
		return self._query("tl.getTestSuitesForTestSuite", \
					devKey      = devkey,       \
					testsuiteid = suiteid )
	
	
	def getFirstLevelTestSuitesForTestProject(self, projectid, devkey=None):
		"""Returns the first level TestSuites for a specified TestProject
		@param devkey: Testlink developer key
		@type devkey: str
		@param projectid: The internal ID of the TestProject
		@type projectid: int
		@returns: Matching TestSuites
		@rtype: dict/list/???
		"""
		return self._query("tl.getFirstLevelTestSuitesForTestProject", \
					devKey        = devkey,                 \
					testprojectid = projectid )
	
	
	def getTestSuitesForTestPlan(self, planid, devkey=None):
		"""Returns all TestSuites for a specified TestPlan
		@param devkey: Testlink developer key
		@type devkey: str
		@param planid: The internal ID of the TestPlan
		@type planid: int
		@returns: Matching TestSuites
		@rtype: dict/list/???
		"""
		return self._query("tl.getTestSuitesForTestPlan", \
					devKey     = devkey,       \
					testplanid = planid )
	
	
	def createTestCase(self, name, suiteid, projectid, author, summary, steps=[], preconditions=None, importance=0, execution=0, order=None, checkduplicates=True, actiononduplicate='block', devkey=None):
		"""Creates a new TestCase
		@param devkey: Testlink developer key
		@type devkey: str
		@param name: TestCase title
		@type name: str
		@param suiteid: The internal ID of the parent TestSuite
		@type suiteid: int
		@param projectid: The internal ID of the parent TestProject
		@type projectid: int
		@param author: The author of the TestCase
		@type author: str
		@param summary: The summary of the TestCase
		@type summary: str
		@param steps: <OPTIONAL> Steps of the TestCase
		@type steps: list
		@param preconditions: <OPTIONAL> Preconditions of the TestCase
		@type preconditions: str
		@param importance: <OPTIONAL> The importance of the TestCase (Default is: 'LOW')
		@type importance: int
		@param execution: <OPTIONAL> The execution mode of the TestCase (Default is: 'MANUAL')
		@type execution: int
		@param order: <OPTIONAL> The order of the TestCase within the TestSuite
		@type order: int
		@param checkduplicates: <OPTIONAL> Enables duplicate handling (Default is: True)
		@type checkduplicates: bool
		@param actiononduplicate: <OPTIONAL> Action on duplicate (Default is: 'block')
		@type actiononduplicate: str
		@returns: Server response
		@rtype: dict/list/???
		"""
		return self._query("tl.createTestCase",                          \
					devKey                 = devkey,          \
					testcasename           = name,            \
					testsuiteid            = suiteid,         \
					testprojectid          = projectid,       \
					authorlogin            = author,          \
					summary                = summary,         \
					steps                  = steps,           \
					preconditions          = preconditions,   \
					importance             = importance,      \
					execution              = execution,       \
					order                  = order,           \
					checkduplicatedname    = checkduplicates, \
					actiononduplicatedname = actiononduplicate )

	def updateTestCase(self, testcaseexternalid, version=None, testcasename=None, summary=None, preconditions=None, steps=None, importance=None, executiontype=None, status=None, estimatedexecduration=None, user=None, devkey=None):
		"""Updates a specified TestCase
		@since: Testlink 1.9.8

		@param devkey: Testlink developer key
		@type devkey: str
		@param testcaseexternalid: The external ID of the TestCase (PREFIX-NUMBER)
		@type testcaseexternalid: str
		@param version: <OPTIONAL> The version of the TestCase
		@type version: int
		@param testcasename: <OPTIONAL> The name of the TestCase
		@type testcasename: str
		@param summary: <OPTIONAL> The summary of the TestCase
		@type summary: str
		@param preconditions: <OPTIONAL> The preconditions of the TestCase
		@type preconditions: str
		@param steps: <OPTIONAL> The steps of the TestCase
		@type steps: list
		@param importance: <OPTIONAL> The importance of the TestCase
		@type importance: int
		@param executiontype: <OPTIONAL> The execution type of the TestCase
		@type executiontype: int
		@param status: <OPTIONAL> The status of the TestCase
		@type status: ???
		@param estimatedexecduration: <OPTIONAL> The estimated duration for execution
		@type estimatedexecduration: ???
		@param user: <OPTIONAL> The user used as updater. If not given, will be set to user that request update.
		@type user: str
		@returns: Server response
		@rtype: dict/list/???
		"""
		return self._query("tl.updateTestCase", \
					devKey = devkey, \
					testcaseexternalid = testcaseexternalid, \
					version = version, \
					testcasename = testcasename, \
					summary = summary, \
					preconditions = preconditions, \
					steps = steps, \
					importance = importance, \
					executiontype = executiontype, \
					status = status, \
					estimatedexecduration = estimatedexecduration, \
					user = user )


	def setTestCaseExecutionType(self, testcaseexternalid, version, testprojectid, executiontype, devkey=None):
		"""Updates the execution type for a specified TestCase
		@since: Testlink 1.9.4

		@param devkey: Testlink developer key
		@type devkey: str
		@param testcaseexternalid: The external ID of the TestCase
		@type testcaseexternalid: int
		@param version: The version of the TestCase
		@type version: int
		@param testprojectid: The internal ID of the TestProject
		@type testprojectid: int
		@param executiontype: The execution type
		@type executiontype: testlink.ExecutionType
		@returns: Server response
		@rtype: list/dict/???
		"""
		return self._query("tl.setTestCaseExecutionType", \
					devKey = devkey, \
					testcaseexternalid = testcaseexternalid, \
					version = version, \
					testprojectid = testprojectid, \
					executiontype = executiontype )
	

	def createTestCaseSteps(self, steps, action, testcaseid=None, testcaseexternalid=None, version=None, devkey=None):
		"""Creates a new Step for the specified TestCase, can also be used for upgrade
		@since: Testlink 1.9.4

		@param devkey: Testlink developer key
		@type devkey: str
		@param steps: Steps to create, keys are: step_number,actions,expected,results,execution_type
		@type steps: list
		@param action: {'create' : If step exist, nothing will be done, 'update' : If step does not exist, will be created, else will be updated, 'push' : NOT IMPLEMENTED}
		@type action: str
		@param testcaseid: <OPTIONAL> The internal ID of the TestCase. If not given, external ID must be set.
		@type testcaseid: int
		@param testcaseexternalid: <OPTIONAL> The external IF of the TestCase. If not given, internal ID must be set.
		@type testcaseexternalid: int
		@param version: <OPTIONAL> Version of the TestCase, If not given, last active version will be used. If all versions are inactive, the latest version will be used.
		@type version: int
		@returns: Server response
		@rtype: dict/list/???
		"""
		return self._query("tl.createTestCaseStep",  \
					devKey = devkey,  \
					testcaseexternalid = testcaseexternalid, \
					testcaseid = testcaseid, \
					version = version, \
					action = action, \
					steps = steps )


	def deleteTestCaseSteps(self, testcaseexternalid, steps, version=None, devkey=None):
		"""Deletes specified Steps for the specified TestCase
		@since: Testlink 1.9.4

		@param devkey: Testlink developer key
		qtype devkey: str
		@param testcaseexternalid: The external ID of the TestCase
		@type testcaseexternalid: int
		@param steps: Step numbers to delete
		@type steps: list
		@param version: <OPTIONAL> The version of the TestCase. If not given, the last active version will be used.
		@type version: int
		@returns: Server response
		@rtype: dict/list/???
		"""
		return self._query("tl.deleteTestCaseSteps", \
					devKey = devkey, \
					testcaseexternalid = testcaseexternalid, \
					steps = steps, \
					version = version )

	
	def getTestCase(self, testcaseid=None, testcaseexternalid=None, version=None, devkey=None):
		"""Returns a single TestCase specified by its ID
		@param devkey: Testlink developer key
		@type devkey: str
		@param testcaseid: <OPTIONAL> The internal ID of the TestCase. If not given, external ID must be set
		@type testcaseid: int
		@param testcaseexternalid: <OPTIONAL> The external ID of the TestCase. If not given, internal ID must be set
		@type testcaseexternalid: int
		@param version: <OPTIONAL> The verion of the TestCase
		@type version: int
		@returns: Matching TestCase
		@rtype: list/dict/???
		"""
		return self._query("tl.getTestCase",                            \
					devKey             = devkey,             \
					testcaseid         = testcaseid,         \
					testcaseexternalid = testcaseexternalid, \
					version            = version )
	
	
	def getTestCaseIdByName(self, name, suite=None, project=None, path=None, devkey=None):
		"""Returns the internal ID of a specified TestCase
		@param devkey: Testlink developer key
		@type devkey: str
		@param name: Title of the TestCase
		@type name: str
		@param suite: <OPTIONAL> Name of the parent TestSuite
		@type suite: str
		@param project: <OPTIONAL> Name of the paren TestProject
		@type project: str
		@param path: <OPTIONAL> Hierarchical path of the TestCase
		@type path: str
		@returns: Matching TestCase ID
		@rtype: int?
		"""
		return self._query("tl.getTestCaseIDByName",       \
					devKey           = devkey,  \
					testcasename     = name,    \
					testsuitename    = suite,   \
					testprojectname  = project, \
					testcasepathname = path )
	
	
	def getTestCasesForTestSuite(self, suiteid, deep=False, details='simple', devkey=None):
		"""Returns all TestCases for a specified TestSuite
		@param devkey: Testlink developer key
		@type devkey: str
		@param suiteid: The internal ID of the TestSuite
		@type suiteid: int
		@param deep: <OPTIONAL> Recursively returns TestCases from TestSuite (Default is: False)
		@type deep: bool
		@param details: <OPTIONAL> Toggle detailed output (Defailt is: 'simple')
		@type details: str
		@returns: Matching TestCases
		@rtype: list/dict/???
		"""
		return self._query("tl.getTestCasesForTestSuite", \
					devKey      = devkey,      \
					testsuiteid = suiteid,     \
					deep        = deep,        \
					details     = details )
	
	
	def getTestCasesForTestPlan(self, planid, testcaseid=None, buildid=None, keywordid=None, keywords=None, executed=None, assignedto=None, executionstatus=None, executiontype=None, steps=False, devkey=None):
		"""Returns all TestCases for a specified TestPlan
		@param devkey: Testlink developer key
		@type devkey: str
		@param planid: The internal ID of the TestPlan
		@type planid: int
		@param testcaseid: <OPTIONAL> The internal ID of the TestCase
		@type testcaseid: int
		@param buildid: <OPTIONAL> The internal ID of the Build
		@type buildid: int
		@param keywordid: <OPTIONAL> The internal ID of a Keyword
		@type keywordid: int
		@param keywords: <OPTIONAL> Keywords to query
		@type keywords: list
		@param executed: <OPTIONAL> Toggles if the TestCase is already executed
		@type executed: bool
		@param assignedto: <OPTIONAL> Assigned user
		@type assignedto: str
		@param executionstatus: <OPTIONAL> The execution status
		@type executionstatus: int
		@param executiontype: <OPTIONAL> The execution type
		@type executiontype: int
		@param steps: <OPTIONAL> Toggles if steps are returned
		@type steps: bool
		@returns: Matching TestCases
		@rtype: list/dict/???
		"""
		return self._query("tl.getTestCasesForTestPlan",        \
					devKey        = devkey,          \
					testplanid    = planid,          \
					testcaseid    = testcaseid,      \
					buidlid       = buildid,         \
					keywordid     = keywordid,       \
					keywords      = keywords,        \
					executed      = executed,        \
					assignedto    = assignedto,      \
					executestatus = executionstatus, \
					executiontype = executiontype,   \
					getstepsinfo   = steps )
	
	
	def addTestCaseToTestPlan(self, projectid, planid, testcaseexternalid, version, platformid=None, executionorder=None, urgency=None, devkey=None):
		"""Adds a specified TestCase to a specified TestPlan
		@param devkey: Testlink developer key
		@type devkey: str
		@param projectid: The internal ID of the TestProject
		@type projectid: int
		@param planid: The internal ID of the TestPlan
		@type planid: int
		@param testcaseexternalid: The external ID of the TestCase
		@type testcaseexternalid: int
		@param version: The version of the TestCase
		@type version: int
		@param platformid: <OPTIONAL> The internal ID of the platform
		@type platformid: int
		@param executionorder: <OPTIONAL> The order of the TestCase within the execution TestSuite
		@type executionorder: int
		@param urgency: <OPTIONAL> The urgency level of the TestCase
		@type urgency: int
		@returns: Server response
		@rtype: dict

		@todo: Set valid values for urgency
		"""
		return self._query("tl.addTestCaseToTestPlan",                  \
					devKey             = devkey,             \
					testprojectid      = projectid,          \
					testplanid         = planid,             \
					testcaseexternalid = testcaseexternalid, \
					version            = version,            \
					platformid         = platformid,         \
					executionorder     = executionorder,     \
					urgency            = urgency )


	def addPlatformToTestPlan(self, testplanid, platformname, devkey=None):
		"""Adds a specified platform to a specified testplan
		@since: Testlink 1.9.6

		@param devkey: Testlink developer key
		@type devkey: str
		@param testplanid: The internal ID of the TestPlan
		@type testplanid: int
		@param platformname: The name of the platform to add
		@type platformname: str
		@returns: Server response
		@rtype: dict/list/???
		"""
		return self._query("tl.addPlatformToTestPlan", \
					devKey = devkey, \
					testplanid = testplanid, \
					platformname = platformname )


	def removePlatformFromTestPlan(self, testplanid, platformname, devkey=None):
		"""Removes a specified platform from a specified testplan.
		@since: Testlink 1.9.6

		@param devkey: Testlink developer key
		@type devkey: str
		@param testplanid: The internal ID of the TestPlan
		@type testplanid: int
		@param platformname: The name of the platform to remove
		@type platformname: str
		@returns: Server response
		@rtype: dict/list/???
		"""
		return self._query("tl.remotePlatformFromTestPlan", \
					devKey = devkey, \
					testplanid = testplanid, \
					platformname = platformname )

	
	def assignRequirements(self, testcaseexternalid, projectid, requirements, devkey=None):
		"""Assigns specified Requirements to a specified TestCase
		@param devkey: Testlink developer key
		@type devkey: str
		@param testcaseexternalid: The external ID of the TestCase
		@type testcaseexternalid: int
		@param projectid: The internal ID of the TestProject
		@type projectid: int
		@param requirements: The requirements to assign
		@type requirements: list
		@returns: Server response
		@rtype: dict
		"""
		return self._query("tl.assignRequirements",                     \
					devKey             = devkey,             \
					testcaseexternalid = testcaseexternalid, \
					testprojectid      = projectid,          \
					requirements       = requirements )


	def getReqSpecCustomFieldDesignValue(self, reqspecid, testprojectid, fieldname, devkey=None):
		"""Returns the value of a specified CustomField for a specified Requirement Specification
		@since: Testlink 1.9.4

		@param devkey: Testlink developer key
		@type devkey: str
		@param reqspecid: The internal ID of the Requirement Specification
		@type reqspecid: int
		@param testprojectid: The internal ID of the TestProject
		@type testprojectid: int
		@param fieldname: The internal name of the CustomField
		@type fieldname: str
		@returns: Server response
		@rtype: list/dict/???
		"""
		return self._query("tl.getReqSpecCustomFieldDesignValue", \
					devKey = devkey, \
					customfieldname = fieldname, \
					testprojectid = testprojectid, \
					reqspecid = reqspecid )


	def getRequirementCustomFieldDesignValue(self, requirementid, testprojectid, fieldname, devkey=None):
		"""Returns the value of a specified CustomField for a specified Requirement
		@since: Testlink 1.9.4

		@param devkey: Testlink developer key
		@type devkey: str
		@param requirementid: The internal ID of the Requirement
		@type requirementid: int
		@param testprojectid: The internal ID of the TestProject
		@type testprojectid: int
		@param fieldname: The internal name of the CustomField
		@type fieldname: str
		@returns: Server response
		@rtype: list/dict/???
		"""
		return self._query("tl.getRequirementCustomFieldDesignValue", \
					devKey = devkey, \
					customfieldname = fieldname, \
					testprojectid = testprojectid, \
					requirementid = requirementid )


	def getTestSuiteCustomFieldDesignValue(self, testsuiteid, testprojectid, fieldname, devkey=None):
		"""Returns the value of a specified CustomField for a specified TestSuite
		@since: Testlink 1.9.4

		@param devkey: Testlink developer key
		@type devkey: str
		@param testsuiteid: The internal ID of the TestSuite
		@type testsuiteid: int
		@param testprojectid: The internal ID of the TestProject
		@type testprojectid: int
		@param fieldname: The internal name of the CustomField
		@type fieldname: str
		@returns: Server response
		@rtype: list/dict/???
		"""
		return self._query("tl.getTestSuiteCustomFieldDesignValue", \
					devKey = devkey, \
					customfieldname = fieldname, \
					testprojectid = testprojectid, \
					testsuiteid = testsuiteid )
	
	
	def getTestCaseCustomFieldDesignValue(self, testcaseexternalid, version, projectid, fieldname, details='value', devkey=None):
		"""Returns the value of a specified CustomField for a specified TestCase
		@param devkey: Testlink developer key
		@type devkey: str
		@param testcaseexternalid: The external ID of the TestCase
		@type testcaseexternalid: int
		@param version: The version of the TestCase
		@type version: int
		@param projectid: The internal ID of the TestProject
		@type projectid: int
		@param fieldname: The internal name of the CustomField
		@type fieldname: str
		@param details: <OPTIONAL> Sets the detail level of the result (Default is: 'value')
		@type details: str
		@returns: Single value, information about specified field, information about all fields
		@rtype: mixed
		"""
		return self._query("tl.getTestCaseCustomFieldDesignValue",      \
					devKey             = devkey,             \
					testcaseexternalid = testcaseexternalid, \
					version            = version,            \
					testprojectid      = projectid,          \
					customfieldname    = fieldname,          \
					details            = details )


	def updateTestCaseCustomFieldDesignValue(self, testcaseexternalid, version, testprojectid, customfields=None, devkey=None):
		"""Updates values of CustomFields for a specified TestCase
		@since: Testlink 1.9.4

		@param devkey: Testlink developer key
		@type devkey: str
		@param testcaseexternalid: The external ID of the TestCase
		@type testcaseexternalid: int
		@param version: The version of the TestCase
		@type version: int
		@param testprojectid: The internal ID of the TestProject
		@type testprojectid: int
		@param customfields: <OPTIONAL> Dictionary containing values using CustomField names as keys
		@type customfields: dict
		@returns: Server response
		@rtype: list/dict/???
		"""
		return self._query("tl.updateTestCaseCustomFieldDesignValue", \
					devKey = devkey, \
					testcaseexternalid = testcaseexternalid, \
					version = version, \
					testprojectid = testprojectid, \
					customfields = customfields )


	def getTestCaseCustomFieldExecutionValue(self, executionid, testplanid, version, projectid, fieldname, devkey=None):
		"""Returns the value of a specified CustomField for a specified Execution
		@since: Testlink 1.9.4

		@param devkey: Testlink developer key
		@type devkey: str
		@param executionid: The internal ID of the execution
		@type executionid: int
		@param testplanid: The internal ID of the TestPlan
		@type testplanid: int
		@param version: The version of the TestCase
		@type version: int
		@param projectid: The internal ID of the TestProject
		@type projectid: int
		@param fieldname: The inernal name of the CustomField
		@type fieldname: str
		@returns: Server response
		@rtype: list/dict/???
		"""
		return self._query("tl.getTestCaseCustomFieldExecutionValue", \
					devKey = devkey, \
					customfieldname = fieldname, \
					testprojectid = projectid, \
					version = version, \
					executionid = executionid, \
					testplanid = testplanid )

	def getTestCaseCustomFieldTestPlanDesignValue(self, linkid, testplanid, version, testcaseid, fieldname, devkey=None):
		"""Returns the value of the specified CustomField for a specified TestCase within a specified TestPlan
		@since: Testlink 1.9.4

		@param devkey: Testlink developer key
		@type devkey: str
		@param linkid: The internal ID of the link?
		@type linkid: int
		@param testplanid: The internal ID of the TestPlan
		@type testplanid: int
		@param version; The version of the testcase
		@type version: int
		@param testcaseid: The internal ID of the TestCase
		@type testcaseid: int
		@param fieldname: The internal name of the CustomField
		@type fieldname: str
		@returns: Server response
		@rtype: list/dict/???
		"""
		return self._query("tl.getTestCaseCustomFieldTestPlanDesignValue", \
					devKey = devkey, \
					customfieldname = fieldname, \
					testcaseid = testcaseid, \
					version = version, \
					testplanid = testplanid, \
					linkid = linkid )
	

	def uploadAttachment(self, objectid, objecttable, name, mime, content, title=None, description=None, devkey=None):
		"""Uploads the specified Attachment for the specified object
		@param devkey: Testlink developer key
		@type devkey: str
		@param objectid: The internal ID of the attached object
		@type objectid: int
		@param objecttable: The table of the attached object
		@type objecttable: str
		@param name: The file name of the Attachment
		@type name: str
		@param mime: The MIME-Type of the Attachment
		@type mime: str
		@param content: Base64 encoded dump of Attachment
		@type content: str
		@param title: <OPTIONAL> Title for the Attachment
		@type title: str
		@param description: <OPTIONAL> Additional description for the Attachment
		@type description: str
		@returns: Server response
		@rtype: dict
		"""
		return self._query("tl.uploadAttachment",         \
					devKey      = devkey,      \
					fkid        = objectid,    \
					fktable     = objecttable, \
					filename    = name,        \
					filetype    = mime,        \
					content     = content,     \
					title       = title,       \
					description = description )
	
	
	def uploadRequirementSpecificationAttachment(self, reqspecid, name, mime, content, title=None, description=None, devkey=None):
		"""Uploads the specified Attachment for the specified Requirement Specification
		@param devkey: Testlink developer key
		@type devkey: str
		@param reqspecid: The internal ID of the Requirement Specification
		@type reqspecid: int
		@param name: The file name of the Attachment
		@type name: str
		@param mime: The MIME-Type of the Attachment
		@type mime: str
		@param content: Base64 encoded dump of Attachment
		@type content: str
		@param title: <OPTIONAL> Title for the Attachment
		@type title: str
		@param description: <OPTIONAL> Additional description for the Attachment
		@type description: str
		@returns: Server response
		@rtype: dict
		"""
		return self._query("tl.uploadRequirementSpecificationAttachment", \
					devKey      = devkey,                      \
					reqspecid   = reqspecid,                   \
					filename    = name,                        \
					filetype    = mime,                        \
					content     = content,                     \
					title       = title,                       \
					description = description )
	
	
	def uploadRequirementAttachment(self, reqid, name, mime, content, title=None, description=None, devkey=None):
		"""Uploads the specified Attachment for the specified Requirement
		@param devkey: Testlink developer key
		@type devkey: str
		@param reqid: The internal ID of the Requirement
		@type reqid: int
		@param name: The file name of the Attachment
		@type name: str
		@param mime: The MIME-Type of the Attachment
		@type mime: str
		@param content: Base64 encoded dump of Attachment
		@type content: str
		@param title: <OPTIONAL> Title for the Attachment
		@type title: str
		@param description: <OPTIONAL> Additional description for the Attachment
		@type description: str
		@returns: Server response
		@rtype: dict
		"""
		return self._query("tl.uploadRequirementAttachment", \
					devKey         = devkey,      \
					requirementsid = reqid,       \
					filename       = name,        \
					filetype       = mime,        \
					content        = content,     \
					title          = title,       \
					description    = description )
	
	
	def uploadTestProjectAttachment(self, projectid, name, mime, content, title=None, description=None, devkey=None):
		"""Uploads the specified Attachment for the specified TestProject
		@param devkey: Testlink developer key
		@type devkey: str
		@param projectid: The internal ID of the TestProject
		@type projectid: int
		@param name: The file name of the Attachment
		@type name: str
		@param mime: The MIME-Type of the Attachment
		@type mime: str
		@param content: Base64 encoded dump of Attachment
		@type content: str
		@param title: <OPTIONAL> Title for the Attachment
		@type title: str
		@param description: <OPTIONAL> Additional description for the Attachment
		@type description: str
		@returns: Server response
		@rtype: dict
		"""
		return self._query("tl.uploadTestProjectAttachment", \
					devKey        = devkey,       \
					testprojectid = projectid,    \
					filename      = name,         \
					filetype      = mime,         \
					content       = content,      \
					title         = title,        \
					description   = description )
	
	
	def uploadTestSuiteAttachment(self, suiteid, name, mime, content, title=None, description=None, devkey=None):
		"""Uploads the specified Attachment for the specified TestSuite
		@param devkey: Testlink developer key
		@type devkey: str
		@param suiteid: The internal ID of the TestSuite
		@type suiteid: int
		@param name: The file name of the Attachment
		@type name: str
		@param mime: The MIME-Type of the Attachment
		@type mime: str
		@param content: Base64 encoded dump of Attachment
		@type content: str
		@param title: <OPTIONAL> Title for the Attachment
		@type title: str
		@param description: <OPTIONAL> Additional description for the Attachment
		@type description: str
		@returns: Server response
		@rtype: dict
		"""
		return self._query("tl.uploadTestSuiteAttachment", \
					devKey      = devkey,       \
					testsuiteid = suiteid,      \
					filename    = name,         \
					filetype    = mime,         \
					content     = content,      \
					title       = title,        \
					description = description )
	
	
	def uploadTestCaseAttachment(self, testcaseid, name, mime, content, title=None, description=None, devkey=None):
		"""Uploads the specified Attachment for the specified TestCase
		@param devkey: Testlink developer key
		@type devkey: str
		@param testcaseid: The internal ID of the TestCase
		@type testcaseid: int
		@param name: The file name of the Attachment
		@type name: str
		@param mime: The MIME-Type of the Attachment
		@type mime: str
		@param content: Base64 encoded dump of Attachment
		@type content: str
		@param title: <OPTIONAL> Title for the Attachment
		@type title: str
		@param description: <OPTIONAL> Additional description for the Attachment
		@type description: str
		@returns: Server response
		@rtype: dict
		"""
		return self._query("tl.uploadTestCaseAttachment", \
					devKey      = devkey,      \
					testcaseid  = testcaseid,  \
					filename    = name,        \
					filetype    = mime,        \
					content     = content,     \
					title       = title,       \
					description = description )
	
	
	def uploadExecutionAttachment(self, executionid, name, mime, content, title=None, description=None, devkey=None):
		"""Uploads the specified Attachment for the specified Execution
		@param devkey: Testlink developer key
		@type devkey: str
		@param executionid: The internal ID of the Execution
		@type executionid: int
		@param name: The file name of the Attachment
		@type name: str
		@param mime: The MIME-Type of the Attachment
		@type mime: str
		@param content: Base64 encoded dump of Attachment
		@type content: str
		@param title: <OPTIONAL> Title for the Attachment
		@type title: str
		@param description: <OPTIONAL> Additional description for the Attachment
		@type description: str
		@returns: Server response
		@rtype: dict
		"""
		return self._query("tl.uploadExecutionAttachment", \
					devKey      = devkey,       \
					executionid = executionid,  \
					filename    = name,         \
					filetype    = mime,         \
					content     = content,      \
					title       = title,        \
					description = description )
	
	
	def getTestCaseAttachments(self, testcaseid=None, testcaseexternalid=None, devkey=None):
		"""Returns all available Attachments for the specified TestCase
		@param devkey: Testlink developer key
		@type devkey: str
		@param testcaseid: <OPTIONAL> The internal ID of the TestCase. If not given, external ID must be set
		@type testcaseid: int
		@param testcaseexternalid: <OPTIONAL> The external ID of the TestCase. If not given, the internal ID must be set
		@type testcaseexternalid: int
		@returns: Matching attachments
		@rtype: dict
		"""
		return self._query("tl.getTestCaseAttachments",          \
					devKey             = devkey,     \
					testcaseid         = testcaseid, \
					testcaseexternalid = testcaseexternalid )
