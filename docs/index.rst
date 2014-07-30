.. _index:

pyDHTMLParser
=============

Python version of DHTMLParser_ DOM HTML/XML parser.

This version is actually much more advanced, D version is kinda unupdated.

.. _DHTMLParser: https://github.com/Bystroushaak/DHTMLParser

Sources
-------
Source codes can be found at GitHub; https://github.com/Bystroushaak/pyDHTMLParser

Installation
------------
pyDHTMLParser is hosted at pypi_, so you can install it using pip::

    pip install pyDHTMLParser

.. _pypi: https://pypi.python.org/pypi/pyDHTMLParser


Package content
---------------

.. toctree::
    :maxdepth: 1

    /api/dhtmlparser
    /api/dhtmlparser.htmlelement
    /api/dhtmlparser.quoter
    /api/dhtmlparser.specialdict

Unittests
---------
Almost everything should be tested. You can run tests using script ``run_tests.sh``
which can be found at the root of the project::

    $ ./run_tests.sh 
    ============================= test session starts ==============================
    platform linux2 -- Python 2.7.5 -- py-1.4.20 -- pytest-2.5.2
    collected 52 items 

    tests/test_escapers.py ..
    tests/test_htmlelement_find.py .......
    tests/test_htmlelement_functions.py ..
    tests/test_htmlelement_getters.py ...........
    tests/test_htmlelement_mult_param.py ....
    tests/test_htmlelement_one_param.py ......
    tests/test_htmlelement_setters.py ..
    tests/test_module.py .............
    tests/test_specialdict.py .....

    ========================== 52 passed in 0.32 seconds ===========================

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
