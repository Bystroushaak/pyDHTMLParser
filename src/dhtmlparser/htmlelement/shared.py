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


def _closeElements(childs, HTMLElement):
    """
    Create `endtags` to elements which looks like openers, but doesn't have
    proper :attr:`HTMLElement.endtag`.

    Args:
        childs (list): List of childs (:class:`HTMLElement` obj) - typically
               from :attr:`HTMLElement.childs` property.

    Returns:
        list: List of closed elements.
    """
    out = []

    # close all unclosed pair tags
    for e in childs:
        if not e.isTag():
            out.append(e)
            continue

        if not e.isNonPairTag() and not e.isEndTag() and not e.isComment() \
           and e.endtag is None:
            e.childs = _closeElements(e.childs, HTMLElement)

            out.append(e)
            out.append(HTMLElement("</" + e.getTagName() + ">"))

            # join opener and endtag
            e.endtag = out[-1]
            out[-1].openertag = e
        else:
            out.append(e)

    return out
