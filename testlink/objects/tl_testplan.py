#!/usr/bin/env python
# pylint: disable=line-too-long
# pylint: disable=invalid-name
# pylint: disable=too-many-arguments
# pylint: disable=too-many-locals
# pylint: disable=too-many-branches
# pylint: disable=star-args
# -*- coding: utf-8 -*-

"""TestPlan Object"""

# IMPORTS
from testlink.log import LOGGER as log

from testlink.objects.tl_object import TestlinkObject
from testlink.objects.tl_object import normalize_list

from testlink.objects.tl_build import Build
from testlink.objects.tl_platform import Platform
from testlink.objects.tl_testcase import TestCase

from testlink.exceptions import APIError

class TestPlan(TestlinkObject):
    """Testlink TestPlan representation
    @ivar notes: TestPlan notes
    @type notes: str
    @ivar active: TestPlan active flag
    @type active: bool
    @ivar public: TestPlan public flag
    @type public: bool
    """

    __slots__ = ("notes", "active", "public", "_parent_testproject")

    def __init__(
            self,\
            name="",\
            notes="",\
            is_public="0",\
            active="0",\
            parent_testproject=None,\
            api=None,\
            **kwargs\
    ):
        TestlinkObject.__init__(self, kwargs.get('id'), name, api)
        self.notes = unicode(notes)
        self.active = bool(int(active))
        self.public = bool(int(is_public))
        self._parent_testproject = parent_testproject

    def __str__(self):
        return "TestPlan: %s" % self.name

    def getTestProject(self):
        """Returns associated TestProject"""
        return self._parent_testproject

    def iterTestProject(self):
        """Returns associated TestProject"""
        yield self._parent_testproject

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

        platforms = [Platform(parent_testplan=self, api=self._api, **platform) for platform in response]

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

    def iterTestCase(
            self,\
            name=None,\
            buildid=None,\
            keywordid=None,\
            keywords=None,\
            executed=None,\
            assigned_to=None,\
            execution_type=None,\
            **params
        ):
        """Iterates over Testcases specified by parameters
        @param name: The name of the TestCase
        @type name: str
        @param id: The internal ID of the TestCase
        @type id: int
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
        _id = params.get('id')
        params.update({'id': None})

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
            response = self._api.getTestCasesForTestPlan(\
                                    testprojectid=self.getTestProject().id,\
                                    testplanid=self.id,\
                                    testcaseid=_id,\
                                    buildid=buildid,\
                                    keywordid=keywordid,\
                                    keywords=keywords,\
                                    executed=executed,\
                                    assignedto=assigned_to,\
                                    executestatus=execution_status,\
                                    executiontype=execution_type,\
                                    getstepsinfo=True\
                                )
        except APIError, ae:
            if ae.error_code == 3030:
                # TestCase not linked to TestPlan
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
                log.debug("No Platforms within this testplan")
                for tc in platforms:
                    testcases.append(tc)
            else:
                for tc in platforms.values():
                    testcases.append(tc)

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
                            cf_val = self._api.getTestCaseCustomFieldDesignValue(ext_id, tcase.version, tcase.getTestProject().id, key)
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

    def getTestCase(
            self,\
            name=None,\
            buildid=None,\
            keywordid=None,\
            keywords=None,\
            executed=None,\
            assigned_to=None,\
            execution_type=None,\
            **params
        ):
        """Returns all Testcases specified by parameters
        @param name: The name of the TestCase
        @type name: str
        @param id: The internal ID of the TestCase
        @type id: int
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
        return normalize_list([c for c in self.iterTestCase(name, buildid, keywordid, keywords, executed, assigned_to, execution_type, **params)])

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
        self._api.addTestCaseToTestPlan(self.getTestProject().id, self.id, "%s-%s" % (self.getTestProject().prefix, str(case.external_id)), case.version, platform.id, execution_order, urgency)

