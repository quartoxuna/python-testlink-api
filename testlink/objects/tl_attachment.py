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
        return Attachment(
            # Attachment
            name=self.name,
            description=self.description,
            file_type=self.file_type,
            created=self.created,
            content=self.content,
            # TestlinkObject
            testlink_id=self.testlink_id,
            parent_testlink=self.testlink
    )


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

    def __init__(self, *args, **kwargs):
        super(Attachment,self).__init__(*args, **kwargs)
        self.__name = kwargs['name']
        self.__description = kwargs['description']
        self.__file_type = kwargs['file_type']
        self.__created = kwargs['created']
        self.__content = kwargs['content']

    def __str__(self):
        return "{}: {}".format(self.__class__.__name__, self.name)

    @staticmethod
    def builder():
        return AttachmentBuilder()

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


class IAttachmentGetter(object):
    """Interface class for getting attachments of various Testlink Objects"""

    def __init__(self, foreign_key_table="nodes_hierarchy"):
        super(IAttachmentGetter, self).__init__()
        self._foreign_key_table = foreign_key_table

    def iterAttachment(self, **params):
        """Iterates over TestlinkObject's attachments specified by parameters
        @returns: Matching attachments
        @rtype: generator
        """
        # Get all attachments for this object
        response = self._api.getAttachments(self.id, self._foreign_key_table)

        # Check for empty result
        if len(response) == 0:
            return
        attachments = [Attachment(api=self._api, **resp) for resp in response.values()]

        # Filter
        if len(params) > 0:
            for attach in attachments:
                for key, value in params.items():
                    # Skip None
                    if value is None:
                        continue
                    try:
                        if not unicode(getattr(attach, key)) == unicode(value):
                            attach = None
                            break
                    except AttributeError:
                        raise AttributeError("Invalid Search Paramater for Attachment: %s" % key)
                if attach is not None:
                    yield attach
        else:
            # Return all found attachments
            for attach in attachments:
                yield attach

    def getAttachment(self, **params):
        """Return all TestlinkObject's attachments specified by parameters
        @returns: Matching Attachments
        @rtype: mixed
        """
        return normalize_list([p for p in self.iterAttachment(**params)])

    def uploadAttachment(self, filename, filetype, content, title=None, description=None, **kwargs):
        """Upload an Attachment for the current object
        @param filename: Filename of the attached file
        @type filename: str
        @param filetype: MIME Type of the attached file
        @type filetype: str
        @param content: Contents of the file as Base64 encoded string
        @type content: str
        @param title: <optional> Title of the attachment
        @type title: str
        @param description: <optional> Description of the attachment
        @type description: str
        @keyword id: <optional> ID Override (used for TestCases)
        @returns: Server response
        @rtype: dict
        """
        # Check which ID to use
        _id = self.id
        if 'id' in kwargs:
            _id = kwargs['id']

        self._api.uploadAttachment(fkid=_id,
                                   fktable=self._foreign_key_table,
                                   filename=str(filename),
                                   filetype=str(filetype),
                                   content=content,
                                   title=title,
                                   description=description)
