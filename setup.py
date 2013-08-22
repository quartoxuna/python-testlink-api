#!/usr/bin/env python

from setuptools import setup

setup(
	name="testlink_api",
	version="0.1",
	description="Testlink API Wrapper library",
	author="Kai Borowiak",
	author_email="kai.borowiak@secunet.com",
	packages=['testlink'],
	long_description="""\
	Provides classes and methods for
	interfacing with Testlink XML-RPC API.
	""",
	classifiers=[
		"License :: OSI Approved :: GNU General Public License (GPL)",
		"Programming Language :: Python",
		"Development Status :: 5 - Production/Stable",
		"Intended Audience :: Developers",
	],
	keywords='testlink api xml rpc python',
	license='GPL',
)
