#!/usr/bin/env python

"""
@author: Kai Borowiak
@summary: Common parsers for Testlink internals
"""

# IMPORTS
import HTMLParser
from .log import tl_log as log

class DefaultParser(HTMLParser.HTMLParser()):
	def __init__(self,*args,**kwargs):
		HTMLParser.HTMLParser(self,*args,**kwargs)
