# IMPORTS
import socket
import xmlrpclib
import time

from testlink_api import TestlinkAPI
from testlink_api import TestlinkAPIBuilder

from testlink.log import LOGGER

from testlink.enums import IMPORTANCE_LEVEL
from testlink.enums import EXECUTION_TYPE
from testlink.enums import DUPLICATE_STRATEGY

from testlink.exceptions import APIError
from testlink.exceptions import ConnectionError


class TestlinkXMLRPCAPIBuilder(TestlinkAPIBuilder):

    RPC_PATHS = [
        ['lib', 'api', 'xmlrpc', 'v1'],
        ['lib', 'api', 'xmlrpc']
    ]

    def __init__(self, *args, **kwargs):
        super(TestlinkXMLRPCAPIBuilder, self).__init__(*args, **kwargs)

    def build(self):
        proxy = None
        for path in TestlinkXMLRPCAPIBuilder.RPC_PATHS:
            try:
                uri = '/'.join([self.url] + path + ['xmlrpc.php'])
                proxy = xmlrpclib.ServerProxy(uri)
                assert proxy.system.listMethods()
                break
            except:
                continue
        return TestlinkXMLRPCAPI(proxy, devkey=self.devkey)


class TestlinkXMLRPCAPI(TestlinkAPI):
    """Interface class for Testlink's XML-RPC API

    :param xmlrpclib.ServerProxy proxy: Used Proxy Server instance
    """

    def __init__(self, proxy, *args, **kwargs):
        super(TestlinkXMLRPCAPI, self).__init__(*args, **kwargs)
        self.__proxy = proxy

        # Bootstrap Testlink API Version
        try:
            self.__version = self.proxy.tl.testLinkVersion()
        except:
            self.__version = "1.0"

    @property
    def proxy(self):
        return self.__proxy

    #
    # TestlinkAPI Interface Implementation
    #

    def __str__(self):
        return "{} {} @ {} using {}".format(self.__class__.__name__, self.version, str(self.proxy), self.devkey)

    @property
    def version(self):
        return self.__version

    def query(self, method, **parameters):
        """Executes XML-RPC call to server

        :param str method: Method to call
        :param dict parameters: Parameters to send
        """
        # Use global develop key if none is defined
        if not 'devKey' in parameters:
            parameters.update({'devKey': self.devkey})

        try:
            # Call the actual method
            LOGGER.debug(">>> Query: %s(%s)", method, parameters)
            function = getattr(self.proxy, method)

            response = function(parameters)
            LOGGER.debug("<<< Response: %s", response)
        except Exception, ex:
            LOGGER.exception(ex)
            raise
        else:
            return response

    #
    # Raw API methods
    #

    def testLinkVersion(self):
        """testLinkVersion()

        Returns Testlink Version String

        :Since: Testlink Version 1.9.9
        :rtype: str
        :return: Testlink Version String
        """
        return self.query("tl.testLinkVersion")

    def about(self):
        """about()

        Returns informations about the current Testlink API

        :rtype: str
        :returns: 'Testlink Testlink Version: x.x initially written by ...'
        """
        return self.query("tl.about")

    def sayHello(self):
        """sayHello()

        The 'Hello World' of the Testlink API.

        :rtype: str
        :returns: 'Hello!'
        """
        return self.query("tl.sayHello")
    ping = sayHello

    def repeat(self, value):
        """repeat(value)

        Repeats the given value.

        :param str value: The value to be repeated by the server
        :rtype: str
        :returns: The value send to the server
        """
        return self.query("tl.repeat", str=str(value))

    def checkDevKey(self, devkey=None):
        """checkDevKey([devkey])

        Checks if the specified developer key is valid.

        :param str devkey: The Testlink Developer Key to check. If no key is specified, the Developer Key of the current connection will be used.
        :rtype: bool
        :returns: Status of the specified Developer Key.
        """
        return self.query("tl.checkDevKey", devKey=devkey)

    def doesUserExist(self, user, devkey=None):
        """doesUserExist(user[, devkey])

        Checks, if a specified user exists.

        :param str user: The Login name of the User to check
        :param str devkey: The Testlink Developer Key. If no key is specified, the Developer Key of the current connection will be used.
        :rtype: bool
        :returns: Status of the specified User
        """
        return self.query("tl.doesUserExist", devKey=devkey, user=user)

    def getUserByLogin(self, user, devkey=None):
        """getUserByLogin(user[, devkey])

        Returns user information for specified user.

        :Since: Testlink Version 1.9.8
        :param str user: The Login name of the User to check
        :param str devkey: The Testlink Developer Key. If no key is specified, the Developer Key of the current connection will be used.
        :rtype: dict
        :returns: User Information
        """
        return self.query("tl.getUserByLogin", devKey=devkey, user=user)

    def getUserByID(self, userid, devkey=None):
        """getUserByID(userid[, devkey])

        Returns user information for specified user.

        :Since: Testlink Version 1.9.8
        :param int userid: The ID of the User to check
        :param str devkey: The Testlink Developer Key. If no key is specified, the Developer Key of the current connection will be used.
        :rtype: dict
        :returns: User Information
        """
        return self.query("tl.getUserByID", devKey=devkey, userid=userid)

    def getFullPath(self, nodeid, devkey=None):
        """getFullPath(nodeid[, devkey])

        Returns the full path of an object.

        :param int nodeid: The ID of the Node
        :param str devkey: The Testlink Developer Key. If no key is specified, the Developer Key of the current connection will be used.
        :rtype: dict
        :returns: Hierarchical Path of the specified Node
        """
        return self.query("tl.getFullPath", devKey=devkey, nodeid=int(nodeid))

    def createTestProject(self, name, prefix, notes='', active=True, public=True, requirements=False,
                          priority=False, automation=False, inventory=False, devkey=None):
        """createTestProject(name, prefix[, notes=''][, active=True][, public=True][, requirements=False][, priority=False][, automation=False][, inventory=False][, devkey])

        Creates a new TestProject with the specified parameters.

        :param str name: Name of the new TestProject
        :param str prefix: The TestCase Prefix to use within the new TestProject
        :param str notes: Description of the new TestProject
        :param bool active: Flag if the new TestProject should be active or not
        :param bool public: Flag if the new TestProject should be public or not
        :param bool requirement: Flag if the *Requirements Feature* should be enabled in the new TestProject
        :param bool priority: Flag if the *Test Priority Feature* should be enabled in the new TestProject
        :param bool automation: Flag if the *Test Automation Feature* should be enabled in the new TestProject
        :param bool inventory: Flag if the *Inventory Feature* should be enabled in the new TestProject
        :param str devkey: The Testlink Developer Key. If no key is specified, the Developer Key of the current connection will be used.
        :rtype: dict
        :returns: Server response
        """

        opts = {'requirementsEnabled': requirements,
                'testPriorityEnabled': priority,
                'automationEnabled': automation,
                'inventoryEnabled': inventory}

        return self.query("tl.createTestProject",
                           devKey=devkey,
                           name=name,
                           prefix=prefix,
                           notes=notes,
                           active=active,
                           public=public,
                           options=opts)

    def getProjects(self, devkey=None):
        """getProjects([devkey])

        Returns all available TestProjects.

        :param str devkey: The Testlink Developer Key. If no key is specified, the Developer Key of the current connection will be used.
        :rtype: list
        :returns: List of available TestProjects
        """
        return self.query("tl.getProjects", devKey=devkey)

    def getTestProjectByName(self, name, devkey=None):
        """getTestProjectByName(name[, devkey])

        Returns a single TestProject specified by its name.

        :param str name: The name of the wanted TestProject
        :param str devkey: The Testlink Developer Key. If no key is specified, the Developer Key of the current connection will be used.
        :rtype: mixed
        :returns: TestProject dictionary if TestProject has been found, else None.
        """
        resp = self.query("tl.getTestProjectByName", devKey=devkey, testprojectname=name)
        # Return None for an empty string
        if resp is not None and len(resp) == 0:
            resp = None
        return resp

    def createTestPlan(self, name, project, notes='', active=True, public=True, devkey=None):
        """createTestPlan(name, project[, notes=''][, active=True][, public=True][, devkey])

        Creates a new TestPlan with the specified parameters.

        :param str name: The Name of the new TestPlan
        :param str project: The Name of the parent TestProject
        :param str notes: Description of the new TestPlan
        :param bool active: Flag if the new TestPlan is active or not
        :param bool public: Flag if the new TestPlan is public or not
        :param str devkey: The Testlink Developer Key. If no key is specified, the Developer Key of the current connection will be used.
        :rtype: dict
        :returns: Server response

        .. todo:: Update Return Value
        """
        return self.query("tl.createTestPlan",
                           devKey=devkey,
                           testplanname=name,
                           testprojectname=project,
                           notes=notes,
                           active=active,
                           public=public)

    def getTestPlanByName(self, name, projectname, devkey=None):
        """getTestPlanByName(name, projectname[, devkey])

        Returns a single TestPlan specified by its name.

        :param str name: Name of the wanted TestPlan
        :param str projectname: Name of the parent TestProject
        :param str devkey: The Testlink Developer Key. If no key is specified, the Developer Key of the current connection will be used.
        :rtype: dict
        :returns: Server response

        .. todo:: Update Return Value
        """
        return self.query("tl.getTestPlanByName", devKey=devkey, testplanname=name, testprojectname=projectname)

    def getProjectTestPlans(self, projectid, devkey=None):
        """getProjectTestPlans(projectid[, devkey])

        Returns all TestPlans for a specified TestProject.

        :param int projectid: The internal ID of the parent TestProject
        :param str devkey: The Testlink Developer Key. If no key is specified, the Developer Key of the current connection will be used.
        :rtype: list
        :returns: Server response

        .. todo:: Update Return Value
        """
        return self.query("tl.getProjectTestPlans", devKey=devkey, testprojectid=projectid)

    def getTestPlanCustomFieldValue(self, testplanid, testprojectid, fieldname, devkey=None):
        """getTestPlanCustomFieldValue(testplanid, testprojectid, fieldname[, devkey])

        Returns the value of a specified CustomField for a specified TestPlan.

        :Since: Testlink Version 1.9.4
        :param int testplanid: The internal ID of the TestPlan
        :param int testprojectid: The internal ID of the parent TestProject
        :param str fielname: The name of the wanted custom field
        :param str devkey: The Testlink Developer Key. If no key is specified, the Developer Key of the current connection will be used.
        :rtype: mixed
        :returns: Server response

        .. todo:: Update Return Value
        """
        return self.query("tl.getTestPlanCustomFieldValue",
                           devKey=devkey,
                           customfieldname=fieldname,
                           testprojectid=testprojectid,
                           testplanid=testplanid)

    def createBuild(self, testplanid, name, notes='', devkey=None):
        """createBuild(testplanid, name[, notes=''][, devkey])

        Creates a new Build for the specified TestPlan.

        :param int testplanid: The internal ID of the parent TestPlan
        :param str name: The name of the new Build
        :param str notes: Description of the new Build
        :param str devkey: The Testlink Developer Key. If no key is specified, the Developer Key of the current connection will be used.
        :rtype: dict
        :returns: Server Response

        .. todo:: Update Return Value
        """
        return self.query("tl.createBuild",
                           devKey=devkey,
                           testplanid=testplanid,
                           buildname=name,
                           buildnotes=notes)

    def getLatestBuildForTestPlan(self, testplanid, devkey=None):
        """getLatestBuildForTestPlan(testplanid[, devkey])

        Returns the latest Build for the specified TestPlan.

        :param int testplanid: The internal ID of the TestPlan
        :param str devkey: The Testlink Developer Key. If no key is specified, the Developer Key of the current connection will be used.
        :rtype: mixed
        :returns: Server Response

        .. todo:: Update Return Value
        """
        return self.query("tl.getLatestBuildForTestPlan", devKey=devkey, testplanid=testplanid)

    def getBuildsForTestPlan(self, testplanid, devkey=None):
        """getBuildsForTestPlan(testplanid[, devkey])

        Returns all Builds for the specified TestPlan.

        :parem int testplanid: The internal ID of the TestPlan
        :param str devkey: The Testlink Developer Key. If no key is specified, the Developer Key of the current connection will be used.
        :rtype: list
        :returns: Server Response

        .. todo:: Update Return Value
        """
        return self.query("tl.getBuildsForTestPlan", devKey=devkey, testplanid=testplanid)

    def getExecCountersByBuild(self, testplanid, devkey=None):
        """getExecCountersByBuild(testplanid[, devkey])

        Returns the execution counters for a specified TestPlan.

        :Since: Testlink Version 1.9.4
        :param int testplanid: The indernal ID of the TestPlan
        :param str devkey: The Testlink Developer Key. If no key is specified, the Developer Key of the current connection will be used.
        :rtype: list
        :returns: Server Response

        .. todo:: Update Return Value
        """
        return self.query("tl.getExecCountersByBuild", devKey=devkey, testplanid=testplanid)

    def createPlatform(self, testprojectname, platformname, notes="", devkey=None):
        """createPlatform(testprojectname, platforname[, notes=""][, devkey])

        Creates a new Platform for the specified TestProject.

        :Since: Testlink Version 1.9.6
        :param str testprojectname: The name of the parent TestProject
        :param str platformname: The name of the new Platform
        :param str notes: Description of the new Platform
        :param str devkey: The Testlink Developer Key. If no key is specified, the Developer Key of the current connection will be used.
        :rtype: list
        :returns: Server Response

        .. todo:: Update Return Value
        """
        return self.query("tl.createPlatform",
                           devKey=devkey,
                           testprojectname=testprojectname,
                           platformname=platformname,
                           notes=notes)

    def getProjectPlatforms(self, testprojectid, devkey=None):
        """getProjectPlatforms(testprojectid[, devkey])

        Returns all platforms for a specified TestProject.

        :Since: Testlink Version 1.9.6
        :param int testprojectid: The internal ID of the parent TestProject
        :param str devkey: The Testlink Developer Key. If no key is specified, the Developer Key of the current connection will be used.
        :rtype: list
        :returns: Server Response

        .. todo:: Update Return Value
        """
        return self.query("tl.getProjectPlatforms", devKey=devkey, testprojectid=testprojectid)

    def getTestPlanPlatforms(self, testplanid, devkey=None):
        """getTestPlanPlatforms(testplanid[, devkey])

        Returns all Platforms fot the specified TestPlan.

        :param int testplanid: The internal ID of the TestPlan
        :param str devkey: The Testlink Developer Key. If no key is specified, the Developer Key of the current connection will be used.
        :rtype: list
        :returns: Server Response

        .. todo:: Update Return Value
        """
        return self.query("tl.getTestPlanPlatforms", devKey=devkey, testplanid=testplanid)

    def reportTCResult(self, testplanid, status, testcaseid=None, testcaseexternalid=None, buildid=None,
                       buildname=None, notes=None, guess=True, bugid=None, platformid=None, platformname=None,
                       customfields=None, overwrite=False, execduration=None, devkey=None):
        """reportTCResult(testplanid, status[, (testcaseid \| testcaseexternalid)][,( buildid \| buildname)][, notes][, guess=True][, bugid][, (platformid \| platformname)][, customfields][, overwrite=False][, execduration][, devkey])

        Sets the execution result for a specified TestCase.

        :param int testplanid: The internal ID of the parent TestPlan
        :param testlink.enums.EXECUTION_STATUS status: The Status of the Execution
        :param notes: Additional Notes for the Execution
        :param bool guess: Try to guess missing values
        :param int bugid: Bug ID related to the Execution
        :param dict customfields: Custom Field values of the Execution.
        :param bool overwrite: Overwrite last matching Execution Result
        :param float execduration: The Duration of the Execution
        :param int testcaseid: The **internal** ID of the TestCase. If not given, the **external** ID has to be specified.
        :param int testcaseexternalid: The **external** ID of the TestCase. If not given, the **internal** ID has to be specified.
        :param int buildid: The internal ID of the Build. If not given, the name of the Build has to be specified.
        :param str buildname: The Name of the Build. If not given, the internal ID of the Build has to be specified.
        :param int platformid: The internal ID of the Platform. If not given, the name of the Platform has to be specified.
        :param str platformname: The Name of the Platform. If not given, the internal ID of the Platform has to be specified.
        :param str devkey: The Testlink Developer Key. If no key is specified, the Developer Key of the current connection will be used.
        :rtype: list
        :returns: Server Response

        .. todo:: Update Return Value
        """
        arguments = {}
        if (self._tl_version >= Version("1.9.14")) or TestlinkXMLRPCAPI.IGNORE_VERSION_CHECK:
            arguments['execduration'] = execduration

        return self.query("tl.reportTCResult",
                           devKey=devkey,
                           testplanid=testplanid,
                           status=status,
                           testcaseid=testcaseid,
                           testcaseexternalid=testcaseexternalid,
                           buildid=buildid,
                           buildname=buildname,
                           notes=notes,
                           guess=guess,
                           bugid=bugid,
                           platformid=platformid,
                           platformname=platformname,
                           customfields=customfields,
                           overwrite=overwrite,
                           **arguments)
    setTestCaseExecutionResult = reportTCResult

    def getLastExecutionResult(self, testplanid, testcaseid=None, testcaseexternalid=None, platformid=None,
                               platformname=None, buildid=None, buildname=None, bugs=False, devkey=None):
        """getLastExecutionResult(testplanid[, (testcaseid \| testcaseexternalid)][, (platformname \| platformid)][, (buildid | buildname)][, bugs=False][, devkey])

        Returns the execution result for a specified TestCase and TestPlan.

        :param int testplanid: The internal ID of the TestPlan
        :param int testcaseid: The **internal** ID of the TestCase. If not given, the **external** ID has to be specified.
        :param int testcaseexternalid: The **external** ID of the TestCase. If not given, the **internal** ID has to be specified.
        :param int buildid: The internal ID of the Build. If not given, the name of the Build has to be specified.
        :param str buildname: The Name of the Build. If not given, the internal ID of the Build has to be specified.
        :param int platformid: The internal ID of the Platform. If not given, the name of the Platform has to be specified.
        :param str platformname: The Name of the Platform. If not given, the internal ID of the Platform has to be specified.
        :param bool bugs: If True, also get related bugs (**Since Testlink Version 1.9.9**)
        :param str devkey: The Testlink Developer Key. If no key is specified, the Developer Key of the current connection will be used.
        :rtype: list
        :returns: Server Response

        .. todo:: Update Return Value
        """
        arguments = {"devKey": devkey,
                     "testplanid": testplanid,
                     "testcaseid": testcaseid,
                     "testcaseexternalid": testcaseexternalid}

        if (self._tl_version >= Version("1.9.9")) or TestlinkXMLRPCAPI.IGNORE_VERSION_CHECK:
            arguments['platformid'] = platformid
            arguments['platformname'] = platformname
            arguments['buildid'] = buildid
            arguments['buildname'] = buildname
            arguments['options'] = {'getBugs': bugs}

        return self.query("tl.getLastExecutionResult", **arguments)

    def deleteExecution(self, executionid, devkey=None):
        """deleteExecution(externalid[, devkey])

        Deletes a specific exexution result.

        :param int executionid: The internal ID of the Execution
        :param str devkey: The Testlink Developer Key. If no key is specified, the Developer Key of the current connection will be used.
        :rtype: list
        :returns: Server Response

        .. todo:: Update Return Value
        """
        return self.query("tl.deleteExecution", devKey=devkey, executionid=executionid)

    def createTestSuite(self, testsuitename, testprojectid, details=None, parentid=None, order=None,
                        checkduplicatedname=True, actiononduplicatedname=DUPLICATE_STRATEGY.BLOCK, devkey=None):
        """createTestSuite(testsuitename, testprojectid[, details][, parentid][, order][, checkduplicatedname=True][, actiononduplicatedname=testlink.enums.DUPLICATE_STRATEGY.BLOCK][, devkey])

        Creates a new TestSuite with the specified parameters.

        :param str testsuitename: The name of the new TestSuite
        :param int testprojectid: The internal ID of the parent TestProject
        :param str details: Description of the new TestProject
        :param int parentid: The internal ID of the parent TestSuite. If not specified, the new TestSuite will be created at the top level.
        :param int order: The order of the new TestSuite in relation to other TestSuites within the same level.
        :param bool checkduplicatedname: Flag if check for duplicated names is active or not.
        :param testlink.enums.DUPLICATE_STRATEGY actiononduplicatedname: The Action to perform if a TestSuite with the same name is found.
        :param str devkey: The Testlink Developer Key. If no key is specified, the Developer Key of the current connection will be used.
        :rtype: list
        :returns: Server Response

        .. todo:: Update Return Value
        """
        return self.query("tl.createTestSuite",
                           devKey=devkey,
                           testsuitename=testsuitename,
                           testprojectid=testprojectid,
                           details=details,
                           parentid=parentid,
                           order=order,
                           checkduplicatedname=checkduplicatedname,
                           actiononduplicatedname=actiononduplicatedname)

    def getTestSuiteById(self, testprojectid, testsuiteid, devkey=None):
        """getTestSuiteById(testprojectid, testsuiteid[, devkey])

        Returns a single TestSuite specified by the internal ID.

        :param int testprojectid: The internal ID of the TestProject
        :param int testsuiteid: The internal ID of the wanted TestSuite
        :param str devkey: The Testlink Developer Key. If no key is specified, the Developer Key of the current connection will be used.
        :rtype: list
        :returns: Server Response

        .. todo:: Update Return Value
        """
        return self.query("tl.getTestSuiteByID", devKey=devkey, testprojectid=testprojectid, testsuiteid=testsuiteid)

    def getTestSuitesForTestSuite(self, testsuiteid, testprojectid=None, devkey=None):
        """getTestSuitesForTestSuite(testsuiteid[, devkey])

        Returns all TestSuites within the specified TestSuite.

        :param int testsuiteid: The internal ID of the parent TestSuite.
        :param int testprojectid: The internal ID of the parent TestProject (used for rights checks)
        :param str devkey: The Testlink Developer Key. If no key is specified, the Developer Key of the current connection will be used.
        :rtype: list
        :returns: Server Response

        .. todo:: Update Return Value
        """
        return self.query("tl.getTestSuitesForTestSuite", devKey=devkey, testsuiteid=testsuiteid, testprojectid=testprojectid)

    def getFirstLevelTestSuitesForTestProject(self, testprojectid, devkey=None):
        """getFirstLevelTestSuitesForTestProject(testprojecid[, devkey])

        Returns the first level TestSuites for a specified TestProject.

        :param int testprojectid: The internal ID of the parent TestProject.
        :param str devkey: The Testlink Developer Key. If no key is specified, the Developer Key of the current connection will be used.
        :rtype: list
        :returns: Server Response

        .. todo:: Update Return Value
        """
        return self.query("tl.getFirstLevelTestSuitesForTestProject", devKey=devkey, testprojectid=testprojectid)

    def getTestSuitesForTestPlan(self, planid, devkey=None):
        """getTestSuitesForTestPlan(planid[, devkey])

        Returns all TestSuites for a specified TestPlan.

        :param int planid: The internal ID of the TestPlan
        :param str devkey: The Testlink Developer Key. If no key is specified, the Developer Key of the current connection will be used.
        :rtype: list
        :returns: Server Response

        .. todo:: Update Return Value
        """
        return self.query("tl.getTestSuitesForTestPlan", devKey=devkey, testplanid=planid)

    def createTestCase(self, testcasename, testsuiteid, testprojectid, authorlogin, summary, steps=None,
                       preconditions=None, importance=IMPORTANCE_LEVEL.MEDIUM, executiontype=EXECUTION_TYPE.MANUAL,
                       order=None, checkduplicatedname=True, actiononduplicatedname=DUPLICATE_STRATEGY.BLOCK,
                       customfields=None, devkey=None):
        """createTestCase(testcasename, testsuiteid, testprojectid, authorlogin, summary[, steps][, preconditions][, importance=testlink.enums.IMPORTANCE_LEVEL.MEDIUM][, executiontype=testlink.enums.EXECUTION_TYPE.MANUAL][, order][, checkduplicatedname=True][, actiononduplicatedname=testlink.enums.DUPLICATE_STRATEGY.BLOCK][, customfields][, devkey])

        Creates a new TestCase with the specified parameters.

        :param str testcasename: The Title of the new TestCase
        :param int testsuiteid: The internal ID of the parent TestSuite
        :param int testprojectid: The internal ID of the parent TestProject
        :param str authorlogin: The login name of the Author of the new TestCase
        :param str summary: Summary of the new TestCase
        :param list steps: Steps of the new TestCase
        :param str preconditions: Preconditions of the new TestCase
        :param testlink.enums.IMPORTANCE_LEVEL importance: Importance Level of the new TestCase
        :param testlink.exnums.EXECUTION_TYPE executiontype: Execution Type of the new TestCase
        :param int order: Ordering of the new TestCase related to other TestCases in the same level
        :param bool checkduplicatedname: Flag if check for duplicated names is active or not
        :param testlink.enums.DUPLICATE_STRATEGY actiononduplicatedname: The Action to perform if a TestSuite with the same name is found.
        :param dict customfields: Custom Field values of the Execution.
        :param str devkey: The Testlink Developer Key. If no key is specified, the Developer Key of the current connection will be used.
        :rtype: list
        :returns: Server Response

        .. todo:: Update Return Value
        """
        return self.query("tl.createTestCase",
                           devKey=devkey,
                           testcasename=testcasename,
                           testsuiteid=testsuiteid,
                           testprojectid=testprojectid,
                           authorlogin=authorlogin,
                           summary=summary,
                           steps=steps,
                           preconditions=preconditions,
                           importance=importance,
                           executiontype=executiontype,
                           order=order,
                           customfields=customfields,
                           checkduplicatedname=checkduplicatedname,
                           actiononduplicatedname=actiononduplicatedname)

    def updateTestCase(self, testcaseexternalid, version=None, testcasename=None, summary=None, preconditions=None,
                       steps=None, importance=None, executiontype=None, status=None, estimatedexecduration=None,
                       user=None, devkey=None):
        """updateTestCase(testcaseexternalid[, version][, testcasename][, summary][, preconditions][, steps][, importance][, executiontype][, status][, estimatedexecduration][, user][, devkey])

        Updates a specified TestCase.

        :Since: Testlink Version 1.9.8
        :param int testcasexternalid: The **external** ID of the TestCase being edited
        :param int version: The version of the TestCase being edited
        :param str testcasename: The new name of the TestCase
        :param str summary: The new summary of the TestCase
        :param str preconditions: The new preconditions of the TestCase
        :param list steps: The new Steps of the TestCase
        :param testlink.enums.IMPORTANCE_LEVEL importance: The new Importance of the TestCase
        :param testlink.enums.EXECUTION_TYPE executiontype: The new Execution Type of the TestCase
        :param testlink.enmums.TESTCASE_STATUS status: The new Status of the TestCase
        :param float estimatedexecduration: The new estimated execution duration of the TestCase in Minutes.
        :param str user: Login name of the editing User.
        :param str devkey: The Testlink Developer Key. If no key is specified, the Developer Key of the current connection will be used.
        :rtype: list
        :returns: Server Response

        .. todo:: Update Return Value
        """
        return self.query("tl.updateTestCase",
                           devKey=devkey,
                           testcaseexternalid=testcaseexternalid,
                           version=version,
                           testcasename=testcasename,
                           summary=summary,
                           preconditions=preconditions,
                           steps=steps,
                           importance=importance,
                           executiontype=executiontype,
                           status=status,
                           estimatedexecduration=estimatedexecduration,
                           user=user)

    def setTestCaseExecutionType(self, testcaseexternalid, version, testprojectid, executiontype, devkey=None):
        """setTestCaseExecutionType(testcaseexternalid, version, testprojectid, executiontype[, devkey])

        Updates the execution type for a specified TestCase.

        :Since: Testlink Version 1.9.4
        :param int testcasexternalid: The **external** ID of the TestCase being edited
        :param int version: The version of the TestCase being edited
        :param int testprojectid: The internal ID of the parent TestProject
        :param testlink.enums.EXECUTION_TYPE executiontype: The new Execution Type of the TestCase
        :param str devkey: The Testlink Developer Key. If no key is specified, the Developer Key of the current connection will be used.
        :rtype: list
        :returns: Server Response

        .. todo:: Update Return Value
        """
        return self.query("tl.setTestCaseExecutionType",
                           devKey=devkey,
                           testcaseexternalid=testcaseexternalid,
                           version=version,
                           testprojectid=testprojectid,
                           executiontype=executiontype)

    def createTestCaseSteps(self, steps, action, testcaseid=None, testcaseexternalid=None, version=None, devkey=None):
        """createTestCaseSteps(steps, action[, (testcaseid \|testcaseexternalid)][, version][, devkey])

        Creates a new Step for the specified TestCase, can also be used for upgrade.

        :Since: Testlink Version 1.9.4
        :param list steps: New Steps for the TestCase
        :param str action: Action to perform with the new set of Steps

        .. todo:: Create STEP_ACTION enum

        :param int testcaseid: The **internal** ID of the TestCase being updated. If not given, the **external** ID must be specified.
        :param int testcaseexternalid: The **external** ID of the TestCase being updated. If not given, the **internal** ID must be specified.
        :param int version: The Version of the TestCase being updated
        :param str devkey: The Testlink Developer Key. If no key is specified, the Developer Key of the current connection will be used.
        :rtype: list
        :returns: Server Response

        .. todo:: Update Return Value
        """
        return self.query("tl.createTestCaseSteps",
                           devKey=devkey,
                           testcaseexternalid=testcaseexternalid,
                           testcaseid=testcaseid,
                           version=version,
                           action=action,
                           steps=steps)

    def deleteTestCaseSteps(self, testcaseexternalid, steps, version=None, devkey=None):
        """deleteTestCaseSteps(testcaseexternalid, steps[, version][, devkey])

        Deletes specified Steps for the specified TestCase.

        :Since: Testlink Version 1.9.4
        :param int testcaseexternalid: The **external** ID of the TestCase being updated
        :param list steps: The Steps which should be deleted
        :param int version: The Version of the TestCase being updated
        :param str devkey: The Testlink Developer Key. If no key is specified, the Developer Key of the current connection will be used.
        :rtype: list
        :returns: Server Response

        .. todo:: Update Return Value
        """
        return self.query("tl.deleteTestCaseSteps",
                           devKey=devkey,
                           testcaseexternalid=testcaseexternalid,
                           steps=steps,
                           version=version)

    def getTestCase(self, testcaseid=None, testcaseexternalid=None, version=None, devkey=None):
        """getTestCase((testcaseid \| testcaseexternalid)[, version][, devkey])

        Returns a single TestCase specified by its ID.

        :param int testcaseid: The **internal** ID of the TestCase being updated. If not given, the **external** ID must be specified.
        :param int testcaseexternalid: The **external** ID of the TestCase being updated. If not given, the **internal** ID must be specified.
        :param int version: The Version of the TestCase being updated
        :param str devkey: The Testlink Developer Key. If no key is specified, the Developer Key of the current connection will be used.
        :rtype: list
        :returns: Server Response

        .. todo:: Update Return Value
        """
        return self.query("tl.getTestCase",
                           devKey=devkey,
                           testcaseid=testcaseid,
                           testcaseexternalid=testcaseexternalid,
                           version=version)

    def getTestCaseIdByName(self, testcasename, testsuitename=None, testprojectname=None,
                            testcasepathname=None, devkey=None):
        """getTestCaseIdByName(testcasename[, testsuitename][, testprojectname][, testcasepathname][, devkey])

        Returns the internal ID of a specified TestCase.

        :param str testcasename: The name of the wanted TestCase
        :param str testsuitename: The name of tne parent TestSuite
        :param str testprojectname: The name of the parent TestProject
        :param str testcasepathname: Hierarchical Path of the wanted TestCase
        :param str devkey: The Testlink Developer Key. If no key is specified, the Developer Key of the current connection will be used.
        :rtype: list
        :returns: Server Response

        .. todo:: Update Return Value
        """
        return self.query("tl.getTestCaseIDByName",
                           devKey=devkey,
                           testcasename=testcasename,
                           testsuitename=testsuitename,
                           testprojectname=testprojectname,
                           testcasepathname=testcasepathname)

    def getTestCasesForTestSuite(self, testsuiteid, deep=False, details='simple', getkeywords=False, devkey=None):
        """getTestCasesForTestSuite(testsuiteid[, deep=False][, details='simple'][, getkeywords=False][, devkey])

        Returns all TestCases for a specified TestSuite.

        :param int testsuiteid: The internal ID of the TestSuite
        :param bool deep: Flag if TestCases should be retrieved recursively
        :param str details: Flag to set the amount of details being retrieved
        :param bool getkeywords: Flag if Keywords of the TestCase should be retrieved or not
        :param str devkey: The Testlink Developer Key. If no key is specified, the Developer Key of the current connection will be used.
        :rtype: list
        :returns: Server Response

        .. todo:: Update Return Value
        """
        arguments = {"testsuiteid": testsuiteid,
                     "deep": deep,
                     "details": details}
        if (self._tl_version >= Version("1.9.10")) or TestlinkXMLRPCAPI.IGNORE_VERSION_CHECK:
            arguments['getkeywords'] = getkeywords
        return self.query("tl.getTestCasesForTestSuite", devKey=devkey, **arguments)

    def getTestCasesForTestPlan(self, testprojectid, testplanid, testcaseid=None, buildid=None, keywordid=None,
                                keywords=None, executed=None, assignedto=None, executestatus=None, executiontype=None,
                                getstepsinfo=False, details='full', devkey=None):
        """getTestCasesForTestPlan(testprojectid, testplanid[, testcaseid][, buildid][, keywordid][, keywords][, executed][, assignedto][, executestatus][, executiontype][, getstepsinfo=False][, details='full'][, devkey])

        Returns all TestCases for a specified TestPlan.

        :param int testprojectid: The internal ID of the parent TestProject
        :param int testplanid: The internal ID of the TestPlan
        :param int testcaseid: Filter by specified internal TestCase ID
        :param int buildid: Filter by specified internal Build ID
        :param int keywordid: Filter by specified Keyword ID
        :param list keywords: Filter by specified Keywords
        :param bool executed: Filter if TestCase has been executed or not
        :param str assignedto: Filter by assigned Tester
        :param testlink.enums.EXECUTION_STATUS executestatus: Filter by specified Execution Status
        :param testlink.enums.EXECUTION_TYPE executiontype: Filter by specified Execution Type
        :param bool getstepsinfo: Flag to enable Step Information
        :param str details: Flag to control amount of retrieved Information
        :param str devkey: The Testlink Developer Key. If no key is specified, the Developer Key of the current connection will be used.
        :rtype: list
        :returns: Server Response

        .. todo:: Update Return Value
        """
        arguments = {"devKey": devkey,
                     "testprojectid": testprojectid,
                     "testplanid": testplanid,
                     "testcaseid": testcaseid,
                     "buildid": buildid,
                     "keywordid": keywordid,
                     "keywords": keywords,
                     "executed": executed,
                     "assignedto": assignedto,
                     "executestatus": executestatus,
                     "executiontype": executiontype,
                     "getstepsinfo": getstepsinfo}

        if (self._tl_version >= Version("1.9.4")) or TestlinkXMLRPCAPI.IGNORE_VERSION_CHECK:
            # Add 'details' attribute
            arguments['details'] = details

        return self.query("tl.getTestCasesForTestPlan", **arguments)

    def addTestCaseToTestPlan(self, testprojectid, testplanid, testcaseexternalid, version, platformid=None,
                              executionorder=None, urgency=None, devkey=None):
        """addTestCaseToTestPlan(testprojectid, testplanid, testcaseexternalid, version[, platformid][, executionorder][, urgency][, devkey])

        Adds a specified TestCase to a specified TestPlan.

        :param int testprojectid: The internal ID of the parent TestProject
        :param int testplanid: The internal ID of the TestPlan
        :param int testcaseexternalid: The **external** ID of the TestCase being added
        :param int version: The Version of the TestCase beind added
        :param int platformid: The internal ID of the Platform to add the TestCase to
        :param int executionorder: The ordering of the TestCase within the Execution View related to other TestCases
        :param testlink.enums.URGENCY_LEVEL urgency: The urgency of the TestCase
        :param str devkey: The Testlink Developer Key. If no key is specified, the Developer Key of the current connection will be used.
        :rtype: list
        :returns: Server Response

        .. todo:: Update Return Value
        """
        return self.query("tl.addTestCaseToTestPlan",
                           devKey=devkey,
                           testprojectid=testprojectid,
                           testplanid=testplanid,
                           testcaseexternalid=testcaseexternalid,
                           version=version,
                           platformid=platformid,
                           executionorder=executionorder,
                           urgency=urgency)

    def addPlatformToTestPlan(self, testplanid, platformname, devkey=None):
        """addPlatformToTestPlan(testplanid, platformname[, devkey])

        Adds a specified platform to a specified testplan.

        :Since: Testlink Version 1.9.6
        :param int testplanid: The internal ID of the TestPlan
        :param str platformname: The Name of the Platform being added
        :param str devkey: The Testlink Developer Key. If no key is specified, the Developer Key of the current connection will be used.
        :rtype: list
        :returns: Server Response

        .. todo:: Update Return Value
        """
        return self.query("tl.addPlatformToTestPlan",
                           devKey=devkey,
                           testplanid=testplanid,
                           platformname=platformname)

    def removePlatformFromTestPlan(self, testplanid, platformname, devkey=None):
        """removePlatformFromTestPlan(testplanid, platformname[, devkey])

        Removes a specified platform from a specified testplan.

        :Since: Testlink Version 1.9.6
        :param int testplanid: The internal ID of the TestPlan
        :param str platformname: The Name of the Platform being removed
        :param str devkey: The Testlink Developer Key. If no key is specified, the Developer Key of the current connection will be used.
        :rtype: list
        :returns: Server Response

        .. todo:: Update Return Value
        """
        return self.query("tl.removePlatformFromTestPlan",
                           devKey=devkey,
                           testplanid=testplanid,
                           platformname=platformname)

    def assignRequirements(self, testcaseexternalid, testprojectid, requirements, devkey=None):
        """assignRequirements(testcaseexternalid, testprojectid, requirements[, devkey])

        Assigns specified Requirements to a specified TestCase.

        :param int testcaseexternalid: The **external** ID of the TestCase
        :param int testprojectid: The internal ID of the TestProject
        :param list requirements: Requirements to assign to the TestCase
        :param str devkey: The Testlink Developer Key. If no key is specified, the Developer Key of the current connection will be used.
        :rtype: list
        :returns: Server Response

        .. todo:: Update Return Value
        """
        return self.query("tl.assignRequirements",
                           devKey=devkey,
                           testcaseexternalid=testcaseexternalid,
                           testprojectid=testprojectid,
                           requirements=requirements)

    def getReqSpecCustomFieldDesignValue(self, reqspecid, testprojectid, customfieldname, devkey=None):
        """getReqSpecCustomFieldDesignValue(reqspecid, testprojectid, customfieldname[, devkey])

        Returns the value of a specified CustomField for a specified Requirement Specification.

        :Since: Testlink Version 1.9.4
        :param int reqspecid: The internal ID of the Requirement Specification
        :param int testprojectid: The internal ID of the TestProject
        :param str customfieldname: The name of the wanted Custom Field
        :param str devkey: The Testlink Developer Key. If no key is specified, the Developer Key of the current connection will be used.
        :rtype: list
        :returns: Server Response

        .. todo:: Update Return Value
        """
        return self.query("tl.getReqSpecCustomFieldDesignValue",
                           devKey=devkey,
                           customfieldname=customfieldname,
                           testprojectid=testprojectid,
                           reqspecid=reqspecid)

    def getRequirementCustomFieldDesignValue(self, requirementid, testprojectid, customfieldname, devkey=None):
        """getRequirementCustomFieldDesignValue(requirementid, testprojectid, customfieldname[, devkey])

        Returns the value of a specified CustomField for a specified Requirement.

        :Since: Testlink Version 1.9.4
        :param int requirementid: The internal ID of the Requirement
        :param int testprojectid: The internal ID of the TestProject
        :param str customfieldname: The name of the wanted Custom Field
        :param str devkey: The Testlink Developer Key. If no key is specified, the Developer Key of the current connection will be used.
        :rtype: list
        :returns: Server Response

        .. todo:: Update Return Value
        """
        return self.query("tl.getRequirementCustomFieldDesignValue",
                           devKey=devkey,
                           customfieldname=customfieldname,
                           testprojectid=testprojectid,
                           requirementid=requirementid)

    def getTestSuiteCustomFieldDesignValue(self, testsuiteid, testprojectid, customfieldname, devkey=None):
        """getTestSuiteCustomFieldDesignValue(testsuiteid, testprojectid, customfieldname[, devkey])

        Returns the value of a specified CustomField for a specified TestSuite.

        :Since: Testlink Version 1.9.4
        :param int testsuiteid: The internal ID of the TestSuite
        :param int testprojectid: The internal ID of the TestProject
        :param str customfieldname: The name of the wanted Custom Field
        :param str devkey: The Testlink Developer Key. If no key is specified, the Developer Key of the current connection will be used.
        :rtype: list
        :returns: Server Response

        .. todo:: Update Return Value
        """
        return self.query("tl.getTestSuiteCustomFieldDesignValue",
                           devKey=devkey,
                           customfieldname=customfieldname,
                           testprojectid=testprojectid,
                           testsuiteid=testsuiteid)

    def getTestCaseCustomFieldDesignValue(self, testcaseexternalid, version, testprojectid, customfieldname,
                                          details='value', devkey=None):
        """getTestCaseCustomFieldDesignValue(testcaseexternalid, version, testprojectid, customfieldname[, details='value'][, devkey])

        Returns the value of a specified CustomField for a specified TestCase.

        :param int testcaseexternalid: The **external** ID of the TestCase
        :param int version: The Version of the TestCase
        :param int testprojectid: The internal ID of the TestProject
        :param str customfieldname: The name of the wanted Custom Field
        :param str details: Flag to control the amount of Information
        :param str devkey: The Testlink Developer Key. If no key is specified, the Developer Key of the current connection will be used.
        :rtype: list
        :returns: Server Response

        .. todo:: Update Return Value
        """
        resp = self.query("tl.getTestCaseCustomFieldDesignValue",
                           devKey=devkey,
                           testcaseexternalid=testcaseexternalid,
                           version=version,
                           testprojectid=testprojectid,
                           customfieldname=customfieldname,
                           details=details)
        # Return None for an empty string
        if resp is not None and len(resp) == 0:
            resp = None
        return resp

    def updateTestCaseCustomFieldDesignValue(self, testcaseexternalid, version, testprojectid, customfields=None,
                                             devkey=None):
        """updateTestCaseCustomFieldDesignValue(testcaseexternalid, version, testprojectid[, customfields][, devkey])

        Updates values of CustomFields for a specified TestCase.

        :Since: Testlink Version 1.9.4
        :param int testcasexternalid: The **external** ID of the TestCase being edited
        :param int version: The Version of the TestCase being edited
        :param int testprojectid: The internal ID of the parent TestProject
        :param dict customfields: Custom Fields to edit
        :param str devkey: The Testlink Developer Key. If no key is specified, the Developer Key of the current connection will be used.
        :rtype: list
        :returns: Server Response

        .. todo:: Update Return Value
        """
        return self.query("tl.updateTestCaseCustomFieldDesignValue",
                           devKey=devkey,
                           testcaseexternalid=testcaseexternalid,
                           version=version,
                           testprojectid=testprojectid,
                           customfields=customfields)

    def getTestCaseCustomFieldExecutionValue(self, executionid, testplanid, version, testprojectid, customfieldname,
                                             devkey=None):
        """getTestCaseCustomFieldExecutionValue(executionid, testplanid, version, testprojectid, customfieldname[, devkey])

        Returns the value of a specified CustomField for a specified Execution.

        :Since: Testlink Version 1.9.4
        :param int executionid: The internal ID of the Execution
        :param int testplanid: The internal ID of the TestPlan
        :param int version: The Verion of the TestCase
        :param int testprojectid: The internal ID of the parent TestProject
        :param str customfieldname: The name of the wanted Custom Field
        :param str devkey: The Testlink Developer Key. If no key is specified, the Developer Key of the current connection will be used.
        :rtype: list
        :returns: Server Response

        .. todo:: Update Return Value
        """
        return self.query("tl.getTestCaseCustomFieldExecutionValue",
                           devKey=devkey,
                           customfieldname=customfieldname,
                           testprojectid=testprojectid,
                           version=version,
                           executionid=executionid,
                           testplanid=testplanid)

    def getTestCaseCustomFieldTestPlanDesignValue(self, linkid, testplanid, version, testprojectid, customfieldname,
                                                  devkey=None):
        """getTestCaseCustomFieldTestPlanDesignValue(linkid, testplanid, version, testprojectid, customfieldname[, devkey])

        Returns the value of the specified CustomField for a specified TestCase within a specified TestPlan,

        :Since: Testlink Version 1.9.4
        :param int linkid: The internal ID of the Relation between TestCase and TestPlan
        :param int testplanid: The internal ID of the TestPlan
        :param int version: The Version of the TestCase
        :param int testprojectid: The internal ID of the parent TestProject
        :param str customfieldname: The name of the wanted Custom Field
        :param str devkey: The Testlink Developer Key. If no key is specified, the Developer Key of the current connection will be used.
        :rtype: list
        :returns: Server Response

        .. todo:: Update Return Value
        """
        return self.query("tl.getTestCaseCustomFieldTestPlanDesignValue",
                           devKey=devkey,
                           customfieldname=customfieldname,
                           testprojectid=testprojectid,
                           version=version,
                           testplanid=testplanid,
                           linkid=linkid)

    def uploadAttachment(self, fkid, fktable, filename, filetype, content, title=None, description=None, devkey=None):
        """uploadAttachment(fkid, fktable, filename, filetype, content[, title][, description][, devkey])

        Uploads the specified Attachment for the specified object.

        :param int fkid: The internal ID of the attached Object
        :param str fktable: The Table name of the attached Object
        :param str filename: The filename of the Attachment
        :param str filetype: The MIME-Type of the Attachment
        :param str content: Base64 encoded contents of the Attachment
        :param str title: Title for the Attachment
        :param str description: Description of the Attachment
        :param str devkey: The Testlink Developer Key. If no key is specified, the Developer Key of the current connection will be used.
        :rtype: list
        :returns: Server Response

        .. todo:: Update Return Value
        """
        return self.query("tl.uploadAttachment",
                           devKey=devkey,
                           fkid=fkid,
                           fktable=fktable,
                           filename=filename,
                           filetype=filetype,
                           content=content,
                           title=title,
                           description=description)

    def deleteAttachment(self, attachment_id, devkey=None):
        """deleteAttachment(attachment_id[, devkey])

        Deletes the specified attachment.

        :Since: Custom Testlink Verion 1.11.0-sinaqs
        :param int attachment_id: The internal ID of the Attachment to delete
        :param str devkey: The Testlink Developer Key. If no key is specified, the Developer Key of the current connection will be used.
        :rtype: list
        :returns: Server Response

        .. todo:: Update Return Value
        """
        return self.query("tl.deleteAttachment", devKey=devkey, attachmentid=attachment_id)

    def uploadRequirementSpecificationAttachment(self, reqspecid, filename, filetype, content, title=None,
                                                 description=None, devkey=None):
        """uploadRequirementSpecificationAttachment(reqspecid, filename, filetype, content[, title][, description][, devkey])

        Uploads the specified Attachment for the specified Requirement Specification.

        :param int reqspecid: The internal ID of the Requirement Specification
        :param str filename: The filename of the Attachment
        :param str filetype: The MIME-Type of the Attachment
        :param str content: Base64 encoded contents of the Attachment
        :param str title: Title for the Attachment
        :param str description: Description of the Attachment
        :param str devkey: The Testlink Developer Key. If no key is specified, the Developer Key of the current connection will be used.
        :rtype: list
        :returns: Server Response

        .. todo:: Update Return Value
        """
        return self.query("tl.uploadRequirementSpecificationAttachment",
                           devKey=devkey,
                           reqspecid=reqspecid,
                           filename=filename,
                           filetype=filetype,
                           content=content,
                           title=title,
                           description=description)

    def uploadRequirementAttachment(self, requirementid, filename, filetype, content, title=None, description=None, devkey=None):
        """uploadRequirementAttachment(requirementid, filename, filetype, content[, title][, description][, devkey])

        Uploads the specified Attachment for the specified Requirement.

        :param int requirementid: The internal ID of the Requirement
        :param str filename: The filename of the Attachment
        :param str filetype: The MIME-Type of the Attachment
        :param str content: Base64 encoded contents of the Attachment
        :param str title: Title for the Attachment
        :param str description: Description of the Attachment
        :param str devkey: The Testlink Developer Key. If no key is specified, the Developer Key of the current connection will be used.
        :rtype: list
        :returns: Server Response

        .. todo:: Update Return Value
        """
        return self.query("tl.uploadRequirementAttachment",
                           devKey=devkey,
                           requirementid=requirementid,
                           filename=filename,
                           filetype=filetype,
                           content=content,
                           title=title,
                           description=description)

    def uploadTestProjectAttachment(self, testprojectid, filename, filetype, content, title=None, description=None, devkey=None):
        """uploadTestProjectAttachment(testprojectid, filename, filetype, content[, title][, description][, devkey])

        Uploads the specified Attachment for the specified TestProject

        :param int testprojectid: The internal ID of the TestProject
        :param str filename: The filename of the Attachment
        :param str filetype: The MIME-Type of the Attachment
        :param str content: Base64 encoded contents of the Attachment
        :param str title: Title for the Attachment
        :param str description: Description of the Attachment
        :param str devkey: The Testlink Developer Key. If no key is specified, the Developer Key of the current connection will be used.
        :rtype: list
        :returns: Server Response

        .. todo:: Update Return Value
        """
        return self.query("tl.uploadTestProjectAttachment",
                           devKey=devkey,
                           testprojectid=testprojectid,
                           filename=filename,
                           filetype=filetype,
                           content=content,
                           title=title,
                           description=description)

    def uploadTestSuiteAttachment(self, testsuiteid, filename, filetype, content, title=None, description=None, devkey=None):
        """uploadTestProjectAttachment(testsuiteid, filename, filetype, content[, title][, description][, devkey])

        Uploads the specified Attachment for the specified TestSuite.

        :param int testsuiteid: The internal ID of the TestSuite
        :param str filename: The filename of the Attachment
        :param str filetype: The MIME-Type of the Attachment
        :param str content: Base64 encoded contents of the Attachment
        :param str title: Title for the Attachment
        :param str description: Description of the Attachment
        :param str devkey: The Testlink Developer Key. If no key is specified, the Developer Key of the current connection will be used.
        :rtype: list
        :returns: Server Response

        .. todo:: Update Return Value
        """
        return self.query("tl.uploadTestSuiteAttachment",
                           devKey=devkey,
                           testsuiteid=testsuiteid,
                           filename=filename,
                           filetype=filetype,
                           content=content,
                           title=title,
                           description=description)

    def uploadTestCaseAttachment(self, testcaseid, filename, filetype, content, title=None, description=None, devkey=None):
        """uploadTestCaseAttachment(testcaseid, filename, filetype, content[, title][, description][, devkey])

        Uploads the specified Attachment for the specified TestCase.

        :param int testcaseid: The internal ID of the TestCase
        :param str filename: The filename of the Attachment
        :param str filetype: The MIME-Type of the Attachment
        :param str content: Base64 encoded contents of the Attachment
        :param str title: Title for the Attachment
        :param str description: Description of the Attachment
        :param str devkey: The Testlink Developer Key. If no key is specified, the Developer Key of the current connection will be used.
        :rtype: list
        :returns: Server Response

        .. todo:: Update Return Value
        """
        return self.query("tl.uploadTestCaseAttachment",
                           devKey=devkey,
                           testcaseid=testcaseid,
                           filename=filename,
                           filetype=filetype,
                           content=content,
                           title=title,
                           description=description)

    def uploadExecutionAttachment(self, executionid, filename, filetype, content, title=None, description=None, devkey=None):
        """uploadTestCaseAttachment(executionid, filename, filetype, content[, title][, description][, devkey])

        Uploads the specified Attachment for the specified Execution

        :param int executionid: The internal ID of the Execution
        :param str filename: The filename of the Attachment
        :param str filetype: The MIME-Type of the Attachment
        :param str content: Base64 encoded contents of the Attachment
        :param str title: Title for the Attachment
        :param str description: Description of the Attachment
        :param str devkey: The Testlink Developer Key. If no key is specified, the Developer Key of the current connection will be used.
        :rtype: list
        :returns: Server Response

        .. todo:: Update Return Value
        """
        return self.query("tl.uploadExecutionAttachment",
                           devKey=devkey,
                           executionid=executionid,
                           filename=filename,
                           filetype=filetype,
                           content=content,
                           title=title,
                           description=description)

    def getTestCaseAttachments(self, testcaseid=None, testcaseexternalid=None, devkey=None):
        """getTestCaseAttachments((testcaseid \| testcaseexternalid)[, devkey])

        Returns all available Attachments for the specified TestCase.

        :param int testcaseid: The **internal** ID of the TestCase. If not given, the **external** ID has to be specified.
        :param int testcaseexternalid: The **external** ID of the TestCase. If not given, the **internal** ID has to be specified.
        :param str devkey: The Testlink Developer Key. If no key is specified, the Developer Key of the current connection will be used.
        :rtype: list
        :returns: Server Response

        .. todo:: Update Return Value
        """
        return self.query("tl.getTestCaseAttachments",
                           devKey=devkey,
                           testcaseid=testcaseid,
                           testcaseexternalid=testcaseexternalid)

    def getRequirementSpecificationsForTestProject(self, testprojectid, devkey=None):
        """getRequirementSpecificationsForTestProject(testprojectid[, devkey])

        Returns all available Requirement Specifications for the specified TestProject.

        :Since: Custom Testlink Version 1.11.0-sinaqs
        :param int testprojectid: The internal ID of the TestProject
        :param str devkey: The Testlink Developer Key. If no key is specified, the Developer Key of the current connection will be used.
        :rtype: list
        :returns: Server Response

        .. todo:: Update Return Value
        """
        return self.query("tl.getRequirementSpecificationsForTestProject",
                           devKey=devkey,
                           testprojectid=testprojectid)

    def getRequirementSpecificationsForRequirementSpecification(self, reqspecid, devkey=None):
        """getRequirementSpecificationsForRequirementSpecification(reqspecid[, devkey])

        Returns all available Requirement Specifications for the specified Requirement Specification.

        :Since: Custom Testlink Version 1.11.0-sinaqs
        :param int reqspecid: The internal ID of the Requirement Specification
        :param str devkey: The Testlink Developer Key. If no key is specified, the Developer Key of the current connection will be used.
        :rtype: list
        :returns: Server Response

        .. todo:: Update Return Value
        """
        return self.query("tl.getRequirementSpecificationsForRequirementSpecification",
                           devKey=devkey,
                           reqspecid=reqspecid)

    def getRequirementsForRequirementSpecification(self, reqspecid, testprojectid, devkey=None):
        """getRequirementsForRequirementSpecification(reqspecid, testprojectid[, devkey=None])

        Returns all available Requirements for the specified Requirement Specification.

        :Since: Custom Testlink Version 1.11.0-sinaqs
        :param int reqspecid: The internal ID of the Requirement Specification
        :param int testprojectid: The internal ID of the parent TestProject
        :param str devkey: The Testlink Developer Key. If no key is specified, the Developer Key of the current connection will be used.
        :rtype: list
        :returns: Server Response

        .. todo:: Update Return Value
        """
        return self.query("tl.getRequirementsForRequirementSpecification",
                           devKey=devkey,
                           reqspecid=reqspecid,
                           testprojectid=testprojectid)

    def getRisksForRequirement(self, requirementid, devkey=None):
        """getRisksForRequirement(requirementid[, devkey])

        Returns all avaialble Risks for the specified Requirement.

        :Since: Custom Testlink Version 1.11.0-sinaqs
        :param int requirementid: The internal ID of the Requirement
        :param str devkey: The Testlink Developer Key. If no key is specified, the Developer Key of the current connection will be used.
        :rtype: list
        :returns: Server Response

        .. todo:: Update Return Value
        """
        return self.query("tl.getRisksForRequirement", devKey=devkey, requirementid=requirementid)

    def createRequirementSpecification(self, testprojectid, parentid, docid, title, scope, userid, typ, devkey=None):
        """createRequirementSpecification(testprojecid, parentid, docid, title, scope, userid, typ[, devkey])

        Creates a new Requirement Specification with the specified parameters.

        :Since: Custom Testlink Version 1.11.0-sinaqs
        :param int testprojectid: The internal ID of the parent TestProject
        :param int parentid: The internal ID of the parent Requirement Specification
        :param str docid: The Document ID of the new Requirement Specification
        :param str title: The name of the new Requiremenet Specification
        :param str scope: The scope of the new Requirement Specification
        :param int userid: The internal User ID of the Author

        .. todo:: What is typ

        :param str typ: None
        :param str devkey: The Testlink Developer Key. If no key is specified, the Developer Key of the current connection will be used.
        :rtype: list
        :returns: Server Response

        .. todo:: Update Return Value
        """
        return self.query("tl.createRequirementSpecification",
                           devKey=devkey,
                           testprojectid=testprojectid,
                           parentid=parentid,
                           docid=docid,
                           title=title,
                           scope=scope,
                           userid=userid,
                           type=typ)

    def createRequirement(self, testprojectid, reqspecid, docid, title, scope, userid, status, typ, coverage=1,
                          devkey=None):
        """createRequirement(testprojectid, reqspecid, docid, title, scope, userid, status, typ[, coverage=1][, devkey])

        Creates a new Requirement with the specified parameters.

        :Since: Custom Testlink Version 1.11.0-sinaqs
        :param int testprojectid: The internal ID of the parent TestProject
        :param int reqspecid: The internal ID of the parent Requirement Specification
        :param str docid: The Document ID of the new Requirement
        :param str title: The name of the new Requirement
        :param str scope: The scope of the new Requirement
        :param testlink.enums.REQUIREMENT_STATUS status: The status of the new Requirement
        :param testlink.enums.REQUIREMENT_TYPE typ: The type of the new Requirement
        :param int coverage: The expected Coverage of the Requirement
        :param str devkey: The Testlink Developer Key. If no key is specified, the Developer Key of the current connection will be used.
        :rtype: list
        :returns: Server Response

        .. todo:: Update Return Value
        .. todo:: Modify 'typ'
        """
        return self.query("tl.createRequirement",
                           devKey=devkey,
                           testprojectid=testprojectid,
                           reqspecid=reqspecid,
                           docid=docid,
                           title=title,
                           scope=scope,
                           userid=userid,
                           status=status,
                           type=typ,
                           coverage=coverage)

    def createRisk(self, requirementid, docid, title, scope, userid, coverage=None, devkey=None):
        """createRisk(requirementid, docid, title, scope, userid[, coverage][, devkey])

        Creates a new Risk with the specified parameters.

        :Since: Custom Testlink Version 1.11.0-sinaqs
        :param requirementid: The internal ID of the parent Requirement
        :param str docid: The Document ID of the new Risk
        :param str title: The name of the new Risk
        :param str scope: The scope of the new Risk
        :param int userid: The internal User ID of the Author
        :param list coverage: List of covered TestCases
        :param str devkey: The Testlink Developer Key. If no key is specified, the Developer Key of the current connection will be used.
        :rtype: list
        :returns: Server Response

        .. todo:: Update Return Value
        """
        return self.query("tl.createRisk",
                           devKey=devkey,
                           requirementid=requirementid,
                           docid=docid,
                           title=title,
                           scope=scope,
                           userid=userid,
                           coverage=coverage)

    def assignRisks(self, testcaseexternalid, testprojectid, risks, devkey=None):
        """assignRisks(testcaseexternalid, testprojectid, risks[, devkey])

        Assigns risks to a testcase.

        :Since: Custom Testlink Version 1.11.0-sinaqs
        :param int testcaseexternalid: The **external** ID of the TestCase
        :param int testprojectid: The internal ID of the parent TestProject
        :param list risks: Risks to assign to the TestCase
        :param str devkey: The Testlink Developer Key. If no key is specified, the Developer Key of the current connection will be used.
        :rtype: list
        :returns: Server Response

        .. todo:: Update Return Value
        """
        return self.query("tl.assignRisks",
                           devKey=devkey,
                           testprojectid=testprojectid,
                           testcaseexternalid=testcaseexternalid,
                           risks=risks)

    def getExecutions(self, testplanid, testcaseid=None, testcaseexternalid=None, platformid=None, platformname=None,
                      buildid=None, buildname=None, bugs=False, devkey=None):
        """getExecutions(testplanid[, (testcaseid \| testcaseexternalid)][, (platformname \| platformid)][, (buildid | buildname)][, bugs=False][, devkey])

        Returns all execution result for a specified TestCase and TestPlan.

        :Since: Custom Testlink Version 1.11.0-sinaqs
        :param int testplanid: The internal ID of the TestPlan
        :param int testcaseid: The **internal** ID of the TestCase. If not given, the **external** ID has to be specified.
        :param int testcaseexternalid: The **external** ID of the TestCase. If not given, the **internal** ID has to be specified.
        :param int buildid: The internal ID of the Build. If not given, the name of the Build has to be specified.
        :param str buildname: The Name of the Build. If not given, the internal ID of the Build has to be specified.
        :param int platformid: The internal ID of the Platform. If not given, the name of the Platform has to be specified.
        :param str platformname: The Name of the Platform. If not given, the internal ID of the Platform has to be specified.
        :param bool bugs: If True, also get related bugs (**Since Testlink Version 1.9.9**)
        :param str devkey: The Testlink Developer Key. If no key is specified, the Developer Key of the current connection will be used.
        :rtype: list
        :returns: Server Response

        .. todo:: Update Return Value
        """
        return self.query("tl.getExecutions",
                           devKey=devkey,
                           testplanid=testplanid,
                           testcaseid=testcaseid,
                           testcaseexternalid=testcaseexternalid,
                           platformid=platformid,
                           platformname=platformname,
                           buildid=buildid,
                           buildname=buildname,
                           options={'getBugs': bugs})

    def getAttachments(self, fkid, fktable, devkey=None):
        """getAttachments(fkid, fktable[, devkey])

        Returns an attachment for the specified ID in the specified table.

        :Since: Custom Testlink Version 1.11.0-sinaqs
        :param int fkid: The internal ID of the attached Object
        :param str fktable: The Table name of the attached Object
        :param str devkey: The Testlink Developer Key. If no key is specified, the Developer Key of the current connection will be used.
        :rtype: list
        :returns: Server Response

        .. todo:: Update Return Value
        """
        return self.query("tl.getAttachments",
                           devKey=devkey,
                           fkid=fkid,
                           fktable=fktable)

    def getRequirementCoverage(self, requirementid, testplanid=None, platformid=None, devkey=None):
        """getRequirementCoverage(requirementid[, testplanid][, platformid][, devkey])

        Returns the coverage for a specified Requirement within a given context.

        :Since: Custom Testlink Version 1.11.0-sinaqs
        :param int requirementid: The internal ID of the Requirement
        :param int testplanid: The internal ID of the TestPlan to filter Coverage by TestPlan
        :param int platformid: The internal ID of the Platform to filter Coverage by TestPlan
        :param str devkey: The Testlink Developer Key. If no key is specified, the Developer Key of the current connection will be used.
        :rtype: list
        :returns: Server Response

        .. todo:: Update Return Value
        """
        return self.query('tl.getRequirementCoverage',
                           devKey=devkey,
                           requirementid=requirementid,
                           testplanid=testplanid,
                           platformid=platformid)
