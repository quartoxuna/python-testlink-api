#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@author: Kai Borowiak
@summary: TestSuite for testlink.objects.TestProject
"""

# IMPORTS
import unittest
import inspect

from .. import randint, randput, randict

from testlink.objects import TestProject

class TestProjectTests(unittest.TestCase):

	def __init__(self,*args,**kwargs):
		super(TestProjectTests,self).__init__(*args,**kwargs)
		self._testMethodDoc = "TestProject: " + self._testMethodDoc

	def test__str__(self):
		"""String representation"""
		name = randput()
		obj = TestProject(name=name)
		string = str(obj)
		self.assertEqual(string, "TestProject: %s" % name)
