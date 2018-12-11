#!/usr/bin/env python
# -*- coding: utf-8 -*-

# IMPORTS
import os
from setuptools import setup
execfile(os.path.relpath(os.path.join('testlink', 'version.py')))

setup(
    # Summary
    name='python-testlink-api',
    version=__version__,
    description='Testlink API Wrapper Library',

    author='Kai Borowiak',
    author_email='info@quartoxuna.com',
    url='https://github.com/quartoxuna/python-testlink-api',

    # Package Contents
    packages=['testlink','testlink.objects'],
    keywords='testlink api xmlrpc python',

    # Unit Tests
    tests_require=['mock'],
    test_suite='test'
)
