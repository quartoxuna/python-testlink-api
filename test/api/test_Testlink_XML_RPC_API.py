# -*- coding: utf-8 -*-

"""
@author: Kai Borowiak
@summary: TestSuite for testlink.api.xmlrpc.TestlinkXMLRPCAPI
"""

# IMPORTS
import mock
import unittest

from testlink.api.xmlrpc import TestlinkXMLRPCAPI

class TestlinkXMLRPCAPITests(unittest.TestCase):
    """Testcases for Testlink XML-RPC API Wrapper"""

    def test_query(self):
        """Query wrapper"""
        proxy = mock.MagicMock()
        proxy.test = mock.MagicMock(return_value="Passed")
        api = TestlinkXMLRPCAPI(proxy)
        parameters = {'id': 1234, 'name': 'Test'}
        expected = parameters
        expected.update({'devKey': 123456})

        # Call method
        self.assertEqual(api.query('test', **parameters), "Passed")
        proxy.test.assert_called_with(expected)

    def test_global_devkey(self):
        """Global DevKey setting"""
        proxy = mock.MagicMock()
        proxy.test = mock.MagicMock(return_value="Passed")

        devkey = '123456789ABCDEF'
        api = TestlinkXMLRPCAPI(proxy)
        api.devkey = devkey

        self.assertEqual(api.query('test'), "Passed")
        proxy.test.assert_called_with({'devKey': devkey})
