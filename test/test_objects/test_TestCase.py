#!/usr/bin/env python
# -*- coding: utf-8 -*-
# pylint: disable=C0103
# pylint: disable=C0301

"""
@author: Kai Borowiak
@summary: TestCase for testlink.objects.TestTestCase
"""

# IMPORTS
import unittest
from mock import patch, Mock

from .. import randint, randput

from testlink.objects import TestCase

class TestCaseTests(unittest.TestCase):
    """TestCase Object Tests"""

    def __init__(self, *args, **kwargs):
        super(TestCaseTests, self).__init__(*args, **kwargs)
        self._testMethodDoc = "TestCase: " + self._testMethodDoc

    @patch('testlink.objects.TestCase.getTestProject')
    def test__str__(self, _patch):
        """String representation"""
        ext_id = randint()
        name = randput()

        project = Mock()
        project.prefix = randput()
        _patch.return_value = project

        obj = TestCase(name=name, external_id=ext_id)
        string = str(obj)
        self.assertEqual(string, "Testcase %s-%s: %s" % (project.prefix, ext_id, name))
