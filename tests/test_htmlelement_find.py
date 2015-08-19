#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
import dhtmlparser
from dhtmlparser import first


# Functions & objects =========================================================
def test_find():
    dom = dhtmlparser.parseString(
        """
        "<div ID='xa' a='b'>obsah xa divu</div> <!-- ID, not id :) -->
         <div id='xex' a='b'>obsah xex divu</div>
        """
    )

    div_xe = dom.find("div", {"id": "xa"})  # notice the small `id`
    div_xex = dom.find("div", {"id": "xex"})
    div_xerexes = dom.find("div", {"id": "xerexex"})

    assert div_xe
    assert div_xex
    assert not div_xerexes

    div_xe = first(div_xe)
    div_xex = first(div_xex)

    assert div_xe.toString() == '<div ID="xa" a="b">obsah xa divu</div>'
    assert div_xex.toString() == '<div id="xex" a="b">obsah xex divu</div>'

    assert div_xe.getTagName() == "div"
    assert div_xex.getTagName() == "div"


def test_find_fn():
    dom = dhtmlparser.parseString(
        """
        <div id=first>
            First div.
            <div id=first.subdiv>
                Subdiv in first div.
            </div>
        </div>
        <div id=second>
            Second.
        </div>
        """
    )

    div_tags = dom.find("div", fn=lambda x: x.params.get("id") == "first")

    assert div_tags
    assert len(div_tags) == 1

    assert first(div_tags).params.get("id") == "first"
    assert first(div_tags).getContent().strip().startswith("First div.")


def test_find_params():
    dom = dhtmlparser.parseString(
        """
        <div id=first>
            First div.
            <div id=first.subdiv>
                Subdiv in first div.
            </div>
        </div>
        <div id=second>
            Second.
        </div>
        """
    )

    div_tags = dom.find("", {"id": "first"})

    assert div_tags
    assert len(div_tags) == 1

    assert first(div_tags).params.get("id") == "first"
    assert first(div_tags).getContent().strip().startswith("First div.")


def test_findB():
    dom = dhtmlparser.parseString(
        """
        <div id=first>
            First div.
            <div id=first.subdiv>
                Subdiv in first div.
            </div>
        </div>
        <div id=second>
            Second.
        </div>
        """
    )

    assert dom.find("div")[1].getContent().strip() == "Subdiv in first div."
    assert dom.findB("div")[1].getContent().strip() == "Second."


def test_wfind():
    dom = dhtmlparser.parseString(
        """
        <div id=first>
            First div.
            <div id=first.subdiv>
                Subdiv in first div.
            </div>
        </div>
        <div id=second>
            Second.
        </div>
        """
    )

    div = dom.wfind("div").wfind("div")

    assert div.childs
    assert first(div.childs).params["id"] == "first.subdiv"


def test_wfind_complicated():
    dom = dhtmlparser.parseString(
        """
        <root>
            <some>
                <something>
                    <xe id="wanted xe" />
                </something>
                <something>
                    asd
                </something>
                <xe id="another xe" />
            </some>
            <some>
                else
                <xe id="yet another xe" />
            </some>
        </root>
        """
    )

    xe = dom.wfind("root").wfind("some").wfind("something").find("xe")

    assert len(xe) == 1
    assert first(xe).params["id"] == "wanted xe"

    unicorn = dom.wfind("root").wfind("pink").wfind("unicorn")

    assert not unicorn.childs


def test_wfind_multiple_matches():
    dom = dhtmlparser.parseString(
        """
        <root>
            <some>
                <something>
                    <xe id="wanted xe" />
                </something>
                <something>
                    <xe id="another wanted xe" />
                </something>
                <xe id="another xe" />
            </some>
            <some>
                <something>
                    <xe id="last wanted xe" />
                </something>
            </some>
        </root>
        """
    )

    xe = dom.wfind("root").wfind("some").wfind("something").wfind("xe")

    assert len(xe.childs) == 3
    assert xe.childs[0].params["id"] == "wanted xe"
    assert xe.childs[1].params["id"] == "another wanted xe"
    assert xe.childs[2].params["id"] == "last wanted xe"


def test_match():
    dom = dhtmlparser.parseString(
        """
        <root>
            <some>
                <something>
                    <xe id="wanted xe" />
                </something>
                <something>
                    <xe id="another wanted xe" />
                </something>
                <xe id="another xe" />
            </some>
            <some>
                <something>
                    <xe id="last wanted xe" />
                </something>
            </some>
        </root>
        """
    )

    xe = dom.match("root", "some", "something", "xe")
    assert len(xe) == 3
    assert xe[0].params["id"] == "wanted xe"
    assert xe[1].params["id"] == "another wanted xe"
    assert xe[2].params["id"] == "last wanted xe"

def test_match_parameters():
    dom = dhtmlparser.parseString(
        """
        <root>
            <div id="1">
                <div id="5">
                    <xe id="wanted xe" />
                </div>
                <div id="10">
                    <xe id="another wanted xe" />
                </div>
                <xe id="another xe" />
            </div>
            <div id="2">
                <div id="20">
                    <xe id="last wanted xe" />
                </div>
            </div>
        </root>
        """
    )

    xe = dom.match(
        "root",
        {"tag_name": "div", "params": {"id": "1"}},
        ["div", {"id": "5"}],
        "xe"
    )

    assert len(xe) == 1
    assert first(xe).params["id"] == "wanted xe"


def test_match_parameters_relative_path():
    dom = dhtmlparser.parseString(
        """
        <root>
            <div id="1">
                <div id="5">
                    <xe id="wanted xe" />
                </div>
                <div id="10">
                    <xe id="another wanted xe" />
                </div>
                <xe id="another xe" />
            </div>
            <div id="2">
                <div id="20">
                    <xe id="last wanted xe" />
                </div>
            </div>
        </root>
        """
    )

    xe = dom.match(
        {"tag_name": "div", "params": {"id": "1"}},
        ["div", {"id": "5"}],
        "xe",
    )

    assert len(xe) == 1
    assert first(xe).params["id"] == "wanted xe"

    xe = dom.match(
        {"tag_name": "div", "params": {"id": "1"}},
        ["div", {"id": "5"}],
        "xe",
        absolute=True
    )

    assert not xe
