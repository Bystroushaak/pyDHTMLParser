#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
from collections import OrderedDict


# Functions & objects =========================================================
def _lower_if_str(item):
    """
    Try to convert item to lowercase, if it is string.

    Args:
        item (obj): Str, unicode or any other object.

    Returns:
        obj: ``item.lower()`` if `item` is ``str`` or ``unicode``, else just \
             `item` itself.
    """
    if type(item) in [str, unicode]:
        return item.lower()

    return item


class SpecialDict(OrderedDict):
    """
    This dictionary stores items case sensitive, but compare them case
    INsensitive.
    """
    def __contains__(self, key):
        keys = super(SpecialDict, self).keys()
        return _lower_if_str(key) in set(map(lambda x: _lower_if_str(x), keys))

    def __getitem__(self, key):
        key = _lower_if_str(key)

        for item in self.keys():
            if key == _lower_if_str(item):
                return super(SpecialDict, self).__getitem__(item)

        raise KeyError("Can't find key '%s'!" % key)

    def __eq__(self, obj):
        if self is obj:
            return True

        if not hasattr(obj, "keys"):
            return False

        if len(self.keys()) != len(obj.keys()):
            return False

        for key in obj.keys():
            if not self.__contains__(key):
                return False

            if obj[key] != self.__getitem__(key):
                return False

        return True

    def __ne__(self, obj):
        return not self.__eq__(obj)
