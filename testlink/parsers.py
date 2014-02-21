#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@author: Kai Borowiak
@summary: HTML Parsers for handling Testlink's formattings
"""

# IMPORTS
from testlink import log
from HTMLParser import HTMLParser

class NullParser(HTMLParser):
	"""Does nothing"""
	def feed(self,data):
		return data


class EntityRemover(HTMLParser):
	"""Translates HTML entities"""

	entitymap = {\
			'auml':'ä',\
			'ouml':'ö',\
			'uuml':'ü',\
			'Auml':'Ä',\
			'Ouml':'Ö',\
			'Uuml':'Ü',\
			'gt':'>',\
			'lt':'<',\
			'nbsp':' '\
		}

	def handle_charref(self,name):
		try:
			return self.entitymap[name]
		except AttributeError,ae:
			log.exception(str(ae))
			raise RobotError("Cannot convert entity '%s'" % str(name))
