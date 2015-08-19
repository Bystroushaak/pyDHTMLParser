#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
import dhtmlparser
from dhtmlparser import first


# Variables ===================================================================
TEXT = "<div><nonpair /></div>"
dom = dhtmlparser.parseString(TEXT)


# Functions & objects =========================================================
def test_replaceWith():
    nonpair = first(dom.find("nonpair"))

    assert nonpair

    nonpair.replaceWith(
        dhtmlparser.HTMLElement("<another />")
    )

    assert dom.find("another")

    assert dom.getContent() == "<div><another /></div>"


def test_removeChild():
    dom.removeChild(
        dom.find("another")
    )

    assert dom.getContent() == "<div></div>"

    dom.removeChild(dom.find("div"), end_tag_too=False)

    assert dom.getContent() == ""
    assert len(dom.childs) == 1  # endtag wasn't removed

    dom2 = dhtmlparser.parseString("<div></div>")
    dom2.removeChild(dom2.find("div"))

    assert dom2.getContent() == ""
    assert not dom2.childs


def test_params():
    dom = dhtmlparser.parseString("<xe id=1 />")
    xe = first(dom.find("xe"))

    assert xe.params["id"] == "1"

    xe.params = {}
    assert str(xe) == "<xe />"
