#!/usr/bin/env python
# -*- coding: utf-8 -*-
# pylint: disable=C0103

"""
@author: Kai Borowiak
@summary: TestSuite for testlink.objects.TestTestSuite
"""

# IMPORTS
import unittest

from .. import randput

from testlink.objects import TestSuite

class TestSuiteTests(unittest.TestCase):
    """TestSuite Object Tests"""

    def __init__(self, *args, **kwargs):
        super(TestSuiteTests, self).__init__(*args, **kwargs)
        self._testMethodDoc = "TestSuite: " + self._testMethodDoc

    def test__str__(self):
        """String representation"""
        name = randput()
        obj = TestSuite(name=name)
        string = str(obj)
        self.assertEqual(string, "TestSuite: %s" % name)
