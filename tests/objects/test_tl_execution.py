# pylint: disable=missing-docstring

# IMPORTS
import unittest
import datetime
import mock

from testlink.objects.tl_execution import ExecutionFromAPIBuilder
from testlink.objects.tl_execution import Execution

from testlink.api.testlink_api import TestlinkAPI

from testlink.objects.tl_testlink import Testlink
from testlink.objects.tl_testplan import TestPlan
from testlink.objects.tl_build import Build
from testlink.objects.tl_platform import Platform

from testlink.enums import ExecutionStatus
from testlink.enums import ExecutionType


class ExecutionFromAPIBuilderTests(unittest.TestCase):

    def test_api_data(self):
        """Test builder initialisation with raw API data"""
        data = {'id': '123', 'testplan_id': '23', 'build_id': '32', 'platform_id': '42',
                'tcversion_id': '456', 'tcversion_number': '3', 'status': 'p',
                'notes': 'Just some notes', 'execution_type': '1',
                'execution_ts': '2019-12-10 12:34:56', 'duration': '32.44',
                'tester_id': '33'}
        builder = ExecutionFromAPIBuilder(**data)
        self.assertEqual(builder.testlink_id, 123)
        self.assertEqual(builder.testplan_id, 23)
        self.assertEqual(builder.build_id, 32)
        self.assertEqual(builder.platform_id, 42)
        self.assertEqual(builder.tcversion_id, 456)
        self.assertEqual(builder.tcversion_number, 3)
        self.assertEqual(builder.status, ExecutionStatus.PASSED)
        self.assertEqual(builder.notes, "Just some notes")
        self.assertEqual(builder.execution_type, ExecutionType.MANUAL)
        self.assertEqual(builder.execution_ts, datetime.datetime(2019, 12, 10, 12, 34, 56))
        self.assertEqual(builder.duration, 32.44)
        self.assertEqual(builder.tester_id, 33)


class ExecutionBuilderTests(unittest.TestCase):

    def test_with_id(self):
        """Test setter for Testlink ID"""
        builder = Execution.builder()
        self.assertEqual(builder, builder.with_id(123))
        self.assertEqual(builder.testlink_id, 123)

    def test_from_testlink(self):
        """Test setter for parent Testlink instance"""
        testlink = mock.MagicMock()
        builder = Execution.builder()
        self.assertEqual(builder, builder.from_testlink(testlink))
        self.assertEqual(builder.testlink, testlink)

    def test_from_testplan(self):
        """Test setter for parent Testplan instance"""
        testplan = mock.MagicMock()
        testplan.id = 23
        builder = Execution.builder()
        self.assertEqual(builder, builder.from_testplan(testplan))
        self.assertEqual(builder.parent_testplan, testplan)
        self.assertEqual(builder.testplan_id, 23)

    def test_from_build(self):
        """Test setter for parent Build instance"""
        build = mock.MagicMock()
        build.id = 23
        builder = Execution.builder()
        self.assertEqual(builder, builder.from_build(build))
        self.assertEqual(builder.parent_build, build)
        self.assertEqual(builder.build_id, 23)

    def test_from_platform(self):
        """Test setter for parent Platform instance"""
        platform = mock.MagicMock()
        platform.id = 23
        builder = Execution.builder()
        self.assertEqual(builder, builder.from_platform(platform))
        self.assertEqual(builder.parent_platform, builder.parent_platform)
        self.assertEqual(builder.platform_id, 23)

    def test_with_status(self):
        """Test setter for Execution status"""
        builder = Execution.builder()
        self.assertEqual(builder, builder.with_status(ExecutionStatus.BLOCKED))
        self.assertEqual(builder.status, ExecutionStatus.BLOCKED)

    def test_with_notes(self):
        """Test setter for Execution notes"""
        builder = Execution.builder()
        self.assertEqual(builder, builder.with_notes("Just some notes"))
        self.assertEqual(builder.notes, "Just some notes")

    def test_with_execution_type(self):
        """Test setter for Execution type"""
        builder = Execution.builder()
        self.assertEqual(builder, builder.with_execution_type(ExecutionType.AUTOMATIC))
        self.assertEqual(builder.execution_type, ExecutionType.AUTOMATIC)

    def test_executed_on(self):
        """Test setter for Execution time"""
        execution_time = datetime.datetime(2019, 12, 10, 12, 34, 56)
        builder = Execution.builder()
        self.assertEqual(builder, builder.executed_on(execution_time))
        self.assertEqual(builder.execution_ts, execution_time)

    def test_executed_by(self):
        """Test setter for Execution Tester"""
        tester = mock.MagicMock()
        tester.id = 23
        builder = Execution.builder()
        self.assertEqual(builder, builder.executed_by(tester))
        self.assertEqual(builder.tester, tester)
        self.assertEqual(builder.tester_id, 23)


class ExecutionTests(unittest.TestCase):

    def test_builder(self):
        """Test initialization with default builder"""
        testlink = mock.MagicMock()
        testplan = mock.MagicMock()
        build = mock.MagicMock()
        platform = mock.MagicMock()
        testcase = mock.MagicMock()
        execution_time = datetime.datetime(2019, 10, 29, 12, 34, 56)
        tester = mock.MagicMock()

        execution = Execution.builder()\
            .with_id(123)\
            .from_testlink(testlink)\
            .from_testplan(testplan)\
            .from_build(build)\
            .from_platform(platform)\
            .from_testcase(testcase)\
            .with_status(ExecutionStatus.FAILED)\
            .with_notes("Just some notes")\
            .with_execution_type(ExecutionType.AUTOMATIC)\
            .executed_on(execution_time)\
            .with_duration(23.23)\
            .executed_by(tester)\
            .build()
        self.assertEqual(execution.id, 123)
        self.assertEqual(execution.testlink, testlink)
        self.assertEqual(execution.testplan, testplan)
        self.assertEqual(execution.build, build)
        self.assertEqual(execution.platform, platform)
        self.assertEqual(execution.testcase, testcase)
        self.assertEqual(execution.status, ExecutionStatus.FAILED)
        self.assertEqual(execution.notes, "Just some notes")
        self.assertEqual(execution.execution_type, ExecutionType.AUTOMATIC)
        self.assertEqual(execution.execution_ts, execution_time)
        self.assertEqual(execution.duration, 23.23)
        self.assertEqual(execution.tester, tester)
