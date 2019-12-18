#!/usr/bin/env python
# -*- coding: utf-8 -*-

# IMPORTS
from datetime import datetime

from testlink.objects.tl_object import TestlinkObjectFromAPIBuilder
from testlink.objects.tl_object import TestlinkObjectBuilder
from testlink.objects.tl_object import TestlinkObject

from testlink.enums import TestCaseStatus
from testlink.enums import ExecutionType
from testlink.enums import ImportanceLevel


class TestCaseFromAPIBuilder(TestlinkObjectFromAPIBuilder):
    """Testlink TestCase Builder for raw API data

    :ivar int external_id: The external ID of the TestCase
    :ivar str name: The title of the TestCase
    :ivar int testsuite_id: The internal ID of the parent TestSuite
    """

    def __init__(self, *args, **kwargs):
        self.external_id = kwargs.pop('tc_external_id', None)
        self.name = kwargs.pop('name', None)
        self.testsuite_id = kwargs.pop('testsuite_id', None)
        super(TestCaseFromAPIBuilder, self).__init__(*args, **kwargs)

        # Fix types
        if self.external_id:
            self.external_id = int(self.external_id)
        if self.testsuite_id:
            self.testsuite_id = int(self.testsuite_id)


class TestCaseVersionFromAPIBuilder(TestlinkObjectFromAPIBuilder):
    """Testlink TestCaseVersion Builder for war API data

    :ivar int version: Version number of TestCaseVersion
    :ivar int author_id: Internal ID of the Author of the TestCaseVersion
    :ivar datetime.datetime creation_ts: Creation time of the TestCaseVersion
    :ivar int modifier_id: Internal ID of the Modifier of the TestCaseVersion
    :ivar datetime.datetime modification_ts: Modification time of the TestCaseVersion
    :ivar str summary: Summary of the TestCaseVersion
    :ivar str preconditions: Preconditions of the TestCaseVersion
    :ivar ExecutionType execution_type: Execution Type of the TestCaseVersion
    :ivar TestCaseStatus status: Status of the TestCaseVersion
    :ivar ImportanceLevel importance: Importance level of the TestCaseVersion
    """

    def __init__(self, *args, **kwargs):
        self.version = kwargs.pop('version', None)
        self.author_id = kwargs.pop('author_id', None)
        self.creation_ts = kwargs.pop('creation_ts', None)
        self.modifier_id = kwargs.pop('modifier_id', None)
        self.modification_ts = kwargs.pop('modification_ts', None)
        self.summary = kwargs.pop('summary', None)
        self.preconditions = kwargs.pop('preconditions', None)
        self.execution_type = kwargs.pop('execution_type', None)
        self.status = kwargs.pop('status', None)
        self.importance = kwargs.pop('importance', None)
        super(TestCaseVersionFromAPIBuilder, self).__init__(*args, **kwargs)

        # Fix types
        if self.version:
            self.version = int(self.version)
        if self.author_id:
            self.author_id = int(self.author_id)
        if self.creation_ts:
            self.creation_ts = datetime.strptime(self.creation_ts, TestCaseVersion.DATETIME_FORMAT)
        if self.modifier_id:
            self.modifier_id = int(self.modifier_id)
        if self.modification_ts:
            self.modification_ts = datetime.strptime(self.modification_ts,
                                                     TestCaseVersion.DATETIME_FORMAT)
        if self.execution_type:
            self.execution_type = ExecutionType(int(self.execution_type))
        if self.status:
            self.status = TestCaseStatus(int(self.status))
        if self.importance:
            self.importance = ImportanceLevel(int(self.importance))


class TestCaseBuilder(TestlinkObjectBuilder,
                      TestCaseFromAPIBuilder):
    """General TestCase Builder

    :ivar TestSuite testsuite: The parent TestSuite
    """

    def __init__(self, *args, **kwargs):
        self.parent_testsuite = kwargs.pop('parent_testsuite', None)
        super(TestCaseBuilder, self).__init__(*args, **kwargs)

    def with_external_id(self, external_id):
        """Set the external ID of the TestCase

        :param int external_id: The external ID of the TestCase
        :rtype: TestCaseBuilder
        """
        self.external_id = external_id
        return self

    def with_name(self, name):
        """Set the name of the TestCase

        :param str name: The title of the TestCase
        :rtype: TestCaseBuilder
        """
        self.name = name
        return self

    def from_testsuite(self, testsuite):
        """Set the parent TestSuite of the TestCase

        :param TestSuite testsuite: Parent TestSuite
        :rtype: TestCaseBuilder
        """
        self.parent_testsuite = testsuite
        self.testsuite_id = testsuite.id
        return self


