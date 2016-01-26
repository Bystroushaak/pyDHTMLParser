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
    if isinstance(item, basestring):
        return item.lower()

    return item


class SpecialDict(OrderedDict):
    """
    This dictionary stores items case sensitive, but compare them case
    INsensitive.
    """
    def __init__(self, *args, **kwargs):
        # lower_key -> key mapping
        self._case = OrderedDict()

        super(SpecialDict, self).__init__(*args, **kwargs)

    def __setitem__(self, key, value):
        lower_key = _lower_if_str(key)

        # remove the old key with (possibly) different case
        if lower_key in self._case:
            original_key = self._case[lower_key]
            super(SpecialDict, self).__delitem__(original_key)

        self._case[lower_key] = key

        super(SpecialDict, self).__setitem__(key, value)

    def __getitem__(self, key):
        lower_key = _lower_if_str(key)

        if lower_key not in self._case:
            raise KeyError(repr(key))

        return super(SpecialDict, self).__getitem__(self._case[lower_key])

    def __delitem__(self, key):
        lower_key = _lower_if_str(key)
        key = self._case[lower_key]

        del self._case[lower_key]

        return super(SpecialDict, self).__delitem__(key)

    def clear(self):
        self._case.clear()
        return super(SpecialDict, self).clear()

    def get(self, k, d=None):
        lower_key = _lower_if_str(k)
        if lower_key not in self._case:
            return d

        return super(SpecialDict, self).get(self._case[lower_key], d)

    def __contains__(self, key):
        lower_key = _lower_if_str(key)
        right_key = self._case.get(lower_key, None)

        return right_key and right_key in set(self.viewkeys())

    def has_key(self, key):
        return key in self

    def __eq__(self, obj):
        if self is obj:
            return True

        if not hasattr(obj, "__getitem__"):
            return False

        keys = None
        if hasattr(obj, "keys"):
            keys = obj.keys()
        elif hasattr(obj, "iterkeys"):
            keys = list(obj.keys())
        else:
            keys = list(obj)

        if len(self.keys()) != len(keys):
            return False

        for key in keys:
            if not self.__contains__(key):
                return False

            if obj[key] != self.__getitem__(key):
                return False

        return True

    def __ne__(self, obj):
        return not self.__eq__(obj)
