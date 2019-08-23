
"""
.. autoclass:: TestlinkObject
   :members:

.. autoclass:: TestlinkObjectBuilder
   :members:
"""


class TestlinkObjectFromAPIBuilder(object):
    """Testlink Object Builder for raw Testlink API data

    :ivar int _id: Internal Testlink ID of the object
    :ivar Testlink testlink: Parent Testlink instance
    """
    # pylint: disable=too-few-public-methods

    def __init__(self, *args, **kwargs):
        self.testlink_id = kwargs.pop('id', None)
        self.testlink = kwargs.pop('parent_testlink', None)
        super(TestlinkObjectFromAPIBuilder, self).__init__(*args, **kwargs)

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

    def with_id(self, testlink_id):
        """Set the internal ID of the Testlink Object

        :param int testlink_id: Internal Testlink ID
        :rtype: TestlinkObjectBuilder
        """
        self.testlink_id = testlink_id
        return self

    def from_testlink(self, testlink):
        """Set the parent Testlink instance

        :param Testlink testlink: Parent Testlink instance
        :rtype: TestlinkObjectBuilder
        """
        self.testlink = testlink
        return self


class TestlinkObject(object):
    """General Testlink Object

    :arg int id: Internal Testlink ID
    :arg Testlink testlink: Parent Testlink instance
    """

    DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
    """Default timestamp format for Testlink Objects"""

    def __init__(self, builder, *args, **kwargs):
        super(TestlinkObject, self).__init__(*args, **kwargs)
        self.__testlink_id = builder.testlink_id
        self.__parent_testlink = builder.testlink

    @staticmethod
    def builder(**api_data):
        """Generate a new TestlinkObjectBuilder

        :param api_data: Raw API data
        :rtype: TestlinkObjectBuilder
        """
        return TestlinkObjectBuilder(**api_data)

    def __str__(self):
        return "{}: {}".format(self.__class__.__name__, self.id)

    def __id__(self):
        return self.__testlink_id

    def __eq__(self, other):
        return self.id == other.id

    # pylint: disable=invalid-name
    @property
    def id(self):
        """Internal Testlink ID

        :rtype: int
        """
        return self.__testlink_id

    @property
    def testlink(self):
        """Parent Testlink instance

        :rtype: Testlink
        """
        return self.__parent_testlink
