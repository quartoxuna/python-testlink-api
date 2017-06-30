#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Platform representation"""

# IMPORTS
from testlink.objects.tl_object import TestlinkObject


class Platform(TestlinkObject):
    """Testlink Platform representation
    @ivar notes: Platform notes
    @type notes: str
    """

    __slots__ = ("notes", "_parent_testproject", "_parent_testplan")

    def __init__(self, name=None, notes=None, parent_testproject=None, parent_testplan=None, api=None, **kwargs):
        TestlinkObject.__init__(self, kwargs.get('id'), name, api)
        self.notes = unicode(notes)
        self._parent_testproject = parent_testproject
        self._parent_testplan = parent_testplan

    def __str__(self):
        """Returns string representation"""
        return "Platform: %s" % self.name

    def getTestProject(self):
        """Returns associated TestProject"""
        return self._parent_testproject

    def iterTestProject(self):
        """Returns associated TestProject"""
        yield self._parent_testproject

    def getTestPlan(self):
        """Returns associated TestPlan"""
        return self._parent_testplan

    def iterTestPlan(self):
        """Returns associated TestPlan"""
        yield self._parent_testplan
