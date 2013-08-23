#!/usr/bin/env python

#               /                ______                __    ___                __
#         -+ydNMM....``         /\__  _\              /\ \__/\_ \    __        /\ \
#      `+mMMMMMMM........`      \/_/\ \/    __    ____\ \ ,_\//\ \  /\_\    ___\ \ \/'\
#     /mMMMMMMMMM..........`       \ \ \  /'__`\ /',__\\ \ \/ \ \ \ \/\ \ /' _ `\ \ , <
#    oMMMMMMMMMMM...........`       \ \ \/\  __//\__, `\\ \ \_ \_\ \_\ \ \/\ \/\ \ \ \ \`\
#   :MMMMMMMMMMMM............        \ \_\ \____\/\____/ \ \__\/\____\\ \_\ \_\ \_\ \_\ \_\
#   hMMMMMMMMMMMM............`        \/_/\/____/\/___/   \/__/\/____/ \/_/\/_/\/_/\/_/\/_/
# ..::::::::::::oMMMMMMMMMMMMo..   ______  ____    ______      __      __
#   ............+MMMMMMMMMMMM-    /\  _  \/\  _ `\/\__  _\    /\ \  __/\ \
#    ...........+MMMMMMMMMMMs     \ \ \_\ \ \ \_\ \/_/\ \/    \ \ \/\ \ \ \  _ __    __     _____   _____      __   _ __
#     ..........+MMMMMMMMMMy       \ \  __ \ \ ,__/  \ \ \     \ \ \ \ \ \ \/\`'__\/'__`\  /\ '__`\/\ '__`\  /'__`\/\`'__\
#      `........+MMMMMMMMm:         \ \ \/\ \ \ \/    \_\ \__   \ \ \_/ \_\ \ \ \//\ \_\.\_\ \ \_\ \ \ \_\ \/\  __/\ \ \/
#        `......+MMMMMNy:            \ \_\ \_\ \_\    /\_____\   \ `\___x___/\ \_\\ \__/.\_\\ \ ,__/\ \ ,__/\ \____\\ \_\
#            ```/ss+/.                \/_/\/_/\/_/    \/_____/    '\ __//__/  \/_/ \/__/\/_/ \ \ \/  \ \ \/  \/____/ \/_/
#               /                                                                             \ \_\   \ \_\
#                                                                                              \/_/    \/_/

#
# Epydoc documentation
#

"""
@author: Kai Borowiak
@summary: Raw API Wrapper for Testlink
"""

#
# IMPORTS
#
import logging
import xmlrpclib
import inspect # For disabling invalid calls

#
# ENABLES LOGGING
#
logging.getLogger(__name__).addHandler(logging.NullHandler())

#
# EXCEPTIONS
#
class InvalidProxy(TypeError): pass
class NotSupported(NotImplementedError): pass
class APIError(Exception): pass

#
# ANNOTATIONS
#
def handleAPIError(fn):
	"""Annotation which checks for error in Testlink API"""
	def wrapped(self,*args,**kwargs):
		resp = fn(self,*args,**kwargs)
		# Testlink API error struct
		# {'message': 'xxx', 'code': 'xxx'}
		if (len(resp)==1 and 'message' in resp[0].keys() and 'code' in resp[0].keys()):
			logging.getLogger(__name__).exception("API ERROR [%s] %s" % (resp[0]['code'],resp[0]['message']) )
			raise APIError("[%s] %s" % (resp[0]['code'],resp[0]['message']) )
		return resp
	return wrapped

def handleNotSupported(fn):
	"""Annotation which checks for unsupported XML-RPC methods"""
	def wrapped(self,*args,**kwargs):
		try:
			return fn(self,*args,**kwargs)
		except xmlrpclib.Fault,f:
			if f.faultCode==-32601: # Method not supported
				logging.getLogger(__name__).exception("Method 'tl.%s' not supported @ %s" % (fn.__name__,repr(self._server)) )
				raise NotSupported("Method tl.%s @ %s" % (fn.__name__,repr(self._server)) )
	return wrapped

