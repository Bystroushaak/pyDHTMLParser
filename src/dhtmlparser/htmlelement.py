#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
"""
HTMLElement class used in DOM representation.
"""
# Imports =====================================================================
from quoter import escape, unescape
from specialdict import SpecialDict


# Variables ===================================================================
NONPAIR_TAGS = [
    "br",
    "hr",
    "img",
    "input",
    #"link",
    "meta",
    "spacer",
    "frame",
    "base"
]
"""
List of non-pair tags. Set this to blank list, if you wish to parse XML.
"""


# Functions & objects =========================================================
def _rotate_buff(buff):
    """
    Rotate buffer (for each ``buff[i] = buff[i-1]``).

    Example:
        assert _rotate_buff([1, 2, 3, 4]) == [4, 1, 2, 3]

    Args:
        buff (list): Buffer which will be rotated.

    Returns:
        list: Rotated buffer.
    """
    return [buff[-1]] + buff[:-1]


def _closeElements(childs):
    """
    Create `endtags` to elements which looks like openers, but doesn't have
    proper :attr:`HTMLElement.endtag`.

    Args:
        childs (list): List of childs (:class:`HTMLElement` obj) - typically
               from :attr:`HTMLElement.childs` property.

    Returns:
        list: List of closed elements.
    """
    o = []

    # close all unclosed pair tags
    for e in childs:
        if not e.isTag():
            o.append(e)
            continue

        if not e.isNonPairTag() and not e.isEndTag() and not e.isComment() \
           and e.endtag is None:
            e.childs = _closeElements(e.childs)

            o.append(e)
            o.append(HTMLElement("</" + e.getTagName() + ">"))

            # join opener and endtag
            e.endtag = o[-1]
            o[-1].openertag = e
        else:
            o.append(e)

    return o


