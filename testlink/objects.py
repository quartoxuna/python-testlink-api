#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@author: Kai Borowiak
@summary: Object oriented Wrapper for Testlink
"""

# IMPORTS
import re
import copy
from datetime import datetime
from distutils.version import LooseVersion as Version

from log import log
from api import Testlink_XML_RPC_API
from exceptions import ConnectionError
from exceptions import NotSupported
from enums import APIType
from enums import DuplicateStrategy
from enums import ImportanceLevel
from enums import ExecutionType
from enums import CustomFieldDetails

# Global datetime format
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"

# Helper method
def normalize(res):
	"""Normalizes a result list.
	If the specified list is empty, return None.
	If the specified list has only one element, return that element.
	Else return the list as is.
	@param res: Result list
	@type res: list
	@rtype: mixed
	"""
	if len(res)==0:
		return None
	elif len(res)==1:
		return res[0]
	else:
		return res

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
		# Init raw API
		if api == APIType.XML_RPC:
			self._api = Testlink_XML_RPC_API(url)
		elif api == APIType.REST:
			raise NotImplementedError()
		self._api_type = api

		# Log API Information
		log.info("Testlink %s API Version '%s' at '%s'" % (self._api_type,self.getVersion(),url) )

		# Set devkey globally
		self._api._devkey = devkey

	def getVersion(self):
		"""Retrieve informations about the used Testlink API
		@return: Version struct
		@rtype: distutils.version.LooseVersion
		"""
		# Check for easy API call
		return self._api._tl_version

	def iterTestProject(self,name=None,**params):
		"""Iterates over TestProjects specified by parameters
		@param name: The name of the TestProject
		@type name: str
		@param params: Other params for TestProject
		@type params: dict
		@returns: Matching TestProjects
		@rtype: generator
		"""
		# Check if simple API call can be done
		if name and len(params)==0:
			response = self._api.getTestProjectByName(name)

			# Since Testlink 1.9.6, the server returns already a dict
			# before, there was a list containing a dict
			# The getVersion() method still returns 1.0 in that case
			# so we have to check by trial and error
			try:
				response = response[0]
			except KeyError:
				pass
			yield TestProject(api=self._api,**response)

		else:
			# Filter by specified parameters
			response = self._api.getProjects()
			if len(params)>0:
				params['name'] = name
				for project in copy.copy(response):
					for key,value in params.items():
						if not (unicode(project[key]) == unicode(value)):
							response.remove(project)
							break
			for project in response:
				yield TestProject(api=self._api,**project)

	def getTestProject(self,name=None,**params):
		"""Returns all TestProjects specified by parameters
		@param name: The name of the TestProject
		@type name: str
		@param params: Other params for TestProject
		@type params: dict
		@returns: Matching TestProjects
		@rtype: mixed
		"""
		return normalize( [p for p in self.iterTestProject(name,**params)] )

	def create(self,obj,*args,**kwargs):
		"""Create a new object using the current connected Testlink.
		@param obj: Object to create
		@type obj: mixed
		@param args: Additional arguments for object creation
		@type args: list
		@param kwargs: Additional arguments for object creation
		@type kwargs: dict
		@raises TypeError: Unknown object type
		"""
		# Dispatch creation calls
		if isinstance(obj,TestProject):
			return TestProject.create(self,obj,*args,**kwargs)
		elif isinstance(obj,TestSuite):
			return TestSuite.create(self,obj,*args,**kwargs)
		elif isinstance(obj,TestCase):
			return TestCase.create(self,obj,*args,**kwargs)
		else:
			raise TypeError(str(obj))


class TestlinkObject(object):
	"""Abstract Testlink Object
	@ivar id: Internal Testlink Id of the object
	@type id: int
	@ivar name: Internal Testlink name of the object
	@type name: str
	"""

	__slots__ = ("id","name","_api")

	def __init__(self,id=None,name="",api=None):
		"""Initialises base Testlink object
		@param id: Internal Testlink Id of the object
		@type id: int
		@param name: Internal Testlink name of the object
		@type name: str
		@keyword kwargs: Additonal attributes
		"""
		if id is not None:
			self.id = int(id)
		else:
			self.id = id
		self.name = name
		self._api = api

	def __str__(self):
		return str(self.name)

	def __unicode__(self):
		return unicode(self.name)

	def __repr__(self):
		return self.__unicode__()

	def __eq__(self,other):
		return self.id == other.id

	def getTestlink(self,*args,**kwargs):
		raise NotImplementedError()

	def iterTestProject(self,*args,**kwargs):
		raise NotImplementedError()

	def getTestProject(self,*args,**kwargs):
		return normalize( [p for p in self.iterTestProject(*args,**kwargs)] )

	def iterTestPlan(self,*args,**kwargs):
		raise NotImplementedError()

	def getTestPlan(self,*args,**kwargs):
		return normalize( [p for p in self.iterTestPlan(*args,**kwargs)] )

	def iterBuild(self,*args,**kwargs):
		raise NotImplementedError()

	def getBuild(self,*args,**kwargs):
		return normalize( [b for b in self.iterBuild(*args,**kwargs)] )

	def iterPlatform(self,*args,**kwargs):
		raise NotImplementedError()

	def getPlatform(self,*args,**kwargs):
		return normalize( [p for p in self.iterPlatform(*args,**kwargs)] )

	def iterTestSuite(self,*args,**kwargs):
		raise NotImplementedError()

	def getTestSuite(self,*args,**kwargs):
		return normalize( [s for s in self.iterTestSuite(*args,**kwargs)] )

	def iterTestCase(self,*args,**kwargs):
		raise NotImplementedError()

	def getTestCase(self,*args,**kwargs):
		return normalize( [c for c in self.iterTestCase(*args,**kwargs)] )


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
	@ivar tc_counter: Current amount of TestCases in TestProject
	@type tc_counter: int
	@ivar color: Assigned color of TestProject
	@type color: str"""

	__slots__ = ("notes","prefix","active","public","requirements",\
			"priority","automation","inventory","tc_counter","color")

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
			api=None,\
			**kwargs\
		):
		TestlinkObject.__init__(self,id,name,api)
		self.notes = notes
		self.prefix = prefix
		self.active = bool(active)
		self.public = bool(is_public)
		self.requirements = bool(opt['requirementsEnabled'])
		self.priority = bool(opt['testPriorityEnabled'])
		self.automation = bool(opt['automationEnabled'])
		self.inventory = bool(opt['inventoryEnabled'])
		self.tc_counter = int(tc_counter)
		self.color = color

	def iterTestPlan(self,name=None,**params):
		"""Iterates over TestPlans specified by parameters
		@param name: The name of the TestPlan
		@type name: str
		@param params: Other params for TestPlan
		@type params: dict
		@returns: Matching TestPlans
		@rtype: generator
		"""
		# Check if simple API call can be done
		if name and len(params)==0:
			response = self._api.getTestPlanByName(name,projectname=self.name)
			yield TestPlan(api=self._api,parent_testproject=self,**response[0])
		else:
			# Filter by specified parameters
			response = self._api.getProjectTestPlans(self.id)
			if len(params)>0:
				params['name'] = name
				for plan in copy.copy(response):
					for key,value in params.items():
						if not (unicode(plan[key]) == unicode(value)):
							response.remove(plan)
							break
			for plan in response:
				yield TestPlan(api=self._api,parent_testproject=self,**plan)

	def getTestPlan(self,name=None,**params):
		"""Returns all TestPlans specified by parameters
		@param name: The name of the TestPlan
		@type name: str
		@param params: Other params for TestPlan
		@type params: dict
		@returns: Matching TestPlans
		@rtype: mixed
		"""
		return normalize( [p for p in self.iterTestPlan(name,**params)] )

	def iterTestSuite(self,name=None,id=None,recursive=True,**params):
		"""Iterates over TestSuites specified by parameters
		@param name: The name of the wanted TestSuite
		@type name: str
		@param id: The internal ID of the TestSuite
		@type id: int
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
			response = self._api.getTestSuiteById(id)
			yield TestSuite(api=self._api,**response)
		else:
			# Filter by specified parameters
			response = self._api.getFirstLevelTestSuitesForTestProject(self.id)

			# Bug !
			# Since the API call to getFirstLevelTestSuites does NOT
			# return the details, we have to get it with another API call
			# This has to be done BEFORE the acutal filtering because otherwise
			# we could not filter by the details
			response = [self._api.getTestSuiteById(suite['id']) for suite in response]

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
			first_level_suites = [TestSuite(api=self._api,parent_testproject=self,**suite) for suite in response]
			for suite in first_level_suites:
				yield suite
			# Recursively search in sub suites
			for suite in first_level_suites:
				for s in suite.getTestSuite(**params):
					yield s

	def getTestSuite(self,name=None,id=None,recursive=True,**params):
		"""Returns all TestSuites specified by parameters
		@param name: The name of the wanted TestSuite
		@type name: str
		@param id: The internal ID of the TestSuite
		@type id: int
		@param recursive: Enable recursive search
		@type recursive: bool
		@param params: Other params for TestSuite
		@type params: dict
		@returns: Matching TestSuites
		@rtype: mixed
		"""
		return normalize( [s for s in self.iterTestSuite(self,name,id,recursive,**params)] )

	def iterTestCase(self,name=None,id=None,external_id=None,recursive=True,**params):
		"""Iterates over TestCases specified by parameters
		@param name: The name of the wanted TestCase
		@type name: str
		@param id: The internal ID of the TestCase
		@type id: int
		@param external_id: The external ID of the TestCase
		@type external_id: int
		@param recursive: Enable recursive search
		@type recursive: bool
		@param params: Other params for TestCase
		@type params: dict
		@returns: Matching TestCases
		@rtype: generator
		"""
		# Check if simple API calls can be done
		# Since the ID is unique, try to get it in any case
		if name and not id:
			response = self._api.getTestCaseIdByName(name,project=self.name)
			# If we got more than one TestCase, ignore the name
			if len(response)==1:
				id = response[0]['id']

		# If we have the id or external id, try to get the testcase by that
		if id or external_id:
			if external_id:
				ext = "%s-%s" % (str(self.prefix),str(external_id))
			else:
				ext = None
			response = self._api.getTestCase(id,ext)
			# Server response is a list
			if len(response)==1:
				response = response[0]

			# Need to get testsuite to set as parent

			suite_resp = self._api.getTestSuiteById(response['testsuite_id'])
			suite = TestSuite(**suite_resp)

			yield TestCase(api=self._api,parent_testproject=self,parent_testsuite=suite,**response)
		else:
			# Get all TestCases for the TestProject
			raise NotImplementedError("Cannot get all TestCases for a TestProject yet")

	def getTestCase(self,name=None,id=None,external_id=None,recursive=True,**params):
		"""Returns all TestCases specified by parameters
		@param name: The name of the wanted TestCase
		@type name: str
		@param id: The internal ID of the TestCase
		@type id: int
		@param external_id: The external ID of the TestCase
		@type external_id: int
		@param recursive: Enable recursive search
		@type recursive: bool
		@param params: Other params for TestCase
		@type params: dict
		@returns: Matching TestCases
		@rtype: mixed
		"""
		return normalize( [c for c in self.iterTestCase(name,id,external_id,recursive,**params)] )

	def iterRequirementSpecification(self,title=None,**params):
		"""Iterates over Requirement Specifications specified by parameters
		@param title: The title of the wanted Requirement Specification
		@type title: str
		@returns: Matching Requirement Specifications
		@rtype: generator
		"""
		# No simple API call possible, get all
		response = self._api.getRequirementSpecificationsForTestProject(self.id)

		# Filter by speficied params
		if len(params)>0 or title:
			params['title'] = title
			for reqspec in copy.copy(response):
				for key,value in params.items():
					if value and not (unicode(reqspec[key]) == unicode(value)):
						response.remove(reqspec)
						break
		for reqspec in response:
			yield RequirementSpecification(api=self._api,name=title,parent_testproject=self,**reqspec)

	def getRequirementSpecification(self,title=None,**params):
		"""Returns all Requirement Specifications specified by parameters
		@param title: The title of the wanted Requirement Specification
		@type title: str
		@returns: Matching Requirement Specifications
		@rtype: list
		"""
		return normalize( [r for r in self.iterRequirementSpecification(title,**params)] )

	@staticmethod
	def create(tl,project,*args,**kwargs):
		"""Creates the specified TestProject for the specified Testlink instance.
		@param tl: Used Testlink instance
		@type tl: Testlink
		@param project: Used TestProject
		@type project: TestProject
		"""
		return tl._api.createTestProject(
					name = project.name,
					prefix = project.prefix,
					notes = project.notes,
					active = project.active,
					public = project.public,
					requirements = project.requirements,
					priority = project.priority,
					automation = project.automation,
					inventory = project.inventory
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

	__slots__ = ("notes","active","public","_parent_testproject")

	def __init__(
			self,\
			id=-1,\
			name="",\
			notes="",\
			is_public=False,\
			active=False,\
			parent_testproject=None,\
			api=None,\
			**kwargs
		):
		TestlinkObject.__init__(self,id,name,api)
		self.notes = notes
		self.active = bool(active)
		self.public = bool(is_public)
		self._parent_testproject = parent_testproject
	
	def iterTestProject(self,*args,**kwargs):
		yield self._parent_testproject

	def iterBuild(self,name=None,**params):
		"""Iterates over Builds specified by parameters
		@param name: The name of the Build
		@type name: str
		@param params: Other params for Build
		@type params: dict
		@returns: Macthing Builds
		@rtype: generator
		"""
		# No simple API call possible, get all
		response = self._api.getBuildsForTestPlan(self.id)

		# Filter by specified params
		if len(params)>0 or name:
			params['name'] = name
			for build in copy.copy(response):
				for key,value in params.items():
					if value and not (unicode(build[key]) == unicode(value)):
						response.remove(build)
						break
		for build in response:
			yield Build(api=self._api,**build)

	def getBuild(self,name=None,**params):
		"""Returns all Builds specified by parameters
		@param name: The name of the Build
		@type name: str
		@param params: Other params for Build
		@type params: dict
		@returns: Macthing Builds
		@rtype: mixed
		"""
		return normalize( [b for b in self.iterBuild(name,**params)] )

	def iterPlatform(self,name=None,**params):
		"""Iterates over Platforms specified by parameters
		@param name: The name of the Platform
		@type name: str
		@param params: Other params for Platform
		@type params: dict
		@returns: Matching Platforms
		@rtype: generator
		"""
		# No simple API call possible, get all
		response = self._api.getTestPlanPlatforms(self.id)

		# Filter by specified params
		if len(params)>0 or name:
			params['name'] = name
			for platform in copy.copy(response):
				for key,value in params.items():
					if value and not (unicode(platform[key]) == unicode(value)):
						response.remove(platform)
						break
		for platform in response:
			yield Platform(api=self._api,**platform)

	def getPlatform(self,name=None,**params):
		"""Returns all Platforms specified by parameters
		@param name: The name of the Platform
		@type name: str
		@param params: Other params for Platform
		@type params: dict
		@returns: Matching Platforms
		@rtype: mixed
		"""
		return normalize( [p for p in self.iterPlatform(name,**params)] )

	def iterTestCase(
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
		"""Iterates over Testcases specified by parameters
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
		response = self._api.getTestCasesForTestPlan(\
								self.id,\
								id,\
								buildid,\
								keywordid,\
								keywords,\
								executed,\
								assigned_to,\
								execution_status,\
								execution_type,\
								getstepsinfo = True\
							)

		# Check for empty response
		if (response is None) or len(response)==0:
			return

		# Normalize result
		testcases = []
		for tcid,platforms in response.items():
			if isinstance(platforms,list):
				# No platforms, first nested items are testcases as list
				log.debug("No Platforms within this testplan")
				for tc in platforms:
					testcases.append(tc)
			else:
				for platform_id,tc in platforms.items():
					testcases.append(tc)

		# Filter by specified params
		if len(params)>0 or name:
			params['name'] = name
			for case in copy.copy(testcases):
				# Create a testcase instance here
				# to have normalized attributes
				tcase = TestCase(api=self._api,parent_testproject=self.getTestProject(),**case)
				for key,value in params.items():
					try:
						if value and not (unicode(getattr(tcase,key)) == unicode(value)):
							# Testcase does not match
							tcase = None
							break
					except AttributeError:
						# TestCase has no attribute key
						# Try to treat key as the name of a custom field
						ext_id = "%s-%s" % (tcase.getTestProject().prefix,tcase.external_id)
						cf_val = self._api.getTestCaseCustomFieldDesignValue(ext_id,tcase.version,tcase.getTestProject().id,key)
						if ( \
							(cf_val is None) or \
							( value and not(unicode(cf_val) == unicode(value)) ) \
						):
							# No match either, try next testcase
							tcase = None
							break
				# Yield matching testcase
				if tcase is not None:
					yield tcase

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
		"""Returns all Testcases specified by parameters
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
		@rtype: mixed
		"""
		return normalize( [c for c in self.iterTestCase(name,id,buildid,keywordid,keywords,executed,assigned_to,execution_status,execution_type,**params)] )

	def assignTestCase(self, case, platform=None, execution_order=None, urgency=None):
		"""Assigns the specified TestCase to the current TestPlan.
		@param case: TestCase to add to current TestPlan
		@type case: TestCase
		@param platform: <OPTIONAL> Platform to add to
		@type platform: Platform
		@param execution_order: <OPTIONAL> Desired execution order
		@type execution_order: int
		@param urgency: <OPTIONAL> Desired urgency
		@type urgency: enums.UrgencyLevel
		@raises APIError: Could not add TestCase
		"""
		if not platform:
			platform = Platform(-1)
		self._api.addTestCaseToTestPlan(self.getTestProject().id,self.id,"%s-%s" % (self.getTestProject().prefix,str(case.external_id)),case.version,platform.id,execution_order,urgency)

