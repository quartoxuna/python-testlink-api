#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@author: Kai Borowiak
@summary: TestSuite for testlink.enums
"""

# IMPORTS
import unittest

class EnumerationTests(unittest.TestCase):
	""" Tests for Enums"""
	def __init__(self,*args,**kwargs):
		super(EnumerationTests,self).__init__(*args,**kwargs)
		self._testMethodDoc = "Enumeration: " + self._testMethodDoc

	def test_ExecutionType(self):
		"""ExecutionType"""
		from testlink.enums import EXECUTION_TYPE as ExecutionType
		self.assertEqual(ExecutionType.MANUAL,1)
		self.assertEqual(ExecutionType.AUTOMATIC,2)

	def test_ImportanceLeveL(self):
		"""ImportanceLevel"""
		from testlink.enums import IMPORTANCE_LEVEL as ImportanceLevel
		self.assertEqual(ImportanceLevel.HIGH,3)
		self.assertEqual(ImportanceLevel.MEDIUM,2)
		self.assertEqual(ImportanceLevel.LOW,1)

	def test_UrgencyLevel(self):
		"""DuplicateStrategy"""
		from testlink.enums import DUPLICATE_STRATEGY as DuplicateStrategy
		self.assertEqual(DuplicateStrategy.NEW_VERSION,"create_new_version")
		self.assertEqual(DuplicateStrategy.GENERATE_NEW,"generate_new")
		self.assertEqual(DuplicateStrategy.BLOCK,"block")

	def test_CustomFieldDetails(self):
		"""CustomFieldDetails"""
		from testlink.enums import CUSTOM_FIELD_DETAILS as CustomFieldDetails
		self.assertEqual(CustomFieldDetails.VALUE_ONLY,"value")

	def test_APIType(self):
		"""APIType"""
		from testlink.enums import API_TYPE as APIType
		self.assertEqual(APIType.XML_RPC,"XML-RPC")
		self.assertEqual(APIType.REST,"REST")

	def test_TestcaseStatus(self):
		"""TestcaseStatus"""
		from testlink.enums import TESTCASE_STATUS as TestcaseStatus
		self.assertEqual(TestcaseStatus.DRAFT,1)
		self.assertEqual(TestcaseStatus.READY_FOR_REVIEW,2)
		self.assertEqual(TestcaseStatus.REVIEW_IN_PROGRESS,3)
		self.assertEqual(TestcaseStatus.REWORK,4)
		self.assertEqual(TestcaseStatus.OBSOLETE,5)
		self.assertEqual(TestcaseStatus.FUTURE,6)
		self.assertEqual(TestcaseStatus.FINAL,7)
