#!/usr/bin/env python
# -*- coding: utf-8 -*-

# IMPORTS
import time
import datetime

__all__ = ["strptime", "TestlinkObject", "normalize_list"]


# Backwards compatability methods
def strptime(date_string, fmt):
    date = time.strptime(date_string, fmt)
    return datetime.datetime(*(date[0:6]))
try:
    strptime = datetime.datetime.strptime
except AttributeError:
    pass


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


class TestlinkObjectFromAPIBuilder(object):
    """Testlink Object Builder for raw Testlink API data

    :param int _id: Internal Testlink ID of the object
    :param Testlink testlink: Parent Testlink instance
    """

    def __init__(self, *args, **kwargs):
        super(TestlinkObjectFromAPIBuilder, self).__init__()
        self.testlink_id = kwargs.get('id', None)
        self.testlink = kwargs.get('parent_testlink', None)

        # Fix types
        if self.testlink_id is not None:
            self.testlink_id = int(self.testlink_id)

    def build(self):
        """Generates a new TestlinkObject"""
        # Sanity checks
        assert self.testlink_id is not None, "Invalid internal ID '{}'".format(self.testlink_id)
        assert self.testlink is not None, "No parent Testlink instance defined"

        return TestlinkObject(self)


class TestlinkObjectBuilder(TestlinkObjectFromAPIBuilder):
    """General TestlinkObject Builder"""

    def __init__(self, *args, **kwargs):
        super(TestlinkObjectBuilder, self).__init__(*args, **kwargs)

    def with_id(self, testlink_id):
        """Set the internal ID of the Testlink Object
        :type testlink_id: int"""
        self.testlink_id = testlink_id
        return self

    def from_testlink(self, testlink):
        """Set the parent Testlink instance
        :type testlink: Testlink"""
        self.testlink = testlink
        return self


class TestlinkObject(object):
    """General Testlink Object

    :param int id: Internal Testlink ID
    :param Testlink testlink: Parent Testlink instance
    """

    DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"

    def __init__(self, builder, *args, **kwargs):
        super(TestlinkObject, self).__init__()
        self.__testlink_id = builder.testlink_id
        self.__parent_testlink = builder.testlink

    @staticmethod
    def builder():
        return TestlinkObjectBuilder()

    def __str__(self):
        return "{}: {}".format(self.__class__.__name__, self.id)

    def __id__(self):
        return self.__testlink_id

    def __eq__(self, other):
        return self.id == other.id

    @property
    def id(self):
        return self.__testlink_id

    @property
    def testlink(self):
        return self.__parent_testlink
