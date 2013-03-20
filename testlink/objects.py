#!/usr/bin/env python

#               /                ______                __    ___                __
#         -+ydNMM....``         /\__  _\              /\ \__/\_ \    __        /\ \ 
#      `+mMMMMMMM........`      \/_/\ \/    __    ____\ \ ,_\//\ \  /\_\    ___\ \ \/'\ 
#     /mMMMMMMMMM..........`       \ \ \  /'__`\ /',__\\ \ \/ \ \ \ \/\ \ /' _ `\ \ , <
#    oMMMMMMMMMMM...........`       \ \ \/\  __//\__, `\\ \ \_ \_\ \_\ \ \/\ \/\ \ \ \\`\ 
#   :MMMMMMMMMMMM............        \ \_\ \____\/\____/ \ \__\/\____\\ \_\ \_\ \_\ \_\ \_\ 
#   hMMMMMMMMMMMM............`        \/_/\/____/\/___/   \/__/\/____/ \/_/\/_/\/_/\/_/\/_/ 
# ..::::::::::::oMMMMMMMMMMMMo..   ______  ____    ______      __      __
#   ............+MMMMMMMMMMMM-    /\  _  \/\  _`\ /\__  _\    /\ \  __/\ \ 
#    ...........+MMMMMMMMMMMs     \ \ \_\ \ \ \_\ \/_/\ \/    \ \ \/\ \ \ \  _ __    __     _____   _____      __   _ __
#     ..........+MMMMMMMMMMy       \ \  __ \ \ ,__/  \ \ \     \ \ \ \ \ \ \/\`'__\/'__`\  /\ '__`\/\ '__`\  /'__`\/\`'__\ 
#      `........+MMMMMMMMm:         \ \ \/\ \ \ \/    \_\ \__   \ \ \_/ \_\ \ \ \//\ \_\.\_\ \ \_\ \ \ \_\ \/\  __/\ \ \/
#        `......+MMMMMNy:            \ \_\ \_\ \_\    /\_____\   \ `\___x___/\ \_\\ \__/.\_\\ \ ,__/\ \ ,__/\ \____\\ \_\ 
#            ```/ss+/.                \/_/\/_/\/_/    \/_____/    '\/__//__/  \/_/ \/__/\/_/ \ \ \/  \ \ \/  \/____/ \/_/
#               /                                                                             \ \_\   \ \_\ 
#                                                                                              \/_/    \/_/

#
# Epydoc documentation
#

"""
@author: Kai Borowiak
@version: 1.0
@summary: Object oriented Wrapper for Testlink
"""

#
# IMPORTS
#
import re
import testlink.api

class Testlink(testlink.api.TestlinkAPI):
	"""Testlink Server representation"""

	def __init__(self,proxy,devkey):
		"""Initializes the Testlink Server object
		@param proxy: Testlink URL
		@type proxy: str
		@param devkey: Testlink developer key
		@type devkey: str
		"""
		testlink.api.TestlinkAPI.__init__(self,proxy)
		self.devkey = devkey

	def getVersion(self):
		"""Returns the version of the Testlink API
		@returns: Version in list format [x,y,z]
		@rtype: list
		"""
		about_str = self.about()
		version_str = re.search(r"(?P<version>\d+(\.{0,1}\d+)+)",about_str).group('version')
		version = version_str.split('.')
		# Get Alphas and Betas
		pre = re.search(r"(Alpha|Beta)\s*(\d+)", about_str)
		if pre:
			if pre.group(1)=="Alpha": version.append(0)
			elif pre.group(1)=="Beta": version.append(1)
			version.append(pre.group(2))
		return '.'.join(version)

	def getTestProject(self,**params):
		if 'name' in params:
			# Search by Name
			resp = self.getTestProjectByName(self.devkey,params['name'])
			if isinstance(resp,list) and len(resp)==1: resp=resp[0]
			return TestProject(server=self,**resp)

		projects = self.getProjects(self.devkey)
		if len(params)>0:
			# Search by params
			for key,value in params.items():
				for p in projects:
					if p[key]==value: return TestProject(server=self,**p)
		else: return [TestProject(server=self,**p) for p in projects]


