#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
"""
This module provides ability to quote and unquote strings using backslash
notation.
"""


# Functions & objects =========================================================
def unescape(inp, quote='"'):
    """
    Unescape `quote` in string `inp`.

    Example usage::

        >> unescape('hello \\"')
        'hello "'

    Args:
        inp (str): String in which `quote` will be unescaped.
        quote (char, default "): Specify which character will be unescaped.

    Returns:
        str: Unescaped string.
    """
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


def escape(inp, quote='"'):
    """
    Escape `quote` in string `inp`.

    Example usage::

        >>> escape('hello "')
        'hello \\"'
        >>> escape('hello \\"')
        'hello \\\\"'

    Args:
        inp (str): String in which `quote` will be escaped.
        quote (char, default "): Specify which character will be escaped.

    Returns:
        str: Escaped string.
    """
    output = ""

    for c in inp:
        if c == quote:
            output += '\\'

        output += c

    return output
