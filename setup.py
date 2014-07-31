#! /usr/bin/env python
# -*- coding: utf-8 -*-
import os
import os.path
import shutil

from setuptools import setup, find_packages
from distutils.command.sdist import sdist

try:
    from docs import getVersion
except ImportError:  # during packaging, docs are moved to html_docs
    from html_docs import getVersion

changelog = open('CHANGES.rst').read()
long_description = "\n\n".join([
    open('README.rst').read(),
    changelog
])


class BuildSphinx(sdist):
    """
    Generates sphinx documentation, puts it into html_docs/, packs it to
    package and removes unused directory.
    """
    def run(self):
        d = os.path.abspath('.')
        DOCS = d + "/" + "docs"
        DOCS_IN = DOCS + "/_build/html"
        DOCS_OUT = d + "/html_docs"

        if not self.dry_run:
            print "Generating the documentation .."

            os.chdir(DOCS)
            os.system("make clean")
            os.system("make html")

            if os.path.exists(DOCS_OUT):
                shutil.rmtree(DOCS_OUT)

            shutil.copytree(DOCS_IN, DOCS_OUT)
            shutil.copy(DOCS + "/__init__.py", DOCS_OUT)  # for getVersion()
            os.chdir(d)

        sdist.run(self)

        if os.path.exists(DOCS_OUT):
            shutil.rmtree(DOCS_OUT)


setup(
    name         = 'pyDHTMLParser',
    version      = getVersion(changelog),
    py_modules   = ['dhtmlparser'],

    author       = 'Bystroushaak',
    author_email = 'bystrousak@kitakitsune.org',

    url          = 'https://github.com/Bystroushaak/pyDHTMLParser',
    description  = 'Python HTML/XML parser for simple web scraping.',
    license      = 'CC BY (public domain)',

    long_description = long_description,

    packages=find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,

    classifiers=[
        "License :: Public Domain",

        "Programming Language :: Python :: 2.7",

        "Topic :: Software Development :: Libraries",

        "Topic :: Text Processing :: Markup :: HTML",
        "Topic :: Text Processing :: Markup :: XML"
    ],

    cmdclass={'sdist': BuildSphinx}
)
