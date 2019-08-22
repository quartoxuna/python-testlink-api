# pylint: disable=missing-docstring

# IMPORTS
import unittest
import datetime
import mock

from testlink.objects.tl_testplan import TestPlanFromAPIBuilder
from testlink.objects.tl_testplan import TestPlan

from testlink.api.testlink_api import TestlinkAPI
from testlink.objects.tl_testlink import Testlink
from testlink.objects.tl_testproject import TestProject
from testlink.objects.tl_platform import Platform
from testlink.objects.tl_build import Build

class TestPlanFromAPIBuilderTests(unittest.TestCase):

    def test_api_data(self):
        """Test builder initialisation with raw API data"""
        data = {'id': '123', 'name': 'Example',
                'notes': "Description", 'active': '1', 'is_public': '0'}
        builder = TestPlanFromAPIBuilder(**data)
        self.assertEqual(builder.testlink_id, 123)
        self.assertEqual(builder.name, "Example")
        self.assertEqual(builder.description, "Description")
        self.assertTrue(builder.active)
        self.assertFalse(builder.public)


class TestPlanBuilderTests(unittest.TestCase):

    def test_with_id(self):
        """Test setter for internal Testlink ID"""
        builder = TestPlan.builder()
        self.assertEqual(builder, builder.with_id(123))
        self.assertEqual(builder.testlink_id, 123)

    def test_from_testlink(self):
        """Test setter for parent Testlink instance"""
        testlink = mock.MagicMock()
        builder = TestPlan.builder()
        self.assertEqual(builder, builder.from_testlink(testlink))
        self.assertEqual(builder.testlink, testlink)

    def test_with_name(self):
        """Test setter for TestPlan name"""
        builder = TestPlan.builder()
        self.assertEqual(builder, builder.with_name("Example"))
        self.assertEqual(builder.name, "Example")

    def test_with_description(self):
        """Test setter for TestPlan description"""
        builder = TestPlan.builder()
        self.assertEqual(builder, builder.with_description("Description"))
        self.assertEqual(builder.description, "Description")

    def test_is_active(self):
        """Test setter for TestPlan active status"""
        builder = TestPlan.builder()
        self.assertEqual(builder, builder.is_active())
        self.assertTrue(builder.active)
        builder.is_active(False)
        self.assertFalse(builder.active)

    def test_is_not_active(self):
        """Test setter for TestPlan inactive status"""
        builder = TestPlan.builder()
        self.assertEqual(builder, builder.is_not_active())
        self.assertFalse(builder.active)

    def test_is_public(self):
        """Test setter for TestPlan public status"""
        builder = TestPlan.builder()
        self.assertEqual(builder, builder.is_public())
        self.assertTrue(builder.public)
        builder.is_public(False)
        self.assertFalse(builder.public)

    def test_is_not_public(self):
        """Test setter for TestPlan not public status"""
        builder = TestPlan.builder()
        self.assertEqual(builder, builder.is_not_public())
        self.assertFalse(builder.public)

    def test_from_testproject(self):
        """Test setter for TestPlan parent TestProject"""
        testlink = mock.MagicMock()
        builder = TestPlan.builder()
        self.assertEqual(builder, builder.from_testlink(testlink))
        self.assertEqual(builder.testlink, testlink)


