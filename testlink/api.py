# -*- coding: utf-8 -*-
# pylint: disable=N802

"""
Testlink XML-RPC API
====================

API Wrapper for Testlink XML-RPC/REST API.

.. decorator:: TLVersion(version[, strict=False])

  Function decorator for Testlink version requirements

  :param version: Version to be checked
  :type version: str
  :param strict: Strict check
  :type strict: bool

  :Examples:

      >>> # Default function
      >>> @TLVersion("1.0")
      >>> def function1():
      >>>     pass

      >>> # Function available in Testlink 1.9.11 and higher
      >>> @TLVersion("1.9.11")
      >>> def function2():
      >>>     pass

      >>> # Function ONLY avaialble in Testlink 1.9.11-alpha
      >>> @TLVersion("1.9.11-alpha", strict=1)
      >>> def function3():
      >>>     pass
"""

# IMPORTS
import socket
import xmlrpclib
import time
import functools

from testlink.log import LOGGER

from testlink.enums import IMPORTANCE_LEVEL
from testlink.enums import EXECUTION_TYPE
from testlink.enums import DUPLICATE_STRATEGY

from testlink.exceptions import NotSupported
from testlink.exceptions import APIError
from testlink.exceptions import ConnectionError

from pkg_resources import parse_version as Version
from urlparse import urlparse

class TLVersion(object):
    """Testlink Version Checker decorator"""

    def __init__(self, version, strict=False):
        self.version = Version(version)
        self.strict = strict

    def __call__(self, fn):
        @functools.wraps(fn)
        def wrapper(testlink_api, *args, **kwargs):
            if not TestlinkXMLRPCAPI.IGNORE_VERSION_CHECK and (
                (self.strict and self.version != testlink_api.tl_version) or
                (self.version > testlink_api.tl_version)
            ):
                if self.strict:
                    sign = "=="
                else:
                    sign = ">="
                raise NotSupported("Method '%s' requires Testlink version %s %s but is %s" %
                    (str(fn.__name__), sign, str(self.version), str(testlink_api.tl_version)))
            return fn(testlink_api, *args, **kwargs)
        return wrapper


class ThreadSafeTransport(xmlrpclib.Transport):
    def make_connection(self, host):
        # Disable connection caching in Python >= 2.7
        self._connection = None
        return xmlrpclib.Transport.make_connection(self, host)


