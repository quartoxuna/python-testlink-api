# pylint: disable=missing-docstring

# IMPORTS
import datetime
import unittest
import mock

from testlink.objects.tl_testcase import TestCaseFromAPIBuilder
from testlink.objects.tl_testcase import TestCase

from testlink.enums import ExecutionType
from testlink.enums import TestCaseStatus
from testlink.enums import ImportanceLevel

from testlink.objects.tl_testcase import TestCaseVersionFromAPIBuilder
from testlink.objects.tl_testcase import TestCaseVersion


class TestCaseFromAPIBuilderTests(unittest.TestCase):

    def test_api_data(self):
        """Test builder initialization with raw API data"""
        data = {'id': '123', 'tc_external_id': '456',
                'name': 'Some TestCase', 'testsuite_id': '789'}
        builder = TestCaseFromAPIBuilder(**data)
        self.assertEqual(builder.testlink_id, 123)
        self.assertEqual(builder.name, "Some TestCase")
        self.assertEqual(builder.external_id, 456)
        self.assertEqual(builder.testsuite_id, 789)


class TestCaseBuilderTests(unittest.TestCase):

    def test_with_id(self):
        """Test setter for Testlink ID"""
        builder = TestCase.builder()
        self.assertEqual(builder, builder.with_id(123))
        self.assertEqual(builder.testlink_id, 123)

    def test_from_testlink(self):
        """Test setter for parent Testlink instance"""
        testlink = mock.MagicMock()
        builder = TestCase.builder()
        self.assertEqual(builder, builder.from_testlink(testlink))
        self.assertEqual(builder.testlink, testlink)

    def test_with_name(self):
        """Test settter for TestCase name"""
        builder = TestCase.builder()
        self.assertEqual(builder, builder.with_name("Some TestCase"))
        self.assertEqual(builder.name, "Some TestCase")

    def test_with_external_id(self):
        """Test setter for TestCase external ID"""
        builder = TestCase.builder()
        self.assertEqual(builder, builder.with_external_id(456))
        self.assertEqual(builder.external_id, 456)

    def test_from_testsuite(self):
        """Test setter for TestCase TestSuite"""
        testsuite = mock.MagicMock()
        builder = TestCase.builder()
        self.assertEqual(builder, builder.from_testsuite(testsuite))
        self.assertEqual(builder.parent_testsuite, testsuite)


class TestCaseVersionFromAPIBuilderTests(unittest.TestCase):

    def test_api_data(self):
        """Test builder initialization with raw API data"""
        data = {}
        builder = TestCaseVersionFromAPIBuilder(**data)
        raise NotImplementedError


class TestCaseVersionBuilderTests(unittest.TestCase):

    def test_with_id(self):
        """Test setter for Testlink ID"""
        builder = TestCaseVersion.builder()
        self.assertEqual(builder, builder.with_id(123))
        self.assertEqual(builder.testlink_id, 123)

    def test_from_testlink(self):
        """Test setter for parent Testlink instance"""
        testlink = mock.MagicMock()
        builder = TestCaseVersion.builder()
        self.assertEqual(builder, builder.from_testlink(testlink))
        self.assertEqual(builder.testlink, testlink)

    def test_with_version(self):
        """Test setter for TestCaseVersion version"""
        builder = TestCaseVersion.builder()
        self.assertEqual(builder, builder.with_version(5))
        self.assertEqual(builder.version, 5)

    def test_with_summary(self):
        """Test setter for TestCaseVersion summary"""
        builder = TestCaseVersion.builder()
        self.assertEqual(builder, builder.with_summary("Some Summary"))
        self.assertEqual(builder.summary, "Some Summary")

    def test_with_preconditions(self):
        """Test setter for TestCaseVersion preconditions"""
        builder = TestCaseVersion.builder()
        self.assertEqual(builder, builder.with_preconditions("Some Preconditions"))
        self.assertEqual(builder.preconditions, "Some Preconditions")

    def test_created_by(self):
        """Test setter for TestCaseVersion author"""
        author = mock.MagicMock()
        author.id = 123
        builder = TestCaseVersion.builder()
        self.assertEqual(builder, builder.created_by(author))
        self.assertEqual(builder.author, author)
        self.assertEqual(builder.author_id, author.id)

    def test_created_on(self):
        """Test setter for TestCaseVersion creation time"""
        creation_ts = datetime.datetime(2019, 12, 10, 12, 34, 56)
        builder = TestCaseVersion.builder()
        self.assertEqual(builder, builder.created_on(creation_ts))
        self.assertEqual(builder.creation_ts, creation_ts)

    def test_updated_by(self):
        """Test setter for TestCaseVersion modifier"""
        modifier = mock.MagicMock()
        modifier.id = 123
        builder = TestCaseVersion.builder()
        self.assertEqual(builder, builder.updated_by(modifier))
        self.assertEqual(builder.modifier, modifier)
        self.assertEqual(builder.modifier_id, modifier.id)

    def test_updated_on(self):
        """Test setter for TestCaseVersion modification time"""
        modification_ts = datetime.datetime(2019, 12, 10, 12, 34, 56)
        builder = TestCaseVersion.builder()
        self.assertEqual(builder, builder.updated_on(modification_ts))
        self.assertEqual(builder.modification_ts, modification_ts)

    def test_with_execution_type(self):
        """Test setter for TestCaseVersion ExecutionType"""
        builder = TestCaseVersion.builder()
        self.assertEqual(builder, builder.with_execution_type(ExecutionType.AUTOMATIC))
        self.assertEqual(builder.execution_type, ExecutionType.AUTOMATIC)

    def test_with_status(self):
        """Test setter for TestCaseVersion TestCaseStatus"""
        builder = TestCaseVersion.builder()
        self.assertEqual(builder, builder.with_status(TestCaseStatus.FINAL))
        self.assertEqual(builder.status, TestCaseStatus.FINAL)

    def test_with_importance(self):
        """Test setter for TestCaseVersion ImportanceLevel"""
        builder = TestCaseVersion.builder()
        self.assertEqual(builder, builder.with_importance(ImportanceLevel.MEDIUM))
        self.assertEqual(builder.importance, ImportanceLevel.MEDIUM)