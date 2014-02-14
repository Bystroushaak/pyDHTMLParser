#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Author:  Bystroushaak (bystrousak@kitakitsune.org)

This version doens't corresponds with DHTMLParser v1.5.0 - there were updates,
which makes both parsers incompatible.

This work is licensed under a Creative Commons 3.0 Unported License
(http://creativecommons.org/licenses/by/3.0/cz/).

Project page; https://github.com/Bystroushaak/pyDHTMLParser
"""



# Nonpair tags
NONPAIR_TAGS = [
	"br",
	"hr",
	"img",
	"input",
	#"link",
	"meta",
	"spacer",
	"frame",
	"base"
]



def unescape(inp, quote = '"'):
	if len(inp) < 2:
		return inp

	output = ""
	unesc = False
	for act in inp:
		if act == quote and unesc:
			output = output[:-1]

		output += act

		if act == "\\":
			unesc = not unesc
		else:
			unesc = False

	return output


def escape(input, quote = '"'):
	output = ""

	for c in input:
		if c == quote:
			output += '\\'

		output += c

	return output


def rotate_buff(buff):
	"Rotate buffer (for each buff[i] = buff[i-1])"
	i = len(buff) - 1
	while i > 0:
		buff[i] = buff[i - 1]
		i -= 1

	return buff


class SpecialDict(dict):
	"""
	This dictionary stores items case sensitive, but compare them case
	INsensitive.
	"""
	def __contains__(self, k):
		for item in super(SpecialDict, self).keys():
			if k.lower() == item.lower():
				return True

	def __getitem__(self, k):
		for item in self.keys():
			if k.lower() == item.lower():
				return super(SpecialDict, self).__getitem__(item)



class HTMLElement():
	"""
	Container for parsed html elements.
	"""

	def __init__(self, tag = "", second = None, third = None):
		self.__element = None
		self.__tagname = ""

		self.__istag        = False
		self.__isendtag     = False
		self.__iscomment    = False
		self.__isnonpairtag = False

		self.childs = []
		self.params = SpecialDict()
		self.endtag = None
		self.openertag = None

		# blah, constructor overloading in python sux :P
		if isinstance(tag, str) and second is None and third is None:
			self.__init_tag(tag)
		elif isinstance(tag, str) and isinstance(second, dict) and third is None:
			self.__init_tag_params(tag, second)
		elif isinstance(tag, str) and isinstance(second, dict) and     \
		     (isinstance(third, list) or isinstance(third, tuple)) and \
		     len(third) > 0 and isinstance(third[0], HTMLElement):

			# containers with childs are automatically considered tags
			if tag.strip() != "":
				if not tag.startswith("<"):
					tag = "<" + tag
				if not tag.endswith(">"):
					tag += ">"
			self.__init_tag_params(tag, second)
			self.childs = closeElements(third)
			self.endtag = HTMLElement("</" + self.getTagName() + ">")
		elif isinstance(tag, str) and (isinstance(second, list) or \
			 isinstance(second, tuple)) and len(second) > 0 and    \
			 isinstance(second[0], HTMLElement):

			# containers with childs are automatically considered tags
			if tag.strip() != "":
				if not tag.startswith("<"):
					tag = "<" + tag
				if not tag.endswith(">"):
					tag += ">"

			self.__init_tag(tag)
			self.childs = closeElements(second)
			self.endtag = HTMLElement("</" + self.getTagName() + ">")
		elif (isinstance(tag, list) or isinstance(tag, tuple)) and len(tag) > 0 \
		     and isinstance(tag[0], HTMLElement):
			self.__init_tag("")
			self.childs = closeElements(tag)
		else:
			raise Exception("Oh no, not this crap!")


	#===========================================================================
	#= Constructor overloading =================================================
	#===========================================================================
	def __init_tag(self, tag):
			self.__element = tag

			self.__parseIsTag()
			self.__parseIsComment()

			if (not self.__istag) or self.__iscomment:
				self.__tagname = self.__element
			else:
				self.__parseTagName()

			if self.__iscomment or not self.__istag:
				return

			self.__parseIsEndTag()
			self.__parseIsNonPairTag()

			if self.__istag and (not self.__isendtag) or "=" in self.__element:
				self.__parseParams()


	# used when HTMLElement(tag, params) is called - basically create string
	# from tagname and params
	def __init_tag_params(self, tag, params):
		tag = tag.strip().replace(" ", "")
		nonpair = ""

		if tag.startswith("<"):
			tag = tag[1:]

		if tag.endswith("/>"):
			tag = tag[:-2]
			nonpair = " /"
		elif tag.endswith(">"):
			tag = tag[:-1]

		output = "<" + tag

		for key in params.keys():
			output += " " + key + '="' + escape(params[key], '"') + '"'

		self.__init_tag(output + nonpair + ">")


	def find(self, tag_name, params = None, fn = None, case_sensitive = False):
		"""
		Same as findAll, but without endtags. You can always get them from
		.endtag property..
		"""

		dom = self.findAll(tag_name, params, fn, case_sensitive)

		return filter(lambda x: not x.isEndTag(), dom)


	def findB(self, tag_name, params = None, fn = None, case_sensitive = False):
		"""
		Same as findAllB, but without endtags. You can always get them from
		.endtag property..
		"""

		dom = self.findAllB(tag_name, params, fn, case_sensitive)

		return filter(lambda x: not x.isEndTag(), dom)


	def findAll(self, tag_name, params = None, fn = None, case_sensitive = False):
		"""
		Simple search engine using Depth-first algorithm
		http://en.wikipedia.org/wiki/Depth-first_search.

		Finds elements and subelements which match patterns given by parameters.
		Allows searching defined by users lambda function.

		@param tag_name: Name of tag.
		@type tag_name: string

		@param params: Parameters of arg.
		@type params: dictionary

		@param fn: User defined function for search.
		@type fn: lambda function

		@param case_sensitive: Search case sensitive. Default True.
		@type case_sensitive: bool

		@return: Matches.
		@rtype: Array of HTMLElements
		"""
		output = []

		if self.isAlmostEqual(tag_name, params, fn, case_sensitive):
			output.append(self)

		tmp = []
		for el in self.childs:
			tmp = el.findAll(tag_name, params, fn, case_sensitive)

			if tmp is not None and len(tmp) > 0:
				output.extend(tmp)

		return output


	def findAllB(self, tag_name, params = None, fn = None, case_sensitive = False):
		"""
		Simple search engine using Breadth-first algorithm
		http://en.wikipedia.org/wiki/Breadth-first_search.

		Finds elements and subelements which match patterns given by parameters.
		Allows searching defined by users lambda function.

		@param tag_name: Name of tag.
		@type tag_name: string

		@param params: Parameters of arg.
		@type params: dictionary

		@param fn: User defined function for search.
		@type fn: lambda function

		@param case_sensitive: Search case sensitive. Default True.
		@type case_sensitive: bool

		@return: Matches.
		@rtype: Array of HTMLElements
		"""
		output = []

		if self.isAlmostEqual(tag_name, params, fn, case_sensitive):
			output.append(self)

		breadth_search = self.childs
		for el in breadth_search:
			if el.isAlmostEqual(tag_name, params, fn, case_sensitive):
				output.append(el)

			if len(el.childs) > 0:
				breadth_search.extend(el.childs)

		return output


	#==========================================================================
	#= Parsers ================================================================
	#==========================================================================
	def __parseIsTag(self):
		if self.__element.startswith("<") and self.__element.endswith(">"):
			self.__istag = True
		else:
			self.__istag = False


	def __parseIsEndTag(self):
		last = ""
		self.__isendtag = False

		if self.__element.startswith("<") and self.__element.endswith(">"):
			for c in self.__element:
				if c == "/" and last == "<":
					self.__isendtag = True
				if ord(c) > 32:
					last = c


	def __parseIsNonPairTag(self):
		last = ""
		self.__isnonpairtag = False

		# Tags endings with /> are nonpair - do not mind whitespaces (< 32)
		if self.__element.startswith("<") and self.__element.endswith(">"):
			for c in self.__element:
				if c == ">" and last == "/":
					self.__isnonpairtag = True
					return
				if ord(c) > 32:
					last = c

		# Check listed nonpair tags
		if self.__tagname.lower() in NONPAIR_TAGS:
			self.__isnonpairtag = True


	def __parseIsComment(self):
		if self.__element.startswith("<!--") and self.__element.endswith("-->"):
			self.__iscomment = True
		else:
			self.__iscomment = False


	def __parseTagName(self):
		for el in self.__element.split(" "):
			el = el.replace("/", "").replace("<", "").replace(">", "")
			if len(el) > 0:
				self.__tagname = el.rstrip()
				return


	def __parseParams(self):
		# check if there are any parameters
		if " " not in self.__element or "=" not in self.__element:
			return

		# Remove '<' & '>'
		params = self.__element.strip()[1:-1].strip()
		# Remove tagname
		params = params[
			params.find(self.getTagName()) + len(self.getTagName()):
		].strip()

		# Parser machine
		next_state = 0
		key = ""
		value = ""
		end_quote = ""
		buff = ["", ""]
		for c in params:
			if next_state == 0:  # key
				if c.strip() != "":  # safer than list space, tab and all possible whitespaces in UTF
					if c == "=":
						next_state = 1
					else:
						key += c
			elif next_state == 1:  # value decisioner
				if c.strip() != "":  # skip whitespaces
					if c == "'" or c == '"':
						next_state = 3
						end_quote = c
					else:
						next_state = 2
						value += c
			elif next_state == 2:  # one word parameter without quotes
				if c.strip() == "":
					next_state = 0
					self.params[key] = value
					key = ""
					value = ""
				else:
					value += c
			elif next_state == 3:  # quoted string
				if c == end_quote and (buff[0] != "\\" or (buff[0]) == "\\" and buff[1] == "\\"):
					next_state = 0
					self.params[key] = unescape(value, end_quote)
					key = ""
					value = ""
					end_quote = ""
				else:
					value += c

			buff = rotate_buff(buff)
			buff[0] = c

		if key != "":
			if end_quote != "" and value.strip() != "":
				self.params[key] = unescape(value, end_quote)
			else:
				self.params[key] = value

		if len(filter(lambda x: x == "/", self.params.keys())) > 0:
			del self.params["/"]
			self.__isnonpairtag = True

	#* /Parsers ****************************************************************


	#===========================================================================
	#= Getters =================================================================
	#===========================================================================
	def isTag(self):
		"True if element is tag (not content)."
		return self.__istag


	def isEndTag(self):
		"True if HTMLElement is end tag (/tag)."
		return self.__isendtag


	def isNonPairTag(self, isnonpair = None):
		"""
		Returns True if HTMLElement is listed nonpair tag table (br for example)
		or if it ends with / - <br /> for example.

		You can also change state from pair to nonpair if you use this as setter.
		"""
		if isnonpair is None:
			return self.__isnonpairtag
		else:
			self.__isnonpairtag = isnonpair
			if not isnonpair:
				self.endtag = None
				self.childs = []


	def isPairTag(self):
		"""
		Return True if this is paired tag - <body> .. </body> for example.
		"""
		if self.isComment() or self.isNonPairTag:
			return False
		if self.isEndTag():
			return True
		if self.isOpeningTag() and self.endtag is not None:
			return True

		return False


	def isComment(self):
		"True if HTMLElement is html comment."
		return self.__iscomment


	def isOpeningTag(self):
		"True if is opening tag."
		if self.isTag() and (not self.isComment()) and (not self.isEndTag()) \
		   and (not self.isNonPairTag()):
			return True
		else:
			return False


	def isEndTagTo(self, opener):
		"Returns true, if this element is endtag to opener."
		if self.__isendtag and opener.isOpeningTag():
			if self.__tagname.lower() == opener.getTagName().lower():
				return True
			else:
				return False
		else:
			return False


	def tagToString(self):
		"Returns tag (with parameters), without content or endtag."
		if len(self.params) <= 0:
			return self.__element
		else:
			output = "<" + str(self.__tagname)

			for key in self.params.keys():
				output += " " + key + "=\"" + escape(self.params[key], '"') + "\""

			return output + " />" if self.__isnonpairtag else output + ">"


	def getTagName(self):
		"Returns tag name."
		return self.__tagname


	def getContent(self):
		"Returns content of tag (everything between opener and endtag)."
		output = ""

		for c in self.childs:
			if not c.isEndTag():
				output += c.toString()

		if output.endswith("\n"):
			output = output[:-1]

		return output


	def prettify(self, depth = 0, separator = "  ", last = True, pre = False, inline = False):
		"Returns prettifyied tag with content."
		output = ""

		if self.getTagName() != "" and self.tagToString().strip() == "":
			return ""

		# if not inside <pre> and not inline, shift tag to the right
		if not pre and not inline:
			output += (depth * separator)

		# for <pre> set 'pre' flag
		if self.getTagName().lower() == "pre" and self.isOpeningTag():
			pre = True
			separator = ""

		output += self.tagToString()

		# detect if inline
		is_inline = inline  # is_inline shows if inline was set by detection, or as parameter
		for c in self.childs:
			if not (c.isTag() or c.isComment()):
				if len(c.tagToString().strip()) != 0:
					inline = True

		# don't shift if inside container (containers have blank tagname)
		original_depth = depth
		if self.getTagName() != "":
			if not pre and not inline:  # inside <pre> doesn't shift tags
				depth += 1
				if self.tagToString().strip() != "":
					output += "\n"

		# prettify childs
		for e in self.childs:
			if not e.isEndTag():
				output += e.prettify(depth, last = False, pre = pre, inline = inline)

		# endtag
		if self.endtag is not None:
			if not pre and not inline:
				output += ((original_depth) * separator)

			output += self.endtag.tagToString().strip()

			if not is_inline:
				output += "\n"

		return output

	#* /Getters ****************************************************************


	#===========================================================================
	#= Operators ===============================================================
	#===========================================================================
	def toString(self, original = False):
		"""
		Returns almost original string (use original = True if you want exact copy).

		If you want prettified string, try .prettify()

		If original == True, return parsed element, so if you changed something
		in .params, there will be no traces of those changes.
		"""
		output = ""

		if self.childs != [] or self.isOpeningTag():
			output += self.__element if original else self.tagToString()

			for c in self.childs:
				output += c.toString(original)

			if self.endtag is not None:
				output += self.endtag.tagToString()
		elif not self.isEndTag():
			output += self.tagToString()

		return output


	def __str__(self):
		return self.toString()


	def isAlmostEqual(self, tag_name, params = None, fn = None, case_sensitive = False):
		"""
		Compare element with given tagname, params and/or by lambda function.

		Lambda function is same as in .find().
		"""

		if isinstance(tag_name, HTMLElement):
			return self.isAlmostEqual(tag_name.getTagName(), self.params)

		# search by lambda function
		if fn is not None:
			if fn(self):
				return True

		if not case_sensitive:
			self.__tagname = self.__tagname.lower()
			tag_name = tag_name.lower()

		# compare tagname
		if self.__tagname == tag_name and self.__tagname != "" and self.__tagname is not None:
			# compare parameters
			if params is None or len(params) == 0:
				return True
			elif len(self.params) > 0:
				for key in params.keys():
					if key not in self.params:
						return False
					elif params[key] != self.params[key]:
						return False

				return True

		return False

	#* /Operators **************************************************************


	#===========================================================================
	#= Setters =================================================================
	#===========================================================================
	def replaceWith(self, el):
		"""
		Replace element. Useful when you don't want change all references to object.
		"""
		self.childs = el.childs
		self.params = el.params
		self.endtag = el.endtag
		self.openertag = el.openertag

		self.__tagname = el.getTagName()
		self.__element = el.tagToString()

		self.__istag = el.isTag()
		self.__isendtag = el.isEndTag()
		self.__iscomment = el.isComment()
		self.__isnonpairtag = el.isNonPairTag()


	def removeChild(self, child, end_tag_too = True):
		"""
		Remove subelement (child) specified by reference.

		This can't be used for removing subelements by value! If you want do
		such thing, do:

		---
		for e in dom.find("value"):
			dom.removeChild(e)
		---

		Params:
			child
				child which will be removed from dom (compared by reference)
			end_tag_too
				remove end tag too - default true
		"""

		if len(self.childs) <= 0:
			return

		end_tag = None
		if end_tag_too:
			end_tag = child.endtag

		for e in self.childs:
			if e == child:
				self.childs.remove(e)
			if end_tag_too and end_tag == e and end_tag is not None:
				self.childs.remove(e)
			else:
				e.removeChild(child, end_tag_too)

	#* /Setters ****************************************************************



def closeElements(childs):
	"Close tags - used in some constructors"

	o = []

	# Close all unclosed pair tags
	for e in childs:
		if e.isTag():
			if not e.isNonPairTag() and not e.isEndTag() and not e.isComment() and e.endtag is None:
				e.childs = closeElements(e.childs)

				o.append(e)
				o.append(HTMLElement("</" + e.getTagName() + ">"))

				# Join opener and endtag
				e.endtag = o[-1]
				o[-1].openertag = e
			else:
				o.append(e)
		else:
			o.append(e)

	return o



def __raw_split(itxt):
	"""
	Parse HTML from text into array filled with tags end text.

	Source code is little bit unintutive, because it is simple parser machine.
	For better understanding, look at;
	http://kitakitsune.org/images/field_parser.png
	"""
	echr = ""
	buff = ["", "", "", ""]
	content = ""
	array = []
	next_state = 0
	inside_tag = False

	for c in itxt:
		if next_state == 0:  # content
			if c == "<":
				if len(content) > 0:
					array.append(content)
				content = c
				next_state = 1
				inside_tag = False
			else:
				content += c
		elif next_state == 1:  # html tag
			if c == ">":
				array.append(content + c)
				content = ""
				next_state = 0
			elif c == "'" or c == '"':
				echr = c
				content += c
				next_state = 2
			elif c == "-" and buff[0] == "-" and buff[1] == "!" and buff[2] == "<":
				if len(content[:-3]) > 0:
					array.append(content[:-3])
				content = content[-3:] + c
				next_state = 3
			else:
				if c == "<":  # jump back into tag instead of content
					inside_tag = True
				content += c
		elif next_state == 2:  # "" / ''
			if c == echr and (buff[0] != "\\" or (buff[0] == "\\" and buff[1] == "\\")):
				next_state = 1
			content += c
		elif next_state == 3:  # html comments
			if c == ">" and buff[0] == "-" and buff[1] == "-":
				if inside_tag:
					next_state = 1
				else:
					next_state = 0
				inside_tag = False

				array.append(content + c)
				content = ""
			else:
				content += c

		# rotate buffer
		buff = rotate_buff(buff)
		buff[0] = c

	if len(content) > 0:
		array.append(content)

	return array



def __repair_tags(raw_input):
	"""
	Repair tags with comments (<HT<!-- asad -->ML> is parsed to
	["<HT", "<!-- asad -->", "ML>"]	and I need ["<HTML>", "<!-- asad -->"])
	"""
	ostack = []

	index = 0
	while index < len(raw_input):
		el = raw_input[index]

		if el.isComment():
			if index > 0 and index < len(raw_input) - 1:
				if raw_input[index - 1].tagToString().startswith("<") and raw_input[index + 1].tagToString().endswith(">"):
					ostack[-1] = HTMLElement(ostack[-1].tagToString() + raw_input[index + 1].tagToString())
					ostack.append(el)
					index += 1
					continue

		ostack.append(el)

		index += 1

	return ostack



def __indexOfEndTag(istack):
	"""
	Go through istack and search endtag. Element at first index is considered as
	opening tag.

	Returns: index of end tag or 0 if not found.
	"""
	if len(istack) <= 0:
		return 0

	if not istack[0].isOpeningTag():
		return 0

	opener = istack[0]
	cnt = 0

	index = 0
	for el in istack[1:]:
		if el.isOpeningTag() and (el.getTagName().lower() == opener.getTagName().lower()):
			cnt += 1
		elif el.isEndTagTo(opener):
			if cnt == 0:
				return index + 1
			else:
				cnt -= 1

		index += 1

	return 0



def __parseDOM(istack):
	"Recursively go through element array and create DOM."
	ostack = []
	end_tag_index = 0

	index = 0
	while index < len(istack):
		el = istack[index]

		end_tag_index = __indexOfEndTag(istack[index:])  # Check if this is pair tag

		if not el.isNonPairTag() and end_tag_index == 0 and not el.isEndTag():
			el.isNonPairTag(True)

		if end_tag_index != 0:
			el.childs = __parseDOM(istack[index + 1: end_tag_index + index])
			el.endtag = istack[end_tag_index + index]  # Reference to endtag
			el.endtag.openertag = el
			ostack.append(el)
			ostack.append(el.endtag)
			index = end_tag_index + index
		else:
			if not el.isEndTag():
				ostack.append(el)

		index += 1

	return ostack



def parseString(txt):
	"""
	Parse given string and return DOM tree consisting of single linked
	HTMLElements.
	"""
	istack = []

	# remove UTF BOM (prettify fails if not)
	if len(txt) > 3 and txt.startswith("\xef\xbb\xbf"):
		txt = txt[3:]

	for el in __raw_split(txt):
		istack.append(HTMLElement(el))

	container = HTMLElement()
	container.childs = __parseDOM(__repair_tags(istack))

	return container



def makeDoubleLinked(dom, parent = None):
	"""
	Standard output from dhtmlparser is single-linked tree. This will make it 
	double-linked.
	"""
	dom.parent = parent

	if len(dom.childs) > 0:
		for child in dom.childs:
			child.parent = dom
			makeDoubleLinked(child, dom)



def removeTags(dom):
	"""
	Remove all tags from dom, so result should be plaintext.

	dom -- string, HTMLElement or just array of elements.
	"""
	output = ""

	# initialize stack with proper value (based on dom parameter)
	element_stack = None
	if isinstance(dom, list) or isinstance(dom, tuple):
		element_stack = dom
	elif isinstance(dom, HTMLElement):
		if not dom.isTag():
			element_stack = [dom]
		else:
			element_stack = dom.childs
	elif isinstance(dom, str):
		element_stack = parseString(dom).childs
	else:
		element_stack = dom

	# remove all tags
	while len(element_stack) > 0:
		el = element_stack.pop(0)

		if not (el.isTag() or el.isComment() or el.getTagName() == ""):
			output += str(el)

		if len(el.childs) > 0:
			element_stack = el.childs + element_stack

	return output


#==============================================================================
#= Main program ===============================================================
#==============================================================================
if __name__ == "__main__":
	print "Testing.."

	assert unescape(r"""\' \\ \" \n""")      == r"""\' \\ " \n"""
	assert unescape(r"""\' \\ \" \n""", "'") == r"""' \\ \" \n"""
	assert unescape(r"""\' \\" \n""")        == r"""\' \\" \n"""
	assert unescape(r"""\' \\" \n""")        == r"""\' \\" \n"""
	assert unescape(r"""printf(\"hello \t world\");""") == r"""printf("hello \t world");"""

	assert escape(r"""printf("hello world");""") == r"""printf(\"hello world\");"""
	assert escape(r"""'""", "'") == r"""\'"""

	dom = parseString("""
		"<div Id='xe' a='b'>obsah xe divu</div> <!-- Id, not id :) -->
		 <div id='xu' a='b'>obsah xu divu</div>
	""")

	# find test
	divXe = dom.find("div", {"id": "xe"})[0]
	divXu = dom.find("div", {"id": "xu"})[0]

	# assert divXe.tagToString() == """<div a="b" id="xe">"""
	# assert divXu.tagToString() == """<div a="b" id="xu">"""

	# unit test for toString
	assert divXe.toString() == """<div a="b" Id="xe">obsah xe divu</div>"""
	assert divXu.toString() == """<div a="b" id="xu">obsah xu divu</div>"""

	# getTagName() test
	assert divXe.getTagName() == "div"
	assert divXu.getTagName() == "div"

	# isComment() test
	assert divXe.isComment() is False
	assert divXe.isComment() == divXu.isComment()

	assert divXe.isNonPairTag() != divXe.isOpeningTag()

	assert divXe.isTag() is True
	assert divXe.isTag() == divXu.isTag()

	assert divXe.getContent() == "obsah xe divu"

	# find()/findB() test
	dom = parseString("""
		<div id=first>
			First div.
			<div id=first.subdiv>
				Subdiv in first div.
			</div>
		</div>
		<div id=second>
			Second.
		</div>
	""")

	assert dom.find("div")[1].getContent().strip() == "Subdiv in first div."
	assert dom.findB("div")[1].getContent().strip() == "Second."

	# test removeTags()
	assert removeTags(divXe) == "obsah xe divu"
	assert removeTags(parseString("a<b>xax<i>xe</i>xi</b>d")) == "axaxxexid"

	print "Everything ok."
