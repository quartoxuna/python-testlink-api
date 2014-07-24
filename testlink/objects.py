#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@author: Kai Borowiak
@summary: Object oriented Wrapper for Testlink
"""

# IMPORTS
import re
import copy
from datetime import date

from . import log
from .api import Testlink_XML_RPC_API
from .exceptions import InvalidURL
from .exceptions import NotSupported
from .enums import APIType
from .enums import DuplicateStrategy
from .enums import ImportanceLevel
from .enums import ExecutionType
from .enums import CustomFieldDetails
from .parsers import DefaultParser

class Testlink(object):
	"""Testlink Server implementation
	@ivar _url: URL of connected Testlink
	@type _url: str
	@ivar _devkey: Valid Testlink developer key
	@type _devkey: str
	"""

	def __init__(self,url,devkey,api=APIType.XML_RPC):
		"""Initializes the Testlink Server object
		@param url: Testlink URL
		@type url: str
		@param devkey: Testlink developer key
		@type devkey: str
		"""
		self._url = url
		self._devkey = devkey

		# Init raw API
		if api == APIType.XML_RPC:
			self._api = Testlink_XML_RPC_API(url)
		elif api == APIType.REST:
			raise NotImplementedError()

		# Log API Information
		log.info("Testlink Version '%s' at '%s'" % (self.getVersion(),url) )

		# Set devkey globally
		self._api.devkey = devkey

	def getVersion(self):
		"""Retrieve informations about the used Testlink API
		@return: Version String
		@rtype: str
		"""
		# Check for easy API call
		try:
			return self._api.testLinkVersion()
		except NotSupported:
			about_str = self._api.about()
			return re.search(r"(?P<version>\d+(\.{0,1}\d+)+)",about_str).group('version')

	def getTestProject(self,name=None,**params):
		"""Returns generator over TestProjects specified by parameters
		@param name: The name of the TestProject
		@type name: str
		@param params: Other params for TestProject
		@type params: dict
		@returns: Matching TestProjects
		@rtype: generator
		"""
		# Check if simple API call can be done
		if name and len(params)==0:
			response = Testlink._api.getTestProjectByName(name)
			yield TestProject(**response[0])
		else:
			# Filter by specified parameters
			response = Testlink._api.getProjects()
			if len(params)>0:
				params['name'] = name
				for project in copy.copy(response):
					for key,value in params.items():
						if not (unicode(project[key]) == unicode(value)):
							response.remove(project)
							break
			for project in response:
				yield TestProject(**project)

class TestlinkObject:
	"""Abstract Testlink Object
	@ivar id: Internal Testlink Id of the object
	@type id: int
	@ivar name: Internal Testlink name of the object
	@type name: str
	"""

	__slots__ = ("id","name")

	def __init__(self,id=-1,name=""):
		"""Initialises base Testlink object
		@param id: Internal Testlink Id of the object
		@type id: int
		@param name: Internal Testlink name of the object
		@type name: str
		@keyword kwargs: Additonal attributes
		"""
		self.id = int(id) if id else id
		self.name = DefaultParser().feed(name)

	def __str__(self):
		return str(self.name)

	def __unicode__(self):
		return unicode(self.name)

	def __eq__(self,other):
		return self.id == other.id


class TestProject(TestlinkObject):
	"""Testlink TestProject representation
	@ivar notes: TestProject notes
	@type notes: str
	@ivar prefix: TestCase prefix within TestProject
	@type prefix: str
	@ivar active: TestProject active flag
	@type active: bool
	@ivar public: TestProject public flag
	@type public: bool
	@ivar requirements_enabled: Requirement Feature flag
	@type requirements_enabled: bool
	@ivar priority_enabled: Test Priority feature flag
	@type priority_enabled: bool
	@ivar automation_enabled: Automation Feature flag
	@type automation_enabled: bool
	@ivar inventory_enabled: Inventory Feature flag
	@type inventory_enabled: bool
	@ivar tc_count: Current amount of TestCases in TestProject
	@type tc_count: int
	@ivar color: Assigned color of TestProject
	@type color: str"""

	__slots__ = ("id","name","notes","prefix","active","public","requirements_enabled",\
			"priority_enabled","automation_enabled","inventory_enabled","tc_count","color")

	def __init__(
			self,\
			id=-1,\
			name="",\
			notes="",\
			prefix="",\
			active=False,\
			is_public=False,\
			tc_counter=0,\
			opt={
				'requirementsEnabled':False,
				'testPriorityEnabled':False,
				'automationEnabled':False,
				'inventoryEnabled':False
			},\
			color="",\
			**kwargs\
		):
		TestlinkObject.__init__(self,id,name)
		self.notes = DefaultParser().feed(notes)
		self.prefix = DefaultParser().feed(prefix)
		self.active = bool(active)
		self.public = bool(is_public)
		self.requirements = bool(opt['requirementsEnabled'])
		self.priority = bool(opt['testPriorityEnabled'])
		self.automation = bool(opt['automationEnabled'])
		self.inventory = bool(opt['inventoryEnabled'])
		self.tc_count = int(tc_counter)
		self.color = DefaultParser().feed(color)


	def getTestPlan(self,name=None,**params):
		"""Returns generator over TestPlans specified by parameters
		@param name: The name of the TestPlan
		@type name: str
		@param params: Other params for TestPlan
		@type params: dict
		@returns: Matching TestPlans
		@rtype: generator
		"""
		# Check if simple API call can be done
		if name and len(params)==0:
			response = Testlink._api.getTestPlanByName(name,projectname=self.name)
			yield TestPlan(**response[0])
		else:
			# Filter by specified parameters
			response = Testlink._api.getProjectTestPlans(self.id)
			if len(params)>0:
				params['name'] = name
				for plan in copy.copy(response):
					for key,value in params.items():
						if not (unicode(plan[key]) == unicode(value)):
							response.remove(plan)
							break
			for plan in response:
				yield TestPlan(**plan)
			

	def getTestSuite(self,name=None,id=None,recursive=True,**params):
		"""Returns generator over TestSuites specified by parameters
		@param name: The name of the wanted TestSuite
		@type name: str
		@param recursive: Enable recursive search
		@type recursive: bool
		@param params: Other params for TestSuite
		@type params: dict
		@returns: Matching TestSuites
		@rtype: generator
		"""
		# Check if simple API call can be done
		# Since the ID is unique, all other params can be ignored
		if id:
			response = Testlink._api.getTestSuiteById(id)
			yield TestSuite(**response)
		else:
			# Filter by specified parameters
			response = Testlink._api.getFirstLevelTestSuitesForTestProject(self.id)

			# Bug !
			# Since the API call to getFirstLevelTestSuites does NOT
			# return the details, we have to get it with another API call
			# This has to be done BEFORE the acutal filtering because otherwise
			# we could not filter by the details
			response = [Testlink._api.getTestSuiteById(suite['id']) for suite in response]

			# Filter by specified parameters
			if len(params)>0 or name:
				params['name'] = name
				params['id'] = None
				for suite in copy.copy(response):
					for key,value in params.items():
						if value and not (unicode(suite[key]) == unicode(value)):
							response.remove(suite)
							break

			# Built TestSuite objects here to simplify recursive search
			first_level_suites = [TestSuite(parent_testproject=self,**suite) for suite in response]
			for suite in first_level_suites:
				yield suite
			# Recursively search in sub suites
			for suite in first_level_suites:
				for s in suite.getTestSuite(**params):
					yield s

	def create_test_suite(self,suite,order=0,on_duplicate=DuplicateStrategy.BLOCK):
		"""Creates a new TestSuite in the current TestProject
		@param suite: TestSuite to create
		@type suite: TestSuite
		@param order: Order of the new TestSuite within parent object
		@type order: int
		@param on_duplicate: Action on duplicate (Default: DuplicateStrategy.BLOCK)
		@type on_duplicate: DuplicateStrategy
		@raises TypeError: Specified suite is not of type TestSuite
		"""
		# Check for correct type
		if not isinstance(suite,TestSuite):
			raise TypeError(str(suite.__class__.__name__))

		# Create TestSuite
		Testlink._api.createTestSuite(
					name = suite.name,\
					testprojectid = self.id,\
					details = suite.details,\
					order = order,\
					actiononduplicate = on_duplicate\
				)


class TestPlan(TestlinkObject):
	"""Testlink TestPlan representation
	@ivar notes: TestPlan notes
	@type notes: str
	@ivar active: TestPlan active flag
	@type active: bool
	@ivar public: TestPlan public flag
	@type public: bool
	"""

	__slots__ = ("id","name","notes","active","public")

	def __init__(
			self,\
			id=-1,\
			name="",\
			notes="",\
			is_public=False,\
			active=False,\
			parent_testproject=None,\
			**kwargs
		):
		TestlinkObject.__init__(self,id,name)
		self.notes = DefaultParser().feed(notes)
		self.active = bool(active)
		self.public = bool(is_public)
		self._parent_testproject = parent_testproject
	

	def getBuild(self,name=None,**params):
		"""Returns generator over Builds specified by parameters
		@param name: The name of the Build
		@type name: str
		@param params: Other params for Build
		@type params: dict
		@returns: Macthing Builds
		@rtype: generator
		"""
		# No simple API call possible, get all
		response = Testlink._api.getBuildsForTestPlan(self.id)

		# Filter by specified params
		if len(params)>0 or name:
			params['name'] = name
			for build in copy.copy(response):
				for key,value in params.items():
					if value and not (unicode(build[key]) == unicode(value)):
						response.remove(build)
						break
		for build in response:
			yield Build(**build)

	def getPlatform(self,name=None,**params):
		"""Returns generator over Platforms specified by parameters
		@param name: The name of the Platform
		@type name: str
		@param params: Other params for Platform
		@type params: dict
		@returns: Matching Platforms
		@rtype: generator
		"""
		# No simple API call possible, get all
		response = Testlink._api.getTestPlanPlatforms(self.id)

		# Filter by specified params
		if len(params)>0 or name:
			params['name'] = name
			for platform in copy.copy(response):
				for key,value in params.items():
					if value and not (unicode(platform[key]) == unicode(value)):
						response.remove(platform)
						break
		for platform in response:
			yield Platform(**platform)
		
	def getTestSuite(self,name=None,**params):
		"""Return generator TestSuites specified by parameters"""

		raise NotImplementedError()

	def getTestCase(
			self,\
			name = None,\
			id = None,\
			buildid = None,\
			keywordid = None,\
			keywords = None,\
			executed = None,\
			assigned_to = None,\
			execution_status = None,\
			execution_type = None,\
			**params
		):
		"""Returns generator over Testcases specified by parameters
		@param name: The name of the TestCase
		@type name: str
		@param id: The internal ID of the TestCase
		@type id: int
		@param buildid: The internal ID of the Build
		@type buildid: int
		@param keywordid: The internal ID of the used Keyword
		@type keywordid: int
		@param keywords: Keywords to filter for
		@type keywords: list
		@param executed: Checks if TestCase is executed
		@type executed: bool
		@param assigned_to: Filter by internal ID of assigned Tester
		@type assigned_to: int
		@param execution_status: Filter by execution status
		@type execution_status: char ???
		@param execution_type: Filter by execution type
		@type execution_type: ExecutionType
		@param params: Other params for TestCase
		@type params: dict
		@returns: Matching TestCases
		@rtype: generator
		"""
		# Get all available TestCases
		# Use all possible API params to speed up API call
		response = Testlink._api.getTestCasesForTestPlan(\
								self.id,\
								id,\
								buildid,\
								keywordid,\
								keywords,\
								executed,\
								assigned_to,\
								execution_status,\
								execution_type,\
								steps = True\
							)
										
		# Normalize result
		testcases = []
		for tcid,platforms in response.items():
			# Check if the platform is really one
			for platform_id,tc in platforms.items():
				if not isinstance(tc,dict):
					# No platforms, first nested items are testcases
					log.debug("No Platforms within this testplan")
					testcases = platforms
					break
				testcases.append(tc)

		# Filter by specified params
		if len(params)>0 or name:
			params['name'] = name
			for case in copy.copy(testcases):
				for key,value in params.items():
					if value and not (unicode(case[key]) == unicode(value)):
						testcases.remove(case)
						break
		log.debug("Got %d testcases total" % len(testcases))
		for case in testcases:
			yield TestCase(parent_testproject=self._parent_testproject,**case)

class Build(TestlinkObject):
	"""Testlink Build representation
	@ivar notes: Build notes
	@type notes: str
	"""

	__slots__ = ("id","name","notes")

	def __init__(self,id=None,name=None,notes=None,**kwargs):
		TestlinkObject.__init__(self,id,name)
		self.notes = DefaultParser().feed(notes)


class Platform(TestlinkObject):
	"""Testlink Platform representation
	@ivar notes: Platform notes
	@type notes: str
	"""

	__slots__ = ("id","name","notes")

	def __init__(self,id=None,name=None,notes=None,**kwargs):
		TestlinkObject.__init__(self,id,name)
		self.notes = DefaultParser().feed(notes)


class TestSuite(TestlinkObject):
	"""Testlink TestSuite representation
	@ivar notes: TestSuite notes
	@type notes: str
	"""

	__slots__ = ("id","name","details","_parent_testproject","_parent_testsuite")

	def __init__(self,id=-1,name="",details="",parent_testproject=None,parent_testsuite=None,**kwargs):
		TestlinkObject.__init__(self,id,name)
		self.details = DefaultParser().feed(details)
		self._parent_testproject = parent_testproject
		self._parent_testsuite = parent_testsuite

	def getTestSuite(self,name=None,id=None,**params):
		"""Returns geneator over TestSuites speficied by parameters
		@param name: The name of the wanted TestSuite
		@type name: str
		@param params: Other params for TestSuite
		@type params: dict
		@returns: Matching TestSuites
		@rtype: generator
		"""
		# Simple API call could be done, but
		# we want to ensure, that only sub suites of this
		# particular suite are involved, so no API call here
		response = Testlink._api.getTestSuitesForTestSuite(self.id)

		# Normalize result
		if isinstance(response,str) and response.strip() == "":
			response = []
		elif isinstance(response,dict):
			# Check for nested dict
			if isinstance(response[response.keys()[0]],dict):
				response = [Testlink._api.getTestSuiteById(suite_id) for suite_id in response.keys()]
			else:
				response = [response]

		# Filter by specified parameters
		if len(params)>0 or name:
			params['name'] = name
			params['id'] = id
			for suite in copy.copy(response):
				for key,value in params.items():
					if value and not (unicode(suite[key]) == unicode(value)):
						response.remove(suite)
						break

		# Built TestSuite object here to simplify recursive search
		sub_suites = [TestSuite(parent_testproject=self._parent_testproject,parent_testsuite=self,**suite) for suite in response]
		for suite in sub_suites:
			yield suite
		# Recursively search in sub suites
		for suite in sub_suites:
			for s in suite.getTestSuite(**params):
				yield s

	def getTestCase(self,name=None,**params):
		"""Returns all TestCaes specified by parameters
		@param name: The name of the wanted TestCase
		@type name: str
		@param params: Other params for TestCase
		@type params: dict
		@returns: Matching TestCases
		@rtype: list
		"""
		# No simple API call possible, get all
		response = Testlink._api.getTestCasesForTestSuite(self.id,details='full')

		# Filter by specified parameters
		if len(params)>0 or name:
			params['name'] = name
			for case in copy.copy(response):
				for key,value in params.items():
					if value and not (unicode(case[key]) == unicode(value)):
						response.remove(case)
						break
		for case in response:
			yield TestCase(parent_testproject=self._parent_testproject,parent_testsuite=self,**case)

	def create_test_suite(self,suite,order=0,on_duplicate=DuplicateStrategy.BLOCK):
		"""Creates a new TestSuite within the current TestSuite
		@param suite: TestSuite to create
		@type suite: TestSuite
		@param order: Order of the new TestSuite within parent object
		@type order: int
		@param on_duplicate: Action on duplicate (Default: DuplicateStrategy.BLOCK)
		@type on_duplicate: DuplicateStrategy
		@raises TypeError: Specified suite is not of type TestSuite
		"""
		# Check for correct type
		if not isinstance(suite,TestSuite):
			raise TypeError(str(suite.__class__.__name__))

		# Create TestSuite
		Testlink._api.createTestSuite(
					name = suite.name,\
					testprojectid = self.__testproject_id,\
					details = suite.details,\
					parentid = self.id,\
					order = order,\
					actiononduplicate = on_duplicate\
				)


class TestCase(TestlinkObject):
	"""Testlink TestCase representation
	@ivar executed: Flag if TestCase has been executed yet
	@type executed: bool
	@ivar execution_notes: Notes for the last execution
	@type execution_notes: unicode
	@ivar execution_order: Order of execution
	@type execution_order: int
	@ivar version: Version number
	@type version: int
	@ivar exec_status: Execution status
	@type exec_status: str
	@ivar status: Status
	@type status: ???
	@ivar importance: ImportanceLevel
	@type importance: ImportanceLevel
	@ivar execution_type: Execution Type
	@type execution_type: ExecutionType
	@ivar active: Active flag
	@type active: bool
	@ivar summary: Summary of the TestCase
	@type summary: unicode
	@ivar platform_id: Internal ID of platform
	@type platform_id: int
	@ivar external_id: External ID of the TestCase
	@type external_id: int
	"""

	__slots__ = ("id","name","executed","execution_notes","execution_order","version",\
			"exec_status","status","importance","execution_type","active","summary",\
			"platform_id","external_id","_parent_testproject","_parent_testsuite")

	class Step(object):
		"""Testlink TestCase Step representation
		@ivar id: Internal ID of the Step
		@type id: int
		@ivar number: Number of the step
		@type number: int
		@ivar actions: Actions of the step
		@type actions: str
		@ivar execution_type: Type of Execution
		@type execution_type: ExecutionType
		@ivar active: Active flag
		@type active: bool
		@ivar results: Expected result of the step
		@type results: str
		"""

		__slots__ = ("id","number","actions","execution_type","active","results")

		def __init__(
				self,\
				step_number=1,\
				actions="",\
				execution_type=ExecutionType.MANUAL,\
				active=False,\
				id=-1,\
				expected_results="",\
				**kwargs\
			):
			self.id = int(id)
			self.number = int(step_number)
			self.actions = DefaultParser().feed(actions)
			self.execution_type = int(execution_type)
			self.active = bool(active)
			self.results = DefaultParser().feed(expected_results)

	class Execution(object):
		"""Testlink TestCase Execution representation
		@cvar DATETIME_FORMAT: Format of execution timestamp
		@type DATETIME_FORMAT: str

		@ivar id: The internal ID of the Execution
		@type id: int
		@ivar testplan_id: The internal ID of the parent TestPlan
		@type testplan_id: int
		@ivar build_id: The internal ID of the parent Build
		@type build_id: int
		@ivar tcversion_id: The internal ID of the parent TestCase Version
		@type tcversion_id: int
		@ivar tcversion_number: The version of the parent TestCase
		@type tcversion_number: int
		@ivar status: The status of the Execution
		@type status: str
		@ivar notes: Notes of the Execution
		@type notes: str
		@ivar execution_type: Execution Type
		@type execution_type: ExecutionType
		@ivar execution_ts: Timestamp of execution
		@type execution_ts: datetime
		@ivar tester_id: The internal ID of the tester
		@type tester_id: int
		"""

		__slots__ = ("id","testplan_id","platform_id","build_id","tcversion_id","tcversion_number","status",\
				"notes","execution_type","execution_ts","tester_id")

		DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"

		def __init__(
				self,\
				id=-1,\
				testplan_id=-1,\
				platform_id=-1,\
				build_id=-1,\
				tcversion_id=-1,\
				tcversion_number=0,\
				status='',\
				notes="",\
				execution_type=ExecutionType.MANUAL,\
				execution_ts="0000-00-00 00:00:00",\
				tester_id=-1,\
				**kwargs\
			):
			self.id = int(id)
			self.testplan_id = int(testplan_id)
			self.platform_id = int(platform_id)
			self.build_id = int(build_id)
			self.tcversion_id = int(tcversion_id)
			self.tcversion_number = int(tcversion_number)
			self.status = unicode(status)
			self.notes = DefaultParser().feed(notes)
			self.execution_type = int(execution_type)
			self.execution_ts = date.strptime(str(execution_ts),Execution.DATETIME_FORMAT)
			self.tester_id = int(tester_id)

		def delete(self):
			Testlink._api.deleteExecution(self.id)

	class Precondition(object):
		"""Testlink TestCase Precondition representation
		@ivar condition: Name of the condition
		@type conditions: str
		@ivar subconditions: Subconditions of the condition
		@type subconditions: list
		"""
		def __init__(self,condition,subs=()):
			self.condition = condition
			self.subconditions = [TestCase.Precondition(*sub) for sub in subs]

	def __init__(
			self,\
			tc_id=-1,\
			name="",\
			executed=False,\
			execution_notes="",\
			execution_order=-1,\
			version=0,\
			exec_status="",\
			status="",\
			importance=ImportanceLevel.LOW,\
			execution_type=ExecutionType.MANUAL,\
			active=False,\
			summary="",\
			preconditions="",\
			platform_id=-1,\
			tc_external_id=None,\
			external_id=-1,\
			steps=[],\
			parent_testproject=None,\
			parent_testsuite=None,\
			**kwargs\
		):
		TestlinkObject.__init__(self,tc_id,name)
		self.executed = bool(executed)
		self.execution_notes = DefaultParser().feed(execution_notes)
		self.execution_order = int(execution_order)
		self.version = int(version)
		self.exec_status = unicode(exec_status)
		self.status = unicode(status)
		self.importance = int(importance)
		self.execution_type = int(execution_type)
		self.active = bool(active)
		self.summary = DefaultParser().feed(summary)
		self.platform_id = int(platform_id)
		self.external_id = int(tc_external_id) if tc_external_id else external_id
		self._parent_testproject = parent_testproject
		self._parent_testsuite = parent_testsuite


		# TestCase Steps
		self.steps = [TestCase.Step(**s) for s in steps]

		# TestCase Preconditions
		self.preconditions = DefaultParser().feed(preconditions)

	def getLastExecutionResult(self,testplanid):
		resp = Testlink._api.getLastExecutionResult(testplanid,self.id,self.external_id)
		return TestCase.Execution(**resp)

	def deleteLastExecution(self,testplanid):
		# Update last execution
		last = self.getLastExecutionResult(testplanid)
		Testlink._api.deleteExecution(last.id)

	def reportResult(self,testplanid,status,notes=None,overwrite=False):
		Testlink._api.reportTCResult(
			testplanid = testplanid,\
			status = status,\
			testcaseid = self.id,\
			testcaseexternalid = self.external_id,\
			notes = notes,\
			platformid = self.platform_id,\
			overwrite = overwrite\
		)

	def getAttachments(self):
		return Testlink._api.getTestCaseAttachments(self.id,self.external_id)

	def getCustomFieldDesignValue(self,fieldname,details=CustomFieldDetails.VALUE_ONLY):
		"""Returns the custom field design value for the specified custom field
		@param fieldname: The internal name of the custom field
		@type fieldname: str
		@param details: Granularity of the response
		@type details: CustomFieldDetails
		@returns: Custom Field value or informations
		@rtype: mixed
		"""
		return Testlink._api.getTestCaseCustomFieldDesignValue(
					testcaseexternalid = "%s-%s" % (str(self._parent_testproject.prefix),str(self.external_id)),\
					version = self.version,\
					projectid = self._parent_testproject.id,\
					fieldname = fieldname,\
					details = details\
				)
