# pylint: disable=missing-docstring

# IMPORTS
import unittest
import datetime
from mock import MagicMock

from testlink.objects.tl_attachment import AttachmentFromAPIBuilder
from testlink.objects.tl_attachment import Attachment

class AttachmentFromAPIBuilderTests(unittest.TestCase):

    def test_api_data(self):
        """Test initialisation with raw API data"""
        data = {'id': '123', 'name': "Example", 'title': "Description",
                'file_type': 'text/plain', 'date_added': "2019-08-19 12:34:56",
                'content': 'SGVsbG8gV29ybGQK'}
        builder = AttachmentFromAPIBuilder(**data)
        self.assertEqual(builder.testlink_id, 123)
        self.assertEqual(builder.name, "Example")
        self.assertEqual(builder.description, "Description")
        self.assertEqual(builder.file_type, 'text/plain')
        self.assertEqual(builder.created, datetime.datetime(2019, 8, 19, 12, 34, 56))
        self.assertEqual(builder.content, 'SGVsbG8gV29ybGQK')


class AttachmentBuilderTests(unittest.TestCase):

    def test_with_id(self):
        """Test setter for internal Testlink ID"""
        builder = Attachment.builder()
        self.assertEqual(builder, builder.with_id(123))
        self.assertEqual(builder.testlink_id, 123)

    def test_from_testlink(self):
        """Test setter for parent Testlink instance"""
        testlink = MagicMock()
        builder = Attachment.builder()
        self.assertEqual(builder, builder.from_testlink(testlink))
        self.assertEqual(builder.testlink, testlink)

    def test_with_name(self):
        """Test setter for Attachment name"""
        builder = Attachment.builder()
        self.assertEqual(builder, builder.with_name("Example"))
        self.assertEqual(builder.name, "Example")

    def test_with_description(self):
        """Test setter for Attachment description"""
        builder = Attachment.builder()
        self.assertEqual(builder, builder.with_description("Description"))
        self.assertEqual(builder.description, "Description")

    def test_with_file_type(self):
        """Test setter for Attachment file type"""
        builder = Attachment.builder()
        self.assertEqual(builder, builder.with_file_type('text/plain'))
        self.assertEqual(builder.file_type, 'text/plain')

    def test_created_on(self):
        """Test setter for Attachment creation date"""
        creation_date = datetime.datetime(2019, 8, 19, 12, 34, 56)
        builder = Attachment.builder()
        self.assertEqual(builder, builder.created_on(creation_date))
        self.assertEqual(builder.created, creation_date)

    def test_with_content(self):
        """Test setter for Attachment content"""
        builder = Attachment.builder()
        self.assertEqual(builder, builder.with_content('SGVsbG8gV29ybGQK'))
        self.assertEqual(builder.content, 'SGVsbG8gV29ybGQK')


class AttachmentTests(unittest.TestCase):

    def test_builder(self):
        """Test initialisation with default builder"""
        testlink = MagicMock()
        attachment = Attachment.builder()\
                     .with_id(123)\
                     .from_testlink(testlink)\
                     .with_name("Example")\
                     .with_description("Description")\
                     .with_file_type('text/plain')\
                     .created_on(datetime.datetime(2019, 8, 19, 12, 34, 56))\
                     .with_content('SGVsbG8gV29ybGQK')\
                     .build()
        self.assertEqual(attachment.id, 123)
        self.assertEqual(attachment.name, "Example")
        self.assertEqual(attachment.description, "Description")
        self.assertEqual(attachment.file_type, 'text/plain')
        self.assertEqual(attachment.created, datetime.datetime(2019, 8, 19, 12, 34, 56))
        self.assertEqual(attachment.content, 'SGVsbG8gV29ybGQK')
        self.assertEqual(attachment.testlink, testlink)
