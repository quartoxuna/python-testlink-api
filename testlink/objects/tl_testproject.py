#!/usr/bin/env python
# -*- coding: utf-8 -*.

# IMPORTS
from testlink.objects.tl_object import TestlinkObjectFromAPIBuilder
from testlink.objects.tl_object import TestlinkObjectBuilder
from testlink.objects.tl_object import TestlinkObject

from testlink.objects.tl_testsuite import TestSuite
from testlink.objects.tl_testcase import TestCase
from testlink.objects.tl_testplan import TestPlan
from testlink.objects.tl_attachment import AttachmentMixin

from testlink.exceptions import APIError


class TestProjectFromAPIBuilder(TestlinkObjectFromAPIBuilder):
    """Testlink TestProject Builder for raw Testlink API data

    :ivar str prefix: Prefix of the project
    :ivar str description: Description of the project
    :ivar bool active: Active status of the project
    :ivar bool public: Public status of the project
    :ivar str color: Color coding for the project
    :ivar int testcase_count: Maximum external testcase ID of the project
    :ivar bool requirement_feature: Status of requirement feature
    :ivar bool priority_feature: Status of priority feature
    :ivar bool automation_feature: Status of automation feature
    :ivar bool inventory_feature: Status of inventory feature
    """

    def __init__(self, *args, **kwargs):
        self.name = kwargs.pop('name', None)
        self.prefix = kwargs.pop('prefix', None)
        self.description = kwargs.pop('notes', None)
        self.active = kwargs.pop('active', None)
        self.public = kwargs.pop('is_public', None)
        self.color = kwargs.pop('color', None)
        self.testcase_count = kwargs.pop('tc_counter', None)

        self.requirement_feature = None
        self.priority_feature = None
        self.automation_feature = None
        self.inventory_feature = None
        if kwargs.get('opt', None):
            options = kwargs.pop('opt')
            self.requirement_feature = options['requirementsEnabled']
            self.priority_feature = options['testPriorityEnabled']
            self.automation_feature = options['automationEnabled']
            self.inventory_feature =  options['inventoryEnabled']
        super(TestProjectFromAPIBuilder, self).__init__(*args, **kwargs)

        # Fix types
        if self.active is not None:
            self.active = bool(int(self.active))
        if self.public is not None:
            self.public = bool(int(self.public))
        if self.requirement_feature is not None:
            self.requirement_feature = bool(int(self.requirement_feature))
        if self.priority_feature is not None:
            self.priority_feature = bool(int(self.priority_feature))
        if self.automation_feature is not None:
            self.automation_feature = bool(int(self.automation_feature))
        if self.inventory_feature is not None:
            self.inventory_feature = bool(int(self.inventory_feature))
        if self.testcase_count is not None:
            self.testcase_count = int(self.testcase_count)

    def build(self):
        """Generates a new TestProject"""
        # Call Sanity checks of parent class
        super(TestProjectFromAPIBuilder, self).build()

        # Sanity checks
        assert self.name is not None, "No TestProject name defined"
        assert self.prefix is not None, "No TestProject prefix defined"
        assert self.active is not None, "No TestProject active status defined"
        assert self.public is not None, "No TestProject public status defined"
        assert self.testcase_count >= 0, "Invalid testcase count for TestProject: {}".format(self.testcase_count)

        return TestProject(self)


