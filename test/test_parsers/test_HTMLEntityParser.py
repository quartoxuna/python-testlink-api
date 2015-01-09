#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@author: Kai Borowiak
@summary: TestSuite for testlink.parsers.HTMLEntityParser
"""

# IMPORTS
import unittest
from testlink.parsers import HTMLEntityParser

class HTMLEntityParserTests(unittest.TestCase):
	"""Tests for HTMLEntityParser"""

	def __init__(self,*args,**kwargs):
		super(HTMLEntityParserTests,self).__init__(*args,**kwargs)
		self._testMethodDoc = "HTMLEntityParser: " + self._testMethodDoc

	def setUp(self):
		self.parser = HTMLEntityParser()

	def test_entities(self):
		"""Convert entities"""
		ent = "&nbsp;&amp;&lt;&gt;"
		self.assertEqual(self.parser.feed(ent)," &<>")
