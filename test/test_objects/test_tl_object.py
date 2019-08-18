#!/usr/bin/env python

# IMPORTS
import unittest
from mock import MagicMock

from testlink.objects.tl_object import TestlinkObject
from testlink.objects.tl_object import TestlinkObjectFromAPIBuilder

class TestlinkObject_Tests(unittest.TestCase):

    def test_api_builder(self):
        mock_testlink = MagicMock()
        parameters = {'id': '123'}
        obj = TestlinkObjectFromAPIBuilder(parent_testlink=mock_testlink, **parameters).build()
        self.assertEqual(obj.id, 123)
        self.assertEqual(obj.testlink, mock_testlink)

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
