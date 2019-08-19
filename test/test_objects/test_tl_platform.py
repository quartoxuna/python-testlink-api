# pylint: disable=missing-docstring

# IMPORTS
import unittest
from mock import MagicMock

from testlink.objects.tl_platform import PlatformFromAPIBuilder
from testlink.objects.tl_platform import Platform

class PlatformFromAPIBuilderTests(unittest.TestCase):

    def test_api_data(self):
        """Test builder initialisation with raw API data"""
        data = {'id': '123', 'name': "Example", 'notes': "Description"}
        builder = PlatformFromAPIBuilder(**data)
        self.assertEqual(builder.testlink_id, 123)
        self.assertEqual(builder.name, "Example")
        self.assertEqual(builder.description, "Description")


class PlatformBuilderTests(unittest.TestCase):

    def test_with_id(self):
        """Test setter for internal Testlink ID"""
        builder = Platform.builder()
        self.assertEqual(builder, builder.with_id(123))
        self.assertEqual(builder.testlink_id, 123)

    def test_from_testlink(self):
        """Test setter for parent Testlink instance"""
        testlink = MagicMock()
        builder = Platform.builder()
        self.assertEqual(builder, builder.from_testlink(testlink))
        self.assertEqual(builder.testlink, testlink)

    def test_with_name(self):
        """Test setter for Platform name"""
        builder = Platform.builder()
        self.assertEqual(builder, builder.with_name("Example"))
        self.assertEqual(builder.name, "Example")

    def test_with_description(self):
        """Test setter for Platform description"""
        builder = Platform.builder()
        self.assertEqual(builder, builder.with_description("Description"))
        self.assertEqual(builder.description, "Description")

    def test_from_testproject(self):
        """Test setter fro Platform parent TestProject"""
        testproject = MagicMock()
        builder = Platform.builder()
        self.assertEqual(builder, builder.from_testproject(testproject))
        self.assertEqual(builder.testproject, testproject)

    def test_from_testplan(self):
        """Test setter for Platform parent TestPlan"""
        testplan = MagicMock()
        builder = Platform.builder()
        self.assertEqual(builder, builder.from_testplan(testplan))
        self.assertEqual(builder.testplan, testplan)


class PlatformTests(unittest.TestCase):

    def test_builder(self):
        """Test initialisation with default builder"""
        testlink = MagicMock()
        testproject = MagicMock()
        testplan = MagicMock()

        platform = Platform.builder()\
                   .with_id(123)\
                   .from_testlink(testlink)\
                   .with_name("Example")\
                   .with_description("Description")\
                   .from_testproject(testproject)\
                   .from_testplan(testplan)\
                   .build()
        self.assertEqual(platform.id, 123)
        self.assertEqual(platform.name, "Example")
        self.assertEqual(platform.description, "Description")
        self.assertEqual(platform.testlink, testlink)
        self.assertEqual(platform.testproject, testproject)
        self.assertEqual(platform.testplan, testplan)
