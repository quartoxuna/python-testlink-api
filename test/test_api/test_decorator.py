#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@author: Kai Borowiak
@summary: TestSuite for testlink.api.TLVersion
"""

# IMPORTS
import unittest
from testlink.api import TLVersion
from testlink.api import NotSupported


class TLVersionDecoratorTests(unittest.TestCase):
    """Tests of TLVersion decorator"""

    _tl_version = "1.0"

    def __init__(self, *args, **kwargs):
        super(TLVersionDecoratorTests, self).__init__(*args, **kwargs)
        self._testMethodDoc = "@TLVersion: " + self._testMethodDoc

    def tearDown(self):
        # Restore defaults
        TLVersion.IGNORE = False

    @staticmethod
    def dummy(*args, **kwargs):
        """Dummy method"""
        pass

    def test_equal(self):
        """Equal version"""
        decorated = TLVersion(self._tl_version)
        decorated(self.dummy)(self)

    def test_lower(self):
        """Lower version"""
        for version in ("0.1", "0.9", "0.9.9", "0.1.0"):
            decorated = TLVersion(version)
            decorated(self.dummy)(self)

    def test_higher(self):
        """Higher version"""
        for version in ("1.1", "1.0.1", "1.9.3"):
            decorated = TLVersion(str(version))
            self.assertRaises(NotSupported, decorated(self.dummy), self)

    def test_strict(self):
        """Strict version check"""
        # Check if error is raised on other version
        for version in ("0.1", "0.9", "0.9.9", "0.1.0", "1.1", "1.0.1", "1.9.3"):
            decorated = TLVersion(version, strict=True)
            self.assertRaises(NotSupported, decorated(self.dummy), self)
        # Check if call can be done if version is exactly the same
        decorated = TLVersion(self._tl_version, strict=True)
        decorated(self.dummy)(self)

    def test_ignore(self):
        """Ignore version checks"""
        self.assertEquals(TLVersion.IGNORE, False)
        TLVersion.IGNORE = True
        for version in ("1.0", "0.9", "1.1"):
            decorated = TLVersion(str(version))
            self.assertEquals(decorated.IGNORE, True)
            decorated(self.dummy)(self)
