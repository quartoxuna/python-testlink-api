# pylint: disable=C0302
# pylint: disable=W0142
# pylint: disable=W0212
# pylint: disable=C0103
# pylint: disable=C0301
# pylint: disable=R0902
# pylint: disable=R0903
# pylint: disable=R0912
# pylint: disable=R0913
# pylint: disable=R0914
# pylint: disable=R0915
# -*- coding: utf-8 -*-

"""
@author: Kai Borowiak
@summary: Object oriented Wrapper for Testlink
"""

# IMPORTS
import time
from datetime import datetime

from testlink.log import LOGGER as log
from testlink.api import Testlink_XML_RPC_API
from testlink.exceptions import NotSupported
from testlink.exceptions import APIError

from testlink.enums import API_TYPE as APIType
from testlink.enums import EXECUTION_TYPE as ExecutionType
from testlink.enums import IMPORTANCE_LEVEL as ImportanceLevel
from testlink.enums import CUSTOM_FIELD_DETAILS as CustomFieldDetails
from testlink.enums import DUPLICATE_STRATEGY as DuplicateStrategy
from testlink.enums import REQSPEC_TYPE as RequirementSpecificationType
from testlink.enums import REQ_STATUS as RequirementStatus
from testlink.enums import REQ_TYPE as RequirementType

__all__ = ["Testlink", "TestProject", "TestPlan", "Build", "Platform",\
        "TestSuite", "TestCase", "RequirementSpecification",\
        "Requirement", "Risk"]

# Global datetime format
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"

# Backwards compatability methods
try:
    _strptime = datetime.strptime
except AttributeError:
    _strptime = lambda date_string, fmt: datetime(*(time.strptime(date_string, fmt)[0:6]))


# Helper method
def normalize_list(res):
    """Normalizes a result list.
    If the specified list is empty, return None.
    If the specified list has only one element, return that element.
    Else return the list as is.
    @param res: Result list
    @type res: list
    @rtype: mixed
    """
    if len(res) == 0:
        return None
    elif len(res) == 1:
        return res[0]
    else:
        return res

class Testlink(object):
    """Testlink Server implementation
    @ivar _url: URL of connected Testlink
    @type _url: str
    @ivar _devkey: Valid Testlink developer key
    @type _devkey: str
    """

    def __init__(self, url, devkey, api=APIType.XML_RPC):
        """Initializes the Testlink Server object
        @param url: Testlink URL
        @type url: str
        @param devkey: Testlink developer key
        @type devkey: str
        """
        self._url = url
        # Init raw API
        if api == APIType.XML_RPC:
            self._api = Testlink_XML_RPC_API(url)
        elif api == APIType.REST:
            raise NotImplementedError()
        self._api_type = api

        # Log API Information
        log_msg = "Testlink %s API Version %s at %s" % (self._api_type, self.getVersion(), self._url)
        log.info(log_msg)

        # Set devkey globally
        self._api._devkey = devkey

    def __str__(self):
        return "Testlink %s API Version %s at %s" % (self._api_type, self.getVersion(), self._url)

    def getVersion(self):
        """Retrieve informations about the used Testlink API
        @return: Version
        @rtype: str
        """
        return str(self._api._tl_version)

    def iterTestProject(self, name=None, **params):
        """Iterates over TestProjects specified by parameters
        @param name: The name of the TestProject
        @type name: str
        @param params: Other params for TestProject
        @type params: dict
        @returns: Matching TestProjects
        @rtype: generator
        """
        # Check if simple API call can be done
        if name and len(params) == 0:
            try:
                response = self._api.getTestProjectByName(name)
                # Since Testlink 1.9.6, the server returns already a dict
                # before, there was a list containing a dict
                # The getVersion() method still returns 1.0 in that case
                # so we have to check by trial and error
                try:
                    response = response[0]
                except KeyError:
                    pass
                yield TestProject(api=self._api, **response)
            except APIError, api_error:
                if api_error.error_code == 7011:
                    # No TestProject found at all
                    return
                else:
                    raise
        else:
            # Get all projects and convert them to TestProject instances
            response = self._api.getProjects()
            projects = [TestProject(api=self._api, **project) for project in response]

            # Filter
            if len(params) > 0:
                params['name'] = name
                for tproject in projects:
                    for key, value in params.items():
                        # Skip None values
                        if value is None:
                            continue
                        try:
                            if not unicode(getattr(tproject, key)) == unicode(value):
                                tproject = None
                                break
                        except AttributeError:
                            raise AttributeError("Invalid Search Parameter for TestProject: %s" % key)
                    # Return found project
                    if tproject is not None:
                        yield tproject
            # Return all found projects
            else:
                for tproject in projects:
                    yield tproject

    def getTestProject(self, name=None, **params):
        """Returns all TestProjects specified by parameters
        @param name: The name of the TestProject
        @type name: str
        @param params: Other params for TestProject
        @type params: dict
        @returns: Matching TestProjects
        @rtype: mixed
        """
        return normalize_list([p for p in self.iterTestProject(name, **params)])

    def createTestProject(self, project):
        """Creates a new TestProject using the current Testlink instance.
        @param project: Project to create
        @type project: TestProject
        """
        return self._api.createTestProject(\
                    name=project.name,\
                    prefix=project.prefix,\
                    notes=project.notes,\
                    active=project.active,\
                    public=project.public,\
                    requirements=project.requirements,\
                    priority=project.priority,\
                    automation=project.automation,\
                    inventory=project.inventory\
                )

    def createTestPlan(self, testplan, testproject):
        """Creates a new TestPlan for the specified TestProject using the current Testlink instance.
        @param testplan: TestPlan to create
        @type testplan: TestPlan
        @param testproject: TestProject to add the Testplan to
        @type testproject: TestProject
        """
        return self._api.createTestPlan(\
                    name=testplan.name,\
                    notes=testplan.notes,\
                    active=testplan.active,\
                    public=testplan.public,\
                    project=testproject.name\
                )

    def createBuild(self, build, testplan):
        """Creates a new Build for the specified TestPlan using the current Testlink instance.
        @param build: Build to create
        @type build: Build
        @param testplan: TestPlan to add the Build to
        @type testplan: TestPlan
        """
        return self._api.createBuild(\
                    name=build.name,\
                    notes=build.notes,\
                    testplanid=testplan.id\
                )

    def createPlatform(self, platform, testproject):
        """Creates a new Platform for the specified TestProject using the current Testlink instance.
        @param platform: Platform to create
        @type platform: Platform
        @param testproject: TestProject to add the Platform to
        @type testproject: TestProject
        """
        return self._api.createPlatform(\
                    platformname=platform.name,\
                    notes=platform.notes,\
                    testprojectname=testproject.name\
                )

    def createTestSuite(self, suite, testproject, parent=None, order=0, on_duplicate=DuplicateStrategy.BLOCK):
        """Creates a new TestSuite for the specified parent objects using the current Testlink instance.
        @param suite: TestSuite to create
        @type suite: TestSuite
        @param parent: Parent TestSuite
        @type parent: mixed
        @param testproject: The parent TestProject
        @type testproject: TestProject
        @param order: Order within the parent object
        @type order: int
        @param on_duplicate: Used duplicate strategy
        @type on_duplicate: testlink.enums.DuplicateStrategy
        """
        duplicate_check = False
        if on_duplicate is not None:
            duplicate_check = True

        parent_id = None
        if parent is not None:
            parent_id = parent.id

        return self._api.createTestSuite(\
                    testsuitename=suite.name,\
                    details=suite.details,\
                    testprojectid=testproject.id,\
                    parentid=parent_id,\
                    order=order,\
                    checkduplicatedname=duplicate_check,\
                    actiononduplicatedname=on_duplicate\
                )

    def createTestCase(self, testcase, testsuite, testproject, authorlogin, order=0, on_duplicate=DuplicateStrategy.BLOCK):
        """Creates a new TestCase for the specifies parent objects using the current Testlink instance.
        @param testcase: TestCase to create
        @type testcase: TestCase
        @param testsuite: Parent TestSuite
        @type testsuite: TestSuite
        @param testproject: Parent TestProject
        @type testproject: TestProject
        @param authorlogin: Author Login to use
        @type authorlogin: str
        @param order: Order within parent TestSuite
        @type order: int
        @param on_duplicate: Used duplicate strategy
        @type on_duplicate: testlink.enums.DuplicateStrategy
        """
        duplicate_check = False
        if on_duplicate is not None:
            duplicate_check = True

        steps = [s.__dict__ for s in testcase.steps]

        return self._api.createTestCase(\
                    testcasename=testcase.name,\
                    testsuiteid=testsuite.id,\
                    testprojectid=testproject.id,\
                    authorlogin=authorlogin,\
                    summary=testcase.summary,\
                    steps=steps,\
                    preconditions=testcase.preconditions,\
                    importance=testcase.importance,\
                    executiontype=testcase.execution_type,\
                    order=order,\
                    customfields=testcase.customfields,\
                    checkduplicatedname=duplicate_check,\
                    actiononduplicatedname=on_duplicate\
                )

    def createRequirementSpecification(self, reqspec, testproject, parent=None):
        """Creates a new RequirementSpecification for the specified testproject using the current Testlink instance.
        @param reqspec: ReqSpec to create
        @type reqspec: RequirementSpecification
        @param testproject: Parent TestProject
        @type testproject: TestProject
        @param parent: <OPTIONAL> Parent ReqSpec
        @type parent: RequirementSpecification
        """
        if parent:
            parent_id = parent.id
        else:
            parent_id = None

        return self._api.createRequirementSpecification(\
                    testprojectid=testproject.id,\
                    parentid=parent_id,\
                    docid=reqspec.doc_id,\
                    title=reqspec.name,\
                    scope=reqspec.scope,\
                    userid=reqspec.author_id,\
                    typ=reqspec.typ\
                )

    def createRequirement(self, requirement, testproject, reqspec):
        """Creates a new Requirement for the specified TestProject and Requirement Specification using the current Testlink instance.
        @param requirement: Requirement to create
        @type requirement: Requirement
        @param testproject: Parent TestProject
        @type testproject: TestProject
        @param reqspec: Parent Requirement Specification
        @type reqspec: RequirementSpecification
        """
        return self._api.createRequirement(\
                    testprojectid=testproject.id,\
                    reqspecid=reqspec.id,\
                    docid=requirement.req_doc_id,\
                    title=requirement.name,\
                    scope=requirement.scope,\
                    userid=requirement.author_id,\
                    typ=requirement.typ,\
                    status=requirement.status\
                )

    def createRisk(self, risk, requirement):
        """Creates a new Risk for the specified Requirement using the current Testlink instance.
        @param risk: Risk to create
        @rype risk: Risk
        @param requirement: Parent Requirement
        @type requirement: Requirement
        """
        return self._api.createRisk(\
                    requirementid=requirement.id,\
                    docid=risk.doc_id,\
                    title=risk.name,\
                    scope=risk.description,\
                    userid=risk.author_id,\
                    coverage=risk.cross_coverage\
                )

