#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@author: Kai Borowiak
@summary: TestSuite for testlink.objects.TestBuild
"""

# IMPORTS
import random
import string
import unittest
from testlink.objects.tl_build import Build


def randput(length=10): return "".join([random.choice(string.letters) for _ in xrange(random.randint(1, length))])


class BuildTests(unittest.TestCase):
    """Build Object Tests"""

    def __init__(self, *args, **kwargs):
        super(BuildTests, self).__init__(*args, **kwargs)
        self._testMethodDoc = "Build: " + self._testMethodDoc

    def test__str__(self):
        """String representation"""
        name = randput()
        obj = Build(name=name)
        _string = str(obj)
        self.assertEqual(_string, "Build: %s" % name)
