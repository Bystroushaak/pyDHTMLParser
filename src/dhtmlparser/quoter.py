#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================


# Functions & objects =========================================================
def unescape(inp, quote='"'):
    if len(inp) < 2:
        return inp

    output = ""
    unesc = False
    for act in inp:
        if act == quote and unesc:
            output = output[:-1]

        output += act

        if act == "\\":
            unesc = not unesc
        else:
            unesc = False

    return output


def escape(input, quote='"'):
    output = ""

    for c in input:
        if c == quote:
            output += '\\'

        output += c

    return output
