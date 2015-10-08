#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@author: Kai Borowiak
@summary: TestCase for testlink.objects.TestCase.Execution
"""

# IMPORTS
import unittest
import inspect
import datetime
from mock import patch, Mock

from .. import randint, randput, randict

from testlink.objects import TestCase
from testlink.objects import DATETIME_FORMAT

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

	def test_datetime_conversion(self):
		"""Datetime Conversion"""
		date = "2020-10-20 12:34:45"
		ts = datetime.datetime.strptime(date,DATETIME_FORMAT)

		execution = TestCase.Execution(execution_ts=date)
		self.assertEquals(ts,execution.execution_ts)
