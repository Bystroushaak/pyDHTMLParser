#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
import pytest

from dhtmlparser.specialdict import SpecialDict, _lower_if_str


# Variables ===================================================================
sd = SpecialDict({
    "a": "b",
    "A": "B",
    "b": "c",
    "X": "Y"
})


# Functions & objects =========================================================
def test_constructor():
    assert len(sd) == 4


def test_in_operator():
    assert "a" in sd
    assert "B" in sd
    assert "x" in sd


def test_getting_item():
    assert sd["a"] == "b"
    assert sd["A"] == "b"
    assert sd["B"] == "c"
    assert sd["x"] == "Y"

    assert dict(sd)["A"] == "B"

    with pytest.raises(KeyError):
        dict(sd)["y"]

    with pytest.raises(KeyError):
        sd["y"]


def test_setting_item():
    sd["C"] = 1

    assert sd["C"] == 1
    assert sd["c"] == 1

    sd["a"] = 1
    assert sd["a"] == 1
    assert sd["A"] == 1


def test_get_function():
    assert sd.get("A") == "B"
    assert sd.get("a") == 1

    assert not sd.get("y")
    assert sd.get("y", "Nope") == "Nope"


def test_quality():
    first = SpecialDict({1:2, 2:3, 3:4})
    second = SpecialDict({3:4, 2:3, 1:2})

    assert first == second

    assert SpecialDict({"a": "b", "B": "a"}) == SpecialDict({"A": "b", "b": "a"})


def test_lower_if_str():
    assert _lower_if_str("ASD") == "asd"
    assert _lower_if_str(u"ASD") == u"asd"
    assert _lower_if_str(123) == 123
