#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@author: Kai Borowiak
@summary: TestSuite for testlink.parsers.HTMLTagRemover
"""

# IMPORTS
import unittest
from testlink.parsers import HTMLTagRemover

class HTMLTagRemoverTests(unittest.TestCase):

	def setUp(self):
		self.parser = HTMLTagRemover()

	def test_no_tag(self):
		html = "SPAM!"
		self.assertEqual(self.parser.feed(html),"SPAM!")

	def test_start_tag(self):
		html = "<html>SPAM!"
		self.assertEqual(self.parser.feed(html),"SPAM!")

	def test_end_tag(self):
		html = "SPAM!</html>"
		self.assertEqual(self.parser.feed(html),"SPAM!")

	def test_startend_tag(self):
		html = "SPAM!<br />"
		self.assertEqual(self.parser.feed(html),"SPAM!")

	def test_entityref(self):
		html = "SPAM!&nbsp;"
		self.assertEqual(self.parser.feed(html),"SPAM!")

	def test_charref(self):
		html = "SPAM!&#42"
		self.assertEqual(self.parser.feed(html),"SPAM!")

	def test_comment(self):
		html = "SPAM!<!-- NO SPAM! -->"
		self.assertEqual(self.parser.feed(html),"SPAM!")

	def test_decl(self):
		html = "<!DOCTYPE html>SPAM!"
		self.assertEqual(self.parser.feed(html),"SPAM!")

	def test_pi(self):
		html = "SPAM!<?proc>"
		self.assertEqual(self.parser.feed(html),"SPAM!")

	def test_unknown_decl(self):
		html = "<!NO SPAM>SPAM!"
		self.assertEqual(self.parser.feed(html),"SPAM!")
