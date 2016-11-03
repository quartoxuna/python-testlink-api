#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Setup Script for python-testlink-api
"""

from setuptools import setup
import testlink

setup(\
  name='python-testlink-api',\
  version=testlink.__version__,\
  description='Testlink API Wrapper Library',\
  author='Kai Borowiak',\
  author_email='info@quartoxuna.com',\
  url='https://github.com/quartoxuna/python-testlink-api',\
  packages=['testlink'],\
  keywords='testlink api xmlrpc python',\

  tests_require=['mock'],\
  test_suite='test'\
)
