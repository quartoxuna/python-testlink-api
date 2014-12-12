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
	"""Tests for HTMLTagRemover"""

	def setUp(self):
		self.parser = HTMLTagRemover()

	def test_no_tag(self):
		"""Check No Tag"""
		html = "SPAM!"
		self.assertEqual(self.parser.feed(html),"SPAM!")

	def test_start_tag(self):
		"""Check Start Tag"""
		html = "<html>SPAM!"
		self.assertEqual(self.parser.feed(html),"SPAM!")

	def test_end_tag(self):
		"""Check End Tag"""
		html = "SPAM!</html>"
		self.assertEqual(self.parser.feed(html),"SPAM!")

	def test_startend_tag(self):
		"""Check StartEnd Tag"""
		html = "SPAM!<br />"
		self.assertEqual(self.parser.feed(html),"SPAM!")

	def test_entityref(self):
		"""Check EntityRef"""
		html = "SPAM!&nbsp;"
		self.assertEqual(self.parser.feed(html),"SPAM!")

	def test_charref(self):
		"""Check CharRef"""
		html = "SPAM!&#42"
		self.assertEqual(self.parser.feed(html),"SPAM!")

	def test_comment(self):
		"""Check Comment"""
		html = "SPAM!<!-- NO SPAM! -->"
		self.assertEqual(self.parser.feed(html),"SPAM!")

	def test_decl(self):
		"""Check Decl"""
		html = "<!DOCTYPE html>SPAM!"
		self.assertEqual(self.parser.feed(html),"SPAM!")

	def test_pi(self):
		"""Check proc"""
		html = "SPAM!<?proc>"
		self.assertEqual(self.parser.feed(html),"SPAM!")

	def test_unknown_decl(self):
		"""Check unknown decl"""
		html = "<!NO SPAM>SPAM!"
		self.assertEqual(self.parser.feed(html),"SPAM!")
