#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@author: Kai Borowiak
@summary: Logging Setup
"""

# IMPORTS
import logging

tl_log = logging.getLogger('testlink')

# Backwards compatability for Python < 2.7
try:
	from logging import NullHandler
	tl_log.addHandler(NullHandler())
except ImportError:
	pass