class HTMLElement(object):
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
        self.__element = None
        self.__tagname = ""

        self.__istag = False
        self.__isendtag = False
        self.__iscomment = False
        self.__isnonpairtag = False
        self._container = False  # used by .wfind()

        self.childs = []
        self.params = SpecialDict()
        self.endtag = None
        self.openertag = None

        # blah, constructor overloading in python sux :P
        if type(tag) in [str, unicode] and not any([second, third]):
            self.__init_tag(tag)

        elif type(tag) in [str, unicode] and type(second) == dict and not third:
            self.__init_tag_params(tag, second)

        elif type(tag) in [str, unicode] and type(second) == dict and \
             type(third) in [list, tuple] and len(third) > 0 and \
             all(map(lambda x: isinstance(x, HTMLElement), third)):

            # containers with childs are automatically considered as tags
            if tag.strip():
                if not tag.startswith("<"):
                    tag = "<" + tag
                if not tag.endswith(">"):
                    tag += ">"

            self.__init_tag_params(tag, second)
            self.childs = _closeElements(third)
            self.endtag = HTMLElement("</" + self.getTagName() + ">")

        elif type(tag) in [str, unicode] and type(second) in [list, tuple] and \
             second and all(map(lambda x: isinstance(x, HTMLElement), second)):

            # containers with childs are automatically considered as tags
            if tag.strip():
                if not tag.startswith("<"):
                    tag = "<" + tag
                if not tag.endswith(">"):
                    tag += ">"

            self.__init_tag(tag)
            self.childs = _closeElements(second)
            self.endtag = HTMLElement("</" + self.getTagName() + ">")

        elif type(tag) in [list, tuple] and tag and \
             all(map(lambda x: isinstance(x, HTMLElement), tag)):
            self.__init_tag("")
            self.childs = _closeElements(tag)

        else:
            raise Exception("Unknown type '%s'!" % type(tag))

    #==========================================================================
    #= Constructor overloading ================================================
    #==========================================================================
    def __init_tag(self, tag):
        """
        True constructor, which really initializes the :class:`HTMLElement`.

        This is the function where all the preprocessing happens.

        Args:
            tag (str): HTML tag as string.
        """
        self.__element = tag

        self.__parseIsTag()
        self.__parseIsComment()

        if (not self.__istag) or self.__iscomment:
            self.__tagname = self.__element
        else:
            self.__parseTagName()

        if self.__iscomment or not self.__istag:
            return

        self.__parseIsEndTag()
        self.__parseIsNonPairTag()

        if self.__istag and (not self.__isendtag) or "=" in self.__element:
            self.__parseParams()

    def __init_tag_params(self, tag, params):
        """
        Alternative constructor used when the tag parameters are added to the
        HTMLElement (HTMLElement(tag, params)).

        This method just creates string and then pass it to the
        :meth:`__init_tag`.

        Args:
            tag (str): HTML tag as string.
            params (dict): HTML tag parameters as dictionary.
        """
        self.__element = tag
        self.params = params
        self.__parseTagName()
        self.__istag = True
        self.__isendtag = False
        self.__isnonpairtag = False

        self.__element = self.tagToString()

    def find(self, tag_name, params=None, fn=None, case_sensitive=False):
        """
        Same as :meth:`findAll`, but without `endtags`.

        You can always get them from :attr:`endtag` property.
        """
        return filter(
            lambda x: not x.isEndTag(),
            self.findAll(tag_name, params, fn, case_sensitive)
        )

    def findB(self, tag_name, params=None, fn=None, case_sensitive=False):
        """
        Same as :meth:`findAllB`, but without `endtags`.

        You can always get them from :attr:`endtag` property.
        """
        return filter(
            lambda x: not x.isEndTag(),
            self.findAllB(tag_name, params, fn, case_sensitive)
        )

    def findAll(self, tag_name, params=None, fn=None, case_sensitive=False):
        """
        Search for elements by their parameters using `Depth-first algorithm
        <http://en.wikipedia.org/wiki/Depth-first_search>`_.

        Args:
            tag_name (str): Name of the tag you are looking for. Set to "" if
                            you wish to use only `fn` parameter.
            params (dict, default None): Parameters which have to be present
                   in tag to be considered matching.
            fn (function, default None): Use this function to match tags.
               Function expects one parameter which is HTMLElement instance.
            case_sensitive (bool, default False): Use case sensitive search.

        Returns:
            list: List of :class:`HTMLElement` instances matching your criteria.
        """
        output = []

        if self.isAlmostEqual(tag_name, params, fn, case_sensitive):
            output.append(self)

        tmp = []
        for el in self.childs:
            tmp = el.findAll(tag_name, params, fn, case_sensitive)

            if tmp:
                output.extend(tmp)

        return output

    def findAllB(self, tag_name, params=None, fn=None, case_sensitive=False):
        """
        Simple search engine using `Breadth-first algorithm
        <http://en.wikipedia.org/wiki/Breadth-first_search>`_.

        Args:
            tag_name (str): Name of the tag you are looking for. Set to "" if
                            you wish to use only `fn` parameter.
            params (dict, default None): Parameters which have to be present
                   in tag to be considered matching.
            fn (function, default None): Use this function to match tags.
               Function expects one parameter which is HTMLElement instance.
            case_sensitive (bool, default False): Use case sensitive search.

        Returns:
            list: List of :class:`HTMLElement` instances matching your criteria.
        """
        output = []

        if self.isAlmostEqual(tag_name, params, fn, case_sensitive):
            output.append(self)

        breadth_search = self.childs
        for el in breadth_search:
            if el.isAlmostEqual(tag_name, params, fn, case_sensitive):
                output.append(el)

            if el.childs:
                breadth_search.extend(el.childs)

        return output

    def wfind(self, tag_name, params=None, fn=None, case_sensitive=False):
        """
        This methods works same as :meth:`find`, but only in one level of the
        :attr:`childs`.

        This allows to chain :meth:`wfind` calls::

            >>> dom = dhtmlparser.parseString('''
            ... <root>
            ...     <some>
            ...         <something>
            ...             <xe id="wanted xe" />
            ...         </something>
            ...         <something>
            ...             asd
            ...         </something>
            ...         <xe id="another xe" />
            ...     </some>
            ...     <some>
            ...         else
            ...         <xe id="yet another xe" />
            ...     </some>
            ... </root>
            ... ''')
            >>> xe = dom.wfind("root").wfind("some").wfind("something").find("xe")
            >>> xe
            [<dhtmlparser.htmlelement.HTMLElement object at 0x8a979ac>]
            >>> str(xe[0])
            '<xe id="wanted xe" />'

        Args:
            tag_name (str): Name of the tag you are looking for. Set to "" if
                            you wish to use only `fn` parameter.
            params (dict, default None): Parameters which have to be present
                   in tag to be considered matching.
            fn (function, default None): Use this function to match tags.
               Function expects one parameter which is HTMLElement instance.
            case_sensitive (bool, default False): Use case sensitive search.

        Returns:
            obj: Blank HTMLElement with all matches in :attr:`childs` property.

        Note:
            Returned element also have set :attr:`_container` property to True.
        """
        childs = self.childs
        if self._container:  # container object
            childs = map(
                lambda x: x.childs,
                filter(lambda x: x.childs, self.childs)
            )
            childs = sum(childs, [])  # flattern the list

        el = HTMLElement()
        el._container = True
        for child in childs:
            if child.isEndTag():
                continue

            if child.isAlmostEqual(tag_name, params, fn, case_sensitive):
                el.childs.append(child)

        return el

    def match(self, *args, **kwargs):
        """
        :meth:`wfind` is nice function, but still kinda long to use, because
        you have to manually chain all calls together and in the end, you get
        :class:`HTMLElement` instance container.

        This function recursively calls :meth:`wfind` for you and in the end,
        you get list of matching elements::

            xe = dom.match("root", "some", "something", "xe")

        is alternative to::

            xe = dom.wfind("root").wfind("some").wfind("something").wfind("xe")

        You can use all arguments used in :meth:`wfind`::

            dom = dhtmlparser.parseString('''
                <root>
                    <div id="1">
                        <div id="5">
                            <xe id="wanted xe" />
                        </div>
                        <div id="10">
                            <xe id="another wanted xe" />
                        </div>
                        <xe id="another xe" />
                    </div>
                    <div id="2">
                        <div id="20">
                            <xe id="last wanted xe" />
                        </div>
                    </div>
                </root>
            ''')

            xe = dom.match(
                "root",
                {"tag_name": "div", "params": {"id": "1"}},
                ["div", {"id": "5"}],
                "xe"
            )

            assert len(xe) == 1
            assert xe[0].params["id"] == "wanted xe"

        Args:
            *args: List of :meth:`wfind` parameters.
            absolute (bool, default None): If true, first element will be
                     searched from the root of the DOM. If None,
                     :attr:`_container` attribute will be used to decide value
                     of this argument. If False, :meth:`find` call will be run
                     first to find first element, then :meth:`wfind` will be
                     used to progress to next arguments.

        Returns:
            list: List of matching elements (blank if no matchin element found).
        """
        if not args:
            return self.childs

        # pop one argument from argument stack (tuples, so .pop() won't work)
        act = args[0]
        args = args[1:]

        # this is used to define relative/absolute root of the first element
        def wrap_find(*args, **kwargs):
            """
            Find wrapper, to allow .wfind() to be substituted witřh .find()
            call, which normally returns blank array instead of blank
            `container` element.
            """
            el = HTMLElement()
            el.childs = self.find(*args, **kwargs)
            return el

        # if absolute is not specified (ie - next recursive call), use
        # self._container, which is set to True by .wfind(), so next search will
        # be absolute from the given element
        absolute = kwargs.get("absolute", None)
        if absolute is None:
            absolute = self._container

        find_func = self.wfind if absolute else wrap_find

        result = None
        if type(act) in [list, tuple]:
            result = find_func(*act)
        elif type(act) == dict:
            result = find_func(**act)
        elif type(act) in [str, unicode]:
            result = find_func(act)
        else:
            raise KeyError(
                "Unknown parameter type '%s': %s" % (type(act), act)
            )

        if not result.childs:
            return []

        match = result.match(*args)

        # just to be sure return always blank array, when the match is
        # False/None and so on (it shouldn't be, but ..)
        return match if match else []


    #==========================================================================
    #= Parsers ================================================================
    #==========================================================================
    def __parseIsTag(self):
        """
        Detect whether the element is HTML tag or not.

        Result is saved to the :attr:`__istag` property.
        """
        self.__istag = self.__element.startswith("<") and \
                       self.__element.endswith(">")

    def __parseIsEndTag(self):
        """
        Detect whether the element is `endtag` or not.

        Result is saved to the :attr:`__isendtag` property.
        """
        self.__isendtag = self.__element.startswith("</")

    def __parseIsNonPairTag(self):
        """
        Detect whether the element is nonpair or not (ends with ``/>``).

        Result is saved to the :attr:`__isnonpairtag` property.
        """
        self.__isnonpairtag = False

        if self.__element.startswith("<") and self.__element.endswith("/>"):
            self.__isnonpairtag = True

        # check listed nonpair tags
        if self.__istag and self.__tagname.lower() in NONPAIR_TAGS:
            self.__isnonpairtag = True

    def __parseIsComment(self):
        """
        Detect whether the element is HTML comment or not.

        Result is saved to the :attr:`__iscomment` property.
        """
        self.__iscomment = self.__element.startswith("<!--") and \
                           self.__element.endswith("-->")

    def __parseTagName(self):
        """
        Parse name of the tag.

        Result is saved to the :attr:`__tagname` property.
        """
        for el in self.__element.split():
            el = el.replace("/", "").replace("<", "").replace(">", "")

            if el.strip():
                self.__tagname = el.rstrip()
                return

    def __parseParams(self):
        """
        Parse parameters from their string HTML representation to dictionary.

        Result is saved to the :attr:`params` property.
        """
        # check if there are any parameters
        if " " not in self.__element or "=" not in self.__element:
            return

        # remove '<' & '>'
        params = self.__element.strip()[1:-1].strip()
        # remove tagname
        params = params[
            params.find(self.getTagName()) + len(self.getTagName()):
        ].strip()

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

        if filter(lambda x: x == "/", self.params.keys()):
            del self.params["/"]
            self.__isnonpairtag = True

    #* /Parsers ***************************************************************

    #==========================================================================
    #= Getters ================================================================
    #==========================================================================
    def isTag(self):
        """
        Returns:
            bool: True if the element is considered to be HTML tag.
        """
        return self.__istag

    def isEndTag(self):
        """
        Returns:
            bool: True if the element is end tag (``</endtag>``).
        """
        return self.__isendtag

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
            return self.__isnonpairtag

        if not self.__istag:
            return

        if isnonpair:
            self.endtag = None
            self.childs = []

        self.__isnonpairtag = isnonpair

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
        if not (self.__isendtag and opener.isOpeningTag()):
            return False

        return self.__tagname.lower() == opener.getTagName().lower()

    def isComment(self):
        """
        Returns:
            bool: True if this element is encapsulating HTML comment.
        """
        return self.__iscomment

    def tagToString(self):
        """
        Get HTML element representation of the tag, but only the gag, not the
        :attr:`childs` or :attr:`endtag`.

        Returns:
            str: HTML representation.
        """
        if not self.params:
            return self.__element

        output = "<" + str(self.__tagname)

        for key in self.params:
            output += " " + key + "=\"" + escape(self.params[key], '"') + "\""

        return output + " />" if self.__isnonpairtag else output + ">"

    def toString(self, original=False):
        """
        Returns almost original string (use `original` = True if you want exact
        copy).

        If you want prettified string, try :meth:`prettify`.

        Args:
            original (bool, default False): If True, return parsed element, so
                     if you changed something in :attr:`params`, there will be
                     no traces of those changes.

        Returns:
            str: Complete representation of the element with childs, endtag \
                 and so on.
        """
        output = ""

        if self.childs or self.isOpeningTag():
            output += self.__element if original else self.tagToString()

            for c in self.childs:
                output += c.toString(original)

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
        if not self.__istag:
            return self.__element

        return self.__tagname

    def getContent(self):
        """
        Returns:
            str: Content of tag (everything between `opener` and `endtag`).
        """
        if not self.isTag() and self.__element:
            return self.__element

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
            This method is partially broken, and can sometimes create unexpected
            results.

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

    #* /Getters ***************************************************************

    #==========================================================================
    #= Operators ==============================================================
    #==========================================================================
    def __str__(self):
        return self.toString()

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
        if isinstance(tag_name, HTMLElement):
            return self.isAlmostEqual(
                tag_name.getTagName(),
                tag_name.params if tag_name.params else None
            )

        # search by lambda function
        if fn and not fn(self):
            return False

        if not case_sensitive and tag_name:
            self.__tagname = self.__tagname.lower()
            tag_name = tag_name.lower()

        # compare tagname
        if tag_name and tag_name != self.__tagname:
            return False

        # None params = don't use parameters to compare equality
        if params is None:
            return True

        # compare parameters
        if params == self.params:
            return True

        for key in params.keys():
            if key not in self.params:
                return False

            if params[key] != self.params[key]:
                return False

        return True

    #* /Operators *************************************************************

    #==========================================================================
    #= Setters ================================================================
    #==========================================================================
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

        self.__tagname = el.getTagName()
        self.__element = el.tagToString()

        self.__istag = el.isTag()
        self.__isendtag = el.isEndTag()
        self.__iscomment = el.isComment()
        self.__isnonpairtag = el.isNonPairTag()

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
        if type(child) in [list, tuple]:
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

    #* /Setters ***************************************************************
