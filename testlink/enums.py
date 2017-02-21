#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Enumerations
============
:module: testlink.enums

This module defines common unsed enumerations, which are used
throughout the whole implementation, but can also be very handy
when using the objects provided by the wrapper.

.. py:data:: EXECUTION_TYPE

   Execution Type of a TestCase or TestCase Step

   .. py:attribute:: MANUAL
   .. py:attribute:: AUTOMATIC


.. py:data:: IMPORTANCE_LEVEL

   Importance Level of a TestCase. The Importance Level is visible
   within the Test Specification View.

   .. py:attribute:: HIGH
   .. py:attribute:: MEDIUM
   .. py:attribute:: LOW


.. py:data:: URGENCY_LEVEL

   Urgency Level of a TestCase. The Urgency Level is visible
   within the Test Execution View.

   .. py:attribute:: HIGH
   .. py:attribute:: MEDIUM
   .. py:attribute:: LOW


.. py:data:: DUPLICATE_STRATEGY

   Duplicate Strategy to be used in case of a duplicated name.

   .. py:attribute:: NEW_VERSION

      Create new version of a TestCase

   .. py:attribute:: GENERATE_NEW

      Create a complete new TestCase. In case of a duplicated name,
      a timestamp will be added to the name of the newly created TestCase.

   .. py:attribute:: BLOCK

      Blocks the creation of new objects in case of a duplicated name.


.. py:data:: CUSTOM_FIELD_DETAILS

   Grade of details when retrieving values of CustomFields.

   .. py:attribute:: VALUE_ONLY

      Retrieve only the value of the CustomField. Keep in mind that all data
      that is returned by the API is converted to :func:`python:str`.


.. py:data:: API_TYPE

   Type of API which is used.

   .. py:attribute:: XML_RPC

      Original XML-RPC API

   .. py:attribute:: REST

      Experimental REST API


.. py:data:: TESTCASE_STATUS

   Status of a TestCase.

   .. py:attribute:: DRAFT
   .. py:attribute:: READY_FOR_REVIEW
   .. py:attribute:: REVIEW_IN_PROGRESS
   .. py:attribute:: REWORK
   .. py:attribute:: OBSOLETE
   .. py:attribute:: FUTURE
   .. py:attribute:: FINAL


.. py:data:: REQSPEC_TYPE

   Type of a Requirement Specification.

   .. py:attribute:: SECTION
   .. py:attribute:: USER
   .. py:attribute:: SYSTEM


.. py:data:: REQ_STATUS

   Status of a Requirement.

   .. py:attribute:: VALID
   .. py:attribute:: NOT_TESTABLE
   .. py:attribute:: DRAFT
   .. py:attribute:: REVIEW
   .. py:attribute:: REWORK
   .. py:attribute:: FINISH
   .. py:attribute:: IMPLEMENTED
   .. py:attribute:: OBSOLETE


.. py:data:: REQ_TYPE

   Type of a Requirement.

   .. py:attribute:: INFO
   .. py:attribute:: FEATURE
   .. py:attribute:: USE_CASE
   .. py:attribute:: INTERFACE
   .. py:attribute:: NON_FUNC
   .. py:attribute:: CONSTRAIN
   .. py:attribute:: SYSTEM_FUNC


.. py:data:: EXECUTION_STATUS

   Possible Execution Results.

   .. py:attribute:: NOT_RUN
   .. py:attribute:: PASSED
   .. py:attribute:: FAILED
   .. py:attribute:: BLOCKED

"""

# IMPORTS
from collections import namedtuple as nt

EXECUTION_TYPE = nt("ExecutionType",\
                   ("MANUAL", "AUTOMATIC"))\
                   (MANUAL=1, AUTOMATIC=2)

IMPORTANCE_LEVEL = nt("ImportanceLevel",\
                     ("HIGH", "MEDIUM", "LOW"))\
                     (HIGH=3, MEDIUM=2, LOW=1)

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
