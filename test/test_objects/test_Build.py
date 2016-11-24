#!/usr/bin/env python
# -*- coding: utf-8 -*-
# pylint: disable=C0103

"""
@author: Kai Borowiak
@summary: TestSuite for testlink.objects.TestBuild
"""

# IMPORTS
import unittest

from .. import randput

from testlink.objects.tl_build import Build

class BuildTests(unittest.TestCase):
    """Build Object Tests"""

    def __init__(self, *args, **kwargs):
        super(BuildTests, self).__init__(*args, **kwargs)
        self._testMethodDoc = "Build: " + self._testMethodDoc

    def test__str__(self):
        """String representation"""
        name = randput()
        obj = Build(name=name)
        string = str(obj)
        self.assertEqual(string, "Build: %s" % name)
