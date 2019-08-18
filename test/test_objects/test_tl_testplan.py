#!/usr/bin/env python

# IMPORTS
import unittest
from mock import MagicMock

from testlink.objects.tl_testplan import TestPlanFromAPIBuilder
from testlink.objects.tl_testplan import TestPlan


class TestPlanFromAPIBuilder_Tests(unittest.TestCase):

    def test_api_data(self):
        data = {'id': '123', 'name': 'Example', 'notes': "Description",
                'active': '1','is_public': '0'}
        builder = TestPlanFromAPIBuilder(**data)
        self.assertEqual(builder._id, 123)
        self.assertEqual(builder.name, "Example")
        self.assertEqual(builder.description, "Description")
        self.assertTrue(builder.active)
        self.assertFalse(builder.public)


class TestPlanBuilder_Tests(unittest.TestCase):

    def test_with_id(self):
        builder = TestPlan.builder()
        self.assertEqual(builder, builder.with_id(123))
        self.assertEqual(builder._id, 123)

    def test_from_testlink(self):
        testlink = MagicMock()
        builder = TestPlan.builder()
        self.assertEqual(builder, builder.from_testlink(testlink))
        self.assertEqual(builder.testlink, testlink)

    def test_with_name(self):
        builder = TestPlan.builder()
        self.assertEqual(builder, builder.with_name("Example"))
        self.assertEqual(builder.name, "Example")

    def test_with_description(self):
        builder = TestPlan.builder()
        self.assertEqual(builder, builder.with_description("Description"))
        self.assertEqual(builder.description, "Description")

    def test_is_active(self):
        builder = TestPlan.builder()
        self.assertEqual(builder, builder.is_active())
        self.assertTrue(builder.active)
        builder.is_active(False)
        self.assertFalse(builder.active)

    def test_is_not_active(self):
        builder = TestPlan.builder()
        self.assertEqual(builder, builder.is_not_active())
        self.assertFalse(builder.active)

    def test_is_public(self):
        builder = TestPlan.builder()
        self.assertEqual(builder, builder.is_public())
        self.assertTrue(builder.public)
        builder.is_public(False)
        self.assertFalse(builder.public)

    def test_is_not_public(self):
        builder = TestPlan.builder()
        self.assertEqual(builder, builder.is_not_public())
        self.assertFalse(builder.public)

    def test_from_testproject(self):
        testlink = MagicMock()
        builder = TestPlan.builder()
        self.assertEqual(builder, builder.from_testlink(testlink))
        self.assertEqual(builder.testlink, testlink)


class TestPlan_Tests(unittest.TestCase):

    def test_default(self):
        testlink = MagicMock()
        testproject = MagicMock()
        testplan = TestPlan.builder()\
                   .with_id(123)\
                   .from_testlink(testlink)\
                   .with_name("Example")\
                   .with_description("Description")\
                   .is_active()\
                   .is_public()\
                   .from_testproject(testproject)\
                   .build()
        self.assertEqual(testplan.id, 123)
        self.assertEqual(testplan.testlink, testlink)
        self.assertEqual(testplan.name, "Example")
        self.assertEqual(testplan.description, "Description")
        self.assertTrue(testplan.active)
        self.assertTrue(testplan.public)
        self.assertEqual(testplan.testproject, testproject)
