# pylint: disable=missing-docstring

# IMPORTS
import datetime
import unittest
import mock


from testlink.objects.tl_build import BuildFromAPIBuilder
from testlink.objects.tl_build import Build

class BuildFromAPIBuilderTests(unittest.TestCase):

    def test_api_data(self):
        """Test builder initialization with raw API data"""
        data = {'id': '123', 'name': "Example", 'notes': "Description", 'active': '0',
                'is_public': '1', 'creation_ts': '2019-08-19 12:34:56',
                'release_date': '2019-08-18', 'closed_on_date': '2019-08-26'}
        builder = BuildFromAPIBuilder(**data)
        self.assertEqual(builder.testlink_id, 123)
        self.assertEqual(builder.name, "Example")
        self.assertEqual(builder.description, "Description")
        self.assertFalse(builder.active)
        self.assertTrue(builder.public)
        self.assertEqual(builder.created, datetime.datetime(2019, 8, 19, 12, 34, 56))
        self.assertEqual(builder.released, datetime.date(2019, 8, 18))
        self.assertEqual(builder.closed, datetime.date(2019, 8, 26))


class BuildBuilderTests(unittest.TestCase):

    def test_with_id(self):
        """Test setter for Testlink ID"""
        builder = Build.builder()
        self.assertEqual(builder, builder.with_id(123))
        self.assertEqual(builder.testlink_id, 123)

    def test_from_testlink(self):
        """Test setter for parent Testlink instance"""
        testlink = mock.MagicMock()
        builder = Build.builder()
        self.assertEqual(builder, builder.from_testlink(testlink))
        self.assertEqual(builder.testlink, testlink)

    def test_with_name(self):
        """Test setter for Build name"""
        builder = Build.builder()
        self.assertEqual(builder, builder.with_name("Example"))
        self.assertEqual(builder.name, "Example")

    def test_with_description(self):
        """Test setter for Build description"""
        builder = Build.builder()
        self.assertEqual(builder, builder.with_description("Description"))
        self.assertEqual(builder.description, "Description")

    def test_is_active(self):
        """Test setter for Build active status"""
        builder = Build.builder()
        self.assertEqual(builder, builder.is_active())
        self.assertTrue(builder.active)
        builder.is_active(False)
        self.assertFalse(builder.active)

    def test_is_not_active(self):
        """Test setter for Build inactive status"""
        builder = Build.builder()
        self.assertEqual(builder, builder.is_not_active())
        self.assertFalse(builder.active)

    def test_is_public(self):
        """Test setter for Build public status"""
        builder = Build.builder()
        self.assertEqual(builder, builder.is_public())
        self.assertTrue(builder.public)
        builder.is_public(False)
        self.assertFalse(builder.public)

    def test_is_not_public(self):
        """Test setter for Build not public status"""
        builder = Build.builder()
        self.assertEqual(builder, builder.is_not_public())
        self.assertFalse(builder.public)

    def test_created_on(self):
        """Test setter for Build creation date"""
        creation_date = datetime.datetime(2019, 8, 19, 12, 34, 56)
        builder = Build.builder()
        self.assertEqual(builder, builder.created_on(creation_date))
        self.assertEqual(builder.created, creation_date)

    def test_released_on(self):
        """Test setter for Build release date"""
        release_date = datetime.date(2019, 8, 18)
        builder = Build.builder()
        self.assertEqual(builder, builder.released_on(release_date))
        self.assertEqual(builder.released, release_date)

    def test_closed_on(self):
        """Test setter for Build closed date"""
        closing_date = datetime.date(2019, 8, 26)
        builder = Build.builder()
        self.assertEqual(builder, builder.closed_on(closing_date))
        self.assertEqual(builder.closed, closing_date)

    def test_from_testplan(self):
        """Test setter for Build parent testplan"""
        testplan = mock.MagicMock()
        builder = Build.builder()
        self.assertEqual(builder, builder.from_testplan(testplan))
        self.assertEqual(builder.testplan, testplan)


class BuildTests(unittest.TestCase):

    def test_builder(self):
        """Test initialization with default builder"""
        testlink = mock.MagicMock()
        testplan = mock.MagicMock()
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

    def test_api_builder(self):
        """Test intiialisation of default builer with raw API data"""
        testlink = mock.MagicMock()
        testplan = mock.MagicMock()
        data = {'id': '123', 'name': "Example", 'notes': "Description", 'active': '1',
                'is_public': '0', 'creation_ts': '2019-08-19 12:34:56',
                'release_date': '2019-08-18', 'closed_on_date': '2019-08-26'}
        build = Build.builder(**data)\
                .from_testlink(testlink)\
                .from_testplan(testplan)\
                .build()
        self.assertEqual(build.id, 123)
        self.assertEqual(build.name, "Example")
        self.assertEqual(build.description, "Description")
        self.assertTrue(build.active)
        self.assertFalse(build.public)
        self.assertEqual(build.created, datetime.datetime(2019, 8, 19, 12, 34, 56))
        self.assertEqual(build.released, datetime.date(2019, 8, 18))
        self.assertEqual(build.closed, datetime.date(2019, 8, 26))
        self.assertEqual(build.testlink, testlink)
        self.assertEqual(build.testplan, testplan)
