#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
import dhtmlparser


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
br = div.find("br")[0]


# Functions & objects =========================================================
def test_isTag():
    assert div.isTag()
    assert not div.childs[0].isTag()


def test_isEndTag():
    assert not div.isEndTag()
    assert not div.childs[0].isEndTag()

    assert div.endtag.isEndTag()


def test_isNonPairTag():
    assert not div.isNonPairTag()

    text = div.childs[0]
    assert text.getTagName().strip() == "Second."

    assert not text.isTag()
    assert not text.isNonPairTag()

    assert br.isNonPairTag()


def test_isComment():
    assert not div.isComment()
    assert not div.childs[0].isComment()

    assert div.childs[-2].isComment()


def test_isOpeningTag():
    assert div.isOpeningTag()
    assert not div.childs[0].isOpeningTag()

    assert not br.isOpeningTag()


def test_isEndTagTo():
    assert div.endtag.isEndTagTo(div)


def test_tagToString():
    assert div.tagToString() == '<div id="second">'
    assert div.childs[0].tagToString() == '\n        Second.\n        '

    assert br.tagToString() == "<br />"


def test_getTagName():
    assert div.getTagName() == 'div'
    assert div.childs[0].getTagName() == '\n        Second.\n        '

    assert br.getTagName() == "br"


def test_getContent():
    match = '\n        Second.\n        <br />\n        <!-- comment -->\n    '
    assert div.getContent() == match
    assert div.childs[0].getContent() == '\n        Second.\n        '

    assert br.getContent() == ""


def test_toString():
    assert div.toString().startswith(div.tagToString())
    assert div.childs[0].toString() == '\n        Second.\n        '
    assert br.toString() == "<br />"


def test_isNonPairTag_setter():
    div.isNonPairTag(True)

    assert div.toString() == '<div id="second" />'