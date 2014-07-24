#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@author: Kai Borowiak
@summary: Testlink API Wrapper
"""

# IMPORTS
import logging
# Define logger before importing the rest
log = logging.getLogger('testlink')
# Backwards compatibility for Python < 2.7
try:
	from logging import NullHandler
	log.addHandler(NullHandler())
except ImportError:
	pass

# EXPORTS
from .exceptions import *
from .enums import *
#from .parsers import *
from .server import *
from .api import *
from .objects import *

__all__ = [\
		# exceptions.py
		'NotSupported','APIError','InvalidURL', \

		# enums.py
		'ExecutionType','ImportanceLevel','DuplicateStrategy','CustomFieldDetails','APIType', \

		# server.py
		'TestlinkXMLRPCServer', \

		# xml_rpc_api.py
		'Testlink_XML_RPC_API', \

		# objects.py
		'Testlink','TestProject','TestSuite','TestCase','TestPlan','Build','Platform' \
	]
