# pylint: disable=missing-docstring

# IMPORTS
import unittest
import mock

from testlink.api.xmlrpc import TestlinkXMLRPCAPI
from testlink.objects.tl_testlink import Testlink

class TestlinkTests(unittest.TestCase):

    def test_initialization(self):
        """Test default initialisation"""
        proxy = mock.MagicMock()
        api = TestlinkXMLRPCAPI(proxy)

        testlink = Testlink(api)
        self.assertEqual(testlink.api, api)
