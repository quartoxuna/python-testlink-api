#!/usr/bin/env python

from distutils.core import setup
from distutils.core import Command
import os

_PACKAGES_ = ['testlink']
_APIDOC_ = "apidoc"

try:
	from epydoc import cli as epydoc_cli

	_OPTIONS_ = type("",(),epydoc_cli.OPTION_DEFAULTS)()
	_OPTIONS_.verbosity = 1
	_OPTIONS_.include_log = False
	_OPTIONS_.dotpath = None
	_OPTIONS_.action = "html"
	_OPTIONS_.target = _APIDOC_

	USE_EPYDOC = True
except Exception,ex:
	USE_EPYDOC= False
	EPYDOC_ERROR = str(ex)

class GenerateDoc(Command):
	description = "custom command, that generates documentation using the epydoc module"
	user_options = []
	def initialize_options(self):
		pass
	def finalize_options(self):
		pass
	def run(self):
		# Create directory if needed
		if not os.path.isdir(_APIDOC_):
			os.mkdir(_APIDOC_)
		if USE_EPYDOC:
			epydoc_cli.main(_OPTIONS_,_PACKAGES_)
		else:
			print("Cannot generate apidoc: %s" % EPYDOC_ERROR)

setup(
	name='python-testlink_api_wrapper',
	version='0.9',
	description='Testlink API Wrapper library',
	author='Kai Borowiak',
	author_email='kai.borowiak@secunet.com',
	packages=_PACKAGES_,
	keywords='testlink api xmlrpc python',
	license='GPL',
	requires=['bs4'],
	cmdclass={'epydoc':GenerateDoc}
)
