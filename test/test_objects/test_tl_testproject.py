# pylint: disable=missing-docstring

# IMPORTS
import unittest
import mock

from testlink.objects.tl_testproject import TestProjectFromAPIBuilder
from testlink.objects.tl_testproject import TestProject

from testlink.api.testlink_api import TestlinkAPI
from testlink.objects.tl_testlink import Testlink
from testlink.objects.tl_testsuite import TestSuite
from testlink.objects.tl_testplan import TestPlan

class TestProjectFromAPIBuilderTests(unittest.TestCase):

    def test_api_data(self):
        """Test builder initialisation with raw API data"""
        data = {'id': '123', 'name': "Example", 'prefix': 'ABC',
                'notes': "Description", 'active': '0', 'is_public': '1',
                'color': '#00FF00', 'tc_counter': '42',
                'opt': {
                    'requirementsEnabled': '1',
                    'testPriorityEnabled': '0',
                    'automationEnabled': '1',
                    'inventoryEnabled': '0'
                }
               }
        builder = TestProjectFromAPIBuilder(**data)
        self.assertEqual(builder.testlink_id, 123)
        self.assertEqual(builder.name, "Example")
        self.assertEqual(builder.description, "Description")
        self.assertEqual(builder.prefix, 'ABC')
        self.assertFalse(builder.active)
        self.assertTrue(builder.public)
        self.assertEqual(builder.color, '#00FF00')
        self.assertEqual(builder.testcase_count, 42)
        self.assertTrue(builder.requirement_feature)
        self.assertFalse(builder.priority_feature)
        self.assertTrue(builder.automation_feature)
        self.assertFalse(builder.inventory_feature)


