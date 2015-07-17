
#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@author: Kai Borowiak
@summary: Common Enumerations
"""

class ExecutionType:
    """Enumeration for execution types
    	@cvar MANUAL: Manual execution


    """
	MANUAL = 1
	AUTOMATIC = 2

class ImportanceLevel:
    """Enumeration for importance levels
    	@cvar HIGH: High Importance


    """
	HIGH = 3
	MEDIUM = 2
	LOW = 1

class UrgencyLevel:
    """Enumeration for urgency levels
    	@cvar HIGH: High Urgency


    """
	HIGH = 3
	MEDIUM = 2
	LOW = 1

class DuplicateStrategy:
    """Enumeration for duplicate handling strategies
    	@cvar BLOCK: Block on duplicate


    """
	NEW_VERSION = 'create_new_version'
	GENERATE_NEW = 'generate_new'
	BLOCK = 'block'

class CustomFieldDetails:
    """Enumeration for custom field detail options
    	@cvar VALUE_ONLY: Only the value of the custom field


    """
	VALUE_ONLY = 'value'


class APIType:
    """APIType enum
    	@cvar XML_RPC: Use XML-RPC API


    """
	XML_RPC = "XML-RPC"
	REST = "REST"

class TestcaseStatus:
    """TestlinkStatus enum
    	@cvar DRAFT: Draft status


    """
	DRAFT = 1
	READY_FOR_REVIEW = 2
	REVIEW_IN_PROGRESS = 3
	REWORK = 4
	OBSOLETE = 5
	FUTURE = 6
	FINAL = 7

class RequirementSpecificationType:
    """Requirement Specification Type enum
    	@cvar SECTION: Section


    """
	SECTION = 1
	USER = 2
	SYSTEM = 3

class RequirementStatus:
    """Requirement Status enum
    	@cvar VALID: Valid


    """
	VALID = 'V'
	NOT_TESTABLE = 'N'
	DRAFT = 'D'
	REVIEW = 'R'
	REWORK = 'W'
	FINISH = 'F'
	IMPLEMENTED = 'I'
	OBSOLETE = 'O'

class RequirementType:
    """Requirement Type enum
    	@cvar INFO: Info


    """
	INFO = 1
	FEATURE = 2
	USE_CASE = 3
	INTERFACE = 4
	NON_FUNC = 5
	CONSTRAIN = 6
	SYSTEM_FUNC = 7
