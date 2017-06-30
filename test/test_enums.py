#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@author: Kai Borowiak
@summary: TestSuite for testlink.enums
"""

# IMPORTS
import unittest

from testlink.enums import EXECUTION_TYPE
from testlink.enums import IMPORTANCE_LEVEL
from testlink.enums import DUPLICATE_STRATEGY
from testlink.enums import CUSTOM_FIELD_DETAILS
from testlink.enums import API_TYPE
from testlink.enums import TESTCASE_STATUS


class EnumerationTests(unittest.TestCase):
    """ Tests for Enums"""
    def __init__(self, *args, **kwargs):
        super(EnumerationTests, self).__init__(*args, **kwargs)
        self._testMethodDoc = 'Enumeration: ' + self._testMethodDoc

    def test_enums(self):
        """Enumerations"""
        self.assertEqual(EXECUTION_TYPE.MANUAL, 1)
        self.assertEqual(EXECUTION_TYPE.AUTOMATIC, 2)

        self.assertEqual(IMPORTANCE_LEVEL.HIGH, 3)
        self.assertEqual(IMPORTANCE_LEVEL.MEDIUM, 2)
        self.assertEqual(IMPORTANCE_LEVEL.LOW, 1)

        self.assertEqual(DUPLICATE_STRATEGY.NEW_VERSION, 'create_new_version')
        self.assertEqual(DUPLICATE_STRATEGY.GENERATE_NEW, 'generate_new')
        self.assertEqual(DUPLICATE_STRATEGY.BLOCK, 'block')

        self.assertEqual(CUSTOM_FIELD_DETAILS.VALUE_ONLY, 'value')

        self.assertEqual(API_TYPE.XML_RPC, 'XML-RPC')
        self.assertEqual(API_TYPE.REST, 'REST')

        self.assertEqual(TESTCASE_STATUS.DRAFT, 1)
        self.assertEqual(TESTCASE_STATUS.READY_FOR_REVIEW, 2)
        self.assertEqual(TESTCASE_STATUS.REVIEW_IN_PROGRESS, 3)
        self.assertEqual(TESTCASE_STATUS.REWORK, 4)
        self.assertEqual(TESTCASE_STATUS.OBSOLETE, 5)
        self.assertEqual(TESTCASE_STATUS.FUTURE, 6)
        self.assertEqual(TESTCASE_STATUS.FINAL, 7)
