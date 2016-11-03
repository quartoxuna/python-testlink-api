#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@author: Kai Borowiak
@summary: TestSuites for Testlink API Wrapper
"""

# IMPORTS
import string
import random
from mock import Mock

__all__ = ["randint", "randput", "randict", "generate", "ServerMock"]

def randint(_min=0, _max=9):
    """Generates a random number within specified range
    @param min: Lower limit
    @type min: int
    @param max: Upper limit
    @type max: int
    @returns: Randomly generated number
    @rtype: int
    """
    return random.randint(_min, _max)

def randput(length=randint(1, 10)):
    """Generates random input with specified length
    @param length: Length of input (Default: 10)
    @type length: int
    @returns: Randomly generated string
    @rtype:str
    """
    return ''.join(\
                    random.choice(\
                        string.ascii_uppercase +\
                        string.ascii_lowercase +\
                        string.digits\
                    ) for _ in range(length)\
                )

def randict(*args):
    """Genrates a dictionary with random values.
    @param args: Keys of the resulting dict
    @type args: list
    @returns: Dictionary with *args as keys and random values
    @rtype: dict
    """
    res = {}
    for arg in args:
        if randint() % 2:
            res[arg] = randput()
        else:
            res[arg] = randint()
    return res

def generate(*args):
    """Returns a generator which yields the specified elements.
    @param args: Elements to yield
    @type args: list
    @rtype: generator
    """
    for arg in args:
        yield arg

class ServerMock(Mock):
    """XML-RPC Server Mock"""
    system = Mock()
    system.listMethods = Mock()

    def __init__(self, *args, **kwargs):
        super(ServerMock, self).__init__(*args, **kwargs)

