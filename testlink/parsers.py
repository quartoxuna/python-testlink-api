#!/usr/bin/env python

"""
@author: Kai Borowiak
@summary: Common parsers for Testlink internals
"""

# IMPORTS
import HTMLParser
import inspect
from bs4 import BeautifulSoup
from .log import tl_log as log


class DefaultParser(HTMLParser.HTMLParser):
	"""Default parser, just unescape fed data"""

	def feed(self,data):
		if inspect.isgenerator(data):
			for elem in data:
				yield self.feed(elem)
		else:
				yield HTMLParser.HTMLParser.unescape(self,data.replace("&nbsp;",' '))



class SectionParser(object):
	"""Splits <p> sections to a list"""

	def feed(self,data):
		if inspect.isgenerator(data):
			for elem in data:
				for e in self.feed(elem):
					yield e
		else:
			soup = BeautifulSoup(data)
			if soup.p:
				for p in soup.find_all('p',recursive=False):
					try:
						elem = next(p.stripped_strings)
						yield elem
					except StopIteration:
						break
			else:
				yield data
