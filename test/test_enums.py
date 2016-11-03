#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@author: Kai Borowiak
@summary: TestSuite for testlink.enums
"""

# IMPORTS
import unittest

from testlink.enums import EXECUTION_TYPE as ExecutionType
from testlink.enums import IMPORTANCE_LEVEL as ImportanceLevel
from testlink.enums import DUPLICATE_STRATEGY as DuplicateStrategy
from testlink.enums import CUSTOM_FIELD_DETAILS as CustomFieldDetails
from testlink.enums import API_TYPE as APIType
from testlink.enums import TESTCASE_STATUS as TestcaseStatus

class EnumerationTests(unittest.TestCase):
    """ Tests for Enums"""
    def __init__(self, *args, **kwargs):
        super(EnumerationTests, self).__init__(*args, **kwargs)
        self._testMethodDoc = 'Enumeration: ' + self._testMethodDoc

    def test_enums(self):
        """Enumerations"""
        self.assertEqual(ExecutionType.MANUAL, 1)
        self.assertEqual(ExecutionType.AUTOMATIC, 2)

        self.assertEqual(ImportanceLevel.HIGH, 3)
        self.assertEqual(ImportanceLevel.MEDIUM, 2)
        self.assertEqual(ImportanceLevel.LOW, 1)

        self.assertEqual(DuplicateStrategy.NEW_VERSION, 'create_new_version')
        self.assertEqual(DuplicateStrategy.GENERATE_NEW, 'generate_new')
        self.assertEqual(DuplicateStrategy.BLOCK, 'block')

        self.assertEqual(CustomFieldDetails.VALUE_ONLY, 'value')

        self.assertEqual(APIType.XML_RPC, 'XML-RPC')
        self.assertEqual(APIType.REST, 'REST')

        self.assertEqual(TestcaseStatus.DRAFT, 1)
        self.assertEqual(TestcaseStatus.READY_FOR_REVIEW, 2)
        self.assertEqual(TestcaseStatus.REVIEW_IN_PROGRESS, 3)
        self.assertEqual(TestcaseStatus.REWORK, 4)
        self.assertEqual(TestcaseStatus.OBSOLETE, 5)
        self.assertEqual(TestcaseStatus.FUTURE, 6)
        self.assertEqual(TestcaseStatus.FINAL, 7)
