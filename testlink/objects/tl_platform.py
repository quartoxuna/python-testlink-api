#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Platform representation"""

# IMPORTS
from testlink.objects.tl_object import TestlinkObjectFromAPIBuilder
from testlink.objects.tl_object import TestlinkObject


class PlatformFromAPIBuilder(TestlinkObjectFromAPIBuilder):
    """Testlink Platform Builder for raw Testlink API data

    :param str name: Name of the Platform
    :param str description: Description of the Platform
    :param TestProject testproject: Parent TestProject
    :param TestPlan testplan: Parent TestPlan
    """

    def __init__(self, *args, **kwargs):
        super(PlatformFromAPIBuilder, self).__init__(*args, **kwargs)
        self.name = kwargs.get('name', None)
        self.description = kwargs.get('notes', None)
        self.testproject = kwargs.get('parent_testproject', None)
        self.testplan = kwargs.get('parent_testplan', None)

    def build(self):
        """Generate new Platform"""
        # Sanity checks
        assert self.name is not None, "No Platform name defined"
        assert self.testproject is not None; "No parent TestProject defined"

        return Platform(
            # Platform
            name=self.name,
            description=self.description,
            parent_testproject=self.testproject,
            parent_testplan=self.testplan,
            # TestlinkObject
            _id=self._id,
            parent_testlink=self.testlink
        )


class PlatformBuilder(PlatformFromAPIBuilder):
    """General Platform Builder"""

    def __init__(self, *args, **kwargs):
        super(PlatformBuilder, self).__init__(*args, **kwargs)

    def with_name(self, name):
        """Set the name of the Platform
        :type name: str"""
        self.name = name
        return self

    def with_description(self, description):
        """Set the description of the Platform
        :type description: str"""
        self.description = description
        return self

    def from_testproject(self, testproject):
        """Set the parent TestProject for the Platform
        :type testproject: TestProject"""
        self.testproject = testproject
        return self

    def from_testplan(self, testplan):
        """Set the parent TestPlan for the Platform
        :type testplan: TestPlan"""
        self.testplan = testplan
        return self


class Platform(TestlinkObject):
    """Testlink Platform

    :param str name: Name of the Platform
    :param str description: Description of the Platform
    :param TestProject testproject: Parent Testproject
    :param TestPlan testplan: Parent TestPlan
    """

    def __init__(self, *args, **kwargs):
        self.__name = kwargs['name']
        self.__description = kwargs['description']
        self.__parent_testproject = kwargs['parent_testproject']
        self.__parent_testplan = kwargs['parent_testplan']

    def __str__(self):
        return "{}: {}".format(self.__class__.__name__, self.name)

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
