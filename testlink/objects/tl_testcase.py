#!/usr/bin/env python
# pylint: disable=line-too-long
# pylint: disable=invalid-name
# pylint: disable=star-args
# pylint: disable=too-many-arguments
# pylint: disable=too-many-instance-attributes
# pylint: disable=too-few-public-methods
# pylint: disable=too-many-locals
# pylint: disable=too-many-branches
# pylint: disable=too-many-statements
# pylint: disable=protected-access
# -*- coding: utf-8 -*-

"""TestCase Object"""

# IMPORTS
import datetime

from testlink.objects.tl_object import TestlinkObject
from testlink.objects.tl_object import _STRPTIME_FUNC as strptime

from testlink.exceptions import APIError
from testlink.exceptions import NotSupported

from testlink.enums import EXECUTION_TYPE as ExecutionType
from testlink.enums import IMPORTANCE_LEVEL as ImportanceLevel
from testlink.enums import CUSTOM_FIELD_DETAILS as CustomFieldDetails
from testlink.enums import TESTCASE_STATUS as TestcaseStatus

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
                execution_ts=str(datetime.datetime.min),\
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
                self.execution_ts = strptime(str(execution_ts), TestlinkObject.DATETIME_FORMAT)
            except ValueError:
                self.execution_ts = datetime.datetime.min
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
            status=TestcaseStatus.DRAFT,\
            importance=ImportanceLevel.MEDIUM,\
            execution_type=ExecutionType.MANUAL,\
            summary="",\
            active=True,\
            api=None,\
            parent_testproject=None,\
            parent_testsuite=None,\
            customfields=None,\
            requirements=None,\
            tester_id=-1,\
            estimated_exec_duration=0.0,\
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
                self.creation_ts = strptime(kwargs['creation_ts'], TestlinkObject.DATETIME_FORMAT)
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
                self.modification_ts = strptime(kwargs['modification_ts'], TestlinkObject.DATETIME_FORMAT)
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
        self.status = int(status)
        self.importance = int(importance)
        self.execution_type = int(execution_type)
        self.summary = unicode(summary)
        self.active = bool(int(active))
        self.tester_id = int(tester_id)
        self.exec_duration = float(estimated_exec_duration)

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
            if ae.error_code == 3030:
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
            if ae.error_code == 3030:
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