class Build(TestlinkObject):
	"""Testlink Build representation
	@ivar notes: Build notes
	@type notes: str
	"""

	__slots__ = ("notes")

	def __init__(self,id=None,name=None,notes=None,api=None,**kwargs):
		TestlinkObject.__init__(self,id,name,api)
		self.notes = notes


class Platform(TestlinkObject):
	"""Testlink Platform representation
	@ivar notes: Platform notes
	@type notes: str
	"""

	__slots__ = ("notes")

	def __init__(self,id=None,name=None,notes=None,api=None,**kwargs):
		TestlinkObject.__init__(self,id,name,api)
		self.notes = notes


class TestSuite(TestlinkObject):
	"""Testlink TestSuite representation
	@ivar notes: TestSuite notes
	@type notes: str
	"""

	__slots__ = ("details","_parent_testproject","_parent_testsuite")

	def __init__(self,id=-1,name="",details="",parent_testproject=None,parent_testsuite=None,api=None,**kwargs):
		TestlinkObject.__init__(self,id,name,api)
		self.details = details
		self._parent_testproject = parent_testproject
		self._parent_testsuite = parent_testsuite

	def iterTestProject(self,*args,**kwargs):
		yield self._parent_testproject

	def iterTestSuite(self):
		yield self._parent_testsuite

	def iterTestSuite(self,name=None,id=None,**params):
		"""Iterates over TestSuites speficied by parameters
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
		response = self._api.getTestSuitesForTestSuite(self.id)

		# Normalize result
		if isinstance(response,str) and response.strip() == "":
			response = []
		elif isinstance(response,dict):
			# Check for nested dict
			if isinstance(response[response.keys()[0]],dict):
				response = [self._api.getTestSuiteById(suite_id) for suite_id in response.keys()]
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
		sub_suites = [TestSuite(api=self._api,parent_testproject=self.getTestProject(),parent_testsuite=self,**suite) for suite in response]
		for suite in sub_suites:
			yield suite
		# Recursively search in sub suites
		for suite in sub_suites:
			for s in suite.getTestSuite(**params):
				yield s

	def getTestSuite(self,name=None,id=None,**params):
		"""Returns all TestSuites speficied by parameters
		@param name: The name of the wanted TestSuite
		@type name: str
		@param params: Other params for TestSuite
		@type params: dict
		@returns: Matching TestSuites
		@rtype: mixed
		"""
		return normalize( [s for s in self.iterTestSuite(name,id,**params)] )

	def iterTestCase(self,name=None,**params):
		"""Iterates over TestCases specified by parameters
		@param name: The name of the wanted TestCase
		@type name: str
		@param params: Other params for TestCase
		@type params: dict
		@returns: Matching TestCases
		@rtype: generator
		"""
		# No simple API call possible, get all
		response = self._api.getTestCasesForTestSuite(self.id,details='full')

		# Filter by specified parameters
		if len(params)>0 or name:
			params['name'] = name
			for case in copy.copy(response):
				for key,value in params.items():
					if value and not (unicode(case[key]) == unicode(value)):
						response.remove(case)
						break
		for case in response:
			yield TestCase(api=self._api,parent_testproject=self.getTestProject(),parent_testsuite=self,**case)

	def getTestCase(self,name=None,**params):
		"""Returns all TestCases specified by parameters
		@param name: The name of the wanted TestCase
		@type name: str
		@param params: Other params for TestCase
		@type params: dict
		@returns: Matching TestCases
		@rtype: mixed
		"""
		return normalize( [c for c in self.iterTestCase(name,**params)] )

	@staticmethod
	def create(tl,suite,order=0,on_duplicate=DuplicateStrategy.BLOCK):
		"""Creates the specified TestSuite for the specified Testlink instance.
		@param tl: Used Testlink instance
		@type tl: Testlink
		@param project: Used TestProject
		@type project: TestProject
		"""
		kwargs = {
				'name' : suite.name,
				'testprojectid' : suite.getTestProject().id,
				'details' : suite.details,
				'order' : order,
				'actiononduplicate' : on_duplicate,
				'parentid' : None
		}

		if suite.getTestSuite() is not None:
			kwargs['parentid'] = suite.getTestSuite().id

		response = tl._api.createTestSuite(**kwargs)

		if isinstance(response,list) and len(response)==1:
			response = response[0]

		return response



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

	@note: No __slots__ defined, so __dict__ available
	"""

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
		def __init__(
				self,\
				step_number=1,\
				actions="",\
				execution_type=ExecutionType.MANUAL,\
				active=False,\
				id=None,\
				expected_results="",\
				**kwargs\
			):
			if id is not None:
				self.id = int(id)
			else:
				self.id = id
			self.step_number = int(step_number)
			self.actions = actions
			self.execution_type = int(execution_type)
			self.active = bool(active)
			self.expected_results = expected_results

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
				execution_ts=str(datetime.min),\
				tester_id=-1,\
				**kwargs\
			):
			self.id = int(id)
			self.testplan_id = int(testplan_id)
			self.platform_id = int(platform_id)
			self.build_id = int(build_id)
			self.tcversion_id = int(tcversion_id)
			self.tcversion_number = int(tcversion_number)
			self.status = status
			self.notes = notes
			self.execution_type = int(execution_type)
			try:
				self.execution_ts = datetime.strptime(str(execution_ts),DATETIME_FORMAT)
			except ValueError:
				self.execution_ts = datetime.min
			self.tester_id = int(tester_id)

		def delete(self):
			self._api.deleteExecution(self.id)

	def __init__(
			self,
			version=1,
			status=None,
			importance=ImportanceLevel.MEDIUM,
			execution_type=ExecutionType.MANUAL,
			preconditions="",
			summary="",
			active=True,
			steps=[],
			api=None,
			parent_testproject=None,
			parent_testsuite=None,
			customfields={},
			**kwargs
			):
		"""Initialises a new TestCase with the specified parameters.
		@param name: The name of the TestCase
		@type name: str
		@param version: The version of the TestCase
		@type version: int
		@param status: The status of the TestCase
		@type status: int
		@param importance: The importance of the TestCase
		@type importance: int
		@param execution_type: The execution type of the TestCase
		@type execution_type: int
		@param preconditions: The preconditions for the TestCase
		@type preconditions: str
		@param summary: The summary of the TestCase
		@type summary: str
		@param active: Indicator for active TestCase version
		@type active: bool

		@param parent_testproject: The parent TestProject of the TestCase
		@type parent_testproject: TestProject
		@param parent_testsuite: The parent TestSuite of the TestCase
		@type parent_testsuite: TestSuite
		@param customfields: Custom Fields defined for this TestCase
		@type customfields: dict

		@note: All other attributes depend on the called API method
		-------------------------------------------------------------------------------------------
		| getTestCaseForTestSuite()   | getTestCase()               | getTestCasesForTestPlan()   |
		|	                      |                             |                             |
		|  node_order                 |  node_order                 |                             |
		|  is_open                    |  is_open                    |                             |
		|  id # Testcase ID           |  id  # Version ID           |                             |
		|                             |  testcase_id # Testcase ID  |                             |
		|  node_type_id               |                             |                             |
		|  layout                     |  layout                     |                             |
		|  tc_external_id             |  tc_external_id             |                             |
		|                             |                             |  external_id                |
		|  parent_id                  |                             |                             |
		|  version                    |  version                    |  version                    |
		|  details                    |                             |                             |
		|  updater_id                 |  updater_id                 |                             |
		|  status                     |  status                     |  status                     |
		|  importance                 |  importance                 |  importance                 |
		|                             |                             |  urgency                    |
		|                             |                             |  priority                   |
		|  modification_ts            |  modification_ts            |                             |
		|  execution_type             |  execution_type             |  execution_type             |
		|  preconditions              |  preconditions              |  preconditions              |
		|  active                     |  active                     |  active                     |
		|  creation_ts                |  creation_ts                |                             |
		|  node_table                 |                             |                             |
		|  tcversion_id # Version ID  |                             |                             |
		|  name                       |  name                       |  name                       |
		|  summary                    |  summary                    |  summary                    |
		|                             |  steps                      |  steps                      |
		|  author_id                  |  author_id                  |                             |
		|                             |  author_login               |                             |
		|                             |  author_first_name          |                             |
		|                             |  author_last_name           |                             |
		|                             |  updater_login              |                             |
		|                             |  updater_first_name         |                             |
		|                             |  updater_last_name          |                             |
		|                             |  testsuite_id               |  testsuite_id               |
		|                             |                             |  exec_id                    |
		|                             |                             |  executed                   |
		|                             |                             |  execution_notes            |
		|                             |                             |  execution_ts               |
		|                             |                             |  tcversion_number           |
		|                             |                             |  tc_id # Testcase ID        |
		|                             |                             |  assigner_id                |
		|                             |                             |  execution_order            |
		|                             |                             |  platform_name              |
		|                             |                             |  linked_ts                  |
		|                             |                             |  linked_by                  |
		|                             |                             |  tsuite_name                |
		|                             |                             |  assigned_build_id          |
		|                             |                             |  exec_on_tplan              |
		|                             |                             |  exec_on_build              |
		|                             |                             |  execution_run_type         |
		|                             |                             |  feature_id                 |
		|                             |                             |  exec_status                |
		|                             |                             |  user_id                    |
		|                             |                             |  tester_id                  |
		|                             |                             |  tcversion_id # Version ID  |
		|                             |                             |  type                       |
		|                             |                             |  platform_id                |
		===========================================================================================
		"""
		# Init
		TestlinkObject.__init__(self,api = api)

		# Get the "correct" id
		if ('id' in kwargs) and ('tcversion_id' in kwargs):
			# getTestCasesForTestSuite()
			self.id = kwargs['id']
			self.tc_version_id = kwargs['tcversion_id']
		elif ('id' in kwargs) and ('testcase_id' in kwargs):
			# getTestCase()
			self.id = kwargs['testcase_id']
			self.tc_version_id = kwargs['id']
		elif ('tc_id' in kwargs) and ('tcversion_id' in kwargs):
			# getTestCasesForTestPlan
			self.id = kwargs['tc_id']
			self.tc_version_id = kwargs['tcversion_id']

		# Get the "correct" name
		if ('name' in kwargs):
			self.name = kwargs['name']
		elif ('tcase_name' in kwargs):
			self.name = kwargs['tcase_name']

		# Set the "correct" external id
		if ('tc_external_id' in kwargs):
			self.external_id = kwargs['tc_external_id']
		elif ('external_id' in kwargs):
			self.external_id = kwargs['external_id']

		# Set uncommon, but necessary attributes
		if ('platform_id' in kwargs):
			self.platform_id = kwargs['platform_id']
		else:
			self.platform_id = None

		# Set exec status if available
		if ('exec_status' in kwargs):
			self.exec_status = kwargs['exec_status']
		else:
			self.exec_status = None

		# Set exec notes if available
		if ('execution_notes' in kwargs):
			self.execution_notes = kwargs['execution_notes']
		else:
			self.execution_notes = None

		# Set common attributes
		self.version = int(version)
		self.status = status
		self.importance = importance
		self.execution_type = execution_type
		self.preconditions = preconditions
		self.summary = summary
		self.active = active
		
		# Set internal attributes
		self._parent_testproject = parent_testproject
		self._parent_testsuite = parent_testsuite
		self.customfields = customfields

		# Set steps
		self.steps = []
		for s in steps:
			if isinstance(s,TestCase.Step):
				self.steps.append(s)
			else:
				self.steps.append(TestCase.Step(**s))

	def __unicode__(self):
		return "%s-%s %s" % (unicode(self.getTestProject().prefix),unicode(self.external_id),unicode(self.name))

	def __str__(self):
		return __unicode__(self)

	def iterTestProject(self,*args,**kwargs):
		yield self._parent_testproject

	def iterTestSuite(self,*args,**kwargs):
		yield self._parent_testsuite

	def getLastExecutionResult(self,testplanid,platformid=None,platformname=None,buildid=None,buildname=None,bugs=False):
		resp = self._api.getLastExecutionResult(testplanid,self.id,self.external_id,platformid,platformname,buildid,buildname,bugs)
		if isinstance(resp,list) and len(resp)==1:
			resp = resp[0]
		return TestCase.Execution(**resp)

	def deleteLastExecution(self,testplanid):
		# Update last execution
		last = self.getLastExecutionResult(testplanid)
		self._api.deleteExecution(last.id)

	def reportResult(self,testplanid,buildid,status,notes=None,overwrite=False):
		self._api.reportTCResult(
			testplanid = testplanid,\
			status = status,\
			testcaseid = self.id,\
			testcaseexternalid = self.external_id,\
			notes = notes,\
			platformid = self.platform_id,\
			overwrite = overwrite,\
			buildid = buildid\
		)

	def getAttachments(self):
		return self._api.getTestCaseAttachments(self.id,self.external_id)

	def getCustomFieldDesignValue(self,fieldname,details=CustomFieldDetails.VALUE_ONLY):
		"""Returns the custom field design value for the specified custom field
		@param fieldname: The internal name of the custom field
		@type fieldname: str
		@param details: Granularity of the response
		@type details: CustomFieldDetails
		@returns: Custom Field value or informations
		@rtype: mixed
		"""
		return self._api.getTestCaseCustomFieldDesignValue(
					testcaseexternalid = "%s-%s" % (str(self.getTestProject().prefix),str(self.external_id)),\
					version = int(self.version),\
					projectid = self.getTestProject().id,\
					fieldname = fieldname,\
					details = details\
				)

	def update(self,testcasename=None,summary=None,preconditions=None,steps=None,importance=None,executiontype=None,status=None,estimatedexecduration=None):
		"""Updates the the current TestCase.
		@param testcasename: The name of the TestCase
		@type testcasname: str
		@param summary: The summary of the TestCase
		@type summary: str
		@param preconditions: The Preconditions of the TestCase
		@type preconditions: str
		@param steps: The steps of the TestCase
		@type steps: list
		@param importance: The importance of the TestCase
		@type importance: enums.ImportanceLevel
		@param executiontype: The execution type of the TestCase
		@type executiontype: enums.ExecutionType
		@param status: The status of the TestCase
		@type status: enums.TestcaseStatus
		@param estimatedexecduration: The estimated execution time of the TestCase
		@type estimatedexecduration: int
		@returns: None
		"""

		if not testcasename:
			testcasename = self.name
		if not summary:
			summary = self.summary
		if not preconditions:
			preconditions = self.preconditions
		if not steps:
			steps = self.steps
		if not importance:
			importance = self.importance
		if not executiontype:
			executiontype = self.execution_type
		if not status:
			status = self.status

		self._api.updateTestCase(
				testcaseexternalid = "%s-%s" % (str(self.getTestProject().prefix),str(self.external_id)),\
				testcasename = testcasename,\
				summary = summary,\
				preconditions = preconditions,\
				steps = steps,\
				importance = importance,\
				executiontype = executiontype,\
				status = status,\
				estimatedexecduration = estimatedexecduration
			)

	@staticmethod
	def create(tl,case,order=0,on_duplicate=DuplicateStrategy.BLOCK):
		"""Creates the specified TestCase for the specified Testlink instance.
		@param tl: Used Testlink instance
		@type tl: Testlink
		@param case: Used TestCase
		@type case: TestCase
		"""
		response = tl._api.createTestCase(
						name = case.name,
						suiteid = case.getTestSuite().id,
						projectid = case.getTestProject().id,
						author = case.author,
						summary = case.summary,
						steps = case.steps,
						preconditions = case.preconditions,
						importance = case.importance,
						execution = case.execution_type,
						customfields = case.customfields,
						order = order,
						actiononduplicate = on_duplicate
					)
		# Normalize result
		if isinstance(response,list) and len(response)==1:
			response = response[0]
		return response

