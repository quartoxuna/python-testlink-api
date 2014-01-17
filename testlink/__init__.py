#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@author: Kai Borowiak
@summary: Testlink API Wrapper
"""

import logging
log = logging.getLogger('testlink-api')

# Add NullHandler if available to avoid
# warnings if user has not configured logging
try:
	from logging import NullHandler
	log.addHandler(NullHandler())
except ImportError:
	pass

from api import TestlinkAPI
from api import InvalidURI, NotSupported, APIError
from objects import Testlink
from server import TestlinkXMLRPCServer

__all__ = ['TestlinkAPI','Testlink','TestlinkXMLRPCServer',\
		'InvalidURI','NotSupported','APIError']
