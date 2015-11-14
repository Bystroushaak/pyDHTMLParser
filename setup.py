#! /usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

from docs import getVersion

changelog = open('CHANGES.rst').read()
long_description = "\n\n".join([
    open('README.rst').read(),
    changelog
])


setup(
    name='pyDHTMLParser',
    version=getVersion(changelog),
    py_modules=['dhtmlparser'],

    author='Bystroushaak',
    author_email='bystrousak@kitakitsune.org',

    url='https://github.com/Bystroushaak/pyDHTMLParser',
    description='Python HTML/XML parser for simple web scraping.',
    license='MIT',

    long_description=long_description,

    packages=find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,

    classifiers=[
        "License :: OSI Approved :: MIT License",

        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",

        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development :: Libraries :: Python Modules",

        "Topic :: Text Processing :: Markup :: HTML",
        "Topic :: Text Processing :: Markup :: XML"
    ],

    extras_require={
        "test": [
            "pytest",
            "pytest-cov",
        ],
        "docs": [
            "sphinx",
            "sphinxcontrib-napoleon",
        ]
    }
)
