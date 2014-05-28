#!/usr/bin/env python

"""
@author: Kai Borowiak
@summary: Common parsers for Testlink internals
"""

# IMPORTS
import HTMLParser
from .log import tl_log as log


class DefaultParser(HTMLParser.HTMLParser):
	"""Default parser, just unescape fed data"""

	def __init___(self):
		HTMLParser.HTMLParser(self)

	def feed(self,data):
		return HTMLParser.HTMLParser.unescape(self,data)


