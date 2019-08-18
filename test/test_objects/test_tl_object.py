#!/usr/bin/env python

# IMPORTS
import unittest
from mock import MagicMock

from testlink.objects.tl_object import TestlinkObject
from testlink.objects.tl_object import TestlinkObjectFromAPIBuilder

class TestlinkObjectFromAPIBuilder_Tests(unittest.TestCase):

    def test_api_data(self):
        parameters = {'id': '123'}
        builder = TestlinkObjectFromAPIBuilder(**parameters)
        self.assertEqual(builder._id, 123)


class TestlinkObjectBuilder_Tests(unittest.TestCase):

    def test_with_id(self):
        builder = TestlinkObject.builder()
        self.assertEqual(builder, builder.with_id(123))
        self.assertEqual(builder._id, 123)

    def test_from_testlink(self):
        testlink = MagicMock()
        builder = TestlinkObject.builder()
        self.assertEqual(builder, builder.from_testlink(testlink))
        self.assertEqual(builder.testlink, testlink)


class TestlinkObject_Tests(unittest.TestCase):

    def test_default_builder(self):
        mock_testlink = MagicMock()
        obj = TestlinkObject.builder()\
              .with_id(123)\
              .from_testlink(mock_testlink)\
              .build()
        self.assertEqual(obj.id, 123)
        self.assertEqual(obj.testlink, mock_testlink)

    def test_invalid_no_id(self):
        mock_testlink = MagicMock()
        obj_builder = TestlinkObject.builder()\
                      .from_testlink(mock_testlink)
        self.assertRaises(AssertionError, obj_builder.build)

    def test_invalid_no_parent_testlink(self):
        obj_builder = TestlinkObject.builder()\
                      .with_id(123)
        self.assertRaises(AssertionError, obj_builder.build)

    def test_equal_check(self):
        mock_testlink = MagicMock()
        a = TestlinkObject.builder()\
            .with_id(123)\
            .from_testlink(mock_testlink)\
            .build()

        b = TestlinkObject.builder()\
            .with_id(456)\
            .from_testlink(mock_testlink)\
            .build()

        c = TestlinkObject.builder()\
            .with_id(123)\
            .from_testlink(mock_testlink)\
            .build()

        self.assertEqual(a, c)
        self.assertNotEqual(a, b)
        self.assertNotEqual(b, c)

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
