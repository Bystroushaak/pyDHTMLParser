Changelog
=========

2.0.10
------
    - Added more tests of removeTags().
    - run_tests.sh now gets arguments.
    - Check for string in removeTags() changed to basestring from str.

2.0.9
-----
    - Fixed nasty bug which *could* cause invalid XML output.

2.0.8
-----
    - Removed _repair_tags() - it wasn't really necessary.

2.0.7
-----
    - Fixed bug in _repair_tags().

2.0.6
-----
    - Fixed behaviour of toString() and tagToString().
    - SpecialDict is now derived from OrderedDict.
    - Changed and added tests of .params attribute (OrderedDict is now used).

2.0.5
-----
    - Added new method ``.containsParamSubset()`` to ``HTMLElement``.

2.0.4
-----
    - Added op ``.__eq__()`` to the `SpecialDict`.

2.0.3
-----
    - ``.find()``; Fixed bug which prevented tag_name to be None.

2.0.2
-----
    - Fixed bugs in ``.isAlmostEqual()``.

2.0.1
-----
    - Fixed bugs in ``.match()``.
    - Fixed broken links in documentation.

2.0.0
-----
    - Rewritten, refactored, splitted to multiple files.
    - Added unittest coverage of almost 100% of the code.
    - Added better selector methods (``.wfind()``, ``.match``)
    - Added Sphinx documentation.
    - Fixed a lot of bugs.
