#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@author: Kai Borowiak
@summary: Object oriented Wrapper for Testlink
"""

# IMPORTS
import re
import xmlrpclib
from HTMLParser import HTMLParser
from api import TestlinkAPI
from testlink import log
from testlink.parsers import DefaultParser


class Testlink(TestlinkAPI):
	"""Testlink Server implementation
	@ivar devkey: Valid Testlink developer key
	@type devkey: str
	"""

	def __init__(self,uri,devkey,parser=DefaultParser(),*parsers):
		"""Initializes the Testlink Server object
		@param uri: Testlink URL
		@type uri: str
		@param devkey: Testlink developer key
		@type devkey: str
		@raises InvalidURI: The given URI is not valid
		"""

		# Set active parsers
		parsers += (parser,)
		self.setParser(*parsers)
		log.debug("Active parsers: %s" % str(self.getParser()))

		# URI modification for API initiation
		self.__uri = uri
		if not uri.endswith('/lib/api/xmlrpc.php'):
			if not uri.endswith('/'):
				uri += '/'
			uri += 'lib/api/xmlrpc.php'

		# Init raw API
		super(Testlink,self).__init__(uri)		
		self.devkey = devkey

	def __str__(self):
		return "<Testlink@%s>" % self.__uri
	__repr__ = __str__


	def setParser(self,*parsers):
		"""Changes the set of active parsers
		@param parsers: Parsers to use
		@type parsers: Instances of HTMLParser
		"""
		self.__parsers = parsers	

	def getParser(self):
		"""Returns the current active parsers
		@rtype: list
		"""
		return self.__parsers

	def parse(self,data):
		"""Parses given data with all given parsers
		@param data: Data to parse
		@type data: mixed
		"""
		for p in self.__parsers:
			p.reset()
			p.feed(data)
			p.close()
			data = p.result
		return data


	def getVersion(self):
		"""Retrieve informations about the used Testlink API
		@return: Version in list format [x,y,z]
		@rtype: list
		"""
		about_str = self.about()
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
		@rtype: mixed
		"""
		# Check if simple API call can be done
		if name and len(params)==0:
			response = self.getTestProjectByName(name)
			return TestProject(self,**response)

		# Get all available Projects
		response = self.getProjects()

		if len(params)>0:
			# Add name to search parameters
			params['name'] = name
	
			# Check for every project if all params
			# match and return this project
			matches = []
			for project in response:
				match = True
				for key,value in params.items():
					if not (project[key] == str(value)):
						match = False
						break
				if match:
					matches.append(TestProject(self,**project))
			return matches
		else:
			# Otherwise, return all available projects
			return [TestProject(self,**project) for project in response]


class TestlinkObject:
	"""Abstract Testlink Object
	@ivar api: TestlinkAPI instance
	@type api: testlink.api.TestlinkAPI
	@ivar Id: Internal Testlink Id of the object
	@type Id: int
	@ivar name: Internal Testlink name of the object
	@type name: str
	"""

	def __init__(self,api,id,name,parent=None):
		"""Initialises base Testlink object
		@param api: TestlinkAPI instance
		@type api: testlink.api.TestlinkAPI
		@param id: Internal Testlink Id of the object
		@type id: int
		@param name: Internal Testlink name of the object
		@type name: str
		@keyword kwargs: Additonal attributes
		"""
		self.api = api
		self.id = int(id)
		self.name = unicode(name)
		self.parent = parent

	def __str__(self):
		result = {}
		for k,v in self.__dict__.items():
			if not str(k).startswith('_'):
				result.update({k:v})
		return str(result)
	__repr__ = __str__


