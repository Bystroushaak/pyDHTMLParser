#! /usr/bin/env sh
export PYTHONPATH="src:$PYTHONPATH"

py.test tests $@