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

	def setUp(self):
		self.parser = HTMLEntityParser()

	def test_entities(self):
		ent = "&nbsp;&amp;&lt;&gt;"
		self.assertEqual(self.parser.feed(ent)," &<>")
