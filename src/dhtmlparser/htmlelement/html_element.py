#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
from html_query import HTMLQuery
from html_parser import _is_iterable


# Variables ===================================================================
# Functions & classes =========================================================
class HTMLElement(HTMLQuery):
    def replaceWith(self, el):
        """
        Replace value in this element with values from `el`.

        This useful when you don't want change all references to object.

        Args:
            el (obj): :class:`HTMLElement` instance.
        """
        self.childs = el.childs
        self.params = el.params
        self.endtag = el.endtag
        self.openertag = el.openertag

        self._tagname = el.getTagName()
        self._element = el.tagToString()

        self._istag = el.isTag()
        self._isendtag = el.isEndTag()
        self._iscomment = el.isComment()
        self._isnonpairtag = el.isNonPairTag()

    def removeChild(self, child, end_tag_too=True):
        """
        Remove subelement (`child`) specified by reference.

        Note:
            This can't be used for removing subelements by value! If you want
            to do such thing, try::

                for e in dom.find("value"):
                    dom.removeChild(e)

        Args:
            child (obj): :class:`HTMLElement` instance which will be removed
                         from this element.
            end_tag_too (bool, default True): Remove also `child` endtag.
        """
        # if there are multiple childs, remove them
        if _is_iterable(child):
            map(lambda x: self.removeChild(x, end_tag_too), child)
            return

        if not self.childs:
            return

        end_tag = None
        if end_tag_too:
            end_tag = child.endtag

        for e in self.childs:
            if e != child:
                e.removeChild(child, end_tag_too)
                continue

            if end_tag_too and end_tag in self.childs:
                self.childs.remove(end_tag)

            self.childs.remove(e)
