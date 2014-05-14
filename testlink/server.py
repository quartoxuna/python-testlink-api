#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@author: Kai Borowiak
@summary: Testlink conform automation server.
"""

# IMPORTS
import time
from SimpleXMLRPCServer import SimpleXMLRPCServer
from .log import tl_log as log

class TestlinkXMLRPCServer(SimpleXMLRPCServer):
	"""Testlink conform XML-RPC automation server"""

	def __init__(self,callback,host='127.0.0.1',port=8080,verbose=False):
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
		SimpleXMLRPCServer.__init__(self,(host,port),logRequests=verbose)
		self.register_introspection_functions()
		log.info("Starting Testlink compatible XML-RPC Server at http://%s:%d/" % (str(host),int(port)) )
		log.info("Registering '%s' as callback" % str(callback.__name__))
		self.register_function(callback,"executeTestCase")
		try:
			self.serve_forever()
		except KeyboardInterrupt:
			log.warning("Exiting Testlink compatible XML-RPC Server at http://%s:%d/" % (str(host),int(port)) )
