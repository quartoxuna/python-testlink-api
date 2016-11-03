Enumerations
============

The Python Testlink API provides several enumerations for common used constants

.. _api-type:

API related
-----------

.. py:data:: API_TYPE

   Defines the type of API to use.

   .. py:data:: XML_RPC
   .. py:data:: REST

Unrelated
---------

.. py:data:: DUPLICATE_STRATEGY

   Possible strategies to handle a duplicate entry.

   .. py:data:: NEW_VERSION

       Creates a new Version

   .. py:data:: GENERATE_NEW

       Explicitly create a new entity

   .. py:data:: BLOCK

       Block generation

.. py:data:: CUSTOM_FIELD_DETAILS

   Defines which data of a custom field should be returned.

   .. py:data:: VALUE_ONLY

       Return only the value of the Custom Field


Testcase related
----------------

.. py:data:: EXECUTION_TYPE

   Possible execution type of Testcases.

   .. py:data:: MANUAL = 1
   .. py:data:: AUTOMATIC = 2


.. py:data:: IMPORTANCE_LEVEL

   Possible importance levels of Testcases.

   .. py:data:: HIGH = 3
   .. py:data:: MEDIUM = 2
   .. py:data:: LOW = 1


.. py:data:: URGENCY_LEVEL

   Possible urgency levels of a Testcase which is associated with a Testplan.

   .. py:data:: HIGH = 3
   .. py:data:: MEDIUM = 2
   .. py:data:: LOW = 1


.. py:data:: TESTCASE_STATUS

   Defines the specification status of a Testcase.
   .. versionadded:: Testlink 1.9.8

   .. py:data:: DRAFT = 1
   .. py:data:: READY_FOR_REVIEW = 2
   .. py:data:: REVIEW_IN_PROGRESS = 3
   .. py:data:: REWORK = 4
   .. py:data:: OBSOELETE = 5
   .. py:data:: FUTURE = 6
   .. py:data:: FINAL = 7

Requirement related
-------------------

.. py:data:: REQSPEC_TYPE

   Defines the type of a Requirement Specification
   .. versionadded:: Testlink 1.9.8

   .. py:data:: SECTION = 1
   .. py:data:: USER = 2
   .. py:data:: SYSTEM = 3

.. py:data:: REQ_STATUS

   Defines the status for a Requirement
   .. versionadded:: Testlink 1.9.8

   .. py:data:: VALID = 'V'
   .. py:data:: NOT_TESTABLE = 'N'
   .. py:data:: DRAFT = 'D'
   .. py:data:: REVIEW = 'R'
   .. py:data:: REWORK = 'W'
   .. py:data:: FINISH = 'F'
   .. py:data:: IMPLEMENTED = 'I'
   .. py:data:: OBSOLETE = 'O'

.. py:data:: REQ_TYPE

   Defines the type of a Requirement
   .. versionadded:: Testlink 1.9.8

   .. py:data:: INFO = 1
   .. py:data:: FUTURE = 2
   .. py:data:: USE_CASE = 3
   .. py:data:: INTERFACE = 4
   .. py:data:: NON_FUNC = 5
   .. py:data:: CONSTRAIN = 6
   .. py:data:: SYSTEM_FUNC = 7

