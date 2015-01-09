#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@author: Kai Borowiak
@summary: TestSuite for testlink.objects.Testlink
"""

# IMPORTS
import unittest
from mock import Mock, MagicMock, patch

from testlink.api import Testlink_XML_RPC_API
from testlink.objects import Testlink
from testlink.exceptions import *

class TestlinkTests(unittest.TestCase):

	def __init__(self,*args,**kwargs):
		super(TestlinkTests,self).__init__(*args,**kwargs)
		self._testMethodDoc = "Testlink: " + self._testMethodDoc

	@patch('xmlrpclib.ServerProxy')
	def test_apiType(self,mock_proxy):
		"""API Type settings"""
		tl = Testlink("http://localhost/lib/api/xmlrpc.php","SPAM")
		self.assertTrue(isinstance(tl._api,Testlink_XML_RPC_API))