class TestlinkObject(object):
    """Abstract Testlink Object
    @ivar id: Internal Testlink Id of the object
    @type id: int
    @ivar name: Internal Testlink name of the object
    @type name: str
    """

    __slots__ = ("id", "name", "_api")

    def __init__(self, _id=None, name="", api=None):
        """Initialises base Testlink object
        @param id: Internal Testlink Id of the object
        @type id: int
        @param name: Internal Testlink name of the object
        @type name: str
        @keyword kwargs: Additonal attributes
        """
        if _id is not None:
            self.id = int(_id)
        else:
            self.id = _id
        self.name = name
        self._api = api

    def __str__(self):
        """Returns string representation"""
        return "TestlinkObject (%d) %s" % (self.id, self.name)

    def __unicode__(self):
        return unicode(self.__str__())

    def __eq__(self, other):
        return self.id == other.id


class TestProject(TestlinkObject):
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

    __slots__ = ("notes", "prefix", "active", "public", "requirements",\
            "priority", "automation", "inventory", "tc_counter", "color")

    def __init__(
            self,\
            name="",\
            notes="",\
            prefix="",\
            active="0",\
            is_public="0",\
            tc_counter=0,\
            opt=None,\
            color="",\
            api=None,\
            **kwargs\
    ):
        if opt is None:
            opt = {}
            opt['requirementsEnabled'] = 0
            opt['testPriorityEnabled'] = 0
            opt['automationEnabled'] = 0
            opt['inventoryEnabled'] = 0
        TestlinkObject.__init__(self, kwargs.get('id'), name, api)
        self.notes = notes
        self.prefix = prefix
        self.active = bool(int(active))
        self.public = bool(int(is_public))
        self.requirements = bool(int(opt['requirementsEnabled']))
        self.priority = bool(int(opt['testPriorityEnabled']))
        self.automation = bool(int(opt['automationEnabled']))
        self.inventory = bool(int(opt['inventoryEnabled']))
        self.tc_counter = int(tc_counter)
        self.color = color

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
        @param id: The internal ID of the TestSuite
        @type id: int
        @param recursive: Search recursive to get all nested TestSuites
        @type recursive: bool
        @param params: Other params for TestSuite
        @type params: dict
        @returns: Matching TestSuites
        @rtype: generator
        """
        _id = params.get('id')
        # Check if simple API call can be done
        # Since the ID is unique, all other params can be ignored
        if _id:
            response = self._api.getTestSuiteById(self.id, _id)
            yield TestSuite(api=self._api, parent_testproject=self, **response)
        else:
            try:
                response = self._api.getFirstLevelTestSuitesForTestProject(self.id)
            except APIError, ae:
                if ae.errorCode == 7008:
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
                                cf_val = self._api.getTestSuiteCustomFieldDesignValue(tsuite.id, tsuite.getTestProject().id, key)
                                if not unicode(cf_val) == unicode(value):
                                    tsuite = None
                                    break
                        except AttributeError:
                            raise AttributeError("Invalid Search Parameter for TestSuite: %s" % key)
                    if tsuite is not None:
                        yield tsuite
                # If recursive is specified,\
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
                    # First return the suites from this level,\
                    # then return nested ones if recursive is specified
                    yield tsuite
                    if recursive:
                        for s in tsuite.iterTestSuite(name=name, recursive=recursive, **params):
                            yield s

    def getTestSuite(self, name=None, recursive=True, **params):
        """Returns all TestSuites specified by parameters
        @param name: The name of the wanted TestSuite
        @type name: str
        @param id: The internal ID of the TestSuite
        @type id: int
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
        @param id: The internal ID of the TestCase
        @type id: int
        @param external_id: The external ID of the TestCase
        @type external_id: int
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
                if ae.errorCode == 5030:
                    # If no testcase has been found here,\
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

            # Need to get testsuite to set as parent
            suite_resp = self._api.getTestSuiteById(self.id, response['testsuite_id'])
            suite = TestSuite(**suite_resp)

            yield TestCase(api=self._api, parent_testproject=self, parent_testsuite=suite, **response)
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
        @param id: The internal ID of the TestCase
        @type id: int
        @param external_id: The external ID of the TestCase
        @type external_id: int
        @param params: Other params for TestCase
        @type params: dict
        @returns: Matching TestCases
        @rtype: mixed
        """
        return normalize_list([c for c in self.iterTestCase(name, external_id, **params)])

    def iterRequirementSpecification(self, name=None, **params):
        """Iterates over Requirement Specifications specified by parameters
        @param name: The title of the wanted Requirement Specification
        @type name: str
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
                            cf_val = self._api.getReqSpecCustomFieldDesignValue(rspec.id, rspec.getTestProject().id, key)
                            if not unicode(cf_val) == unicode(value):
                                rspec = None
                                break
                    except AttributeError:
                        raise AttributeError("Invalid Search Parameter for Requirement Specification: %s" % key)
                if rspec is not None:
                    yield rspec
        # Return all Requirement Specifications
        else:
            for rspec in specs:
                yield rspec

    def getRequirementSpecification(self, title=None, **params):
        """Returns all Requirement Specifications specified by parameters
        @param title: The title of the wanted Requirement Specification
        @type title: str
        @returns: Matching Requirement Specifications
        @rtype: list
        """
        return normalize_list([r for r in self.iterRequirementSpecification(title, **params)])

    def iterRequirement(self, name=None, **params):
        """Returns all Requirements specified by paramaters
        @param name: The title of the wanted Requirements
        @type name: str
        @param returns: Matching Requirements
        @rtype: generator
        """
        params['name'] = name
        for spec in self.iterRequirementSpecification():
            for req in spec.iterRequirement(**params):
                yield req

    def getRequirement(self, name=None, **params):
        """Returns all Requirements specified by paramaters
        @param name: The title of the wanted Requirements
        @type name: str
        @param returns: Matching Requirements
        @rtype: list
        """
        return normalize_list([r for r in self.iterRequirement(name, **params)])


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
        self.notes = notes
        self.active = bool(int(active))
        self.public = bool(int(is_public))
        self._parent_testproject = parent_testproject

    def __str__(self):
        return "TestPlan: %s" % self.name

    def getTestProject(self):
        """Returns associated TestProject"""
        return self._parent_testproject

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
        builds = [Build(api=self._api, **build) for build in response]

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
            if ae.errorCode == 3041:
                # No platforms linked at all
                return
            else:
                raise

        platforms = [Platform(api=self._api, **platform) for platform in response]

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
        _id = params.get('id')

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
            if ae.errorCode == 3030:
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