class TestlinkXMLRPCAPI(object):
    """Proxy class for Testlink's XML-RPC API.

    This class handles the initial connection to Testlink, the sending of queries to the server and handling the responses send from it.

    .. data:: RPC_PATHS

       RPC endpoints to check when a connection is established

    .. data:: WAIT_BEFORE_RECONNECT

       Timeout in seconds to wait before trying a reconnect

    .. data:: MAX_RECONNECTION_ATTEMPTS

       Maximal amount of reconnection tries in case of connection loss.

    .. data:: IGNORE_VERSION_CHECK

       Ignore version checks

    .. attribute:: devkey

       The Testlink Developer Key to be used

    .. attribute:: tl_version

       The Version of the currently connected Testlink
    """

    RPC_PATHS = ["/lib/api/xmlrpc.php", "/lib/api/xmlrpc/v1/xmlrpc.php"]  # RPC endpoints
    WAIT_BEFORE_RECONNECT = 5   # Time (seconds) to wait before reconnect
    MAX_RECONNECTION_ATTEMPTS = 5  # Max amout of reconnection attempts
    IGNORE_VERSION_CHECK = False # Ignores version checking via TLVersion decorator

    def __init__(self, url):
        """Initialize the TestlinkAPI
        @param url: Testlink URL
        @type url: str
        @raises ConnectionError: The given URL is not valid
        """
        self._proxy = None
        self._devkey = None
        self._tl_version = Version("1.0")
        self._rpc_path_cache = None

        # Patch URL
        if url.endswith('/'):
            url = url[:-1]

        # Check if URL is correct and save it for further use
        url_components = urlparse(url)
        # Must have scheme and net location
        if len(url_components[0].strip()) == 0 or len(url_components[1].strip()) == 0:
            raise ConnectionError("Invalid URI (%s)" % str(url))
        else:
            self._url = url

        # Establish connection
        self._reconnect()

        try:
            # Get the version
            # Wihtout wrapping function to avoid version check
            # before acutally having the version
            if hasattr(self._proxy, 'tl.testLinkVersion'):
                self._tl_version = Version(self._proxy.tl.testLinkVersion())
        except NotSupported:
            # Testlink API has version 1.0
            return
        except AttributeError:
            # Mocked _query during tests
            return

    @property
    def devkey(self):
        return self._devkey

    @devkey.setter
    def devkey(self, value):
        if self._devkey is None:
            self._devkey = value
        else:
            raise AttributeError("Cannot overwrite current Developer Key!")

    @property
    def tl_version(self):
        return self._tl_version

    def _reconnect(self):
        """Reconnects to initially specified URL"""
        if self._proxy is not None:
            LOGGER.debug("Reconnecting to '%s'" % str(self._url))

        # Get possinle RPC paths either
        # cached one or all available
        if not self._rpc_path_cache:
            possible_rpc_paths = TestlinkXMLRPCAPI.RPC_PATHS
        else:
            possible_rpc_paths = [self._rpc_path_cache]

        # Check for each possible RPC path,
        # if a connection can be made
        last_excpt = None
        for i in range(self.MAX_RECONNECTION_ATTEMPTS):
            for path in possible_rpc_paths:
                tmp = self._url
                try:
                    # Check if path is valid
                    if not tmp.endswith(path):
                        tmp += path

                    # Connect and test connection by retrieving remote methods
                    self._proxy = xmlrpclib.ServerProxy(tmp, encoding='UTF-8', allow_none=True,
                                                        transport=ThreadSafeTransport(use_datetime=False))
                    self._proxy.system.listMethods()

                    # Cache fitting RPC path for later reconnection attempts
                    self._rpc_path_cache = path

                    break
                except Exception, ex:
                    last_excpt = ex
                    self._proxy = None
                    continue
            if self._proxy is None:
                LOGGER.debug("Connection attempt %d failed: '%s'" % (i+1, str(last_excpt)))

                # Wait a moment before retry
                time.sleep(5)
            else:
                break

        if self._proxy is None:
            raise ConnectionError("Cannot connect to Testlink API @ %s (%s)" % (str(self._url), str(last_excpt)))

    def _query(self, method, _reconnect=True, **kwargs):
        """Remote calls a method on the server
        @param method: Method to call
        @type method: str
        @raise NotSupported: Called method is not supported by Testlink
        @raise APIError: Testlink API server side error
        """
        # Use class wide devkey if not given
        if not ('devKey' in kwargs and kwargs['devKey']) or kwargs['devKey'].strip() == "":
            kwargs['devKey'] = self._devkey

        # Check for empty method name
        if not method or method.strip() == "":
            raise NotSupported("Empty method name")

        LOGGER.debug("Query: %s(%s)" % (str(method), str(kwargs)))
        try:
            # Call the actual method
            fn = getattr(self._proxy, method)
            resp = fn(kwargs)
            LOGGER.debug(u"Response: %s" % unicode(resp))
        except xmlrpclib.Fault, f:
            # If method is not supported, raise NotSupported
            # Otherwise re-raise original error
            if f.faultCode == -32601:
                raise NotSupported(method)
            else:
                raise
        except (Exception, socket.error), ex:
            # Something was wrong with the request, try to reestablish
            LOGGER.debug("Connection Error: %s" + str(ex))
            if _reconnect:
                self._reconnect()
                return self._query(method, _reconnect=False, **kwargs)
            else:
                raise
        else:
            # Check for API error [{'code': 123, 'message': foo}]
            if isinstance(resp, list) and len(resp) == 1:
                tmp = resp[0]
                if ('code' in tmp) and ('message' in tmp):
                    raise APIError(tmp['code'], tmp['message'])
            return resp

    #
    # Raw API methods
    #
    @TLVersion("1.9.9")
    def testLinkVersion(self):
        """testLinkVersion()

        Returns Testlink Version String

        :Since: Testlink Version 1.9.9
        :rtype: str
        :return: Testlink Version String
        """
        return self._query("tl.testLinkVersion")

    @TLVersion("1.0")
    def about(self):
        """about()

        Returns informations about the current Testlink API

        :rtype: str
        :returns: 'Testlink Testlink Version: x.x initially written by ...'
        """
        return self._query("tl.about")

    @TLVersion("1.0")
    def sayHello(self):
        """sayHello()

        The 'Hello World' of the Testlink API.

        :rtype: str
        :returns: 'Hello!'
        """
        return self._query("tl.sayHello")
    ping = sayHello

    @TLVersion("1.0")
    def repeat(self, value):
        """repeat(value)

        Repeats the given value.

        :param str value: The value to be repeated by the server
        :rtype: str
        :returns: The value send to the server
        """
        return self._query("tl.repeat", str=str(value))

    @TLVersion("1.0")
    def checkDevKey(self, devkey=None):
        """checkDevKey([devkey])

        Checks if the specified developer key is valid.

        :param str devkey: The Testlink Developer Key to check. If no key is specified, the Developer Key of the current connection will be used.
        :rtype: bool
        :returns: Status of the specified Developer Key.
        """
        return self._query("tl.checkDevKey", devKey=devkey)

    @TLVersion("1.0")
    def doesUserExist(self, user, devkey=None):
        """doesUserExist(user[, devkey])

        Checks, if a specified user exists.

        :param str user: The Login name of the User to check
        :param str devkey: The Testlink Developer Key. If no key is specified, the Developer Key of the current connection will be used.
        :rtype: bool
        :returns: Status of the specified User
        """
        return self._query("tl.doesUserExist", devKey=devkey, user=user)

    @TLVersion("1.9.8")
    def getUserByLogin(self, user, devkey=None):
        """getUserByLogin(user[, devkey])

        Returns user information for specified user.

        :Since: Testlink Version 1.9.8
        :param str user: The Login name of the User to check
        :param str devkey: The Testlink Developer Key. If no key is specified, the Developer Key of the current connection will be used.
        :rtype: dict
        :returns: User Information
        """
        return self._query("tl.getUserByLogin", devKey=devkey, user=user)

    @TLVersion("1.9.8")
    def getUserByID(self, userid, devkey=None):
        """getUserByID(userid[, devkey])

        Returns user information for specified user.

        :Since: Testlink Version 1.9.8
        :param int userid: The ID of the User to check
        :param str devkey: The Testlink Developer Key. If no key is specified, the Developer Key of the current connection will be used.
        :rtype: dict
        :returns: User Information
        """
        return self._query("tl.getUserByID", devKey=devkey, userid=userid)

    @TLVersion("1.0")
    def getFullPath(self, nodeid, devkey=None):
        """getFullPath(nodeid[, devkey])

        Returns the full path of an object.

        :param int nodeid: The ID of the Node
        :param str devkey: The Testlink Developer Key. If no key is specified, the Developer Key of the current connection will be used.
        :rtype: dict
        :returns: Hierarchical Path of the specified Node
        """
        return self._query("tl.getFullPath", devKey=devkey, nodeid=int(nodeid))

    @TLVersion("1.0")
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

        return self._query("tl.createTestProject",
                           devKey=devkey,
                           name=name,
                           prefix=prefix,
                           notes=notes,
                           active=active,
                           public=public,
                           options=opts)

    @TLVersion("1.0")
    def getProjects(self, devkey=None):
        """getProjects([devkey])

        Returns all available TestProjects.

        :param str devkey: The Testlink Developer Key. If no key is specified, the Developer Key of the current connection will be used.
        :rtype: list
        :returns: List of available TestProjects
        """
        return self._query("tl.getProjects", devKey=devkey)

    @TLVersion("1.0")
    def getTestProjectByName(self, name, devkey=None):
        """getTestProjectByName(name[, devkey])

        Returns a single TestProject specified by its name.

        :param str name: The name of the wanted TestProject
        :param str devkey: The Testlink Developer Key. If no key is specified, the Developer Key of the current connection will be used.
        :rtype: mixed
        :returns: TestProject dictionary if TestProject has been found, else None.
        """
        resp = self._query("tl.getTestProjectByName", devKey=devkey, testprojectname=name)
        # Return None for an empty string
        if resp is not None and len(resp) == 0:
            resp = None
        return resp

    @TLVersion("1.0")
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
        return self._query("tl.createTestPlan",
                           devKey=devkey,
                           testplanname=name,
                           testprojectname=project,
                           notes=notes,
                           active=active,
                           public=public)

    @TLVersion("1.0")
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
        return self._query("tl.getTestPlanByName", devKey=devkey, testplanname=name, testprojectname=projectname)

    @TLVersion("1.0")
    def getProjectTestPlans(self, projectid, devkey=None):
        """getProjectTestPlans(projectid[, devkey])

        Returns all TestPlans for a specified TestProject.

        :param int projectid: The internal ID of the parent TestProject
        :param str devkey: The Testlink Developer Key. If no key is specified, the Developer Key of the current connection will be used.
        :rtype: list
        :returns: Server response

        .. todo:: Update Return Value
        """
        return self._query("tl.getProjectTestPlans", devKey=devkey, testprojectid=projectid)

    @TLVersion("1.9.4")
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
        return self._query("tl.getTestPlanCustomFieldValue",
                           devKey=devkey,
                           customfieldname=fieldname,
                           testprojectid=testprojectid,
                           testplanid=testplanid)

    @TLVersion("1.0")
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
        return self._query("tl.createBuild",
                           devKey=devkey,
                           testplanid=testplanid,
                           buildname=name,
                           buildnotes=notes)

    @TLVersion("1.0")
    def getLatestBuildForTestPlan(self, testplanid, devkey=None):
        """getLatestBuildForTestPlan(testplanid[, devkey])

        Returns the latest Build for the specified TestPlan.

        :param int testplanid: The internal ID of the TestPlan
        :param str devkey: The Testlink Developer Key. If no key is specified, the Developer Key of the current connection will be used.
        :rtype: mixed
        :returns: Server Response

        .. todo:: Update Return Value
        """
        return self._query("tl.getLatestBuildForTestPlan", devKey=devkey, testplanid=testplanid)

    @TLVersion("1.0")
    def getBuildsForTestPlan(self, testplanid, devkey=None):
        """getBuildsForTestPlan(testplanid[, devkey])

        Returns all Builds for the specified TestPlan.

        :parem int testplanid: The internal ID of the TestPlan
        :param str devkey: The Testlink Developer Key. If no key is specified, the Developer Key of the current connection will be used.
        :rtype: list
        :returns: Server Response

        .. todo:: Update Return Value
        """
        return self._query("tl.getBuildsForTestPlan", devKey=devkey, testplanid=testplanid)

    @TLVersion("1.9.4")
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
        return self._query("tl.getExecCountersByBuild", devKey=devkey, testplanid=testplanid)

    @TLVersion("1.9.6")
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
        return self._query("tl.createPlatform",
                           devKey=devkey,
                           testprojectname=testprojectname,
                           platformname=platformname,
                           notes=notes)

    @TLVersion("1.9.6")
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
        return self._query("tl.getProjectPlatforms", devKey=devkey, testprojectid=testprojectid)

    @TLVersion("1.0")
    def getTestPlanPlatforms(self, testplanid, devkey=None):
        """getTestPlanPlatforms(testplanid[, devkey])

        Returns all Platforms fot the specified TestPlan.

        :param int testplanid: The internal ID of the TestPlan
        :param str devkey: The Testlink Developer Key. If no key is specified, the Developer Key of the current connection will be used.
        :rtype: list
        :returns: Server Response

        .. todo:: Update Return Value
        """
        return self._query("tl.getTestPlanPlatforms", devKey=devkey, testplanid=testplanid)

    @TLVersion("1.0")
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

        return self._query("tl.reportTCResult",
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

    @TLVersion("1.0")
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

        return self._query("tl.getLastExecutionResult", **arguments)

    @TLVersion("1.0")
    def deleteExecution(self, executionid, devkey=None):
        """deleteExecution(externalid[, devkey])

        Deletes a specific exexution result.

        :param int executionid: The internal ID of the Execution
        :param str devkey: The Testlink Developer Key. If no key is specified, the Developer Key of the current connection will be used.
        :rtype: list
        :returns: Server Response

        .. todo:: Update Return Value
        """
        return self._query("tl.deleteExecution", devKey=devkey, executionid=executionid)

    @TLVersion("1.0")
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
        return self._query("tl.createTestSuite",
                           devKey=devkey,
                           testsuitename=testsuitename,
                           testprojectid=testprojectid,
                           details=details,
                           parentid=parentid,
                           order=order,
                           checkduplicatedname=checkduplicatedname,
                           actiononduplicatedname=actiononduplicatedname)

    @TLVersion("1.0")
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
        return self._query("tl.getTestSuiteByID", devKey=devkey, testprojectid=testprojectid, testsuiteid=testsuiteid)

    @TLVersion("1.0")
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
        return self._query("tl.getTestSuitesForTestSuite", devKey=devkey, testsuiteid=testsuiteid, testprojectid=testprojectid)

    @TLVersion("1.0")
    def getFirstLevelTestSuitesForTestProject(self, testprojectid, devkey=None):
        """getFirstLevelTestSuitesForTestProject(testprojecid[, devkey])

        Returns the first level TestSuites for a specified TestProject.

        :param int testprojectid: The internal ID of the parent TestProject.
        :param str devkey: The Testlink Developer Key. If no key is specified, the Developer Key of the current connection will be used.
        :rtype: list
        :returns: Server Response

        .. todo:: Update Return Value
        """
        return self._query("tl.getFirstLevelTestSuitesForTestProject", devKey=devkey, testprojectid=testprojectid)

    @TLVersion("1.0")
    def getTestSuitesForTestPlan(self, planid, devkey=None):
        """getTestSuitesForTestPlan(planid[, devkey])

        Returns all TestSuites for a specified TestPlan.

        :param int planid: The internal ID of the TestPlan
        :param str devkey: The Testlink Developer Key. If no key is specified, the Developer Key of the current connection will be used.
        :rtype: list
        :returns: Server Response

        .. todo:: Update Return Value
        """
        return self._query("tl.getTestSuitesForTestPlan", devKey=devkey, testplanid=planid)

    @TLVersion("1.0")
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
        return self._query("tl.createTestCase",
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

    @TLVersion("1.9.8")
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
        return self._query("tl.updateTestCase",
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

    @TLVersion("1.9.4")
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
        return self._query("tl.setTestCaseExecutionType",
                           devKey=devkey,
                           testcaseexternalid=testcaseexternalid,
                           version=version,
                           testprojectid=testprojectid,
                           executiontype=executiontype)

    @TLVersion("1.9.4")
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
        return self._query("tl.createTestCaseSteps",
                           devKey=devkey,
                           testcaseexternalid=testcaseexternalid,
                           testcaseid=testcaseid,
                           version=version,
                           action=action,
                           steps=steps)

    @TLVersion("1.9.4")
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
        return self._query("tl.deleteTestCaseSteps",
                           devKey=devkey,
                           testcaseexternalid=testcaseexternalid,
                           steps=steps,
                           version=version)

    @TLVersion("1.0")
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
        return self._query("tl.getTestCase",
                           devKey=devkey,
                           testcaseid=testcaseid,
                           testcaseexternalid=testcaseexternalid,
                           version=version)

    @TLVersion("1.0")
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
        return self._query("tl.getTestCaseIDByName",
                           devKey=devkey,
                           testcasename=testcasename,
                           testsuitename=testsuitename,
                           testprojectname=testprojectname,
                           testcasepathname=testcasepathname)

    @TLVersion("1.0")
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
        return self._query("tl.getTestCasesForTestSuite", devKey=devkey, **arguments)

    @TLVersion("1.0")
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

        return self._query("tl.getTestCasesForTestPlan", **arguments)

    @TLVersion("1.0")
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
        return self._query("tl.addTestCaseToTestPlan",
                           devKey=devkey,
                           testprojectid=testprojectid,
                           testplanid=testplanid,
                           testcaseexternalid=testcaseexternalid,
                           version=version,
                           platformid=platformid,
                           executionorder=executionorder,
                           urgency=urgency)

    @TLVersion("1.9.6")
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
        return self._query("tl.addPlatformToTestPlan",
                           devKey=devkey,
                           testplanid=testplanid,
                           platformname=platformname)

    @TLVersion("1.9.6")
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
        return self._query("tl.removePlatformFromTestPlan",
                           devKey=devkey,
                           testplanid=testplanid,
                           platformname=platformname)

    @TLVersion("1.0")
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
        return self._query("tl.assignRequirements",
                           devKey=devkey,
                           testcaseexternalid=testcaseexternalid,
                           testprojectid=testprojectid,
                           requirements=requirements)

    @TLVersion("1.9.4")
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
        return self._query("tl.getReqSpecCustomFieldDesignValue",
                           devKey=devkey,
                           customfieldname=customfieldname,
                           testprojectid=testprojectid,
                           reqspecid=reqspecid)

    @TLVersion("1.9.4")
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
        return self._query("tl.getRequirementCustomFieldDesignValue",
                           devKey=devkey,
                           customfieldname=customfieldname,
                           testprojectid=testprojectid,
                           requirementid=requirementid)

    @TLVersion("1.9.4")
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
        return self._query("tl.getTestSuiteCustomFieldDesignValue",
                           devKey=devkey,
                           customfieldname=customfieldname,
                           testprojectid=testprojectid,
                           testsuiteid=testsuiteid)

    @TLVersion("1.0")
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
        resp = self._query("tl.getTestCaseCustomFieldDesignValue",
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

    @TLVersion("1.9.4")
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
        return self._query("tl.updateTestCaseCustomFieldDesignValue",
                           devKey=devkey,
                           testcaseexternalid=testcaseexternalid,
                           version=version,
                           testprojectid=testprojectid,
                           customfields=customfields)

    @TLVersion("1.9.4")
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
        return self._query("tl.getTestCaseCustomFieldExecutionValue",
                           devKey=devkey,
                           customfieldname=customfieldname,
                           testprojectid=testprojectid,
                           version=version,
                           executionid=executionid,
                           testplanid=testplanid)

    @TLVersion("1.9.4")
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
        return self._query("tl.getTestCaseCustomFieldTestPlanDesignValue",
                           devKey=devkey,
                           customfieldname=customfieldname,
                           testprojectid=testprojectid,
                           version=version,
                           testplanid=testplanid,
                           linkid=linkid)

    @TLVersion("1.0")
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
        return self._query("tl.uploadAttachment",
                           devKey=devkey,
                           fkid=fkid,
                           fktable=fktable,
                           filename=filename,
                           filetype=filetype,
                           content=content,
                           title=title,
                           description=description)

    @TLVersion("1.11.0-sinaqs")
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
        return self._query("tl.deleteAttachment", devKey=devkey, attachmentid=attachment_id)

    @TLVersion("1.0")
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
        return self._query("tl.uploadRequirementSpecificationAttachment",
                           devKey=devkey,
                           reqspecid=reqspecid,
                           filename=filename,
                           filetype=filetype,
                           content=content,
                           title=title,
                           description=description)

    @TLVersion("1.0")
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
        return self._query("tl.uploadRequirementAttachment",
                           devKey=devkey,
                           requirementid=requirementid,
                           filename=filename,
                           filetype=filetype,
                           content=content,
                           title=title,
                           description=description)

    @TLVersion("1.0")
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
        return self._query("tl.uploadTestProjectAttachment",
                           devKey=devkey,
                           testprojectid=testprojectid,
                           filename=filename,
                           filetype=filetype,
                           content=content,
                           title=title,
                           description=description)

    @TLVersion("1.0")
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
        return self._query("tl.uploadTestSuiteAttachment",
                           devKey=devkey,
                           testsuiteid=testsuiteid,
                           filename=filename,
                           filetype=filetype,
                           content=content,
                           title=title,
                           description=description)

    @TLVersion("1.0")
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
        return self._query("tl.uploadTestCaseAttachment",
                           devKey=devkey,
                           testcaseid=testcaseid,
                           filename=filename,
                           filetype=filetype,
                           content=content,
                           title=title,
                           description=description)

    @TLVersion("1.0")
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
        return self._query("tl.uploadExecutionAttachment",
                           devKey=devkey,
                           executionid=executionid,
                           filename=filename,
                           filetype=filetype,
                           content=content,
                           title=title,
                           description=description)

    @TLVersion("1.0")
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
        return self._query("tl.getTestCaseAttachments",
                           devKey=devkey,
                           testcaseid=testcaseid,
                           testcaseexternalid=testcaseexternalid)

    @TLVersion("1.11.0-sinaqs")
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
        return self._query("tl.getRequirementSpecificationsForTestProject",
                           devKey=devkey,
                           testprojectid=testprojectid)

    @TLVersion("1.11.0-sinaqs")
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
        return self._query("tl.getRequirementSpecificationsForRequirementSpecification",
                           devKey=devkey,
                           reqspecid=reqspecid)

    @TLVersion("1.11.0-sinaqs")
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
        return self._query("tl.getRequirementsForRequirementSpecification",
                           devKey=devkey,
                           reqspecid=reqspecid,
                           testprojectid=testprojectid)

    @TLVersion("1.11.0-sinaqs")
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
        return self._query("tl.getRisksForRequirement", devKey=devkey, requirementid=requirementid)

    @TLVersion("1.11.0-sinaqs")
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
        return self._query("tl.createRequirementSpecification",
                           devKey=devkey,
                           testprojectid=testprojectid,
                           parentid=parentid,
                           docid=docid,
                           title=title,
                           scope=scope,
                           userid=userid,
                           type=typ)

    @TLVersion("1.11.0-sinaqs")
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
        return self._query("tl.createRequirement",
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

    @TLVersion("1.11.0-sinaqs")
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
        return self._query("tl.createRisk",
                           devKey=devkey,
                           requirementid=requirementid,
                           docid=docid,
                           title=title,
                           scope=scope,
                           userid=userid,
                           coverage=coverage)

    @TLVersion("1.11.0-sinaqs")
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
        return self._query("tl.assignRisks",
                           devKey=devkey,
                           testprojectid=testprojectid,
                           testcaseexternalid=testcaseexternalid,
                           risks=risks)

    @TLVersion("1.11.0-sinaqs")
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
        return self._query("tl.getExecutions",
                           devKey=devkey,
                           testplanid=testplanid,
                           testcaseid=testcaseid,
                           testcaseexternalid=testcaseexternalid,
                           platformid=platformid,
                           platformname=platformname,
                           buildid=buildid,
                           buildname=buildname,
                           options={'getBugs': bugs})

    @TLVersion("1.11.0-sinaqs")
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
        return self._query("tl.getAttachments",
                           devKey=devkey,
                           fkid=fkid,
                           fktable=fktable)

    @TLVersion("1.11.0-sinaqs")
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
        return self._query('tl.getRequirementCoverage',
                           devKey=devkey,
                           requirementid=requirementid,
                           testplanid=testplanid,
                           platformid=platformid)
