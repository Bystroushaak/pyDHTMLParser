#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
from dhtmlparser import *

# if inside container (or other tag), create endtag automatically
print HTMLElement([
	HTMLElement("<xe>")
])
"""
Writes:

<xe>
</xe>
"""

#-------------------------------------------------------------------------------

# if not inside container, elements are left unclosed 
print HTMLElement("<xe>")
"""
Writes only:

<xe>
"""