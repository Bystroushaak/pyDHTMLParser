#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
from dhtmlparser.quoter import escape, unescape


# Functions & objects =========================================================
def test_unescape():
    assert unescape(r"""\' \\ \" \n""") == r"""\' \\ " \n"""
    assert unescape(r"""\' \\ \" \n""", "'") == r"""' \\ \" \n"""
    assert unescape(r"""\' \\" \n""") == r"""\' \\" \n"""
    assert unescape(r"""\' \\" \n""") == r"""\' \\" \n"""
    assert unescape(r'printf(\"hello \t world\");') == \
           r'printf("hello \t world");'

def test_escape():
    assert escape(r"'", "'") == r"""\'"""
    assert escape(r"\\", "'") == "\\\\"
    assert escape(r"""printf("hello world");""") == r"""printf(\"hello world\");"""
