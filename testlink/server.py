#!/usr/bin/env python
# -*- coding: utf-8 -*-
# pylint: disable=C0301
# pylint: disable=R0904
# pylint: disable=R0901

"""
@author: Kai Borowiak
@summary: Testlink conform automation server.
"""

# IMPORTS
from threading import Thread
from SimpleXMLRPCServer import SimpleXMLRPCServer
from testlink.log import LOGGER as log

class TestlinkXMLRPCServer(SimpleXMLRPCServer, Thread):
    """Testlink conform XML-RPC automation server"""

    def __init__(self, callback, host='127.0.0.1', port=8080, verbose=False):
        """Initializes the Server
        @param callback: Method to be executed if server is triggerd
        @type callback: method
        @param host: The address of the Server
        @type host: str
        @param port: The port of the Server
        @type port: int
        @param verbose: Log HTTP requests
        @type verbose: bool
        """
        SimpleXMLRPCServer.__init__(self, (host, port), logRequests=verbose)
        Thread.__init__(self)
        self.register_introspection_functions()
        start_msg = "Starting Testlink compatible XML-RPC Server at http://%s:%d/" % (str(host), int(port))
        log.info(start_msg)
        register_msg = "Registering '%s' as callback" % str(callback.__name__)
        log.info(register_msg)
        self.register_function(callback, "executeTestCase")
        self.start()

    def run(self):
        self.handle_request()
