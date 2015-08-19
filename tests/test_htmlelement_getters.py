#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
import dhtmlparser
from dhtmlparser import first


# Variables ===================================================================
DOM = dhtmlparser.parseString("""
    <div id=first>
        First div.
        <div id=first.subdiv>
            Subdiv in first div.
        </div>
    </div>
    <div id=second>
        Second.
        <br />
        <!-- comment -->
    </div>
""")
div = DOM.find("div")[-1]
br = first(div.find("br"))


# Functions & objects =========================================================
def test_isTag():
    assert div.isTag()
    assert not first(div.childs).isTag()


def test_isEndTag():
    assert not div.isEndTag()
    assert not first(div.childs).isEndTag()

    assert div.endtag.isEndTag()


def test_isNonPairTag():
    assert not div.isNonPairTag()

    text = first(div.childs)
    assert text.getTagName().strip() == "Second."

    assert not text.isTag()
    assert not text.isNonPairTag()

    assert br.isNonPairTag()


def test_isComment():
    assert not div.isComment()
    assert not first(div.childs).isComment()

    assert div.childs[-2].isComment()


def test_isOpeningTag():
    assert div.isOpeningTag()
    assert not first(div.childs).isOpeningTag()

    assert not br.isOpeningTag()


def test_isEndTagTo():
    assert div.endtag.isEndTagTo(div)


def test_tagToString():
    assert div.tagToString() == '<div id="second">'
    assert first(div.childs).tagToString() == '\n        Second.\n        '

    assert br.tagToString() == "<br />"


def test_getTagName():
    assert div.getTagName() == 'div'
    assert first(div.childs).getTagName() == '\n        Second.\n        '

    assert br.getTagName() == "br"


def test_getContent():
    match = '\n        Second.\n        <br />\n        <!-- comment -->\n    '
    assert div.getContent() == match
    assert first(div.childs).getContent() == '\n        Second.\n        '

    assert br.getContent() == ""


def test_toString():
    assert div.toString().startswith(div.tagToString())
    assert first(div.childs).toString() == '\n        Second.\n        '
    assert br.toString() == "<br />"


def test_isNonPairTag_setter():
    div.isNonPairTag(True)

    assert div.toString() == '<div id="second" />'


def test_containsParamSubset():
    dom = dhtmlparser.parseString("<div id=x class=xex></div>")
    div = first(dom.find("div"))

    assert div.containsParamSubset({"id": "x"})
    assert div.containsParamSubset({"class": "xex"})
    assert div.containsParamSubset({"id": "x", "class": "xex"})
    assert not div.containsParamSubset({"asd": "bsd", "id": "x", "class": "xex"})
