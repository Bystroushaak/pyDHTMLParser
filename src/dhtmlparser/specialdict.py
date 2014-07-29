#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================


# Functions & objects =========================================================
class SpecialDict(dict):
    """
    This dictionary stores items case sensitive, but compare them case
    INsensitive.
    """
    def __contains__(self, key):
        keys = super(SpecialDict, self).keys()
        return key.lower() in set(map(lambda x: x.lower(), keys))

    def __getitem__(self, key):
        key = key.lower()

        for item in self.keys():
            if key == item.lower():
                return super(SpecialDict, self).__getitem__(item)

        raise KeyError("Can't find key '%s'!" % key)
