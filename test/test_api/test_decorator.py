#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@author: Kai Borowiak
@summary: TestSuite for testlink.api.TLVersion
"""

# IMPORTS
import unittest
from testlink.api.testlink_api import TLVersion
from testlink.api.xmlrpc import TestlinkXMLRPCAPI
from testlink.exceptions import NotSupported

from pkg_resources import parse_version

class DummyAPI(object):
    tl_version = parse_version("1.0")

class TLVersionDecoratorTests(unittest.TestCase):
    """Tests of TLVersion decorator"""

    def __init__(self, *args, **kwargs):
        super(TLVersionDecoratorTests, self).__init__(*args, **kwargs)
        self._testMethodDoc = "@TLVersion: " + self._testMethodDoc

    def tearDown(self):
        # Restore defaults
        TestlinkXMLRPCAPI.IGNORE_VERSION_CHECK = False

    def test_equal(self):
        """Equal version"""
        @TLVersion("1.0")
        def decorated(arg):
            pass
        decorated(DummyAPI)

    def test_lower(self):
        """Lower version"""
        for version in ("0.1", "0.9", "0.9.9", "0.1.0"):
            @TLVersion(version)
            def decorated(arg):
                pass
            decorated(DummyAPI)

    def test_higher(self):
        """Higher version"""
        for version in ("1.1", "1.0.1", "1.9.3"):
            @TLVersion(version)
            def decorated(arg):
                pass
            self.assertRaises(NotSupported, decorated, DummyAPI)

    def test_strict(self):
        """Strict version check"""
        # Check if error is raised on other version
        for version in ("0.1", "0.9", "0.9.9", "0.1.0", "1.1", "1.0.1", "1.9.3"):
            @TLVersion(version, strict=True)
            def decorated(arg):
                pass
            self.assertRaises(NotSupported, decorated, DummyAPI)

    def test_ignore(self):
        """Ignore version checks"""
        self.assertEquals(TestlinkXMLRPCAPI.IGNORE_VERSION_CHECK, False)
        TestlinkXMLRPCAPI.IGNORE_VERSION_CHECK = True
        for version in ("1.0", "0.9", "1.1"):
            @TLVersion(version)
            def decorated(arg):
                pass
            self.assertEquals(TestlinkXMLRPCAPI.IGNORE_VERSION_CHECK, True)
            decorated(DummyAPI)