class Build(TestlinkObject):
    """Testlink Build representation
    @ivar notes: Build notes
    @type notes: str
    """

    __slots__ = ("notes")

    def __init__(self, name=None, notes=None, api=None, **kwargs):
        TestlinkObject.__init__(self, kwargs.get('id'), name, api)
        self.notes = notes

    def __str__(self):
        return "Build: %s" % self.name


class Platform(TestlinkObject):
    """Testlink Platform representation
    @ivar notes: Platform notes
    @type notes: str
    """

    __slots__ = ("notes")

    def __init__(self, name=None, notes=None, api=None, **kwargs):
        TestlinkObject.__init__(self, kwargs.get('id'), name, api)
        self.notes = notes

    def __str__(self):
        return "Platform: %s" % self.name


class TestSuite(TestlinkObject):
    """Testlink TestSuite representation
    @ivar notes: TestSuite notes
    @type notes: str
    """

    __slots__ = ("details", "_parent_testproject", "_parent_testsuite")

    def __init__(self, name="", details="", parent_testproject=None, parent_testsuite=None, api=None, **kwargs):
        TestlinkObject.__init__(self, kwargs.get('id'), name, api)
        self.details = details
        self._parent_testproject = parent_testproject
        self._parent_testsuite = parent_testsuite

    def __str__(self):
        return "TestSuite: %s" % self.name

    def getTestProject(self):
        """Returns associated TestProject"""
        return self._parent_testproject

    def iterTestSuite(self, name=None, recursive=True, **params):
        """Iterates over TestSuites speficied by parameters
        @param name: The name of the wanted TestSuite
        @type name: str
        @param id: The internal ID of the TestSuite
        @type id: int
        @param recursive: Search recursive to get all nested TestSuites
        @type recursive: bool
        @param params: Other params for TestSuite
        @type params: dict
        @returns: Matching TestSuites
        @rtype: generator
        """
        # Simple API call could be done, but
        # we want to ensure, that only sub suites of this
        # particular suite are involved, so no API call here
        response = self._api.getTestSuitesForTestSuite(self.id)

        # Normalize result
        if isinstance(response, str) and response.strip() == "":
            response = []
        elif isinstance(response, dict):
            # Check for nested dict
            if isinstance(response[response.keys()[0]], dict):
                response = [self._api.getTestSuiteById(self.getTestProject().id, suite_id) for suite_id in response.keys()]
            else:
                response = [response]
        suites = [TestSuite(api=self._api, parent_testproject=self.getTestProject(), parent_testsuite=self, **suite) for suite in response]

        # Filter
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
                            cf_val = self._api.getTestSuiteCustomFieldDesignValue(tsuite.id, tsuite.getTestProject().id, key)
                            if not unicode(cf_val) == unicode(value):
                                tsuite = None
                                break
                    except AttributeError:
                        raise AttributeError("Invalid Search Parameter for TestSuite: %s" % key)
                if tsuite is not None:
                    yield tsuite
            # If recursive is specified
            # also serch in nested suites
            if recursive:
                # For each suite of this level
                for tsuite in suites:
                    # Yield nested suites that match
                    for s in tsuite.iterTestSuite(recursive=recursive, **params):
                        yield s
        # Return all suites
        else:
            for tsuite in suites:
                # First return the suites from this level,\
                # then return nested ones if recursive is specified
                yield tsuite
                if recursive:
                    for s in tsuite.iterTestSuite(name=name, recursive=recursive, **params):
                        yield s

    def getTestSuite(self, name=None, recursive=True, **params):
        """Returns all TestSuites speficied by parameters
        @param name: The name of the wanted TestSuite
        @type name: str
        @param id: The internal ID of the TestSuite
        @type id: int
        @param recursive: Search recursive to get all nested TestSuites
        @type recursive: bool
        @param params: Other params for TestSuite
        @type params: dict
        @returns: Matching TestSuites
        @rtype: mixed
        """
        return normalize_list([s for s in self.iterTestSuite(name, recursive, **params)])

    def iterTestCase(self, name=None, **params):
        """Iterates over TestCases specified by parameters
        @param name: The name of the wanted TestCase
        @type name: str
        @param params: Other params for TestCase
        @type params: dict
        @returns: Matching TestCases
        @rtype: generator
        """
        # No simple API call possible, get all
        response = self._api.getTestCasesForTestSuite(self.id, details='full', getkeywords=True)
        cases = [TestCase(api=self._api, parent_testproject=self.getTestProject(), parent_testsuite=self, **case) for case in response]

        # Filter by specified parameters
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
                                tcase = None
                                break
                        except AttributeError:
                            # Try as custom field
                            ext_id = "%s-%s" % (tcase.getTestProject().prefix, tcase.external_id)
                            cf_val = self._api.getTestCaseCustomFieldDesignValue(ext_id, tcase.version, tcase.getTestProject().id, key)
                            if not unicode(cf_val) == unicode(value):
                                tcase = None
                                break
                    except APIError, ae:
                        if ae.errorCode == 9000:
                            # Neither found by custom field
                            raise AttributeError("Invalid Search Parameter for TestCase: %s" % key)
                        else:
                            raise
                if tcase is not None:
                    yield tcase
        else:
            # Return all found testcases
            for tcase in cases:
                yield tcase

    def getTestCase(self, name=None, **params):
        """Returns all TestCases specified by parameters
        @param name: The name of the wanted TestCase
        @type name: str
        @param params: Other params for TestCase
        @type params: dict
        @returns: Matching TestCases
        @rtype: mixed
        """
        return normalize_list([c for c in self.iterTestCase(name, **params)])


