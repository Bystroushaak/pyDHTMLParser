#! /usr/bin/env sh
export PYTHONPATH="src:$PYTHONPATH"

python -m pytest tests $@
python3 -m pytest tests $@