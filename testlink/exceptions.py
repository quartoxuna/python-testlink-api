#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Exceptions
==========
:module: testlink.exceptions
"""


class NotSupported(Exception):
    """Method is not supported within the Testlink version"""
    def __init__(self, fn_name):
        Exception.__init__(self, fn_name)
        self.error_msg = fn_name


class APIError(Exception):
    """Testlink API returns an error struct"""
    def __init__(self, code='-1', message=''):
        msg = unicode(message).encode("utf-8")
        Exception.__init__(self, str(msg))
        if not str(code).isdigit():
            code = -1
        self.error_code = int(code)
        self.error_msg = str(msg)

    def __str__(self):
        return "%d - %s" % (self.error_code, self.error_msg)


class ConnectionError(Exception):
    """Connection to the server cannot be stablished"""
    pass
