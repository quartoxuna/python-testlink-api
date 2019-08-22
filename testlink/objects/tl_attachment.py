#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Attachment Object"""

# IMPORTS
from datetime import datetime

from testlink.objects.tl_object import TestlinkObjectFromAPIBuilder
from testlink.objects.tl_object import TestlinkObjectBuilder
from testlink.objects.tl_object import TestlinkObject
from testlink.objects.tl_object import strptime
from testlink.objects.tl_object import normalize_list


class AttachmentFromAPIBuilder(TestlinkObjectFromAPIBuilder):
    """Testlink Attachment Builder for raw Testlink API data

    :param str name: File name of the Attachment
    :param str description: Description of the Attachment
    :param str file_type: MIME type of the Attachment
    :param datetime.date created: Creation Date of the Attachment
    :param str content: Contents of the Attachment as base64 encoded string
    """

    def __init__(self, *args, **kwargs):
        super(AttachmentFromAPIBuilder, self).__init__(*args, **kwargs)
        self.name = kwargs.get('name', None)
        self.description = kwargs.get('title', None)
        self.file_type = kwargs.get('file_type', None)
        self.created = kwargs.get('date_added', None)
        self.content = kwargs.get('content', None)

        # Fix types
        if self.created is not None:
            self.created = datetime.strptime(self.created, Attachment.DATETIME_FORMAT)

    def build(self):
        """Generate new Attachment"""
        return Attachment(self)


class AttachmentBuilder(TestlinkObjectBuilder,
                        AttachmentFromAPIBuilder):
    """General Attachment Builder"""

    def __init__(self, *args, **kwargs):
        super(AttachmentBuilder, self).__init__(*args, **kwargs)

    def with_name(self, name):
        """Set the name of the Attachment
        :type name: str"""
        self.name = name
        return self

    def with_description(self, description):
        """Set the description of the Attachment
        :type description: str"""
        self.description = description
        return self

    def with_file_type(self, file_type):
        """Set the file type of the Attachment
        :type file_type: str"""
        self.file_type = file_type
        return self

    def created_on(self, creation_date):
        """Set the creation date of the Attachment
        :type creation_date: datetime.datetime"""
        self.created = creation_date
        return self

    def with_content(self, content):
        """Set the content of the Attachment
        :type content: str"""
        self.content = content
        return self


class Attachment(TestlinkObject):
    """Testlink Attachmen

    :param str name: Name of the Attachment
    :param str description: Description of the Attachment
    :param str file_type: File type of the Attachment
    :param datetime.datetime created: Creation time of the Attachment
    :param str content: Content of the Attachemnt as base64 encoded string
    """

    def __init__(self, builder, *args, **kwargs):
        super(Attachment,self).__init__(builder, *args, **kwargs)
        self.__name = builder.name
        self.__description = builder.description
        self.__file_type = builder.file_type
        self.__created = builder.created
        self.__content = builder.content

    def __str__(self):
        return "{}: {}".format(self.__class__.__name__, self.name)

    @staticmethod
    def builder(*args, **kwargs):
        return AttachmentBuilder(*args, **kwargs)

    @property
    def name(self):
        return self.__name

    @property
    def description(self):
        return self.__description

    @property
    def file_type(self):
        return self.__file_type

    @property
    def created(self):
        return self.__created

    @property
    def content(self):
        return self.__content


class AttachmentMixin(object):
    """Mixin class for Testlink Objects which can have Attachments

    :param str foreign_key_table: Name of foreign key table, used for getting attachment
    """

    def __init__(self, *args, **kwargs):
        super(AttachmentMixin, self).__init__()
        self.__foreign_key_table = kwargs.get('foreign_key_table', None)

    @property
    def foreign_key_table(self):
        return self.__foreign_key_table

    def attachments(self):
        """Returns all attachments for the current TestlinkObject
        :rtype: Iterator[Attachment]"""
        for data in self.testlink.getAttachments(self.id, self.foreign_key_table):
            yield AttachmentFromAPIBuilder(**data).build()
