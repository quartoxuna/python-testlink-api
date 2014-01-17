#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@author: Kai Borowiak
@summary: Object oriented Wrapper for Testlink
"""

# IMPORTS
import abc
import re
import xmlrpclib
from api import TestlinkAPI
from testlink import log


class Testlink(object):
	"""Testlink Server implementation
	@ivar devkey: Valid Testlink developer key
	@type devkey: str
	"""

	def __init__(self,uri,devkey):
		"""Initializes the Testlink Server object
		@param uri: Testlink URL
		@type uri: str
		@param devkey: Testlink developer key
		@type devkey: str
		@param short_uri: If enabled, just path to Testlink directory is needed, else whole path to api (Default: True)
		@type short_uri: bool
		@raise InvalidURI: The given URI is not valid
		"""
		self.api = TestlinkAPI(uri)
		self.api.devkey = str(devkey)

	def getVersion(self):
		"""Retrieve informations about the used Testlink API
		@return: Version in list format [x,y,z]
		@rtype: list
		"""
		about_str = self.api.about()
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
		"""Returns TestProject specified by parameters"""
		if name:
			resp = self.api.getTestProjectByName(name)
			if isinstance(resp,list) and len(resp)==1:
				resp=resp[0]
			return TestProject(api=self.api,**resp)
	
		projects = self.getProjects(self.devkey)
		if len(params)>0:
			# Search by params
			for key,value in params.items():
				for p in projects:
					if p[key]==value:
						return TestProject(api=self.api,**p)
		else:
			return [TestProject(api=self.api,**p) for p in projects]


class TestlinkObject:
	"""Abstract Testlink Object
	@ivar api: TestlinkAPI instance
	@type api: testlink.api.TestlinkAPI
	@ivar Id: Internal Testlink Id of the object
	@type Id: int
	@ivar name: Internal Testlink name of the object
	@type name: str
	"""

	__metaclass__ = abc.ABCMeta

	def __init__(self,api,id,name,parent=None):
		"""Initialises base Testlink object
		@param api: TestlinkAPI instance
		@type api: testlink.api.TestlinkAPI
		@param Id: Internal Testlink Id of the object
		@type Id: int
		@param name: Internal Testlink name of the object
		@type name: str
		@keyword kwargs: Additonal attributes
		"""
		self.api = api
		self.id = int(id)
		self.name = str(name)
		self.parent = parent


class TestProject(TestlinkObject):
	"""Testlink TestProject representation
	Additional members to TestlinkObject
	@ivar notes: TestProject notes
	@type notes: str
	@ivar prefix: TestCase prefix within TestProject
	@str prefix: str
	@ivar active: TestProject active flag
	@type active: bool
	@ivar public: TestProject public flag
	@type public: bool
	@ivar requirements: Requirement Feature flag
	@type requirements: bool
	@ivar priority: Test Priority feature flag
	@type priority: bool
	@ivar automation: Automation Feature flag
	@type automation: bool
	@ivar inventory: Inventory Feature flag
	@type inventory: bool
	@ivar tc_count: Current amount of TestCases in TestProject
	@type tc_count: int
	@ivar color: Assigned color of TestProject
	@type color: str"""

	def __init__(self,api,id,name,notes,prefix,active,is_public,tc_counter,opt,color,**kwargs):
		super(TestProject,self).__init__(api,id,name)
		self.notes = str(notes)
		self.prefix = str(prefix)
		self.is_active = bool(active)
		self.is_public = bool(is_public)
		self.requirements = bool(opt['requirementsEnabled'])
		self.priority = bool(opt['testPriorityEnabled'])
		self.automation = bool(opt['automationEnabled'])
		self.inventory = bool(opt['inventoryEnabled'])
		self.tc_count = int(tc_counter)
		self.color = str(color)


	def getTestPlan(self,name=None,**params):
		"""Returns TestPlans specified by parameters"""
		if name:
			# Search by Name
			resp = self.api.getTestPlanByName(self.api.devkey,name,self.name)
			if isinstance(resp,list) and len(resp)==1:
				resp=resp[0]
			return TestPlan(api=self.api,parent=self,**resp)

		plans = self.api.getProjectTestPlans(self.api.devkey,self.id)
		if len(params)>0:
			# Search by params
			for key,value in params.items():
				for p in plans:
					if p[key]==value:
						return TestPlan(api=self.api,parent=self,**p)
		else:
			return [TestPlan(api=self.api,parent=self,**p) for p in plans]

	def getTestSuite(self,name=None,**params):
		"""Returns TestSuites specified by parameters"""
		if 'id' in params:
			# Search by ID
			resp = self.api.getTestSuiteById(self.api.devkey,id)
			if isinstance(resp,list) and len(resp)==1:
				resp=resp[0]
			return TestSuite(api=self.api,parent=self,**resp)
		
		suites = self.api.getFirstLevelTestSuitesForTestProject(self.api.devkey,self.id)
		if len(params)>0:
			# Search by params
			for key,value in params.items():
				for s in suites:
					if s[key]==value:
						return TestSuite(api=self.api,parent=self,**s)
		else:
			return [TestSuite(api=self.api,parent=self,**s) for s in suites]


class TestPlan(TestlinkObject):
	"""Testlink TestPlan representation"""

	def __init__(self,api,id,name,notes,is_public,is_open,active,**kwargs):
		super(TestPlan,self).__init__(api,id,name)
		self.notes = str(notes)
		self.is_open = bool(is_open)
		self.is_active = bool(active)
		self.is_public = bool(is_public)
		
	def getBuild(self,name=None,**params):
		"""Returns Builds specified by parameters"""
		builds = self.api.getBuildsForTestPlan(self.api.devkey,self.id)
		if len(params)>0:
			for key,value in params.items():
				for b in builds:
					if b[key]==value: return Build(api=self.api,parent=self,**b)
		else: return [Build(api=self.api,parent=self,**b) for b in builds]

	def getPlatform(self,name=None,**params):
		"""Returns platforms specified by parameters"""
		platforms = self.api.getTestPlanPlatforms(self.api.devkey,self.id)
		if len(params)>0:
			for key,value in params.items():
				for p in platforms:
					if p[key]==value: return Platform(api=self.api,parent=self,**p)
		else: return [Platform(api=self.api,parent=self,**p)]
		
	def getTestSuite(self,name=None,**params):
		"""Return TestSuites specified by parameters"""
		suites = self.api.getTestSuitesForTestPlan(self.api.devkey,self.id)
		if len(params)>0:
			for key,value in params.items():
				for s in suites:
					if s[key]==value: return TestSuite(api=self.api,parent=self,**s)
		else: return [TestSuite(api=self.api,parent=self,**s) for s in suites]

	def getTestCase(self,name=None,**params):
		cases = self.api.getTestCasesForTestPlan(self.api.devkey,self.id)
		if len(params)>0:
			for key,value in params.items():
				for c in cases:
					if c[key]==value: return TestCase(api=self.api,parent=self,**c)
		else: return [TestCase(api=self.api,parent=self,**c) for c in cases]


class Build(TestlinkObject):
	"""Testlink Build representation"""

	def __init__(self,api,id,name,notes):
		super(Build,self).__init__(api,id,name)
		self.notes = str(notes)


class Platform(TestlinkObject):
	"""Testlink Platform representation"""

	def __init__(self,api,id,name,notes):
		super(Platform,self).__init__(api,id,name)
		self.notes = str(notes)


class TestSuite(TestlinkObject):
	"""Testlink TestSuite representation"""

	def __init__(self,api,id,name,notes,**kwargs):
		super(TestSuite,self).__init__(api,id,name)
		self.notes = str(notes)

	def getTestSuite(self,name=None,**params):
		suites = self.api.getTestSuitesForTestSuite(self.api.devkey,self.id)
		if len(params)>0:
			for key,value in params.items():
				for s in suites:
					if s[key]==value: return TestSuite(api=self.api,parent=self,**s)
		else: return [TestSuite(api=self.api,parent=self,**s) for s in suites]

	def getTestCase(self,name=None,**params):
		cases = self.api.getTestCasesForTestSuite(self.api.devkey,self.id,details='full')
		if len(params)>0:
			for key,value in params.items():
				for c in cases:
					if c[key]==value: return TestCase(api=self.api,parent=self,**c)
		else: return [TestCase(api=self.api,parent=self,**c) for c in cases]

class TestCase(TestlinkObject):
	"""Testlink TestCase representation"""

	def __init__(self,api,id,name,notes,**kwargs):
		super(TestCase,self).__init__(api,id,name)
		self.notes = str(notes)
