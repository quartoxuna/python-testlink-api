#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""TestPlan Object"""

# IMPORTS
from testlink.log import LOGGER

from testlink.objects.tl_object import TestlinkObjectFromAPIBuilder
from testlink.objects.tl_object import TestlinkObjectBuilder
from testlink.objects.tl_object import TestlinkObject
from testlink.objects.tl_object import normalize_list

from testlink.objects.build import Build
from testlink.objects.tl_platform import Platform
from testlink.objects.tl_testcase import TestCase

from testlink.exceptions import APIError


class TestPlanFromAPIBuilder(TestlinkObjectFromAPIBuilder):
    """Testlink TestProject Builder for raw Testlink API data

    :param str name: Name of the TestPlan
    :param str description: Description of the TestPlan
    :param bool active: Active status of the plan
    :param bool public: Public status of the plan
    :param TestProject testproject: Parent TestProject
    """

    def __init__(self, *args, **kwargs):
        super(TestPlanFromAPIBuilder, self).__init__(*args, **kwargs)
        self.name = kwargs.get('name', None)
        self.description = kwargs.get('notes', None)
        self.active = bool(kwargs.get('active', None))
        self.public = bool(kwargs.get('is_public', None))
        self.testproject = kwargs.get('parent_testproject', None)

    def build(self):
        """Generate a new TestPlan"""
        # Sanity checks
        assert self.name is not None, "No TestPlan name defined"
        assert self.active is not None, "No TestPlan active status defined"
        assert self.public is not None, "No TestPlan public status defined"
        assert self.testproject is not None, "No parent TestProject defined"

        return TestPlan(
            # TestPlan
            name=self.name,
            description=self.description,
            active=self.active,
            public=self.public,
            parent_testproject=self.testproject,
            # TestlinkObject
            _id=self._id,
            parent_testlink=self.testlink,
        )


class TestPlanBuilder(TestPlanFromAPIBuilder):
    """General TestPlan Builder"""

    def __init__(self, *args, **kwargs):
        super(TestPlanBuilder, self).__init__(*args, **kwargs)

    def with_name(self, name):
        """Set the name of the TestPlan
        :type name: str"""
        self.name = name
        return self

    def with_description(self, description):
        """Set the description of the TestPlan
        :type description: str"""
        self.description = description
        return self

    def is_active(self, active=True):
        """Set the TestPlan to active
        :type active: bool"""
        self.active = active
        return self

    def is_not_active(self):
        """Set the TestPlan to inactive"""
        self.active = False
        return self

    def is_public(self, public=True):
        """Set the TestPlan to public
        :type public: bool"""
        self.public = public
        return self

    def is_not_public(self):
        """Set the TestPlan to not public"""
        self.public = False
        return self

    def with_testproject(self, testproject):
        """Set the parent TestProject instance
        :type testproject: TestProject"""
        self.testproject = testproject
        return self


class TestPlan(TestlinkObject):
    """Testlink TestPlan

    :param str name: Name of the TestPlan
    :param str description: Description of the TestPlan
    :param bool active: Status of the TestPlan
    :param bool public: Visibility of the TestPlan
    :param TestProject testproject: Parent TestProject instance
    """

    def __init__(self, *args, **kwargs):
        super(TestlinkObject, self).__init__(*args, **kwargs)
        self.__name = kwargs['name']
        self.__description = kwargs['description']
        self.__active = kwargs['active']
        self.__public = kwargs['public']
        self.__parent_testproject = kwargs['parent_testproject']

    def __str__(self):
        return "{}: {}".format(self.__class__.__name__, self.name)

    @staticmethod
    def builder():
        return TestProjectBuilder()

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

    def iterBuild(self, name=None, **params):
        """Iterates over Builds specified by parameters
        @param name: The name of the Build
        @type name: str
        @param params: Other params for Build
        @type params: dict
        @returns: Macthing Builds
        @rtype: generator
        """
        # No simple API call possible, get all
        response = self._api.getBuildsForTestPlan(self.id)
        builds = [Build(parent_testplan=self, api=self._api, **build) for build in response]

        # Filter
        if len(params) > 0 or name:
            params['name'] = name
            for bd in builds:
                for key, value in params.items():
                    # Skip None
                    if value is None:
                        continue
                    try:
                        if not unicode(getattr(bd, key)) == unicode(value):
                            bd = None
                            break
                    except AttributeError:
                        raise AttributeError("Invalid Search Parameter for Build: %s" % key)
                if bd is not None:
                    yield bd
        # Return all Builds
        else:
            for bd in builds:
                yield bd

    def getBuild(self, name=None, **params):
        """Returns all Builds specified by parameters
        @param name: The name of the Build
        @type name: str
        @param params: Other params for Build
        @type params: dict
        @returns: Macthing Builds
        @rtype: mixed
        """
        return normalize_list([b for b in self.iterBuild(name, **params)])

    def iterPlatform(self, name=None, **params):
        """Iterates over Platforms specified by parameters
        @param name: The name of the Platform
        @type name: str
        @param params: Other params for Platform
        @type params: dict
        @returns: Matching Platforms
        @rtype: generator
        """
        # No simple API call possible, get all
        try:
            response = self._api.getTestPlanPlatforms(self.id)
        except APIError, ae:
            if ae.error_code == 3041:
                # No platforms linked at all
                return
            else:
                raise

        platforms = [Platform(parent_testproject=self, parent_testplan=self, api=self._api, **platform)
                     for platform in response]

        # Filter
        if len(params) > 0 or name:
            params['name'] = name
            for ptf in platforms:
                for key, value in params.items():
                    # Skip None
                    if value is None:
                        continue
                    try:
                        if not unicode(getattr(ptf, key)) == unicode(value):
                            ptf = None
                            break
                    except AttributeError:
                        raise AttributeError("Invalid Search Parameter for Platform: %s" % key)
                if ptf is not None:
                    yield ptf
        # Return all Platforms
        else:
            for ptf in platforms:
                yield ptf

    def getPlatform(self, name=None, **params):
        """Returns all Platforms specified by parameters
        @param name: The name of the Platform
        @type name: str
        @param params: Other params for Platform
        @type params: dict
        @returns: Matching Platforms
        @rtype: mixed
        """
        return normalize_list([p for p in self.iterPlatform(name, **params)])

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
            response = self._api.getTestCasesForTestPlan(testprojectid=self.getTestProject().id,
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
        cases = [TestCase(api=self._api, parent_testproject=self.getTestProject(), **case) for case in testcases]

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
                            ext_id = "%s-%s" % (tcase.getTestProject().prefix, tcase.external_id)
                            cf_val = self._api.getTestCaseCustomFieldDesignValue(ext_id,
                                                                                 tcase.version,
                                                                                 tcase.getTestProject().id,
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
        return normalize_list([c for c in self.iterTestCase(name, buildid, keywordid, keywords,
                                                            executed, assigned_to, execution_type, **params)])

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
        self._api.addTestCaseToTestPlan(self.getTestProject().id,
                                        self.id,
                                        "%s-%s" % (self.getTestProject().prefix,
                                                   str(case.external_id)),
                                        case.version,
                                        platform.id,
                                        execution_order,
                                        urgency)
