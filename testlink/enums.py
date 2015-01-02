
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
