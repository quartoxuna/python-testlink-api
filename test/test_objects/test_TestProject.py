#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@author: Kai Borowiak
@summary: TestSuite for testlink.objects.TestProject
"""

# IMPORTS
import random
import string
import unittest
from testlink.objects.tl_testproject import TestProject


def randput(length=10): return "".join([random.choice(string.letters) for _ in xrange(random.randint(1, length))])


class TestProjectTests(unittest.TestCase):
    """TestProject Object Tests"""

    def __init__(self, *args, **kwargs):
        super(TestProjectTests, self).__init__(*args, **kwargs)
        self._testMethodDoc = "TestProject: " + self._testMethodDoc

    def test__str__(self):
        """String representation"""
        name = randput()
        obj = TestProject(name=name)
        _string = str(obj)
        self.assertEqual(_string, "%s" % name)
