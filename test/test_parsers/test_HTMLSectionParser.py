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

	def setUp(self):
		self.parser = HTMLSectionParser()

	def test_sections(self):
		html = "<p>S</p><p>P</p><p>A</p><p>M</p>"
		self.assertEqual(self.parser.feed(html),list("SPAM"))
