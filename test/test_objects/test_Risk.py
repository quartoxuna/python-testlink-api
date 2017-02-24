#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@author: Kai Borowiak
@summary: TestSuite for testlink.objects.Risk
"""

# IMPORTS
import unittest

from .. import randput

from testlink.objects.tl_risk import Risk

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
        string = str(obj)
        self.assertEqual(string, "Risk %s: %s" % (risk_id, name))
