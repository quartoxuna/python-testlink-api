#!/usr/bin/env python
# -*- coding: utf-8 -*-
# pylint: disable=C0103

"""
@author: Kai Borowiak
@summary: TestSuite for testlink.objects.TestRequirement
"""

# IMPORTS
import unittest

from .. import randput

from testlink.objects.tl_req import Requirement

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
        string = str(obj)
        self.assertEqual(string, "Requirement %s: %s" % (doc_id, name))
