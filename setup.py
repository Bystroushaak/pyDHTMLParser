#!/usr/bin/env python
from setuptools import setup, find_packages


url = 'https://github.com/Bystroushaak/pyDHTMLParser'


setup(
    name         = 'pyDHTMLParser',
    version      = '2.0.0',
    py_modules   = ['dhtmlparser'],

    author       = 'Bystroushaak',
    author_email = 'bystrousak@kitakitsune.org',

    url          = url,
    description  = 'Python HTML/XML parser for simple web scraping.',
    license      = 'CC BY',

    long_description = """Documentation can be found in README.creole, or at
project pages at github: """ + url,

    packages=find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,

    classifiers=[
        "License :: Public Domain",

        "Programming Language :: Python :: 2.7",

        "Topic :: Software Development :: Libraries",

        "Topic :: Text Processing :: Markup :: HTML",
        "Topic :: Text Processing :: Markup :: XML"
    ]
)
