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
				yield self.handle(elem)
		else:
			# Not iterable
			yield self.handle(data)

	def handle(self,data):
		return HTMLParser.HTMLParser.unescape(self,data.replace("&nbsp;",' '))


class ListParser(object):
	"""Parses (un)numbered lists to python lists"""

	def feed(self,data):
		if inspect.isgenerator(data):
			for elem in data:
				yield self.handle(elem)
		else:
			# Not iterable
			yield self.handle(data)

	def handle(self,data):
		soup = BeautifulSoup(data)
		if soup.ul:
			return self.listify(soup.ul)
		elif soup.ol:
			return self.listify(soup.ol)
		else:
			return data

	def listify(self,html):
		for li in html.find_all('li',recursive=False):
				try:
					elem = next(li.stripped_strings)
				except StopIteration:
					break

				if li.find('ul'):
					yield (elem , self.listify(li.find('ul')))
				elif li.find('ol'):
					yield (elem , self.listify(li.find('ol')))
				else:
					yield (elem)


class SectionParser(object):
	"""Splits <p> sections to a list"""

	def feed(self,data):
		if inspect.isgenerator(data):
			for elem in data:
				return self.handle(elem)
		else:
			# Not iterable
			return self.handle(data)

	def handle(self,data):
		soup = BeautifulSoup(data)
		# Is there any <p> element?
		if soup.p:
			for p in soup.find_all('p',recursive=False):
				try:
					yield next(p.stripped_strings)
				except StopIteration:
					pass
		else:
			yield data
