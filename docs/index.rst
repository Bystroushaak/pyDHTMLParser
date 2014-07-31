.. _index:

pyDHTMLParser
=============

Python version of DHTMLParser_ DOM HTML/XML parser.

This version is actually much more advanced, D version is kinda unupdated.

.. _DHTMLParser: https://github.com/Bystroushaak/DHTMLParser

What is it?
===========
DHTMLParser is a lightweight HTML/XML parser created for one purpose - quick and easy 
picking selected tags from DOM.

It can be very useful when you are in need to write own "guerilla" API for some webpage, or a 
scrapper.

If you want, you can also create HTML/XML documents more easily than by joining strings.

How it works?
=============
The module have just one important function; :func:`.parseString`. This function takes
a string and returns a Document Object Model made of linked :class:`.HTMLElement`
objects (see bellow).

When you call :func:`.parseString`, the string argument is cut into pieces and
then evaluated. Each piece is checked and if it looks like it could be HTML
element, then it is put into :class:`.HTMLElement` object and proper attributes
are set (:attr:`.HTMLElement.__istag` and so on). 

Every following element is put into :attr:`.HTMLElement.childs` list of this
element, until proper closing element is found by simple stack mechanism.

Elements with parameters are parsed and parameters are extracted into
:attr:`.HTMLElement.params` property.

Result is array of single linked trees (you can make double linke by calling 
:func:`.makeDoubleLinked`), which is then encapsulated in a blank 
:class:`.HTMLElement` container, which holds the whole DOM in its
:attr:`.HTMLElement.childs` property.

This container can be then queried using :meth:`.HTMLElement.find`,
:meth:`.HTMLElement.findB`, :meth:`.HTMLElement.wfind` and 
:meth:`.HTMLElement.match` methods.

XML
---

This module is intended mainly for parsing HTML. If you want to parse XML and
you don't want parser to guess nonpair tags from source, just set global module
property :attr:`~dhtmlparser.htmlelement.NONPAIR_TAGS` to blank list.

There is also ``cip`` argument of :func:`.parseString` function, which makes
parameters of the HTML/XML tags case sensitive.

Package content
===============

.. toctree::
    :maxdepth: 1

    /api/dhtmlparser
    /api/dhtmlparser.htmlelement
    /api/dhtmlparser.quoter
    /api/dhtmlparser.specialdict

Interactive example
===================

::

    >>> import dhtmlparser as d
    >>> dom = d.parseString("""
    ... <root>
    ...  <element name="xex" />
    ... </root>
    ... """)
    >>> print dom
    <dhtmlparser.HTMLElement instance at 0x240b320>
    >>> dom.getTagName()  # blank, container element
    ''

