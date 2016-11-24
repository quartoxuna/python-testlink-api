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

class Attachment(TestlinkObject):
    """Testlink Attachment representation"""

    slots = ["title", "file_type", "content", "date_added"]

    def __init__(self, title, file_type, content="", date_added=None, api=None, **kwargs):
        TestlinkObject.__init__(self, kwargs.get('id'), kwargs.get('name', "None", api))
        self.title = str(title)
        self.file_type = str(file_type)
        try:
            self.content = base64.b64decode(str(content))
        except TypeError:
            self.content = None
        try:
            self.date_added = strptime(str(date_added), TestlinkObject.DATETIME_FORMAT)
        except ValueError:
            self.date_added = datetime.datetime.min

    def __str__(self):
        return "Attachment %d: %s - %s (%s) %s" % (self.id, self.title, self.name, self.file_type, str(self.date_added))
