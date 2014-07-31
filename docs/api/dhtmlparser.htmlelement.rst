HTMLElement class
=================

This class can be used for parsing or for creating DOM manually.

DOM building
------------
If you want to create DOM from HTMLElements, you can use one of theese four
constructors::

   HTMLElement()
   HTMLElement("<tag>")
   HTMLElement("<tag>", {"param": "value"})
   HTMLElement("tag", {"param": "value"}, [HTMLElement("<tag1>"), ...])

Tag or parameter specification parts can be omitted::


   HTMLElement("<root>", [HTMLElement("<tag1>"), ...])
   HTMLElement(
      [HTMLElement("<tag1>"), ...]
   )


Examples
++++++++

Blank element
^^^^^^^^^^^^^
::

   >>> from dhtmlparser import HTMLElement 
   >>> e = HTMLElement()
   >>> e
   <dhtmlparser.HTMLElement instance at 0x7fb2b39ca170>
   >>> print e

   >>> 

Usually, it is better to use ``HTMLElement("")``.

Nonpair tag
^^^^^^^^^^^
::

   >>> e = HTMLElement("<br>")
   >>> e.isNonPairTag()
   True
   >>> e.isOpeningTag()
   False
   >>> print e
   <br>

Notice, that closing tag wasn't automatically created.

Pair tag
^^^^^^^^
::

   >>> e = HTMLElement("<tag>")
   >>> e.isOpeningTag() # this doesn't check if tag actually is paired, just if it looks like opening tag
   True
   >>> e.isPairTag()    # this does check if element is actually paired
   False
   >>> e.endtag = HTMLElement("</tag>")
   >>> e.isOpeningTag()
   True
   >>> e.isPairTag()
   True
   >>> print e
   <tag></tag>

In short::

   >>> e = HTMLElement("<tag>")
   >>> e.endtag = HTMLElement("</tag>")

Or you can always use string parser::


   >>> e = d.parseString("<tag></tag>")
   >>> print e
   <tag></tag>

But don't forget, that elements returned from parseString() are encapsulated in blank "root" tag::

   >>> e = d.parseString("<tag></tag>")
   >>> e.getTagName()
   ''
   >>> e.childs[0].tagToString()
   '<tag>'
   >>> e.childs[0].endtag.tagToString() # referenced thru .endtag property
   >>> e.childs[1].tagToString() # manually selected entag from childs - don't use this
   '</tag>'
   '</tag>

Tags with parameters
^^^^^^^^^^^^^^^^^^^^

Tag (with or without <>) can have as dictionary as second parameter.

::

   >>> e = HTMLElement("tag", {"param":"value"})  # without <>, because normal text can't have parameters
   >>> print e
   <tag param="value">
   >>> print e.params  # parameters are accessed thru .params property
   {'param': 'value'}

Tags with content
^^^^^^^^^^^^^^^^^

You can create content manually::

   >>> e = HTMLElement("<tag>")
   >>> e.childs.append(HTMLElement("content"))
   >>> e.endtag = HTMLElement("</tag>")
   >>> print e
   <tag>content</tag>

But there is also easier way::

   >>> print HTMLElement("tag", [HTMLElement("content")])
   <tag>content</tag>

or::

   >>> print HTMLElement("tag", {"some": "parameter"}, [HTMLElement("content")])
   <tag some="parameter">content</tag>

HTMLElement class API
---------------------

.. automodule:: dhtmlparser.htmlelement
    :members:
    :undoc-members:
