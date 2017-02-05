#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
from .html_query import HTMLQuery
from .html_parser import _is_iterable


# Variables ===================================================================
# Functions & classes =========================================================
class HTMLElement(HTMLQuery):
    def __str__(self):
        return self.toString()

    def __repr__(self):
        return "HTMLElement(%s)" % repr(self.__str__())

    def toString(self):
        """
        Returns almost original string.

        If you want prettified string, try :meth:`.prettify`.

        Returns:
            str: Complete representation of the element with childs, endtag \
                 and so on.
        """
        output = ""

        if self.childs or self.isOpeningTag():
            output += self.tagToString()

            for c in self.childs:
                output += c.toString()

            if self.endtag is not None:
                output += self.endtag.tagToString()

        elif not self.isEndTag():
            output += self.tagToString()

        return output

    def getContent(self):
        """
        Returns:
            str: Content of tag (everything between `opener` and `endtag`).
        """
        if not self.isTag() and self._element:
            return self._element

        if not self.childs:
            return ""

        output = ""
        for c in self.childs:
            if not c.isEndTag():
                output += c.toString()

        if output.endswith("\n"):
            return output.rstrip()

        return output

    def prettify(self, depth=0, separator="  ", last=True, pre=False,
                 inline=False):
        """
        Same as :meth:`toString`, but returns prettified element with content.

        Note:
            This method is partially broken, and can sometimes create
            unexpected results.

        Returns:
            str: Prettified string.
        """
        output = ""

        if self.getTagName() != "" and self.tagToString().strip() == "":
            return ""

        # if not inside <pre> and not inline, shift tag to the right
        if not pre and not inline:
            output += (depth * separator)

        # for <pre> set 'pre' flag
        if self.getTagName().lower() == "pre" and self.isOpeningTag():
            pre = True
            separator = ""

        output += self.tagToString()

        # detect if inline - is_inline shows if inline was set by detection, or
        # as parameter
        is_inline = inline
        for c in self.childs:
            if not (c.isTag() or c.isComment()):
                if len(c.tagToString().strip()) != 0:
                    inline = True

        # don't shift if inside container (containers have blank tagname)
        original_depth = depth
        if self.getTagName() != "":
            if not pre and not inline:  # inside <pre> doesn't shift tags
                depth += 1
                if self.tagToString().strip() != "":
                    output += "\n"

        # prettify childs
        for e in self.childs:
            if not e.isEndTag():
                output += e.prettify(
                    depth,
                    last=False,
                    pre=pre,
                    inline=inline
                )

        # endtag
        if self.endtag is not None:
            if not pre and not inline:
                output += ((original_depth) * separator)

            output += self.endtag.tagToString().strip()

            if not is_inline:
                output += "\n"

        return output

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
            for x in child:
                self.removeChild(child=x, end_tag_too=end_tag_too)
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
