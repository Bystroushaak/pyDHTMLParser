#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
from dhtmlparser import *

foo = HTMLElement("<xe one='param'>")
baz = HTMLElement('<xe one="param">')

assert foo != baz # references are not the same
assert foo.isAlmostEqual(baz)