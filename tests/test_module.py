#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
import dhtmlparser


# Functions & objects =========================================================
def test_raw_split():
    splitted = dhtmlparser._raw_split(
        """<html><tag params="true"></html>"""
    )

    assert splitted
    assert len(splitted) == 3
    assert splitted[0] == "<html>"
    assert splitted[1] == '<tag params="true">'
    assert splitted[2] == "</html>"


def test_raw_split_text():
    splitted = dhtmlparser._raw_split(
        """   <html>asd asd"as das</html>   """
    )

    assert splitted
    assert len(splitted) == 5
    assert splitted[0] == "   "
    assert splitted[1] == "<html>"
    assert splitted[2] == 'asd asd"as das'
    assert splitted[3] == "</html>"
    assert splitted[4] == "   "


def test_raw_split_parameters():
    splitted = dhtmlparser._raw_split(
        """<html><tag params="<html_tag>"></html>"""
    )

    assert splitted
    assert len(splitted) == 3
    assert splitted[0] == "<html>"
    assert splitted[1] == '<tag params="<html_tag>">'
    assert splitted[2] == "</html>"


def test_raw_split_parameters_quotes():
    splitted = dhtmlparser._raw_split(
        """<html><tag params="some \\"<quoted>\\" text"></html>"""
    )

    assert splitted
    assert len(splitted) == 3
    assert splitted[0] == "<html>"
    assert splitted[1] == '<tag params="some \\"<quoted>\\" text">'
    assert splitted[2] == "</html>"


def test_raw_split_comments():
    splitted = dhtmlparser._raw_split(
        """<html><!-- asd " asd" > asd --></html>"""
    )

    assert splitted
    assert len(splitted) == 3
    assert splitted[0] == "<html>"
    assert splitted[1] == '<!-- asd " asd" > asd -->'
    assert splitted[2] == "</html>"


def test_repair_tags():
    repaired = dhtmlparser._repair_tags(
        map(
            lambda x: dhtmlparser.HTMLElement(x),
            dhtmlparser._raw_split(
                '<html><tag params="true"></html>'
            )
        )
    )

    assert repaired[0].tagToString() == "<html>"
    assert repaired[1].tagToString() == '<tag params="true">'
    assert repaired[2].tagToString() == '</html>'


def test_repair_tags_bad():
    repaired = dhtmlparser._repair_tags(
        map(
            lambda x: dhtmlparser.HTMLElement(x),
            dhtmlparser._raw_split(
                '<html><tag <!-- comment --> params="true"></html>'
            )
        )
    )

    assert repaired[0].tagToString() == "<html>"
    assert repaired[1].tagToString() == '<tag params="true">'
    assert repaired[2].tagToString() == '<!-- comment -->'
    assert repaired[3].tagToString() == '</html>'


def test_index_of_end_tag():
    pass


def test_parse_dom():
    pass


def test_parseString():
    pass


def test_makeDoubleLinked():
    pass


def test_remove_tags():
    dom = dhtmlparser.parseString("a<b>xax<i>xe</i>xi</b>d")
    assert dhtmlparser.removeTags(dom) == "axaxxexid"

    dom = dhtmlparser.parseString("<b></b>")
    assert not dhtmlparser.removeTags(dom)

    dom = dhtmlparser.parseString("<b><i></b>")
    assert not dhtmlparser.removeTags(dom)

    dom = dhtmlparser.parseString("<b><!-- asd --><i></b>")
    assert not dhtmlparser.removeTags(dom)
