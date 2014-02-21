#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@author: Kai Borowiak
@summary: Testlink API Wrapper
"""

# ENABLE MODULE WIDE LOGGING
import logging
log = logging.getLogger('testlink')
try:
	from logging import NullHandler
	log.addHandler(NullHandler())
except ImportError:
	pass

# EXPORTS
from api import TestlinkAPI
from api import InvalidURI, NotSupported, APIError
from objects import Testlink
from server import TestlinkXMLRPCServer

__all__ = ['TestlinkAPI','Testlink','TestlinkXMLRPCServer',\
		'InvalidURI','NotSupported','APIError']
