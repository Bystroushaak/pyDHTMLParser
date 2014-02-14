#!/usr/bin/env python
import os
from distutils.core import setup


def dirToLinks(directory):
	return map(lambda x: directory + "/" + x, os.listdir(directory))


url = 'https://github.com/Bystroushaak/pyDHTMLParser'

setup(
	name         = 'pyDHTMLParser',
	version      = '1.7.5',
	py_modules   = ['dhtmlparser'],

	author       = 'Bystroushaak',
	author_email = 'bystrousak@kitakitsune.org',

	url          = url,
	description  = 'Python HTML/XML parser for simple web scraping.',
	license      = 'CC BY',

	long_description = """Documentation can be found in README.creole, or at
project pages at github: """ + url,

	classifiers=[
		"License :: Public Domain",

		"Programming Language :: Python :: 2.7",

		"Topic :: Software Development :: Libraries",

		"Topic :: Text Processing :: Markup :: HTML",
		"Topic :: Text Processing :: Markup :: XML"
	],

	data_files=[
		('examples', dirToLinks("examples")),
		('others', ['README.creole', "__init__.py"]),
	]
)
