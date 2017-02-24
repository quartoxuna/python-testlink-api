#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@author: Kai Borowiak
@summary: TestSuite for testlink.objects.TestPlatform
"""

# IMPORTS
import unittest

from .. import randput

from testlink.objects.tl_platform import Platform

class PlatformTests(unittest.TestCase):
    """Platform Object Tests"""

    def __init__(self, *args, **kwargs):
        super(PlatformTests, self).__init__(*args, **kwargs)
        self._testMethodDoc = "Platform: " + self._testMethodDoc

    def test__str__(self):
        """String representation"""
        name = randput()
        obj = Platform(name=name)
        string = str(obj)
        self.assertEqual(string, "Platform: %s" % name)
