#!/usr/bin/env python
# -*- coding: utf-8 -*.

"""TestProject Object"""

# IMPORTS
from testlink.objects.tl_object import TestlinkObject
from testlink.objects.tl_object import normalize_list

from testlink.objects.tl_testsuite import TestSuite
from testlink.objects.tl_testcase import TestCase
from testlink.objects.tl_reqspec import RequirementSpecification
from testlink.objects.tl_testplan import TestPlan
from testlink.objects.tl_attachment import IAttachmentGetter

from testlink.exceptions import APIError


class TestProject(TestlinkObject, IAttachmentGetter):
    """Testlink TestProject representation
    @ivar notes: TestProject notes
    @type notes: str
    @ivar prefix: TestCase prefix within TestProject
    @type prefix: str
    @ivar active: TestProject active flag
    @type active: bool
    @ivar public: TestProject public flag
    @type public: bool
    @ivar requirements_enabled: Requirement Feature flag
    @type requirements_enabled: bool
    @ivar priority_enabled: Test Priority feature flag
    @type priority_enabled: bool
    @ivar automation_enabled: Automation Feature flag
    @type automation_enabled: bool
    @ivar inventory_enabled: Inventory Feature flag
    @type inventory_enabled: bool
    @ivar tc_counter: Current amount of TestCases in TestProject
    @type tc_counter: int
    @ivar color: Assigned color of TestProject
    @type color: str"""

    __slots__ = ("notes", "prefix", "active", "public", "requirements_enabled", "priority_enabled",
                 "automation_enabled", "inventory_enabled", "tc_counter", "color", "_parent_testlink")

    def __init__(self, name="", notes="", prefix="", active="0", is_public="0", tc_counter=0, opt=None, color="",
                 api=None, parent_testlink=None, **kwargs):
        if opt is None:
            opt = dict()
            opt['requirementsEnabled'] = 0
            opt['testPriorityEnabled'] = 0
            opt['automationEnabled'] = 0
            opt['inventoryEnabled'] = 0
        TestlinkObject.__init__(self, kwargs.get('id', -1), name, api)
        IAttachmentGetter.__init__(self)
        self.notes = unicode(notes)
        self.prefix = str(prefix)
        self.active = bool(int(active))
        self.public = bool(int(is_public))
        self.requirements_enabled = bool(int(opt['requirementsEnabled']))
        self.priority_enabled = bool(int(opt['testPriorityEnabled']))
        self.automation_enabled = bool(int(opt['automationEnabled']))
        self.inventory_enabled = bool(int(opt['inventoryEnabled']))
        self.tc_counter = int(tc_counter)
        self.color = str(color)
        self._parent_testlink = parent_testlink

    def __str__(self):
        return "%s" % self.name

    def iterTestPlan(self, name=None, **params):
        """Iterates over TestPlans specified by parameters
        @param name: The name of the TestPlan
        @type name: str
        @param params: Other params for TestPlan
        @type params: dict
        @returns: Matching TestPlans
        @rtype: generator
        """
        # Check if simple API call can be done
        if name and len(params) == 0:
            response = self._api.getTestPlanByName(name, projectname=self.name)
            yield TestPlan(api=self._api, parent_testproject=self, **response[0])
        else:
            # Get all plans and convert them to TestPlan instances
            response = self._api.getProjectTestPlans(self.id)
            plans = [TestPlan(api=self._api, parent_testproject=self, **plan) for plan in response]

            # Filter
            if len(params) > 0:
                params['name'] = name
                for tplan in plans:
                    for key, value in params.items():
                        # Skip None
                        if value is None:
                            continue
                        try:
                            try:
                                if not unicode(getattr(tplan, key)) == unicode(value):
                                    tplan = None
                                    break
                            except AttributeError:
                                # TestPlan has no attribute 'key'
                                # Try to treat as custom field
                                cf_val = self._api.getTestPlanCustomFieldValue(tplan.id, tplan.getTestProject().id, key)
                                if not unicode(cf_val) == unicode(value):
                                    # No match either
                                    tplan = None
                                    break
                        except AttributeError:
                            raise AttributeError("Invalid Search Parameter for TestPlan: %s" % key)
                    if tplan is not None:
                        yield tplan
            # Return all found TestPlans
            else:
                for tplan in plans:
                    yield tplan

    def getTestPlan(self, name=None, **params):
        """Returns all TestPlans specified by parameters
        @param name: The name of the TestPlan
        @type name: str
        @param params: Other params for TestPlan
        @type params: dict
        @returns: Matching TestPlans
        @rtype: mixed
        """
        return normalize_list([p for p in self.iterTestPlan(name, **params)])

    def iterTestSuite(self, name=None, recursive=True, **params):
        """Iterates over TestSuites specified by parameters
        @param name: The name of the wanted TestSuite
        @type name: str
        @param recursive: Search recursive to get all nested TestSuites
        @type recursive: bool
        @param params: Other params for TestSuite
        @type params: dict
        @returns: Matching TestSuites
        @rtype: generator
        """
        # Check if simple API call can be done
        # Since the ID is unique, all other params can be ignored
        _id = params.get('id')
        if _id:
            response = self._api.getTestSuiteById(self.id, _id)
            # We cannot be sure that the found TestSuite resides within the
            # current TestProject, so we have to do a small check using the
            # name of the current TestProject
            # API call returns a dictionary
            node_path = self._api.getFullPath(_id).values()[0]
            if node_path[0] == self.name:
                yield TestSuite(api=self._api, parent_testproject=self, **response)
        else:
            try:
                response = self._api.getFirstLevelTestSuitesForTestProject(self.id)
            except APIError, ae:
                if ae.error_code == 7008:
                    # TestProject has no TestSuites
                    return
                else:
                    raise

            # Bug !
            # Since the API call to getFirstLevelTestSuites does NOT
            # return the details, we have to get it with another API call
            # This has to be done BEFORE the acutal filtering because otherwise
            # we could not filter by the details
            response = [self._api.getTestSuiteById(self.id, suite['id']) for suite in response]
            suites = [TestSuite(api=self._api, parent_testproject=self, **suite) for suite in response]

            # Filter by specified parameters
            if len(params) > 0 or name:
                params['name'] = name
                for tsuite in suites:
                    for key, value in params.items():
                        # Skip None
                        if value is None:
                            continue
                        try:
                            try:
                                if not unicode(getattr(tsuite, key)) == unicode(value):
                                    tsuite = None
                                    break
                            except AttributeError:
                                # Try as custom field
                                cf_val = self._api.getTestSuiteCustomFieldDesignValue(tsuite.id,
                                                                                      tsuite.getTestProject().id,
                                                                                      key)
                                if not unicode(cf_val) == unicode(value):
                                    tsuite = None
                                    break
                        except AttributeError:
                            raise AttributeError("Invalid Search Parameter for TestSuite: %s" % key)
                    if tsuite is not None:
                        yield tsuite
                # If recursive is specified,
                # also search in nestes suites
                if recursive:
                    # For each suite of this level
                    for tsuite in suites:
                        # Yield nested suites that match
                        for s in tsuite.iterTestSuite(recursive=recursive, **params):
                            yield s
            # Return all TestSuites
            else:
                for tsuite in suites:
                    # First return the suites from this level,
                    # then return nested ones if recursive is specified
                    yield tsuite
                    if recursive:
                        for s in tsuite.iterTestSuite(name=name, recursive=recursive, **params):
                            yield s

    def getTestSuite(self, name=None, recursive=True, **params):
        """Returns all TestSuites specified by parameters
        @param name: The name of the wanted TestSuite
        @type name: str
        @param recursive: Search recursive to get all nested TestSuites
        @type recursive: bool
        @param params: Other params for TestSuite
        @type params: dict
        @returns: Matching TestSuites
        @rtype: mixed
        """
        return normalize_list([s for s in self.iterTestSuite(name, recursive, **params)])

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

    def iterRequirementSpecification(self, name=None, recursive=False, **params):
        """Iterates over Requirement Specifications specified by parameters
        @param name: The title of the wanted Requirement Specification
        @type name: str
        @param recursive: Get Specifications recursively
        @type recursive: bool
        @returns: Matching Requirement Specifications
        @rtype: generator
        """
        # No simple API call possible, get all
        response = self._api.getRequirementSpecificationsForTestProject(self.id)
        specs = [RequirementSpecification(api=self._api, parent_testproject=self, **reqspec) for reqspec in response]

        # Filter
        if len(params) > 0 or name:
            params['name'] = name
            for rspec in specs:
                for key, value in params.items():
                    # Skip None
                    if value is None:
                        continue
                    try:
                        try:
                            if not unicode(getattr(rspec, key)) == unicode(value):
                                rspec = None
                                break
                        except AttributeError:
                            # Try to treat as custom field
                            cf_val = self._api.getReqSpecCustomFieldDesignValue(rspec.id,
                                                                                rspec.getTestProject().id,
                                                                                key)
                            if not unicode(cf_val) == unicode(value):
                                rspec = None
                                break
                    except AttributeError:
                        raise AttributeError("Invalid Search Parameter for Requirement Specification: %s" % key)
                if rspec is not None:
                    yield rspec
            # If recursive is specified,
            # also search in nested specs
            if recursive:
                # For each reqspec of this level
                for rspec in specs:
                    # Yield nested specs that match
                    for r in rspec.iterRequirementSpecification(recursive=recursive, **params):
                        yield r
        # Return all Requirement Specifications
        else:
            for rspec in specs:
                # First return the reqspecs from this level,
                # then return nested ones if recursive is specified
                yield rspec
                if recursive:
                    for r in rspec.iterRequirementSpecification(name=name, recursive=recursive, **params):
                        yield r

    def getRequirementSpecification(self, name=None, recursive=False, **params):
        """Returns all Requirement Specifications specified by parameters
        @param name: The title of the wanted Requirement Specification
        @type name: str
        @param recursive: Get Specifications recursively
        @type recursive: bool
        @returns: Matching Requirement Specifications
        @rtype: list
        """
        return normalize_list([r for r in self.iterRequirementSpecification(name, recursive, **params)])

    def iterRequirement(self, name=None, **params):
        """Returns all Requirements specified by paramaters
        @param name: The title of the wanted Requirements
        @type name: str
        @returns: Matching Requirements
        @rtype: generator
        """
        params['name'] = name
        for spec in self.iterRequirementSpecification(recursive=True):
            for req in spec.iterRequirement(**params):
                yield req

    def getRequirement(self, name=None, **params):
        """Returns all Requirements specified by paramaters
        @param name: The title of the wanted Requirements
        @type name: str
        @returns: Matching Requirements
        @rtype: list
        """
        return normalize_list([r for r in self.iterRequirement(name, **params)])
