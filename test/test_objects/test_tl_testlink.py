#!/usr/bin/env python

# IMPORTS
import unittest
import mock

from testlink.api.xmlrpc import TestlinkXMLRPCAPI
from testlink.objects.tl_testlink import Testlink

class Testlink_Tests(unittest.TestCase):

    def test_initialization(self):
        proxy = mock.MagicMock()
        api = TestlinkXMLRPCAPI(proxy)
        
        tl = Testlink(api)
        self.assertEqual(tl.api, api)

