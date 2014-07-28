#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
import dhtmlparser
from dhtmlparser.htmlelement import _rotate_buff, _closeElements


# Functions & objects =========================================================
def test_rotate_buff():
    buff = [1, 2, 3, 4]

    buff = _rotate_buff(buff)
    assert buff == [4, 1, 2, 3]

    buff = _rotate_buff(buff)
    assert buff == [3, 4, 1, 2]

    buff = _rotate_buff(buff)
    assert buff == [2, 3, 4, 1]

    buff = _rotate_buff(buff)
    assert buff == [1, 2, 3, 4]


def test_closeElements():
    tag = dhtmlparser.HTMLElement("<div>")
    tag.endtag = dhtmlparser.HTMLElement("</div>")

    tag.childs = [
        dhtmlparser.HTMLElement("<xe>")
    ]

    xe = tag.find("xe")
    assert xe
    assert not xe[0].endtag

    tag.chids = _closeElements(tag.childs)

    xe = tag.find("xe")
    assert xe
    assert xe[0].endtag
