# pylint: disable=missing-docstring

# IMPORTS
import unittest
import mock

from testlink.objects.tl_testsuite import TestSuiteFromAPIBuilder
from testlink.objects.tl_testsuite import TestSuite

from testlink.api.testlink_api import TestlinkAPI
from testlink.objects.tl_testlink import Testlink
from testlink.objects.tl_testproject import TestProject

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

    def test_iterate_testsuites(self):
        """Iterator over nested testsuites"""
        # Initialize Testlink Object
        testlink_api = mock.create_autospec(spec=TestlinkAPI)
        testlink = Testlink(testlink_api)

        # Prepare Server Mock
        #
        # + TestSuite 0 (self)
        #     + TestSuite 1
        #     + TestSuite 2
        #         + TestSuite 2.1
        #             + TestSuite 2.1.1
        #         + TestSuite 2.2
        #     + TestSuite 3
        #         + TestSuite 3.1
        #

        leveled_results = [
            # Children of 'TestSuite 0'
            [
                {'id': '1', 'name': "TestSuite 1", 'details': "Description 1", 'level': '2'},
                {'id': '2', 'name': "TestSuite 2", 'details': "Description 2", 'level': '2'},
                {'id': '3', 'name': "TestSuite 3", 'details': "Description 3", 'level': '2'}
            ],

            # Children of 'TestSuite 1'
            [],

            # Children of 'TestSuite 2'
            [
                {'id': '21', 'name': "TestSuite 2.1", 'details': "Description 2.1", 'level': '3'},
                {'id': '22', 'name': "TestSuite 2.2", 'details': "Description 2.2", 'level': '3'}
            ],

            # Children of 'TestSuite 2.1'
            [
                {'id': '211', 'name': "TestSuite 2.1.1", 'details': "Description 2.1.1", 'level': '4'}
            ],

            # Children of 'TestSuite 2.1.1'
            [],

            # Children of 'TestSuite 2.2'
            [],

            # Children of 'TestSuite 3'
            [
                {'id': '31', 'name': "TestSuite 3.1", 'details': "Description 3.1", 'level': '3'}
            ],

            # Children of 'TestSuite 3.1'
            []
        ]
        testlink_api.getTestSuitesForTestSuite = mock.MagicMock(side_effect=leveled_results)

        # Prepare parent TestProject
        testproject = TestProject.builder()\
                      .with_id(23)\
                      .from_testlink(testlink)\
                      .with_name("TestProject")\
                      .with_prefix("ABC")\
                      .with_testcase_count(20)\
                      .is_active()\
                      .is_public()\
                      .build()

        # Prepare current TestSuite
        testsuite_0 = TestSuite.builder()\
                    .with_id(0)\
                    .from_testlink(testlink)\
                    .with_name("TestSuite 0")\
                    .with_description("Description 0")\
                    .with_level(1)\
                    .from_testproject(testproject)\
                    .build()

        # Generate expected results
        testsuite_1 = TestSuite.builder()\
                      .with_id(1)\
                      .from_testlink(testlink)\
                      .with_name("TestSuite 1")\
                      .with_description("Description 1")\
                      .with_level(2)\
                      .from_testproject(testproject)\
                      .from_testsuite(testsuite_0)\
                      .build()
        testsuite_2 = TestSuite.builder()\
                      .with_id(2)\
                      .from_testlink(testlink)\
                      .with_name("TestSuite 2")\
                      .with_description("Description 2")\
                      .with_level(2)\
                      .from_testproject(testproject)\
                      .from_testsuite(testsuite_0)\
                      .build()
        testsuite_2_1 = TestSuite.builder()\
                        .with_id(21)\
                        .from_testlink(testlink)\
                        .with_name("TestSuite 2.1")\
                        .with_description("Description 2.1")\
                        .with_level(3)\
                        .from_testproject(testproject)\
                        .from_testsuite(testsuite_2)\
                        .build()
        testsuite_2_1_1 = TestSuite.builder()\
                          .with_id(211)\
                          .from_testlink(testlink)\
                          .with_name("TestSuite 2.1.1")\
                          .with_description("Description 2.1.1")\
                          .with_level(4)\
                          .from_testproject(testproject)\
                          .from_testsuite(testsuite_2_1)\
                          .build()
        testsuite_2_2 = TestSuite.builder()\
                        .with_id(22)\
                        .from_testlink(testlink)\
                        .with_name("TestSuite 2.2")\
                        .with_description("Description 2.2")\
                        .with_level(3)\
                        .from_testproject(testproject)\
                        .from_testsuite(testsuite_2)\
                        .build()
        testsuite_3 = TestSuite.builder()\
                      .with_id(3)\
                      .from_testlink(testlink)\
                      .with_name("TestSuite 3")\
                      .with_description("Description 3")\
                      .with_level(2)\
                      .from_testproject(testproject)\
                      .from_testsuite(testsuite_0)\
                      .build()
        testsuite_3_1 = TestSuite.builder()\
                        .with_id(31)\
                        .from_testlink(testlink)\
                        .with_name("TestSuite 3.1")\
                        .with_description("Description 3.1")\
                        .with_level(3)\
                        .from_testproject(testproject)\
                        .from_testsuite(testsuite_3)\
                        .build()
        expected_testsuites = [
            testsuite_1,
            testsuite_2,
            testsuite_2_1,
            testsuite_2_1_1,
            testsuite_2_2,
            testsuite_3,
            testsuite_3_1
        ]

        # Check results
        for i, testsuite in enumerate(testsuite_0.testsuites):
            expected = expected_testsuites[i]
            self.assertEqual(expected.id, testsuite.id)
            self.assertEqual(expected.name, testsuite.name)
            self.assertEqual(expected.description, testsuite.description)
            self.assertEqual(expected.level, testsuite.level)
            self.assertEqual(expected.testproject, testsuite.testproject)
            self.assertEqual(expected.testlink, testsuite.testlink)
            self.assertEqual(expected.testsuite, testsuite.testsuite)

        # Verify that amount of returned testsuites match
        self.assertEqual(len(expected_testsuites), i+1)

        # Verify that API method was called directly
        expected_calls = [
            mock.call(testsuite_0.id, testproject.id),
            mock.call(testsuite_1.id, testproject.id),
            mock.call(testsuite_2.id, testproject.id),
            mock.call(testsuite_2_1.id, testproject.id),
            mock.call(testsuite_2_1_1.id, testproject.id),
            mock.call(testsuite_2_2.id, testproject.id),
            mock.call(testsuite_3.id, testproject.id),
            mock.call(testsuite_3_1.id, testproject.id)
        ]
        testlink_api.getTestSuitesForTestSuite.assert_has_calls(expected_calls)
