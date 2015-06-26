#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@author: Kai Borowiak
@summary: TestSuite for testlink.objects.TestRequirementSpecification
"""

# IMPORTS
import unittest
import inspect

from .. import randint, randput, randict

from testlink.objects import RequirementSpecification

class RequirementSpecificationTests(unittest.TestCase):

	def __init__(self,*args,**kwargs):
		super(RequirementSpecificationTests,self).__init__(*args,**kwargs)
		self._testMethodDoc = "RequirementSpecification: " + self._testMethodDoc

	def test__str__(self):
		"""String representation"""
		doc_id = randput()
		name = randput()
		obj = RequirementSpecification(doc_id=doc_id,title=name)
		string = str(obj)
		self.assertEqual(string, "Requirement Specification %s: %s" % (doc_id,name))
