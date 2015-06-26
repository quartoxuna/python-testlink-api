#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@author: Kai Borowiak
@summary: TestSuite for testlink.objects.TestPlan
"""

# IMPORTS
import unittest
import inspect

from .. import randint, randput, randict

from testlink.objects import TestPlan

class TestPlanTests(unittest.TestCase):

	def __init__(self,*args,**kwargs):
		super(TestPlanTests,self).__init__(*args,**kwargs)
		self._testMethodDoc = "TestPlan: " + self._testMethodDoc

	def test__str__(self):
		"""String representation"""
		name = randput()
		obj = TestPlan(name=name)
		string = str(obj)
		self.assertEqual(string, "TestPlan: %s" % name)
