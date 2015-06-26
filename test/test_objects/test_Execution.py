#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@author: Kai Borowiak
@summary: TestCase for testlink.objects.TestCase.Execution
"""

# IMPORTS
import unittest
import inspect
from mock import patch, Mock

from .. import randint, randput, randict

from testlink.objects import TestCase

class ExecutionTests(unittest.TestCase):

	def __init__(self,*args,**kwargs):
		super(ExecutionTests,self).__init__(*args,**kwargs)
		self._testMethodDoc = "TestCase.Execution: " + self._testMethodDoc

	def test__str__(self):
		"""String representation"""
		id_ = randint()
		notes = randput()

		obj = TestCase.Execution(id=id_,notes=notes)
		string = str(obj)
		self.assertEqual(string, "Execution (%d) %s" % (id_,notes))
