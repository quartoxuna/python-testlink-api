#!/usr/bin/env python
# -*- coding: utf-8 -*.

"""TestProject Object"""

# IMPORTS
from testlink.objects.tl_object import TestlinkObjectFromAPIBuilder
from testlink.objects.tl_object import TestlinkObjectBuilder
from testlink.objects.tl_object import TestlinkObject
from testlink.objects.tl_object import normalize_list

from testlink.objects.tl_testsuite import TestSuite
from testlink.objects.tl_testcase import TestCase
from testlink.objects.tl_testplan import TestPlan
from testlink.objects.tl_attachment import AttachmentMixin

from testlink.exceptions import APIError


class TestProjectFromAPIBuilder(TestlinkObjectFromAPIBuilder):
    """Testlink TestProject Builder for raw Testlink API data

    :param str prefix: Prefix of the project
    :param str description: Description of the project
    :param bool active: Active status of the project
    :param bool public: Public status of the project
    :param str color: Color coding for the project
    :param int testcase_count: Maximum external testcase ID of the project
    :param bool requirement_feature: Status of requirement feature
    :param bool priority_feature: Status of priority feature
    :param bool automation_feature: Status of automation feature
    :param bool inventory_feature: Status of inventory feature
    """

    def __init__(self, *args, **kwargs):
        super(TestProjectFromAPIBuilder, self).__init__(*args, **kwargs)
        self.name = kwargs.get('name', None)
        self.prefix = kwargs.get('prefix', None)
        self.description = kwargs.get('notes', None)
        self.active = kwargs.get('active', None)
        self.public = kwargs.get('is_public', None)
        self.color = kwargs.get('color', None)
        self.testcase_count = kwargs.get('tc_counter', None)

        self.requirement_feature = None
        self.priority_feature = None
        self.automation_feature = None
        self.inventory_feature = None
        if kwargs.get('opt', None):
            options = kwargs.get('opt')
            self.requirement_feature = options['requirementsEnabled']
            self.priority_feature = options['testPriorityEnabled']
            self.automation_feature = options['automationEnabled']
            self.inventory_feature =  options['inventoryEnabled']

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
        # Sanity checks
        assert self.name is not None, "No TestProject name defined"
        assert self.prefix is not None, "No TestProject prefix defined"
        assert self.active is not None, "No TestProject active status defined"
        assert self.public is not None, "No TestProject public status defined"
        assert self.testcase_count >= 0, "Invalid testcase count for TestProject: {}".format(self.testcase_count)

        return TestProject(
            # TestProject
            name=self.name,
            prefix=self.prefix,
            description=self.description,
            active=self.active,
            public=self.public,
            color=self.color,
            testcase_count=self.testcase_count,
            requirement_feature=self.requirement_feature,
            priority_feature=self.priority_feature,
            automation_feature=self.automation_feature,
            inventory_feature=self.inventory_feature,
            # TestlinkObject
            testlink_id=self.testlink_id,
            parent_testlink=self.testlink,
        )


