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
        self._case = OrderedDict()
        super(SpecialDict, self).__init__(*args, **kwargs)

    def __setitem__(self, key, value):
        lower_key = _lower_if_str(key)
        self._case[lower_key] = key

        super(SpecialDict, self).__setitem__(lower_key, value)

    def __getitem__(self, key):
        return super(SpecialDict, self).__getitem__(_lower_if_str(key))

    def __delitem__(self, key):
        lower_key = _lower_if_str(key)

        # in case of popitem() this is not true, because it is poped before
        if lower_key in self._case:
            del self._case[lower_key]

        return super(SpecialDict, self).__delitem__(lower_key)

    def clear(self):
        self._case.clear()
        return super(SpecialDict, self).clear()

    def keys(self):
        return self._case.values()

    def iterkeys(self):
        return self._case.itervalues()

    def items(self):
        return zip(self.iterkeys(), self.itervalues())

    def iteritems(self):
        value_iterator = iter(self.itervalues())

        for key in self._case.itervalues():
            yield key, next(value_iterator)

    def get(self, k, d=None):
        return super(SpecialDict, self).get(_lower_if_str(k), d)

    def popitem(self, ):
        lower_key, key = self._case.popitem()
        return key, self.pop(lower_key)

    def __iter__(self):
        return self._case.itervalues()

    def __contains__(self, key):
        return super(SpecialDict, self).__contains__(_lower_if_str(key))

    def has_key(self, key):
        return key in self

    # def __eq__(self, obj):
    #     if self is obj:
    #         return True

    #     if not hasattr(obj, "keys"):
    #         return False

    #     if len(self.keys()) != len(obj.keys()):
    #         return False

    #     for key in obj.keys():
    #         if not self.__contains__(key):
    #             return False

    #         if obj[key] != self.__getitem__(key):
    #             return False

    #     return True

    # def __ne__(self, obj):
    #     return not self.__eq__(obj)

    # def __getattribute__(self, name):
    #     attr = object.__getattribute__(self, name)
    #     print name
    #     if hasattr(attr, '__call__'):
    #         print "%s has __call__" % name
    #         def newfunc(*args, **kwargs):
    #             print('before calling %s' %attr.__name__)
    #             result = attr(*args, **kwargs)
    #             print('done calling %s' %attr.__name__)
    #             return result
    #         return newfunc
    #     else:
    #         print "attr", name, attr
    #         return attr