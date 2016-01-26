#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
import pytest

from dhtmlparser.specialdict import SpecialDict, _lower_if_str


# Variables ===================================================================
sd = SpecialDict([
    ("a", "b"),
    ("A", "B"),
    ("b", "c"),
    ("X", "Y"),
])


# Functions & objects =========================================================
def test_constructor():
    assert len(sd) == 3


def test_in_operator():
    assert "a" in sd
    assert "A" in sd
    assert "B" in sd
    assert "x" in sd


def test_getting_item():
    assert sd["a"] == "B"
    assert sd["A"] == "B"
    assert sd["B"] == "c"
    assert sd["x"] == "Y"

    assert list(sd) == ["A", "b", "X"]
    assert dict(sd)["A"] == "B"

    with pytest.raises(KeyError):
        dict(sd)["y"]

    with pytest.raises(KeyError):
        sd["y"]


def test_keys():
    assert sd.keys() == ["A", "b", "X"]


def test_iterkeys():
    assert list(sd.iterkeys()) == ["A", "b", "X"]


def test_items():
    assert sd.items() == [("A", "B"), ("b", "c"), ("X", "Y")]


def test_iteritems():
    assert list(sd.iteritems()) == [("A", "B"), ("b", "c"), ("X", "Y")]


def test_iteration():
    assert list(sd) == ["A", "b", "X"]


def test_setting_item():
    sd["C"] = 1

    assert sd["C"] == 1
    assert sd["c"] == 1

    sd["A"] = 1
    assert sd["a"] == 1
    assert sd["A"] == 1


def test_get_function():
    assert sd.get("A") == 1
    assert sd.get("a") == 1

    assert not sd.get("y")
    assert sd.get("y", "Nope") == "Nope"


def test_equality():
    first = SpecialDict({1: 2, 2: 3, 3: 4})
    second = SpecialDict({3: 4, 2: 3, 1: 2})

    assert first == second

    assert SpecialDict([("a", "b"), ("B", "a")]) == SpecialDict([("A", "b"), ("b", "a")])

    assert first == first
    assert SpecialDict({2: 3}) != SpecialDict({1: 2})
    assert SpecialDict({1: 2, 2: 3, 3: 4}) != "potato"


def test_lower_if_str():
    assert _lower_if_str("ASD") == "asd"
    assert _lower_if_str(u"ASD") == u"asd"
    assert _lower_if_str(123) == 123
