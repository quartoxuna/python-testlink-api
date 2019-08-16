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
from testlink.objects.tl_reqspec import RequirementSpecification
from testlink.objects.testplan import TestPlan
from testlink.objects.tl_attachment import IAttachmentGetter

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
        self.active = bool(kwargs.get('active', False))
        self.public = bool(kwargs.get('is_public', None))
        self.color = kwargs.get('color', None)
        self.testcase_count = int(kwargs.get('tc_counter', 0))

        self.requirement_feature = None
        self.priority_feature = None
        self.automation_feature = None
        self.inventory_feature = None
        if kwargs.get('opt', None):
            options = kwargs.get('opt')
            self.requirement_feature = bool(options['requirementsEnabled'])
            self.priority_feature = bool(options['testPriorityEnabled'])
            self.automation_feature = bool(options['automationEnabled'])
            self.inventory_feature = bool(options['inventoryEnabled'])

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
            _id=self._id,
            parent_testlink=self.testlink,
        )


class TestProjectBuilder(TestProjectFromAPIBuilder):
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


class TestProject(TestlinkObject, IAttachmentGetter):
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
