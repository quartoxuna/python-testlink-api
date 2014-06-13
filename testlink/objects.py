#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@author: Kai Borowiak
@summary: Object oriented Wrapper for Testlink
"""

# IMPORTS
import re
import xmlrpclib
import datetime
import copy
from .api import TestlinkAPI
from .log import tl_log as log
from .parsers import *

# Common enumerations
class ExecutionType:
	MANUAL = 1
	AUTOMATIC = 2

class Importance:
	HIGH = 3
	MEDIUM = 2
	LOW = 1

class OnDuplicate:
	BLOCK = 'block'

class Testlink(object):
	"""Testlink Server implementation
	@cvar _api: Used API instance
	@type _api: TestlinkAPI

	@ivar _url: URL of connected Testlink
	@type _url: str
	@ivar _devkey: Valid Testlink developer key
	@type _devkey: str
	"""

	_api = None

	def __init__(self,url,devkey):
		"""Initializes the Testlink Server object
		@param url: Testlink URL
		@type url: str
		@param devkey: Testlink developer key
		@type devkey: str
		"""
		self._url = url

		# URI modification for API initiation
		if not url.endswith('/lib/api/xmlrpc.php'):
			if not url.endswith('/'):
				url += '/'
			url += 'lib/api/xmlrpc.php'

		# Init raw API
		Testlink._api = TestlinkAPI(url)

		# Set devkey globally
		Testlink._api.devkey = devkey


	def getVersion(self):
		"""Retrieve informations about the used Testlink API
		@return: Version in list format [x,y,z]
		@rtype: list
		"""
		about_str = Testlink._api.about()
		version_str = re.search(r"(?P<version>\d+(\.{0,1}\d+)+)",about_str).group('version')
		version = version_str.split('.')
		# Get Alphas and Betas
		pre = re.search(r"(Alpha|Beta)\s*(\d+)", about_str)
		if pre:
			if pre.group(1)=="Alpha":
				version.append(0)
			elif pre.group(1)=="Beta":
				version.append(1)
			version.append(pre.group(2))
		return version

	def getTestProject(self,name=None,**params):
		"""Returns TestProject specified by parameters
		@param name: The name of the TestProject
		@type name: str
		@param params: Other params for TestProject
		@type params: Keyword arguments
		@returns: Matching TestProjects
		@rtype: list
		"""
		# Check if simple API call can be done
		if name and len(params)==0:
			response = Testlink._api.getTestProjectByName(name)
			# Response is a list
			return [TestProject(**response[0])]

		# Get all available Projects
		response = Testlink._api.getProjects()

		if len(params)>0:
			# Add name to search parameters
			params['name'] = name
	
			# Check for every project if all params
			# match and return this project
			matches = []
			for project in response:
				match = True
				for key,value in params.items():
					if not (project[key] == value):
						match = False
						break
				if match:
					matches.append(TestProject(**project))
			return matches
		else:
			# Otherwise, return all available projects
			return [TestProject(**project) for project in response]


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
		self.id = int(id)
		self.name = DefaultParser().feed(unicode(name))

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
		self.prefix = DefaultParser().feed(unicode(prefix))
		self.active = bool(active)
		self.public = bool(is_public)
		self.requirements = bool(opt['requirementsEnabled'])
		self.priority = bool(opt['testPriorityEnabled'])
		self.automation = bool(opt['automationEnabled'])
		self.inventory = bool(opt['inventoryEnabled'])
		self.tc_count = int(tc_counter)
		self.color = DefaultParser().feed(unicode(color))


	def getTestPlan(self,name=None,**params):
		"""Returns TestPlans specified by parameters
		@param name: The name of the TestPlan
		@type name: str
		@param params: Other params for TestPlan
		@type params: dict
		@returns: Matching TestPlans
		@rtype: list
		"""
		# Check if simple API call can be done
		if name and len(params)==0:
			response = Testlink._api.getTestPlanByName(name,projectname=self.name)
			return [TestPlan(**response[0])]

		# Get all TestPlans for the project
		response = Testlink._api.getProjectTestPlans(self.id)

		if len(params)>0:
			# Add name to search parameters
			params['name'] = name
	
			# Check for every plan if all params
			# match and return this testplan
			matches = []
			for plan in response:
				match = True
				for key,value in params.items():
					if not (str(plan[key]) == str(value)):
						match = False
						break
				if match:
					matched.append(TestPlan(**plan))
			return matches
		else:
			# Otherwise, return all available testplans
			return [TestPlan(**plan) for plan in response]
			

	def getTestSuite(self,name=None,id=None,recursive=True,**params):
		"""Returns TestSuites specified by parameters
		@param name: The name of the wanted TestSuite
		@type name: str
		@param recursive: Enable recursive search
		@type recursive: bool
		@param params: Other params for TestSuite
		@type params: dict
		@returns: Matching TestSuites
		@rtype: list
		"""
		# Check if simple API call can be done
		# Since the ID is unique, all other params
		# can be ignored
		if id:
			response = Testlink._api.getTestSuiteById(id)
			return [TestSuite(**response)]

		# Get all first level testsuites
		response = Testlink._api.getFirstLevelTestSuitesForTestProject(self.id)

		# Bug !
		# Since the API call to getFirstLevelTestSuites does NOT
		# return the details, we have to get it with another API call
		# This has to be done BEFORE the acutal filtering because otherwise
		# we could not filter by the details
		response = [Testlink._api.getTestSuiteById(suite['id']) for suite in response]

		# Built TestSuite object here to simplify method calls
		first_level_suites = [TestSuite(testproject_id=self.id,**suite) for suite in response]

		result = []
		if len(params)>0 or name:
			search_params = copy.copy(params)
			search_params.update({'name':name})

			# Check for every testsuite if all params
			# match and return that testsuite
			matches = []
			for suite in response:
				match = True
				for key,value in search_params.items():
					if value and not (unicode(suite[key]) == unicode(value)):
						match = False
						break
				if match:
					matches.append(TestSuite(testproject_id=self.id,**suite))
			# Add to results
			result.extend(matches)
		else:
			# Add all to results
			result.extend(first_level_suites)

		# Add matches in nested testsuites
		if recursive:
			for suite in first_level_suites:
				result.extend(suite.getTestSuite(name,id,recursive,**params))
		return result

	def create(self):
		"""Creates a new TestProject within the associated Testlink installation"""
		Testlink._api.createTestProject(
					name = self.name,\
					prefix = self.prefix,\
					notes = self.notes,\
					active = self.active,\
					public = self.public,\
					requirements = self.requirements_enabled,\
					priority = self.priority_enabled,\
					automation = self.automation_enabled,\
					inventory = self.inventory_enabled\
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
			**kwargs
		):
		TestlinkObject.__init__(self,id,name)
		self.notes = DefaultParser().feed(unicode(notes))
		self.active = bool(active)
		self.public = bool(is_public)
	

	def getBuild(self,name=None,**params):
		"""Returns Builds specified by parameters"""
		builds = Testlink._api.getBuildsForTestPlan(self.id)
		# Add name to params
		params['name'] = name
		for key,value in params.items():
			# Check for single result
			if isinstance(builds,dict):
				return Build(**builds)
			for b in builds:
				if b[key]==value:
					return Build(**b)

	def getPlatform(self,name=None,**params):
		"""Returns platforms specified by parameters"""
		platforms = Testlink._api.getTestPlanPlatforms(self.id)
		# Add name to params
		params['name'] = name		
		for key,value in params.items():
			# Check for single results
			if isinstance(platforms,dict):
				return Platform(**platforms)
			for p in platforms:
				if p[key]==value:
					return Platform(api,**p)
		
	def getTestSuite(self,name=None,**params):
		"""Return TestSuites specified by parameters"""
		raise NotImplementedError()
		"""
		suites = Testlink._api.getTestSuitesForTestPlan(self.id)
		if len(params)>0:
			for key,value in params.items():
				for s in suites:
					if s[key]==value:
						return TestSuite(api=Testlink._api,**s)
		else:
			return [TestSuite(api=Testlink._api,**s) for s in suites]
		"""

	def getTestCase(
			self,\
			testcaseid=None,\
			buildid=None,\
			keywordid=None,\
			keywords=None,\
			executed=None,\
			assignedto=None,\
			executionstatus=None,\
			executiontype=None,\
			**params
		):
		"""Returns testcases specified by parameters
		@param params: Params for TestCase
		@type params: mixed
		@returns: Matching TestCases
		@rtype: mixed
		"""
		# Get all available TestCases
		# Use all possible API params to speed up API call
		response = Testlink._api.getTestCasesForTestPlan(\
								self.id,\
								testcaseid,\
								buildid,\
								keywordid,\
								keywords,\
								executed,\
								assignedto,\
								executionstatus,\
								executiontype,\
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
		log.debug("Got %d testcases total" % len(testcases))

		# Check for every project if all other params
		# match and return this testcase
		matches = []

		# Remove None flagged additional params
		# Otherwise, there will be checks if the none string '' returned
		# by Testlink API matches the given None
		for key,value in params.items():
			if value is None:
				del params[key]

		# Check additional params
		if len(params)>0:
			log.debug("Checking for additional params: %s" % unicode(params))
			for case in testcases:
				match = True
				for key,value in params.items():
					if not(str(case[key]) == str(value)):
						match = False
						break
				if match:
					matches.append(TestCase(**case))
			log.debug("Got %d matching testcases" % len(matches))
			return matches
		else:
			return [TestCase(**case) for case in testcases]
						

class Build(TestlinkObject):
	"""Testlink Build representation
	@ivar notes: Build notes
	@type notes: str
	"""

	__slots__ = ("id","name","notes")

	def __init__(self,id=None,name=None,notes=None,**kwargs):
		TestlinkObject.__init__(self,id,name)
		self.notes = DefaultParser().feed(unicode(notes))


class Platform(TestlinkObject):
	"""Testlink Platform representation
	@ivar notes: Platform notes
	@type notes: str
	"""

	__slots__ = ("id","name","notes")

	def __init__(self,id=None,name=None,notes=None,**kwargs):
		TestlinkObject.__init__(self,id,name)
		self.notes = DefaultParser().feed(unicode(notes))


class TestSuite(TestlinkObject):
	"""Testlink TestSuite representation
	@ivar notes: TestSuite notes
	@type notes: str
	"""

	__slots__ = ("id","name","details","parent_id","__testproject_id")

	def __init__(self,id=-1,name="",details="",parent_id=-1,testproject_id=-1,**kwargs):
		TestlinkObject.__init__(self,id,name)
		self.details = DefaultParser().feed(unicode(details))
		self.parent_id = int(parent_id)
		self.__testproject_id = int(testproject_id)

	def getTestSuite(self,name=None,id=None,recursive=True,**params):
		"""Returns TestSuites speficied by parameters
		@param name: The name of the wanted TestSuite
		@type name: str
		@param recursive: Enable recursive search
		@type recursive: bool
		@param params: Other params for TestSuite
		@type params: dict
		@returns: Matching TestSuites
		@rtype: list
		"""
		# Check if simple API call can be done
		# Since the ID is unique, all other params
		# can be ignored
		if id:
			response = Testlink._api.getTestSuiteById(id)
			return [TestSuite(**response[0])]

		# Get all sub suites
		response = Testlink._api.getTestSuitesForTestSuite(self.id)

		# Normalize result
		if isinstance(response,str) and response.strip() == "":
			# Nothing more to do here
			return []
		elif isinstance(response,dict):
			# Check for nested dict
			if isinstance(response[response.keys()[0]],dict):
				response = [Testlink._api.getTestSuiteById(suite_id) for suite_id in response.keys()]
			else:
				response = [response]

		# Built TestSuite object here to simplify recursive calls
		sub_suites = [TestSuite(testproject_id=self.__testproject_id,**suite) for suite in response]

		result = []
		if len(params)>0 or name:
			search_params = copy.copy(params)
			search_params.update({'name':name})

			# Check for every testsuite if all params
			# match and return that testsuite
			matches = []
			for suite in response:
				match = True
				for key,value in search_params.items():
					if value and not (unicode(suite[key]) == unicode(value)):
						match = False
						break
				if match:
					matches.append(TestSuite(testproject_id=self.__testproject_id,**suite))
			# Add to results
			result.extend(matches)
		else:
			# Add all to results
			result.extend(sub_suites)

		# Add matches in nested testsuites recursively
		if recursive:
			for suite in sub_suites:
				result.extend(suite.getTestSuite(name,id,recursive,**params))
		return result



	def getTestCase(self,name=None,**params):
		"""Returns all TestCaes specified by parameters
		@param name: The name of the wanted TestCase
		@type name: str
		@param params: Other params for TestCase
		@type params: dict
		@returns: Matching TestCases
		@rtype: list
		"""
		# Get all sub testcases
		response = Testlink._api.getTestCasesForTestSuite(self.id,details='full')

		if len(params)>0 or name:
			# Add name to search params
			params['name'] = name

			log.debug(" * Search params: " + str(params))

			# Check for every testcase if all params
			# match and return that testcase
			matches = []
			for case in response:
				match = True
				for key,value in params.items():
					if value and not (unicode(case[key]) == unicode(value)):
						match = False
						break
				if match:
					matches.append(TestCase(**case))

			# Return results
			return matches
		else:
			# Return all available testcases
			return [TestCase(**case) for case in response]


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
	@ivar importance: Importance
	@type importance: Importance
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
			"platform_id","external_id")

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
			self.actions = SectionParser().feed(DefaultParser().feed(unicode(actions)))
			self.execution_type = int(execution_type)
			self.active = bool(active)
			self.results = SectionParser().feed(DefaultParser().feed(unicode(expected_results)))

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
			self.notes = DefaultParser().feed(unicode(notes))
			self.execution_type = int(execution_type)
			self.execution_ts = date.strptime(str(execution_ts),Execution.DATETIME_FORMAT)
			self.tester_id = int(tester_id)

		def delete(self):
			Testlink._api.deleteExecution(self.id)


	def __init__(
			self,\
			id=-1,\
			name="",\
			executed=False,\
			execution_notes="",\
			execution_order=-1,\
			version=0,\
			exec_status="",\
			status="",\
			importance=Importance.LOW,\
			execution_type=ExecutionType.MANUAL,\
			active=False,\
			summary="",\
			preconditions="",\
			platform_id=-1,\
			external_id=-1,\
			steps=[],\
			**kwargs\
		):
		TestlinkObject.__init__(self,id,name)
		self.executed = bool(executed)
		self.execution_notes = DefaultParser().feed(unicode(execution_notes))
		self.execution_order = int(execution_order)
		self.version = int(version)
		self.exec_status = unicode(exec_status)
		self.status = unicode(status)
		self.importance = int(importance)
		self.execution_type = int(execution_type)
		self.active = bool(active)
		self.summary = DefaultParser().feed(unicode(summary))
		self.platform_id = int(platform_id)
		self.external_id = int(external_id)

		# TestCase Steps
		self.steps = [TestCase.Step(**s) for s in steps]

		# TestCase Preconditions
		self.preconditions = ListParser().feed(DefaultParser().feed(unicode(preconditions)))

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
