#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@author: Kai Borowiak
@summary: Common parsers
"""

# IMPORTS
import HTMLParser

class HTMLEntityParser(HTMLParser.HTMLParser):
	"""Default parser for XML-RPC responses. Translates HTML-Entities to readable characters."""
	def feed(self,data):
		if not data:
			data = ""
		# Replace blanks (&nbsp;) before using the unescape
		# method, because it would result in unicode blank (\x0a)
		return HTMLParser.HTMLParser.unescape(self,data.replace("&nbsp;",' '))