class TestProjectBuilder(TestlinkObjectBuilder,
                         TestProjectFromAPIBuilder):
    """General TestProject Builder"""

    def __init__(self, *args, **kwargs):
        super(TestProjectBuilder, self).__init__(*args, **kwargs)

    def with_name(self, name):
        """Set the name of the TestProject

        :param str name: TestProject name
        :rtype: TestProjectBuilder
        """
        self.name = name
        return self

    def with_prefix(self, prefix):
        """Set the prefix of the TestProject

        :param str prefix: TestProject prefix
        :rtype: TestProjectBuilder
        """
        self.prefix = prefix
        return self

    def with_description(self, description):
        """Set the description of the TestProject

        :param str description: TestProject Description
        :rtype: TestProjectBuilder
        """
        self.description = description
        return self

    def is_active(self, active=True):
        """Set the TestProject status to active

        :param bool active: TestProject active status
        :rtype: TestProjectBuilder
        """
        self.active = active
        return self

    def is_not_active(self):
        """Set the TestProject status to inactive

        :rtype: TestProjectBuilder
        """
        self.active = False
        return self

    def is_public(self, public=True):
        """Set the TestProject visibility to public

        :param bool public: TestProject public status
        :rtype: TestProjectBuilder
        """
        self.public = public
        return self

    def is_not_public(self):
        """Set the TestProject visibility to not public

        :rtype: TestProjectBuilder
        """
        self.public = False
        return self

    def with_color(self, color):
        """Set the color coding for the TestProject

        :param color str: TestProject color code
        """
        self.color = color
        return self

    def with_testcase_count(self, testcase_count):
        """Set the currently highest external testcase ID for the TestProject

        :param int testcase_count: TestProject testcase count
        :rtype: TestProjectBuilder
        """
        self.testcase_count = testcase_count
        return self

    def with_requirement_feature(self, requirement_feature=True):
        """Set the status for the requirement feature of the TestProject

        :param bool requirement_feature: TestProject requirement feature status
        :rtype: TestProjectBuilder
        """
        self.requirement_feature = requirement_feature
        return self

    def without_requirement_feature(self):
        """Disables the requirement feature for the TestProject

        :rtype: TestProjectBuilder
        """
        self.requirement_feature = False
        return self

    def with_priority_feature(self, priority_feature=True):
        """Set the status for the priority feature of the TestProject

        :param bool priority_feature: TestProject priority feature status
        :rtype: TestProjectBuilder
        """
        self.priority_feature = priority_feature
        return self

    def without_priority_feature(self):
        """Disables the priority feature for the TestProject

        :rtype: TestProjectBuilder
        """
        self.priority_feature = False
        return self

    def with_automation_feature(self, automation_feature=True):
        """Set the status for the automation feature of the TestProjecta

        :param bool automation_feature: TestProject automation feature status
        :rtype: TestProjectBuilder
        """
        self.automation_feature = automation_feature
        return self

    def without_automation_feature(self):
        """Disables the automation feature for the TestProject

        :rtype: TestProjectBuilder
        """
        self.automation_feature = False
        return self

    def with_inventory_feature(self, inventory_feature=True):
        """Set the status for the inventory feature of the TestProject

        :param bool inventory_feature: TestProject inventory feature status
        :rtype: TestProjectBuilder
        """
        self.inventory_feature = inventory_feature
        return self

    def without_inventory_feature(self):
        """Disables the inventory feature for the TestProject

        :rtype: TestProjectBuilder
        """
        self.inventory_feature = False
        return self


