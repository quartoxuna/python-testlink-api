#!/usr/bin/env python

"""
@author: Kai Borowiak
@summary: Common parsers for Testlink internals
"""

# IMPORTS
import HTMLParser
from bs4 import BeautifulSoup
from .log import tl_log as log


class DefaultParser(HTMLParser.HTMLParser):
	"""Default parser, just unescape fed data"""

	def feed(self,data):
		# Replace space by hand
		data = data.replace("&nbsp;",' ')
		yield HTMLParser.HTMLParser.unescape(self,data)


class ListParser(object):
	"""Parses (un)numbered lists to python lists"""

	def feed(self,data):
		soup = BeautifulSoup(data)
		if soup.ul:
			elem = soup.ul
		elif soup.ol:
			elem = soup.ol
		else:
			yield data
		for res in self.listify(elem):
			yield res

	def listify(self,html):
		for li in html.find_all('li',recursive=False):
			try:
				elem = next(li.stripped_strings)
				if li.find('ul'):
					yield (elem , self.listify(li.find('ul')),)
				elif li.find('ol'):
					yield (elem , self.listify(li.find('ol')),)
				else:
					yield (elem,)
			except StopIteration:
				break


class SectionParser(object):
	"""Splits <p> sections to a list"""

	def feed(self,data):
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
