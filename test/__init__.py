#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@author: Kai Borowiak
@summary: TestSuites for Testlink API Wrapper
"""

# IMPORTS
import string
import random
from mock import Mock

def input(length=10):
	"""Generates random input with specified length
	@param length: Length of input (Default: 10)
	@type length: int
	@returns: Randomly generated string
	@rtype:str
	"""
	return ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(length))

def randict(*args):
	"""Genrates a dictionary with random values.
	@param args: Keys of the resulting dict
	@type args: list
	@returns: Dictionary with *args as keys and random values
	@rtype: dict
	"""
	res = {}
	for arg in args:
		res[arg] = input()
	return res

class ServerMock(Mock):
	class system:
		@staticmethod
		def listMethods():
			pass
	def __init__(self,*args,**kwargs):
		super(ServerMock,self).__init__(*args,**kwargs)

