# pylint: disable=missing-docstring

# IMPORTS
import unittest
from mock import MagicMock

from testlink.objects.tl_object import TestlinkObject
from testlink.objects.tl_object import TestlinkObjectFromAPIBuilder

class TestlinkObjectFromAPIBuilderTests(unittest.TestCase):

    def test_api_data(self):
        """Test builder initialisation with raw API data"""
        parameters = {'id': '123'}
        builder = TestlinkObjectFromAPIBuilder(**parameters)
        self.assertEqual(builder.testlink_id, 123)


class TestlinkObjectBuilderTests(unittest.TestCase):

    def test_with_id(self):
        """Test setter for internal Testlink ID"""
        builder = TestlinkObject.builder()
        self.assertEqual(builder, builder.with_id(123))
        self.assertEqual(builder.testlink_id, 123)

    def test_from_testlink(self):
        """Test setter for parent Testlink instance"""
        testlink = MagicMock()
        builder = TestlinkObject.builder()
        self.assertEqual(builder, builder.from_testlink(testlink))
        self.assertEqual(builder.testlink, testlink)

    def test_invalid_no_id(self):
        """Test building without internal Testlink ID"""
        mock_testlink = MagicMock()
        obj_builder = TestlinkObject.builder()\
                      .from_testlink(mock_testlink)
        self.assertRaises(AssertionError, obj_builder.build)

    def test_invalid_no_parent_testlink(self):
        """Test building without parent Testlink instance"""
        obj_builder = TestlinkObject.builder()\
                      .with_id(123)
        self.assertRaises(AssertionError, obj_builder.build)


class TestlinkObjectTests(unittest.TestCase):

    def test_builder(self):
        """Test initialisation with default builder"""
        mock_testlink = MagicMock()
        obj = TestlinkObject.builder()\
              .with_id(123)\
              .from_testlink(mock_testlink)\
              .build()
        self.assertEqual(obj.id, 123)
        self.assertEqual(obj.testlink, mock_testlink)

    def test_equal_check(self):
        """Test override of __eq__"""
        mock_testlink = MagicMock()
        object_a = TestlinkObject.builder()\
            .with_id(123)\
            .from_testlink(mock_testlink)\
            .build()

        object_b = TestlinkObject.builder()\
            .with_id(456)\
            .from_testlink(mock_testlink)\
            .build()

        object_c = TestlinkObject.builder()\
            .with_id(123)\
            .from_testlink(mock_testlink)\
            .build()

        self.assertEqual(object_a, object_c)
        self.assertNotEqual(object_a, object_b)
        self.assertNotEqual(object_b, object_c)

    def test_read_only_attributes(self):
        mock_testlink = MagicMock()
        obj = TestlinkObject.builder()\
              .with_id(123)\
              .from_testlink(mock_testlink)\
              .build()

        with self.assertRaises(AttributeError):
            obj.id = 456

        with self.assertRaises(AttributeError):
            obj.testlink = MagicMock()

if __name__ == "__main__":
    unittest.main()
