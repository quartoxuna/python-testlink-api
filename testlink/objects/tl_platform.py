#!/usr/bin/env python

# IMPORTS
from testlink.objects.tl_object import TestlinkObject

class Platform(TestlinkObject):
    """Testlink Platform representation
    @ivar notes: Platform notes
    @type notes: str
    """

    __slots__ = ("notes")

    def __init__(self, name=None, notes=None, api=None, **kwargs):
        TestlinkObject.__init__(self, kwargs.get('id'), name, api)
        self.notes = notes

    def __str__(self):
        return "Platform: %s" % self.name

