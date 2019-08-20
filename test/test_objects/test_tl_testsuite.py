# pylint: disable=missing-docstring

# IMPORTS
import unittest
import mock

from testlink.objects.tl_testsuite import TestSuiteFromAPIBuilder
from testlink.objects.tl_testsuite import TestSuite

class TestSuiteFromAPIBuilderTests(unittest.TestCase):

    def test_api_data(self):
        """Test builder initialisation with raw API data"""
        data = {'id': '123', 'name': "Example",
                'details': "Description", 'level': '4'}
        builder = TestSuiteFromAPIBuilder(**data)
        self.assertEqual(builder.testlink_id, 123)
        self.assertEqual(builder.name, "Example")
        self.assertEqual(builder.description, "Description")
        self.assertEqual(builder.level, 4)


class TestSuiteBuilderTests(unittest.TestCase):

    def test_with_id(self):
        """Test setter for internal Testlink ID"""
        builder = TestSuite.builder()
        self.assertEqual(builder, builder.with_id(123))
        self.assertEqual(builder.testlink_id, 123)

    def test_from_testlink(self):
        """Test setter for parent Testlink instance"""
        testlink = mock.MagicMock()
        builder = TestSuite.builder()
        self.assertEqual(builder, builder.from_testlink(testlink))
        self.assertEqual(builder.testlink, testlink)

    def test_with_name(self):
        """Test setter for TestSuite name"""
        builder = TestSuite.builder()
        self.assertEqual(builder, builder.with_name("Example"))
        self.assertEqual(builder.name, "Example")

    def test_with_description(self):
        """Test setter for TestSuite description"""
        builder = TestSuite.builder()
        self.assertEqual(builder, builder.with_description("Description"))
        self.assertEqual(builder.description, "Description")

    def test_with_level(self):
        """Test setter for TestSuite hierarchy level"""
        builder = TestSuite.builder()
        self.assertEqual(builder, builder.with_level(4))
        self.assertEqual(builder.level, 4)

    def test_from_testproject(self):
        """Test setter for TestSuite parent TestProject"""
        testproject = mock.MagicMock()
        builder = TestSuite.builder()
        self.assertEqual(builder, builder.from_testproject(testproject))
        self.assertEqual(builder.testproject, testproject)

    def test_from_testsuite(self):
        """Test setter for TestSuite parent TestSuite"""
        testsuite = mock.MagicMock()
        builder = TestSuite.builder()
        self.assertEqual(builder, builder.from_testsuite(testsuite))
        self.assertEqual(builder.testsuite, testsuite)


class TestSuiteTests(unittest.TestCase):

    def test_builder(self):
        """Test initialisation with default builder"""
        testsuite = mock.MagicMock()
        testproject = mock.MagicMock()
        testlink = mock.MagicMock()
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

    def test_api_builder(self):
        """Test initialisation of default builder with raw API data"""
        testlink = mock.MagicMock()
        testproject = mock.MagicMock()
        testsuite = mock.MagicMock()
        data = {'id': '123', 'name': "Example",
                'details': "Description", 'level': '4'}
        suite = TestSuite.builder(**data)\
                    .from_testlink(testlink)\
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
