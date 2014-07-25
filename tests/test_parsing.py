#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
import dhtmlparser


# Functions & objects =========================================================
def test_find():
    dom = dhtmlparser.parseString("""
        "<div ID='xa' a='b'>obsah xa divu</div> <!-- ID, not id :) -->
         <div id='xex' a='b'>obsah xex divu</div>
    """)

    div_xe = dom.find("div", {"id": "xa"})  # notice the small `id`
    div_xex = dom.find("div", {"id": "xex"})
    div_xerexes = dom.find("div", {"id": "xerexex"})

    assert div_xe
    assert div_xex
    assert not div_xerexes

    div_xe = div_xe[0]
    div_xex = div_xex[0]

    assert div_xe.toString() == '<div a="b" ID="xa">obsah xa divu</div>'
    assert div_xex.toString() == '<div a="b" id="xex">obsah xex divu</div>'

    assert div_xe.getTagName() == "div"
    assert div_xex.getTagName() == "div"


def test_findB():
    dom = dhtmlparser.parseString("""
        <div id=first>
            First div.
            <div id=first.subdiv>
                Subdiv in first div.
            </div>
        </div>
        <div id=second>
            Second.
        </div>
    """)

    assert dom.find("div")[1].getContent().strip() == "Subdiv in first div."
    assert dom.findB("div")[1].getContent().strip() == "Second."
