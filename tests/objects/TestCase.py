#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@author: Kai Borowiak
@summary: TestCase for testlink.objects.TestTestCase
"""

# IMPORTS
import random
import string
import unittest
from mock import patch, Mock

from testlink.objects.tl_testcase import TestCase


def randput(length=10): return "".join([random.choice(string.letters) for _ in xrange(random.randint(1, length))])


def randint(length=10): return int("".join([random.choice(string.digits) for _ in xrange(random.randint(1, length))]))


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
        _string = str(obj)
        self.assertEqual(_string, "Testcase %s-%s: %s" % (project.prefix, ext_id, name))
