#!/usr/bin/env python
# -*- coding: utf-8 -*-
# pylint: disable=C0103

"""
@author: Kai Borowiak
@summary: TestSuite for testlink.objects.TestProject
"""

# IMPORTS
import unittest

from .. import randput

from testlink.objects.tl_testproject import TestProject

class TestProjectTests(unittest.TestCase):
    """TestProject Object Tests"""

    def __init__(self, *args, **kwargs):
        super(TestProjectTests, self).__init__(*args, **kwargs)
        self._testMethodDoc = "TestProject: " + self._testMethodDoc

    def test__str__(self):
        """String representation"""
        name = randput()
        obj = TestProject(name=name)
        string = str(obj)
        self.assertEqual(string, "%s" % name)
