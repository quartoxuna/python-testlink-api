#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@author: Kai Borowiak
@summary: TestSuite for testlink.objects.TestlinkObject
"""

# IMPORTS
import unittest
import inspect

from testlink.objects import TestlinkObject

class TestlinkObjectTests(unittest.TestCase):

	def __init__(self,*args,**kwargs):
		super(TestlinkObjectTests,self).__init__(*args,**kwargs)
		self._testMethodDoc = "TestlinkObject: " + self._testMethodDoc
