#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Keyword Object"""

# IMPORTS
from testlink.objects.tl_object import TestlinkObject


class Keyword(TestlinkObject):
    """Testlink TestCase Keyword representation    
    @ivar notes: Notes of the keyword
    @type notes: str
    @ivar testcase_id: <OPTIONAL> Related TestCase ID
    @type testcase_id: int
    @ivar _keyword: The actual keyword
    @type: str
    """

    __slots__ = ["id", "notes", "testcase_id", "_keyword"]

    def __init__(self, keyword_id=-1, notes=None, testcase_id=None, keyword=None, *args, **kwargs):
        super(Keyword, self).__init__(*args, **kwargs)
        self.notes = notes
        self.testcase_id = int(testcase_id)
        self._keyword = keyword

    def __str__(self):
        return str(self._keyword)

    def __eq__(self, other):
        if isinstance(other, Keyword):
            return self._keyword == other._keyword
        elif isinstance(other, basestring):
            return self._keyword == other
        else:
            return unicode(self._keyword) == unicode(other)

    def __ne__(self, other):
        return not self.__eq__(other)
