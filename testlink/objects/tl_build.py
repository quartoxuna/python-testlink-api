#!/usr/bin/env python
# -*- coding: utf-8 -*-

# IMPORTS
from datetime import datetime

from testlink.objects.tl_object import TestlinkObjectFromAPIBuilder
from testlink.objects.tl_object import TestlinkObjectBuilder
from testlink.objects.tl_object import TestlinkObject


class BuildFromAPIBuilder(TestlinkObjectFromAPIBuilder):
    """Testlink Build Builder for raw Testlink API data

    :ivar str name: Name of the Build
    :ivar str description: Description of the Build
    :ivar bool active: Active status of the build
    :ivar bool public: Public status of the build
    :ivar datetime.datetime created: Creation time of the Build
    :ivar datetime.date released: Relase date of the Build
    :ivar datetime.date closed: Closing date of the Build
    :ivar TestPlan testplan: Parent TestPlan
    """

    def __init__(self, *args, **kwargs):
        self.name = kwargs.pop('name', None)
        self.description = kwargs.pop('notes', None)
        self.active = kwargs.pop('active', None)
        self.public = kwargs.pop('is_public', None)
        self.testplan = kwargs.pop('parent_testplan', None)
        self.created = kwargs.pop('creation_ts', None)
        self.released = kwargs.pop('release_date', None)
        self.closed = kwargs.pop('closed_on_date', None)
        super(BuildFromAPIBuilder, self).__init__(*args, **kwargs)

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
        # Call Sanity checks of parent class
        super(BuildFromAPIBuilder, self).build()

        # Sanity checks
        assert self.name is not None, "No Build name defined"
        assert self.active is not None, "No Build active status defined"
        assert self.created is not None, "No Build creaton time defined"
        assert self.public is not None, "No Build public status defined"
        assert self.testplan is not None, "No parent TestPlan defined"

        return Build(self)


class BuildBuilder(TestlinkObjectBuilder,
                   BuildFromAPIBuilder):
    """General Build Builder"""

    def __init__(self, *args, **kwargs):
        super(BuildBuilder, self).__init__(*args, **kwargs)

    def with_name(self, name):
        """Set the name of the Build

        :param str name: Build name
        """
        self.name = name
        return self

    def with_description(self, description):
        """Set the description of the Build

        :param str description: Build description
        """
        self.description = description
        return self

    def is_active(self, active=True):
        """Set the Build to active

        :param bool active: Build active status
        """
        self.active = active
        return self

    def is_not_active(self):
        """Set the Build to inactive
        """
        self.active = False
        return self

    def is_public(self, public=True):
        """Set the Build to public

        :param bool public: Build public status
        """
        self.public = public
        return self

    def is_not_public(self):
        """Set the Build to not public
        """
        self.public = False
        return self

    def created_on(self, creation_date):
        """Set the creation date of the Build

        :param datetime.datetime creation_date: Build creation time
        """
        self.created = creation_date
        return self

    def released_on(self, release_date):
        """Set the release date of the Build

        :param datetime.date release_date: Build release date
        """
        self.released = release_date
        return self

    def closed_on(self, closing_date):
        """Set the closing date of the Build

        :param datetime.date closing_date: Build closing date
        """
        self.closed = closing_date
        return self

    def from_testplan(self, testplan):
        """Set the parent TestPlan of the Build

        :param TestPlan testplan: Build parent TestPlan
        """
        self.testplan = testplan
        return self


class Build(TestlinkObject):
    """Testlink Build

    :ivar str name: Name of the Build
    :ivar str description: Description of the Build
    :ivar bool active: Status of the Build
    :ivar bool public: Visibility of the Build
    :ivar datetime.datetime created: Creation Time of the Build
    :ivar datetime.datetime relased: Release Time of the Build
    :ivar datetime.datetime closed: Closing Time of the Build
    :ivar TestPlan testplan: Parent TestPlan instance
    """

    DATE_FORMAT = "%Y-%m-%d"
    """Default timestamp format for dates"""

    def __init__(self, builder, *args, **kwargs):
        super(Build, self).__init__(builder, *args, **kwargs)
        self.__name = builder.name
        self.__description = builder.description
        self.__active = builder.active
        self.__public = builder.public
        self.__created = builder.created
        self.__released = builder.released
        self.__closed = builder.closed
        self.__parent_testplan = builder.testplan

    def __str__(self):
        return "{}: {}".format(self.__class__.__name__, self.name)

    @staticmethod
    def builder(**api_data):
        """Generate a new BuildBuilder

        :param api_data: Raw API data
        :rtype: BuildBuilder
        """
        return BuildBuilder(**api_data)

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
