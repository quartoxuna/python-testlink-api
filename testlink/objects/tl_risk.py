#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Risk Object"""

# IMPORTS
import datetime

from testlink.objects.tl_object import TestlinkObject
from testlink.objects.tl_object import _STRPTIME_FUNC as strptime

class Risk(TestlinkObject):
    """Testlink Risk representation"""

    __slots__ = ["doc_id", "description", "author_id", "creation_ts", "modifier_id", "modification_ts",\
            "_requirement_id", "cross_coverage"]

    def __init__(\
            self,\
            risk_doc_id=None,\
            name='',\
            description='',\
            author_id=-1,\
            creation_ts=str(datetime.datetime.min),\
            modifier_id=-1,\
            modification_ts=str(datetime.datetime.min),\
            requirement_id=-1,\
            cross_coverage='',\
            api=None,\
            **kwargs\
        ):
        """Initializes a new Risk with the specified parameters
        @todo: doc
        """
        TestlinkObject.__init__(self, kwargs.get('id'), name, api)
        self.doc_id = unicode(risk_doc_id)
        self.description = description
        self.author_id = int(author_id)
        try:
            self.creation_ts = strptime(str(creation_ts), TestlinkObject.DATETIME_FORMAT)
        except ValueError:
            self.creation_ts = datetime.datetime.min
        try:
            self.modifier_id = int(modifier_id)
        except ValueError:
            self.modifier_id = -1
        try:
            self.modification_ts = strptime(str(modification_ts), TestlinkObject.DATETIME_FORMAT)
        except ValueError:
            self.modification_ts = datetime.datetime.min
        self._requirement_id = requirement_id
        self.cross_coverage = str(cross_coverage)

    def __str__(self):
        return "Risk %s: %s" % (self.doc_id, self.name)
