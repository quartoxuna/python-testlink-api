#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Exceptions
==========
:module: testlink.exceptions

.. exception:: NotSupported

    Raised if method is not supported within the Testlink version

    .. attribute:: error_msg

        The error message

.. exception:: APIError

    Raised if Testlink API return an API error

    .. attribute:: error_msg

        The error message

    .. attribute:: error_code

        The API error code

.. exception:: ConnectionError

    Raised if there was a connection error to the Testlink server
"""

class NotSupported(Exception):
    def __init__(self, fn_name):
        Exception.__init__(self, fn_name)
        self.error_msg = fn_name


class APIError(Exception):
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
    pass
