#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@author: Kai Borowiak
@summary: TestSuite for testlink.objects.TestPlan
"""

# IMPORTS
import random
import string
import unittest
from testlink.objects import tl_testplan


def randput(length=10): return "".join([random.choice(string.letters) for _ in xrange(random.randint(1, length))])


class TestPlanTests(unittest.TestCase):
    """TestPlan Object Tests"""

    def __init__(self, *args, **kwargs):
        super(TestPlanTests, self).__init__(*args, **kwargs)
        self._testMethodDoc = "TestPlan: " + self._testMethodDoc

    def test__str__(self):
        """String representation"""
        name = randput()
        obj = tl_testplan.TestPlan(name=name)
        _string = str(obj)
        self.assertEqual(_string, "TestPlan: %s" % name)
