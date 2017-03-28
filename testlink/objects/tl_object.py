#!/usr/bin/env python

"""Helper Methods and Classes"""

__all__ = ["_STRPTIME_FUNC", "TestlinkObject", "normalize_list"]

# IMPORTS
import time
import datetime

# Backwards compatability methods
try:
    _STRPTIME_FUNC = datetime.datetime.strptime
except AttributeError:
    _STRPTIME_FUNC = lambda date_string, fmt: datetime.datetime((time.strptime(date_string, fmt)[0:6]).values())

# Helper method
def normalize_list(res):
    """Normalizes a result list.
    If the specified list is empty, return None.
    If the specified list has only one element, return that element.
    Else return the list as is.
    @param res: Result list
    @type res: list
    @rtype: mixed
    """
    if len(res) == 0:
        return None
    elif len(res) == 1:
        return res[0]
    else:
        return res

class TestlinkObject:
    """Abstract Testlink Object
    @ivar id: Internal Testlink Id of the object
    @type id: int
    @ivar name: Internal Testlink name of the object
    @type name: str
    """

    __slots__ = ("id", "name", "_api", "path")

    # Global datetime format
    DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"

    # Default ID
    DEFAULT_ID = 0

    def __init__(self, _id=None, name="", api=None):
        """Initialises base Testlink object
        @param id: Internal Testlink Id of the object
        @type id: int
        @param name: Internal Testlink name of the object
        @type name: str
        @keyword kwargs: Additonal attributes
        """
        if _id is not None:
            self.id = int(_id)
        else:
            self.id = TestlinkObject.DEFAULT_ID
        self.name = unicode(name)
        self._api = api

    def __str__(self):
        """Returns string representation"""
        return "TestlinkObject (%d) %s" % (self.id, self.name)

    def __unicode__(self):
        return unicode(self.__str__())

    def __eq__(self, other):
        return self.id == other.id

    @property
    def path(self):
        """Returns the full path of a testlink object.
        @returns: List
        @rtype: list
        """
        res = self._api.getFullPath(self.id)
        if len(res) > 0:
            return res[str(self.id)]
        else:
            return []
