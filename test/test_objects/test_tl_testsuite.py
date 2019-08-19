#!/usr/bin/env python

# IMPORTS
import unittest
from mock import MagicMock

from testlink.objects.tl_testsuite import TestSuiteFromAPIBuilder
from testlink.objects.tl_testsuite import TestSuite

class TestSuiteFromAPIBuilder_Tests(unittest.TestCase):

    def test_api_data(self):
        data = {'id': '123', 'name': "Example", 'details': "Description",
                'level': '4'}
        builder = TestSuiteFromAPIBuilder(**data)
        self.assertEqual(builder._id, 123)
        self.assertEqual(builder.name, "Example")
        self.assertEqual(builder.description, "Description")
        self.assertEqual(builder.level, 4)


class TestSuiteBuilder_Tests(unittest.TestCase):

    def test_with_id(self):
        builder = TestSuite.builder()
        self.assertEqual(builder, builder.with_id(123))
        self.assertEqual(builder._id, 123)

    def test_from_testlink(self):
        testlink = MagicMock()
        builder = TestSuite.builder()
        self.assertEqual(builder, builder.from_testlink(testlink))
        self.assertEqual(builder.testlink, testlink)

    def test_with_description(self):
        builder = TestSuite.builder()
        self.assertEqual(builder, builder.with_description("Description"))
        self.assertEqual(builder.description, "Description")

    def test_with_level(self):
        builder = TestSuite.builder()
        self.assertEqual(builder, builder.with_level(4))
        self.assertEqual(builder.level, 4)

    def test_from_testproject(self):
        testproject = MagicMock()
        builder = TestSuite.builder()
        self.assertEqual(builder, builder.from_testproject(testproject))
        self.assertEqual(builder.testproject, testproject)

    def test_from_testsuite(self):
        testsuite = MagicMock()
        builder = TestSuite.builder()
        self.assertEqual(builder, builder.from_testsuite(testsuite))
        self.assertEqual(builder.testsuite, testsuite)


class TestSuite_Tests(unittest.TestCase):

    def test_builder(self):
        testsuite = MagicMock()
        testproject = MagicMock()
        testlink = MagicMock()
        suite = TestSuite.builder()\
                .with_id(123)\
                .from_testlink(testlink)\
                .with_name("Example")\
                .with_description("Description")\
                .with_level(4)\
                .from_testproject(testproject)\
                .from_testsuite(testsuite)\
                .build()
        self.assertEqual(suite.id, 123)
        self.assertEqual(suite.name, "Example")
        self.assertEqual(suite.description, "Description")
        self.assertEqual(suite.level, 4)
        self.assertEqual(suite.testlink, testlink)
        self.assertEqual(suite.testproject, testproject)
        self.assertEqual(suite.testsuite, testsuite)
