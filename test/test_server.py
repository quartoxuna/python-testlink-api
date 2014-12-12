#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@author: Kai Borowiak
@summary: TestSuite for testlink.server
"""

# IMPORTS
import unittest
import time
from testlink.server import TestlinkXMLRPCServer
from xmlrpclib import ServerProxy

def dummy_callback(val):
	return val

class TestlinkXMLRPCServerTests(unittest.TestCase):
	"""Tests of TestlinkXMLRPCServer implementation"""

	def test_rpc_call(self):
		"""RPC call"""
		server = TestlinkXMLRPCServer(dummy_callback)
		client = ServerProxy("http://127.0.0.1:8080/")
		self.assertEqual(client.executeTestCase("SPAM!"), "SPAM!")
