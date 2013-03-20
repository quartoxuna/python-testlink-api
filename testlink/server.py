#!/usr/bin/env python

#               /                ______                __    ___                __
#         -+ydNMM....``         /\__  _\              /\ \__/\_ \    __        /\ \ 
#      `+mMMMMMMM........`      \/_/\ \/    __    ____\ \ ,_\//\ \  /\_\    ___\ \ \/'\ 
#     /mMMMMMMMMM..........`       \ \ \  /'__`\ /',__\\ \ \/ \ \ \ \/\ \ /' _ `\ \ , <
#    oMMMMMMMMMMM...........`       \ \ \/\  __//\__, `\\ \ \_ \_\ \_\ \ \/\ \/\ \ \ \\`\ 
#   :MMMMMMMMMMMM............        \ \_\ \____\/\____/ \ \__\/\____\\ \_\ \_\ \_\ \_\ \_\ 
#   hMMMMMMMMMMMM............`        \/_/\/____/\/___/   \/__/\/____/ \/_/\/_/\/_/\/_/\/_/ 
# ..::::::::::::oMMMMMMMMMMMMo..   ______  ____    ______      __      __
#   ............+MMMMMMMMMMMM-    /\  _  \/\  _`\ /\__  _\    /\ \  __/\ \ 
#    ...........+MMMMMMMMMMMs     \ \ \_\ \ \ \_\ \/_/\ \/    \ \ \/\ \ \ \  _ __    __     _____   _____      __   _ __
#     ..........+MMMMMMMMMMy       \ \  __ \ \ ,__/  \ \ \     \ \ \ \ \ \ \/\`'__\/'__`\  /\ '__`\/\ '__`\  /'__`\/\`'__\ 
#      `........+MMMMMMMMm:         \ \ \/\ \ \ \/    \_\ \__   \ \ \_/ \_\ \ \ \//\ \_\.\_\ \ \_\ \ \ \_\ \/\  __/\ \ \/
#        `......+MMMMMNy:            \ \_\ \_\ \_\    /\_____\   \ `\___x___/\ \_\\ \__/.\_\\ \ ,__/\ \ ,__/\ \____\\ \_\ 
#            ```/ss+/.                \/_/\/_/\/_/    \/_____/    '\/__//__/  \/_/ \/__/\/_/ \ \ \/  \ \ \/  \/____/ \/_/
#               /                                                                             \ \_\   \ \_\ 
#                                                                                              \/_/    \/_/

#
# Epydoc documentation
#

"""
@author: Kai Borowiak
@version: 1.0
@summary: Testlink conform automation server.
"""

#
# IMPORTS
#
import logging
import SimpleXMLRPCServer

#
# ENABLES LOGGING
#
try:
	logging.getLogger(__name__).addHandler(logging.NullHandler())
except AttributeError: pass # Workaround for Python < 2.7

class XMLRPCServer(object):
	"""Automation Server"""

	def __init__(self,addr="127.0.0.1",port=8000,callback=None):
		"""Initializes the Server
		@param addr: The address of the Server
		@type addr: str
		@param port: The port of the Server
		@type port: int
		"""
		logging.getLogger(__name__).info("Starting Testlink XML-RPC Server at http://%s:%d" % (str(addr),int(port)) )
		self.__server = SimpleXMLRPCServer.SimpleXMLRPCServer((addr,port),logRequests=False)
		logging.getLogger(__name__).info("Registering method '%s'" % callback.__name__)
		self.__server.register_function(callback,"executeTestCase")
		logging.getLogger(__name__).info("...idle")
		try:
			self.__server.serve_forever()
		except KeyboardInterrupt:
			logging.getLogger(__name__).info("Exiting.")
