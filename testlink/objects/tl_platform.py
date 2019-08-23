#!/usr/bin/env python
# -*- coding: utf-8 -*-

# IMPORTS
from testlink.objects.tl_object import TestlinkObjectFromAPIBuilder
from testlink.objects.tl_object import TestlinkObjectBuilder
from testlink.objects.tl_object import TestlinkObject


class PlatformFromAPIBuilder(TestlinkObjectFromAPIBuilder):
    """Testlink Platform Builder for raw Testlink API data

    :ivar str name: Name of the Platform
    :ivar str description: Description of the Platform
    :ivar TestProject testproject: Parent TestProject
    :ivar TestPlan testplan: Parent TestPlan

    .. todo::
        Remove *parent_testproject* from API builder


    .. todo::
        Remove *parent_testplan* from API builder
    """

    def __init__(self, *args, **kwargs):
        self.name = kwargs.pop('name', None)
        self.description = kwargs.pop('notes', None)
        self.testproject = kwargs.pop('parent_testproject', None)
        self.testplan = kwargs.pop('parent_testplan', None)
        super(PlatformFromAPIBuilder, self).__init__(*args, **kwargs)

    def build(self):
        """Generate new Platform"""
        # Call Sanity checks of parent class
        super(PlatformFromAPIBuilder, self).build()

        # Sanity checks
        assert self.name is not None, "No Platform name defined"
        assert self.testproject is not None; "No parent TestProject defined"

        return Platform(self)


class PlatformBuilder(TestlinkObjectBuilder,
                      PlatformFromAPIBuilder):
    """General Platform Builder"""

    def __init__(self, *args, **kwargs):
        super(PlatformBuilder, self).__init__(*args, **kwargs)

    def with_name(self, name):
        """Set the name of the Platform

        :param str name: Platform name
        :rtype: PlatformBuilder
        """
        self.name = name
        return self

    def with_description(self, description):
        """Set the description of the Platform

        :param str description: Platform description
        :rtype: PlatformBuilder
        """
        self.description = description
        return self

    def from_testproject(self, testproject):
        """Set the parent TestProject for the Platform

        :param TestProject testproject: Platform parent TestProject
        :rtype: PlatformBuilder
        """
        self.testproject = testproject
        return self

    def from_testplan(self, testplan):
        """Set the parent TestPlan for the Platform

        :param TestPlan testplan: Platform parent TestPlan
        :rtype: PlatformBuilder
        """
        self.testplan = testplan
        return self


class Platform(TestlinkObject):
    """Testlink Platform

    :ivar str name: Name of the Platform
    :ivar str description: Description of the Platform
    :ivar TestProject testproject: Parent Testproject
    :ivar TestPlan testplan: Parent TestPlan
    """

    def __init__(self, builder, *args, **kwargs):
        super(Platform, self).__init__(builder, *args, **kwargs)
        self.__name = builder.name
        self.__description = builder.description
        self.__parent_testproject = builder.testproject
        self.__parent_testplan = builder.testplan

    def __str__(self):
        return "{}: {}".format(self.__class__.__name__, self.name)

    @staticmethod
    def builder(**api_data):
        """Generate a new PlatformBuilder

        :param api_data: Raw API data
        :rtype: PlatformBuilder
        """
        return PlatformBuilder(**api_data)

    @property
    def name(self):
        return self.__name

    @property
    def description(self):
        return self.__description

    @property
    def testproject(self):
        return self.__parent_testproject

    @property
    def testplan(self):
        return self.__parent_testplan