class TestCase(TestlinkObject):
    """Testlink TestCase representation"""

    __slots__ = ["tc_id", "external_id", "platform_id", "execution_status", "execution_notes", "priority",\
            "__author", "author_id", "creation_ts", "__modifier", "modifier_id", "modification_ts",\
            "__testsuite", "__testsuite_id", "version", "status", "importance", "execution_type", "preconditions",\
            "summary", "active", "testsuite_id", "tester_id", "exec_duration", "_parent_testproject", "customfields", "requirements",\
            "__steps", "__preconditions", "keywords"]

    class Step(object):
        """Testlink TestCase Step representation
        @ivar id: Internal ID of the Step
        @type id: int
        @ivar number: Number of the step
        @type number: int
        @ivar actions: Actions of the step
        @type actions: str
        @ivar execution_type: Type of Execution
        @type execution_type: ExecutionType
        @ivar active: Active flag
        @type active: bool
        @ivar results: Expected result of the step
        @type results: str
        """
        def __init__(
                self,\
                step_number=1,\
                actions="",\
                execution_type=ExecutionType.MANUAL,\
                active="0",\
                expected_results="",\
                **kwargs\
            ):
            if 'id' in kwargs.keys():
                self.id = int(kwargs['id'])
            else:
                self.id = None
            self.step_number = int(step_number)
            self.actions = actions
            self.execution_type = int(execution_type)
            self.active = bool(int(active))
            self.expected_results = expected_results

        def __repr__(self):
            """Returns parsable representation"""
            return str(self.as_dict())

        def as_dict(self):
            """Returns dict representation"""
            res = {}
            res["step_number"] = self.step_number
            res["actions"] = self.actions
            res["execution_type"] = self.execution_type
            res["active"] = self.active
            res["id"] = self.id
            res["expected_results"] = self.expected_results
            return res

        def __str__(self):
            return "Step %d:\n%s\n%s" % (self.step_number, self.actions, self.expected_results)

    class Execution(TestlinkObject):
        """Testlink TestCase Execution representation
        @ivar id: The internal ID of the Execution
        @type id: int
        @ivar testplan_id: The internal ID of the parent TestPlan
        @type testplan_id: int
        @ivar build_id: The internal ID of the parent Build
        @type build_id: int
        @ivar tcversion_id: The internal ID of the parent TestCase Version
        @type tcversion_id: int
        @ivar tcversion_number: The version of the parent TestCase
        @type tcversion_number: int
        @ivar status: The status of the Execution
        @type status: str
        @ivar notes: Notes of the Execution
        @type notes: str
        @ivar execution_type: Execution Type
        @type execution_type: ExecutionType
        @ivar execution_ts: Timestamp of execution
        @type execution_ts: datetime
        @ivar tester_id: The internal ID of the tester
        @type tester_id: int
        """

        __slots__ = ("id", "testplan_id", "platform_id", "build_id", "tcversion_id", "tcversion_number", "status",\
                "notes", "execution_type", "execution_ts", "tester_id", "__tester", "duration")

        def __init__(
                self,\
                testplan_id=-1,\
                platform_id=-1,\
                build_id=-1,\
                tcversion_id=-1,\
                tcversion_number=0,\
                status='',\
                notes="",\
                execution_type=ExecutionType.MANUAL,\
                execution_ts=str(datetime.min),\
                tester_id=-1,\
                execution_duration=0.0,\
                api=None,\
                **kwargs\
            ):
            TestlinkObject.__init__(self, kwargs.get('id'), kwargs.get('id', "None"), api)
            self.testplan_id = int(testplan_id)
            self.platform_id = int(platform_id)
            self.build_id = int(build_id)
            self.tcversion_id = int(tcversion_id)
            self.tcversion_number = int(tcversion_number)
            self.status = status
            self.notes = notes
            self.execution_type = int(execution_type)
            try:
                self.execution_ts = _strptime(str(execution_ts), DATETIME_FORMAT)
            except ValueError:
                self.execution_ts = datetime.min
            self.tester_id = int(tester_id)
            self.__tester = None
            try:
                self.duration = float(execution_duration)
            except ValueError:
                self.duration = float(0.0)

        def __str__(self):
            """String representaion"""
            return "Execution (%d) [%s] %s" % (self.id, self.status, self.notes)

        @property
        def tester(self):
            """Tester of this execution"""
            if self.__tester is None:
                try:
                    user = self._api.getUserByID(self.tester_id)
                    if isinstance(user, list) and len(user) == 1:
                        user = user[0]
                    self.__tester = "%s %s" % (unicode(user['firstName']), unicode(user['lastName']))
                except NotSupported:
                    pass
            return self.__tester

        def delete(self):
            """Delete this execution"""
            self._api.deleteExecution(self.id)

    class Keyword(TestlinkObject):
        """Testlink TestCase Keyword representation
        @ivar id: The internal ID of the Keyword
        @type id: int
        @ivar notes: Notes of the keyword
        @type notes: str
        @ivar testcase_id: <OPTIONAL> Related TestCase ID
        @type testcase_id: int
        @ivar _keyword: The actual keyword
        @type: str
        """

        __slots__ = ["id", "notes", "testcase_id", "_keyword"]

        def __init__(
                self,\
                keyword_id=-1,\
                notes=None,\
                testcase_id=None,\
                keyword=None,\
                api=None,\
        ):
            TestlinkObject.__init__(self, keyword_id, keyword, api)
            self.notes = notes
            self.testcase_id = int(testcase_id)
            self._keyword = keyword

        def __str__(self):
            return str(self._keyword)

        def __eq__(self, other):
            return self._keyword == other

        def __ne__(self, other):
            return not self._keyword == other

    def __init__(
            self,\
            version=1,\
            status=None,\
            importance=ImportanceLevel.MEDIUM,\
            execution_type=ExecutionType.MANUAL,\
            summary="",\
            active=True,\
            api=None,\
            parent_testproject=None,\
            parent_testsuite=None,\
            customfields=None,\
            requirements=None,\
            tester_id=None,\
            estimated_exec_duration=None,\
            keywords=None,\
            **kwargs
        ):
        """Initialises a new TestCase with the specified parameters.
        @param name: The name of the TestCase
        @type name: str
        @param version: The version of the TestCase
        @type version: int
        @param status: The status of the TestCase
        @type status: int
        @param importance: The importance of the TestCase
        @type importance: int
        @param execution_type: The execution type of the TestCase
        @type execution_type: int
        @param preconditions: The preconditions for the TestCase
        @type preconditions: str
        @param summary: The summary of the TestCase
        @type summary: str
        @param active: Indicator for active TestCase version
        @type active: bool

        @param parent_testproject: The parent TestProject of the TestCase
        @type parent_testproject: TestProject
        @param parent_testsuite: The parent TestSuite of the TestCase
        @type parent_testsuite: TestSuite
        @param customfields: Custom Fields defined for this TestCase
        @type customfields: dict

        @note: All other attributes depend on the called API method
        -------------------------------------------------------------------------------------------
        | getTestCaseForTestSuite()   | getTestCase()               | getTestCasesForTestPlan()   |
        |                          |                             |                             |
        |  node_order                 |  node_order                 |                             |
        |  is_open                    |  is_open                    |                             |
        |  id # Testcase ID           |  id  # Version ID           |                             |
        |                             |  testcase_id # Testcase ID  |                             |
        |  node_type_id               |                             |                             |
        |  layout                     |  layout                     |                             |
        |  tc_external_id             |  tc_external_id             |                             |
        |                             |                             |  external_id                |
        |  parent_id                  |                             |                             |
        |  version                    |  version                    |  version                    |
        |  details                    |                             |                             |
        |  updater_id                 |  updater_id                 |                             |
        |  status                     |  status                     |  status                     |
        |  importance                 |  importance                 |  importance                 |
        |                             |                             |  urgency                    |
        |                             |                             |  priority                   |
        |  modification_ts            |  modification_ts            |                             |
        |  execution_type             |  execution_type             |  execution_type             |
        |  preconditions              |  preconditions              |  preconditions              |
        |  active                     |  active                     |  active                     |
        |  creation_ts                |  creation_ts                |                             |
        |  node_table                 |                             |                             |
        |  tcversion_id # Version ID  |                             |                             |
        |  name                       |  name                       |  name                       |
        |  summary                    |  summary                    |  summary                    |
        |                             |  steps                      |  steps                      |
        |  author_id                  |  author_id                  |                             |
        |                             |  author_login               |                             |
        |                             |  author_first_name          |                             |
        |                             |  author_last_name           |                             |
        |                             |  updater_login              |                             |
        |                             |  updater_first_name         |                             |
        |                             |  updater_last_name          |                             |
        |                             |  testsuite_id               |  testsuite_id               |
        |                             |                             |  exec_id                    |
        |                             |                             |  executed                   |
        |                             |                             |  execution_notes            |
        |                             |                             |  execution_ts               |
        |                             |                             |  tcversion_number           |
        |                             |                             |  tc_id # Testcase ID        |
        |                             |                             |  assigner_id                |
        |                             |                             |  execution_order            |
        |                             |                             |  platform_name              |
        |                             |                             |  linked_ts                  |
        |                             |                             |  linked_by                  |
        |                             |                             |  tsuite_name                |
        |                             |                             |  assigned_build_id          |
        |                             |                             |  exec_on_tplan              |
        |                             |                             |  exec_on_build              |
        |                             |                             |  execution_run_type         |
        |                             |                             |  feature_id                 |
        |                             |                             |  exec_status                |
        |                             |                             |  user_id                    |
        |                             |                             |  tester_id                  |
        |                             |                             |  tcversion_id # Version ID  |
        |                             |                             |  type                       |
        |                             |                             |  platform_id                |
        ===========================================================================================
        """
        # Get the "correct" id
        if ('id' in kwargs) and ('tcversion_id' in kwargs):
            # getTestCasesForTestSuite()
            _id = kwargs['tcversion_id']
            self.tc_id = kwargs['id']
        elif ('id' in kwargs) and ('testcase_id' in kwargs):
            # getTestCase()
            _id = kwargs['id']
            self.tc_id = kwargs['testcase_id']
        elif ('tc_id' in kwargs) and ('tcversion_id' in kwargs):
            # getTestCasesForTestPlan
            _id = kwargs['tcversion_id']
            self.tc_id = kwargs['tc_id']
        else:
            _id = None

        # Get the "correct" name
        if 'name' in kwargs:
            _name = kwargs['name']
        elif 'tcase_name' in kwargs:
            _name = kwargs['tcase_name']
        else:
            _name = None

        # Init
        TestlinkObject.__init__(self, _id, _name, api=api)

        # Set the "correct" external id
        if 'tc_external_id' in kwargs:
            self.external_id = int(kwargs['tc_external_id'])
        elif 'external_id' in kwargs:
            self.external_id = int(kwargs['external_id'])
        else:
            self.external_id = None

        # Set uncommon, but necessary attributes
        if 'platform_id' in kwargs:
            self.platform_id = kwargs['platform_id']
        else:
            self.platform_id = None

        # Set exec status if available
        if 'exec_status' in kwargs:
            self.execution_status = kwargs['exec_status']
        else:
            self.execution_status = None

        # Set exec notes if available
        if 'execution_notes' in kwargs:
            self.execution_notes = kwargs['execution_notes']
        else:
            self.execution_notes = None

        # Set priority if available
        if 'priority' in kwargs:
            self.priority = kwargs['priority']
        else:
            self.priority = None

        # Try to get the creator
        self.__author = None
        if ('author_first_name' in kwargs) and ('author_last_name' in kwargs):
            self.__author = "%s %s" % (unicode(kwargs['author_first_name']), unicode(kwargs['author_last_name']))
        if 'author_id' in kwargs:
            self.author_id = int(kwargs['author_id'])
        else:
            self.author_id = None

        # Try to get creation ts
        if 'creation_ts' in kwargs:
            try:
                self.creation_ts = _strptime(kwargs['creation_ts'], DATETIME_FORMAT)
            except ValueError:
                # Cannot convert
                self.creation_ts = None
        else:
            self.creation_ts = None

        # Try to get updater
        self.__modifier = None
        if ('updater_first_name' in kwargs) and ('updater_last_name' in kwargs):
            self.__modifier = "%s %s" % (unicode(kwargs['updater_first_name']), unicode(kwargs['updater_last_name']))
        elif 'updater_id' in kwargs and kwargs['updater_id'].strip() != '':
            self.modifier_id = int(kwargs['updater_id'])
        else:
            self.modifier_id = None

        # Try to get modification ts
        if 'modification_ts' in kwargs:
            try:
                self.modification_ts = _strptime(kwargs['modification_ts'], DATETIME_FORMAT)
            except ValueError:
                # Cannot convert
                self.modification_ts = None
        else:
            self.modification_ts = None

        # Set parent Testsuite by lazy loading
        if parent_testsuite is not None:
            self.__testsuite = parent_testsuite
        else:
            self.__testsuite = None
        if 'testsuite_id' in kwargs:
            self.__testsuite_id = kwargs['testsuite_id']
        else:
            self.__testsuite_id = None

        # Set steps by lazy loading
        if 'steps' in kwargs:
            self.__steps = [TestCase.Step(**s) for s in kwargs['steps']]
        else:
            self.__steps = None

        # Set preconditions by lazy loading
        if 'preconditions' in kwargs:
            self.__preconditions = kwargs['preconditions']
        else:
            self.__preconditions = None

        # Set keywords
        self.keywords = []
        if keywords is not None:
            self.keywords = [TestCase.Keyword(**k) for k in keywords.values()]

        # Set common attributes
        self.version = int(version)
        self.status = status
        self.importance = importance
        self.execution_type = int(execution_type)
        self.summary = summary
        self.active = active
        self.tester_id = tester_id
        self.exec_duration = estimated_exec_duration

        # Set internal attributes
        self._parent_testproject = parent_testproject
        self.customfields = {}
        if self.customfields is not None:
            self.customfields = customfields
        self.requirements = []
        if self.requirements is not None:
            self.requirements = requirements

    def __str__(self):
        """Returns String Representation"""
        return "Testcase %s-%s: %s" % (self.getTestProject().prefix, self.external_id, self.name)

    def __unicode__(self):
        """Returns Unicode Representation"""
        return unicode(u"Testcase %s-%s: %s" % (self.getTestProject().prefix, self.external_id, self.name))

    @property
    def author(self):
        """Author of this testcase"""
        if (self.__author is None) and (self.author_id is not None):
            try:
                user = self._api.getUserByID(self.author_id)
                if isinstance(user, list) and len(user) == 1:
                    user = user[0]
                self.__author = "%s %s" % (unicode(user['firstName']), unicode(user['lastName']))
            except NotSupported:
                pass
        return self.__author

    @property
    def modifier(self):
        """Modifier of this testcase"""
        if (self.__modifier is None) and (self.modifier_id is not None):
            try:
                user = self._api.getUserByID(self.modifier_id)
                if isinstance(user, list) and len(user) == 1:
                    user = user[0]
                self.__modifier = "%s %s" % (unicode(user['firstName']), unicode(user['lastName']))
            except NotSupported:
                pass
        return self.__modifier

    def _get_testsuite(self):
        """Lazy-loading testsuite getter"""
        if self.__testsuite is not None:
            return self.__testsuite
        else:
            if self.__testsuite_id is not None:
                ts = self._parent_testproject.getTestSuite(id=self.__testsuite_id)
                self.__testsuite = ts
            else:
                # We have to get ourself
                this = self.getTestProject().getTestCase(id=self.tc_id)
                self.__testsuite = this.testsuite
                return self.__testsuite
    def _set_testsuite(self, suite):
        """Lazy-loading testsuite setter"""
        self.__testsuite = suite
    testsuite = property(_get_testsuite, _set_testsuite)

    def _get_steps(self):
        """Lazy-loading step getter"""
        if self.__steps is not None:
            return self.__steps
        else:
            case = self.getTestProject().getTestCase(id=self.tc_id, external_id=self.external_id, version=self.version)
            self.__steps = case.__steps
            return self.__steps
    def _set_steps(self, steps):
        """Lazy-loading step setter"""
        self.__steps = steps
    steps = property(_get_steps, _set_steps)

    def _get_preconditions(self):
        """Lazy-loading precondition getter"""
        if self.__preconditions is not None:
            return self.__preconditions
        else:
            case = self.getTestProject().getTestCase(id=self.tc_id, version=self.version)
            self.__preconditions = case.__preconditions
            return self.__preconditions
    def _set_preconditions(self, preconditions):
        """Lazy-loading precondition setter"""
        self.__preconditions = preconditions
    preconditions = property(_get_preconditions, _set_preconditions)

    def getTestProject(self):
        """Returns associated TestProject"""
        return self._parent_testproject

    def getTestSuite(self):
        """Returns associated TestSuite"""
        return self.testsuite

    def getLastExecutionResult(self, testplanid, platformid=None, platformname=None, buildid=None, buildname=None, bugs=False):
        """Return last execution result"""
        try:
            resp = self._api.getLastExecutionResult(testplanid, self.tc_id, self.external_id, platformid, platformname, buildid, buildname, bugs)
            if isinstance(resp, list) and len(resp) == 1:
                resp = resp[0]
            execution = TestCase.Execution(api=self._api, **resp)
            if execution.id > 0:
                return execution
        except APIError, ae:
            if ae.errorCode == 3030:
                # Testcase not linked to testplan
                return
            else:
                raise

    def getExecutions(self, testplanid, platformid=None, platformname=None, buildid=None, buildname=None, bugs=False):
        """Returns last executions"""
        try:
            resp = self._api.getExecutions(testplanid, self.tc_id, self.external_id, platformid, platformname, buildid, buildname, bugs)
            if len(resp) == 0:
                return []
            else:
                return [TestCase.Execution(api=self._api, **exc) for exc in resp.values()]
        except APIError, ae:
            if ae.errorCode == 3030:
                # Testcase not linked to testplan
                return []
            else:
                raise

    def deleteLastExecution(self, testplanid):
        """Deletes last execution"""
        # Update last execution
        last = self.getLastExecutionResult(testplanid)
        self._api.deleteExecution(last.id)

    def reportResult(self, testplanid, buildid, status, notes=None, overwrite=False, execduration=None):
        """Reports TC result"""
        self._api.reportTCResult(\
            testplanid=testplanid,\
            status=status,\
            testcaseid=self.tc_id,\
            testcaseexternalid=self.external_id,\
            notes=notes,\
            platformid=self.platform_id,\
            overwrite=overwrite,\
            buildid=buildid,\
            execduration=execduration\
        )

    def getAttachments(self):
        """Returns attachments for this testcase"""
        return self._api.getTestCaseAttachments(self.tc_id, self.external_id)

    def getCustomFieldDesignValue(self, fieldname, details=CustomFieldDetails.VALUE_ONLY):
        """Returns the custom field design value for the specified custom field
        @param fieldname: The internal name of the custom field
        @type fieldname: str
        @param details: Granularity of the response
        @type details: CustomFieldDetails
        @returns: Custom Field value or informations
        @rtype: mixed
        """
        if fieldname not in self.customfields.keys():
            value = self._api.getTestCaseCustomFieldDesignValue(\
                        testcaseexternalid="%s-%s" % (str(self.getTestProject().prefix), str(self.external_id)),\
                        version=int(self.version),\
                        testprojectid=self.getTestProject().id,\
                        customfieldname=fieldname,\
                        details=details\
                    )
            # If retrieved the value only, we can cache it
            if value is not None and (details == CustomFieldDetails.VALUE_ONLY):
                self.customfields[fieldname] = value
        return self.customfields[fieldname]

    def update(self, testcasename=None, summary=None, preconditions=None, steps=None, importance=None, executiontype=None, status=None, exec_duration=None):
        """Updates the the current TestCase.
        @param testcasename: The name of the TestCase
        @type testcasname: str
        @param summary: The summary of the TestCase
        @type summary: str
        @param preconditions: The Preconditions of the TestCase
        @type preconditions: str
        @param steps: The steps of the TestCase
        @type steps: list
        @param importance: The importance of the TestCase
        @type importance: enums.ImportanceLevel
        @param executiontype: The execution type of the TestCase
        @type executiontype: enums.ExecutionType
        @param status: The status of the TestCase
        @type status: enums.TestcaseStatus
        @param exec_duration: The estimated execution time of the TestCase
        @type exec_duration: int
        @returns: None
        """

        # If some values are not explicitly left emtpty
        # we have to keep update by the original value
        # to keep it within Testlink
        if testcasename is None:
            testcasename = self.name
        if summary is None:
            summary = self.summary
        if preconditions is None:
            preconditions = self.preconditions
        if steps is None:
            steps = self.steps
        if importance is None:
            importance = self.importance
        if executiontype is None:
            executiontype = self.execution_type
        if status is None:
            status = self.status
        if exec_duration is None:
            exec_duration = self.exec_duration

        self._api.updateTestCase(\
                testcaseexternalid="%s-%s" % (str(self.getTestProject().prefix), str(self.external_id)),\
                testcasename=testcasename,\
                summary=summary,\
                preconditions=preconditions,\
                steps=[step.as_dict() for step in steps],\
                importance=importance,\
                executiontype=executiontype,\
                status=status,\
                estimatedexecduration=exec_duration\
            )

    def assignRequirements(self, requirements=None):
        """Assign all specified requirements to current TestCase.
        @param requirements: All requirements of testcase
        @type requirements:list
        """
        if requirements is None:
            requirements = self.requirements

        return self._api.assignRequirements(\
                    testcaseexternalid="%s-%s" % (str(self.getTestProject().prefix), str(self.external_id)),\
                    testprojectid=self.getTestProject().id,\
                    requirements=requirements\
                )

    def updateCustomFieldDesignValue(self, customfields=None):
        """Updates all custom fields of current TestCase.
        @param customfields: All customfields of testcase
        @type customfields:list
        """
        if customfields is None:
            customfields = self.customfields

        return self._api.updateTestCaseCustomFieldDesignValue(\
                    testcaseexternalid="%s-%s" % (str(self.getTestProject().prefix), str(self.external_id)),\
                    version=int(self.version),\
                    testprojectid=self.getTestProject().id,\
                    customfields=customfields\
                )

