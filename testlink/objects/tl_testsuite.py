#!/usr/bin/env python
# pylint: disable=line-too-long
# pylint: disable=invalid-name
# pylint: disable=too-many-arguments
# pylint: disable=too-many-branches
# pylint: disable=star-args
# -*- coding: utf-8 -*-

"""TestSuite Object"""

# IMPORTS
from testlink.objects.tl_object import TestlinkObject
from testlink.objects.tl_object import normalize_list

from testlink.objects.tl_testcase import TestCase

from testlink.exceptions import APIError

class TestSuite(TestlinkObject):
    """Testlink TestSuite representation
    @ivar notes: TestSuite notes
    @type notes: str
    """

    __slots__ = ("details", "_parent_testproject", "_parent_testsuite")

    def __init__(self, name="", details="", parent_testproject=None, parent_testsuite=None, api=None, **kwargs):
        TestlinkObject.__init__(self, kwargs.get('id'), name, api)
        self.details = unicode(details)
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
                        if ae.error_code == 9000:
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

