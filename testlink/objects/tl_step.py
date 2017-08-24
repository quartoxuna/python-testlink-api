#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""TestCase Step Object"""

# IMPORTS
from testlink.enums import EXECUTION_TYPE


class Step(object):
    """Testlink TestCase Step representation
    @ivar id: Internal ID of the Step
    @type id: int
    @ivar number: Number of the step
    @type number: int
    @ivar actions: Actions of the step
    @type actions: str
    @ivar execution_type: Type of Execution
    @type execution_type: EXECUTION_TYPE
    @ivar active: Active flag
    @type active: bool
    @ivar results: Expected result of the step
    @type results: str
    """
    def __init__(self, step_number=1, actions="", execution_type=EXECUTION_TYPE.MANUAL, active="0",
                 expected_results="", **kwargs):
        self.id = kwargs.get('id', -1)
        self.step_number = int(step_number)
        self.actions = actions
        self.execution_type = int(execution_type)
        self.active = bool(int(active))
        self.expected_results = expected_results

    def __repr__(self):
        """Returns parsable representation"""
        return str(self.as_dict())

    def as_dict(self):
        """Returns dict representation"""
        res = dict()
        res["step_number"] = self.step_number
        res["actions"] = self.actions
        res["execution_type"] = self.execution_type
        res["active"] = self.active
        res["id"] = self.id
        res["expected_results"] = self.expected_results
        return res

    def __str__(self):
        return "Step %d:\n%s\n%s" % (self.step_number, self.actions, self.expected_results)
