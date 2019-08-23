#!/usr/bin/env python
# -*- coding: utf-8 -*-

# IMPORTS
from testlink.log import LOGGER

from testlink.objects.tl_object import TestlinkObjectFromAPIBuilder
from testlink.objects.tl_object import TestlinkObjectBuilder
from testlink.objects.tl_object import TestlinkObject

from testlink.objects.tl_build import Build
from testlink.objects.tl_platform import Platform
from testlink.objects.tl_testcase import TestCase

from testlink.exceptions import APIError


class TestPlanFromAPIBuilder(TestlinkObjectFromAPIBuilder):
    """Testlink TestProject Builder for raw Testlink API data

    :ivar str name: Name of the TestPlan
    :ivar str description: Description of the TestPlan
    :ivar bool active: Active status of the plan
    :ivar bool public: Public status of the plan
    :ivar TestProject testproject: Parent TestProject

    .. todo::
        Remove *parent_testproject* from API builder
    """

    def __init__(self, *args, **kwargs):
        self.name = kwargs.pop('name', None)
        self.description = kwargs.pop('notes', None)
        self.active = kwargs.pop('active', None)
        self.public = kwargs.pop('is_public', None)
        self.testproject = kwargs.pop('parent_testproject', None)
        super(TestPlanFromAPIBuilder, self).__init__(*args, **kwargs)

        # Fix types
        if self.active is not None:
            self.active = bool(int(self.active))
        if self.public is not None:
            self.public = bool(int(self.public))

    def build(self):
        """Generate a new TestPlan"""
        # Sanity checks
        # Call Sanity checks of parent class
        super(TestPlanFromAPIBuilder, self).build()

        assert self.name is not None, "No TestPlan name defined"
        assert self.active is not None, "No TestPlan active status defined"
        assert self.public is not None, "No TestPlan public status defined"
        assert self.testproject is not None, "No parent TestProject defined"

        return TestPlan(self)


class TestPlanBuilder(TestlinkObjectBuilder,
                      TestPlanFromAPIBuilder):
    """General TestPlan Builder"""

    def __init__(self, *args, **kwargs):
        super(TestPlanBuilder, self).__init__(*args, **kwargs)

    def with_name(self, name):
        """Set the name of the TestPlan

        :param str name: TestPlan name
        :rtype: TestPlanBuilder
        """
        self.name = name
        return self

    def with_description(self, description):
        """Set the description of the TestPlan

        :param str description: TestPlan description
        :rtype: TestPlanBuilder
        """
        self.description = description
        return self

    def is_active(self, active=True):
        """Set the TestPlan to active

        :param bool active: TestPlan active status
        :rtype: TestPlanBuilder
        """
        self.active = active
        return self

    def is_not_active(self):
        """Set the TestPlan to inactive

        :rtype: TestPlanBuilder
        """
        self.active = False
        return self

    def is_public(self, public=True):
        """Set the TestPlan to public

        :param bool public: TestPlan public status
        :rtype: TestPlanBuilder
        """
        self.public = public
        return self

    def is_not_public(self):
        """Set the TestPlan to not public

        :rtype: TestPlanBuilder
        """
        self.public = False
        return self

    def from_testproject(self, testproject):
        """Set the parent TestProject instance

        :param TestProject testproject: TestPlan parent TestProject
        :rtype: TestPlanBuilder
        """
        self.testproject = testproject
        return self