class TestPlanTests(unittest.TestCase):

    def test_builder(self):
        """Test initialisation with default builder"""
        testlink = mock.MagicMock()
        testproject = mock.MagicMock()
        testplan = TestPlan.builder()\
                   .with_id(123)\
                   .from_testlink(testlink)\
                   .with_name("Example")\
                   .with_description("Description")\
                   .is_not_active()\
                   .is_public()\
                   .from_testproject(testproject)\
                   .build()
        self.assertEqual(testplan.id, 123)
        self.assertEqual(testplan.testlink, testlink)
        self.assertEqual(testplan.name, "Example")
        self.assertEqual(testplan.description, "Description")
        self.assertFalse(testplan.active)
        self.assertTrue(testplan.public)
        self.assertEqual(testplan.testproject, testproject)

    def test_api_builder(self):
        """Test initialisation of default builder with raw API data"""
        testlink = mock.MagicMock()
        testproject = mock.MagicMock()
        data = {'id': '123', 'name': 'Example',
                'notes': "Description", 'active': '1', 'is_public': '0'}
        testplan = TestPlan.builder(**data)\
                   .from_testproject(testproject)\
                   .from_testlink(testlink)\
                   .build()
        self.assertEqual(testplan.id, 123)
        self.assertEqual(testplan.testlink, testlink)
        self.assertEqual(testplan.name, "Example")
        self.assertEqual(testplan.description, "Description")
        self.assertTrue(testplan.active)
        self.assertFalse(testplan.public)
        self.assertEqual(testplan.testproject, testproject)

    def test_iterate_builds(self):
        """Test Iterator over Builds"""
        # Initialize Testlink Object
        testlink_api = mock.create_autospec(spec=TestlinkAPI)
        testlink = Testlink(testlink_api)

        # Prepare Server Mock
        build_data = [
            {'id': '1', 'name': "Build 1", 'notes': "Description 1", 'active': '0',
             'is_public': '1', 'creation_ts': '2019-08-19 12:34:56',
             'release_date': '2019-08-18'},
            {'id': '2', 'name': "Build 2", 'notes': "Description 2", 'active': '0',
             'is_public': '0', 'creation_ts': '2019-08-19 12:34:56',
             'release_date': '2019-08-18', 'closed_on_date': '2019-08-26'},
            {'id': '3', 'name': "Build 3", 'notes': "Description 3", 'active': '1',
             'is_public': '1', 'creation_ts': '2019-08-19 12:34:56'}
        ]
        testlink_api.getBuildsForTestPlan = mock.MagicMock(return_value=build_data)

        # Prepare parent TestProject
        testproject = TestProject.builder()\
                      .with_id(23)\
                      .from_testlink(testlink)\
                      .with_name("TestProject")\
                      .with_prefix("ABC")\
                      .with_testcase_count(12)\
                      .is_active()\
                      .is_public()\
                      .build()

        # Prepare parent TestPlan
        testplan = TestPlan.builder()\
                  .with_id(42)\
                  .with_name("TestPlan")\
                  .is_active()\
                  .is_public()\
                  .from_testlink(testlink)\
                  .from_testproject(testproject)\
                  .build()

        # Generate expected results
        build_1 = Build.builder()\
                  .with_id(1)\
                  .from_testlink(testlink)\
                  .with_name("Build 1")\
                  .with_description("Description 1")\
                  .is_not_active()\
                  .is_public()\
                  .created_on(datetime.datetime(2019, 8, 19, 12, 34, 56))\
                  .released_on(datetime.date(2019, 8, 18))\
                  .from_testplan(testplan)\
                  .build()
        build_2 = Build.builder()\
                  .with_id(2)\
                  .from_testlink(testlink)\
                  .with_name("Build 2")\
                  .with_description("Description 2")\
                  .is_not_active()\
                  .is_not_public()\
                  .created_on(datetime.datetime(2019, 8, 19, 12, 34, 56))\
                  .released_on(datetime.date(2019, 8, 18))\
                  .closed_on(datetime.date(2019, 8, 26))\
                  .from_testplan(testplan)\
                  .build()
        build_3 = Build.builder()\
                  .with_id(3)\
                  .from_testlink(testlink)\
                  .with_name("Build 3")\
                  .with_description("Description 3")\
                  .is_active()\
                  .is_public()\
                  .created_on(datetime.datetime(2019, 8, 19, 12, 34, 56))\
                  .from_testplan(testplan)\
                  .build()
        expected_builds = [build_1, build_2, build_3]

        # Check results
        for i, build in enumerate(testplan.builds):
            expected = expected_builds[i]
            self.assertEqual(expected, build)
            self.assertEqual(expected.id, build.id)
            self.assertEqual(expected.testlink, build.testlink)
            self.assertEqual(expected.name, build.name)
            self.assertEqual(expected.description, build.description)
            self.assertEqual(expected.active, build.active)
            self.assertEqual(expected.public, build.public)
            self.assertEqual(expected.created, build.created)
            self.assertEqual(expected.released, build.released)
            self.assertEqual(expected.closed, build.closed)
            self.assertEqual(expected.testplan, build.testplan)
        self.assertEqual(len(list(testplan.builds)), len(expected_builds))

    def test_iterate_platforms(self):
        """Test Iterator over Platforms"""
        # Initialize Testlink Object
        testlink_api = mock.create_autospec(spec=TestlinkAPI)
        testlink = Testlink(testlink_api)

        # Prepare Server Mock
        platform_data = [
            {'id': '1', 'name': "Platform 1", 'notes': "Description 1"},
            {'id': '2', 'name': "Platform 2", 'notes': "Description 2"},
            {'id': '3', 'name': "Platform 3", 'notes': "Description 3"}
        ]
        testlink_api.getTestPlanPlatforms = mock.MagicMock(return_value=platform_data)

        # Prepare parent TestProject
        testproject = TestProject.builder()\
                      .with_id(23)\
                      .from_testlink(testlink)\
                      .with_name("TestProject")\
                      .with_prefix("ABC")\
                      .with_testcase_count(23)\
                      .is_public()\
                      .is_active()\
                      .build()

        # Prepare parent TestPlan
        testplan = TestPlan.builder()\
                   .with_id(42)\
                   .from_testlink(testlink)\
                   .from_testproject(testproject)\
                   .with_name("TestPlan")\
                   .is_active()\
                   .is_public()\
                   .build()

        # Generate expected results
        platform_1 = Platform.builder()\
                     .with_id(1)\
                     .with_name("Platform 1")\
                     .with_description("Description 1")\
                     .from_testlink(testlink)\
                     .from_testproject(testproject)\
                     .from_testplan(testplan)\
                     .build()
        platform_2 = Platform.builder()\
                     .with_id(2)\
                     .with_name("Platform 2")\
                     .with_description("Description 2")\
                     .from_testlink(testlink)\
                     .from_testproject(testproject)\
                     .from_testplan(testplan)\
                     .build()
        platform_3 = Platform.builder()\
                     .with_id(3)\
                     .with_name("Platform 3")\
                     .with_description("Description 3")\
                     .from_testlink(testlink)\
                     .from_testproject(testproject)\
                     .from_testplan(testplan)\
                     .build()
        expected_platforms = [platform_1, platform_2, platform_3]

        # Check results
        for i, platform in enumerate(testplan.platforms):
            expected = expected_platforms[i]
            self.assertEqual(expected, platform)
            self.assertEqual(expected.id, platform.id)
            self.assertEqual(expected.testlink, platform.testlink)
            self.assertEqual(expected.name, platform.name)
            self.assertEqual(expected.description, platform.description)
            self.assertEqual(expected.testplan, platform.testplan)
        self.assertEqual(len(list(testplan.platforms)), len(expected_platforms))
