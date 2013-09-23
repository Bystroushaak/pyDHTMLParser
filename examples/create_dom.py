#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# DHTMLParser DOM creation example.
from dhtmlparser import *

e = HTMLElement("root", [
		HTMLElement("item", {"param1":"1", "param2":"2"}, [
			HTMLElement("<crap>", [
				HTMLElement("hello parser!")
			]),
			HTMLElement("<another_crap/>", {"with" : "params"}),
			HTMLElement("<!-- comment -->")
		]),
		HTMLElement("<item />", {"blank" : "body"})
	])

print e.prettify()

"""
Writes:

<root>
  <item param2="2" param1="1">
    <crap>hello parser!</crap>
    <another_crap with="params" />
    <!-- comment -->
  </item>
  <item blank="body" />
</root>
"""
