#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""TestSuite Object"""

# IMPORTS
from testlink.objects.tl_object import TestlinkObjectFromAPIBuilder
from testlink.objects.tl_object import TestlinkObjectBuilder
from testlink.objects.tl_object import TestlinkObject
from testlink.objects.tl_object import normalize_list

from testlink.objects.tl_testcase import TestCase
from testlink.objects.tl_attachment import IAttachmentGetter

from testlink.exceptions import APIError


class TestSuiteFromAPIBuilder(TestlinkObjectFromAPIBuilder):
    """Testlink TestSuite Builder for raw Testlink API data

    :param str name: Name of the TestSuite
    :param str description: Description of the TestSuite
    :param int level: Level of the TestSuite
    :param TestProject testproject: Parent TestProject
    :param TestSuite testsuite: Parent testsuite

    .. todo::
        Remove *parent_testsuite* from API builder


    .. todo::
        Remove *parent_testproject* from API builder
    """

    def __init__(self, *args, **kwargs):
        super(TestSuiteFromAPIBuilder, self).__init__(*args, **kwargs)
        self.name = kwargs.get('name', None)
        self.description = kwargs.get('details', None)
        self.level = kwargs.get('level', None)
        self.testsuite = kwargs.get('parent_testsuite', None)
        self.testproject = kwargs.get('parent_testproject', None)

        # Fix types
        if self.level is not None:
            self.level = int(self.level)

    def build(self):
        """Generate a new TestSuite"""
        # Sanity checks
        assert self.name is not None, "No TestSuite name defined"
        assert self.testproject is not None, "No parent TestProject defined"

        return TestSuite(
            # TestSuite
            name=self.name,
            description=self.description,
            level=self.level,
            parent_testsuite=self.testsuite,
            parent_testproject=self.testproject,
            # TestlinkObject
            _id=self._id,
            parent_testlink=self.testlink
        )


class TestSuiteBuilder(TestlinkObjectBuilder,
                       TestSuiteFromAPIBuilder):
    """General TestSuite Builder"""

    def __init__(self, *args, **kwargs):
        super(TestSuiteBuilder, self).__init__(*args, **kwargs)

    def with_name(self, name):
        """Set the name of the TestSuite
        :type name: str"""
        self.name = name
        return self

    def with_description(self, description):
        """Set the description of the TestSuite
        :type description: str"""
        self.description = description
        return self

    def with_level(self, level):
        """Set the level of the TestSuite
        :type level: int"""
        self.level = level
        return self

    def from_testproject(self, testproject):
        """Set the parent TestProject of the TestSuite
        :type testproject: TestProject"""
        self.testproject = testproject
        return self

    def from_testsuite(self, testsuite):
        """Set the parent TestSuite of the current TestSuite
        :type testsuite: TestSuite"""
        self.testsuite = testsuite
        return self


class TestSuite(TestlinkObject, IAttachmentGetter):
    """Testlink TestSuite

    :param str name: Name of the TestSuite
    :param str description: Description of the TestSuite
    :param int level: Level of the TestSuite
    :param TestProject testproject: Parent TestProject
    :param TestSuite testsuite: Parent TestSuite
    """

    def __init__(self, *args, **kwargs):
        super(TestSuite, self).__init__(*args, **kwargs)
        self.__name = kwargs['name']
        self.__description = kwargs['description']
        self.__level = kwargs['level']
        self.__parent_testproject = kwargs['parent_testproject']
        self.__parent_testsuite = kwargs['parent_testsuite']

    def __str__(self):
        return "{}: {}".format(self.__class__.__name__, self.name)

    @staticmethod
    def builder():
        return TestSuiteBuilder()

    @property
    def name(self):
        return self.__name

    @property
    def description(self):
        return self.__description

    @property
    def level(self):
        return self.__level

    @property
    def testproject(self):
        return self.__parent_testproject

    @property
    def testsuite(self):
        return self.__parent_testsuite

    def iterTestProject(self):
        """Returns associated TestProject"""
        yield self._parent_testproject

    def getTestProject(self):
        """Returns associated TestProject"""
        return self._parent_testproject

    def iterTestSuite(self, name=None, recursive=True, **params):
        """Iterates over TestSuites speficied by parameters
        @param name: The name of the wanted TestSuite
        @type name: str
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
        response = self._api.getTestSuitesForTestSuite(self.id, self.getTestProject().id)

        # Normalize result
        if isinstance(response, str) and response.strip() == "":
            response = []
        elif isinstance(response, dict):
            # Check for nested dict
            if isinstance(response[response.keys()[0]], dict):
                response = [self._api.getTestSuiteById(self.getTestProject().id, suite_id)
                            for suite_id in response.keys()]
            else:
                response = [response]
        suites = [TestSuite(api=self._api, parent_testproject=self.getTestProject(),
                            parent_testsuite=self, _level=self._level+1, **suite)
                  for suite in response]

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
                            cf_val = self._api.getTestSuiteCustomFieldDesignValue(tsuite.id,
                                                                                  tsuite.getTestProject().id,
                                                                                  key)
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
        cases = [TestCase(api=self._api, parent_testproject=self.getTestProject(), parent_testsuite=self, **case)
                 for case in response]

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
                            cf_val = self._api.getTestCaseCustomFieldDesignValue(ext_id,
                                                                                 tcase.version,
                                                                                 tcase.getTestProject().id,
                                                                                 key)
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
