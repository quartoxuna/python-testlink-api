#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@author: Kai Borowiak
@summary: TestSuite for testlink.parsers.HTMLListParser
"""

# IMPORTS
import unittest
from testlink.parsers import HTMLListParser

class HTMLListParserTests(unittest.TestCase):
	"""Tests for HTMLListParser"""

	def setUp(self):
		self.parser = HTMLListParser()

	def test_lists(self):
		html = "<ol><li>S</li><ul><li>P</li></ul><li>A</li><li>M</li></ol>"
		self.assertEqual(self.parser.feed(html),["S",["P"],"A","M"])
