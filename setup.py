#!/usr/bin/env python

from distutils.core import setup

setup(
	name='python-testlink_api_wrapper',
	version='0.9',
	description='Testlink API Wrapper library',
	author='Kai Borowiak',
	author_email='kai.borowiak@secunet.com',
	packages=['testlink'],
	keywords='testlink api xmlrpc python',
	license='GPL',
	requires=['bs4'],
)
