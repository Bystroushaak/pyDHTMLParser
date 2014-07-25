#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
from dhtmlparser import HTMLElement


# Functions & objects =========================================================
def test_costructuro_parameters():
    e = HTMLElement("name", {"key": "value"})

    assert e.isTag()
    assert not e.isEndTag()
    assert not e.isPairTag()
    assert not e.isComment()
    assert e.isOpeningTag()
    assert not e.isNonPairTag()

    assert not e.childs
    assert e.params
    assert not e.endtag
    assert not e.openertag

    assert e.toString()
    assert not e.getContent()
    assert e.tagToString()
    assert e.getTagName() == "name"

    assert "key" in e.params
    assert e.params["key"] == "value"

    assert dict(e.params) == {"key": "value"}


def test_costructor_with_childs():
    e = HTMLElement(
        "name",
        {"key": "value"},
        [
            HTMLElement("hello"),
            HTMLElement("<hi />")
        ]
    )

    assert e.isTag()
    assert not e.isEndTag()
    assert e.isOpeningTag()
    assert e.isPairTag()
    assert not e.isComment()
    assert not e.isNonPairTag()

    assert e.childs
    assert e.params
    assert e.endtag
    assert not e.openertag

    assert e.toString()
    assert e.getContent() == "hello<hi />"
    assert e.tagToString()
    assert e.getTagName() == "name"

    assert "key" in e.params
    assert e.params["key"] == "value"

    assert dict(e.params) == {"key": "value"}

    assert len(e.childs) == 2

    assert e.childs[0].getContent() == "hello"
    assert e.childs[1].getTagName() == "hi"


def test_costructor_with_chids_no_param():
    e = HTMLElement(
        "name",
        [
            HTMLElement("hello"),
            HTMLElement("<hi />")
        ]
    )

    assert e.isTag()
    assert not e.isEndTag()
    assert e.isOpeningTag()
    assert e.isPairTag()
    assert not e.isComment()
    assert not e.isNonPairTag()

    assert e.childs
    assert not e.params
    assert e.endtag
    assert not e.openertag

    assert e.toString()
    assert e.getContent() == "hello<hi />"
    assert e.tagToString()
    assert e.getTagName() == "name"

    assert len(e.childs) == 2

    assert e.childs[0].getContent() == "hello"
    assert e.childs[1].getTagName() == "hi"

def test_costructor_with_childs_only():
    e = HTMLElement(
        [
            HTMLElement("hello"),
            HTMLElement("<hi>"),
        ]
    )

    assert not e.isTag()
    assert not e.isEndTag()
    assert not e.isOpeningTag()
    assert not e.isPairTag()
    assert not e.isComment()
    assert not e.isNonPairTag()

    assert e.childs
    assert not e.params
    assert not e.endtag
    assert not e.openertag

    assert e.toString() == "hello<hi></hi>"
    assert e.getContent() == "hello<hi></hi>"
    assert not e.tagToString()
    assert not e.getTagName()

    assert len(e.childs) == 3

    assert e.childs[0].getContent() == "hello"
    assert e.childs[1].getTagName() == "hi"
    assert e.childs[2].getTagName() == "hi"  # endtag is automatically created
    assert e.childs[2].isEndTag()