class TestProjectBuilderTests(unittest.TestCase):

    def test_with_id(self):
        """Test setter for internal Testlink ID"""
        builder = TestProject.builder()
        self.assertEqual(builder, builder.with_id(123))
        self.assertEqual(builder.testlink_id, 123)

    def test_from_testlink(self):
        """Test setter for parent Testlink instance"""
        testlink = mock.MagicMock()
        builder = TestProject.builder()
        self.assertEqual(builder, builder.from_testlink(testlink))
        self.assertEqual(builder.testlink, testlink)

    def test_with_name(self):
        """Test setter for TestProject name"""
        builder = TestProject.builder()
        self.assertEqual(builder, builder.with_name("Example"))
        self.assertEqual(builder.name, "Example")

    def test_with_prefix(self):
        """Test setter for TestProject prefix"""
        builder = TestProject.builder()
        self.assertEqual(builder, builder.with_prefix('ABC'))
        self.assertEqual(builder.prefix, 'ABC')

    def test_with_description(self):
        """Test setter for TestProject description"""
        builder = TestProject.builder()
        self.assertEqual(builder, builder.with_description('Description'))
        self.assertEqual(builder.description, "Description")

    def test_is_active(self):
        """Test setter for TestProject active status"""
        builder = TestProject.builder()
        self.assertEqual(builder, builder.is_active())
        self.assertTrue(builder.active)
        builder.is_active(False)
        self.assertFalse(builder.active)

    def test_is_not_active(self):
        """Test setter for TestProject inactive status"""
        builder = TestProject.builder()
        self.assertEqual(builder, builder.is_not_active())
        self.assertFalse(builder.active)

    def test_is_public(self):
        """Test setter for TestProject public status"""
        builder = TestProject.builder()
        self.assertEqual(builder, builder.is_public())
        self.assertTrue(builder.public)
        builder.is_public(False)
        self.assertFalse(builder.public)

    def test_is_not_public(self):
        """Test setter for TestProject not public status"""
        builder = TestProject.builder()
        self.assertEqual(builder, builder.is_not_public())
        self.assertFalse(builder.public)

    def test_with_color(self):
        """Test setter for TestProject color"""
        builder = TestProject.builder()
        self.assertEqual(builder, builder.with_color('#00FF00'))
        self.assertEqual(builder.color, '#00FF00')

    def test_with_testcase_count(self):
        """Test setter for TestProject testcase count"""
        builder = TestProject.builder()
        self.assertEqual(builder, builder.with_testcase_count(42))
        self.assertEqual(builder.testcase_count, 42)

    def test_with_req_feature(self):
        """Test setter for TestProject requirement feature activation"""
        builder = TestProject.builder()
        self.assertEqual(builder, builder.with_requirement_feature())
        self.assertTrue(builder.requirement_feature)
        builder.with_requirement_feature(False)
        self.assertFalse(builder.requirement_feature)

    def test_without_req__feature(self):
        """Test setter for TestProject requirement feature deactivation"""
        builder = TestProject.builder()
        self.assertEqual(builder, builder.without_requirement_feature())
        self.assertFalse(builder.requirement_feature)

    def test_with_priority_feature(self):
        """Test setter for TestProject test priority feature activation"""
        builder = TestProject.builder()
        self.assertEqual(builder, builder.with_priority_feature())
        self.assertTrue(builder.priority_feature)
        builder.with_priority_feature(False)
        self.assertFalse(builder.priority_feature)

    def test_without_priority_feature(self):
        """Test setter for TestProject test priority feature deactivation"""
        builder = TestProject.builder()
        self.assertEqual(builder, builder.without_priority_feature())
        self.assertFalse(builder.priority_feature)

    def test_with_automation_feature(self):
        """Test setter for TestProject test automation feature activation"""
        builder = TestProject.builder()
        self.assertEqual(builder, builder.with_automation_feature())
        self.assertTrue(builder.automation_feature)
        builder.with_automation_feature(False)
        self.assertFalse(builder.automation_feature)

    def test_without_automation_feature(self):
        """Test setter for TestProject test automation feature deactivation"""
        builder = TestProject.builder()
        self.assertEqual(builder, builder.without_automation_feature())
        self.assertFalse(builder.automation_feature)

    def test_with_inventory_feature(self):
        """Test setter for TestProject inventory feature activation"""
        builder = TestProject.builder()
        self.assertEqual(builder, builder.with_inventory_feature())
        self.assertTrue(builder.inventory_feature)
        builder.with_inventory_feature(False)
        self.assertFalse(builder.inventory_feature)

    def test_without_inventory_feature(self):
        """Test setter for TestProject inventory feature deactivation"""
        builder = TestProject.builder()
        self.assertEqual(builder, builder.without_inventory_feature())
        self.assertFalse(builder.inventory_feature)


