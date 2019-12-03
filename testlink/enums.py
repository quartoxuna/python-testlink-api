#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Enumerations
============
:module: testlink.enums

This module defines common unsed enumerations, which are used
throughout the whole implementation, but can also be very handy
when using the objects provided by the wrapper.

.. autoclass:: DuplicateStrategy

.. autoclass:: ExecutionStatus

.. autoclass:: ExecutionType

.. autoclass:: ImportanceLevel

.. autoclass:: TestCaseStatus

.. autoclass:: UrgencyLevel
"""

# IMPORTS
import enum

class APIType(enum.Enum):
    """Type of Testlink API

    .. deprecated:: 0.52.0
    """
    XML_RPC = 'XML-RPC'
    REST = 'REST'

class CustomFieldDetails(enum.Enum):
    VALUE_ONLY = 'value'

class DuplicateStrategy(enum.Enum):
    NEW_VERSION = 'create_new_version'
    GENERATE_NEW = 'generate_new'
    BLOCK = 'block'

class ExecutionStatus(enum.Enum):
    NOT_RUN = 'n'
    PASSED = 'p'
    FAILED = 'f'
    BLOCKED = 'b'

class ExecutionType(enum.IntEnum):
    MANUAL = 1
    AUTOMATIC = 2

class ImportanceLevel(enum.IntEnum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3

class TestCaseStatus(enum.IntEnum):
    DRAFT = 1
    READY_FOR_REVIEW = 2
    REVIEW_IN_PROGRESS = 3
    REWORK = 4
    OBSOLETE = 5
    FUTURE = 6
    FINAL = 7

class UrgencyLevel(enum.IntEnum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3
