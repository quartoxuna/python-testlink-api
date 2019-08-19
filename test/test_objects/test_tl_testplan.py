# pylint: disable=missing-docstring

# IMPORTS
import unittest
import mock

from testlink.objects.tl_testplan import TestPlanFromAPIBuilder
from testlink.objects.tl_testplan import TestPlan


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
