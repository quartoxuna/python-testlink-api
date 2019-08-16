# IMPORTS
import abc
import functools
from enum import Enum

#
# CONSTANTS
#
class APIType(Enum):
    XMLRPC = "XML-RPC"
    REST = "REST"


class TestlinkAPIBuilder(object):
    """General Testlink API Builder

    :param APIType api_type: The type of the Testlink API
    :param str devkey: Global developer key
    """

    __metaclass__ = abc.ABCMeta

    def __init__(self, url=None, devkey=None):
        super(TestlinkAPIBuilder, self).__init__()
        self.url = url
        self.devkey = devkey

    def connect_to(self, url):
        """Set the URL of the Testlink API
        :type url: str"""
        self.url = url
        return self

    def using_devkey(self, devkey):
        """Set the global developer key
        :type devkey: str"""
        return self

    @abc.abstractmethod
    def build(self):
        """Return Testlink API instance"""
        pass


class TestlinkAPI(object):
    """Abstract Testlink API Interface

    :param str version: Version of the current API
    :param str devkey: Global developer key
    """

    __metaclass__ = abc.ABCMeta

    def __init__(self, devkey = None, *args, **kwargs):
        super(TestlinkAPI, self).__init__()
        self.__global_devkey = devkey

    @staticmethod
    def builder(api_type=APIType.XMLRPC):
        builder_cls = None
        if api_type == APIType.XMLRPC:
            from xmlrpc import TestlinkXMLRPCAPIBuilder as builder_cls
        return builder_cls()

    @property
    def devkey(self):
        return self.__global_devkey

    @devkey.setter
    def devkey(self, devkey):
        if self.__global_devkey:
            raise RuntimeError("Cannot change current Developer Key on runtime (current: '{}')".format(self.__global_devkey))
        self.__global_devkey = devkey

    #
    # Interface definition
    #

    @abc.abstractmethod
    def __str__(self):
        """Proper string representation of the current Testlink API
        :rtype: str"""
        pass

    @abc.abstractproperty
    def version(self):
        """Currrent API Version
        :rtype: str"""
        pass

    @abc.abstractmethod
    def query(self, *args, **kwargs):
        """Send a query to interfacing Testlink API"""
        pass
