#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@author: Kai Borowiak
@summary: TestSuite for testlink.objects.TestRequirementSpecification
"""

# IMPORTS
import random
import string
import unittest
from testlink.objects.tl_reqspec import RequirementSpecification


def randput(length=10): return "".join([random.choice(string.letters) for _ in xrange(random.randint(1, length))])


class RequirementSpecificationTests(unittest.TestCase):
    """Requirement Specification Object Tests"""

    def __init__(self, *args, **kwargs):
        super(RequirementSpecificationTests, self).__init__(*args, **kwargs)
        self._testMethodDoc = "RequirementSpecification: " + self._testMethodDoc

    def test__str__(self):
        """String representation"""
        doc_id = randput()
        name = randput()
        obj = RequirementSpecification(doc_id=doc_id, title=name)
        _string = str(obj)
        self.assertEqual(_string, "Requirement Specification %s: %s" % (doc_id, name))