class RequirementSpecification(TestlinkObject):
    """Testlink Requirement Specification representation"""

    __slots__ = ("doc_id", "typ", "scope", "testproject_id", "author_id", "creation_ts",\
            "modifier_id", "modification_ts", "total_req", "node_order", "_parent_testproject")

    def __init__(\
            self,\
            doc_id='',\
            title='',\
            typ=RequirementSpecificationType.SECTION,\
            scope='',\
            testproject_id=-1,\
            author_id=-1,\
            creation_ts=str(datetime.min),\
            modifier_id=-1,\
            modification_ts=str(datetime.min),\
            total_req=0,\
            node_order=0,\
            api=None,\
            parent_testproject=None,\
            **kwargs\
            ):
        """Initializes a new Requirement Specification with the specified parameters.
        @todo: doc
        """
        TestlinkObject.__init__(self, kwargs.get('id'), title, api)
        self.doc_id = str(doc_id)
        self.typ = int(typ)
        self.scope = scope
        self.testproject_id = int(testproject_id)
        self.author_id = int(author_id)
        try:
            self.modifier_id = int(modifier_id)
        except ValueError:
            self.modifier_id = -1
        self.total_req = int(total_req)
        self.node_order = int(node_order)
        try:
            self.creation_ts = _strptime(str(creation_ts), DATETIME_FORMAT)
        except ValueError:
            self.creation_ts = datetime.min
        try:
            self.modification_ts = _strptime(str(modification_ts), DATETIME_FORMAT)
        except ValueError:
            self.modification_ts = datetime.min
        self._parent_testproject = parent_testproject

    def __str__(self):
        return "Requirement Specification %s: %s" % (self.doc_id, self.name)

    def getTestProject(self):
        """Returns associated TestProject"""
        return self._parent_testproject

    def iterRequirement(self, name=None, **params):
        """Iterates over Requirements specified by parameters
        @param name: The title of the wanted Requirement
        @type name: str
        @returns: Matching Requirements
        @rtype: generator
        """
        # No Simple API Call possible, get all and convert to Requirement instances
        response = self._api.getRequirementsForRequirementSpecification(self.id, self.getTestProject().id)
        requirements = [Requirement(api=self._api, parent_testproject=self.getTestProject(), **req) for req in response]

        # Filter
        if len(params) > 0 or name:
            params['name'] = name
            for req in requirements:
                for key, value in params.items():
                    # Skip None
                    if value is None:
                        continue
                    try:
                        try:
                            if not unicode(getattr(req, key)) == unicode(value):
                                req = None
                                break
                        except AttributeError:
                            # Try as custom field
                            cf_val = self._api.getRequirementCustomFieldDesignValue(req.id, req.getTestProject().id, key)
                            if not unicode(cf_val) == unicode(value):
                                req = None
                                break
                    except AttributeError:
                        raise AttributeError("Invalid Search Parameter for Requirement: %s" % key)
                if req is not None:
                    yield req
        # Return all Requirements
        else:
            for req in requirements:
                yield req

    def getRequirement(self, name=None, **params):
        """Returns all Requirements with the specified parameters
        @param name: The title of the wanted Requirement
        @type name: str
        @returns: Matching Requirements
        @rtype: mixed
        """
        return normalize_list([r for r in self.iterRequirement(name, **params)])