class RequirementSpecification(TestlinkObject):
	"""Testlink Requirement Specification representation"""

	__slots__ = ("doc_id","type","scope","testproject_id","author_id","creation_ts",\
			"modifier_id","modification_ts","total_req","node_order","_parent_testproject")

	def __init__(\
			self,\
			id = -1,\
			doc_id = '',\
			title = '',\
			type = None,\
			scope = '',\
			testproject_id = None,\
			author_id = None,\
			creation_ts = str(datetime.min),\
			modifier_id = None,\
			modification_ts = str(datetime.min),\
			total_req = 0,\
			node_order = 0,\
			api = None,\
			parent_testproject = None,\
			**kwargs\
			):
		"""Initializes a new Requirement Specification with the specified parameters.
		@todo: doc
		"""
		TestlinkObject.__init__(self,id,title,api)
		self.doc_id = str(doc_id)
		self.type = int(type)
		self.scope = scope
		self.testproject_id = int(testproject_id)
		self.author_id = int(author_id)
		try:
			self.modifier_id = int(modifier_id)
		except ValueError:
			self.modifier_id = -1
		self.total_req = int(total_req)
		self.node_order = int(node_order)
		try:
			self.creation_ts = datetime.strptime(str(creation_ts),DATETIME_FORMAT)
		except ValueError:
			self.creation_ts = datetime.min
		try:
			self.modification_ts = datetime.strptime(str(modification_ts),DATETIME_FORMAT)
		except ValueError:
			self.modification_ts = datetime.min
		self._parent_testproject = parent_testproject

	def iterTestProject(self,*args,**kwargs):
		yield self._parent_testproject

	def iterRequirement(self,title=None,**params):
		"""Iterates over Requirements specified by parameters
		@param title: The title of the wanted Requirement
		@type title: str
		@returns: Matching Requirements
		@rtype: generator
		"""
		# No Simple API Call possible, get all
		response = self._api.getRequirementsForRequirementSpecification(self.id,self.getTestProject().id)

		# Filter by specifiec params
		if len(params)>0 or title:
			params['title'] = title
			for req in copy.copy(response):
				for key,value in params.items():
					if value and not (unicode(req[key]) == unicode(value)):
						response.remove(req)
						break
		for req in response:
			yield Requirement(api=self._api,name=title,parent_testproject=self.getTestProject(),**req)

	def getRequirement(self,title=None,**params):
		"""Returns all Requirements with the specified parameters
		@param title: The title of the wanted Requirement
		@type title: str
		@returns: Matching Requirements
		@rtype: mixed
		"""
		return normalize( [r for r in self.iterRequirement(title,**params)] )