class TestlinkAPI(object):
	"""Raw Testlink API"""

	class CustomTransport(xmlrpclib.Transport):
		"""Custom Transport handler, for logging remote API calls"""
		def request(self,host,handler,request_body,verbose=False):
			deflated_request = xmlrpclib.loads(request_body)
			method = deflated_request[1]
			params = deflated_request[0]
			logging.getLogger(__name__).debug("remote call %s(%s) @ %s" % \
					(method, \
					', '.join([str(e) for e in params]), \
					host))
			return xmlrpclib.Transport.request(self,host,handler,request_body,verbose)

	def __init__(self,proxy):
		"""Initializes the TestlinkAPI
		@param proxy: URI of Testlink XML-RPC server implementation
		@type proxy: str
		@raises InvalidProxy: The given proxy is empty
		"""
		proxy = str(proxy)
		# Modulate the proxy to fit requirements
		self.__proxy = proxy
		try:
			self._server = xmlrpclib.ServerProxy(uri=proxy,transport=TestlinkAPI.CustomTransport())
		except IOError:
			raise InvalidProxy(proxy)

	#
	# Raw API methods
	#

	@handleNotSupported
	@handleAPIError
	def about(self):
		"""Returns informations about the current Testlink API
		@returns: 'Testlink API Version: x.x initially written by Asial Brumfield with contributions by Testlink development Team'
		@rtype: str
		"""
		return self._server.tl.about()

	@handleNotSupported
	@handleAPIError
	def sayHello(self):
		"""Returns the string 'Hello!'
		@returns: 'Hello!'
		@rtype: str
		"""
		return self._server.tl.sayHello()

	@handleNotSupported
	@handleAPIError
	def ping(self):
		"""Alias for 'sayHello'
		@returns: 'Hello!'
		@rtype: str
		"""
		return self._server.tl.ping()

	@handleNotSupported
	@handleAPIError
	def repeat(self,value):
		"""Repeats the given value
		@param value: The value to be repeated by the server
		@type value: mixed
		@returns: The given value
		@rtype: mixed
		"""
		return self._server.tl.repeat(value)

	@handleNotSupported
	@handleAPIError
	def checkDevKey(self,devkey):
		"""Checks if the specified developer key is valid
		@param devkey: The developer key to be tested
		@type devkey: str
		@returns: True/False
		@rtype: bool
		"""
		return self._server.tl.checkDevKey({'devKey': devkey})

	@handleNotSupported
	@handleAPIError	
	def doesUserExist(self, devkey, user):
		"""Checks, if a specified user exists
		@param devkey: Testlink developer key
		@type devkey: str
		@param user: User to be tested
		@type user: str
		@returns: True/False
		@rtype: bool
		"""
		return self._server.tl.doesUserExist({
				'devKey': devkey,
				'user': user
			})

	@handleNotSupported
	@handleAPIError
	def getFullPath(self, devkey, nodeid):
		"""Returns the full path of an object
		@param devkey: Testlink developer key
		@type devkey: str
		@param nodeid: The internal ID of the object
		@type nodeid: int
		@returns: Hierarchical path of the object
		@rtype: str
		"""
		return self._server.tl.getFullPath({
				'devKey': devkey,
				'nodeID': nodeid
			})

	@handleNotSupported
	@handleAPIError
	def createTestProject(self, devkey, name, prefix, notes='', active=True, public=True, requirementsEnabled=False, testPriorityEnabled=False, automationEnabled=False, inventoryEnabled=False):
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
		@param requirementsEnabled: <OPTIONAL> The TestProject supports requirements (Default is: False)
		@type requirementsEnabled: bool
		@param testPriorityEnabled: <OPTIONAL> The TestProject supports test case priority (Default is: False)
		@type testPriorityEnabled: bool
		@param automationEnabled: <OPTIONAL> The TestProject supports test automation (Default is: False)
		@type automationEnabled: bool
		@param inventoryEnabled: <OPTIONAL> The TestProject supports inventory features (Default is: False)
		@type inventoryEnabled: bool
		@returns: Server response
		@rtype: dict/list/???

		@todo: Refactor option flags
		@todo: Specify return value
		"""
		# Build options
		opts = {
			'requirementsEnabled': requirementsEnabled,
			'testPriorityEnabled': testPriorityEnabled,
			'automationEnabled': automationEnabled,
			'inventoryEnabled': inventoryEnabled
			}
		return self._server.tl.createTestProject({
				'devKey': devkey,
				'name': name,
				'prefix': prefix,
				'notes': notes,
				'active': active,
				'public': public,
				'options': opts
			})

	@handleNotSupported
	@handleAPIError
	def getProjects(self, devkey):
		"""Returns all available TestProjects
		@param devkey: Testlink developer key
		@type devkey: str
		@returns: TestProjects as list of dicts
		@rtype: list
		"""
		return self._server.tl.getProjects({'devKey': devkey})

	@handleNotSupported
	@handleAPIError
	def getTestProjectByName(self, devkey, name):
		"""Returns a single TestProject specified by its name
		@param devkey: Testlink developer key
		@type devkey: str
		@param name: Name of the TestProject
		@type name: str
		@returns: Matching TestProject
		@rtype: dict
		"""
		return self._server.tl.getTestProjectByName({
				'devKey': devkey,
				'testprojectname': name
			})

	@handleNotSupported
	@handleAPIError
	def createTestPlan(self, devkey, name, projectname, notes='', active=True, public=True):
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
		return self._server.tl.createTestPlan({
				'devKey': devkey,
				'testplanname': name,
				'testprojectname': projectname,
				'notes': notes,
				'active': active,
				'public': public
			})

	@handleNotSupported
	@handleAPIError
	def getTestPlanByName(self, devkey, name, projectname):
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
		return self._server.tl.getTestPlanByName({
				'devKey': devkey,
				'testplanname': name,
				'testprojectname': projectname
			})

	@handleNotSupported
	@handleAPIError
	def getProjectTestPlans(self, devkey, projectid):
		"""Returns all TestPlans for a specified TestProject
		@param devkey: Testlink developer key
		@type devkey: str
		@param projectid: The internal ID of the TestProject
		@type projectid: int
		@returns: Matching TestPlans
		@rtype: list
		"""
		return self._server.tl.getProjectTestPlans({
				'devKey': devkey,
				'testprojectid': projectid
			})

	@handleNotSupported
	@handleAPIError
	def createBuild(self, devkey, testplanid, name, notes=''):
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
		return self._server.tl.createBuild({
				'devKey': devkey,
				'testplanid': testplanid,
				'buildname': name,
				'buildnotes': notes
			})

	@handleNotSupported
	@handleAPIError
	def getLatestBuildForTestPlan(self, devkey, testplanid):
		"""Returns the latest Build for the specified TestPlan
		@param devkey: Testlink developer key
		@type devkey: str
		@param testplanid: The internal ID of the TestPlan
		@type testplanid: int
		@returns: Matching Build
		@rtype: list
		"""
		return self._server.tl.getLatestBuildForTestPlan({
				'devKey': devkey,
				'testplanid': testplanid
			})

	@handleNotSupported
	@handleAPIError
	def getBuildsForTestPlan(self, devkey, testplanid):
		"""Returns all Builds for the specified TestPlan
		@param devkey: Testlink developer key
		@type devkey: str
		@param testplanid: The internal ID of the TestPlan
		@type testplanid: int
		@returns: Matching Builds
		@rtype: list
		"""
		return self._server.tl.getBuildsForTestplan({
				'devKey': devkey,
				'testplanid': testplanid
			})

	@handleNotSupported
	@handleAPIError
	def getTestPlanPlatforms(self, devkey, testplanid):
		"""Returns all Platforms fot the specified TestPlan
		@param devkey: Testlink developer key
		@type devkey: str
		@param testplanid: The internal ID of the TestPlan
		@type testplanid: int
		@returns: Matching Platforms
		@rtype: list
		"""
		return self._server.tl.getTestPlanPlatforms({
				'devKey': devkey,
				'testplanid': testplanid
			})

	@handleNotSupported
	@handleAPIError
	def reportTCResult(self, devkey, testplanid, status, testcaseid=None, testcaseexternalid=None, buildid=None, buildname=None, notes=None, guess=True, bugid=None, platformid=None, platformname=None, customfields=None, overwrite=False):
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
		return self._server.tl.reportTCResult({
				'devKey': devkey,
				'testplanid': testplanid,
				'status': status,
				'testcaseid': testcaseid,
				'testcaseexternalid': testcaseexternalid,
				'buildid': buildid,
				'buildname': buildname,
				'notes': notes,
				'guess': guess,
				'bugid': bugid,
				'platformid': platformid,
				'platformname': platformname,
				'customfields': customfields,
				'ovwerwrite': overwrite
			})

	@handleNotSupported
	@handleAPIError
	def getLastExecutionResult(self, devkey, testplanid, testcaseid=None, testcaseexternalid=None):
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
		return self._server.getLastExecutionResult({
				'devKey': devkey,
				'testplanid': testplanid,
				'testcaseid': testcaseid,
				'testcaseexternalid': testcaseexternalid
			})

	@handleNotSupported
	@handleAPIError
	def deleteExecution(self, devkey, executionid):
		"""Deletes a specific exexution result
		@param devkey: Testlink developer key
		@type devkey: str
		@param executionid: The internal ID of the execution result
		@type executionid: int
		@returns: Server response
		@rtype: dict
		"""
		return self._server.deleteExecution({
				'devKey': devkey,
				'executionid': executionid
			})

	@handleNotSupported
	@handleAPIError
	def createTestSuite(self, devkey, name, testprojectid, details=None, parentid=None, order=None, checkduplicates=True, actiononduplicate='block'):
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
		return self._server.tl.createTestSuite({
				'devKey': devkey,
				'testsuitename': name,
				'testprojectid': testprojectid,
				'details': details,
				'parentid': parentid,
				'order': order,
				'checkduplicatedname': checkduplicates,
				'actiononduplicatedname': actiononduplicate
			})

	@handleNotSupported
	@handleAPIError
	def getTestSuiteById(self, devkey, suiteid):
		"""Returns a single TestSuite specified by the internal ID
		@param devkey: Testlink developer key
		@type devkey: str
		@param suiteid: The internal ID of the TestSuite
		@type suiteid: int
		@returns: Matching TestSuite
		@rtype: dict
		"""
		return self._server.tl.getTestSuiteById({
				'devKey': devkey,
				'testsuiteid': suiteid
			})

	@handleNotSupported
	@handleAPIError
	def getTestSuitesForTestSuite(self, devkey, suiteid):
		"""Returns all TestSuites within the specified TestSuite
		@param devkey: Testlink developer key
		@type devkey: str
		@param suiteid: The internal ID of the TestSuite
		@type suiteid: int
		@returns: Matching TestSuites
		@rtype: dict/list/???
		"""
		return self._server.tl.getTestSuitesForTestSuite({
				'devKey': devkey,
				'testsuiteid': suiteid
			})

	@handleNotSupported
	@handleAPIError
	def getFirstLevelTestSuitesForTestProject(self, devkey, projectid):
		"""Returns the first level TestSuites for a specified TestProject
		@param devkey: Testlink developer key
		@type devkey: str
		@param projectid: The internal ID of the TestProject
		@type projectid: int
		@returns: Matching TestSuites
		@rtype: dict/list/???
		"""
		return self._server.tl.getFirstLevelTestSuitesForTestProject({
				'devKey': devkey,
				'testprojectid': testprojectid
			})

	@handleNotSupported
	@handleAPIError
	def getTestSuitesForTestPlan(self, devkey, planid):
		"""Returns all TestSuites for a specified TestPlan
		@param devkey: Testlink developer key
		@type devkey: str
		@param planid: The internal ID of the TestPlan
		@type planid: int
		@returns: Matching TestSuites
		@rtype: dict/list/???
		"""
		return self._server.tl.getTestSuitesForTestPlan({
				'devKey': devkey,
				'testplanid': planid
			})

	@handleNotSupported
	@handleAPIError
	def createTestCase(self, devkey, name, suiteid, projectid, author, summary, steps=[], preconditions=None, importance=0, execution=0, order=None, checkduplicates=True, actiononduplicate='block'):
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
		return self._server.tl.createTestCase({
				'devKey': devkey,
				'testcasename': name,
				'testsuiteid': suiteid,
				'testprojectid': projectid,
				'authorlogin': author,
				'summary': summary,
				'steps': steps,
				'preconditions': preconditions,
				'importance': importance,
				'exexution': execution,
				'order': order,
				'checkduplicatedname': checkduplicates,
				'actiononduplicatedname': actiononduplicate
			})

	@handleNotSupported
	@handleAPIError
	def getTestCase(self, devkey, testcaseid=None, testcaseexternalid=None, version=None):
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
		return self._server.tl.getTestCase({
				'devKey': devkey,
				'testcaseid': testcaseid,
				'testcaseexternalid': testcaseexternalid,
				'version': version
			})

	@handleNotSupported
	@handleAPIError
	def getTestCaseIdByName(self, devkey, name, suite=None, project=None, path=None):
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
		return self._server.tl.getTestCaseIDByName({
				'devKey': devkey,
				'testcasename': name,
				'testsuitename': suite,
				'testprojectname': project,
				'testcasepathname': path
			})

	@handleNotSupported
	@handleAPIError
	def getTestCasesForTestSuite(self, devkey, suiteid, deep=False, details='simple'):
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
		return self._server.tl.getTestCasesForTestSuite({
				'devKey': devkey,
				'testsuiteid': suiteid,
				'deep': deep,
				'details': details
			})

	@handleNotSupported
	@handleAPIError
	def getTestCasesForTestPlan(self, devkey, planid, testcaseid=None, buildid=None, keywordid=None, keywords=None, executed=None, assignedto=None, executionstatus=None, executiontype=None, steps=False):
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
		return self._server.tl.getTestCasesForTestPlan({
				'devKey': devkey,
				'testplanid': planid,
				'tcid': testcaseid, # Correct?
				'buildid': buildid,
				'keywordid': keywprdid,
				'keywords': keywords,
				'executed': executed,
				'assignedto': assignedto,
				'executestatus': executionstatus,
				'executiontype': executiontype,
				'getstepinfo': steps
			})

	@handleNotSupported
	@handleAPIError
	def addTestCaseToTestPlan(self, devkey, projectid, planid, testcaseexternalid, version, platformid=None, executionorder=None, urgency=None):
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
		return self._server.tl.addTestCaseToTestPlan({
				'devKey': devkey,
				'testprojectid': projectid,
				'testplanid': planid,
				'testcaseexternalid': testcaseexternalid,
				'version': version,
				'platformid': platformid,
				'executionorder': executionorder,
				'urgency': urgency
			})

	@handleNotSupported
	@handleAPIError
	def assignRequirements(self, devkey, testcaseexternalid, projectid, requirements):
		""""Assigns specified Requirements to a specified TestCase
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
		return self._server.tl.assignRequirements({
				'devKey': devkey,
				'testcaseexternalid': testcaseexternalid,
				'testprojectid': projectid,
				'requirements': requirements
			})

	@handleNotSupported
	@handleAPIError
	def getTestCaseCustomFieldDesignValue(self, devkey, testcaseexternalid, version, projectid, fieldname, details='value'):
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
		return self._server.tl.getTestCaseCustomFieldDesignValue({
				'devKey': devkey,
				'testcaseexternalid': testcaseexternalid,
				'version': version,
				'testprojectid': projectid,
				'customfieldname': fieldname,
				'details': details
			})

	@handleNotSupported
	@handleAPIError
	def uploadAttachment(self, devkey, objectid, objecttable, name, mime, content, title=None, description=None):
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
		return self._server.tl.uploadAttachment({
				'devKey': devkey,
				'fkid': objectid,
				'fktable': objecttable,
				'filename': name,
				'filetype': mime,
				'content': content,
				'title': title,
				'description': description
			})

	@handleNotSupported
	@handleAPIError
	def uploadRequirementSpecificationAttachment(self, devkey, reqspecid, name, mime, content, title=None, description=None):
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
		return self._server.tl.uploadRequirementSpecificationAttachment({
				'devKey': devkey,
				'reqspecid': reqspecid,
				'filename': name,
				'filetype': mime,
				'content': content,
				'title': title,
				'description': description
			})

	@handleNotSupported
	@handleAPIError
	def uploadRequirementAttachment(self, devkey, reqid, name, mime, content, title=None, description=None):
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
		return self._server.tl.uploadRequirementAttachment({
				'devKey': devkey,
				'requirementsid': reqid,
				'filename': name,
				'filetype': mime,
				'content': content,
				'title': title,
				'description': description
			})

	@handleNotSupported
	@handleAPIError
	def uploadTestProjectAttachment(self, devkey, projectid, name, mime, content, title=None, description=None):
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
		return self._server.tl.uploadTestProjectAttachment({
				'devKey': devkey,
				'testprojectid': projectid,
				'filename': name,
				'filetype': mime,
				'content': content,
				'title': title,
				'description': description
			})

	@handleNotSupported
	@handleAPIError
	def uploadTestSuiteAttachment(self, devkey, suiteid, name, mime, content, title=None, description=None):
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
		return self._server.tl.uploadTestSuiteAttachment({
				'devKey': devkey,
				'testsuiteid': suiteid,
				'filename': name,
				'filetype': mime,
				'content': content,
				'title': title,
				'description': description
			})

	@handleNotSupported
	@handleAPIError
	def uploadTestCaseAttachment(self, devkey, testcaseid, name, mime, content, title=None, description=None):
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
		return self._server.tl.uploadTestCaseAttachment({
				'devKey': devkey,
				'testcaseid': testcaseid,
				'filename': name,
				'filetype': mime,
				'content': content,
				'title': title,
				'description': description
			})

	@handleNotSupported
	@handleAPIError
	def uploadExecutionAttachment(self, devkey, executionid, name, mime, content, title=None, description=None):
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
		return self._server.tl.uploadExecutionAttachment({
				'devKey': devkey,
				'executionid': executionid,
				'filename': name,
				'filetype': mime,
				'content': content,
				'title': title,
				'description': description
			})

	@handleNotSupported
	@handleAPIError
	def getTestCaseAttachments(self, devkey, testcaseid=None, testcaseexternalid=None):
		"""Returns all available Attachments for the specified TestCase
		@param devkey: Testlink developer key
		@type devkey: str
		@param testcaseid: <OPTIONAL> The internal ID of the TestCase. If not given, external ID must be set
		@type testcaseid: int
		@param testcaseexternalid: <OPTIONAL> The external ID of the TestCase. If not given, the internal ID must be set
		@type testcaseexternalid: int
		@returns: Matching attachments
		@rtype: list/dict/???
		"""
		return self._server.tl.getTestCaseAttachmnts({
				'devKey': devkey,
				'testcaseid': testcaseid,
				'testcaseexternalid': testcaseexternalid
			})

	@handleNotSupported
	@handleAPIError
	def getRequirementSpecifications(self, devkey, testprojectid):
		"""Returns all available Requirement Specifications for the specified TestProject
		@param devkey: Testlink developer key
		@type devkey: str
		@param testprojectid: The internal ID of the parent TestProject.
		@type testprojectid: int
		@returns: Matching Requirement Specifications
		@rtype: list/dict/???
		"""
		return self._server.tl.getRequirementSpecifications({
				'devKey' : devkey,
				'testprojectid' : testprojectid
			})

	@handleNotSupported
	@handleAPIError
	def getRequirementsForRequirementSpecification(self, devkey, testprojectid, reqspecid):
		"""Returns all available Requirements for the specified Requirement Specification
		@param devkey: Testlink developer key
		@type devkey: str
		@param testprojectid: The internal ID of the parent TestProject.
		@type testprojectid: int
		@param reqspecid: The internal ID of the parent Requirement Specification
		@type reqspecid: int
		@returns: Matching Requirements
		@rtype: list/dict/???
		"""
		return self._server.tl.getRequirementsForRequirementSpecification({
				'devKey' : devkey,
				'testprojectid' : testprojectid,
				'reqspecid': reqspecid
			})
