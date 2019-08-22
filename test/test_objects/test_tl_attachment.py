# pylint: disable=missing-docstring

# IMPORTS
import unittest
import datetime
import mock

from testlink.objects.tl_attachment import AttachmentFromAPIBuilder
from testlink.objects.tl_attachment import Attachment
from testlink.objects.tl_attachment import AttachmentMixin

from testlink.api.testlink_api import TestlinkAPI
from testlink.objects.tl_testlink import Testlink
from testlink.objects.tl_object import TestlinkObject

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
        testlink = mock.MagicMock()
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
        testlink = mock.MagicMock()
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

    def test_api_builder(self):
        """Test initialisation of default builder with raw API data"""
        testlink = mock.MagicMock()
        data = {'id': '123', 'name': "Example", 'title': "Description",
                'file_type': 'text/plain', 'date_added': "2019-08-19 12:34:56",
                'content': 'SGVsbG8gV29ybGQK'}
        attachment = Attachment.builder(**data)\
                     .from_testlink(testlink)\
                     .build()
        self.assertEqual(attachment.id, 123)
        self.assertEqual(attachment.name, "Example")
        self.assertEqual(attachment.description, "Description")
        self.assertEqual(attachment.file_type, 'text/plain')
        self.assertEqual(attachment.created, datetime.datetime(2019, 8, 19, 12, 34, 56))
        self.assertEqual(attachment.content, 'SGVsbG8gV29ybGQK')
        self.assertEqual(attachment.testlink, testlink)


class AttachmentMixinTests(unittest.TestCase):

    def test_mixin(self):
        """Test class definition with AttachmentMixin"""
        # Create Mockup class using closure
        class TestClass(AttachmentMixin):
            def __init__(self, *args, **kwargs):
                super(TestClass, self).__init__(*args, **kwargs)
                self._foreign_key_table = 'ForeignKeyTable'
        mixed_object = TestClass()

        self.assertEqual(mixed_object.foreign_key_table, 'ForeignKeyTable')
        self.assertTrue(hasattr(mixed_object, 'attachments'))

    def test_iterate_attachments(self):
        """Test Iterator over Attachments"""
        # Initialize Testlink Object
        testlink_api = mock.create_autospec(spec=TestlinkAPI)
        testlink = Testlink(testlink_api)

        # Prepare Server Mock
        attachment_data = [
            {'id': '1', 'name': "Example 1", 'title': "Description 1",
             'file_type': 'text/plain', 'date_added': "2019-08-20 12:34:56",
             'content': 'SGVsbG8gV29ybGQK'},
            {'id': '2', 'name': "Example 2", 'title': "Description 2",
             'file_type': 'text/html', 'date_added': "2019-05-16 06:54:32",
             'content': 'SGVsbG8gV29ybKQG'}
        ]
        testlink_api.getAttachments = mock.MagicMock(return_value=attachment_data)

        # Create Mockup class using closure
        class TestClass(AttachmentMixin, TestlinkObject):
            def __init__(self, *args, **kwargs):
                super(TestClass, self).__init__(*args, **kwargs)
                self._foreign_key_table = 'ForeignKeyTable'
        obj_builder = TestlinkObject.builder()\
                      .with_id(23)\
                      .from_testlink(testlink)
        mixed_object = TestClass(obj_builder)

        # Generate expected results
        attachment_1 = Attachment.builder()\
                       .with_id(1)\
                       .from_testlink(testlink)\
                       .with_name("Example 1")\
                       .with_description("Description 1")\
                       .with_file_type("text/plain")\
                       .created_on(datetime.datetime(2019, 8, 20, 12, 34, 56))\
                       .with_content("SGVsbG8gV29ybGQK")\
                       .build()
        attachment_2 = Attachment.builder()\
                       .with_id(2)\
                       .from_testlink(testlink)\
                       .with_name("Example 2")\
                       .with_description("Description 2")\
                       .with_file_type("text/html")\
                       .created_on(datetime.datetime(2019, 5, 16, 6, 54, 32))\
                       .with_content("SGVsbG8gV29ybKQG")\
                       .build()
        expected_attachments = [attachment_1, attachment_2]

        # Check results
        for i, attachment in enumerate(mixed_object.attachments):
            expected = expected_attachments[i]
            self.assertEqual(expected, attachment)
            self.assertEqual(expected.id, attachment.id)
            self.assertEqual(expected.testlink, attachment.testlink)
            self.assertEqual(expected.name, attachment.name)
            self.assertEqual(expected.description, attachment.description)
            self.assertEqual(expected.file_type, attachment.file_type)
            self.assertEqual(expected.created, attachment.created)
            self.assertEqual(expected.content, attachment.content)

        # Verity that amount of returned attachments match
        self.assertEqual(len(list(mixed_object.attachments)), len(expected_attachments))

        # Verify that API method was called correctly
        expected_calls = [
            mock.call(mixed_object.id, mixed_object.foreign_key_table)
        ]
        testlink_api.getAttachments.assert_has_calls(expected_calls)
