#! /usr/bin/env sh
export PYTHONPATH="src:$PYTHONPATH"

python3 -m pytest tests $@