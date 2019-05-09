# -*- coding: utf-8 -*-

"""
@author: Kai Borowiak
@summary: TestSuite for testlink.api.TestlinkXMLRPCAPI
"""

# IMPORTS
import string
import unittest
import mock
import testlink.enums
from pkg_resources import parse_version as Version
from testlink.api import TestlinkXMLRPCAPI
from testlink.exceptions import NotSupported
from testlink.exceptions import APIError
from testlink.exceptions import ConnectionError


class ServerMock(mock.Mock):
    """XML-RPC Server mock.Mock"""
    system = mock.Mock()
    system.listMethods = mock.Mock()

    def __init__(self, *args, **kwargs):
        super(ServerMock, self).__init__(*args, **kwargs)


class TestlinkXMLRPCAPITests(unittest.TestCase):
    """Testcases for Testlink XML-RPC API Wrapper"""

    def __init__(self, *args, **kwargs):
        super(TestlinkXMLRPCAPITests, self).__init__(*args, **kwargs)
        self._testMethodDoc = "TestlinkXMLRPCAPI: " + str(self._testMethodDoc)

    def setUp(self):
        """Needed to connect to a mocked Server endpoint in each test"""
        self._patcher = mock.patch('xmlrpclib.ServerProxy', new=ServerMock, spec=True)
        self._mock_server = self._patcher.start()
        self._api = TestlinkXMLRPCAPI("http://localhost/lib/api/xmlrpc.php")
        self._api._proxy = self._mock_server

    def tearDown(self):
        self._patcher.stop()

    # We need to patch to the 'real' ServerProxy here to get good results
    def test_invalid_url(self):
        """Invalid URL"""
        self.assertRaises(Exception, TestlinkXMLRPCAPI)
        self.assertRaises(ConnectionError, TestlinkXMLRPCAPI, "")
        self.assertRaises(ConnectionError, TestlinkXMLRPCAPI, "foo")
        self.assertRaises(ConnectionError, TestlinkXMLRPCAPI, "http://")

    def test_query(self):
        """Query wrapper"""
        # Define mock endpoints
        self._mock_server.passed = mock.Mock(return_value="SPAM!")
        self._mock_server.error = mock.Mock(return_value=[{'code': 1337, 'message': 'SPAM!'}])

        # Check endpoints
        self.assertEqual(self._api._query("passed"), "SPAM!")
        self.assertRaises(APIError, self._api._query, "error")

        # Check APIError struct
        try:
            self._api._query("error")
        except APIError, error:
            self.assertEquals(error.error_code, 1337)
            self.assertEquals(error.error_msg, "SPAM!")

        # Check correct variable forwarding
        data = {'testprojectid': 123, 'name': 'Testproject', 'is_active': True}
        self._api._query("passed", **data)
        data.update({'devKey': None})
        self._mock_server.passed.assert_called_with(data)

    @mock.patch("testlink.api.TestlinkXMLRPCAPI._reconnect")
    def test_socket_error(self, reconnect):
        """Socket Error"""
        import socket
        # Define faulty endpoint
        self._mock_server.socketerror = mock.Mock(side_effect=socket.error())
        # Do the call
        self.assertRaises(socket.error, self._api._query, "socketerror")
        # Check that reconnect has been called
        self.assertTrue(reconnect.called)

    def test_global_devkey(self):
        """Global DevKey setting"""
        key = '123456789ABCDEF'
        test_data = {'foo': 'bar'}
        self._api._devkey = key
        self._mock_server.mockMethod = mock.MagicMock()
        self._api._query("mockMethod", **test_data)
        test_data["devKey"] = key
        self._mock_server.mockMethod.assert_called_with(test_data)

    #
    # Since the raw API calls are very simple, some checks can be done
    # together. For each raw call, the following things are checked:
    #     - Method raises NotSupported if called within wrong API version
    #     - No manipulation of server response (result of _query method call)
    #     - Correct naming and forwarding of arguments
    #       to internal _query method
    #
    # @mock.patch("testlink.api.TestlinkXMLRPCAPI._query")
    # def test_foo(self, query):
    #     """'foo' (x.x.x)"""    # <-- Method and TL version
    #
    #     # Mock query result (since this is checked separaterly)
    #     query.return_value = ...
    #
    #     # Define test data
    #     test_data = ...
    #
    #     # Version check if api version > 1.0
    #     self.assertRaises(NotSupported, self._api.foo)
    #     self._api._tl_version = Version("x.x.x")
    #
    #     # Verify if result matches with query result (no data manipulation)
    #     # Also verify passed arguments
    #     self.assertEquals(self._api.foo(**test_data), query.return_value)
    #     query.assert_called_with('foo',**test_data)
    #
    #     # Version check if api version = 1.0
    #     self._api._tl_version = Version("0.9")
    #     self.assertRaises(NotSupported, self._api.foo)
    #

    @mock.patch("testlink.api.TestlinkXMLRPCAPI._query")
    def test_testlink_version(self, query):
        """'testLinkVersion' (1.9.9)"""
        # First _query fails because NotSupported
        query.return_value = "1.9.9"
        query.side_effect = NotSupported('tl.testLinkVersion')
        self.assertRaises(NotSupported, self._api.testLinkVersion)

        query.side_effect = None
        self._api._tl_version = Version("1.9.9")
        self.assertEquals(self._api.testLinkVersion(), query.return_value)
        query.assert_called_with('tl.testLinkVersion')

    @mock.patch("testlink.api.TestlinkXMLRPCAPI._query")
    def test_about(self, query):
        """'about' (1.0)"""
        self.assertEquals(self._api.about(), query.return_value)
        query.assert_called_with('tl.about')
        self._api._tl_version = Version("0.9")
        self.assertRaises(NotSupported, self._api.about)

    @mock.patch("testlink.api.TestlinkXMLRPCAPI._query")
    def test_say_hello(self, query):
        """'sayHello' (1.0)"""
        self.assertEquals(self._api.sayHello(), query.return_value)
        query.assert_called_with('tl.sayHello')
        self._api._tl_version = Version("0.9")
        self.assertRaises(NotSupported, self._api.sayHello)

    @mock.patch("testlink.api.TestlinkXMLRPCAPI._query")
    def test_repeat(self, query):
        """'repeat' (1.0)"""
        test_data = 'repeatMe'
        self._api.repeat(test_data)
        query.assert_called_with('tl.repeat', str=test_data)
        self._api._tl_version = Version("0.9")
        self.assertRaises(NotSupported, self._api.repeat)

    @mock.patch("testlink.api.TestlinkXMLRPCAPI._query")
    def test_check_devkey(self, query):
        """'checkDevKey' (1.0)"""
        test_data = '123456789abcdef123456789abcdeff'
        self._api.checkDevKey(test_data)
        query.assert_called_with('tl.checkDevKey', devKey=test_data)
        self._api._tl_version = Version("0.9")
        self.assertRaises(NotSupported, self._api.checkDevKey)

    @mock.patch("testlink.api.TestlinkXMLRPCAPI._query")
    def test_does_user_exist(self, query):
        """'doesUserExist' (1.0)"""
        test_data = 'user.login'
        self._api.doesUserExist(test_data)
        query.assert_called_with('tl.doesUserExist', user=test_data, devKey=None)
        self._api._tl_version = Version("0.9")
        self.assertRaises(NotSupported, self._api.doesUserExist)

    @mock.patch("testlink.api.TestlinkXMLRPCAPI._query")
    def test_get_user_by_login(self, query):
        """'getUserByLogin' (1.9.8)"""
        test_data = 'user.login'
        self.assertRaises(NotSupported, self._api.getUserByLogin)
        self._api._tl_version = Version("1.9.8")
        self._api.getUserByLogin(test_data)
        query.assert_called_with('tl.getUserByLogin', user=test_data, devKey=None)

    @mock.patch("testlink.api.TestlinkXMLRPCAPI._query")
    def test_get_user_by_id(self, query):
        """'getUserByID' (1.9.8)"""
        test_data = 23
        self.assertRaises(NotSupported, self._api.getUserByID)
        self._api._tl_version = Version("1.9.8")
        self._api.getUserByID(test_data)
        query.assert_called_with('tl.getUserByID', userid=test_data, devKey=None)

    @mock.patch("testlink.api.TestlinkXMLRPCAPI._query")
    def test_get_full_path(self, query):
        """'getFullPath' (1.0)"""
        test_data = 123456
        self._api.getFullPath(test_data)
        query.assert_called_with('tl.getFullPath', nodeid=test_data, devKey=None)
        self._api._tl_version = Version("0.9")
        self.assertRaises(NotSupported, self._api.getFullPath)

    @mock.patch("testlink.api.TestlinkXMLRPCAPI._query")
    def test_create_testproject(self, query):
        """'createTestProject' (1.0)"""
        # Check default params
        defaults = {'name': 'Testproject', 'prefix': 'TP'}
        self._api.createTestProject(**defaults)
        query.assert_called_with('tl.createTestProject',
                                 notes='',
                                 active=True,
                                 public=True,
                                 options={'requirementsEnabled': False,
                                          'testPriorityEnabled': False,
                                          'automationEnabled': False,
                                          'inventoryEnabled': False},
                                 devKey=None,
                                 **defaults)
        # Check with specified params
        options = {'requirements': True, 'priority': False, 'automation': True, 'inventory': False}
        non_defaults = {'name': 'Testproject', 'prefix': 'TP', 'notes': 'Some notes\nhere', 'active': False, 'public': True}
        non_defaults.update(options)
        self._api.createTestProject(**non_defaults)
        query.assert_called_with('tl.createTestProject',
                                 devKey=None,
                                 options={'requirementsEnabled': options['requirements'],
                                          'testPriorityEnabled': options['priority'],
                                          'automationEnabled': options['automation'],
                                          'inventoryEnabled': options['inventory']},
                                 name=non_defaults['name'],
                                 prefix=non_defaults['prefix'],
                                 notes=non_defaults['notes'],
                                 active=non_defaults['active'],
                                 public=non_defaults['public'])
        self._api._tl_version = Version("0.9")
        self.assertRaises(NotSupported, self._api.createTestProject)

    @mock.patch("testlink.api.TestlinkXMLRPCAPI._query")
    def test_get_projects(self, query):
        """'getProjects' (1.0)"""
        self._api.getProjects()
        query.assert_called_with('tl.getProjects', devKey=None)
        self._api._tl_version = Version("0.9")
        self.assertRaises(NotSupported, self._api.getProjects)

    @mock.patch("testlink.api.TestlinkXMLRPCAPI._query")
    def test_get_testproject_by_name(self, query):
        """'getTestProjectByName' (1.0)"""
        test_data = "Testproject"
        self._api.getTestProjectByName(test_data)
        query.assert_called_with('tl.getTestProjectByName', testprojectname=test_data, devKey=None)
        self._api._tl_version = Version("0.9")
        self.assertRaises(NotSupported, self._api.getTestProjectByName)

    @mock.patch("testlink.api.TestlinkXMLRPCAPI._query")
    def test_create_testplan(self, query):
        """'createTestPlan' (1.0)"""
        # Check default params
        defaults = {'name': 'Testplan', 'project': object()}
        self.assertEquals(self._api.createTestPlan(**defaults), query.return_value)
        query.assert_called_with('tl.createTestPlan',
                                 notes='',
                                 active=True,
                                 public=True,
                                 devKey=None,
                                 testplanname=defaults['name'],
                                 testprojectname=defaults['project'])
        # Check with specified params
        non_defaults = {'name': "Testplan", 'project': object(), 'notes': "Some\nnotes", 'active': False, 'public': True}
        self.assertEquals(self._api.createTestPlan(**non_defaults), query.return_value)
        query.assert_called_with('tl.createTestPlan',
                                 devKey=None,
                                 active=non_defaults['active'],
                                 public=non_defaults['public'],
                                 notes=non_defaults['notes'],
                                 testplanname=non_defaults['name'],
                                 testprojectname=non_defaults['project'])
        self._api._tl_version = Version("0.9")
        self.assertRaises(NotSupported, self._api.createTestPlan)

    @mock.patch("testlink.api.TestlinkXMLRPCAPI._query")
    def test_get_test_plan_by_name(self, query):
        """'getTestPlanByName' (1.0)"""
        test_data = {'name': "Testplan", 'projectname': "Testproject"}
        self._api.getTestPlanByName(**test_data)
        query.assert_called_with('tl.getTestPlanByName',
                                 testplanname=test_data['name'],
                                 testprojectname=test_data['projectname'],
                                 devKey=None)
        self._api._tl_version = Version("0.9")
        self.assertRaises(NotSupported, self._api.getTestPlanByName)

    @mock.patch("testlink.api.TestlinkXMLRPCAPI._query")
    def test_get_project_testplans(self, query):
        """'getProjectTestPlans' (1.0)"""
        test_data = 12345
        self._api.getProjectTestPlans(test_data)
        query.assert_called_with('tl.getProjectTestPlans', testprojectid=test_data, devKey=None)
        self._api._tl_version = Version("0.9")
        self.assertRaises(NotSupported, self._api.getProjectTestPlans)

    @mock.patch("testlink.api.TestlinkXMLRPCAPI._query")
    def test_get_testplan_cf_value(self, query):
        """'getTestPlanCustomFieldValue' (1.9.4)"""
        test_data = {'testplanid': 12345, 'testprojectid': 23456, 'fieldname': "someField"}
        self.assertRaises(NotSupported, self._api.getTestPlanCustomFieldValue)
        self._api._tl_version = Version("1.9.4")
        self._api.getTestPlanCustomFieldValue(**test_data)
        query.assert_called_with('tl.getTestPlanCustomFieldValue',
                                 devKey=None,
                                 customfieldname=test_data['fieldname'],
                                 testprojectid=test_data['testprojectid'],
                                 testplanid=test_data['testplanid'])

    @mock.patch("testlink.api.TestlinkXMLRPCAPI._query")
    def test_create_build(self, query):
        """'createBuild' (1.0)"""
        # Check default params
        defaults = {'testplanid': 12345, 'name': "Build"}
        self._api.createBuild(**defaults)
        query.assert_called_with('tl.createBuild',
                                 devKey=None,
                                 buildnotes='',
                                 buildname=defaults['name'],
                                 testplanid=defaults['testplanid'])
        # Check with specified params
        non_defaults = {'testplanid': 123456, 'name': "Build", 'notes': "Some\nnotes"}
        self._api.createBuild(**non_defaults)
        query.assert_called_with('tl.createBuild',
                                 devKey=None,
                                 buildnotes=non_defaults['notes'],
                                 buildname=non_defaults['name'],
                                 testplanid=non_defaults['testplanid'])
        self._api._tl_version = Version("0.9")
        self.assertRaises(NotSupported, self._api.createBuild)

    @mock.patch("testlink.api.TestlinkXMLRPCAPI._query")
    def test_latest_build_for_plan(self, query):
        """'getLatestBuildForTestPlan' (1.0)"""
        test_data = 123456
        self._api.getLatestBuildForTestPlan(test_data)
        query.assert_called_with('tl.getLatestBuildForTestPlan', devKey=None, testplanid=test_data)
        self._api._tl_version = Version("0.9")
        self.assertRaises(NotSupported, self._api.getLatestBuildForTestPlan)

    @mock.patch("testlink.api.TestlinkXMLRPCAPI._query")
    def test_get_builds_for_testplan(self, query):
        """'getBuildsForTestPlan' (1.0)"""
        test_data = 123456
        self._api.getBuildsForTestPlan(test_data)
        query.assert_called_with('tl.getBuildsForTestPlan', devKey=None, testplanid=test_data)
        self._api._tl_version = Version("0.9")
        self.assertRaises(NotSupported, self._api.getBuildsForTestPlan)

    @mock.patch("testlink.api.TestlinkXMLRPCAPI._query")
    def test_get_exec_counters_by_build(self, query):
        """'getExecCountersByBuild' (1.9.4)"""
        test_data = 12345
        self.assertRaises(NotSupported, self._api.getExecCountersByBuild)
        self._api._tl_version = Version("1.9.4")
        self._api.getExecCountersByBuild(test_data)
        query.assert_called_with('tl.getExecCountersByBuild', devKey=None, testplanid=test_data)

    @mock.patch("testlink.api.TestlinkXMLRPCAPI._query")
    def test_create_platform(self, query):
        """'createPlatform' (1.9.6)"""
        # Check default params
        defaults = {'testprojectname': "Testproject", 'platformname': "Platform"}
        self.assertRaises(NotSupported, self._api.createPlatform)
        self._api._tl_version = Version("1.9.6")
        self._api.createPlatform(**defaults)
        query.assert_called_with('tl.createPlatform', devKey=None, notes='', **defaults)
        # Check with specified parameters
        non_defaults = {'testprojectname': "Testproject", 'platformname': "Platformname", 'notes': "Some\nnotes"}
        self._api.createPlatform(**non_defaults)
        query.assert_called_with('tl.createPlatform', devKey=None, **non_defaults)

    @mock.patch("testlink.api.TestlinkXMLRPCAPI._query")
    def test_get_project_platforms(self, query):
        """'getProjectPlatforms' (1.9.6)"""
        test_data = 123456
        self.assertRaises(NotSupported, self._api.getProjectPlatforms)
        self._api._tl_version = Version("1.9.6")
        self._api.getProjectPlatforms(test_data)
        query.assert_called_with('tl.getProjectPlatforms', devKey=None, testprojectid=test_data)

    @mock.patch("testlink.api.TestlinkXMLRPCAPI._query")
    def test_get_testplan_platforms(self, query):
        """'getTestPlanPlatforms' (1.0)"""
        test_data = 123456
        self._api.getTestPlanPlatforms(test_data)
        query.assert_called_with('tl.getTestPlanPlatforms', devKey=None, testplanid=test_data)
        self._api._tl_version = Version("0.9")
        self.assertRaises(NotSupported, self._api.getTestPlanPlatforms)

    @mock.patch("testlink.api.TestlinkXMLRPCAPI._query")
    def test_report_tc_result(self, query):
        """'reportTCResult' (1.0)"""
        # Check default params
        defaults = {'testplanid': 123456, 'status': 'p'}
        self._api.reportTCResult(**defaults)
        query.assert_called_with('tl.reportTCResult',
                                 devKey=None,
                                 testcaseid=None,
                                 testcaseexternalid=None,
                                 buildid=None,
                                 buildname=None,
                                 notes=None,
                                 guess=True,
                                 bugid=None,
                                 platformid=None,
                                 platformname=None,
                                 customfields=None,
                                 overwrite=False,
                                 **defaults)
        # Check with specified parameters
        non_defaults = {'testplanid': 123456, 'status': 'p', 'testcaseid': 2345, 'testcaseexternalid': 4563, 'buildid': 12354,
                        'buildname': "Build", 'notes': "Some\nnotes", 'guess': False, 'bugid': 1345, 'platformid': 23433,
                        'platformname': "Platform", 'customfields': {'field1': "Something"}, 'overwrite': True}
        self._api.reportTCResult(**non_defaults)
        query.assert_called_with('tl.reportTCResult', devKey=None, **non_defaults)
        self._api._tl_version = Version("0.9")
        self.assertRaises(NotSupported, self._api.reportTCResult)
        # Check new arguments since 1.9.14
        self._api._tl_version = Version("1.9.14")
        self.assertEquals(self._api.reportTCResult(**defaults), query.return_value)
        query.assert_called_with('tl.reportTCResult',
                                 devKey=None,
                                 testcaseid=None,
                                 testcaseexternalid=None,
                                 buildid=None,
                                 buildname=None,
                                 notes=None,
                                 guess=True,
                                 bugid=None,
                                 platformid=None,
                                 platformname=None,
                                 customfields=None,
                                 overwrite=False,
                                 execduration=None,
                                 **defaults)
        non_defaults.update({'execduration': 0.45})
        self.assertEquals(self._api.reportTCResult(**non_defaults), query.return_value)
        query.assert_called_with('tl.reportTCResult', devKey=None, **non_defaults)

    @mock.patch("testlink.api.TestlinkXMLRPCAPI._query")
    def test_get_last_execution_result(self, query):
        """'getLastExecutionResult' (1.0)"""
        # Check default params
        defaults = {'testplanid' : 12345}
        self._api.getLastExecutionResult(**defaults)
        query.assert_called_with('tl.getLastExecutionResult',
                                 devKey=None,
                                 testcaseid=None,
                                 testcaseexternalid=None,
                                 **defaults)
        # Check with specified parameters
        non_defaults = {'testplanid': 123456, 'testcaseid': 34354, 'testcaseexternalid': 324354}
        self._api.getLastExecutionResult(**non_defaults)
        query.assert_called_with('tl.getLastExecutionResult', devKey=None, **non_defaults)
        self._api._tl_version = Version("0.9")
        self.assertRaises(NotSupported, self._api.getLastExecutionResult)
        # Check new arguments since version 1.9.9
        self._api._tl_version = Version("1.9.9")
        self.assertEquals(self._api.getLastExecutionResult(**defaults), query.return_value)
        query.assert_called_with('tl.getLastExecutionResult',
                                 devKey=None,
                                 testplanid=defaults['testplanid'],
                                 testcaseid=None,
                                 testcaseexternalid=None,
                                 platformid=None,
                                 platformname=None,
                                 buildid=None,
                                 buildname=None,
                                 options={'getBugs': False})
        non_defaults.update({'platformid': 12343, 'platformname': "Platform", 'buildid': 23343, 'buildname': "Build", 'bugs': True})
        self._api.getLastExecutionResult(**non_defaults)
        query.assert_called_with('tl.getLastExecutionResult',
                                 devKey=None,
                                 testplanid=non_defaults['testplanid'],
                                 testcaseid=non_defaults['testcaseid'],
                                 testcaseexternalid=non_defaults['testcaseexternalid'],
                                 platformid=non_defaults['platformid'],
                                 platformname=non_defaults['platformname'],
                                 buildid=non_defaults['buildid'],
                                 buildname=non_defaults['buildname'],
                                 options={'getBugs': non_defaults['bugs']})

    @mock.patch("testlink.api.TestlinkXMLRPCAPI._query")
    def test_delete_execution(self, query):
        """'deleteExecution' (1.0)"""
        test_data = 43543
        self._api.deleteExecution(test_data)
        query.assert_called_with('tl.deleteExecution', executionid=test_data, devKey=None)
        self._api._tl_version = Version("0.9")
        self.assertRaises(NotSupported, self._api.deleteExecution)

    @mock.patch("testlink.api.TestlinkXMLRPCAPI._query")
    def test_create_testsuite(self, query):
        """'createTestSuite' (1.0)"""
        # Check default params
        defaults = {'testsuitename': "Testsuite", 'testprojectid': 23243}
        self._api.createTestSuite(**defaults)
        query.assert_called_with('tl.createTestSuite',
                                 devKey=None,
                                 details=None,
                                 parentid=None,
                                 order=None,
                                 checkduplicatedname=True,
                                 actiononduplicatedname='block',
                                 **defaults)
        # Check with specified parameters
        non_defaults = {'testsuitename': "Testsuite", 'testprojectid': 23234, 'details': "Some\ndetails",
                        'parentid': 23434, 'order': 23, 'checkduplicatedname': True, 'actiononduplicatedname': 'block'}
        self.assertEquals(self._api.createTestSuite(**non_defaults), query.return_value)
        query.assert_called_with('tl.createTestSuite', devKey=None, **non_defaults)
        self._api._tl_version = Version("0.9")
        self.assertRaises(NotSupported, self._api.createTestSuite)

    @mock.patch("testlink.api.TestlinkXMLRPCAPI._query")
    def test_get_testsuite_by_id(self, query):
        """'getTestSuiteById' (1.0)"""
        test_data = {'testprojectid': 432434, 'testsuiteid': 432343}
        self._api.getTestSuiteById(**test_data)
        query.assert_called_with('tl.getTestSuiteByID', devKey=None, **test_data)
        self._api._tl_version = Version("0.9")
        self.assertRaises(NotSupported, self._api.getTestSuiteById)

    @mock.patch("testlink.api.TestlinkXMLRPCAPI._query")
    def test_get_suites_for_suite(self, query):
        """'getTestSuitesForTestSuite' (1.0)"""
        test_data = {'testsuiteid': 2343, 'testprojectid': 32344}
        self._api.getTestSuitesForTestSuite(**test_data)
        query.assert_called_with('tl.getTestSuitesForTestSuite', devKey=None, **test_data)
        self._api._tl_version = Version("0.9")
        self.assertRaises(NotSupported, self._api.getTestSuitesForTestSuite)

    @mock.patch("testlink.api.TestlinkXMLRPCAPI._query")
    def test_get_suites_for_project(self, query):
        """'getFirstLevelTestSuitesForTestProject' (1.0)"""
        test_data = 122323
        self._api.getFirstLevelTestSuitesForTestProject(test_data)
        query.assert_called_with('tl.getFirstLevelTestSuitesForTestProject', devKey=None, testprojectid=test_data)
        self._api._tl_version = Version("0.9")
        self.assertRaises(NotSupported, self._api.getFirstLevelTestSuitesForTestProject)

    @mock.patch("testlink.api.TestlinkXMLRPCAPI._query")
    def test_create_testcase(self, query):
        """'createTestCase' (1.0)"""
        # Check default params
        defaults = {'testcasename': "Testcase", 'testsuiteid': 23234, 'testprojectid': 43342, 'authorlogin': "user.name", 'summary': "Some\nSummary"}
        self._api.createTestCase(**defaults)
        query.assert_called_with('tl.createTestCase',
                                 devKey=None,
                                 steps=None,
                                 preconditions=None,
                                 importance=testlink.enums.IMPORTANCE_LEVEL.MEDIUM,
                                 executiontype=testlink.enums.EXECUTION_TYPE.MANUAL,
                                 order=None,
                                 customfields=None,
                                 checkduplicatedname=True,
                                 actiononduplicatedname='block',
                                 **defaults)
        # Check with specified parameters
        non_defaults = {'testcasename': "Testcase", 'testsuiteid': 2323, 'testprojectid': 23233, 'authorlogin': "user.name",
                        'summary': "Some\nSummary", 'steps': {'step_number': 1, 'actions': "Do\nsomething", 'results': "Expect something"},
                        'preconditions': "Some\nconditions", 'importance': 4, 'executiontype': 2, 'order': 23, 'checkduplicatedname': True,
                        'actiononduplicatedname': 'block', 'customfields': {'field1': "Something"}}
        self._api.createTestCase(**non_defaults)
        query.assert_called_with('tl.createTestCase', devKey=None, **non_defaults)
        self._api._tl_version = Version("0.9")
        self.assertRaises(NotSupported, self._api.createTestCase)

    @mock.patch("testlink.api.TestlinkXMLRPCAPI._query")
    def test_update_testcase(self, query):
        """'updateTestCase' (1.9.8)"""
        self.assertRaises(NotSupported, self._api.updateTestCase)
        self._api._tl_version = Version("1.9.8")
        # Check default params
        defaults = {'testcaseexternalid': 2343}
        self._api.updateTestCase(**defaults)
        query.assert_called_with('tl.updateTestCase',
                                 devKey=None,
                                 version=None,
                                 testcasename=None,
                                 summary=None,
                                 preconditions=None,
                                 steps=None,
                                 importance=None,
                                 executiontype=None,
                                 status=None,
                                 estimatedexecduration=None,
                                 user=None,
                                 **defaults)
        # Check with specified parameters
        non_defaults = {'testcaseexternalid': 2323, 'version': 2, 'testcasename': "TestCase", 'summary': "Some\nSummary",
                        'preconditions': "Some\nconditions", 'steps': {'number': 1, 'actions': "Some\nactions", 'results': "Some\nResults"},
                        'importance': 3, 'executiontype': 1, 'status': 3, 'estimatedexecduration': 32.4, 'user': "user.login"}
        self._api.updateTestCase(**non_defaults)
        query.assert_called_with('tl.updateTestCase', devKey=None, **non_defaults)

    @mock.patch("testlink.api.TestlinkXMLRPCAPI._query")
    def test_set_tc_execution_type(self, query):
        """'setTestCaseEXECUTION_TYPE' (1.9.4)"""
        test_data = {'testcaseexternalid': 23232, 'version': 23, 'testprojectid': 2323, 'executiontype': 1}
        self.assertRaises(NotSupported, self._api.updateTestCase)
        self._api._tl_version = Version("1.9.4")
        self._api.setTestCaseExecutionType(**test_data)
        query.assert_called_with('tl.setTestCaseExecutionType', devKey=None, **test_data)

    @mock.patch("testlink.api.TestlinkXMLRPCAPI._query")
    def test_create_testcase_steps(self, query):
        """'createTestCaseSteps' (1.9.4)"""
        self.assertRaises(NotSupported, self._api.createTestCaseSteps)
        self._api._tl_version = Version("1.9.4")
        # Check default params
        defaults = {'steps': {'number': 1}, 'action': "SPAM"}
        self._api.createTestCaseSteps(**defaults)
        query.assert_called_with('tl.createTestCaseSteps',
                                 devKey=None,
                                 testcaseexternalid=None,
                                 testcaseid=None,
                                 version=None,
                                 **defaults)
        # Check with specified parameters
        non_defaults = {'steps': {'number': 1}, 'action': "SPAM", 'testcaseexternalid': 1234, 'testcaseid': 34343, 'version': 23}
        self._api.createTestCaseSteps(**non_defaults)
        query.assert_called_with('tl.createTestCaseSteps', devKey=None, **non_defaults)

    @mock.patch("testlink.api.TestlinkXMLRPCAPI._query")
    def test_delete_testcase_steps(self, query):
        """'deleteTestCaseSteps' (1.9.4)"""
        self.assertRaises(NotSupported, self._api.deleteTestCaseSteps)
        self._api._tl_version = Version("1.9.4")
        # Check default params
        defaults = {'testcaseexternalid': 12232, 'steps': {'number': 2}}
        self._api.deleteTestCaseSteps(**defaults)
        query.assert_called_with('tl.deleteTestCaseSteps', devKey=None, version=None, **defaults)
        # Check with specified parameters
        non_defaults = {'testcaseexternalid': 123243, 'steps': {'number': 2}, 'version': 23}
        self._api.deleteTestCaseSteps(**non_defaults)
        query.assert_called_with('tl.deleteTestCaseSteps', devKey=None, **non_defaults)

    @mock.patch("testlink.api.TestlinkXMLRPCAPI._query")
    def test_get_testcase(self, query):
        """'getTestCase' (1.0)"""
        # Check default params
        self._api.getTestCase()
        query.assert_called_with('tl.getTestCase',
                                 devKey=None,
                                 testcaseid=None,
                                 testcaseexternalid=None,
                                 version=None)
        # Check with specified parameters
        non_defaults = {'testcaseid': 232, 'testcaseexternalid': 322, 'version': 23}
        self._api.getTestCase(**non_defaults)
        query.assert_called_with('tl.getTestCase', devKey=None, **non_defaults)
        self._api._tl_version = Version("0.9")
        self.assertRaises(NotSupported, self._api.getTestCase)

    @mock.patch("testlink.api.TestlinkXMLRPCAPI._query")
    def test_get_testcase_id_by_name(self, query):
        """'getTestCaseIdByName' (1.0)"""
        # Check default params
        defaults = {'testcasename': "Testcase"}
        self._api.getTestCaseIdByName(**defaults)
        query.assert_called_with('tl.getTestCaseIDByName',
                                 devKey=None,
                                 testsuitename=None,
                                 testprojectname=None,
                                 testcasepathname=None,
                                 **defaults)
        # Check with specified parameters
        non_defaults = {'testcasename': "Testcase", 'testsuitename': "Testsuite", 'testprojectname': "Tesproject", 'testcasepathname': "Path"}
        self._api.getTestCaseIdByName(**non_defaults)
        query.assert_called_with('tl.getTestCaseIDByName', devKey=None, **non_defaults)
        self._api._tl_version = Version("0.9")
        self.assertRaises(NotSupported, self._api.getTestCaseIdByName)

    @mock.patch("testlink.api.TestlinkXMLRPCAPI._query")
    def test_get_cases_for_suite(self, query):
        """'getTestCasesForTestSuite' (1.0/1.9.10)"""
        # Check default params
        defaults = {'testsuiteid': 4323}
        self._api.getTestCasesForTestSuite(**defaults)
        query.assert_called_with('tl.getTestCasesForTestSuite',
                                 devKey=None,
                                 deep=False,
                                 details='simple',
                                 **defaults)
        # Check with specified parameters
        non_defaults = {'testsuiteid': 2323434, 'deep': True, 'details': False}
        self._api.getTestCasesForTestSuite(**non_defaults)
        query.assert_called_with('tl.getTestCasesForTestSuite', devKey=None, **non_defaults)
        self._api._tl_version = Version("0.9")
        self.assertRaises(NotSupported, self._api.getTestCasesForTestSuite)
        # Check new argument 'getkeywords' since version 1.9.10
        self._api._tl_version = Version("1.9.10")
        self.assertEquals(self._api.getTestCasesForTestSuite(**defaults), query.return_value)
        query.assert_called_with('tl.getTestCasesForTestSuite',
                                 devKey=None,
                                 deep=False,
                                 details='simple',
                                 getkeywords=False,
                                 **defaults)
        non_defaults.update({'getkeywords': False})
        self.assertEquals(self._api.getTestCasesForTestSuite(**non_defaults), query.return_value)
        query.assert_called_with('tl.getTestCasesForTestSuite', devKey=None, **non_defaults)

    @mock.patch("testlink.api.TestlinkXMLRPCAPI._query")
    def test_get_testcases_for_testplan(self, query):
        """'getTesTCasesForTestPlan' (1.0 /1.9.4)"""
        # Check default params
        defaults = {'testprojectid': 12123, 'testplanid': 232}
        self._api.getTestCasesForTestPlan(**defaults)
        query.assert_called_with('tl.getTestCasesForTestPlan',
                                 devKey=None,
                                 testcaseid=None,
                                 buildid=None,
                                 keywordid=None,
                                 keywords=None,
                                 executed=None,
                                 assignedto=None,
                                 executestatus=None,
                                 executiontype=None,
                                 getstepsinfo=False,
                                 **defaults)
        # Check with specified parameters
        non_defaults = {'testprojectid': 233, 'testplanid': 432, 'testcaseid': 3231, 'buildid': 432, 'keywordid': 234323,
                        'keywords': ["Keyword1"], 'executed': False, 'assignedto': "user.login", 'executestatus': 'p', 'executiontype': 1, 'getstepsinfo': False}
        self._api.getTestCasesForTestPlan(**non_defaults)
        query.assert_called_with('tl.getTestCasesForTestPlan', devKey=None, **non_defaults)
        self._api._tl_version = Version("0.9")
        self.assertRaises(NotSupported, self._api.getTestCasesForTestPlan)
        # Check new argument 'details' since version 1.9.4
        self._api._tl_version = Version("1.9.4")
        self.assertEquals(self._api.getTestCasesForTestPlan(**defaults), query.return_value)
        query.assert_called_with('tl.getTestCasesForTestPlan',
                                 devKey=None,
                                 testcaseid=None,
                                 buildid=None,
                                 keywordid=None,
                                 keywords=None,
                                 executed=None,
                                 assignedto=None,
                                 executestatus=None,
                                 executiontype=None,
                                 getstepsinfo=False,
                                 details='full',
                                 **defaults)
        non_defaults.update({'details': False})
        self._api.getTestCasesForTestPlan(**non_defaults)
        query.assert_called_with('tl.getTestCasesForTestPlan', devKey=None, **non_defaults)

    @mock.patch("testlink.api.TestlinkXMLRPCAPI._query")
    def test_add_testcase_to_testplan(self, query):
        """'addTestCaseToTestPlan' (1.0)"""
        # Check default params
        defaults = {'testprojectid': 21233, 'testplanid': 3243, 'testcaseexternalid': 3213, 'version': 23}
        self._api.addTestCaseToTestPlan(**defaults)
        query.assert_called_with('tl.addTestCaseToTestPlan',
                                 devKey=None,
                                 platformid=None,
                                 executionorder=None,
                                 urgency=None,
                                 **defaults)
        # Check with specified parameters
        non_defaults = {'testprojectid': 232, 'testplanid': 433, 'testcaseexternalid': 23243, 'version': 23,
                        'platformid': 32, 'executionorder': 3, 'urgency': 2}
        self._api.addTestCaseToTestPlan(**non_defaults)
        query.assert_called_with('tl.addTestCaseToTestPlan', devKey=None, **non_defaults)
        self._api._tl_version = Version("0.9")
        self.assertRaises(NotSupported, self._api.addTestCaseToTestPlan)

    @mock.patch("testlink.api.TestlinkXMLRPCAPI._query")
    def test_add_platform_to_testplan(self, query):
        """'addPlatformToTestPlan' (1.9.6)"""
        test_data = {'testplanid': 323, 'platformname': "Platform"}
        self.assertRaises(NotSupported, self._api.addPlatformToTestPlan)
        self._api._tl_version = Version("1.9.6")
        self._api.addPlatformToTestPlan(**test_data)
        query.assert_called_with('tl.addPlatformToTestPlan', devKey=None, **test_data)

    @mock.patch("testlink.api.TestlinkXMLRPCAPI._query")
    def test_remove_platform_from_plan(self, query):
        """'removePlatformFromTestPlan' (1.9.6)"""
        test_data = {'testplanid': 13, 'platformname': "Platform"}
        self.assertRaises(NotSupported, self._api.removePlatformFromTestPlan)
        self._api._tl_version = Version("1.9.6")
        self._api.removePlatformFromTestPlan(**test_data)
        query.assert_called_with('tl.removePlatformFromTestPlan', devKey=None, **test_data)

    @mock.patch("testlink.api.TestlinkXMLRPCAPI._query")
    def test_assign_requirements(self, query):
        """'assignRequirements' (1.0)"""
        test_data = {'testcaseexternalid': 23, 'testprojectid': 232, 'requirements': {'req_id': 32, 'testcases': [323, 43]}}
        self._api.assignRequirements(**test_data)
        query.assert_called_with('tl.assignRequirements', devKey=None, **test_data)
        self._api._tl_version = Version("0.9")
        self.assertRaises(NotSupported, self._api.assignRequirements)

    @mock.patch("testlink.api.TestlinkXMLRPCAPI._query")
    def test_get_reqspec_cf_value(self, query):
        """'getReqSpecCustomFieldDesignValue' (1.9.4)"""
        test_data = {'reqspecid': 32, 'testprojectid': 232, 'customfieldname': "field"}
        self.assertRaises(NotSupported, self._api.getReqSpecCustomFieldDesignValue)
        self._api._tl_version = Version("1.9.4")
        self._api.getReqSpecCustomFieldDesignValue(**test_data)
        query.assert_called_with('tl.getReqSpecCustomFieldDesignValue', devKey=None, **test_data)

    @mock.patch("testlink.api.TestlinkXMLRPCAPI._query")
    def test_get_req_cf_value(self, query):
        """'getRequirementCustomFieldDesignValue' (1.9.4)"""
        test_data = {'requirementid': 32, 'testprojectid': 32, 'customfieldname': "field"}
        self.assertRaises(NotSupported, self._api.getRequirementCustomFieldDesignValue)
        self._api._tl_version = Version("1.9.4")
        self._api.getRequirementCustomFieldDesignValue(**test_data)
        query.assert_called_with('tl.getRequirementCustomFieldDesignValue', devKey=None, **test_data)

    @mock.patch("testlink.api.TestlinkXMLRPCAPI._query")
    def test_get_suite_cf_value(self, query):
        """'getTestSuiteCustomFieldDesignValue' (1.9.4)"""
        test_data = {'testsuiteid': 3234, 'testprojectid': 32, 'customfieldname': "Field"}
        self.assertRaises(NotSupported, self._api.getTestSuiteCustomFieldDesignValue)
        self._api._tl_version = Version("1.9.4")
        self._api.getTestSuiteCustomFieldDesignValue(**test_data)
        query.assert_called_with('tl.getTestSuiteCustomFieldDesignValue', devKey=None, **test_data)

    @mock.patch("testlink.api.TestlinkXMLRPCAPI._query")
    def test_get_case_cf_value(self, query):
        """'getTestCaseCustomFieldDesignValue' (1.0)"""
        # Check default params
        defaults = {'testcaseexternalid': 32, 'version': 23, 'testprojectid': 43, 'customfieldname': "Field"}
        self._api.getTestCaseCustomFieldDesignValue(**defaults)
        query.assert_called_with('tl.getTestCaseCustomFieldDesignValue', devKey=None, details='value', **defaults)
        # Check with specified parameters
        non_defaults = {'testcaseexternalid': 323, 'version': 323, 'testprojectid': 3232, 'customfieldname': "Field", 'details': True}
        self._api.getTestCaseCustomFieldDesignValue(**non_defaults)
        query.assert_called_with('tl.getTestCaseCustomFieldDesignValue', devKey=None, **non_defaults)
        self._api._tl_version = Version("0.9")
        self.assertRaises(NotSupported, self._api.getTestCaseCustomFieldDesignValue)

    @mock.patch("testlink.api.TestlinkXMLRPCAPI._query")
    def test_update_case_cf_value(self, query):
        """'updateTestCaseCustomFieldDesignValue' (1.9.4)"""
        test_data = {'testcaseexternalid': 232, 'version': 3, 'testprojectid': 32, 'customfields': {'field1': "SPAM"}}
        self.assertRaises(NotSupported, self._api.updateTestCaseCustomFieldDesignValue)
        self._api._tl_version = Version("1.9.4")
        self._api.updateTestCaseCustomFieldDesignValue(**test_data)
        query.assert_called_with('tl.updateTestCaseCustomFieldDesignValue', devKey=None, **test_data)

    @mock.patch("testlink.api.TestlinkXMLRPCAPI._query")
    def test_get_case_cf_exec_value(self, query):
        """'getTestCaseCustomFieldExecutionValue' (1.9.4)"""
        test_data = {'executionid': 3231, 'testplanid': 32, 'version': 5, 'testprojectid': 434, 'customfieldname': "Field"}
        self.assertRaises(NotSupported, self._api.getTestCaseCustomFieldExecutionValue)
        self._api._tl_version = Version("1.9.4")
        self._api.getTestCaseCustomFieldExecutionValue(**test_data)
        query.assert_called_with('tl.getTestCaseCustomFieldExecutionValue', devKey=None, **test_data)

    @mock.patch("testlink.api.TestlinkXMLRPCAPI._query")
    def test_get_case_cf_plan_value(self, query):
        """'getTestCaseCustomFieldTestPlanDesignValue' (1.9.4)"""
        test_data = {'linkid': 4323, 'testplanid': 45, 'version': 3, 'testprojectid': 2323, 'customfieldname': "Field"}
        self.assertRaises(NotSupported, self._api.getTestCaseCustomFieldTestPlanDesignValue)
        self._api._tl_version = Version("1.9.4")
        self._api.getTestCaseCustomFieldTestPlanDesignValue(**test_data)
        query.assert_called_with('tl.getTestCaseCustomFieldTestPlanDesignValue', devKey=None, **test_data)

    @mock.patch("testlink.api.TestlinkXMLRPCAPI._query")
    def test_upload_attachment(self, query):
        """'uploadAttachment' (1.0)"""
        # Check default params
        defaults = {'fkid': 3243, 'fktable': 'executtions', 'filename': "test.txt", 'filetype': 'text/plain', 'content': 'aaaaaaa'}
        self._api.uploadAttachment(**defaults)
        query.assert_called_with('tl.uploadAttachment', devKey=None, title=None, description=None, **defaults)
        # Check with specified parameters
        non_defaults = {'fkid': 323, 'fktable': 'executions', 'filename': "test.txt", 'filetype': 'text/plain',
                        'content': 'aaaaa', 'title': "TestFile", 'description': "A test file"}
        self._api.uploadAttachment(**non_defaults)
        query.assert_called_with('tl.uploadAttachment', devKey=None, **non_defaults)
        self._api._tl_version = Version("0.9")
        self.assertRaises(NotSupported, self._api.uploadAttachment)

    @mock.patch("testlink.api.TestlinkXMLRPCAPI._query")
    def test_upload_reqspec_attachment(self, query):
        """'uploadRequirementSpecificationAttachment' (1.0)"""
        # Check default params
        defaults = {'reqspecid': 43232, 'filename': "test.txt", 'filetype': 'text/plain', 'content': 'aaaa'}
        self._api.uploadRequirementSpecificationAttachment(**defaults)
        query.assert_called_with('tl.uploadRequirementSpecificationAttachment',
                                 devKey=None,
                                 title=None,
                                 description=None,
                                 **defaults)
        # Check with specified parameters
        non_defaults = {'reqspecid': 43432, 'filename': "test.txt", 'filetype': 'text/plain',
                        'content': 'aaaaaa', 'title': "TestFile", 'description': "A test file"}
        self._api.uploadRequirementSpecificationAttachment(**non_defaults)
        query.assert_called_with('tl.uploadRequirementSpecificationAttachment', devKey=None, **non_defaults)
        self._api._tl_version = Version("0.9")
        self.assertRaises(NotSupported, self._api.uploadRequirementSpecificationAttachment)

    @mock.patch("testlink.api.TestlinkXMLRPCAPI._query")
    def test_upload_req_attachment(self, query):
        """'uploadRequirementAttachment' (1.0)"""
        # Check default params
        defaults = {'requirementid': 3243, 'filename': "test.txt", 'filetype': 'text/plain', 'content': 'aaaaaa'}
        self._api.uploadRequirementAttachment(**defaults)
        query.assert_called_with('tl.uploadRequirementAttachment',
                                 devKey=None,
                                 title=None,
                                 description=None,
                                 **defaults)
        # Check with specified parameters
        non_defaults = {'requirementid': 323, 'filename': "test.txt", 'filetype': 'text/plain',
                        'content': 'aaaaa', 'title': "TestFile", 'description': "A test file"}
        self._api.uploadRequirementAttachment(**non_defaults)
        query.assert_called_with('tl.uploadRequirementAttachment', devKey=None, **non_defaults)
        self._api._tl_version = Version("0.9")
        self.assertRaises(NotSupported, self._api.uploadRequirementAttachment)

    @mock.patch("testlink.api.TestlinkXMLRPCAPI._query")
    def test_upload_project_attachment(self, query):
        """'uploadTestProjectAttachment' (1.0)"""
        # Check default params
        defaults = {'testprojectid': 23243, 'filename': "test.txt", 'filetype': 'text/plain', 'content': 'aaaa'}
        self._api.uploadTestProjectAttachment(**defaults)
        query.assert_called_with('tl.uploadTestProjectAttachment',
                                 devKey=None,
                                 title=None,
                                 description=None,
                                 **defaults)
        # Check with specified parameters
        non_defaults = {'testprojectid': 334323, 'filename': "test.txt", 'filetype': 'text/plain',
                        'content': 'aaaaa', 'title': "TestFile", 'description': "A test file"}
        self._api.uploadTestProjectAttachment(**non_defaults)
        query.assert_called_with('tl.uploadTestProjectAttachment', devKey=None, **non_defaults)
        self._api._tl_version = Version("0.9")
        self.assertRaises(NotSupported, self._api.uploadTestProjectAttachment)

    @mock.patch("testlink.api.TestlinkXMLRPCAPI._query")
    def test_upload_suite_attachment(self, query):
        """'uploadTestSuiteAttachment' (1.0)"""
        # Check default params
        defaults = {'testsuiteid': 43, 'filename': "test.txt", 'filetype': 'text/plain', 'content': 'aaaaaa'}
        self._api.uploadTestSuiteAttachment(**defaults)
        query.assert_called_with('tl.uploadTestSuiteAttachment',
                                 devKey=None,
                                 title=None,
                                 description=None,
                                 **defaults)
        # Check with specified parameters
        non_defaults = {'testsuiteid': 443, 'filename': "test.txt", 'filetype': 'text/plain',
                       'content': 'aaaaa', 'title': "TestFile", 'description': "A test file"}
        self._api.uploadTestSuiteAttachment(**non_defaults)
        query.assert_called_with('tl.uploadTestSuiteAttachment', devKey=None, **non_defaults)
        self._api._tl_version = Version("0.9")
        self.assertRaises(NotSupported, self._api.uploadTestSuiteAttachment)

    @mock.patch("testlink.api.TestlinkXMLRPCAPI._query")
    def test_upload_case_attachment(self, query):
        """'uploadTestCaseAttachment' (1.0)"""
        # Check default params
        defaults = {'testcaseid': 434, 'filename': "test.txt", 'filetype': 'text/plain', 'content': 'aaaa'}
        self._api.uploadTestCaseAttachment(**defaults)
        query.assert_called_with('tl.uploadTestCaseAttachment', devKey=None, title=None, description=None, **defaults)
        # Check with specified parameters
        non_defaults = {'testcaseid': 4343, 'filename': "test.txt", 'filetype': 'text/plain',
                        'content': 'aaaaa', 'title': "TestFile", 'description': "A test file"}
        self._api.uploadTestCaseAttachment(**non_defaults)
        query.assert_called_with('tl.uploadTestCaseAttachment', devKey=None, **non_defaults)
        self._api._tl_version = Version("0.9")
        self.assertRaises(NotSupported, self._api.uploadTestCaseAttachment)

    @mock.patch("testlink.api.TestlinkXMLRPCAPI._query")
    def test_upload_exec_attachment(self, query):
        """'uploadExecutionAttachment' (1.0)"""
        # Check default params
        defaults = {'executionid': 34343, 'filename': "test.txt", 'filetype': 'text/plain', 'content': 'aaaaaa'}
        self._api.uploadExecutionAttachment(**defaults)
        query.assert_called_with('tl.uploadExecutionAttachment', devKey=None, title=None, description=None, **defaults)
        # Check with specified parameters
        non_defaults = {'executionid': 43432, 'filename': "test.txt", 'filetype': 'text/plain',
                        'content': 'aaaaaa', 'title': "TestFile", 'description': "A test file"}
        self._api.uploadExecutionAttachment(**non_defaults)
        query.assert_called_with('tl.uploadExecutionAttachment', devKey=None, **non_defaults)
        self._api._tl_version = Version("0.9")
        self.assertRaises(NotSupported, self._api.uploadExecutionAttachment)

    @mock.patch("testlink.api.TestlinkXMLRPCAPI._query")
    def test_get_testcase_attachments(self, query):
        """'getTestCaseAttachments' (1.0)"""
        # Check default params
        self._api.getTestCaseAttachments()
        query.assert_called_with('tl.getTestCaseAttachments', devKey=None, testcaseid=None, testcaseexternalid=None)
        # Check with specified parameters
        non_defaults = {'testcaseid': 4234, 'testcaseexternalid': 3432}
        self._api.getTestCaseAttachments(**non_defaults)
        query.assert_called_with('tl.getTestCaseAttachments', devKey=None, **non_defaults)
        self._api._tl_version = Version("0.9")
        self.assertRaises(NotSupported, self._api.getTestCaseAttachments)
