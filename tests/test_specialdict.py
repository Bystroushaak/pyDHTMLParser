#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
import pytest

from dhtmlparser.specialdict import SpecialDict


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