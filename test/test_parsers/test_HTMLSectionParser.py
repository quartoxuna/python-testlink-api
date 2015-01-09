#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@author: Kai Borowiak
@summary: TestSuite for testlink.parsers.HTMLSectionParser
"""

# IMPORTS
import unittest
from testlink.parsers import HTMLSectionParser

class HTMLSectionParserTests(unittest.TestCase):
	"""Tests for HTMLSectionParser"""

	def __init__(self,*args,**kwargs):
		super(HTMLSectionParserTests,self).__init__(*args,**kwargs)
		self._testMethodDoc = "HTMLSectionParser: " + self._testMethodDoc

	def setUp(self):
		self.parser = HTMLSectionParser()

	def test_sections(self):
		"""Parse sections"""
		html = "<p>S</p><p>P</p><p>A</p><p>M</p>"
		self.assertEqual(self.parser.feed(html),list("SPAM"))