class TestProjectBuilder(TestlinkObjectBuilder,
                         TestProjectFromAPIBuilder):
    """General TestProject Builder"""

    def __init__(self, *args, **kwargs):
        super(TestProjectBuilder, self).__init__(*args, **kwargs)

    def with_name(self, name):
        """Set the name of the TestProject
        :type name: str"""
        self.name = name
        return self

    def with_prefix(self, prefix):
        """Set the prefix of the TestProject
        :type prefix: str"""
        self.prefix = prefix
        return self

    def with_description(self, description):
        """Set the description of the TestProject
        :type description: str"""
        self.description = description
        return self

    def is_active(self, active=True):
        """Set the TestProject status to active
        :type active: bool"""
        self.active = active
        return self

    def is_not_active(self):
        """Set the TestProject status to inactive"""
        self.active = False
        return self

    def is_public(self, public=True):
        """Set the TestProject visibility to public
        :type public: bool"""
        self.public = public
        return self

    def is_not_public(self):
        """Set the TestProject visibility to not public"""
        self.public = False
        return self

    def with_color(self, color):
        """Set the color coding for the TestProject
        :type color: str"""
        self.color = color
        return self

    def with_testcase_count(self, testcase_count):
        """Set the currently highest external testcase ID for the TestProject
        :type testcase_count: int"""
        self.testcase_count = testcase_count
        return self

    def with_requirement_feature(self, requirement_feature=True):
        """Set the status for the requirement feature of the TestProject
        :type requirement_feature: bool"""
        self.requirement_feature = requirement_feature
        return self

    def without_requirement_feature(self):
        """Disables the requirement feature for the TestProject"""
        self.requirement_feature = False
        return self

    def with_priority_feature(self, priority_feature=True):
        """Set the status for the priority feature of the TestProject
        :type priority_feature: bool"""
        self.priority_feature = priority_feature
        return self

    def without_priority_feature(self):
        """Disables the priority feature for the TestProject"""
        self.priority_feature = False
        return self

    def with_automation_feature(self, automation_feature=True):
        """Set the status for the automation feature of the TestProject
        :type automation_feature: bool"""
        self.automation_feature = automation_feature
        return self

    def without_automation_feature(self):
        """Disables the automation feature for the TestProject"""
        self.automation_feature = False
        return self

    def with_inventory_feature(self, inventory_feature=True):
        """Set the status for the inventory feature of the TestProject
        :type inventory_feature: bool"""
        self.inventory_feature = inventory_feature
        return self

    def without_inventory_feature(self):
        """Disables the inventory feature for the TestProject"""
        self.inventory_feature = False
        return self


class TestProject(TestlinkObject, AttachmentMixin):
    """Testlink TestProject

    :param str name: Name of the TestProject
    :param str prefix: Prefix of the TestProject
    :param str description: Description of the TestProject
    :param bool active: Status of the TestProject
    :param bool public: Visibility of the TestProject
    :param str color: Color coding of the TestProject
    :param int testcase_count: Currently highest external testcase ID within TestProject
    :param bool requirement_feature: Status of the requirement feature for the TestProject
    :param bool priority_feature: Status of the priority feature for the TestProject
    :param bool automation_feature: Status of the automation feature for the TestProject
    :param bool inventory_feature: Status of the inventory feature for the TestProject
    """

    def __init__(self, *args, **kwargs):
        super(TestProject, self).__init__(*args, **kwargs)
        self.__name = kwargs['name']
        self.__prefix = kwargs['prefix']
        self.__description = kwargs['description']
        self.__active = kwargs['active']
        self.__public = kwargs['public']
        self.__color = kwargs['color']
        self.__testcase_count = kwargs['testcase_count']
        self.__requirement_feature = kwargs['requirement_feature']
        self.__priority_feature = kwargs['priority_feature']
        self.__automation_feature = kwargs['automation_feature']
        self.__inventory_feature = kwargs['inventory_feature']

    def __str__(self):
        return "{}: {}".format(self.__class__.__name__, self.name)

    @staticmethod
    def builder(*args, **kwargs):
        return TestProjectBuilder(*args, **kwargs)

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
        """Returns all Testplans for the current TestProject
        :rtype: Iterator[TestPlan]"""
        for data in self.testlink.api.getProjectTestPlans():
            yield TestPlan.builder(**data)\
                  .from_testproject(self)\
                  .from_testlink(self.testlink)\
                  .build()

    @property
    def testsuites(self):
        """Returns all TestSuites for the current TestProject
        :rtype: Iterator[TestSuite]"""
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
                response = self._api.getTestCaseIdByName(name, testprojectname=self.name)
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
            response = self._api.getTestCase(_id, ext, version)
            # Server response is a list
            if len(response) == 1:
                response = response[0]

            yield TestCase(api=self._api, parent_testproject=self, **response)
        else:
            # Get all TestCases for the TestProject
            params["name"] = name
            params["external_id"] = external_id
            params["version"] = version
            for suite in self.iterTestSuite():
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
        return normalize_list([c for c in self.iterTestCase(name, external_id, **params)])
