#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@author: Kai Borowiak
@summary: Testlink API Wrapper
"""

import logging
from .server import *
from .api import *
from .objects import *

# Define logger
log = logging.getLogger('testlink')
# Backwards compatibility for Python < 2.7
try:
	from logging import NullHandler
	log.addHandler(NullHandler())
except ImportError:
	pass

__all__ = [\
		'TestlinkXMLRPCServer',\
		'NotSupported','APIError','Testlink_XML_RPC_API',\
		'ExecutionType','ImportanceLevel','DuplicateStrategy','CustomFieldDetails',\
		'Testlink','TestProject','TestSuite','TestCase','TestPlan','Build','Platform'\
	]