class TestProject(AttachmentMixin, TestlinkObject):
    """Testlink TestProject

    :ivar str name: Name of the TestProject
    :ivar str prefix: Prefix of the TestProject
    :ivar str description: Description of the TestProject
    :ivar bool active: Status of the TestProject
    :ivar bool public: Visibility of the TestProject
    :ivar str color: Color coding of the TestProject
    :ivar int testcase_count: Currently highest external testcase ID within TestProject
    :ivar bool requirement_feature: Status of the requirement feature for the TestProject
    :ivar bool priority_feature: Status of the priority feature for the TestProject
    :ivar bool automation_feature: Status of the automation feature for the TestProject
    :ivar bool inventory_feature: Status of the inventory feature for the TestProject

    :ivar Iterator[TestSuite] testsuites: TestSuite of the TestProject
    :ivar Iterator[TestPlan] testplans: TestPlans of the TestProject
    """

    def __init__(self, builder, *args, **kwargs):
        super(TestProject, self).__init__(builder, *args, **kwargs)
        self.__name = builder.name
        self.__prefix = builder.prefix
        self.__description = builder.description
        self.__active = builder.active
        self.__public = builder.public
        self.__color = builder.color
        self.__testcase_count = builder.testcase_count
        self.__requirement_feature = builder.requirement_feature
        self.__priority_feature = builder.priority_feature
        self.__automation_feature = builder.automation_feature
        self.__inventory_feature = builder.inventory_feature

    def __str__(self):
        return "{}: {}".format(self.__class__.__name__, self.name)

    @staticmethod
    def builder(**api_data):
        """Generate new TestProjectBuilder

        :param api_data: Raw API data
        :rtype: TestProjectBuilder
        """
        return TestProjectBuilder(**api_data)

    @property
    def name(self):
        return self.__name

    @property
    def prefix(self):
        return self.__prefix

    @property
    def description(self):
        return self.__description

    @property
    def active(self):
        return self.__active

    @property
    def public(self):
        return self.__public

    @property
    def color(self):
        return self.__color

    @property
    def testcase_count(self):
        return self.__testcase_count

    @property
    def requirement_feature(self):
        return self.__requirement_feature

    @property
    def priority_feature(self):
        return self.__priority_feature

    @property
    def automation_feature(self):
        return self.__automation_feature

    @property
    def inventory_feature(self):
        return self.__inventory_feature

    @property
    def testplans(self):
        for data in self.testlink.api.getProjectTestPlans(self.id):
            yield TestPlan.builder(**data)\
                  .from_testproject(self)\
                  .from_testlink(self.testlink)\
                  .build()

    @property
    def testsuites(self):
        # DFS - Deep-First Search
        # First, return all first level testsuite
        for data in self.testlink.api.getFirstLevelTestSuitesForTestProject(self.id):
            testsuite = TestSuite.builder(**data)\
                        .from_testproject(self)\
                        .from_testlink(self.testlink)\
                        .build()
            yield testsuite

            # Then, return all nested testsuites
            # for that particular testsuite
            for nested in testsuite.testsuites:
                yield nested

    def iterTestCase(self, name=None, external_id=None, version=None, **params):
        """Iterates over TestCases specified by parameters
        @param name: The name of the wanted TestCase
        @type name: str
        @param external_id: The external ID of the TestCase
        @type external_id: int
        @param version: Version of the TestCase
        @type version: int
        @param params: Other params for TestCase
        @type params: dict
        @returns: Matching TestCases
        @rtype: generator
        """
        _id = params.get('id')
        # Check if simple API calls can be done
        if name and not _id:
            try:
                response = self.testlink.api.getTestCaseIdByName(name, testprojectname=self.name)
                # If we got more than one TestCase, ignore the name
                if len(response) == 1:
                    _id = response[0]['id']
            except APIError, ae:
                if ae.error_code == 5030:
                    # If no testcase has been found here,
                    # there is no need, to search any further
                    return
                else:
                    raise

        # If we have the id or external id, try to get the testcase by that
        if _id or external_id or version:
            if external_id:
                ext = "%s-%s" % (str(self.prefix), str(external_id))
            else:
                ext = None
            response = self.testlink.api.getTestCase(_id, ext, version)
            # Server response is a list
            if len(response) == 1:
                response = response[0]

            yield TestCase(api=self.testlink.api, parent_testproject=self, **response)
        else:
            # Get all TestCases for the TestProject
            params["name"] = name
            params["external_id"] = external_id
            params["version"] = version
            for suite in self.testsuites:
                for case in suite.iterTestCase(**params):
                    yield case

    def getTestCase(self, name=None, external_id=None, **params):
        """Returns all TestCases specified by parameters
        @param name: The name of the wanted TestCase
        @type name: str
        @param external_id: The external ID of the TestCase
        @type external_id: int
        @param params: Other params for TestCase
        @type params: dict
        @returns: Matching TestCases
        @rtype: mixed
        """
        return [c for c in self.iterTestCase(name, external_id, **params)]
