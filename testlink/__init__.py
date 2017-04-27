#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@author: Kai Borowiak
@summary: Testlink API Wrapper
"""

__version__ = '0.39.0'

# EXPORTS
from testlink.objects import Testlink
from testlink.objects import TestlinkObject
from testlink.objects import TestProject
from testlink.objects import TestSuite
from testlink.objects import TestCase
from testlink.objects import TestPlan
from testlink.objects import Build
from testlink.objects import Platform
from testlink.objects import RequirementSpecification
from testlink.objects import Requirement
from testlink.objects import Risk

from testlink.exceptions import APIError
from testlink.exceptions import NotSupported
