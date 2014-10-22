#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@author: Kai Borowiak
@summary: Common parsers
"""

# IMPORTS
import HTMLParser

class IParser(object):
	"""Abstract Parser Interface"""
	def __init__(self):
		"""Initializes the parser"""
		pass

	def feed(self,data):
		"""Parse the specified data
		@param data: Data to parse
		@type data: str
		@returns: Parsed data
		@rtype: mixed
		@raises Exception: Cannot parse input
		"""
		raise NotImplementedError()

class HTMLTagRemover(HTMLParser.HTMLParser,IParser):
	"""Remove all HTML tags"""
	def __init__(self):
		super(HTMLTagRemover,self).__init__()
		self.__result = ""

	def do_nothing(self,*args,**kwargs):
		pass
	handle_starttag = do_nothing
	handle_endtag = do_nothing
	handle_startendtag = do_nothing
	handle_entityref = do_nothing
	handle_charref = do_nothing
	handle_comment = do_nothing
	handle_decl = do_nothing
	handle_pi = do_nothing
	unknown_decl = do_nothing

	def handle_data(self,data):
		self.__result += data

	def feed(self,data):
		super(HTMLTagRemover,self).feed(data)
		return self.__result

class HTMLEntityParser(HTMLParser.HTMLParser,IParser):
	"""Translates HTML-Entities to normal characters"""
	def __init__(self):
		super(HTMLEntityParser,self).__init__()

	def feed(self,data):
		if not data:
			data = ""
		# Replace blanks (&nbsp;) before using the unescape
		# method, because it would result in unicode blank (\x0a)
		return HTMLParser.HTMLParser.unescape(self,data.replace("&nbsp;",' '))

class HTMLSectionParser(HTMLParser.HTMLParser,IParser):
	"""Splits HTML sections into lists"""
	def __init__(self):
		super(HTMLSectionParser,self).__init__()
		self.__result = []
		self.__active = False
		self.__buffer = ""

	def handle_starttag(self,tag,attrs):
		if tag in 'p':
			self.__active = True

	def handle_data(self,data):
		if self.__active:
			self.__buffer += data

	def handle_endtag(self,tag):
		if tag in 'p':
			self.__active = False
			self.__result.append(self.__buffer)
			self.__buffer = ""

	def feed(self,data):
		super(HTMLSectionParser,self).feed(data)
		return self.__result

class HTMLListParser(HTMLParser.HTMLParser,IParser):
	"""Split HTML lists into nested lists"""
	def __init__(self):
		super(HTMLListParser,self).__init__()
		self.__result = []
		self.__list_active = False
		self.__element_active = False
		self.__nested = False
		self.__list_buffer = []
		self.__element_buffer = ""

	def handle_starttag(self,tag,attrs):
		if tag in ('ol','ul'):
			if not self.__list_active:
				self.__list_active = True
			else:
				self.__nested = True
		elif tag in ('li'):
			self.__element_active = True

	def handle_data(self,data):
		if self.__nested:
			# If we have a nested list, parse it and
			# set it as the current element in the buffer
			self.__element_buffer = HTMLListParser().feed(data)
		elif self.__list_active:
			# Ignore non-list elements within lists tag
			pass
		elif self.__element_active:
			# Store data of the current element
			self.__element_buffer += data

	def handle_endtag(self,tag):
		if tag in ('ol','ul'):
			# Add the current list buffer to the result
			self.__result.append(self.__list_buffer)
			self.__list_active = False
		elif tag in ('li'):
			# Add the current element buffer to the current list buffer
			self.__list_buffer.append(self.__element_buffer)
			self.__element_active = False

	def feed(self,data):
		super(HTMLListParser,self).feed(data)
		return self.__result
