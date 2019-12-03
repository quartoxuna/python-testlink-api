# pylint: disable=missing-docstring

# IMPORTS
import unittest
import mock

from testlink.objects.tl_keyword import KeywordFromAPIBuilder
from testlink.objects.tl_keyword import Keyword

class KeywordFromAPIBuilderTests(unittest.TestCase):

    def test_api_data(self):
        """Test builder initialisation with raw API data"""
        data = {'id': '123', 'keyword': "Keyword", 'notes': "Description 1", 'testcase_id': '42'}
        builder = KeywordFromAPIBuilder(**data)
        self.assertEqual(builder.testlink_id, 123)
        self.assertEqual(builder.name, "Keyword")
        self.assertEqual(builder.description, "Description 1")
        self.assertEqual(builder.testcase_id, 42)


class KeywordBuilderTests(unittest.TestCase):

    def test_with_id(self):
        """Test setter for internal Testlink ID"""
        builder = Keyword.builder()
        self.assertEqual(builder, builder.with_id(123))
        self.assertEqual(builder.testlink_id, 123)

    def test_from_testlink(self):
        """Test setter for parent Testlink instance"""
        testlink = mock.MagicMock()
        builder = Keyword.builder()
        self.assertEqual(builder, builder.from_testlink(testlink))
        self.assertEqual(builder.testlink, testlink)

    def test_with_name(self):
        """Test setter for Keyword name"""
        builder = Keyword.builder()
        self.assertEqual(builder, builder.with_name("Keyword"))
        self.assertEqual(builder.name, "Keyword")

    def test_with_description(self):
        """Test setter for Keyword description"""
        builder = Keyword.builder()
        self.assertEqual(builder, builder.with_description("Description 1"))
        self.assertEqual(builder.description, "Description 1")

    def test_with_testcase_id(self):
        """Test setter for related TestCase ID"""
        builder = Keyword.builder()
        self.assertEqual(builder, builder.with_testcase_id(42))
        self.assertEqual(builder.testcase_id, 42)


class KeywordTests(unittest.TestCase):

    def test_builder(self):
        """Test initialisation with default builder"""
        testlink = mock.MagicMock()
        keyword = Keyword.builder()\
                  .with_id(123)\
                  .from_testlink(testlink)\
                  .with_name("Keyword")\
                  .with_description("Description 1")\
                  .with_testcase_id(42)\
                  .build()
        self.assertEqual(keyword.id, 123)
        self.assertEqual(keyword.name, "Keyword")
        self.assertEqual(keyword.description, "Description 1")
        self.assertEqual(keyword.testcase_id, 42)
        self.assertEqual(keyword.testlink, testlink)

    def test_api_builder(self):
        """Test initialisation of default builder with raw API data"""
        testlink = mock.MagicMock()
        data = {'id': '123', 'keyword': "Keyword", 'notes': "Description 1", 'testcase_id': '42'}
        keyword = Keyword.builder(**data)\
                  .from_testlink(testlink)\
                  .build()
        self.assertEqual(keyword.id, 123)
        self.assertEqual(keyword.name, "Keyword")
        self.assertEqual(keyword.description, "Description 1")
        self.assertEqual(keyword.testcase_id, 42)
        self.assertEqual(keyword.testlink, testlink)
