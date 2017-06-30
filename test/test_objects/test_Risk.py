#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@author: Kai Borowiak
@summary: TestSuite for testlink.objects.Risk
"""

# IMPORTS
import random
import string
import unittest
from testlink.objects.tl_risk import Risk


def randput(length=10): return "".join([random.choice(string.letters) for _ in xrange(random.randint(1, length))])


class RiskTests(unittest.TestCase):
    """Risk Object Tests"""

    def __init__(self, *args, **kwargs):
        super(RiskTests, self).__init__(*args, **kwargs)
        self._testMethodDoc = "Risk: " + self._testMethodDoc

    def test__str__(self):
        """String representation"""
        risk_id = randput()
        name = randput()
        obj = Risk(risk_doc_id=risk_id, name=name)
        _string = str(obj)
        self.assertEqual(_string, "Risk %s: %s" % (risk_id, name))
