#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@author: Kai Borowiak
@summary: TestCase for testlink.objects.TestCase.Step
"""

# IMPORTS
import random
import string
import unittest
from testlink.objects.tl_step import Step


def randput(length=10): return "".join([random.choice(string.letters) for _ in xrange(random.randint(1, length))])


def randint(length=10): return int("".join([random.choice(string.digits) for _ in xrange(random.randint(1, length))]))


class StepTests(unittest.TestCase):
    """Step Object Tests"""

    def __init__(self, *args, **kwargs):
        super(StepTests, self).__init__(*args, **kwargs)
        self._testMethodDoc = "TestCase.Step: " + self._testMethodDoc

    def test__str__(self):
        """String representation"""
        number = randint()
        actions = randput()
        results = randput()

        obj = Step(step_number=number, actions=actions, expected_results=results)
        _string = str(obj)
        self.assertEqual(_string, "Step %d:\n%s\n%s" % (number, actions, results))
