#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
import dhtmlparser


# Variables ===================================================================



# Functions & objects =========================================================
def test_remove_tags():
    dom = dhtmlparser.parseString("a<b>xax<i>xe</i>xi</b>d")
    assert dhtmlparser.removeTags(dom) == "axaxxexid"

    dom = dhtmlparser.parseString("<b></b>")
    assert not dhtmlparser.removeTags(dom)

    dom = dhtmlparser.parseString("<b><i></b>")
    assert not dhtmlparser.removeTags(dom)

    dom = dhtmlparser.parseString("<b><!-- asd --><i></b>")
    assert not dhtmlparser.removeTags(dom)