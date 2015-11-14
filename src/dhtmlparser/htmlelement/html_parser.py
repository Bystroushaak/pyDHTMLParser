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

    def toString(self):
        """
        Returns almost original string (use `original` = True if you want exact
        copy).

        If you want prettified string, try :meth:`prettify`.
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

    def getTagName(self):
        """
        Returns:
            str: Tag name or while element in case of normal text \
                 (``not isTag()``).
        """
        if not self._istag:
            return self._element

        return self._tagname

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

    # * /Getters **************************************************************

    # =========================================================================
    # = Operators =============================================================
    # =========================================================================
    def __str__(self):
        return self.toString()

    def __repr__(self):
        return "HTMLElement(%s)" % repr(self.__str__())

    def containsParamSubset(self, params):
        """
        Test whether this element contains at least all `params`, or more.

        Args:
            params (dict/SpecialDict): Subset of parameters.

        Returns:
            bool: True if all `params` are contained in this element.
        """
        for key in params.keys():
            if key not in self.params:
                return False

            if params[key] != self.params[key]:
                return False

        return True

    def isAlmostEqual(self, tag_name, params=None, fn=None,
                      case_sensitive=False):
        """
        Compare element with given `tag_name`, `params` and/or by lambda
        function `fn`.

        Lambda function is same as in :meth:`find`.

        Args:
            tag_name (str): Compare just name of the element.
            params (dict, default None): Compare also parameters.
            fn (function, default None): Function which will be used for
                                         matching.
            case_sensitive (default False): Use case sensitive matching of the
                                            `tag_name`.

        Returns:
            bool: True if two elements are almost equal.
        """
        if isinstance(tag_name, self.__class__):
            return self.isAlmostEqual(
                tag_name.getTagName(),
                tag_name.params if tag_name.params else None
            )

        # search by lambda function
        if fn and not fn(self):
            return False

        # compare case sensitive?
        comparator = self._tagname  # we need to make self._tagname lower
        if not case_sensitive and tag_name:
            tag_name = tag_name.lower()
            comparator = comparator.lower()

        # compare tagname
        if tag_name and tag_name != comparator:
            return False

        # None params = don't use parameters to compare equality
        if params is None:
            return True

        # compare parameters
        if params == self.params:
            return True

        # test whether params dict is subset of self.params
        if not self.containsParamSubset(params):
            return False

        return True

    # * /Operators ************************************************************

    # =========================================================================
    # = Setters ===============================================================
    # =========================================================================
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

    # * /Setters **************************************************************
