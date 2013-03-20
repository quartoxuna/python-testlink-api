#!/usr/bin/env python

from setuptools import setup

setup(
	name="testlink-api",
	version="0.1",
	description="Testlink API Wrapper library",
	author="Kai Borowiak",
	packages=['testlink'],
	dependency_links=[
		'http://192.168.2.20/basket/',
	],
)