class TestCaseVersionBuilder(TestlinkObjectBuilder,
                             TestCaseVersionFromAPIBuilder):
    """General TestCaseVersion Builder

    :ivar User author: The author of the TestCaseVersion
    :ivar User modifier: The last modifier of the TestCaseVersion
    """

    def __init__(self, *args, **kwargs):
        self.author = kwargs.pop('author', None)
        self.modifier = kwargs.pop('modifier', None)
        super(TestCaseVersionBuilder, self).__init__(*args, **kwargs)

    def with_version(self, version):
        """Set the version number of the TestCaseVersion

        :param int version: Version of the TestCaseVersion
        :rtype: TestCaseVersionBuilder
        """
        self.version = version
        return self

    def with_summary(self, summary):
        """Set the summary of the TestCaseVersion

        :param str summary: Summary of the TestCaseVersion
        :rtype: TestCaseVersionBuilder
        """
        self.summary = summary
        return self

    def with_preconditions(self, preconditions):
        """Set the preconditions of the TestCaseVersion

        :param str preconditions: Preconditions of the TestCaseVersion
        :rtype: TestCaseVersionBuilder
        """
        self.preconditions = preconditions
        return self

    def created_by(self, user):
        """Set the author of the TestCaseVersion

        :param User user: Author of the TestCaseVersion
        :rtype:TestCaseVersionBuilder
        """
        self.author = user
        self.author_id = user.id
        return self

    def created_on(self, creation_time):
        """Set the creation time of the TestCaseVersion

        :param datetime.datetime creation_time: Creation time of the TestCaseVersion
        :rtype: TestCaseVersionBuilder
        """
        self.creation_ts = creation_time
        return self

    def updated_by(self, user):
        """Set the last modifier of the TestCaseVersion

        :param User user: Modifier of the TestCaseVersion
        :rtype: TestCaseVersionBuilder
        """
        self.modifier = user
        self.modifier_id = user.id
        return self

    def updated_on(self, modification_time):
        """Set the modification time of the TestCaseVersion

        :param datetime.datetime modification_time: The modification time of the TestCaseVersion
        :rtype: TestCaseVersionBuilder
        """
        self.modification_ts = modification_time
        return self

    def with_execution_type(self, execution_type):
        """Set the execution type of the TestCaseVersion

        :param ExecutionType execution_type: Execution Type of the TestCaseVersion
        :rtype: TestCaseVersionBuilder
        """
        self.execution_type = execution_type
        return self

    def with_status(self, status):
        """Set the status of the TestCaseVersion

        :param TestCaseStatus status: Status of the TestCaseVersion
        :rtype: TestCaseVersionBuilder
        """
        self.status = status
        return self

    def with_importance(self, importance):
        """Set the importance of the TestCaseVersion

        :param ImportanceLevel importance: Importance level of the TestCaseVersion
        :rtype: TestCaseVersionBuilder
        """
        self.importance = importance
        return self


class TestCase(TestlinkObject):
    """Testlink TestCase

    """

    def __init__(self, builder, *args, **kwargs):
        """Initialize a new TestCase

        :param TestCaseBuilder builder: TestCaseBuilder to use
        """
        super(TestCase, self).__init__(builder, *args, **kwargs)
        self.__external_id = builder.external_id
        self.__name = builder.name

    def __str__(self):
        return "{}: {}".format(self.__class__.__name__, self.id)

    @staticmethod
    def builder(**api_data):
        """Generate a new TestCaseBuilder

        :param api_data: Raw API data
        :rtype: TestCaseBuilder
        """
        return TestCaseBuilder(**api_data)

    @property
    def external_id(self):
        return self.__external_id

    @property
    def name(self):
        return self.__name


class TestCaseVersion(TestlinkObject):
    """"Testlink TestCaseVersion

    """

    def __init__(self, builder, *args, **kwargs):
        """Initialize a new TestCaseVersion

        :param TestCaseVersionBuilder builder: TestCaseVersionBuilder to use
        """
        super(TestCaseVersion, self).__init__(builder, *args, **kwargs)

    def __str__(self):
        return "{}: {}".format(self.__class__.__name__, self.id)

    @staticmethod
    def builder(**api_data):
        """Generate a new TestCaseVersionBuilder

        :param api_data: Raw API data
        :rtype: TestCaseVersionBuilder
        """
        return TestCaseVersionBuilder(**api_data)
