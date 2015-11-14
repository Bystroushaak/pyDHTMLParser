#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
"""
HTMLElement class used in DOM representation.
"""
# Imports =====================================================================
from ..quoter import escape, unescape
from ..specialdict import SpecialDict

from shared import NONPAIR_TAGS
from shared import _rotate_buff
from shared import _closeElements


# Functions & objects =========================================================
# helper functions
def _is_str(tag):
    return isinstance(tag, basestring)


def _is_dict(tag):
    return isinstance(tag, dict)


def _is_iterable(container):
    return type(container) in [list, tuple]


def _all_html_elements(container):
    if not container or not _is_iterable(container):
        return False

    return all(map(lambda x: isinstance(x, HTMLParser), container))


class HTMLParser(object):
    """
    This class is used to represent single linked DOM (see
    :func:`.makeDoubleLinked` for double linked).

    Attributes:
        childs (list): List of child nodes.
        params (dict): :class:`.SpecialDict` instance holding tag parameters.
        endtag (obj): Reference to the ending :class:`HTMLElement` or ``None``.
        openertag (obj): Reference to the openning :class:`HTMLElement` or
                         ``None``.
    """
    def __init__(self, tag="", second=None, third=None):
        self._element = None
        self._tagname = ""

        self._istag = False
        self._isendtag = False
        self._iscomment = False
        self._isnonpairtag = False
        self._container = False  # used by .wfind()

        self.childs = []
        self.params = SpecialDict()
        self.endtag = None
        self.openertag = None

        # blah, constructor overloading in python sux :P
        if _is_str(tag) and not any([second, third]):
            self._init_tag(tag)

        elif _is_str(tag) and _is_dict(second) and not third:
            self._init_tag_params(tag, second)

        elif _is_str(tag) and _is_dict(second) and _all_html_elements(third):
            # containers with childs are automatically considered as tags
            if tag.strip():
                if not tag.startswith("<"):
                    tag = "<" + tag
                if not tag.endswith(">"):
                    tag += ">"

            self._init_tag_params(tag, second)
            self.childs = _closeElements(third, self.__class__)
            self.endtag = self.__class__("</" + self.getTagName() + ">")

        elif _is_str(tag) and _all_html_elements(second):
            # containers with childs are automatically considered as tags
            if tag.strip():
                if not tag.startswith("<"):
                    tag = "<" + tag
                if not tag.endswith(">"):
                    tag += ">"

            self._init_tag(tag)
            self.childs = _closeElements(second, self.__class__)
            self.endtag = self.__class__("</" + self.getTagName() + ">")

        elif _all_html_elements(tag):
            self._init_tag("")
            self.childs = _closeElements(tag, self.__class__)

        else:
            raise Exception("Unknown type '%s'!" % type(tag))

    # =========================================================================
    # = Constructor overloading ===============================================
    # =========================================================================
    def _init_tag(self, tag):
        """
        True constructor, which really initializes the :class:`HTMLElement`.

        This is the function where all the preprocessing happens.

        Args:
            tag (str): HTML tag as string.
        """
        self._element = tag

        self._parseIsTag()
        self._parseIsComment()

        if not self._istag or self._iscomment:
            self._tagname = self._element
        else:
            self._parseTagName()

        if self._iscomment or not self._istag:
            return

        self._parseIsEndTag()
        self._parseIsNonPairTag()

        if self._istag and (not self._isendtag) or "=" in self._element:
            self._parseParams()

    def _init_tag_params(self, tag, params):
        """
        Alternative constructor used when the tag parameters are added to the
        HTMLElement (HTMLElement(tag, params)).

        This method just creates string and then pass it to the
        :meth:`_init_tag`.

        Args:
            tag (str): HTML tag as string.
            params (dict): HTML tag parameters as dictionary.
        """
        self._element = tag
        self.params = params
        self._parseTagName()
        self._istag = True
        self._isendtag = False
        self._isnonpairtag = False

        self._element = self.tagToString()

    # =========================================================================
    # = Parsers ===============================================================
    # =========================================================================
    def _parseIsTag(self):
        """
        Detect whether the element is HTML tag or not.

        Result is saved to the :attr:`_istag` property.
        """
        el = self._element
        self._istag = el and el[0] == "<" and el[-1] == ">"

    def _parseIsEndTag(self):
        """
        Detect whether the element is `endtag` or not.

        Result is saved to the :attr:`_isendtag` property.
        """
        self._isendtag = self._element.startswith("</")

    def _parseIsNonPairTag(self):
        """
        Detect whether the element is nonpair or not (ends with ``/>``).

        Result is saved to the :attr:`_isnonpairtag` property.
        """
        self._isnonpairtag = False

        if self._iscomment:
            return

        if self._element.startswith("<") and self._element.endswith("/>"):
            self._isnonpairtag = True

        # check listed nonpair tags
        if self._istag and self._tagname.lower() in NONPAIR_TAGS:
            self._isnonpairtag = True

    def _parseIsComment(self):
        """
        Detect whether the element is HTML comment or not.

        Result is saved to the :attr:`_iscomment` property.
        """
        self._iscomment = (
            self._element.startswith("<!--") and self._element.endswith("-->")
        )

    def _parseTagName(self):
        """
        Parse name of the tag.

        Result is saved to the :attr:`_tagname` property.
        """
        for el in self._element.split():
            el = el.replace("/", "").replace("<", "").replace(">", "")

            if el.strip():
                self._tagname = el.rstrip()
                return

    def _parseParams(self):
        """
        Parse parameters from their string HTML representation to dictionary.

        Result is saved to the :attr:`params` property.
        """
        # check if there are any parameters
        if " " not in self._element or "=" not in self._element:
            return

        # remove '<' & '>'
        params = self._element.strip()[1:-1].strip()

        # remove tagname
        offset = params.find(self.getTagName()) + len(self.getTagName())
        params = params[offset:].strip()

        # parser machine
        next_state = 0
        key = ""
        value = ""
        end_quote = ""
        buff = ["", ""]
        for c in params:
            if next_state == 0:      # key
                if c.strip() != "":  # safer than list space, tab and all
                    if c == "=":     # possible whitespaces in UTF
                        next_state = 1
                    else:
                        key += c

            elif next_state == 1:    # value decisioner
                if c.strip() != "":  # skip whitespaces
                    if c == "'" or c == '"':
                        next_state = 3
                        end_quote = c
                    else:
                        next_state = 2
                        value += c

            elif next_state == 2:    # one word parameter without quotes
                if c.strip() == "":
                    next_state = 0
                    self.params[key] = value
                    key = ""
                    value = ""
                else:
                    value += c

            elif next_state == 3:    # quoted string
                if c == end_quote and (buff[0] != "\\" or (buff[0]) == "\\" and buff[1] == "\\"):
                    next_state = 0
                    self.params[key] = unescape(value, end_quote)
                    key = ""
                    value = ""
                    end_quote = ""
                else:
                    value += c

            buff = _rotate_buff(buff)
            buff[0] = c

        if key:
            if end_quote and value.strip():
                self.params[key] = unescape(value, end_quote)
            else:
                self.params[key] = value

        if "/" in self.params.keys():
            del self.params["/"]
            self._isnonpairtag = True

    # * /Parsers **************************************************************

    # =========================================================================
    # = Getters ===============================================================
    # =========================================================================
    def isTag(self):
        """
        Returns:
            bool: True if the element is considered to be HTML tag.
        """
        return self._istag

    def isEndTag(self):
        """
        Returns:
            bool: True if the element is end tag (``</endtag>``).
        """
        return self._isendtag

    def isNonPairTag(self, isnonpair=None):
        """
        True if element is listed in nonpair tag table (``br`` for example) or
        if it ends with ``/>`` (``<hr />`` for example).

        You can also change state from pair to nonpair if you use this as
        setter.

        Args:
            isnonpair (bool, default None): If set, internal nonpair state is
                      changed.

        Returns:
            book: True if tag is nonpair.
        """
        if isnonpair is None:
            return self._isnonpairtag

        if not self._istag:
            return

        if isnonpair:
            self.endtag = None
            self.childs = []

        self._isnonpairtag = isnonpair

    def isPairTag(self):
        """
        Returns:
            bool: True if this is pair tag - ``<body> .. </body>`` for example.
        """
        if self.isComment() or self.isNonPairTag():
            return False

        if self.isEndTag():
            return True

        if self.isOpeningTag() and self.endtag:
            return True

        return False

    def isOpeningTag(self):
        """
        Detect whether this tag is opening or not.

        Returns:
            bool: True if it is opening.
        """
        if self.isTag() and \
           not self.isComment() and \
           not self.isEndTag() and \
           not self.isNonPairTag():
            return True

        return False

    def isEndTagTo(self, opener):
        """
        Args:
            opener (obj): :class:`HTMLElement` instance.

        Returns:
            bool: True, if this element is endtag to `opener`.
        """
        if not (self._isendtag and opener.isOpeningTag()):
            return False

        return self._tagname.lower() == opener.getTagName().lower()

    def isComment(self):
        """
        Returns:
            bool: True if this element is encapsulating HTML comment.
        """
        return self._iscomment

    def tagToString(self):
        """
        Get HTML element representation of the tag, but only the tag, not the
        :attr:`childs` or :attr:`endtag`.

        Returns:
            str: HTML representation.
        """
        def is_el_without_params():
            return not self.params and "=" not in self._element

        if not self.isTag() or self.isComment() or is_el_without_params():
            return self._element

        output = "<" + str(self._tagname)

        for key in self.params:
            output += " " + key + "=\"" + escape(self.params[key], '"') + "\""

        return output + " />" if self._isnonpairtag else output + ">"

    def getTagName(self):
        """
        Returns:
            str: Tag name or while element in case of normal text \
                 (``not isTag()``).
        """
        if not self._istag:
            return self._element

        return self._tagname

    # * /Getters **************************************************************
