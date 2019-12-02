#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@author: Kai Borowiak
@summary: TestSuite for testlink.enums
"""

# IMPORTS
import unittest

from testlink.enums import ExecutionType
from testlink.enums import ImportanceLevel
from testlink.enums import DuplicateStrategy
from testlink.enums import CustomFieldDetails
from testlink.enums import APIType
from testlink.enums import TestCaseStatus


class EnumerationTests(unittest.TestCase):
    """ Tests for Enums"""
    def __init__(self, *args, **kwargs):
        super(EnumerationTests, self).__init__(*args, **kwargs)
        self._testMethodDoc = 'Enumeration: ' + self._testMethodDoc

    def test_enums(self):
        """Enumerations"""
        self.assertEqual(ExecutionType.MANUAL.value, 1)
        self.assertEqual(ExecutionType.AUTOMATIC.value, 2)

        self.assertEqual(ImportanceLevel.HIGH.value, 3)
        self.assertEqual(ImportanceLevel.MEDIUM.value, 2)
        self.assertEqual(ImportanceLevel.LOW.value, 1)

        self.assertEqual(DuplicateStrategy.NEW_VERSION.value, 'create_new_version')
        self.assertEqual(DuplicateStrategy.GENERATE_NEW.value, 'generate_new')
        self.assertEqual(DuplicateStrategy.BLOCK.value, 'block')

        self.assertEqual(CustomFieldDetails.VALUE_ONLY.value, 'value')

        self.assertEqual(APIType.XML_RPC.value, 'XML-RPC')
        self.assertEqual(APIType.REST.value, 'REST')

        self.assertEqual(TestCaseStatus.DRAFT.value, 1)
        self.assertEqual(TestCaseStatus.READY_FOR_REVIEW.value, 2)
        self.assertEqual(TestCaseStatus.REVIEW_IN_PROGRESS.value, 3)
        self.assertEqual(TestCaseStatus.REWORK.value, 4)
        self.assertEqual(TestCaseStatus.OBSOLETE.value, 5)
        self.assertEqual(TestCaseStatus.FUTURE.value, 6)
        self.assertEqual(TestCaseStatus.FINAL.value, 7)