class Requirement(TestlinkObject):
    """Testlink Requirement representation"""

    __slots__ = ("srs_id", "req_doc_id", "req_spec_title", "typ", "version", "version_id", "revision", "revision_id",\
            "scope", "status", "node_order", "is_open", "active", "expected_coverage", "testproject_id", "author",\
            "author_id", "creation_ts", "modifier", "modifier_id", "modification_ts", "_parent_testproject")

    def __init__(\
            self,\
            srs_id=None,\
            req_doc_id='',\
            title='',\
            req_spec_title=None,\
            typ=RequirementType.INFO,\
            version=-1,\
            version_id=-1,\
            revision=-1,\
            revision_id=-1,\
            scope='',\
            status=RequirementStatus.DRAFT,\
            node_order=0,\
            is_open="1",\
            active="1",\
            expected_coverage=1,\
            testproject_id=-1,\
            author=None,\
            author_id=-1,\
            creation_ts=str(datetime.min),\
            modifier=None,\
            modifier_id=-1,\
            modification_ts=str(datetime.min),\
            api=None,\
            parent_testproject=None,\
            **kwargs\
    ):
        """Initializes a new Requirement with the specified parameters
        @todo: doc
        """
        TestlinkObject.__init__(self, kwargs.get('id'), title, api)
        self.srs_id = str(srs_id)
        self.req_doc_id = str(req_doc_id)
        self.req_spec_title = req_spec_title
        self.typ = int(typ)
        self.version = int(version)
        self.version_id = int(version_id)
        self.revision = int(revision)
        self.revision_id = int(revision_id)
        self.scope = scope
        self.status = str(status)
        self.node_order = int(node_order)
        self.is_open = bool(int(is_open))
        self.active = bool(int(active))
        self.expected_coverage = int(expected_coverage)
        self.testproject_id = int(testproject_id)
        self.author = str(author)
        self.author_id = int(author_id)
        self.modifier = str(modifier)
        try:
            self.modifier_id = int(modifier_id)
        except ValueError:
            self.modifier_id = -1
        try:
            self.creation_ts = _strptime(str(creation_ts), DATETIME_FORMAT)
        except ValueError:
            self.creation_ts = datetime.min
        try:
            self.modification_ts = _strptime(str(modification_ts), DATETIME_FORMAT)
        except ValueError:
            self.modification_ts = datetime.min
        self._parent_testproject = parent_testproject

    def __str__(self):
        return "Requirement %s: %s" % (self.req_doc_id, self.name)

    def getTestProject(self):
        """Returns the associated TestProject"
        @returns: TestProject
        @rtype: TestProject
        """
        return self._parent_testproject

    def iterRisk(self, name=None, **params):
        """Returns all Risks with the specified parameters.
        @param name: The name of the wanted Risk
        @type name: str
        @returns: Matching Risks
        @rtype: generator
        """
        # No simple API call, so get all Risks for the current Requirement
        response = self._api.getRisksForRequirement(self.id)
        risks = [Risk(api=self._api, parent_testproject=self.getTestProject(), **risk) for risk in response]

        # Filter
        if len(params) > 0 or name:
            params['name'] = name
            for rk in risks:
                for key, value in params.items():
                    # Skip None
                    if value is None:
                        continue
                    try:
                        if not unicode(getattr(rk, key)) == unicode(value):
                            rk = None
                            break
                    except AttributeError:
                        raise AttributeError("Invalid Search Parameter for Risk: %s" % key)
                # Return found risk
                if rk is not None:
                    yield rk
        # Return all found risks
        else:
            for rk in risks:
                yield rk

    def getRisk(self, name=None, **params):
        """Returns all Risks with the specified parameters
        @param name: The name of the Risk
        @type name: str
        @returns: Matching Risks
        @rtype: mixed
        """
        return normalize_list([r for r in self.iterRisk(name, **params)])

