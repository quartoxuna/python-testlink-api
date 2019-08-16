#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@author: Kai Borowiak
@summary: TestSuite for testlink.objects.TestRequirement
"""

# IMPORTS
import random
import string
import unittest
from testlink.objects.tl_req import Requirement


def randput(length=10): return "".join([random.choice(string.letters) for _ in xrange(random.randint(1, length))])


class RequirementTests(unittest.TestCase):
    """Requirement Object Tests"""

    def __init__(self, *args, **kwargs):
        super(RequirementTests, self).__init__(*args, **kwargs)
        self._testMethodDoc = "Requirement: " + self._testMethodDoc

    def test__str__(self):
        """String representation"""
        doc_id = randput()
        name = randput()
        obj = Requirement(req_doc_id=doc_id, title=name)
        _string = str(obj)
        self.assertEqual(_string, "Requirement %s: %s" % (doc_id, name))
