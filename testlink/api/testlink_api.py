# IMPORTS
import functools
from pkg_resources import parse_version as Version

from testlink.exceptions import NotSupported

class TLVersion(object):
    """Testlink Version Checker decorator"""

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
