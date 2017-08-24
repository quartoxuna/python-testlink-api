#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Attachment Object"""

# IMPORTS
import datetime

from testlink.objects.tl_object import TestlinkObject
from testlink.objects.tl_object import strptime
from testlink.objects.tl_object import normalize_list


class Attachment(TestlinkObject):
    """Testlink Attachment representation"""

    slots = ["title", "file_type", "content", "date_added"]

    def __init__(self, title, file_type, content="", date_added=None, api=None, **kwargs):
        TestlinkObject.__init__(self, kwargs.get('id'), title, api)
        self.file_name = kwargs.get("name", "")
        self.file_type = str(file_type)
        self.content = str(content)
        self.length = 0
        if self.content is not None:
            self.length = len(self.content)
        try:
            self.date_added = strptime(str(date_added), TestlinkObject.DATETIME_FORMAT)
        except ValueError:
            self.date_added = datetime.datetime.min

    def __str__(self):
        return "Attachment %d: %s - %s (%s) [%d Bytes] %s" %\
               (self.id, self.name, self.file_name, self.file_type, self.length, str(self.date_added))

    def delete(self):
        """Deletes the current attchment
        @returns: Success state
        @rtype: bool
        """
        resp = self._api.deleteAttachment(self.id)
        if isinstance(resp, list) and len(resp) == 1:
            resp = resp[0]
        return resp['status_ok']


class IAttachmentGetter(object):
    """Interface class for getting attachments of various Testlink Objects"""

    def __init__(self, foreign_key_table="nodes_hierarchy"):
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
