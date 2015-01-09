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

	def __init__(self,*args,**kwargs):
		super(HTMLTagRemoverTests,self).__init__(*args,**kwargs)
		self._testMethodDoc = "HTMLTagRemover: " + self._testMethodDoc

	def setUp(self):
		self.parser = HTMLTagRemover()

	def test_no_tag(self):
		"""handle no tag"""
		html = "SPAM!"
		self.assertEqual(self.parser.feed(html),"SPAM!")

	def test_start_tag(self):
		"""remove start tag"""
		html = "<html>SPAM!"
		self.assertEqual(self.parser.feed(html),"SPAM!")

	def test_end_tag(self):
		"""remove end tag"""
		html = "SPAM!</html>"
		self.assertEqual(self.parser.feed(html),"SPAM!")

	def test_startend_tag(self):
		"""remove startend tag"""
		html = "SPAM!<br />"
		self.assertEqual(self.parser.feed(html),"SPAM!")

	def test_entityref(self):
		"""remove entity"""
		html = "SPAM!&nbsp;"
		self.assertEqual(self.parser.feed(html),"SPAM!")

	def test_charref(self):
		"""remove character reference"""
		html = "SPAM!&#42"
		self.assertEqual(self.parser.feed(html),"SPAM!")

	def test_comment(self):
		"""remove comment"""
		html = "SPAM!<!-- NO SPAM! -->"
		self.assertEqual(self.parser.feed(html),"SPAM!")

	def test_decl(self):
		"""remove type declaration"""
		html = "<!DOCTYPE html>SPAM!"
		self.assertEqual(self.parser.feed(html),"SPAM!")

	def test_pi(self):
		"""remove processing instruction"""
		html = "SPAM!<?proc>"
		self.assertEqual(self.parser.feed(html),"SPAM!")

	def test_unknown_decl(self):
		"""remove unknown declaration"""
		html = "<!NO SPAM>SPAM!"
		self.assertEqual(self.parser.feed(html),"SPAM!")
