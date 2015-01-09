#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@author: Kai Borowiak
@summary: TestSuite for testlink.api.TLVersion
"""

# IMPORTS
import unittest
from testlink.api import TLVersion
from testlink.api import NotSupported
from testlink.api import Version

class TLVersionDecoratorTests(unittest.TestCase):
	"""Tests of TLVersion decorator"""

	_tl_version = Version("1.0")

	def __init__(self,*args,**kwargs):
		super(TLVersionDecoratorTests,self).__init__(*args,**kwargs)
		self._testMethodDoc = "@TLVersion: " + self._testMethodDoc

	def dummy(self,*args,**kwargs):
		pass

	def test_equal(self):
		"""Equal version"""
		decorated = TLVersion("1.0")
		decorated(self.dummy)(self)

	def test_lower(self):
		"""Lower version"""
		lower = ("0.1","0.9","0.9.9","0.1.0")
		for v in lower:
			decorated = TLVersion(v)
			decorated(self.dummy)(self)

	def test_higher(self):
		"""Higher version"""
		higher = ("1.1","1.0.1","1.9.3")
		for v in higher:
			decorated = TLVersion(str(v))
			self.assertRaises(NotSupported,decorated(self.dummy),self)
