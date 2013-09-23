#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
import dhtmlparser as d

s = """
<root>
	<object1>Content of first object</object1>
	<object2>Second objects content</object2>
</root>
"""

dom = d.parseString(s)

print dom
print "---\nRemove all <object1>:\n---\n"

# remove all <object1>
for e in dom.find("object1"):
	dom.removeChild(e)


print dom.prettify()


#* Prints: *********************************************************************
"""
<root>
	<object1>Content of first object</object1>
	<object2>Second objects content</object2>
</root>

---
Remove all <object1>:
---

<root>
  <object2>Second objects content</object2>
</root>
"""
#*******************************************************************************