# IMPORTS
import abc
import functools

from enum import Enum
from pkg_resources import parse_version as Version

from testlink.exceptions import NotSupported

#
# CONSTANTS
#
class APIType(Enum):
    XMLRPC = "XML-RPC"
    REST = "REST"


class TLVersion(object):
    """Testlink Version Checker decorator

    :param pkg_resources.parse_version version: Version to be checked
    :param bool struct: If True, then strict version check is enabled

    :Examples:

        >>> # Default function
        >>> @TLVersion("1.0")
        >>> def function1():
        >>>     pass

        >>> # Function available in Testlink 1.9.11 and higher
        >>> @TLVersion("1.9.11")
        >>> def function2():
        >>>     pass

        >>> # Function ONLY avaialble in Testlink 1.9.11-alpha
        >>> @TLVersion("1.9.11-alpha", strict=1)
        >>> def function3():
        >>>     pass
    """

    def __init__(self, version, strict=False):
        self.version = Version(version)
        self.strict = strict

    def __call__(self, fn):
        @functools.wraps(fn)
        def wrapper(testlink_api, *args, **kwargs):
            if (self.strict and self.version != testlink_api.tl_version)\
            or (self.version > testlink_api.tl_version):
                if self.strict:
                    sign = "=="
                else:
                    sign = ">="
                raise NotSupported("Method '%s' requires Testlink version %s %s but is %s" %
                    (str(fn.__name__), sign, str(self.version), str(testlink_api.tl_version)))
            return fn(testlink_api, *args, **kwargs)
        return wrapper


class TestlinkAPI(object):
    """Abstract Testlink API Interface

    :param str version: Version of the current API
    :param str devkey: Global developer key
    """

    __metaclass__ = abc.ABCMeta

    def __init__(self, *args, **kwargs):
        super(TestlinkAPI, self).__init__()
        self.__global_devkey = None

    @property
    def devkey(self):
        return self.__global_devkeya

    @devkey.setter
    def devkey(self, devkey):
        if self.__global_devkey:
            raise RuntimeError("Cannot change current Developer Key on runtime (current: '{}')".format(self.__global_devkey))
        self.__global_devkey = devkey

    @staticmethod
    def create(url, api_type=APIType.XMLRPC, devkey=None):
        """Factory method for generating a valid Testlink API Interface

        :param str url: URL to Testlink instance
        :param APIType api_type: Type of the API to generate
        :param str devkey: Global developer key to be used
        :rtype TestlinkAPI:
        """
        if api_type == APIType.XMLRPC:
            from xmlrpc import TestlinkXMLRPCAPI as API
        return API

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
