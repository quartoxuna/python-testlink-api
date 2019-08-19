#!/usr/bin/env python

# IMPORTS
import unittest
from mock import MagicMock

import datetime

from testlink.objects.tl_build import BuildFromAPIBuilder
from testlink.objects.tl_build import Build

class BuildFromAPIBuilder_Tests(unittest.TestCase):

    def test_api_data(self):
        data = {'id': '123', 'name': "Example", 'notes': "Description", 'active': '0',
                'is_public': '1', 'creation_ts': '2019-08-19 12:34:56',
                'release_date': '2019-08-18', 'closed_on_date': '2019-08-26'}
        builder = BuildFromAPIBuilder(**data)
        self.assertEqual(builder._id, 123)
        self.assertEqual(builder.name, "Example")
        self.assertEqual(builder.description, "Description")
        self.assertFalse(builder.active)
        self.assertTrue(builder.public)
        self.assertEqual(builder.created, datetime.datetime(2019, 8, 19, 12, 34, 56))
        self.assertEqual(builder.released, datetime.date(2019, 8, 18))
        self.assertEqual(builder.closed, datetime.date(2019, 8, 26))


class BuildBuilder_Tests(unittest.TestCase):

    def test_with_id(self):
        builder = Build.builder()
        self.assertEqual(builder, builder.with_id(123))
        self.assertEqual(builder._id, 123)

    def test_from_testlink(self):
        testlink = MagicMock()
        builder = Build.builder()
        self.assertEqual(builder, builder.from_testlink(testlink))
        self.assertEqual(builder.testlink, testlink)

    def test_with_name(self):
        builder = Build.builder()
        self.assertEqual(builder, builder.with_name("Example"))
        self.assertEqual(builder.name, "Example")

    def test_with_description(self):
        builder = Build.builder()
        self.assertEqual(builder, builder.with_description("Description"))
        self.assertEqual(builder.description, "Description")

    def test_is_active(self):
        builder = Build.builder()
        self.assertEqual(builder, builder.is_active())
        self.assertTrue(builder.active)
        builder.is_active(False)
        self.assertFalse(builder.active)

    def test_is_not_active(self):
        builder = Build.builder()
        self.assertEqual(builder, builder.is_not_active())
        self.assertFalse(builder.active)

    def test_is_public(self):
        builder = Build.builder()
        self.assertEqual(builder, builder.is_public())
        self.assertTrue(builder.public)
        builder.is_public(False)
        self.assertFalse(builder.public)

    def test_is_not_public(self):
        builder = Build.builder()
        self.assertEqual(builder, builder.is_not_public())
        self.assertFalse(builder.public)

    def test_created_on(self):
        creation_date = datetime.datetime(2019, 8, 19, 12, 34, 56)
        builder = Build.builder()
        self.assertEqual(builder, builder.created_on(creation_date))
        self.assertEqual(builder.created, creation_date)

    def test_released_on(self):
        release_date = datetime.date(2019, 8, 18)
        builder = Build.builder()
        self.assertEqual(builder, builder.released_on(release_date))
        self.assertEqual(builder.released, release_date)

    def test_closed_on(self):
        closing_date = datetime.date(2019, 8, 26)
        builder = Build.builder()
        self.assertEqual(builder, builder.closed_on(closing_date))
        self.assertEqual(builder.closed, closing_date)

    def test_from_testplan(self):
        testplan = MagicMock()
        builder = Build.builder()
        self.assertEqual(builder, builder.from_testplan(testplan))
        self.assertEqual(builder.testplan, testplan)


class Build_Tests(unittest.TestCase):

    def test_builder(self):
        testlink = MagicMock()
        testplan = MagicMock()
        creation_date = datetime.datetime(2019, 8, 19, 12, 34, 56)
        release_date = datetime.date(2019, 8, 18)
        closing_date = datetime.date(2019, 8, 26)

        build = Build.builder()\
                .with_id(123)\
                .from_testlink(testlink)\
                .with_name("Example")\
                .with_description("Description")\
                .is_not_active()\
                .is_public()\
                .created_on(creation_date)\
                .released_on(release_date)\
                .closed_on(closing_date)\
                .from_testplan(testplan)\
                .build()
        self.assertEqual(build.id, 123)
        self.assertEqual(build.name, "Example")
        self.assertEqual(build.description, "Description")
        self.assertFalse(build.active)
        self.assertTrue(build.public)
        self.assertEqual(build.created, creation_date)
        self.assertEqual(build.released, release_date)
        self.assertEqual(build.closed, closing_date)
        self.assertEqual(build.testlink, testlink)
        self.assertEqual(build.testplan, testplan)
