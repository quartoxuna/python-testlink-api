#!/usr/bin/env python
# -*- coding: utf-8 -*-
# pylint: disable=C0103
# pylint: disable=C0301

"""
@author: Kai Borowiak
@summary: TestCase for testlink.objects.TestCase.Execution
"""

# IMPORTS
import unittest
import datetime

from .. import randput, randint

from testlink.objects import TestCase

class ExecutionTests(unittest.TestCase):
    """Execution Object Tests"""

    def __init__(self, *args, **kwargs):
        super(ExecutionTests, self).__init__(*args, **kwargs)
        self._testMethodDoc = "TestCase.Execution: " + self._testMethodDoc

    def test__str__(self):
        """String representation"""
        id_ = randint()
        status = randput(1)
        notes = randput()

        obj = TestCase.Execution(id=id_, status=status, notes=notes)
        string = str(obj)
        self.assertEqual(string, "Execution (%d) [%s] %s" % (id_, status, notes))

    def test_datetime_conversion(self):
        """Datetime Conversion"""
        date = "2020-10-20 12:34:45"
        ts = datetime.datetime.strptime(date, TestCase.DATETIME_FORMAT)

        execution = TestCase.Execution(execution_ts=date)
        self.assertEquals(ts, execution.execution_ts)