class TestProject(object):
	def __init__(self,*args,**kwargs):
		self.__dict__.update(kwargs)

	def getTestPlan(self,**params):
		if 'name' in params:
			# Search by Name
			resp = self.server.getTestProjectByName(self.server.devkey,params['name'])
			if isinstance(resp,list) and len(resp)==1: resp=resp[0]
			return TestPlan(server=self.server,testproject=self,**resp)

		plans = self.server.getProjectTestPlans(self.server.devkey,self.id)
		if len(params)>0:
			# Search by params
			for key,value in params.items():
				for p in plans:
					if p[key]==value: return TestPlan(server=self.server,testproject=self,**p)
		else: return [TestPlan(server=self.server,testproject=self,**p) for p in plans]

	def getTestSuite(self,**params):
		if 'id' in params:
			# Search by ID
			resp = self.server.getTestSuiteById(self.server.devkey,params['id'])
			if isinstance(resp,list) and len(resp)==1: resp=resp[0]
			return TestSuite(server=self.server,testproject=self,**resp)
		
		suites = self.server.getFirstLevelTestSuitesForTestProject(self.server.devkey,self.id)
		if len(params)>0:
			# Search by params
			for key,value in params.items():
				for s in suites:
					if s[key]==value: return TestSuite(server=self.server,testproject=self,parent=None,**s)
		else: return [TestSuite(server=self.server,testproject=self,parent=None,**s) for s in suites]

	def __repr__(self):
		return str(self.__dict__)

class TestPlan(object):
	def __init__(self,*args,**kwargs):
		self.__dict__.update(kwargs)

	def getBuild(self,**params):
		builds = self.server.getBuildsForTestPlan(self.server.devkey,self.id)
		if len(params)>0:
			for key,value in params.items():
				for b in builds:
					if b[key]==value: return Build(server=self.server,testplan=self,**b)
		else: return [Build(server=self.server,testplan=self,**b) for b in builds]

	def getPlatform(self,**params):
		platforms = self.server.getTestPlanPlatforms(self.server.devkey,self.id)
		if len(params)>0:
			for key,value in params.items():
				for p in platforms:
					if p[key]==value: return Platform(server=self.server,testplan=self,**p)
		else: return [Platform(server=self.server,testplan=self,**p)]
		
	def getTestSuite(self,**params):
		suites = self.server.getTestSuitesForTestPlan(self.server.devkey,self.id)
		if len(params)>0:
			for key,value in params.items():
				for s in suites:
					if s[key]==value: return TestSuite(server=self.server,testplan=self,**s)
		else: return [TestSuite(server=self.server,testplan=self,**s) for s in suites]

	def getTestCase(self,**params):
		cases = self.server.getTestCasesForTestPlan(self.server.devkey,self.id)
		if len(params)>0:
			for key,value in params.items():
				for c in cases:
					if c[key]==value: return TestCase(server=self.server,testplan=self,**c)
		else: return [TestCase(server=self.server,testplan=self,**c) for c in cases]

	def __repr__(self):
		return str(self.__dict__)

class Build(object):
	def __init__(self,*args,**kwargs):
		self.__dict__.update(kwargs)

	def __repr__(self):
		return str(self.__dict__)

class Platform(object):
	def __init__(self,*args,**kwargs):
		self.__dict__.update(kwargs)

	def __repr__(self):
		return str(self.__dict__)

class TestSuite(object):
	def __init__(self,*args,**kwargs):
		self.__dict__.update(kwargs)

	def getTestSuite(self,**params):
		suites = self.server.getTestSuitesForTestSuite(self.server.devkey,self.id)
		if len(params)>0:
			for key,value in params.items():
				for s in suites:
					if s[key]==value: return TestSuite(server=self.server,parent=self,**s)
		else: return [TestSuite(server=self.server,parent=self,**s) for s in suites]

	def getTestCase(self,**params):
		cases = self.getTestCasesForTestSuite(self.server.devkey,self.id,details='full')
		if len(params)>0:
			for key,value in params.items():
				for c in cases:
					if c[key]==value: return TestCase(server=self.server,suite=self,**c)
		else: return [TestCase(server=self.server,suite=self,**c) for c in cases]

	def __repr__(self):
		return str(self.__dict__)
