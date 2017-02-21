#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Enumerations
==============

Within the *testlink.enums* module there are several commonly used
enumerations. They are defined as :func:`collections.namedtuple`.
"""


# IMPORTS
from collections import namedtuple as nt

EXECUTION_TYPE = nt("ExecutionType",\
                   ("MANUAL", "AUTOMATIC"))\
                   (MANUAL=1, AUTOMATIC=2)
"""Execution Type of a TestCase or TestCase Step.

  .. py:attribute:: MANUAL
  .. py:attribute:: AUTOMATIC

"""

IMPORTANCE_LEVEL = nt("ImportanceLevel",\
                     ("HIGH", "MEDIUM", "LOW"))\
                     (HIGH=3, MEDIUM=2, LOW=1)
"""Importance Level of a TestCase. The Importance Level is
visible on Test Specification View.

  .. py:attribute:: HIGH
  .. py:attribute:: MEDIUM
  .. py:attribute:: LOW

"""

URGENCY_LEVEL = nt("UrgencyLeveL",\
                  ("HIGH", "MEDIUM", "LOW"))\
                  (HIGH=3, MEDIUM=2, LOW=1)
"""Urgency Level of a TestCase. The Urgency Level is
visible on Test Execution View.

  .. py:attribute:: HIGH
  .. py:attribute:: MEDIUM
  .. py:attribute:: LOW

"""

DUPLICATE_STRATEGY = nt("DuplicateStrategy",\
                       ("NEW_VERSION", "GENERATE_NEW", "BLOCK"))\
                       (NEW_VERSION='create_new_version',\
                        GENERATE_NEW='generate_new',\
                        BLOCK='block')
"""Duplicate Strategy to use when generating new objects
within Testlink e.g. TestCase.

  .. py:attribute:: NEW_VERSION

  Creates a complete new version of a TestCase

  .. py:attribute:: GENERATE_NEW

  Creates a new TestCase. The operating can still fail because
  of an already existing TestCase within the same TestSuite.

  .. py:attribute:: BLOCK

  Blocks the creation of new objects if a duplicate is detected.
  This is the default behaviour within Testlink.

"""

CUSTOM_FIELD_DETAILS = nt("CustomFieldDetails",\
                         ("VALUE_ONLY"))\
                         (VALUE_ONLY='value')
"""Defines how detailed information of Custom Fields
should be presented.

  .. py:attribute:: VALUE_ONLY

  Return only the value of a Custom Field. Be aware that the API
  call always returns objects of type :class:`types.StringType`

"""

API_TYPE = nt("APIType",\
             ("XML_RPC", "REST"))\
             (XML_RPC='XML-RPC', REST='REST')
"""Type of currently used API interface.

  .. py:attribute:: XML_RPC

  Use original XML-RPC API.

  .. py:attribute:: REST

  Use new experimental REST API.

"""

TESTCASE_STATUS = nt("TestcaseStatus",\
                    ("DRAFT", "READY_FOR_REVIEW", "REVIEW_IN_PROGRESS",\
                     "REWORK", "OBSOLETE", "FUTURE", "FINAL"))\
                    (DRAFT=1, READY_FOR_REVIEW=2, REVIEW_IN_PROGRESS=3,\
                     REWORK=4, OBSOLETE=5, FUTURE=6, FINAL=7)
"""Status of a TestCase

  .. py:attribute:: DRAFT
  .. py:attribute:: READY_FOR_REVIEW
  .. py:attribute:: REVIEW_IN_PROGRESS
  .. py:attribute:: REWORK
  .. py:attribute:: OBSOLETE
  .. py:attribute:: FUTURE
  .. py:attribute:: FINAL

"""

REQSPEC_TYPE = nt("RequirementSpecificationType",\
                 ("SECTION", "USER", "SYSTEM"))\
                 (SECTION=1, USER=2, SYSTEM=3)
"""Type of a Requirement Specification.

  .. py:attribute:: SECTION
  .. py:attribute:: USER
  .. py:attribute:: SYSTEM

"""


REQ_STATUS = nt("RequirementStatus",\
               ("VALID", "NOT_TESTABLE", "DRAFT", "REVIEW",\
                "REWORK", "FINISH", "IMPLEMENTED", "OBSOLETE"))\
               (VALID='V', NOT_TESTABLE='N', DRAFT='D', REVIEW='R',\
                REWORK='W', FINISH='F', IMPLEMENTED='I', OBSOLETE='O')
"""Status of a Requirement.

  .. py:attribute:: VALID
  .. py:attribute:: NOT_TESTTABLE
  .. py:attribute:: DRAFT
  .. py:attribute:: REVIEW
  .. py:attribute:: REWORK
  .. py:attribute:: FINISH
  .. py:attribute:: IMPLEMENTED
  .. py:attribute:: OBSOLETE

"""

REQ_TYPE = nt("RequirementType",\
             ("INFO", "FEATURE", "USE_CASE", "INTERFACE",\
              "NON_FUNC", "CONSTRAIN", "SYSTEM_FUNC"))\
             (INFO=1, FEATURE=2, USE_CASE=3, INTERFACE=4,\
              NON_FUNC=5, CONSTRAIN=6, SYSTEM_FUNC=7)
"""Type of a Requirement.

  .. py:attribute:: INFO
  .. py:attribute:: FEATURE
  .. py:attribute:: USE_CASE
  .. py:attribute:: INTERFACE
  .. py:attribute:: NON_FUNC
  .. py:attribute:: CONSTRAIN
  .. py:attribute:: SYSTEM_FUNC

"""

EXECUTION_STATUS = nt("ExecutionStatus",\
                      ("NOT_RUN", "PASSED", "FAILED", "BLOCKED"))\
                      (NOT_RUN='n', PASSED='p', FAILED='f', BLOCKED='b')
"""Status of an Execution.

  .. py:attribute:: NOT_RUN
  .. py:attribute:: PASSED
  .. py:attribute:: FAILED
  .. py:attribute:: BLOCKED

"""
