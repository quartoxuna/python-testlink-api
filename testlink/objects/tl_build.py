#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Build Object"""

# IMPORTS
from datetime import datetime

from testlink.objects.tl_object import TestlinkObjectFromAPIBuilder
from testlink.objects.tl_object import TestlinkObjectBuilder
from testlink.objects.tl_object import TestlinkObject


class BuildFromAPIBuilder(TestlinkObjectFromAPIBuilder):
    """Testlink Build Builder for raw Testlink API data

    :param str name: Name of the Build
    :param str description: Description of the Build
    :param bool active: Active status of the build
    :param bool public: Public status of the build
    :param TestPlan testplan: Parent TestPlan
    """

    def __init__(self, *args, **kwargs):
        super(BuildFromAPIBuilder, self).__init__(*args, **kwargs)
        self.name = kwargs.get('name', None)
        self.description = kwargs.get('notes', None)
        self.active = kwargs.get('active', None)
        self.public = kwargs.get('is_public', None)
        self.testplan = kwargs.get('parent_testplan', None)

        self.created = kwargs.get('creation_ts', None)
        self.released = kwargs.get('release_date', None)
        self.closed = kwargs.get('closed_on_date', None)

        # Fix types
        if self.active is not None:
            self.active = bool(int(self.active))
        if self.public is not None:
            self.public = bool(int(self.public))
        if self.created is not None:
            self.created = datetime.strptime(self.created, Build.DATETIME_FORMAT)
        if self.released is not None:
            self.released = datetime.strptime(self.released, Build.DATE_FORMAT).date()
        if self.closed is not None:
            self.closed = datetime.strptime(self.closed, Build.DATE_FORMAT).date()

    def build(self):
        """Generate a new Build"""
        # Sanity checks
        assert self.name is not None, "No Build name defined"
        assert self.active is not None, "No Build active status defined"
        assert self.created is not None, "No Build creaton time defined"
        assert self.public is not None, "No Build public status defined"
        assert self.testplan is not None, "No parent TestPlan defined"

        return Build(
            # Build
            name=self.name,
            description=self.description,
            active=self.active,
            public=self.public,
            created=self.created,
            released=self.released,
            closed=self.closed,
            parent_testplan=self.testplan,
            # TestlinkObject
            _id=self._id,
            parent_testlink=self.testlink
        )


class BuildBuilder(TestlinkObjectBuilder,
                   BuildFromAPIBuilder):
    """General Build Builder"""

    def __init__(self, *args, **kwargs):
        super(BuildBuilder, self).__init__(*args, **kwargs)

    def with_name(self, name):
        """Set the name of the Build
        :type name: str"""
        self.name = name
        return self

    def with_description(self, description):
        """Set the description of the Build
        :type description: str"""
        self.description = description
        return self

    def is_active(self, active=True):
        """Set the Build to active
        :type active: bool"""
        self.active = active
        return self

    def is_not_active(self):
        """Set the Build to inactive"""
        self.active = False
        return self

    def is_public(self, public=True):
        """Set the Build to public
        :type public: bool"""
        self.public = public
        return self

    def is_not_public(self):
        """Set the Build to not public"""
        self.public = False
        return self

    def created_on(self, creation_date):
        """Set the creation date of the Build
        :type creation_date: datetime.datetime"""
        self.created = creation_date
        return self

    def released_on(self, release_date):
        """Set the release date of the Build
        :type release_date: datetime.datetime"""
        self.released = release_date
        return self

    def closed_on(self, closing_date):
        """Set the closing date of the Build
        :type closing_date: datetime.datetime"""
        self.closed = closing_date
        return self

    def from_testplan(self, testplan):
        """Set the parent TestPlan of the Build
        :type testplan: TestPlan"""
        self.testplan = testplan
        return self


class Build(TestlinkObject):
    """Testlink Build

    :param str name: Name of the Build
    :param str description: Description of the Build
    :param bool active: Status of the Build
    :param bool public: Visibility of the Build
    :param datetime.datetime created: Creation Time of the Build
    :param datetime.datetime relased: Release Time of the Build
    :param datetime.datetime closed: Closing Time of the Build
    :param TestPlan testplan: Parent TestPlan instance
    """

    DATE_FORMAT = "%Y-%m-%d"

    def __init__(self, *args, **kwargs):
        super(Build, self).__init__(*args, **kwargs)
        self.__name = kwargs['name']
        self.__description = kwargs['description']
        self.__active = kwargs['active']
        self.__public = kwargs['public']
        self.__created = kwargs['created']
        self.__released = kwargs['released']
        self.__closed = kwargs['closed']
        self.__parent_testplan = kwargs['parent_testplan']

    def __str__(self):
        return "{}: {}".format(self.__class__.__name__, self.name)

    @staticmethod
    def builder():
        return BuildBuilder()

    @property
    def name(self):
        return self.__name

    @property
    def description(self):
        return self.__description

    @property
    def active(self):
        return self.__active

    @property
    def public(self):
        return self.__public

    @property
    def created(self):
        return self.__created

    @property
    def released(self):
        return self.__released

    @property
    def closed(self):
        return self.__closed

    @property
    def testplan(self):
        return self.__parent_testplan

    def getTestPlan(self):
        """Returns associated TestPlan"""
        return self._parent_testplan

    def iterTestPlan(self):
        """Returns associated TestPlan"""
        yield self._parent_testplan