class Requirement(TestlinkObject):
	"""Testlink Requirement representation"""

	__slots__ = ("srs_id","req_doc_id","req_spec_title","type","version","version_id","revision","revision_id",\
			"scope","status","node_order","is_open","active","expected_coverage","testproject_id","author",\
			"author_id","creation_ts","modifier","modifier_id","modification_ts","_parent_testproject" )

	def __init__(\
			self,
			id = -1,\
			srs_id = None,\
			req_doc_id = '',\
			title = '',\
			req_spec_title = None,\
			type = None,\
			version = None,\
			version_id = None,\
			revision = None,\
			revision_id = None,\
			scope = '',\
			status = None,\
			node_order = 0,\
			is_open = True,\
			active = True,\
			expected_coverage = None,\
			testproject_id = -1,\
			author = None,\
			author_id = None,\
			creation_ts = str(datetime.min),\
			modifier = None,\
			modifier_id = None,\
			modification_ts = str(datetime.min),\
			api = None,\
			parent_testproject = None,\
			**kwargs\
			):
		"""Initializes a new Requirement with the specified parameters
		@todo: doc
		"""
		TestlinkObject.__init__(self,id,title,api)
		self.srs_id = str(srs_id)
		self.req_doc_id = str(req_doc_id)
		self.req_spec_title = req_spec_title
		self.type = int(type)
		self.version = int(version)
		self.version_id = int(version_id)
		self.revision = int(revision)
		self.revision_id = int(revision_id)
		self.scope = scope
		self.status = str(status)
		self.node_order = int(node_order)
		self.is_open = bool(is_open)
		self.active = bool(active)
		self.expected_coverage = int(expected_coverage)
		self.testproject_id = int(testproject_id)
		self.author = str(author)
		self.author_id = int(author_id)
		self.modifier = str(modifier)
		try:
			self.modifier_id = int(modifier_id)
		except ValueError:
			self.modifier_id = -1
		try:
			self.creation_ts = datetime.strptime(str(creation_ts),DATETIME_FORMAT)
		except ValueError:
			self.creation_ts = datetime.min
		try:
			self.modification_ts = datetime.strptime(str(modification_ts),DATETIME_FORMAT)
		except ValueError:
			self.modification_ts = datetime.min
		self._parent_testproject = parent_testproject

		def iterTestProject(self,*args,**kwargs):
			yield seld._parent_testproject
			