class TestPlan(TestlinkObject):
    """Testlink TestPlan

    :ivar str name: Name of the TestPlan
    :ivar str description: Description of the TestPlan
    :ivar bool active: Status of the TestPlan
    :ivar bool public: Visibility of the TestPlan
    :ivar TestProject testproject: Parent TestProject instance

    :ivar Iterator[Build]: TestPlan builds
    :ivar Iteratir[Platform]: Testplan platforms
    """

    def __init__(self, builder, *args, **kwargs):
        super(TestPlan, self).__init__(builder, *args, **kwargs)
        self.__name = builder.name
        self.__description = builder.description
        self.__active = builder.active
        self.__public = builder.public
        self.__parent_testproject = builder.testproject

    def __str__(self):
        return "{}: {}".format(self.__class__.__name__, self.name)

    @staticmethod
    def builder(**api_data):
        """Generate a new TestPlanBuilder

        :param api_data: Raw API data
        :rtype: TestPlanBuilder
        """
        return TestPlanBuilder(**api_data)

    @property
    def name(self):
        return self.__name

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
    def testproject(self):
        return self.__parent_testproject

    @property
    def builds(self):
        for data in self.testlink.api.getBuildsForTestPlan(self.id):
            yield Build.builder(**data)\
                  .from_testlink(self.testlink)\
                  .from_testplan(self)\
                  .build()

    @property
    def platforms(self):
        for data in self.testlink.api.getTestPlanPlatforms(self.id):
            yield Platform.builder(**data)\
                  .from_testlink(self.testlink)\
                  .from_testproject(self.testproject)\
                  .from_testplan(self)\
                  .build()

    def iterTestCase(self, name=None, buildid=None, keywordid=None, keywords=None, executed=None, assigned_to=None,
                     execution_type=None, **params):
        """Iterates over Testcases specified by parameters
        @param name: The name of the TestCase
        @type name: str
        @param buildid: The internal ID of the Build
        @type buildid: int
        @param keywordid: The internal ID of the used Keyword
        @type keywordid: int
        @param keywords: Keywords to filter for
        @type keywords: list
        @param executed: Checks if TestCase is executed
        @type executed: bool
        @param assigned_to: Filter by internal ID of assigned Tester
        @type assigned_to: int
        @param execution_type: Filter by execution type
        @type execution_type: ExecutionType
        @param params: Other params for TestCase
        @type params: dict
        @returns: Matching TestCases
        @rtype: generator
        """
        # Get id if specified and remove from params
        _id = None
        if 'id' in params.keys():
            _id = params['id']
            del params['id']

        # Testlink >1.9.2 does not return proper results
        # if API call is made with execution_status='n', but we can
        # filter for it afterwards
        execution_status = None
        if ('execution_status' in params) and (params['execution_status'] != 'n'):
            execution_status = params['execution_status']
            del params['execution_status']

        # Get all available TestCases
        # Use all possible API params to speed up API call
        try:
            response = self.testlink.api.getTestCasesForTestPlan(testprojectid=self.testproject.id,
                                                         testplanid=self.id,
                                                         testcaseid=_id,
                                                         buildid=buildid,
                                                         keywordid=keywordid,
                                                         keywords=keywords,
                                                         executed=executed,
                                                         assignedto=assigned_to,
                                                         executestatus=execution_status,
                                                         executiontype=execution_type,
                                                         getstepsinfo=True)
        except APIError, ae:
            # TestCase not linked to TestPlan
            # Build does not exist in TestPlan
            if ae.error_code in (3030, 3032):
                return
            else:
                raise

        # Check if we have a repsonse
        if len(response) == 0:
            return

        # Normalize result
        testcases = []
        for platforms in response.values():
            if isinstance(platforms, list):
                # No platforms, first nested items are testcases as list
                LOGGER.debug("No Platforms within this testplan")
                for tc in platforms:
                    testcases.append(tc)
            else:
                for platform_id, tc in platforms.items():

                    # Check if filtering for platform_id is requested
                    if 'platform_id' in params:
                        # Filter by platform
                        if int(platform_id) == int(params['platform_id']):
                            testcases.append(tc)
                    else:
                        testcases.append(tc)

        # Remove 'platform_id' from filters since we
        # we already filteres for platform_id
        if 'platform_id' in params:
            del params['platform_id']

        # Initialise TestCase Objects
        cases = [TestCase(api=self.testlink.api, parent_testproject=self.testproject, **case) for case in testcases]

        # Filter
        if len(params) > 0 or name:
            params['name'] = name
            for tcase in cases:
                for key, value in params.items():
                    # Skip None
                    if value is None:
                        continue
                    try:
                        try:
                            if not unicode(getattr(tcase, key)) == unicode(value):
                                # Testcase does not match
                                tcase = None
                                break
                        except AttributeError:
                            # TestCase has no attribute key
                            # Try to treat key as the name of a custom field
                            ext_id = "%s-%s" % (tcase.testproject.prefix, tcase.external_id)
                            cf_val = self.testlink.api.getTestCaseCustomFieldDesignValue(ext_id,
                                                                                 tcase.version,
                                                                                 tcase.testproject.id,
                                                                                 key)
                            if not unicode(cf_val) == unicode(value):
                                # No match either, try next testcase
                                tcase = None
                                break
                    except AttributeError:
                        raise AttributeError("Invalid Search Parameter for TestCase: %s" % key)

                # Yield matching testcase
                if tcase is not None:
                    yield tcase
        else:
            # Return all found TestCases
            for tcase in cases:
                yield tcase

    def getTestCase(self, name=None, buildid=None, keywordid=None, keywords=None, executed=None,
                    assigned_to=None, execution_type=None, **params):
        """Returns all Testcases specified by parameters
        @param name: The name of the TestCase
        @type name: str
        @param buildid: The internal ID of the Build
        @type buildid: int
        @param keywordid: The internal ID of the used Keyword
        @type keywordid: int
        @param keywords: Keywords to filter for
        @type keywords: list
        @param executed: Checks if TestCase is executed
        @type executed: bool
        @param assigned_to: Filter by internal ID of assigned Tester
        @type assigned_to: int
        @param execution_type: Filter by execution type
        @type execution_type: ExecutionType
        @param params: Other params for TestCase
        @type params: dict
        @returns: Matching TestCases
        @rtype: mixed
        """
        return [c for c in self.iterTestCase(name, buildid, keywordid, keywords,
                                                            executed, assigned_to, execution_type, **params)]

    def assignTestCase(self, case, platform=None, execution_order=None, urgency=None):
        """Assigns the specified TestCase to the current TestPlan.
        @param case: TestCase to add to current TestPlan
        @type case: TestCase
        @param platform: <OPTIONAL> Platform to add to
        @type platform: Platform
        @param execution_order: <OPTIONAL> Desired execution order
        @type execution_order: int
        @param urgency: <OPTIONAL> Desired urgency
        @type urgency: enums.UrgencyLevel
        @raises APIError: Could not add TestCase
        """
        if not platform:
            platform = Platform(-1)
        self.testlink.api.addTestCaseToTestPlan(self.testproject.id,
                                        self.id,
                                        "%s-%s" % (self.testproject.prefix,
                                                   str(case.external_id)),
                                        case.version,
                                        platform.id,
                                        execution_order,
                                        urgency)
