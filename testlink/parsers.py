#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@author: Kai Borowiak
@summary: HTML Parsers for handling Testlink's formattings
"""

# IMPORTS

from testlink import log
from HTMLParser import HTMLParser
from HTMLParser import HTMLParseError


class DefaultParser(HTMLParser):
	"""Base class, parsing nothing"""
	def __init__(self):
		HTMLParser.__init__(self)
		self.result = ""

	def reset(self):
		HTMLParser.reset(self)
		self.result = ""

	def handle_starttag(self,tag,attrs):
		self.result += "<%s" % tag
		for attr in attrs:
			self.result += " %s='%s'" % (attr[0],attr[1])
		self.result += ">"

	def handle_endtag(self,tag):
		self.result += "</%s>" % tag

	def handle_startendtag(self,tag,attrs):
		self.result += "<%s" % tag
		for attr in attrs:
			self.result += " %s='%s'" % (attr[0],attr[1])
		self.result += " />"
	
	def handle_data(self,data):
		self.result += data

	def handle_entityref(self,name):
		self.result += "&%s;" % name

	def handle_charref(self,name):
		self.result += "&#%s;" % name

	def handle_comment(self,data):
		self.result += "<!-- %s -->" % data

	def handle_decl(self,decl):
		self.result += "<!%s>" % decl

	def handle_pi(self,data):
		self.result += "<?%s>" % data

	def unknown_decl(self,data):
		self.result += "<![%s]>" % data


class EntityRemover(DefaultParser):
	"""Unescapes HTML entities"""

	entitymap = {\
			'gt':'>',\
			'lt':'<',\
			'nbsp':' '\
		}

	def __init__(self):
		DefaultParser.__init__(self)

	def handle_entityref(self,name):
		try:
			self.result += self.entitymap[name]
		except Exception:
			raise HTMLParseError("Cannot convert entity '%s'" % str(name))