class Risk(TestlinkObject):
    """Testlink Risk representation"""

    __slots__ = ["doc_id", "description", "author_id", "creation_ts", "modifier_id", "modification_ts",\
            "_requirement_id", "cross_coverage"]

    def __init__(\
            self,\
            risk_doc_id=None,\
            name='',\
            description='',\
            author_id=-1,\
            creation_ts=str(datetime.min),\
            modifier_id=-1,\
            modification_ts=str(datetime.min),\
            requirement_id=-1,\
            cross_coverage='',\
            api=None,\
            **kwargs\
        ):
        """Initializes a new Risk with the specified parameters
        @todo: doc
        """
        TestlinkObject.__init__(self, kwargs.get('id'), name, api)
        self.doc_id = str(risk_doc_id)
        self.description = description
        self.author_id = int(author_id)
        try:
            self.creation_ts = _strptime(str(creation_ts), DATETIME_FORMAT)
        except ValueError:
            self.creation_ts = datetime.min
        try:
            self.modifier_id = int(modifier_id)
        except ValueError:
            self.modifier_id = -1
        try:
            self.modification_ts = _strptime(str(modification_ts), DATETIME_FORMAT)
        except ValueError:
            self.modification_ts = datetime.min
        self._requirement_id = requirement_id
        self.cross_coverage = str(cross_coverage)

    def __str__(self):
        return "Risk %s: %s" % (self.doc_id, self.name)