DOM tree now in memory looks like this::

   dom == <dhtmlparser.HTMLElement instance at 0x240b320>
    |- .getTagName() == ""
    |- .isTag()      == False
    |- .params       == ""
    |- .openertag    == None
    |- .endtag       == None
    `- .childs       == [<dhtmlparser.HTMLElement instance at 0x2403b90>, <dhtmlparser.HTMLElement instance at 0x2403ab8>, <dhtmlparser.HTMLElement instance at 0x240b050>, <dhtmlparser.HTMLElement instance at 0x240b248>]
         |
         |- .childs[0]       == <dhtmlparser.HTMLElement instance at 0x2403b90>
         |  |- .getTagName() == "\n"
         |  |- .isTag()      == False
         |  |- .params       == {}
         |  |- .openertag    == None
         |  |- .endtag       == None
         |  `- .childs       == []
         |
         |- .childs[1]         == <dhtmlparser.HTMLElement instance at 0x2403ab8>
         |  |- .getTagName()   == "root"
         |  |- .isTag()        == True
         |  |- .isEndTag()     == False
         |  |- .isOpeningTag() == True
         |  |- .params         == {}
         |  |- .openertag      == None
         |  |- .endtag         == <dhtmlparser.HTMLElement instance at 0x240b050>
         |  `- .childs         == [<dhtmlparser.HTMLElement instance at 0x2403c68>, <dhtmlparser.HTMLElement instance at 0x2403d88>, <dhtmlparser.HTMLElement instance at 0x2403ea8>]
         |     |
         |     |- .childs[0]       == <dhtmlparser.HTMLElement instance at 0x2403c68>
         |     |  |- .getTagName() == '\n '
         |     |  |- .isTag()      == False
         |     |  |- .params       == {}
         |     |  |- .openertag    == None
         |     |  |- .endtag       == None
         |     |  `- .childs       == []
         |     |
         |     |- .childs[1]         == <dhtmlparser.HTMLElement instance at 0x2403d88>
         |     |  |- .getTagName()   == 'element'
         |     |  |- .isTag()        == True
         |     |  |- .isNonPairTag() == True
         |     |  |- .params         == {'name': 'xex'}
         |     |  |- .openertag      == None
         |     |  |- .endtag         == None
         |     |  `- .childs         == []
         |     |
         |     `- .childs[2]       == <dhtmlparser.HTMLElement instance at 0x2403ea8>
         |        |- .getTagName() == '\n'
         |        |- .isTag()      == False
         |        |- .params       == {}
         |        |- .openertag    == None
         |        |- .endtag       == None
         |        `- .childs       == []
         |
         |- .childs[2]       == <dhtmlparser.HTMLElement instance at 0x240b050>
         |  |- .getTagName() == 'root'
         |  |- .isTag()      == True
         |  |- .isEndTag()   == True
         |  |- .params       == {}
         |  |- .openertag    == <dhtmlparser.HTMLElement instance at 0x2403ab8>
         |  |- .endtag       == None
         |  `- .childs       == []
         |
         `- .childs[3]       == <dhtmlparser.HTMLElement instance at 0x240b248>
            |- .getTagName() == '\n'
            |- .isTag()      == False
            |- .params       == {}
            |- .openertag    == None
            |- .endtag       == None
            `- .childs       == []

In interactive shell, we can easily verify the tree::

   >>> dom.childs[1].getTagName()
   'root'
   >>> dom.childs[1].childs
   [<dhtmlparser.HTMLElement instance at 0x2403c68>, <dhtmlparser.HTMLElement instance at 0x2403d88>, <dhtmlparser.HTMLElement instance at 0x2403ea8>]

and so on..

Now, let say, that you know there is HTML element named ``element`` and we want
to get it, but we don't know where it is. In that case :meth:`.HTMLElement.find`
will help us::

   >>> dom.find("element")
   [<dhtmlparser.HTMLElement instance at 0x2403d88>]

Or when we don't know name of the element, but we know that he has ``"name"`` 
parameter (:attr:`.HTMLElement.params`) set to ``"xex"``::

   >>> dom.find("", fn = lambda x: "name" in x.params and x.params["name"] == "xex")
   [<dhtmlparser.HTMLElement instance at 0x2403d88>]

Or we want only ``<element>`` tags with ``name="xex"`` parameters::

   >>> dom.find("element", {"name": "xex"})
   [<dhtmlparser.HTMLElement instance at 0x2403d88>]
   >>> dom.find("element", {"NAME": "xex"})  # parameter names (not values!) are case  insensitive by default
   [<dhtmlparser.HTMLElement instance at 0x2403d88>]

Sources
-------
Source codes can be found at GitHub; https://github.com/Bystroushaak/pyDHTMLParser

Installation
------------
pyDHTMLParser is hosted at pypi_, so you can install it using pip::

    pip install pyDHTMLParser

.. _pypi: https://pypi.python.org/pypi/pyDHTMLParser

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

Confused?
=========
If you don't understand how to use it, look at examples in ``./examples/``.
   
If you have questions, you can write me an email to: ``bystrousak````@kitakitsune.org``


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
