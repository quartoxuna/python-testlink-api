#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
.. Sphinx Autodoc

Enumerations
==============

Within the *testlink.enums* module there are several commonly used
enumerations. They are defined as :func:`python:collections.namedtuple`.
"""


# IMPORTS
from collections import namedtuple as nt

EXECUTION_TYPE = nt("ExecutionType",\
                   ("MANUAL", "AUTOMATIC"))\
                   (MANUAL=1, AUTOMATIC=2)
"""
Execution Type of a TestCase.
"""

IMPORTANCE_LEVEL = nt("ImportanceLevel",\
                     ("HIGH", "MEDIUM", "LOW"))\
                     (HIGH=3, MEDIUM=2, LOW=1)

"""
Importance Level of a TestCase. The Importance Level is
visible at Test Specification View.
"""

URGENCY_LEVEL = nt("UrgencyLeveL",\
                  ("HIGH", "MEDIUM", "LOW"))\
                  (HIGH=3, MEDIUM=2, LOW=1)

DUPLICATE_STRATEGY = nt("DuplicateStrategy",\
                       ("NEW_VERSION", "GENERATE_NEW", "BLOCK"))\
                       (NEW_VERSION='create_new_version',\
                        GENERATE_NEW='generate_new',\
                        BLOCK='block')

CUSTOM_FIELD_DETAILS = nt("CustomFieldDetails",\
                         ("VALUE_ONLY"))\
                         (VALUE_ONLY='value')

API_TYPE = nt("APIType",\
             ("XML_RPC", "REST"))\
             (XML_RPC='XML-RPC', REST='REST')

TESTCASE_STATUS = nt("TestcaseStatus",\
                    ("DRAFT", "READY_FOR_REVIEW", "REVIEW_IN_PROGRESS",\
                     "REWORK", "OBSOLETE", "FUTURE", "FINAL"))\
                    (DRAFT=1, READY_FOR_REVIEW=2, REVIEW_IN_PROGRESS=3,\
                     REWORK=4, OBSOLETE=5, FUTURE=6, FINAL=7)

REQSPEC_TYPE = nt("RequirementSpecificationType",\
                 ("SECTION", "USER", "SYSTEM"))\
                 (SECTION=1, USER=2, SYSTEM=3)

REQ_STATUS = nt("RequirementStatus",\
               ("VALID", "NOT_TESTABLE", "DRAFT", "REVIEW",\
                "REWORK", "FINISH", "IMPLEMENTED", "OBSOLETE"))\
               (VALID='V', NOT_TESTABLE='N', DRAFT='D', REVIEW='R',\
                REWORK='W', FINISH='F', IMPLEMENTED='I', OBSOLETE='O')

REQ_TYPE = nt("RequirementType",\
             ("INFO", "FEATURE", "USE_CASE", "INTERFACE",\
              "NON_FUNC", "CONSTRAIN", "SYSTEM_FUNC"))\
             (INFO=1, FEATURE=2, USE_CASE=3, INTERFACE=4,\
              NON_FUNC=5, CONSTRAIN=6, SYSTEM_FUNC=7)

EXECUTION_STATUS = nt("ExecutionStatus",\
                      ("NOT_RUN", "PASSED", "FAILED", "BLOCKED"))\
                      (NOT_RUN='n', PASSED='p', FAILED='f', BLOCKED='b')
