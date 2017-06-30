#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@author: Kai Borowiak
@summary: TestSuite for testlink.objects.TestPlatform
"""

# IMPORTS
import random
import string
import unittest

from testlink.objects.tl_platform import Platform


def randput(length=10): return "".join([random.choice(string.letters) for _ in xrange(random.randint(1, length))])


class PlatformTests(unittest.TestCase):
    """Platform Object Tests"""

    def __init__(self, *args, **kwargs):
        super(PlatformTests, self).__init__(*args, **kwargs)
        self._testMethodDoc = "Platform: " + self._testMethodDoc

    def test__str__(self):
        """String representation"""
        name = randput()
        obj = Platform(name=name)
        _str = str(obj)
        self.assertEqual(_str, "Platform: %s" % name)
