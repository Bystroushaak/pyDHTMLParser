#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
from dhtmlparser import HTMLElement


# Functions & objects =========================================================
def test_constructor_text():
    text = "hello"
    e = HTMLElement(text)

    assert not e.isTag()
    assert not e.isEndTag()
    assert not e.isPairTag()
    assert not e.isComment()
    assert not e.isOpeningTag()
    assert not e.isNonPairTag()

    assert not e.childs
    assert not e.params
    assert not e.endtag
    assert not e.openertag

    assert e.toString() == text
    assert e.getContent() == text
    assert e.tagToString() == text
    assert e.getTagName() == text


def test_constructor_inline_tag():
    text = "<hello />"
    e = HTMLElement(text)

    assert e.isTag()
    assert not e.isEndTag()
    assert not e.isPairTag()
    assert not e.isComment()
    assert not e.isOpeningTag()
    assert e.isNonPairTag()

    assert not e.childs
    assert not e.params
    assert not e.endtag
    assert not e.openertag

    assert e.toString() == text
    assert e.getContent() == ""
    assert e.tagToString() == text
    assert e.getTagName() == "hello"


def test_constructor_normal_tag():
    text = "<hello>"
    e = HTMLElement(text)

    assert e.isTag()
    assert not e.isEndTag()
    assert not e.isPairTag()
    assert not e.isComment()
    assert e.isOpeningTag()
    assert not e.isNonPairTag()

    assert not e.childs
    assert not e.params
    assert not e.endtag
    assert not e.openertag

    assert e.toString() == text
    assert e.getContent() == ""
    assert e.tagToString() == text
    assert e.getTagName() == "hello"


def test_constructor_end_tag():
    text = "</hello>"
    e = HTMLElement(text)

    assert e.isTag()
    assert e.isEndTag()
    assert e.isPairTag()
    assert not e.isComment()
    assert not e.isOpeningTag()
    assert not e.isNonPairTag()

    assert not e.childs
    assert not e.params
    assert not e.endtag
    assert not e.openertag

    assert e.toString() == ""
    assert e.getContent() == ""
    assert e.tagToString() == text
    assert e.getTagName() == "hello"


def test_constructor_param_tag():
    text = """<hello as='bsd' xe=1 xax="xerexe">"""
    e = HTMLElement(text)

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

    assert e.toString() == '<hello as="bsd" xe="1" xax="xerexe">'
    assert e.getContent() == ""
    assert e.getTagName() == "hello"

    assert "as" in e.params
    assert "xe" in e.params
    assert "xax" in e.params

    assert e.params["as"] == "bsd"
    assert e.params["xe"] == "1"
    assert e.params["xax"] == "xerexe"


def test_constructor_comment():
    text = "<!-- asd -->"
    e = HTMLElement(text)

    assert e.isTag()
    assert not e.isEndTag()
    assert not e.isPairTag()
    assert e.isComment()
    assert not e.isOpeningTag()
    assert not e.isNonPairTag()

    assert not e.childs
    assert not e.params
    assert not e.endtag
    assert not e.openertag

    assert e.toString() == text
    assert e.getContent() == ""
    assert e.tagToString() == text
    assert e.getTagName() == text
