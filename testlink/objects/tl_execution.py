#!/usr/bin/env python
# -*- coding: utf-8 -*-

# IMPORTS
from datetime import datetime

from testlink.objects.tl_object import TestlinkObjectFromAPIBuilder
from testlink.objects.tl_object import TestlinkObjectBuilder
from testlink.objects.tl_object import TestlinkObject

from testlink.enums import ExecutionStatus
from testlink.enums import ExecutionType


class ExecutionFromAPIBuilder(TestlinkObjectFromAPIBuilder):
    """Testlink Execution Builder for raw Testlink API data

    :ivar int testplan_id: Internal ID of parent TestPlan
    :ivar int build_id: Internal ID of the parent Build
    :ivar int platform_id: Internal ID of the parent Platform
    :ivar int tcversion_id: Internal ID of the parent TestCaseVersion
    :ivar int tcversion_number: Version Number of the TestCaseVersion
    :ivar ExecutionStatus status: Status of the Execution
    :ivar str notes: Notes of the Execution
    :ivar ExecutionType execution_type: The type of the Execution
    :ivar datetime.datetime execution_ts: The execution time
    :ivar float duration: The duration of the Execution in minutes
    :ivar int tester_id: The internal ID of the tester
    """

    def __init__(self, *args, **kwargs):
        self.testplan_id = kwargs.pop('testplan_id', None)
        self.build_id = kwargs.pop('build_id', None)
        self.platform_id = kwargs.pop('platform_id', None)
        self.tcversion_id = kwargs.pop('tcversion_id', None)
        self.tcversion_number = kwargs.pop('tcversion_number', None)
        self.status = kwargs.pop('status', None)
        self.notes = kwargs.pop('notes', None)
        self.execution_type = kwargs.pop('execution_type', None)
        self.execution_ts = kwargs.pop('execution_ts', None)
        self.duration = kwargs.pop('duration', None)
        self.tester_id = kwargs.pop('tester_id', None)
        super(ExecutionFromAPIBuilder, self).__init__(*args, **kwargs)

        # Fix types
        if self.testplan_id:
            self.testplan_id = int(self.testplan_id)
        if self.build_id:
            self.build_id = int(self.build_id)
        if self.platform_id:
            self.platform_id = int(self.platform_id)
        if self.tcversion_id:
            self.tcversion_id = int(self.tcversion_id)
        if self.tcversion_number:
            self.tcversion_number = int(self.tcversion_number)
        if self.status:
            self.status = ExecutionStatus(self.status)
        if self.execution_type:
            self.execution_type = ExecutionType(int(self.execution_type))
        if self.execution_ts:
            self.execution_ts = datetime.strptime(str(self.execution_ts), Execution.DATETIME_FORMAT)
        if self.duration:
            self.duration = float(self.duration)
        if self.tester_id:
            self.tester_id = int(self.tester_id)


class ExecutionBuilder(TestlinkObjectBuilder,
                       ExecutionFromAPIBuilder):
    """General Execution Builder"""

    def __init__(self, *args, **kwargs):
        self.parent_testplan = kwargs.pop('testplan', None)
        self.parent_build = kwargs.pop('build', None)
        self.parent_platform = kwargs.pop('platform', None)
        self.testcase = kwargs.pop('testcase', None)
        self.tester = kwargs.pop('tester', None)
        super(ExecutionBuilder, self).__init__(*args, **kwargs)

    def from_testplan(self, testplan):
        """Set the parent TestPlan for the Execution

        :param TestPlan testplan: The TestPlan the Execution was made to
        """
        self.parent_testplan = testplan
        self.testplan_id = testplan.id
        return self

    def from_build(self, build):
        """Set the parent Build for the Execution

        :param Build build: The Build the Execution was made to
        """
        self.parent_build = build
        self.build_id = build.id
        return self

    def from_platform(self, platform):
        """Set the parent Platform for the Execution

        :param Platform platform: The Platform the Execution was made to
        """
        self.parent_platform = platform
        self.platform_id = platform.id
        return self

    def from_testcase(self, testcase):
        """Set the parent TestCase for the Execution

        :param TestCase testcase: The TestCase the Execution was made to
        """
        self.testcase = testcase
        self.tcversion_id = testcase.version.id
        return self

    def with_status(self, status):
        """Set the status of the Execution

        :param ExecutionStatus status: The status of the Execution
        """
        self.status = status
        return self

    def with_notes(self, notes):
        """Set the notes of the Execution

        :param str notes: Notes of the Execution
        """
        self.notes = notes
        return self

    def with_execution_type(self, execution_type):
        """Set the type of the Execution

        :param ExecutionType execution_type: Type of the Execution
        """
        self.execution_type = execution_type
        return self

    def executed_on(self, execution_time):
        """Set the time of the Execution

        :param datetime.datetime execution_time: Time of Execution
        """
        self.execution_ts = execution_time
        return self

    def with_duration(self, duration):
        """Set the duration of the Execution

        :param float duration: The duration of the Execution in minutes
        """
        self.duration = duration
        return self

    def executed_by(self, tester):
        """Set the tester of the Execution

        :param User tester: Executing User
        """
        self.tester = tester
        self.tester_id = tester.id
        return self

    def build(self):
        """Generate a new Execution"""
        # Call Sanity checks of parent class
        super(ExecutionBuilder, self).build()

        # Sanity checks

        return Execution(self)


class Execution(TestlinkObject):
    """Testlink Execution

    :ivar TestPlan testplan: The parent TestPlan
    :ivar Build build: The parent Build
    :ivar Platform platform: The parent Platform
    :ivar TestCase testcase: The executed TestCase
    :ivar ExecutionStatus status: The status of the Execution
    :ivar str notes: Execution notes
    :ivar datetime.datetime execution_ts: The time of the Execution
    :ivar float duration: The duration of the Execution in minutes
    :ivar User tester: The executing User
    """

    def __init__(self, builder, *args, **kwargs):
        """Initializes a new Execution

        :param ExecutionBuilder builder: Builder Object to retireve attributes from
        """
        super(Execution, self).__init__(builder, *args, **kwargs)
        self.__testplan = builder.parent_testplan
        self.__build = builder.parent_build
        self.__platform = builder.parent_platform
        self.__testcase = builder.testcase
        self.__status = builder.status
        self.__notes = builder.notes
        self.__execution_type = builder.execution_type
        self.__execution_ts = builder.execution_ts
        self.__duration = builder.duration
        self.__tester = builder.tester

    def __str__(self):
        return "{}: {}".format(self.__class__.__name__, self.id)

    @staticmethod
    def builder(**api_data):
        """Generate a new ExecutionBuilder

        :param api_data: Raw API data
        :rtype: ExecutionBuilder
        """
        return ExecutionBuilder(**api_data)

    @property
    def testplan(self):
        return self.__testplan

    @property
    def build(self):
        return self.__build

    @property
    def platform(self):
        return self.__platform

    @property
    def testcase(self):
        return self.__testcase

    @property
    def notes(self):
        return self.__notes

    @property
    def status(self):
        return self.__status

    @property
    def execution_type(self):
        return self.__execution_type

    @property
    def execution_ts(self):
        return self.__execution_ts

    @property
    def duration(self):
        return self.__duration

    @property
    def tester(self):
        return self.__tester
