#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Setup Script for python-testlink-api
"""

from setuptools import setup
from testlink import __version__ as VERSION

setup(\
  name='python-testlink-api',\
  version=VERSION,\
  description='Testlink API Wrapper Library',\
  author='Kai Borowiak',\
  author_email='info@quartoxuna.com',\
  url='https://github.com/quartoxuna/python-testlink-api',\
  packages=['testlink','testlink.objects'],\
  keywords='testlink api xmlrpc python',\

  tests_require=['mock'],\
  test_suite='test'\
)
