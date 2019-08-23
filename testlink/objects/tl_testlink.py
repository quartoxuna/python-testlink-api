#!/usr/bin/env python
# -*- coding: utf-8 -*-

# IMPORTS
from testlink.log import LOGGER
from testlink.api.testlink_api import TestlinkAPI
from testlink.exceptions import APIError

from testlink.enums import API_TYPE
from testlink.enums import DUPLICATE_STRATEGY

from testlink.objects.tl_object import normalize_list

from testlink.objects.tl_testproject import TestProject
from testlink.objects.tl_testsuite import TestSuite
from testlink.objects.tl_testcase import TestCase


class Testlink(object):
    """Testlink object

    :ivar TestlinkAPI api: TestlinkAPI instance
    :ivar Iterator[TestProject]: Testlink TestProjects
    """

    def __init__(self, api):
        self.__api = api

        # Log API Information
        LOGGER.info(str(self))

    def __str__(self):
        return "{}: {}".format(self.__class__.__name__, str(self.api))

    @property
    def api(self):
        return self.__api

    @property
    def testprojects(self):
        for data in self.api.getProjects():
            yield TestProject.builder(**data)\
                  .from_testlink(self)\
                  .build()

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