class TestProjectTests(unittest.TestCase):

    def test_builder(self):
        """Test initialisation with default builder"""
        testlink = mock.MagicMock()
        testproject = TestProject.builder()\
                      .with_id(123)\
                      .from_testlink(testlink)\
                      .with_name("Example")\
                      .with_prefix('ABC')\
                      .with_description("Description")\
                      .is_not_active()\
                      .is_public()\
                      .with_color('#00FF00')\
                      .with_testcase_count(42)\
                      .with_requirement_feature()\
                      .without_priority_feature()\
                      .with_automation_feature()\
                      .without_inventory_feature()\
                      .build()
        self.assertEqual(testproject.id, 123)
        self.assertEqual(testproject.name, "Example")
        self.assertEqual(testproject.prefix, 'ABC')
        self.assertEqual(testproject.description, "Description")
        self.assertFalse(testproject.active)
        self.assertTrue(testproject.public)
        self.assertEqual(testproject.color, '#00FF00')
        self.assertEqual(testproject.testcase_count, 42)
        self.assertTrue(testproject.requirement_feature)
        self.assertFalse(testproject.priority_feature)
        self.assertTrue(testproject.automation_feature)
        self.assertFalse(testproject.inventory_feature)
        self.assertEqual(testproject.testlink, testlink)

    def test_api_builder(self):
        """Test initialisation of default builder with raw API data"""
        testlink = mock.MagicMock()
        data = {'id': '123', 'name': "Example", 'prefix': 'ABC',
                'notes': "Description", 'active': '0', 'is_public': '1',
                'color': '#00FF00', 'tc_counter': '42',
                'opt': {
                    'requirementsEnabled': '1',
                    'testPriorityEnabled': '0',
                    'automationEnabled': '1',
                    'inventoryEnabled': '0'
                }
               }
        testproject = TestProject.builder(**data)\
                      .from_testlink(testlink)\
                      .build()
        self.assertEqual(testproject.id, 123)
        self.assertEqual(testproject.name, "Example")
        self.assertEqual(testproject.prefix, 'ABC')
        self.assertEqual(testproject.description, "Description")
        self.assertFalse(testproject.active)
        self.assertTrue(testproject.public)
        self.assertEqual(testproject.color, '#00FF00')
        self.assertEqual(testproject.testcase_count, 42)
        self.assertTrue(testproject.requirement_feature)
        self.assertFalse(testproject.priority_feature)
        self.assertTrue(testproject.automation_feature)
        self.assertFalse(testproject.inventory_feature)
        self.assertEqual(testproject.testlink, testlink)

    def test_iterate_testplans(self):
        """Iterate over testplans"""
        # Initialize Testlink Object
        testlink_api = mock.create_autospec(spec=TestlinkAPI)
        testlink = Testlink(testlink_api)

        # Prepare Server Mock
        testlink_api.getProjectTestPlans = mock.MagicMock()
        testlink_api.getProjectTestPlans.return_value = [
            {'id': '123', 'name': "TestPlan1", 'notes': "Description TestPlan1",
             'active': '1', 'is_public': '0'},
            {'id': '456', 'name': "TestPlan2", 'notes': "Description TestPlan2",
             'active': '0', 'is_public': '1'}
        ]

        # Prepare parent TestProject
        testproject = TestProject.builder()\
                      .with_id(23)\
                      .from_testlink(testlink)\
                      .with_name("TestProject")\
                      .with_prefix("ABC")\
                      .with_testcase_count(23)\
                      .is_active()\
                      .is_public()\
                      .build()

        # Generate expected results
        expected_testplans = [
            TestPlan.builder()\
            .with_id(123)\
            .from_testlink(testlink)\
            .with_name("TestPlan1")\
            .with_description("Description TestPlan1")\
            .is_active()\
            .is_not_public()\
            .from_testproject(testproject)\
            .build(),
            TestPlan.builder()\
            .with_id(456)\
            .from_testlink(testlink)\
            .with_name("TestPlan2")\
            .with_description("Description TestPlan2")\
            .is_not_active()\
            .is_public()\
            .from_testproject(testproject)\
            .build()
        ]

        # Check results
        for i, testplan in enumerate(testproject.testplans):
            expected = expected_testplans[i]
            self.assertEqual(expected, testplan)
            self.assertEqual(expected.id, testplan.id)
            self.assertEqual(expected.testlink, testplan.testlink)
            self.assertEqual(expected.name, testplan.name)
            self.assertEqual(expected.description, testplan.description)
            self.assertEqual(expected.active, testplan.active)
            self.assertEqual(expected.public, testplan.public)
            self.assertEqual(expected.testproject, testplan.testproject)
        self.assertTrue(len(list(testproject.testplans)) == 2)

    def test_iterate_testsuites(self):
        """Iterate over testsuites"""
        # Initialize Testlink Object
        testlink_api = mock.create_autospec(spec=TestlinkAPI)
        testlink = Testlink(testlink_api)

        # Prepare Server Mock
        #
        # + TestSuite 1
        # + TestSuite 2
        #     + TestSuite 2.1
        #         + TestSuite 2.1.1
        #     + TestSuite 2.2
        # + TestSuite 3
        #     + TestSuite 3.1
        #

        first_level_results = [
            {'id': '1', 'name': "TestSuite 1", 'details': "Description 1", 'level': '1'},
            {'id': '2', 'name': "TestSuite 2", 'details': "Description 2", 'level': '1'},
            {'id': '3', 'name': "TestSuite 3", 'details': "Description 3", 'level': '1'}
        ]
        second_level_results = [
            # Children of 'TestSuite 1'
            [],

            # Children of 'TestSuite 2'
            [
                {'id': '21', 'name': "TestSuite 2.1", 'details': "Description 2.1", 'level': '2'},
                {'id': '22', 'name': "TestSuite 2.2", 'details': "Description 2.2", 'level': '2'}
            ],

            # Children of 'TestSuite 2.1'
            [
                {'id': '211', 'name': "TestSuite 2.1.1", 'details': "Description 2.1.1", 'level': '3'}
            ],

            # Children of TestSuite 2.1.1'
            [],

            # Children of 'TestSuite 2.2'
            [],

            # Children of 'TestSuite 3'
            [
                {'id': '31', 'name': "TestSuite 3.1", 'details': "Description 3.1", 'level': '2'}
            ],

            # Children of 'TestSuite 3.1'
            []
        ]
        testlink_api.getFirstLevelTestSuitesForTestProject = mock.MagicMock(return_value=first_level_results)
        testlink_api.getTestSuitesForTestSuite = mock.MagicMock(side_effect=second_level_results)

        # Prepare parent TestProject
        testproject = TestProject.builder()\
                      .with_id(23)\
                      .from_testlink(testlink)\
                      .with_name("TestProject")\
                      .with_prefix("ABC")\
                      .with_testcase_count(23)\
                      .is_active()\
                      .is_public()\
                      .build()

        # Generate expected results
        testsuite_1 = TestSuite.builder()\
                      .with_id(1)\
                      .from_testlink(testlink)\
                      .with_name("TestSuite 1")\
                      .with_description("Description 1")\
                      .with_level(1)\
                      .from_testproject(testproject)\
                      .build()
        testsuite_2 = TestSuite.builder()\
                      .with_id(2)\
                      .from_testlink(testlink)\
                      .with_name("TestSuite 2")\
                      .with_description("Description 2")\
                      .with_level(1)\
                      .from_testproject(testproject)\
                      .build()
        testsuite_2_1 = TestSuite.builder()\
                        .with_id(21)\
                        .from_testlink(testlink)\
                        .with_name("TestSuite 2.1")\
                        .with_description("Description 2.1")\
                        .with_level(2)\
                        .from_testproject(testproject)\
                        .from_testsuite(testsuite_2)\
                        .build()
        testsuite_2_1_1 = TestSuite.builder()\
                          .with_id(211)\
                          .from_testlink(testlink)\
                          .with_name("TestSuite 2.1.1")\
                          .with_description("Description 2.1.1")\
                          .with_level(3)\
                          .from_testproject(testproject)\
                          .from_testsuite(testsuite_2_1)\
                          .build()
        testsuite_2_2 = TestSuite.builder()\
                        .with_id(22)\
                        .from_testlink(testlink)\
                        .with_name("TestSuite 2.2")\
                        .with_description("Description 2.2")\
                        .with_level(2)\
                        .from_testproject(testproject)\
                        .from_testsuite(testsuite_2)\
                        .build()
        testsuite_3 = TestSuite.builder()\
                      .with_id(3)\
                      .from_testlink(testlink)\
                      .with_name("TestSuite 3")\
                      .with_description("Description 3")\
                      .with_level(1)\
                      .from_testproject(testproject)\
                      .build()
        testsuite_3_1 = TestSuite.builder()\
                        .with_id(31)\
                        .from_testlink(testlink)\
                        .with_name("TestSuite 3.1")\
                        .with_description("Description 3.1")\
                        .with_level(2)\
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
        for i, testsuite in enumerate(testproject.testsuites):
            expected = expected_testsuites[i]
            self.assertEqual(expected, testsuite)
            self.assertEqual(expected.id, testsuite.id)
            self.assertEqual(expected.name, testsuite.name)
            self.assertEqual(expected.description, testsuite.description)
            self.assertEqual(expected.level, testsuite.level)
            self.assertEqual(expected.testproject, testsuite.testproject)
            self.assertEqual(expected.testlink, testsuite.testlink)
            self.assertEqual(expected.testsuite, testsuite.testsuite)

        # Verify that amount of returned testsuites match
        self.assertEqual(len(expected_testsuites), i+1)
