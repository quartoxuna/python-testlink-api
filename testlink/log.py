#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@author: Kai Borowiak
@summary: Logging initialization
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

