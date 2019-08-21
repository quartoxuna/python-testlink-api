#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""TestSuite Object"""

# IMPORTS
from testlink.objects.tl_object import TestlinkObjectFromAPIBuilder
from testlink.objects.tl_object import TestlinkObjectBuilder
from testlink.objects.tl_object import TestlinkObject
from testlink.objects.tl_object import normalize_list

from testlink.objects.tl_testcase import TestCase
from testlink.objects.tl_attachment import AttachmentMixin

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
            testlink_id=self.testlink_id,
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


class TestSuite(TestlinkObject, AttachmentMixin):
    """Testlink TestSuite

    :param str name: Name of the TestSuite
    :param str description: Description of the TestSuite
    :param int level: Level of the TestSuite
    :param TestProject testproject: Parent TestProject
    :param TestSuite testsuite: Parent TestSuite
    :param Iterator[TestSuite] testsuites: Child TestSuites
    """

    def __init__(self, *args, **kwargs):
        super(TestSuite, self).__init__(*args, **kwargs)
        self.__name = kwargs['name']
        self.__description = kwargs['description']
        self.__level = kwargs['level']
        self.__parent_testproject = kwargs['parent_testproject']
        self.__parent_testsuite = kwargs['parent_testsuite']

    def __str__(self):
        return "[{}] {}: {}".format(self.level, self.__class__.__name__, self.name)

    def __repr__(self):
        return str(self)

    @staticmethod
    def builder(*args, **kwargs):
        return TestSuiteBuilder(*args, **kwargs)

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

    @property
    def testsuites(self):
        """Returns all TestSuites for the current TestSuite
        :rtype: Iterator[TestSuite]"""
        # DFS - Deep-First Search
        # First, return all currently nested testsuites
        for data in self.testlink.api.getTestSuitesForTestSuite(self.id, self.testproject.id):
            testsuite = TestSuite.builder(**data)\
                        .from_testlink(self.testlink)\
                        .from_testproject(self.testproject)\
                        .from_testsuite(self)\
                        .build()
            yield testsuite

            # Then, return all nested testsuites
            # for that particular testsuite
            for nested in testsuite.testsuites:
                yield nested

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
