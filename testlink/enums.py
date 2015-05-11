
#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@author: Kai Borowiak
@summary: Common Enumerations
"""

class ExecutionType:
	"""Enumeration for execution types
	@cvar MANUAL: Manual execution
	@type MANUAL: int
	@cvar AUTOMATIC: Automamtic execution
	@type AUTOMATIC: int
	"""
	MANUAL = 1
	AUTOMATIC = 2

class ImportanceLevel:
	"""Enumeration for importance levels
	@cvar HIGH: High Importance
	@type HIGH: int
	@cvar MEDIUM: Medium Importance
	@type MEDIUM: int
	@cvar LOW: Low Importance
	@type LOW: int
	"""
	HIGH = 3
	MEDIUM = 2
	LOW = 1

class UrgencyLevel:
	"""Enumeration for urgency levels
	@cvar HIGH: High Urgency
	@type HIGH: int
	@cvar MEDIUM: Medium Urgency
	@type MEDIUM: int
	@cvar LOW: Low Urgency
	@type LOW: int
	"""
	HIGH = 3
	MEDIUM = 2
	LOW = 1

class DuplicateStrategy:
	"""Enumeration for duplicate handling strategies
	@cvar BLOCK: Block on duplicate
	@type BLOCK: str
	"""
	NEW_VERSION = 'create_new_version'
	GENERATE_NEW = 'generate_new'
	BLOCK = 'block'

class CustomFieldDetails:
	"""Enumeration for custom field detail options
	@cvar VALUE_ONLY: Only the value of the custom field
	@type VALUE_ONLY: str
	"""
	VALUE_ONLY = 'value'


class APIType:
	"""APIType enum
	@cvar XML_RPC: Use XML-RPC API
	@type XML_RPC: int
	@cvar REST: Use REST API
	@type REST: int
	"""
	XML_RPC = "XML-RPC"
	REST = "REST"

class TestcaseStatus:
	"""TestlinkStatus enum
	@cvar DRAFT: Draft status
	@type DRAFT: int
	@cvar READY_FOR_REVIEW: Ready for review status
	@type READY_FOR_REVIEW: int
	@cvar REVIEW_IN_PROGRESS: Review in progress status
	@type REVIEW_IN_PROGRESS: int
	@cvar REWORK: Rework status
	@type REWORK: int
	@cvar OBSOLETE: Obsolete status
	@type OBSOLETE: int
	@cvar FUTURE: Future status
	@type FUTURE: int
	@cvar FINAL: Final status
	@type FINAL: int
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
	@type SECTION: int
	@cvar USER: User Requirement Specification
	@type USER: int
	@cvar SYSTEM: System Requirement Specification
	@type SYSTEM: int
	"""
	SECTION = 1
	USER = 2
	SYSTEM = 3

class RequirementStatus:
	"""Requirement Status enum
	@cvar VALID: Valid
	@type VALID: str
	@cvar NOT_TESTABLE: Not testable
	@type NON_TESTABLE: str
	@cvar DRAFT: Draft
	@type DRAFT: str
	@cvar REVIEW: Review
	@type REVIEW: str
	@cvar REWORK: Rework
	@type REWORK: str
	@cvar FINISH: Finish
	@type FINISH: str
	@cvar IMPLEMENTED: Implemented
	@type IMPLEMENTED: str
	@cvar OBSOLETE: Obsolete
	@type OBSOLETE: str
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
	@type INFO: int
	@cvar FEATURE: Feature
	@type FEATURE: int
	@cvar USE_CASE: Use Case
	@type USE_CASE: int
	@cvar INTERFACE: Interace
	@type INTERFACE: int
	@cvar NON_FUNC: Non functional
	@type NON_FUNC: int
	@cvar CONSTRAIN: Constrain
	@type CONSTRAIN: int
	@cvar SYSTEM_FUNC: System function
	@type SYSTEM_FUNC: int
	"""
	INFO = 1
	FEATURE = 2
	USE_CASE = 3
	INTERFACE = 4
	NON_FUNC = 5
	CONSTRAIN = 6
	SYSTEM_FUNC = 7