class TestProject(TestlinkObject):
	"""Testlink TestProject representation
	Additional members to TestlinkObject
	@ivar notes: TestProject notes
	@type notes: str
	@ivar prefix: TestCase prefix within TestProject
	@type prefix: str
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
		TestlinkObject.__init__(self,api,id,name)
		self.notes = self.api.parse(str(notes))
		self.prefix = str(prefix)
		self.active = bool(active)
		self.public = bool(is_public)
		self.requirements = bool(opt['requirementsEnabled'])
		self.priority = bool(opt['testPriorityEnabled'])
		self.automation = bool(opt['automationEnabled'])
		self.inventory = bool(opt['inventoryEnabled'])
		self.tc_count = int(tc_counter)
		self.color = str(color)


	def getTestPlan(self,name=None,**params):
		"""Returns TestPlans specified by parameters
		@param name: The name of the TestPlan
		@type name: str
		@param params: Other params for TestPlan
		@type params: list
		@returns: Matching TestPlans
		@rtype: list
		"""
		# Check if simple API call can be done
		if name and len(params)==0:
			response = self.api.getTestPlanByName(name,projectname=self.name)
			return TestPlan(api = self.api, parent = self,	**response)

		# Get all TestPlans for the project
		response = self.api.getProjectTestPlans(self.id)

		if len(params)>0:
			# Add name to search parameters
			params['name'] = name
	
			# Check for every plan if all params
			# match abd return this testplan
			matches = []
			for plan in response:
				match = True
				for key,value in params.items():
					if not (plan[key] == str(value)):
						match = False
						break
				if match:
					matched.append(TestPlan(api = self.api, parent = self,	**plan))
			return matches
		else:
			# Otherwise, return all available testplans
			return [TestPlan(api = self.api, parent = self, **plan) for plan in response]
			

	def getTestSuite(self,name=None,**params):
		"""Returns TestSuites specified by parameters"""
		raise NotImplementedError()
		"""
		if 'id' in params:
			# Search by ID
			resp = self.api.getTestSuiteById(params['id'])
			if isinstance(resp,list) and len(resp)==1:
				resp=resp[0]
			return TestSuite(api=self.api,parent=self,**resp)
		
		suites = self.api.getFirstLevelTestSuitesForTestProject(self.id)
		if len(params)>0:
			# Search by params
			for key,value in params.items():
				for s in suites:
					if s[key]==value:
						return TestSuite(api=self.api,parent=self,**s)
		else:
			return [TestSuite(api=self.api,parent=self,**s) for s in suites]
		"""


class TestPlan(TestlinkObject):
	"""Testlink TestPlan representation
	Additional member to TestlinkObject
	@ivar notes: TestPlan notes
	@type notes: str
	@ivar active: TestPlan active flag
	@type active: bool
	@ivar public: TestPlan public flag
	@type public: bool
	"""

	def __init__(self,api,id,name,notes,is_public,active,**kwargs):
		TestlinkObject.__init__(self,api,id,name)
		self.notes = self.api.parse(unicode(notes))
		self.is_active = bool(active)
		self.is_public = bool(is_public)
	

	def getBuild(self,name=None,**params):
		"""Returns Builds specified by parameters"""
		builds = self.api.getBuildsForTestPlan(self.id)
		# Add name to params
		params['name'] = name
		for key,value in params.items():
			# Check for single result
			if isinstance(builds,dict):
				return Build(api=self,**builds)
			for b in builds:
				if b[key]==value:
					return Build(api=self.api,**b)

	def getPlatform(self,name=None,**params):
		"""Returns platforms specified by parameters"""
		platforms = self.api.getTestPlanPlatforms(self.id)
		# Add name to params
		params['name'] = name		
		for key,value in params.items():
			# Check for single results
			if isinstance(platforms,dict):
				return Platform(api=self,**platforms)
			for p in platforms:
				if p[key]==value:
					return Platform(api=self.api,**p)
		
	def getTestSuite(self,name=None,**params):
		"""Return TestSuites specified by parameters"""
		raise NotImplementedError()
		"""
		suites = self.api.getTestSuitesForTestPlan(self.id)
		if len(params)>0:
			for key,value in params.items():
				for s in suites:
					if s[key]==value:
						return TestSuite(api=self.api,parent=self,**s)
		else:
			return [TestSuite(api=self.api,parent=self,**s) for s in suites]
		"""

	def getTestCase(self,testcaseid=None,buildid=None,keywordid=None,keywords=None,executed=None,assignedto=None,executionstatus=None,executiontype=None,**params):
		"""Returns testcases specified by parameters
		@param params: Params for TestCase
		@type params: mixed
		@returns: Matching TestCases
		@rtype: mixed
		"""
		# Get all available TestCases
		# Use all possible API params to speed up API call
		testcases = self.api.getTestCasesForTestPlan(\
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
										
		# Check for every project if all other params
		# match and return this testcase
		matches = []
		for case in testcases:
			match = True
			for key,value in params.items():
				if not(case[key] == str(value)):
					match = False
					break
			if match:
				matches.append(TestCase(api = self.api, parent = self, **case))
		return matches
						

class Build(TestlinkObject):
	"""Testlink Build representation"""

	def __init__(self,api,id,name,notes,**kwargs):
		TestlinkObject.__init__(self,api,id,name)
		self.notes = unicode(notes)


class Platform(TestlinkObject):
	"""Testlink Platform representation"""

	def __init__(self,api,id,name,notes,**kwargs):
		TestlinkObject.__init__(self,api,id,name)
		self.notes = unicode(notes)


class TestSuite(TestlinkObject):
	"""Testlink TestSuite representation"""

	def __init__(self,api,id,name,notes,**kwargs):
		TestlinkObject.__init__(self,api,id,name)
		self.notes = unicode(notes)

	def getTestSuite(self,name=None,**params):
		suites = self.api.getTestSuitesForTestSuite(self.id)
		if len(params)>0:
			for key,value in params.items():
				for s in suites:
					if s[key]==value:
						return TestSuite(api=self.api,parent=self,**s)
		else:
			return [TestSuite(api=self.api,parent=self,**s) for s in suites]

	def getTestCase(self,name=None,**params):
		cases = self.api.getTestCasesForTestSuite(self.id,details='full')
		if len(params)>0:
			for key,value in params.items():
				for c in cases:
					if c[key]==value:
						return TestCase(api=self.api,parent=self,**c)
		else:
			return [TestCase(api=self.api,parent=self,**c) for c in cases]

class TestCase(TestlinkObject):
	"""Testlink TestCase representation
	Additional members to TestlinkObject
	@ivar executed: Flag if TestCase has been executed yet
	@type executed
	"""

	class Step(object):
		"""Testlink TestCase Step representation
		@ivar step_number: Number of the step
		@type step_number: int
		@ivar actions: Actions of the step
		@type actions: str
		@ivar result: Expected result of the step
		@type result: str
		"""
		def __init__(self,api,step_number,actions,execution_type,active,id,expected_results,**kwargs):
			self.step_number = int(step_number)
			self.actions = api.parse(unicode(actions))
			self.execution_type = int(execution_type)
			self.active = bool(active)
			self.id = int(id)
			self.result = api.parse(unicode(expected_results))

		def __str__(self):
			result = {}
			for k,v in self.__dict__.items():
				if not str(k).startswith('_'):
					result.update({k:v})
			return str(result)
		__repr__ = __str__

	class Execution(object):
		"""Testlink TestCase Execution representation
		@cvar EXEC_TYPE: Possible execution types
		@type EXEC_TYPE: dict

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
		@type execution_type: int
		@ivar execution_ts: Timestamp of execution
		@type execution_ts: str
		@ivar tester_id: The internal ID of the tester
		@type tester_id: int
		"""

		EXEC_TYPE = {'MANUAL': 1, 'AUTOMATIC': 2}

		def __init__(self,api,id,testplan_id,platform_id,build_id,tcversion_id,tcversion_number,status,notes,execution_type,execution_ts,tester_id,**kwargs):
			self.api = api
			self.id = int(id)
			self.testplan_id = int(testplan_id)
			self.platform_id = int(platform_id)
			self.build_id = int(build_id)
			self.tcversion_id = int(tcversion_id)
			self.tcversion_number = int(tcversion_number)
			self.status = str(status)
			self.notes = unicode(notes)
			self.execution_type = int(execution_type)
			self.execution_ts = str(execution_ts)
			self.tester_id = int(tester_id)

		def __str__(self):
			result = {}
			for k,v in self.__dict__.items():
				if not str(k).startswith('_'):
					result.update({k:v})
			return str(result)
		__repr__ = __str__

		def delete(self):
			self.api.deleteExecution(self.id)


	def __init__(
			self,			\
			api,			\
			executed,		\
			execution_notes,	\
			tcversion_number,	\
			tc_id,			\
			assigner_id,		\
			execution_order,	\
			platform_name,		\
			linked_ts,		\
			tsuite_name,		\
			assigned_build_id,	\
			exec_on_tplan,		\
			execution_run_type,	\
			feature_id,		\
			version,		\
			exec_on_build,		\
			testsuite_id,		\
			exec_status,		\
			status,			\
			importance,		\
			execution_type,		\
			execution_ts,		\
			active,			\
			user_id,		\
			tester_id,		\
			exec_id,		\
			tcversion_id,		\
			name,			\
			linked_by,		\
			type,			\
			summary,		\
			preconditions,		\
			platform_id,		\
			z,			\
			external_id,		\
			urgency,		\
			priority,		\
			steps=[],		\
			**kwargs		\
		):
		"""
		@note: ID param name changed!
		"""
		TestlinkObject.__init__(self,api,tc_id,name)
		self.executed = bool(executed)
		self.execution_notes = self.api.parse(unicode(execution_notes))
		self.execution_order = int(execution_order)
		self.version = int(version)
		self.exec_status = str(exec_status)
		self.status = str(status)
		self.importance = int(importance)
		self.execution_type = int(execution_type)
		self.active = bool(active)
		self.summary = self.api.parse(unicode(summary))
		self.preconditions = self.api.parse(unicode(preconditions))
		self.platform_id = int(platform_id)
		self.external_id = int(external_id)
		self.steps = [TestCase.Step(api,**s) for s in steps]

	def getLastExecutionResult(self,testplanid):
		resp = self.api.getLastExecutionResult(testplanid,self.id,self.external_id)
		return TestCase.Execution(self.api,**resp)

	def deleteLastExecution(self,testplanid):
		# Update last execution
		last = self.getLastExecutionResult(testplanid)
		self.api.deleteExecution(last.id)

	def reportResult(self,testplanid,status,notes=None,overwrite=False):
		self.api.reportTCResult(
			testplanid = testplanid,		\
			status = status,			\
			testcaseid = self.id,			\
			testcaseexternalid = self.external_id,	\
			notes = notes,				\
			platformid = self.platform_id,		\
			overwrite = overwrite
		)

	def getAttachments(self):
		return self.api.getTestCaseAttachments(self.id,self.external_id)
