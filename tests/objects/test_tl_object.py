#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@author: Kai Borowiak
@summary: TestSuite for testlink.objects.TestlinkObject
"""

# IMPORTS
import random
import string
import unittest
from testlink.objects.tl_object import TestlinkObject


def randput(length=10): return "".join([random.choice(string.letters) for _ in xrange(random.randint(1, length))])


def randint(length=10): return int("".join([random.choice(string.digits) for _ in xrange(random.randint(1, length))]))


class TestlinkObjectTests(unittest.TestCase):
    """TestlinkObject Object Tests"""

    def __init__(self, *args, **kwargs):
        super(TestlinkObjectTests, self).__init__(*args, **kwargs)
        self._testMethodDoc = "TestlinkObject: " + self._testMethodDoc

    def test__str__(self):
        """String representation"""
        _id = randint()
        name = randput()
        obj = TestlinkObject(_id, name)
        _string = str(obj)
        self.assertEqual(_string, "TestlinkObject (%d) %s" % (_id, name))
