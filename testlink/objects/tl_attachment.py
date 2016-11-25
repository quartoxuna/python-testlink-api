#!/usr/bin/env python
# pylint: disable=line-too-long
# pylint: disable=too-many-arguments
# pylint: disable=too-few-public-methods
# -*- coding: utf-8 -*-

"""Attachment Object"""

# IMPORTS
import base64
import datetime

from testlink.objects.tl_object import TestlinkObject
from testlink.objects.tl_object import _STRPTIME_FUNC as strptime
from testlink.objects.tl_object import normalize_list

class Attachment(TestlinkObject):
    """Testlink Attachment representation"""

    slots = ["title", "file_type", "content", "date_added"]

    def __init__(self, title, file_type, content="", date_added=None, api=None, **kwargs):
        TestlinkObject.__init__(self, kwargs.get('id'), kwargs.get('name', "None"), api)
        self.title = str(title)
        self.file_type = str(file_type)
        try:
            self.content = base64.b64decode(str(content))
        except TypeError:
            self.content = None
        self.length = 0
        if self.content is not None:
            self.length = len(self.content)
        try:
            self.date_added = strptime(str(date_added), TestlinkObject.DATETIME_FORMAT)
        except ValueError:
            self.date_added = datetime.datetime.min

    def __str__(self):
        return "Attachment %d: %s - %s (%s) [%d Bytes] %s" % (self.id, self.title, self.name, self.file_type, self.length, str(self.date_added))


class IAttachmentGetter(object):
    """Interface class for getting attachments of various Testlink Objects"""

    def __init__(self, foreign_key_table="nodes_hierarchy", *args, **kwargs):
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
        if len(params)>0:
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
