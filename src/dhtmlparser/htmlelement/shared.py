#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
# Variables ===================================================================
#: List of non-pair tags. Set this to blank list, if you wish to parse XML.
NONPAIR_TAGS = [
    "br",
    "hr",
    "img",
    "input",
    # "link",
    "meta",
    "spacer",
    "frame",
    "base"
]


# Functions ===================================================================
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
