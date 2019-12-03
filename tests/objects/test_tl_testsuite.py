#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@author: Kai Borowiak
@summary: TestSuite for testlink.objects.TestTestSuite
"""

# IMPORTS
import random
import string
import unittest
from testlink.objects import tl_testsuite


def randput(length=10): return "".join([random.choice(string.letters) for _ in xrange(random.randint(1, length))])


class TestSuiteTests(unittest.TestCase):
    """TestSuite Object Tests"""

    def __init__(self, *args, **kwargs):
        super(TestSuiteTests, self).__init__(*args, **kwargs)
        self._testMethodDoc = "TestSuite: " + self._testMethodDoc

    def test__str__(self):
        """String representation"""
        name = randput()
        obj = tl_testsuite.TestSuite(name=name)
        _string = str(obj)
        self.assertEqual(_string, "TestSuite: %s" % name)
