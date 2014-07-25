#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
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


# Functions & objects =========================================================
def rotate_buff(buff):
    """
    Rotate buffer (for each buff[i] = buff[i-1]).
    """
    return [buff[-1]] + buff[:-1]


def closeElements(childs):
    "Close tags - used in some constructors"

    o = []

    # Close all unclosed pair tags
    for e in childs:
        if not e.isTag():
            o.append(e)
            continue

        if not e.isNonPairTag() and not e.isEndTag() and not e.isComment() \
           and e.endtag is None:
            e.childs = closeElements(e.childs)

            o.append(e)
            o.append(HTMLElement("</" + e.getTagName() + ">"))

            # Join opener and endtag
            e.endtag = o[-1]
            o[-1].openertag = e
        else:
            o.append(e)

    return o


class HTMLElement(object):
    """
    Container for parsed html elements.
    """
    def __init__(self, tag="", second=None, third=None):
        self.__element = None
        self.__tagname = ""

        self.__istag = False
        self.__isendtag = False
        self.__iscomment = False
        self.__isnonpairtag = False

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
            self.childs = closeElements(third)
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
            self.childs = closeElements(second)
            self.endtag = HTMLElement("</" + self.getTagName() + ">")

        elif type(tag) in [list, tuple] and tag and \
             all(map(lambda x: isinstance(x, HTMLElement), tag)):
            self.__init_tag("")
            self.childs = closeElements(tag)

        else:
            raise Exception("Unknown type '%s'!" % type(tag))

    #==========================================================================
    #= Constructor overloading ================================================
    #==========================================================================
    def __init_tag(self, tag):
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

    # used when HTMLElement(tag, params) is called - basically create string
    # from tagname and params
    def __init_tag_params(self, tag, params):
        tag = tag.strip().replace(" ", "")
        nonpair = ""

        if tag.startswith("<"):
            tag = tag[1:]

        if tag.endswith("/>"):
            tag = tag[:-2]
            nonpair = " /"
        elif tag.endswith(">"):
            tag = tag[:-1]

        output = "<" + tag

        for key in params.keys():
            output += " " + key + '="' + escape(params[key], '"') + '"'

        self.__init_tag(output + nonpair + ">")

    def find(self, tag_name, params=None, fn=None, case_sensitive=False):
        """
        Same as findAll, but without endtags. You can always get them from
        .endtag property..
        """
        return filter(
            lambda x: not x.isEndTag(),
            self.findAll(tag_name, params, fn, case_sensitive)
        )

    def findB(self, tag_name, params=None, fn=None, case_sensitive=False):
        """
        Same as findAllB, but without endtags. You can always get them from
        .endtag property..
        """
        return filter(
            lambda x: not x.isEndTag(),
            self.findAllB(tag_name, params, fn, case_sensitive)
        )

    def findAll(self, tag_name, params=None, fn=None, case_sensitive=False):
        """
        Simple search engine using Depth-first algorithm
        http://en.wikipedia.org/wiki/Depth-first_search.

        Finds elements and subelements which match patterns given by 
        parameters. Also allows search defined by user's lambda function.

        @param tag_name: Name of tag.
        @type tag_name: string

        @param params: Parameters of arg.
        @type params: dictionary

        @param fn: User defined function for search.
        @type fn: lambda function

        @param case_sensitive: Search case sensitive. Default True.
        @type case_sensitive: bool

        @return: Matches.
        @rtype: Array of HTMLElements
        """
        output = []

        if self.isAlmostEqual(tag_name, params, fn, case_sensitive):
            output.append(self)

        tmp = []
        for el in self.childs:
            tmp = el.findAll(tag_name, params, fn, case_sensitive)

            if tmp is not None and len(tmp) > 0:
                output.extend(tmp)

        return output

    def findAllB(self, tag_name, params=None, fn=None, case_sensitive=False):
        """
        Simple search engine using Breadth-first algorithm
        http://en.wikipedia.org/wiki/Breadth-first_search.

        Finds elements and subelements which match patterns given by
        parameters and also allows search defined by users lambda function.

        @param tag_name: Name of tag.
        @type tag_name: string

        @param params: Parameters of arg.
        @type params: dictionary

        @param fn: User defined function for search.
        @type fn: lambda function

        @param case_sensitive: Search case sensitive. Default True.
        @type case_sensitive: bool

        @return: Matches.
        @rtype: Array of HTMLElements
        """
        output = []

        if self.isAlmostEqual(tag_name, params, fn, case_sensitive):
            output.append(self)

        breadth_search = self.childs
        for el in breadth_search:
            if el.isAlmostEqual(tag_name, params, fn, case_sensitive):
                output.append(el)

            if len(el.childs) > 0:
                breadth_search.extend(el.childs)

        return output

    #==========================================================================
    #= Parsers ================================================================
    #==========================================================================
    def __parseIsTag(self):
        self.__istag = self.__element.startswith("<") and \
                       self.__element.endswith(">")

    def __parseIsEndTag(self):
        last = ""
        self.__isendtag = False

        if self.__element.startswith("<") and self.__element.endswith(">"):
            for c in self.__element:
                if c == "/" and last == "<":
                    self.__isendtag = True

                if ord(c) > 32:
                    last = c

    def __parseIsNonPairTag(self):
        last = ""
        self.__isnonpairtag = False

        # Tags endings with /> are nonpair - do not mind whitespaces (< 32)
        if self.__element.startswith("<") and self.__element.endswith(">"):
            for c in self.__element:
                if c == ">" and last == "/":
                    self.__isnonpairtag = True
                    return

                if ord(c) > 32:
                    last = c

        # Check listed nonpair tags
        if self.__tagname.lower() in NONPAIR_TAGS:
            self.__isnonpairtag = True

    def __parseIsComment(self):
        self.__iscomment = self.__element.startswith("<!--") and \
                           self.__element.endswith("-->")

    def __parseTagName(self):
        for el in self.__element.split(" "):
            el = el.replace("/", "").replace("<", "").replace(">", "")

            if len(el) > 0:
                self.__tagname = el.rstrip()
                return

    def __parseParams(self):
        # check if there are any parameters
        if " " not in self.__element or "=" not in self.__element:
            return

        # Remove '<' & '>'
        params = self.__element.strip()[1:-1].strip()
        # Remove tagname
        params = params[
            params.find(self.getTagName()) + len(self.getTagName()):
        ].strip()

        # Parser machine
        next_state = 0
        key = ""
        value = ""
        end_quote = ""
        buff = ["", ""]
        for c in params:
            if next_state == 0:  # key
                if c.strip() != "":  # safer than list space, tab and all possible whitespaces in UTF
                    if c == "=":
                        next_state = 1
                    else:
                        key += c

            elif next_state == 1:  # value decisioner
                if c.strip() != "":  # skip whitespaces
                    if c == "'" or c == '"':
                        next_state = 3
                        end_quote = c
                    else:
                        next_state = 2
                        value += c

            elif next_state == 2:  # one word parameter without quotes
                if c.strip() == "":
                    next_state = 0
                    self.params[key] = value
                    key = ""
                    value = ""
                else:
                    value += c

            elif next_state == 3:  # quoted string
                if c == end_quote and (buff[0] != "\\" or (buff[0]) == "\\" and buff[1] == "\\"):
                    next_state = 0
                    self.params[key] = unescape(value, end_quote)
                    key = ""
                    value = ""
                    end_quote = ""
                else:
                    value += c

            buff = rotate_buff(buff)
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
        "True if element is tag (not content)."
        return self.__istag

    def isEndTag(self):
        "True if HTMLElement is end tag (/tag)."
        return self.__isendtag

    def isNonPairTag(self, isnonpair=None):
        """
        Returns True if HTMLElement is listed nonpair tag table (br for
        example) or if it ends with / - <br /> for example.

        You can also change state from pair to nonpair if you use this as
        setter.
        """
        if isnonpair is None:
            return self.__isnonpairtag

        self.__isnonpairtag = isnonpair
        if not isnonpair:
            self.endtag = None
            self.childs = []

    def isPairTag(self):
        """
        Return True if this is paired tag - <body> .. </body> for example.
        """
        if self.isComment() or self.isNonPairTag():
            return False

        if self.isEndTag():
            return True

        if self.isOpeningTag() and self.endtag:
            return True

        return False

    def isComment(self):
        "True if HTMLElement is html comment."
        return self.__iscomment

    def isOpeningTag(self):
        "True if is opening tag."
        if self.isTag() and (not self.isComment()) and (not self.isEndTag()) \
           and (not self.isNonPairTag()):
            return True

        return False

    def isEndTagTo(self, opener):
        "Returns true, if this element is endtag to opener."
        if not (self.__isendtag and opener.isOpeningTag()):
            return False

        return self.__tagname.lower() == opener.getTagName().lower()

    def tagToString(self):
        "Returns tag (with parameters), without content or endtag."
        if len(self.params) <= 0:
            return self.__element

        output = "<" + str(self.__tagname)

        for key in self.params.keys():
            output += " " + key + "=\"" + escape(self.params[key], '"') + "\""

        return output + " />" if self.__isnonpairtag else output + ">"

    def getTagName(self):
        "Returns tag name."
        return self.__tagname

    def getContent(self):
        "Returns content of tag (everything between opener and endtag)."
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

    def prettify(self, depth=0, separator="  ", last=True, pre=False, inline=False):
        "Returns prettifyied tag with content."
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

        # detect if inline
        is_inline = inline  # is_inline shows if inline was set by detection, or as parameter
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
    def toString(self, original=False):
        """
        Returns almost original string (use original = True if you want exact
        copy).

        If you want prettified string, try .prettify()

        If original == True, return parsed element, so if you changed something
        in .params, there will be no traces of those changes.
        """
        output = ""

        if self.childs != [] or self.isOpeningTag():
            output += self.__element if original else self.tagToString()

            for c in self.childs:
                output += c.toString(original)

            if self.endtag is not None:
                output += self.endtag.tagToString()
        elif not self.isEndTag():
            output += self.tagToString()

        return output

    def __str__(self):
        return self.toString()

    def isAlmostEqual(self, tag_name, params=None, fn=None, case_sensitive=False):
        """
        Compare element with given tagname, params and/or by lambda function.

        Lambda function is same as in .find().
        """
        if isinstance(tag_name, HTMLElement):
            return self.isAlmostEqual(tag_name.getTagName(), self.params)

        # search by lambda function
        if fn is not None:
            if fn(self):
                return True

        if not case_sensitive:
            self.__tagname = self.__tagname.lower()
            tag_name = tag_name.lower()

        # compare tagname
        if self.__tagname == tag_name and self.__tagname != "" and self.__tagname is not None:
            # compare parameters
            if params is None or len(params) == 0:
                return True

            if len(self.params) > 0:
                for key in params.keys():
                    if key not in self.params:
                        return False

                    if params[key] != self.params[key]:
                        return False

                return True

        return False

    #* /Operators *************************************************************

    #==========================================================================
    #= Setters ================================================================
    #==========================================================================
    def replaceWith(self, el):
        """
        Replace element. Useful when you don't want change all references to
        object.
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
        Remove subelement (child) specified by reference.

        This can't be used for removing subelements by value! If you want do
        such thing, do:

        ---
        for e in dom.find("value"):
            dom.removeChild(e)
        ---

        Params:
            child
                child which will be removed from dom (compared by reference)
            end_tag_too
                remove end tag too - default true
        """

        if len(self.childs) <= 0:
            return

        end_tag = None
        if end_tag_too:
            end_tag = child.endtag

        for e in self.childs:
            if e == child:
                self.childs.remove(e)

            if end_tag_too and end_tag == e and end_tag is not None:
                self.childs.remove(e)
            else:
                e.removeChild(child, end_tag_too)

    #* /Setters ***************************************************************
