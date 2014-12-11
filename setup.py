#!/usr/bin/env python
# -*- coding: utf-8 -*-

# IMPORTS
import os
from setuptools import find_packages
from setuptools import setup
from setuptools import Command

_PACKAGES_ = find_packages()
_APIDOC_ = "apidoc"

class GenerateEpydoc(Command):
	description = "custom command, that generates documentation using the epydoc module"
	user_options = []
	def initialize_options(self):
		from epydoc import cli as epydoc_cli
		self.options = type("",(),epydoc_cli.OPTION_DEFAULTS)()
		self.options.verbosity = 0
		self.options.simple_term = True
		self.options.include_log = False
		self.options.dotpath = None
		self.options.action = "html"
		self.options.target = _APIDOC_
		if not os.path.isdir(_APIDOC_):
			os.mkdir(_APIDOC_)
	def finalize_options(self):
		pass
	def run(self):
		from epydoc import cli as epydoc_cli
		epydoc_cli.main(self.options,_PACKAGES_)

setup(
	name='testlink',
	version='0.11',
	description='Testlink API Wrapper library',
	author='Kai Borowiak',
	author_email='kai.borowiak@secunet.com',
	packages=_PACKAGES_,
	keywords='testlink api xmlrpc python',
	cmdclass={'epydoc':GenerateEpydoc},
	test_suite='test',
)
