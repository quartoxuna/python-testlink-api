#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@author: Kai Borowiak
@summary: Testlink API Wrapper
"""

import logging
log = logging.getLogger('testlink')

try:
	log.addHandler(logging.NullHandler())
except Exception:
	pass

from api import TestlinkAPI
from api import InvalidURI, NotSupported, APIError
from objects import Testlink
from server import TestlinkXMLRPCServer

__all__ = ['TestlinkAPI','Testlink','TestlinkXMLRPCServer',\
		'InvalidURI','NotSupported','APIError']
