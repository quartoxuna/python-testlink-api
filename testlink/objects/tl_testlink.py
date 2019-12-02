#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Testlink Object Wrapper"""

# IMPORTS
from testlink.log import LOGGER
from testlink.api.testlink_api import TestlinkAPI
from testlink.exceptions import APIError

from testlink.enums import APIType
from testlink.enums import DuplicateStrategy

from testlink.objects.tl_object import normalize_list
from testlink.objects.tl_testproject import TestProject
from testlink.objects.tl_testsuite import TestSuite
from testlink.objects.tl_testsuite import TestCase


class Testlink(object):
    """Testlink Server implementation
    @ivar _url: URL of connected Testlink
    @type _url: str
    @ivar devkey: Valid Testlink developer key
    @type devkey: str
    """

    def __init__(self, url, devkey, api=APIType.XML_RPC):
        """Initializes the Testlink Server object
        @param url: Testlink URL
        @type url: str
        @param devkey: Testlink developer key
        @type devkey: str
        """
        self._api = TestlinkAPI.builder()\
                    .connect_to(url)\
                    .using_devkey(devkey)\
                    .build()

        # Log API Information
        LOGGER.info(str(self))

    def __str__(self):
        return "{}: {}".format(self.__class__.__name__, str(self._api))

    def getVersion(self):
        return self._api.version

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
                # Since Testlink 1.9.6, the server already returns a dict
                # before, there was a list containing a dict
                if isinstance(response, list):
                    response = response[0]
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
            projects = [TestProject(api=self._api, parent_testlink=self, **project) for project in response]

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
        _id = params.get('id', 0)
        if _id:
            # Since this testsuite is not linked to a testproject
            # we have to set the _parent_testproject attribute directly
            # Alternatively, we could implement _parent_testsuite as
            # dynamic property, but then we would getTestSuite() within
            # Testproject class, but we do not know the testproject :-) so yay
            project_name = self._api.getFullPath(_id).values()[0][0]
            testproject = self.getTestProject(project_name)

            response = self._api.getTestSuiteById(testproject.id, _id)
            yield TestSuite(api=self._api, parent_testproject=testproject, **response)
        else:
            # Simply iterate over all projects and yield
            # all matching testsuites
            for project in self.iterTestProject():
                for suite in project.iterTestSuite(name, recursive, **params):
                    yield suite

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

    def iterTestCase(self, **params):
        """Iterates over TestCases specified by parameters
        @returns: Matching TestCases
        @rtype: generator
        """
        # Check if simple API call can be done
        # Since the internal ID is unique all other paras can be ignored
        _id = params.get('id')
        if _id:
            response = self._api.getTestCase(_id)
            # Servers respones is a list
            if isinstance(response, list) and len(response) > 0:
                response = response[0]

            # Need to get testsuite to set as parent
            suite = self.getTestSuite(**{'id':  int(response['testsuite_id'])})

            # Yield matching TestCase
            yield TestCase(api=self._api, parent_testproject=suite.getTestProject(), parent_testsuite=suite, **response)
        else:
            # Simply iterator over all projects and yield
            # all matching testcases
            for project in self.iterTestProject():
                for case in project.iterTestCase(**params):
                    yield case

    def getTestCase(self, **params):
        """Returns all TestCases specified by parameters
        @returns: Matching TestCases
        @rtype: mixed
        """
        return normalize_list([c for c in self.iterTestCase(**params)])

    def createTestProject(self, project):
        """Creates a new TestProject using the current Testlink instance.
        @param project: Project to create
        @type project: testlink.objects.tl_testproject.TestProject
        """
        return self._api.createTestProject(name=project.name,
                                           prefix=project.prefix,
                                           notes=project.notes,
                                           active=project.active,
                                           public=project.public,
                                           requirements=project.requirements_enabled,
                                           priority=project.priority_enabled,
                                           automation=project.automation_enabled,
                                           inventory=project.inventory_enabled)

    def createTestPlan(self, testplan, testproject):
        """Creates a new TestPlan for the specified TestProject using the current Testlink instance.
        @param testplan: TestPlan to create
        @type testplan: TestPlan
        @param testproject: TestProject to add the Testplan to
        @type testproject: TestProject
        """
        return self._api.createTestPlan(name=testplan.name,
                                        notes=testplan.notes,
                                        active=testplan.active,
                                        public=testplan.public,
                                        project=testproject.name)

    def createBuild(self, build, testplan):
        """Creates a new Build for the specified TestPlan using the current Testlink instance.
        @param build: Build to create
        @type build: Build
        @param testplan: TestPlan to add the Build to
        @type testplan: TestPlan
        """
        return self._api.createBuild(name=build.name, notes=build.notes, testplanid=testplan.id)

    def createPlatform(self, platform, testproject):
        """Creates a new Platform for the specified TestProject using the current Testlink instance.
        @param platform: Platform to create
        @type platform: Platform
        @param testproject: TestProject to add the Platform to
        @type testproject: TestProject
        """
        return self._api.createPlatform(platformname=platform.name,
                                        notes=platform.notes,
                                        testprojectname=testproject.name)

    def createTestSuite(self, suite, testproject, **kwargs):
        """Creates a new TestSuite for the specified parent objects using the current Testlink instance.
        @param suite: TestSuite to create
        @type suite: TestSuite
        @param testproject: The parent TestProject
        @type testproject: TestProject
        @keyword parent: Parent testsuite ID
        @keyword order: Order within the parent object
        @keyword on_duplicate: Used duplicate strategy
        """
        parent = kwargs.get('parent', None)
        order = kwargs.get('order', 0)
        on_duplicate = kwargs.get('on_duplicate', DUPLICATE_STRATEGY.BLOCK)

        duplicate_check = False
        if on_duplicate is not None:
            duplicate_check = True

        parent_id = None
        if parent is not None:
            parent_id = parent.id

        return self._api.createTestSuite(testsuitename=suite.name,
                                         details=suite.details,
                                         testprojectid=testproject.id,
                                         parentid=parent_id,
                                         order=order,
                                         checkduplicatedname=duplicate_check,
                                         actiononduplicatedname=on_duplicate)

    def createTestCase(self, testcase, testsuite, testproject, authorlogin, **kwargs):
        """Creates a new TestCase for the specifies parent objects using the current Testlink instance.
        @param testcase: TestCase to create
        @type testcase: TestCase
        @param testsuite: Parent TestSuite
        @type testsuite: TestSuite
        @param testproject: Parent TestProject
        @type testproject: TestProject
        @param authorlogin: Author Login to use
        @type authorlogin: str
        @keyword order: Order within parent TestSuite
        @keyword on_duplicate: Used duplicate strategy
        """
        order = kwargs.get('order', 0)
        on_duplicate = kwargs.get('on_duplicate', DUPLICATE_STRATEGY.BLOCK)

        duplicate_check = False
        if on_duplicate is not None:
            duplicate_check = True

        steps = [s.__dict__ for s in testcase.steps]

        return self._api.createTestCase(testcasename=testcase.name,
                                        testsuiteid=testsuite.id,
                                        testprojectid=testproject.id,
                                        authorlogin=authorlogin,
                                        summary=testcase.summary,
                                        steps=steps,
                                        preconditions=testcase.preconditions,
                                        importance=testcase.importance,
                                        executiontype=testcase.execution_type,
                                        order=order,
                                        customfields=testcase.customfields,
                                        checkduplicatedname=duplicate_check,
                                        actiononduplicatedname=on_duplicate)

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

        return self._api.createRequirementSpecification(testprojectid=testproject.id,
                                                        parentid=parent_id,
                                                        docid=reqspec.doc_id,
                                                        title=reqspec.name,
                                                        scope=reqspec.scope,
                                                        userid=reqspec.author_id,
                                                        typ=reqspec.typ)

    def createRequirement(self, requirement, testproject, reqspec):
        """Creates a new Requirement for the specified TestProject and Requirement Specification
        using the current Testlink instance.
        @param requirement: Requirement to create
        @type requirement: Requirement
        @param testproject: Parent TestProject
        @type testproject: TestProject
        @param reqspec: Parent Requirement Specification
        @type reqspec: RequirementSpecification
        """
        return self._api.createRequirement(testprojectid=testproject.id,
                                           reqspecid=reqspec.id,
                                           docid=requirement.req_doc_id,
                                           title=requirement.name,
                                           scope=requirement.scope,
                                           userid=requirement.author_id,
                                           typ=requirement.typ,
                                           status=requirement.status)

    def createRisk(self, risk, requirement):
        """Creates a new Risk for the specified Requirement using the current Testlink instance.
        @param risk: Risk to create
        @rype risk: Risk
        @param requirement: Parent Requirement
        @type requirement: Requirement
        """
        return self._api.createRisk(requirementid=requirement.id,
                                    docid=risk.doc_id,
                                    title=risk.name,
                                    scope=risk.description,
                                    userid=risk.author_id,
                                    coverage=risk.cross_coverage)
