#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@author: Kai Borowiak
@summary: Testlink API Wrapper
"""

__all__ = ['TestlinkAPI']

__version__ = "1.0"

# Provide default log
import logging
log = logging.getLogger('testlink')

from api import TestlinkAPI
