#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@author: Kai Borowiak
@summary: Logging initialization
"""

# IMPORTS
import logging

# Define logger before importing the rest
LOGGER = logging.getLogger('testlink')

try:
    from logging import NullHandler
    LOGGER.addHandler(NullHandler())
except Exception:
    pass
