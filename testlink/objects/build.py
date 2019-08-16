#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Build Object"""

# IMPORTS
import datetime
from testlink.objects.tl_object import TestlinkObject
from testlink.objects.tl_object import strptime


class Build(TestlinkObject):
    """Testlink Build representation
    @ivar notes: Build notes
    @type notes: str
    """

    __slots__ = ("active", "open", "notes", "creation_ts", "release_date",
                 "closed_on_date", "_parent_testplan")

    def __init__(self, notes=None, is_open=False, active=False, creation_ts=None, closed_on_date=None,
                 release_date=None, parent_testplan=None, *args, **kwargs):
        super(Build, self).__init__(*args, **kwargs)
        self.active = bool(int(active))
        self.open = bool(int(is_open))
        self.notes = unicode(notes)
        try:
            self.creation_ts = strptime(str(creation_ts), TestlinkObject.DATETIME_FORMAT)
        except ValueError:
            self.creation_ts = datetime.datetime.min
        try:
            self.release_date = strptime(str(release_date), TestlinkObject.DATETIME_FORMAT)
        except ValueError:
            self.release_date = datetime.datetime.min
        try:
            self.closed_on_date = strptime(str(closed_on_date), TestlinkObject.DATETIME_FORMAT)
        except ValueError:
            self.closed_on_date = datetime.datetime.min
        self._parent_testplan = parent_testplan

    def __str__(self):
        """Returns string representation"""
        return "Build: %s" % self.name

    def getTestPlan(self):
        """Returns associated TestPlan"""
        return self._parent_testplan

    def iterTestPlan(self):
        """Returns associated TestPlan"""
        yield self._parent_testplan
