#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@author: Kai Borowiak
@summary: Raw API Wrapper for Testlink
"""

# IMPORTS
import socket
import xmlrpclib
from log import log

from exceptions import NotSupported
from exceptions import APIError
from exceptions import ConnectionError

from enums import ExecutionType
from enums import ImportanceLevel
from enums import DuplicateStrategy
from enums import RequirementSpecificationType
from enums import RequirementStatus
from enums import RequirementType

from distutils.version import LooseVersion as Version
from urlparse import urlparse

class TLVersion(object):
	"""Function decorator for Testlink version requirements.
	@raises NotSupported: Called method is not supported by current Testlink API
	"""
	IGNORE = False
	def __init__(self,version,strict=False):
		self.version = Version(version)
		self.strict = strict

	def __call__(self,fn):
		def _wrapped(parent,*args,**kwargs):
			# Check version
			if not TLVersion.IGNORE and (\
				(self.strict and self.version != parent._tl_version) or
				(self.version > parent._tl_version)\
			):
				if self.strict:
					sign = "=="
				else:
					sign = ">="
				raise NotSupported("Method '%s' requires Testlink version %s %s but is %s" % (str(fn.__name__),str(sign),str(self.version),str(parent._tl_version)))
			return fn(parent,*args,**kwargs)
		_wrapped.__name__ = fn.__name__
		_wrapped.__doc__ = fn.__doc__
		_wrapped.__dict__.update(fn.__dict__)
		return _wrapped


class Testlink_XML_RPC_API(object):
	"""Testlink XML-RPC API
	@cvar RPC_PATHS: Paths to Testlink's XML-RPC endpoint
	@type RPC_PATHS: list
	@cvar: MAX_RECONNECTION_TRIES: Maximum amount of reconnection tries
	@type MAX_RECONNECTION_TRIES: int
	@ivar _proxy: Used ServerProxy instance
	@type _proxy: xmlrpclib.ServerProxy
	@ivar _devkey: Used Developer Key
	@type _devkey: str
	"""

	RPC_PATHS = ["/lib/api/xmlrpc.php","/lib/api/xmlrpc/v1/xmlrpc.php"]
	MAX_RECONNECTION_TRIES = 10

	def __init__(self,url):
		"""Initialize the TestlinkAPI
		@param url: Testlink URL
		@type url: str
		@raises ConnectionError: The given URL is not valid
		"""
		self._proxy = None
		self._devkey = None
		self._tl_version = Version("1.0")
		self._max_connection_tries = self.MAX_RECONNECTION_TRIES

		# Patch URL
		if (url.endswith('/')):
			url = url[:-1]

		# Check if URL is correct and save it for further use
		url_components = urlparse(url)
		if (\
			# Must have scheme and net location
			len(url_components[0].strip())==0 or \
			len(url_components[1].strip())==0 \
		):
			raise ConnectionError("Invalid URI (%s)" % str(url))
		else:
			self._url = url

		# Establish connection
		self._reconnect()

		try:
			# Get the version
			# Wihtout wrapping function to avoid version check
			# before acutally having the version
			self._tl_version = Version(str(self._query("tl.testLinkVersion")))
		except NotSupported,ne:
			# Testlink API has version 1.0
			return
		except AttributeError,ae:
			# Mocked _query during tests
			return

	def _reconnect(self):
		"""Reconnects to initially specified URL"""
		# Check for each possible RPC path,
		# if a connection can be made
		last_excpt = None
		for path in self.RPC_PATHS:
			tmp = self._url
			try:
				if not tmp.endswith(path):
					tmp += path
				self._proxy = xmlrpclib.ServerProxy(tmp,encoding='UTF-8',allow_none=True)
				self._proxy.system.listMethods()
				break
			except Exception,ex:
				last_excpt = ex
				self._proxy = None
				continue
		if self._proxy is None:
			raise ConnectionError("Cannot connect to Testlink API @ %s (%s)" % (str(self._url),str(last_excpt)))

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
			# If method is not supported, raise NotSupported
			# Otherwise re-raise original error
			if (f.faultCode == NotSupported.errorCode):
				raise NotSupported(method)
			else:
				raise
		except socket.error, se:
			# Connection is gone, try to reestablish
			log.debug("Connection Error: %s" + str(se))
			if self._max_connection_tries > 0:
				self._reconnect()
				self._max_connection_tries -= 1
				return self._query(method,**kwargs)
			else:
				raise
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
	@TLVersion("1.9.9")
	def testLinkVersion(self):
		"""Returns Testlink Version String
		@since: Testlink 1.9.9

		@returns: Version String
		@rtype: str
		"""
		return self._query("tl.testLinkVersion")

	@TLVersion("1.0")
	def about(self):
		"""Returns informations about the current Testlink API
		@returns: 'Testlink API Version: x.x initially written by Asial Brumfield with contributions by Testlink development Team'
		@rtype: str
		"""
		return self._query("tl.about")


	@TLVersion("1.0")
	def sayHello(self):
		"""Returns the string 'Hello!'
		@returns: 'Hello!'
		@rtype: str
		"""
		return self._query("tl.sayHello")
	ping = sayHello

	@TLVersion("1.0")
	def repeat(self,value):
		"""Repeats the given value
		@param value: The value to be repeated by the server
		@type value: mixed
		@returns: String 'You said: ' and the given value
		@rtype: mixed
		"""
		return self._query("tl.repeat", str=str(value))

	@TLVersion("1.0")
	def checkDevKey(self,devkey=None):
		"""Checks if the specified developer key is valid
		@param devkey: The developer key to be tested
		@type devkey: str
		@returns: True/False
		@rtype: bool
		"""
		return self._query("tl.checkDevKey", devKey=devkey)

	@TLVersion("1.0")
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

	@TLVersion("1.9.8")
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

	@TLVersion("1.9.8")
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

	@TLVersion("1.0")
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

	@TLVersion("1.0")
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

	@TLVersion("1.0")
	def getProjects(self, devkey=None):
		"""Returns all available TestProjects
		@param devkey: Testlink developer key
		@type devkey: str
		@returns: TestProjects as list of dicts
		@rtype: list
		"""
		return self._query("tl.getProjects", devKey=devkey)

	@TLVersion("1.0")
	def getTestProjectByName(self, name, devkey=None):
		"""Returns a single TestProject specified by its name
		@param devkey: Testlink developer key
		@type devkey: str
		@param name: Name of the TestProject
		@type name: str
		@returns: Matching TestProject, None if none was found
		@rtype: mixed
		"""
		resp = self._query("tl.getTestProjectByName", devKey=devkey, testprojectname=name)
		# Return None for an empty string
		if resp is not None and len(resp)==0:
			resp = None
		return resp

	@TLVersion("1.0")
	def createTestPlan(self, name, project, notes='', active=True, public=True, devkey=None):
		"""Creates a new TestPlan
		@param devkey: Testlink developer key
		@type devkey: str
		@param name: Name of the TestPlan
		@type name: str
		@param project: Name of the parent TestProject
		@type project: str
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
					testprojectname = project,\
					notes           = notes,      \
					active          = active,     \
					public          = public )

	@TLVersion("1.0")
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

	@TLVersion("1.0")
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

	@TLVersion("1.9.4")
	def getTestPlanCustomFieldValue(self, testplanid, testprojectid, fieldname, devkey=None):
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

	@TLVersion("1.0")
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

	@TLVersion("1.0")
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
	
	@TLVersion("1.0")
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

	@TLVersion("1.9.4")
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

	@TLVersion("1.9.6")
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

	@TLVersion("1.9.6")
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
	
	@TLVersion("1.0")
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
	
	@TLVersion("1.0")
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

	@TLVersion("1.0")
	def getLastExecutionResult(self, testplanid, testcaseid=None, testcaseexternalid=None, platformid=None, platformname=None, buildid=None, buildname=None, bugs=False, devkey=None):
		"""Returns the execution result for a specified TestCase and TestPlan
		@param devkey: Testlink developer key
		@type devkey: str
		@param testplanid: The internal ID of the TestPlan
		@type testplanid: int
		@param testcaseid: <OPTIONAL> The internal ID of the TestCase. If not given, the external ID must be set
		@type testcaseid: int
		@param testcaseexternalid: <OPTIONAL> The external ID of the TestCase. If not given, the internal ID must be set
		@type testcaseexternalid: int
		@param platformid: <OPTIONAL> The internal ID of the platform (Since Testlink 1.9.9)
		@type platformid: int
		@param platformname: <OPTIONAL> The name of the platform (Since Testlink 1.9.9)
		@type platformname: str
		@param buildid: <OPTIONAL> The internal ID of the build (Since Testlink 1.9.9)
		@type buildid: int
		@param buildname: <OPTIONAL> The name of the build (Since Testlink 1.9.9)
		@type buildname: str
		@param bugs: <OPTIONAL> Also get related bugs (Since Testlink 1.9.9)
		@type bugs: bool
		@returns: Matching result
		@rtype: dict
		"""
		arguments = {
				"devKey"             : devkey,     \
				"testplanid"         : testplanid, \
				"testcaseid"         : testcaseid, \
				"testcaseexternalid" : testcaseexternalid\
			}

		if (self._tl_version >= Version("1.9.9")) or TLVersion.IGNORE:
			arguments['platformid'] = platformid
			arguments['platformname'] = platformname
			arguments['buildid'] = buildid
			arguments['buildname'] = buildname
			arguments['options'] = {'getBugs':bugs}

		return self._query("tl.getLastExecutionResult",**arguments)

	@TLVersion("1.0")
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
	
	@TLVersion("1.0")
	def createTestSuite(self, testsuitename, testprojectid, details=None, parentid=None, order=None, checkduplicatedname=True, actiononduplicatedname=DuplicateStrategy.BLOCK, devkey=None):
		"""Creates a new TestSuite
		@param devkey: Testlink developer key
		@type devkey: str
		@param testsuitename: The name of the TestSuite
		@type testsuitename: str
		@param testprojectid: The internal ID of the parent TestProject
		@type testprojectid: int
		@param details: <OPTIONAL> Additional notes for the TestSuite
		@type details: str
		@param parentid: <OPTIONAL> The internal ID of the parent TestSuite
		@type parentid: int
		@param order: <OPTIONAL> Ordering withing the parent TestSuite
		@type order: int
		@param checkduplicatedname: <OPTIONAL> Enables duplicate handling (Default is: True)
		@type checkduplicatedname: bool
		@param actiononduplicatedname: <OPTIONAL> Action on duplicate
		@param actiononduplicatedname: str
		@returns: Server response
		@rtype: dict
		"""
		return self._query("tl.createTestSuite",                         \
					devKey                 = devkey,          \
					testsuitename          = testsuitename,   \
					testprojectid          = testprojectid,   \
					details                = details,         \
					parentid               = parentid,        \
					order                  = order,           \
					checkduplicatedname    = checkduplicatedname, \
					actiononduplicatedname = actiononduplicatedname )
	
	@TLVersion("1.0")
	def getTestSuiteById(self, testsuiteid, devkey=None):
		"""Returns a single TestSuite specified by the internal ID
		@param devkey: Testlink developer key
		@type devkey: str
		@param testsuiteid: The internal ID of the TestSuite
		@type testsuiteid: int
		@returns: Matching TestSuite
		@rtype: dict
		"""
		return self._query("tl.getTestSuiteByID",    \
					devKey      = devkey, \
					testsuiteid = testsuiteid )
	
	@TLVersion("1.0")
	def getTestSuitesForTestSuite(self, testsuiteid, devkey=None):
		"""Returns all TestSuites within the specified TestSuite
		@param devkey: Testlink developer key
		@type devkey: str
		@param testsuiteid: The internal ID of the TestSuite
		@type testsuiteid: int
		@returns: Matching TestSuites
		@rtype: dict/list/???
		"""
		return self._query("tl.getTestSuitesForTestSuite", \
					devKey      = devkey,       \
					testsuiteid = testsuiteid )
	
	@TLVersion("1.0")
	def getFirstLevelTestSuitesForTestProject(self, testprojectid, devkey=None):
		"""Returns the first level TestSuites for a specified TestProject
		@param devkey: Testlink developer key
		@type devkey: str
		@param testprojectid: The internal ID of the TestProject
		@type testprojectid: int
		@returns: Matching TestSuites
		@rtype: dict/list/???
		"""
		return self._query("tl.getFirstLevelTestSuitesForTestProject", \
					devKey        = devkey,                 \
					testprojectid = testprojectid )
	
	@TLVersion("1.0")
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
	
	@TLVersion("1.0")
	def createTestCase(self, testcasename, testsuiteid, testprojectid, authorlogin, summary, steps=[], preconditions=None, importance=ImportanceLevel.MEDIUM, executiontype=ExecutionType.MANUAL, order=None, checkduplicatedname=True, actiononduplicatedname=DuplicateStrategy.BLOCK,customfields={},devkey=None):
		"""Creates a new TestCase
		@param devkey: Testlink developer key
		@type devkey: str
		@param testcasename: TestCase title
		@type testcasename: str
		@param testsuiteid: The internal ID of the parent TestSuite
		@type testsuiteid: int
		@param testprojectid: The internal ID of the parent TestProject
		@type testprojectid: int
		@param authorlogin: The author of the TestCase
		@type authorlogin: str
		@param summary: The summary of the TestCase
		@type summary: str
		@param steps: <OPTIONAL> Steps of the TestCase
		@type steps: list
		@param preconditions: <OPTIONAL> Preconditions of the TestCase
		@type preconditions: str
		@param importance: <OPTIONAL> The importance of the TestCase (Default is: 'LOW')
		@type importance: int
		@param executiontype: <OPTIONAL> The execution mode of the TestCase (Default is: 'MANUAL')
		@type executiontype: int
		@param order: <OPTIONAL> The order of the TestCase within the TestSuite
		@type order: int
		@param checkduplicatedname: <OPTIONAL> Enables duplicate handling (Default is: True)
		@type checkduplicatedname: bool
		@param actiononduplicatedname: <OPTIONAL> Action on duplicate (Default is: 'block')
		@type actiononduplicatedname: str
		@param customfields: <OPTIONAL> CustomFields for the TestCase
		@type customfields: dict
		@returns: Server response
		@rtype: dict/list/???
		"""
		return self._query("tl.createTestCase",                          \
					devKey                 = devkey,          \
					testcasename           = testcasename,    \
					testsuiteid            = testsuiteid,     \
					testprojectid          = testprojectid,   \
					authorlogin            = authorlogin,     \
					summary                = summary,         \
					steps                  = steps,           \
					preconditions          = preconditions,   \
					importance             = importance,      \
					executiontype          = executiontype,   \
					order                  = order,           \
					customfields           = customfields,    \
					checkduplicatedname    = checkduplicatedname, \
					actiononduplicatedname = actiononduplicatedname\
				)

	@TLVersion("1.9.8")
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
		@type estimatedexecduration: int
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

	@TLVersion("1.9.4")
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
	
	@TLVersion("1.9.4")
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

	@TLVersion("1.9.4")
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

	@TLVersion("1.0")
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
	
	@TLVersion("1.0")
	def getTestCaseIdByName(self, testcasename, testsuitename=None, testprojectname=None, testcasepathname=None, devkey=None):
		"""Returns the internal ID of a specified TestCase
		@param devkey: Testlink developer key
		@type devkey: str
		@param testcasename: Title of the TestCase
		@type testcasename: str
		@param testsuitename: <OPTIONAL> Name of the parent TestSuite
		@type testsuitename: str
		@param testprojectname: <OPTIONAL> Name of the paren TestProject
		@type testprojectname: str
		@param testcasepathname: <OPTIONAL> Hierarchical path of the TestCase
		@type testcasepathname: str
		@returns: Matching TestCase ID
		@rtype: int?
		"""
		return self._query("tl.getTestCaseIDByName",       \
					devKey           = devkey,          \
					testcasename     = testcasename,    \
					testsuitename    = testsuitename,   \
					testprojectname  = testprojectname, \
					testcasepathname = testcasepathname )
	
	@TLVersion("1.0")
	def getTestCasesForTestSuite(self, testsuiteid, deep=False, details='simple', getkeywords=False, devkey=None):
		"""Returns all TestCases for a specified TestSuite
		@param devkey: Testlink developer key
		@type devkey: str
		@param testsuiteid: The internal ID of the TestSuite
		@type testsuiteid: int
		@param deep: <OPTIONAL> Recursively returns TestCases from TestSuite (Default is: False)
		@type deep: bool
		@param details: <OPTIONAL> Toggle detailed output (Defailt is: 'simple')
		@type details: str
		@param getkeywords: <OPTIONAL> Also get keywords for testcases (Default is: False) (Since Testlink 1.9.10)
		@type getkeywords: bool
		@returns: Matching TestCases
		@rtype: list/dict/???
		"""
		arguments = {
					"devKey"      : devkey,      \
					"testsuiteid" : testsuiteid, \
					"deep"        : deep,        \
					"details"     : details      \
			}
		if (self._tl_version >= Version("1.9.10")) or TLVersion.IGNORE:
			arguments['getkeywords'] = getkeywords
		return self._query("tl.getTestCasesForTestSuite", **arguments)
	
	@TLVersion("1.0")
	def getTestCasesForTestPlan(self, testplanid, testcaseid=None, buildid=None, keywordid=None, keywords=None, executed=None, assignedto=None, executestatus=None, executiontype=None, getstepsinfo=False, details='full', devkey=None):
		"""Returns all TestCases for a specified TestPlan
		@param devkey: Testlink developer key
		@type devkey: str
		@param testplanid: The internal ID of the TestPlan
		@type testplanid: int
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
		@param executestatus: <OPTIONAL> The execution status
		@type executestatus: int
		@param executiontype: <OPTIONAL> The execution type
		@type executiontype: int
		@param getstepsinfo: <OPTIONAL> Toggles if steps are returned
		@type getstepsinfo: bool
		@param details: <OPTIONAL> Set detail amount (Since Testlink 1.9.4)
		@type details: str
		@returns: Matching TestCases
		@rtype: list/dict/???
		"""
		arguments = {
				"devKey"        : devkey,          \
				"testplanid"    : testplanid,      \
				"testcaseid"    : testcaseid,      \
				"buildid"       : buildid,         \
				"keywordid"     : keywordid,       \
				"keywords"      : keywords,        \
				"executed"      : executed,        \
				"assignedto"    : assignedto,      \
				"executestatus" : executestatus, \
				"executiontype" : executiontype,   \
				"getstepsinfo"  : getstepsinfo      \
			}

		if (self._tl_version >= Version("1.9.4")) or TLVersion.IGNORE:
			# Add 'details' attribute
			arguments['details'] = details

		return self._query("tl.getTestCasesForTestPlan", **arguments)
	
	@TLVersion("1.0")
	def addTestCaseToTestPlan(self, testprojectid, testplanid, testcaseexternalid, version, platformid=None, executionorder=None, urgency=None, devkey=None):
		"""Adds a specified TestCase to a specified TestPlan
		@param devkey: Testlink developer key
		@type devkey: str
		@param testprojectid: The internal ID of the TestProject
		@type testprojectid: int
		@param testplanid: The internal ID of the TestPlan
		@type testplanid: int
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
					testprojectid      = testprojectid,      \
					testplanid         = testplanid,         \
					testcaseexternalid = testcaseexternalid, \
					version            = version,            \
					platformid         = platformid,         \
					executionorder     = executionorder,     \
					urgency            = urgency )

	@TLVersion("1.9.6")
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

	@TLVersion("1.9.6")
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
		return self._query("tl.removePlatformFromTestPlan", \
					devKey = devkey, \
					testplanid = testplanid, \
					platformname = platformname )

	@TLVersion("1.0")
	def assignRequirements(self, testcaseexternalid, testprojectid, requirements, devkey=None):
		"""Assigns specified Requirements to a specified TestCase
		@param devkey: Testlink developer key
		@type devkey: str
		@param testcaseexternalid: The external ID of the TestCase
		@type testcaseexternalid: int
		@param testprojectid: The internal ID of the TestProject
		@type testprojectid: int
		@param requirements: The requirements to assign
		@type requirements: list
		@returns: Server response
		@rtype: dict
		"""
		return self._query("tl.assignRequirements",                     \
					devKey             = devkey,             \
					testcaseexternalid = testcaseexternalid, \
					testprojectid      = testprojectid,      \
					requirements       = requirements )

	@TLVersion("1.9.4")
	def getReqSpecCustomFieldDesignValue(self, reqspecid, testprojectid, customfieldname, devkey=None):
		"""Returns the value of a specified CustomField for a specified Requirement Specification
		@since: Testlink 1.9.4

		@param devkey: Testlink developer key
		@type devkey: str
		@param reqspecid: The internal ID of the Requirement Specification
		@type reqspecid: int
		@param testprojectid: The internal ID of the TestProject
		@type testprojectid: int
		@param customfieldname: The internal name of the CustomField
		@type customfieldname: str
		@returns: Server response
		@rtype: list/dict/???
		"""
		return self._query("tl.getReqSpecCustomFieldDesignValue", \
					devKey = devkey, \
					customfieldname = customfieldname, \
					testprojectid = testprojectid, \
					reqspecid = reqspecid )

	@TLVersion("1.9.4")
	def getRequirementCustomFieldDesignValue(self, requirementid, testprojectid, customfieldname, devkey=None):
		"""Returns the value of a specified CustomField for a specified Requirement
		@since: Testlink 1.9.4

		@param devkey: Testlink developer key
		@type devkey: str
		@param requirementid: The internal ID of the Requirement
		@type requirementid: int
		@param testprojectid: The internal ID of the TestProject
		@type testprojectid: int
		@param customfieldname: The internal name of the CustomField
		@type customfieldname: str
		@returns: Server response
		@rtype: list/dict/???
		"""
		return self._query("tl.getRequirementCustomFieldDesignValue", \
					devKey = devkey, \
					customfieldname = customfieldname, \
					testprojectid = testprojectid, \
					requirementid = requirementid )

	@TLVersion("1.9.4")
	def getTestSuiteCustomFieldDesignValue(self, testsuiteid, testprojectid, customfieldname, devkey=None):
		"""Returns the value of a specified CustomField for a specified TestSuite
		@since: Testlink 1.9.4

		@param devkey: Testlink developer key
		@type devkey: str
		@param testsuiteid: The internal ID of the TestSuite
		@type testsuiteid: int
		@param testprojectid: The internal ID of the TestProject
		@type testprojectid: int
		@param customfieldname: The internal name of the CustomField
		@type customfieldname: str
		@returns: Server response
		@rtype: list/dict/???
		"""
		return self._query("tl.getTestSuiteCustomFieldDesignValue", \
					devKey = devkey, \
					customfieldname = customfieldname, \
					testprojectid = testprojectid, \
					testsuiteid = testsuiteid )
	
	@TLVersion("1.0")
	def getTestCaseCustomFieldDesignValue(self, testcaseexternalid, version, testprojectid, customfieldname, details='value', devkey=None):
		"""Returns the value of a specified CustomField for a specified TestCase
		@param devkey: Testlink developer key
		@type devkey: str
		@param testcaseexternalid: The external ID of the TestCase
		@type testcaseexternalid: int
		@param version: The version of the TestCase
		@type version: int
		@param testprojectid: The internal ID of the TestProject
		@type testprojectid: int
		@param customfieldname: The internal name of the CustomField
		@type customfieldname: str
		@param details: <OPTIONAL> Sets the detail level of the result (Default is: 'value')
		@type details: str
		@returns: Single value, information about specified field, information about all fields
		@rtype: mixed
		"""
		resp =  self._query("tl.getTestCaseCustomFieldDesignValue",      \
					devKey             = devkey,             \
					testcaseexternalid = testcaseexternalid, \
					version            = version,            \
					testprojectid      = testprojectid,      \
					customfieldname    = customfieldname,    \
					details            = details )
		# Return None for an empty string
		if resp is not None and len(resp)==0:
			resp = None
		return resp

	@TLVersion("1.9.4")
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

	@TLVersion("1.9.4")
	def getTestCaseCustomFieldExecutionValue(self, executionid, testplanid, version, testprojectid, customfieldname, devkey=None):
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
		@param testprojectid: The internal ID of the TestProject
		@type testprojectid: int
		@param customfieldname: The inernal name of the CustomField
		@type customfieldname: str
		@returns: Server response
		@rtype: list/dict/???
		"""
		return self._query("tl.getTestCaseCustomFieldExecutionValue", \
					devKey = devkey,                   \
					customfieldname = customfieldname, \
					testprojectid = testprojectid,     \
					version = version,                 \
					executionid = executionid,         \
					testplanid = testplanid )

	@TLVersion("1.9.4")
	def getTestCaseCustomFieldTestPlanDesignValue(self, linkid, testplanid, version, testprojectid, customfieldname, devkey=None):
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
		@param testprojectid: The internal ID of the TestProject
		@type testprojectid: int
		@param customfieldname: The internal name of the CustomField
		@type customfieldname: str
		@returns: Server response
		@rtype: list/dict/???
		"""
		return self._query("tl.getTestCaseCustomFieldTestPlanDesignValue", \
					devKey = devkey,                   \
					customfieldname = customfieldname, \
					testprojectid = testprojectid,     \
					version = version,                 \
					testplanid = testplanid,           \
					linkid = linkid )
	
	@TLVersion("1.0")
	def uploadAttachment(self, fkid, fktable, filename, filetype, content, title=None, description=None, devkey=None):
		"""Uploads the specified Attachment for the specified object
		@param devkey: Testlink developer key
		@type devkey: str
		@param fkid: The internal ID of the attached object
		@type fkid: int
		@param fktable: The table of the attached object
		@type fktable: str
		@param filename: The file name of the Attachment
		@type filename: str
		@param filetype: The MIME-Type of the Attachment
		@type filetype: str
		@param content: Base64 encoded dump of Attachment
		@type content: str
		@param title: <OPTIONAL> Title for the Attachment
		@type title: str
		@param description: <OPTIONAL> Additional description for the Attachment
		@type description: str
		@returns: Server response
		@rtype: dict
		"""
		return self._query("tl.uploadAttachment",       \
					devKey      = devkey,   \
					fkid        = fkid,     \
					fktable     = fktable,  \
					filename    = filename, \
					filetype    = filetype, \
					content     = content,  \
					title       = title,    \
					description = description )
	
	@TLVersion("1.0")
	def uploadRequirementSpecificationAttachment(self, reqspecid, filename, filetype, content, title=None, description=None, devkey=None):
		"""Uploads the specified Attachment for the specified Requirement Specification
		@param devkey: Testlink developer key
		@type devkey: str
		@param reqspecid: The internal ID of the Requirement Specification
		@type reqspecid: int
		@param filename: The file name of the Attachment
		@type filename: str
		@param filetype: The MIME-Type of the Attachment
		@type filetype: str
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
					filename    = filename,                    \
					filetype    = filetype,                    \
					content     = content,                     \
					title       = title,                       \
					description = description )
	
	@TLVersion("1.0")
	def uploadRequirementAttachment(self, requirementid, filename, filetype, content, title=None, description=None, devkey=None):
		"""Uploads the specified Attachment for the specified Requirement
		@param devkey: Testlink developer key
		@type devkey: str
		@param requirementid: The internal ID of the Requirement
		@type requirementid: int
		@param filename: The file name of the Attachment
		@type filename: str
		@param filetype: The MIME-Type of the Attachment
		@type filetype: str
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
					devKey         = devkey,       \
					requirementid = requirementid, \
					filename       = filename,     \
					filetype       = filetype,     \
					content        = content,      \
					title          = title,        \
					description    = description )
	
	@TLVersion("1.0")
	def uploadTestProjectAttachment(self, testprojectid, filename, filetype, content, title=None, description=None, devkey=None):
		"""Uploads the specified Attachment for the specified TestProject
		@param devkey: Testlink developer key
		@type devkey: str
		@param testprojectid: The internal ID of the TestProject
		@type testprojectid: int
		@param filename: The file name of the Attachment
		@type filename: str
		@param filetype: The MIME-Type of the Attachment
		@type filetype: str
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
					devKey        = devkey,        \
					testprojectid = testprojectid, \
					filename      = filename,      \
					filetype      = filetype,      \
					content       = content,       \
					title         = title,         \
					description   = description )
	
	@TLVersion("1.0")
	def uploadTestSuiteAttachment(self, testsuiteid, filename, filetype, content, title=None, description=None, devkey=None):
		"""Uploads the specified Attachment for the specified TestSuite
		@param devkey: Testlink developer key
		@type devkey: str
		@param testsuiteid: The internal ID of the TestSuite
		@type testsuiteid: int
		@param filename: The file name of the Attachment
		@type filename: str
		@param filetype: The MIME-Type of the Attachment
		@type filetype: str
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
					devKey      = devkey,      \
					testsuiteid = testsuiteid, \
					filename    = filename,    \
					filetype    = filetype,    \
					content     = content,     \
					title       = title,       \
					description = description )
	
	@TLVersion("1.0")
	def uploadTestCaseAttachment(self, testcaseid, filename, filetype, content, title=None, description=None, devkey=None):
		"""Uploads the specified Attachment for the specified TestCase
		@param devkey: Testlink developer key
		@type devkey: str
		@param testcaseid: The internal ID of the TestCase
		@type testcaseid: int
		@param filename: The file name of the Attachment
		@type filename: str
		@param filetype: The MIME-Type of the Attachment
		@type filetype: str
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
					devKey      = devkey,     \
					testcaseid  = testcaseid, \
					filename    = filename,   \
					filetype    = filetype,   \
					content     = content,    \
					title       = title,      \
					description = description )
	
	@TLVersion("1.0")
	def uploadExecutionAttachment(self, executionid, filename, filetype, content, title=None, description=None, devkey=None):
		"""Uploads the specified Attachment for the specified Execution
		@param devkey: Testlink developer key
		@type devkey: str
		@param executionid: The internal ID of the Execution
		@type executionid: int
		@param filename: The file name of the Attachment
		@type filename: str
		@param filetype: The MIME-Type of the Attachment
		@type filetype: str
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
					devKey      = devkey,      \
					executionid = executionid, \
					filename    = filename,    \
					filetype    = filetype,    \
					content     = content,     \
					title       = title,       \
					description = description )
	
	@TLVersion("1.0")
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

	@TLVersion("1.11-sinaqs",strict=True)
	def getRequirementSpecificationsForTestProject(self, testprojectid, devkey=None):
		"""Returns all available Requirement Specifications for the specified TestProject
		@param devkey: Testlink developer key
		@type devkey: str
		@param testprojectid: The internal ID of the TestProject.
		@type testprojectid: int
		@returns: Matching requirement specifications
		@rtype: list
		"""
		return self._query("tl.getRequirementSpecificationsForTestProject", \
					devKey        = devkey, \
					testprojectid = testprojectid )

	@TLVersion("1.11-sinaqs",strict=True)
	def getRequirementsForRequirementSpecification(self, reqspecid, testprojectid, devkey=None):
		"""Returns all available Requirements for the specified Requirement Specification
		@param devkey: Testlink developer key
		@type devkey: str
		@þaram reqspecid: The internal ID of the Requirement Specification
		@type reqspecid: int
		@param testprojectid: The internal ID of the TestProject
		@type testprojectid: int
		@returns: Matching requirements
		@rtype: list
		"""
		return self._query("tl.getRequirementsForRequirementSpecification", \
					devKey        = devkey,    \
					reqspecid     = reqspecid, \
					testprojectid = testprojectid )

	@TLVersion("1.11-sinaqs",strict=True)
	def getRisksForRequirement(self, requirementid, devkey=None):
		"""Returns all avaialble Risks for the specified Requirement
		@param devkey: Testlink developer key
		@type devkey: str
		@param requirementid: The internal ID of the Requirement
		@type requirementid: int
		@returns: Matching risks
		@rtype: list
		"""
		return self._query("tl.getRisksForRequirement",\
					devKey        = devkey,\
					requirementid = requirementid )

	@TLVersion("1.11-sinaqs",strict=True)
	def createRequirementSpecification(self, testprojectid, parentid, docid, title, scope, userid, typ, devkey=None):
		"""Creates a new Requirement Specification
		@param devkey: Testlink developer key
		@type devkey: str
		@param testprojectid: The internal ID of the TestProject
		@type testprojectid: int
		@param parentid: The internal ID of the parent object
		@type parentid: int
		@param docid: The document ID of the new Requirement Specification
		@type docid: str
		@param title: The title of the new Requirement Specification
		@type title: str
		@param scope: The scope of the new Requirement Specification
		@type scope: str
		@param userid: The ID of the author
		@type userid: int
		@param typ: The type of the new Requirement Specification
		@type typ: RequirementSpecificationType
		@returns: Server response
		@rtype: dict
		"""
		return self._query("tl.createRequirementSpecification", \
					devKey        = devkey,         \
					testprojectid = testprojectid,  \
					parentid      = parentid,       \
					docid         = docid,          \
					title         = title,          \
					scope         = scope,          \
					userid        = userid,         \
					type          = typ )

	@TLVersion("1.11-sinaqs",strict=True)
	def createRequirement(self, testprojectid, reqspecid, docid, title, scope, userid, status, typ, coverage=1, devkey=None):
		"""Creates a new Requirement
		@param devkey: Testlink developer key
		@type devkey: str
		@param testprojectid: The internal ID of the TestProject
		@type testprojectid: int
		@param reqspecid: The internal ID of the parent Requirement Specification
		@type reqspecid: int
		@param docid: The document ID of the new Requirement
		@type docid: str
		@param title: The title pf the new Requirement
		@type title: str
		@param scope: The scope of the new Requirement
		@type scope: str
		@param userid: The ID of the author
		@type useid: int
		@param status: The status of the new Requirement
		@type status: RequirementStatus
		@param typ: The type of the new Requirement
		@type typ: RequirementType
		@param coverage: <OPTIONAL> Expected coverage of the new Requirement (Default: 1)
		@type coverage: int
		@returns: Server response
		@rtype: dict
		"""
		return self._query("tl.createRequirement",             \
					devKey        = devkey,        \
					testprojectid = testprojectid, \
					reqspecid     = reqspecid,     \
					docid         = docid,         \
					title         = title,         \
					scope         = scope,         \
					userid        = userid,        \
					status        = status,        \
					type          = typ,          \
					coverage      = coverage )

	@TLVersion("1.11-sinaqs",strict=True)
	def createRisk(self, requirementid, docid, title, scope, userid, coverage=None, devkey=None):
		"""Creates a new Risk
		@param devkey: Testlink developer key
		@type devkey: str
		@param requirementid: The internal ID of the parent Requirement
		@type requirementid: int
		@param docid: The document ID of the new Risk
		@type docid: str
		@param title: The title of the new Risk
		@type title: str
		@param scope: The scope of the new Risk
		@type scope: str
		@param userid: The ID of the author
		@type userid: int
		@param coverage: <OPTIONAL> Inter-project TestCase coverage (Default: None)
		@type coverage: str
		@returns: Server response
		@rtype: dict
		"""
		return self._query("tl.createRisk",                    \
					devKey        = devkey,        \
					requirementid = requirementid, \
					docid         = docid,         \
					title         = title,         \
					scope         = scope,         \
					userid        = userid,        \
					coverage      = coverage )

	@TLVersion("1.11-sinaqs",strict=True)
	def assignRisks(self, testcaseexternalid, testprojectid, risks, devkey=None):
		"""Assigns risks to a testcase.
		@param devkey: Testlink developer key
		@type devkey: str
		@param testcaseexternalid: The external ID of the Testcase (with prefix!)
		@type testcaseexternalid: str
		@param risks: List of Risk IDs to assign to the TestCase
		@type risks: list
		@returns: Server response
		@rtype: mixed
		"""
		return self._query("tl.assignRisks",                             \
					devKey             = devkey,             \
					testprojectid      = testprojectid,      \
					testcaseexternalid = testcaseexternalid, \
					risks              = risks )
