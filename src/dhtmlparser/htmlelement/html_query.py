#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
from .html_parser import HTMLParser

from .html_parser import _is_str
from .html_parser import _is_dict
from .html_parser import _is_iterable


# Variables ===================================================================
# Functions & classes =========================================================
class HTMLQuery(HTMLParser):
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

        # test whether `params` dict is subset of self.params
        if not self.containsParamSubset(params):
            return False

        return True

    def find(self, tag_name, params=None, fn=None, case_sensitive=False):
        """
        Same as :meth:`findAll`, but without `endtags`.

        You can always get them from :attr:`endtag` property.
        """
        return [
            x for x in self.findAll(tag_name, params, fn, case_sensitive)
            if not x.isEndTag()
        ]

    def findB(self, tag_name, params=None, fn=None, case_sensitive=False):
        """
        Same as :meth:`findAllB`, but without `endtags`.

        You can always get them from :attr:`endtag` property.
        """
        return [
            x for x in self.findAllB(tag_name, params, fn, case_sensitive)
            if not x.isEndTag()
        ]

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
            list: List of :class:`HTMLElement` instances matching your \
                  criteria.
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
            list: List of :class:`HTMLElement` instances matching your \
                  criteria.
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

        el = self.__class__()  # HTMLElement()
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
            list: List of matching elements (empty list if no matching element\
                  is found).
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
            el = self.__class__()  # HTMLElement()
            el.childs = self.find(*args, **kwargs)
            return el

        # if absolute is not specified (ie - next recursive call), use
        # self._container, which is set to True by .wfind(), so next search
        # will be absolute from the given element
        absolute = kwargs.get("absolute", None)
        if absolute is None:
            absolute = self._container

        find_func = self.wfind if absolute else wrap_find

        result = None
        if _is_iterable(act):
            result = find_func(*act)
        elif _is_dict(act):
            result = find_func(**act)
        elif _is_str(act):
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
