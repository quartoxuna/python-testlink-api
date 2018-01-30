#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""TestCase Object"""

# IMPORTS
from testlink.objects.tl_object import TestlinkObject
from testlink.objects.tl_object import strptime
from testlink.objects.tl_step import Step
from testlink.objects.tl_keyword import Keyword
from testlink.objects.tl_execution import Execution
from testlink.objects.tl_attachment import Attachment
from testlink.objects.tl_attachment import IAttachmentGetter
from testlink.objects.tl_user import User

from testlink.exceptions import APIError
from testlink.exceptions import NotSupported

from testlink.enums import EXECUTION_TYPE as EXECUTION_TYPE
from testlink.enums import IMPORTANCE_LEVEL as IMPORTANCE_LEVEL
from testlink.enums import CUSTOM_FIELD_DETAILS as CUSTOM_FIELD_DETAILS
from testlink.enums import TESTCASE_STATUS as TESTCASE_STATUS


class TestCase(TestlinkObject, IAttachmentGetter):
    """Testlink TestCase representation"""

    __slots__ = ["tc_id", "external_id", "platform_id", "execution_status", "execution_notes", "priority",
                 "__author", "author_id", "creation_ts", "__modifier", "modifier_id", "modification_ts",
                 "__testsuite", "__testsuite_id", "version", "status", "importance", "execution_type", "preconditions",
                 "summary", "active", "testsuite_id", "tester_id", "exec_duration", "_parent_testproject",
                 "customfields", "requirements", "__steps", "__preconditions", "linked_by", "linked_ts", "_keywords"]

    def __init__(self, version=1, status=TESTCASE_STATUS.DRAFT, importance=IMPORTANCE_LEVEL.MEDIUM,
                 execution_type=EXECUTION_TYPE.MANUAL, summary="", active=True, api=None, parent_testproject=None,
                 parent_testsuite=None, customfields=None, requirements=None, tester_id=-1, **kwargs):
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
        |                             |                             |                             |
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
            _id = int(kwargs['tcversion_id'])
            self.tc_id = int(kwargs['id'])
        elif ('id' in kwargs) and ('testcase_id' in kwargs):
            # getTestCase()
            _id = int(kwargs['id'])
            self.tc_id = int(kwargs['testcase_id'])
        elif ('tc_id' in kwargs) and ('tcversion_id' in kwargs):
            # getTestCasesForTestPlan
            _id = int(kwargs['tcversion_id'])
            self.tc_id = int(kwargs['tc_id'])
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
        IAttachmentGetter.__init__(self)

        # Set the "correct" external id
        if 'tc_external_id' in kwargs:
            self.external_id = int(kwargs['tc_external_id'])
        elif 'external_id' in kwargs:
            self.external_id = int(kwargs['external_id'])
        else:
            self.external_id = None

        # Set uncommon, but necessary attributes
        if 'platform_id' in kwargs:
            self.platform_id = int(kwargs['platform_id'])
            if self.platform_id == 0:
                self.platform_id = None
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
            self.priority = int(kwargs['priority'])
        else:
            self.priority = 0

        # Set urgency if available
        if 'urgency' in kwargs:
            self.urgency = int(kwargs['urgency'])
        else:
            self.urgency = 0

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

        # Try to get assigned user
        self.__assignee_id = None
        self.__assignee = None
        self.__assignee_id = kwargs.get('user_id')

        # Try get get linked_by
        if ('linked_by' in kwargs) and (kwargs['linked_by'].strip() != ''):
            self.linked_by = int(kwargs['linked_by'])
        else:
            self.linked_by = None

        # Try to get linked_ts
        if 'linked_ts' in kwargs:
            try:
                self.linked_ts = strptime(kwargs['linked_ts'], TestlinkObject.DATETIME_FORMAT)
            except ValueError:
                # Cannot convert
                self.linked_ts = None
        else:
            self.linked_ts = None

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
            self.__steps = [Step(**s) for s in kwargs['steps']]
        else:
            self.__steps = None

        # Set preconditions by lazy loading
        if 'preconditions' in kwargs:
            self.__preconditions = kwargs['preconditions']
        else:
            self.__preconditions = None

        # Set Estimated Execution Duration by lazy loading
        if 'estimated_exec_duration' in kwargs:
            try:
                self.__exec_duration = float(kwargs['estimated_exec_duration'])
            except ValueError:
                self.__exec_duration = 0.0
        else:
            self.__exec_duration = None

        # Set Keywords by lazy loading
        if 'keywords' in kwargs:
            try:
                self._keywords = [Keyword(**keyword) for keyword_id, keyword in kwargs['keywords'].items()]
            except TypeError:
                self._keywords = []
        else:
            self._keywords = None

        # Set common attributes
        self.version = int(version)
        self.status = int(status) if str(status).isdigit() else None
        self.importance = int(importance)
        self.execution_type = int(execution_type)
        self.summary = unicode(summary)
        self.active = bool(int(active))
        self.tester_id = int(tester_id) if str(tester_id).isdigit() else None

        # Set internal attributes
        self._parent_testproject = parent_testproject
        self.customfields = {}
        if customfields is not None:
            self.customfields = customfields
        self.requirements = []
        if requirements is not None:
            self.requirements = requirements

    def __str__(self):
        """Returns String Representation"""
        return "Testcase %s-%s: %s" % (self.getTestProject().prefix, self.external_id, self.name)

    def __unicode__(self):
        """Returns Unicode Representation"""
        return unicode(u"Testcase %s-%s: %s" % (self.getTestProject().prefix, self.external_id, self.name))

    @property
    def keywords(self):
        """Keywords of this testcase"""
        if (self._keywords is None):
            # Unfortunately, the only way to get keywords from a testcase
            # is to get the testcase via the parent testsuite
            case = self.getTestSuite().getTestCase(id=self.id, version=self.version)

            # Also, if a testcase has no keywords, we self._keywords stays empty
            # if the testcase has no keywords at all, so we explicitly have to
            # check the _keywords member after the first lazy load.
            # If this is still None, the testcase has no keywords at all.
            if case._keywords is None:
                self._keywords = []
            else:
                 self._keywords = case._keywords
        return self._keywords

    @property
    def exec_duration(self):
        """Estimated Execution Duration"""
        if (self.__exec_duration is None):
            self.__exec_duration = self.getTestProject().getTestCase(id=self.tc_id, version=self.version).exec_duration
        return self.__exec_duration

    @property
    def author(self):
        """Author of this testcase"""
        if (self.__author is None) and (self.author_id is not None):
            try:
                user = self._api.getUserByID(self.author_id)
                if isinstance(user, list) and len(user) == 1:
                    user = user[0]
                self.__author = User(api=self._api, **user)
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
                self.__modifier = User(api=self._api, **user)
            except NotSupported:
                pass
        return self.__modifier

    @property
    def assignee(self):
        """Assignee of this testcase"""
        if (self.__assignee is None) and (self.__assignee_id is not None):
            try:
                user = self._api.getUserByID(self.__assignee_id)
                if isinstance(user, list) and len(user) == 1:
                    user = user[0]
                self.__assignee = User(api=self._api, **user)
            except NotSupported:
                pass
        return self.__assignee

    @property
    def linker(self):
        """Linker of this testcase"""
        # Do not cache
        if (self.__linker is None) and (self.linked_by is not None):
            try:
                user = self._api.getUserByID(self.linked_by)
                if isinstance(user, list) and len(user) == 1:
                    user = user[0]
                self.__linker = User(api=self._api, **user)
            except NotSupported:
                pass
        return self.__linker

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
                self.__testsuite = this.getTestSuite()
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

    def getLastExecutionResult(self, testplanid, platformid=None, platformname=None, buildid=None,
                               buildname=None, bugs=False):
        """Return last execution result"""
        try:
            resp = self._api.getLastExecutionResult(testplanid, self.tc_id, self.external_id, platformid,
                                                    platformname, buildid, buildname, bugs)
            if isinstance(resp, list) and len(resp) == 1:
                resp = resp[0]
            execution = Execution(api=self._api, **resp)
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
            resp = self._api.getExecutions(testplanid, self.tc_id, self.external_id, platformid, platformname,
                                           buildid, buildname, bugs)
            if len(resp) == 0:
                return []
            else:
                return [Execution(api=self._api, **exc) for exc in resp.values()]
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

    def reportResult(self, testplanid, buildid, status, notes=None, overwrite=False, execduration=None, customfields={}):
        """Reports TC result"""
        if len(customfields) == 0:
            customfields = None

        response = self._api.reportTCResult(testplanid=testplanid,
                                            status=status,
                                            testcaseid=self.tc_id,
                                            testcaseexternalid=self.external_id,
                                            notes=notes,
                                            platformid=self.platform_id,
                                            overwrite=overwrite,
                                            buildid=buildid,
                                            execduration=execduration,
                                            customfields=customfields)

        # Return actual execution object
        if isinstance(response, list) and len(response) == 1:
            response = response[0]

        executions = self.getExecutions(testplanid, self.platform_id, buildid=buildid)
        for execution in executions:
            if execution.id == int(response['id']):
                return execution

    def getCustomFieldDesignValue(self, fieldname, details=CUSTOM_FIELD_DETAILS.VALUE_ONLY):
        """Returns the custom field design value for the specified custom field
        @param fieldname: The internal name of the custom field
        @type fieldname: str
        @param details: Granularity of the response
        @type details: CUSTOM_FIELD_DETAILS
        @returns: Custom Field value or informations
        @rtype: mixed
        """
        if fieldname not in self.customfields.keys():
            value = self._api.getTestCaseCustomFieldDesignValue(
                testcaseexternalid="%s-%s" % (str(self.getTestProject().prefix), str(self.external_id)),
                version=int(self.version),
                testprojectid=self.getTestProject().id,
                customfieldname=fieldname,
                details=details)
            # If retrieved the value only, we can cache it
            if value is not None and (details == CUSTOM_FIELD_DETAILS.VALUE_ONLY):
                self.customfields[fieldname] = value
        return self.customfields.get(fieldname, None)

    def update(self, testcasename=None, summary=None, preconditions=None, steps=None, importance=None,
               executiontype=None, status=None, exec_duration=None):
        """Updates the the current TestCase.
        @param testcasename: The name of the TestCase
        @type testcasename: str
        @param summary: The summary of the TestCase
        @type summary: str
        @param preconditions: The Preconditions of the TestCase
        @type preconditions: str
        @param steps: The steps of the TestCase
        @type steps: list
        @param importance: The importance of the TestCase
        @type importance: enums.IMPORTANCE_LEVEL
        @param executiontype: The execution type of the TestCase
        @type executiontype: enums.EXECUTION_TYPE
        @param status: The status of the TestCase
        @type status: enums.TESTCASE_STATUS
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

        self._api.updateTestCase(
            testcaseexternalid="%s-%s" % (str(self.getTestProject().prefix), str(self.external_id)),
            testcasename=testcasename,
            summary=summary,
            preconditions=preconditions,
            steps=[step.as_dict() for step in steps],
            importance=importance,
            executiontype=executiontype,
            status=status,
            estimatedexecduration=exec_duration)

    def assignRequirements(self, requirements=None):
        """Assign all specified requirements to current TestCase.
        @param requirements: All requirements of testcase
        @type requirements:list
        """
        if requirements is None:
            requirements = self.requirements

        return self._api.assignRequirements(
            testcaseexternalid="%s-%s" % (str(self.getTestProject().prefix), str(self.external_id)),
            testprojectid=self.getTestProject().id,
            requirements=requirements)

    def updateCustomFieldDesignValue(self, customfields=None):
        """Updates all custom fields of current TestCase.
        @param customfields: All customfields of testcase
        @type customfields:list
        """
        if customfields is None:
            customfields = self.customfields

        return self._api.updateTestCaseCustomFieldDesignValue(
            testcaseexternalid="%s-%s" % (str(self.getTestProject().prefix), str(self.external_id)),
            version=int(self.version),
            testprojectid=self.getTestProject().id,
            customfields=customfields)

    def iterAttachment(self, **params):
        """Iterates over TestlinkObject's attachments specified by parameters
        @returns: Matching attachments
        @rtype: generator
        """
        # Get all attachments for this object
        response = self._api.getTestCaseAttachments(self.tc_id, self.external_id)

        # Check for empty result
        if len(response) == 0:
            return
        attachments = [Attachment(api=self._api, **resp) for resp in response.values()]

        # Filter
        if len(params) > 0:
            for attach in attachments:
                for key, value in params.items():
                    # Skip None
                    if value is None:
                        continue
                    try:
                        if not unicode(getattr(attach, key)) == unicode(value):
                            attach = None
                            break
                    except AttributeError:
                        raise AttributeError("Invalid Search Paramater for Attachment: %s" % key)
                if attach is not None:
                    yield attach
        else:
            # Return all found attachments
            for attach in attachments:
                yield attach

    def uploadAttachment(self, *args, **kwargs):
        """Upload an Attachment for the TestCase, see IAttachmentGetter.uploadAttachment"""
        # Update ID to TestCase ID rather than TestCase Version ID
        kwargs.update({'id': self.tc_id})
        IAttachmentGetter.uploadAttachment(self, *args, **kwargs)
