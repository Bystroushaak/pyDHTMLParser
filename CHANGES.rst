Changelog
=========

2.2.1
-----
    - Attempt to fix strange recursive inheritance problem.

2.2.0
-----
    - Rewritten for compatibility with python3.

2.1.0 - 2.1.8
-------------
    - State parser fixed - it can now recover from invalid html like ``<invalid tag=something">``.
    - Rewritten to use ``StateEnum`` in parser for better readability.
    - Garbage collector is now disabled during _raw_split().
    - Fixed #16 - recovery after tags which don't ends with ``>`` (``</code`` for example).
    - Closed #17 - implementation of ignoring of ``<`` in usage as `is smaller than` sign.
    - Restored support of multiline attributes.
    - ``.parseString()`` now doesn't try to parse HTML element parameters.
    - Implemented ``first()`` getter.
    - License changed to MIT.
    - Fixed #18: bug which in some cases caused invalid output.
    - Added HTMLElement.__repr__().
    - Added test_coverage.sh.
    - Added extended test_equality() coverage.
    - Formatting improvements.
    - Improved constructor handling, which is now much more readable.
    - Updated formatting of the setup.py.
    - Added more tests.
    - Fixed #22; bug in the SpecialDict.
    - Fixed some nasty unicode problems.
    - Fixed python 2 / 3 problem in docs/__init__.py.
    - getVersion() -> get_version().

2.0.10
------
    - Added more tests of removeTags().
    - run_tests.sh now gets arguments.
    - Check for string in removeTags() changed to basestring from str.

2.0.6 - 2.0.9
-------------
    - Fixed behaviour of toString() and tagToString().
    - SpecialDict is now derived from OrderedDict.
    - Changed and added tests of .params attribute (OrderedDict is now used).
    - Fixed bug in _repair_tags().
    - Removed _repair_tags() - it wasn't really necessary.
    - Fixed nasty bug which *could* cause invalid XML output.

2.0.1 - 2.0.5
-------------
    - Fixed bugs in ``.match()``.
    - Fixed broken links in documentation.
    - Fixed bugs in ``.isAlmostEqual()``.
    - ``.find()``; Fixed bug which prevented tag_name to be None.
    - Added op ``.__eq__()`` to the `SpecialDict`.
    - Added new method ``.containsParamSubset()`` to ``HTMLElement``.

2.0.0
-----
    - Rewritten, refactored, splitted to multiple files.
    - Added unittest coverage of almost 100% of the code.
    - Added better selector methods (``.wfind()``, ``.match``)
    - Added Sphinx documentation.
    - Fixed a lot of bugs.
