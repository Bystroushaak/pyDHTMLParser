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
    def __contains__(self, k):
        for item in super(SpecialDict, self).keys():
            if k.lower() == item.lower():
                return True

    def __getitem__(self, k):
        for item in self.keys():
            if k.lower() == item.lower():
                return super(SpecialDict, self).__getitem__(item)
