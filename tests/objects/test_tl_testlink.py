#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@author: Kai Borowiak
@summary: TestSuite for testlink.objects.Testlink
"""

# IMPORTS
import random
import string
import unittest
import mock

from testlink.api.xmlrpc import TestlinkXMLRPCAPI
from testlink.enums import APIType
from testlink.exceptions import APIError
from testlink.objects.tl_testproject import TestProject
from testlink.objects.tl_testlink import Testlink


def randput(length=10): return "".join([random.choice(string.letters) for _ in xrange(random.randint(1, length))])


def randint(length=10): return int("".join([random.choice(string.digits) for _ in xrange(random.randint(1, length))]))


def randict(*keys): return dict((k, randput()) for k in keys)


def generate(*args):
    for a in args:
        yield a


class ServerMock(mock.Mock):
    """XML-RPC Server mock.Mock"""
    system = mock.Mock()
    system.listMethods = mock.Mock()

    def __init__(self, *args, **kwargs):
        super(ServerMock, self).__init__(*args, **kwargs)


class TestlinkTests(unittest.TestCase):
    """Testlink Object Tests"""

    def __init__(self, *args, **kwargs):
        super(TestlinkTests, self).__init__(*args, **kwargs)
        self._testMethodDoc = "Testlink: " + self._testMethodDoc
        self.devkey = randput(50)
        self.url = "http://example.de"

    def test_API_TYPE(self):
        """Default API Type"""
        tl = Testlink(self.url, self.devkey)
        self.assertTrue(isinstance(tl._api, TestlinkXMLRPCAPI))

    def test_devKeySetting(self):
        """DevKey Storage"""
        tl = Testlink(self.url, self.devkey)
        self.assertEquals(tl._api.devkey, self.devkey)

    def test_getVersion(self):
        """Version String"""
        tl = Testlink(self.url, self.devkey)
        self.assertEquals(tl.getVersion(), "1.0")

    def test_str(self):
        """String representation"""
        ref = "Testlink: TestlinkXMLRPCAPI 1.0 @"
        tl = Testlink(self.url, self.devkey)
        self.assertTrue(ref in str(tl))

    @mock.patch('testlink.objects.tl_testlink.Testlink.iterTestProject')
    def test_getTestProject(self, patched_iter_testproject):
        """'getTestProject'"""
        # Generate some test data
        args = randput()
        kwargs = randict("foo", "bar")
        return_value = randput()

        # Init Testlink
        tl = Testlink(self.url, self.devkey)

        # Mock the eqivalent iterator
        patched_iter_testproject.return_value = generate(return_value)

        # Check for normalize call, because there would
        # be no single return value otherwise
        self.assertEquals(tl.getTestProject(name=args, **kwargs), return_value)

        # Check correct parameter forwarding
        patched_iter_testproject.assert_called_with(args, **kwargs)

    @mock.patch('testlink.api.xmlrpc.TestlinkXMLRPCAPI.getTestProjectByName')
    @mock.patch('testlink.api.xmlrpc.TestlinkXMLRPCAPI.getProjects')
    def test_iterTestProject_shortcut(self, patched_get_projects, patched_get_testproject_by_name):
        """'iterTestProject' - Shortcut"""
        # Generate some test data
        test_data = [randict("name", "notes"), randict("name", "notes"), randict("name", "notes")]

        # Init Testlink
        tl = Testlink(self.url, self.devkey)

        # Mock internal methods
        patched_get_projects.return_value = test_data
        patched_get_testproject_by_name.return_value = test_data[1]

        # Check calls and result with shortcut usage
        project = tl.iterTestProject(test_data[1]['name']).next()
        patched_get_testproject_by_name.assert_called_with(test_data[1]['name'])
        self.assertFalse(patched_get_projects.called)
        self.assertTrue(isinstance(project, TestProject))
        self.assertEqual(project.name, test_data[1]['name'])
        self.assertEqual(project.notes, test_data[1]['notes'])

    @mock.patch('testlink.api.xmlrpc.TestlinkXMLRPCAPI.getTestProjectByName')
    @mock.patch('testlink.api.xmlrpc.TestlinkXMLRPCAPI.getProjects')
    def test_iterTestProject_shortcut_no_result(self, patched_get_projects, patched_get_testproject_by_name):
        """'iterTestProject' - Shortcut Empty Result"""
        # Init Testlink
        tl = Testlink(self.url, self.devkey)

        # Mock internal methods
        patched_get_projects.return_value = ''
        patched_get_testproject_by_name.side_effect = APIError(7011, "Test Project (name: ) does not exist")

        # Check with no result
        project_iter = tl.iterTestProject(randput())
        self.assertRaises(StopIteration, project_iter.next)

    @mock.patch('testlink.api.xmlrpc.TestlinkXMLRPCAPI.getTestProjectByName')
    @mock.patch('testlink.api.xmlrpc.TestlinkXMLRPCAPI.getProjects')
    def test_iterTestProject(self, patched_get_projects, patched_get_testproject_by_name):
        """'iterTestProject'"""
        # Generate some test data
        test_data = [randict("name", "notes"), randict("name", "notes"), randict("name", "notes")]

        # Init Testlink
        tl = Testlink(self.url, self.devkey)

        # Check with no result
        project_iter = tl.iterTestProject()
        self.assertRaises(StopIteration, project_iter.next)

        # Mock internal methods
        patched_get_projects.return_value = test_data
        patched_get_testproject_by_name.return_value = test_data[1]

        project = tl.iterTestProject(**test_data[1]).next()
        patched_get_projects.assert_called_with()
        self.assertFalse(patched_get_testproject_by_name.called)
        self.assertTrue(isinstance(project, TestProject))
        self.assertEqual(project.name, test_data[1]['name'])
        self.assertEqual(project.notes, test_data[1]['notes'])

    @mock.patch('testlink.api.xmlrpc.TestlinkXMLRPCAPI.getTestProjectByName')
    @mock.patch('testlink.api.xmlrpc.TestlinkXMLRPCAPI.getProjects')
    def test_iterTestProject_no_result(self, patched_get_projects, patched_get_testproject_by_name):
        """'iterTestProject' - Empty Result"""
        # Init Testlink
        tl = Testlink(self.url, self.devkey)

        # Mock internal methods
        patched_get_projects.return_value = ''
        patched_get_testproject_by_name.side_effect = APIError(7011, "Test Project (name: ) does not exist")

        # Check with no result
        project_iter = tl.iterTestProject()
        self.assertRaises(StopIteration, project_iter.next)


class CompatTests(unittest.TestCase):
    """Compatibility Tests"""

    def __init__(self, *args, **kwargs):
        super(CompatTests, self).__init__(*args, **kwargs)
        self._testMethodDoc = "CompatTests: " + self._testMethodDoc

    def test_datetime_conversion(self):
        """Datetime Backwards compatability Python 2.5<"""
        from datetime import datetime
        from testlink.objects.tl_object import TestlinkObject
        from testlink.objects.tl_object import strptime
        date_string = "2000-12-23 12:34:45"
        datetime_obj = datetime.strptime(date_string, TestlinkObject.DATETIME_FORMAT)
        strptime_obj = strptime(date_string, TestlinkObject.DATETIME_FORMAT)
        self.assertEquals(datetime_obj, strptime_obj)
