#!/usr/bin/env python
# -*- coding: utf-8 -*-

# IMPORTS
from testlink.objects.tl_object import TestlinkObjectFromAPIBuilder
from testlink.objects.tl_object import TestlinkObjectBuilder
from testlink.objects.tl_object import TestlinkObject


class KeywordFromAPIBuilder(TestlinkObjectFromAPIBuilder):
    """Testlink Keyword Builder from raw Testlink API data

    :ivar str name: The name of the Keyword
    :ivar str description: The description of the Keyword
    :ivar int testcase_id: Internal ID of related TestCase
    """

    def __init__(self, *args, **kwargs):
        self.name = kwargs.pop('keyword', None)
        self.description = kwargs.pop('notes', None)
        self.testcase_id = kwargs.pop('testcase_id', None)
        super(KeywordFromAPIBuilder, self).__init__(*args, **kwargs)

        # Fix types
        if self.testcase_id is not None:
            self.testcase_id = int(self.testcase_id)


class KeywordBuilder(TestlinkObjectBuilder,
                     KeywordFromAPIBuilder):
    """General Keyword Builder"""

    def __init__(self, *args, **kwargs):
        super(KeywordBuilder, self).__init__(*args, **kwargs)

    def with_name(self, name):
        """Set the name of the Keyword

        :param str name: The name of the Keyword
        :rtype: KeywordBuilder
        """
        self.name = name
        return self

    def with_description(self, description):
        """Set the description of the Keyword

        :param str description: The description of the Keyword
        :rtype: KeywordBuilder
        """
        self.description = description
        return self

    def with_testcase_id(self, testcase_id):
        """Set the a related testcase ID for the Keyword

        :param int testcase_id: Internal ID of related TestCase
        :rtype: KeywordBuilder

        .. todo:: Needed?
        """
        self.testcase_id = testcase_id
        return self

    def build(self):
        """Generate a new Keyword"""
        # Call sanity checks of parent class
        super(KeywordBuilder, self).build()

        # Sanity checks
        assert self.name is not None, "No Keyword name defined"

        return Keyword(self)


class Keyword(TestlinkObject):
    """Testlink Keyword

    :ivar str name: Name of the Keyword
    :ivar str description: Description of the Keyword
    :ivar int testcase_id: Releated TestCase ID
    """

    def __init__(self, builder, *args, **kwargs):
        super(Keyword, self).__init__(builder, *args, **kwargs)
        self.__name = builder.name
        self.__description = builder.description
        self.__testcase_id = builder.testcase_id

    def __str__(self):
        return self.__name

    def __eq__(self, other):
        if isinstance(other, basestring):
            return self.name == other
        return super(Keyword, self).__eq__(other)

    @staticmethod
    def builder(**api_data):
        """Generate new KeywordBuilder

        :param api_data: Raw API data
        :rtype: KeywordBuilder
        """
        return KeywordBuilder(**api_data)

    @property
    def name(self):
        return self.__name

    @property
    def description(self):
        return self.__description

    @property
    def testcase_id(self):
        return self.__testcase_id
