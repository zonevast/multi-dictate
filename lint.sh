#!/bin/bash

t="dictate.py kbd_utils.py"

# Format imports
isort --check-only --quiet $t || isort $t

# Format code
black --line-length 100 $t

# Check code style
flake8 --max-line-length=100 $t

# Run static analysis on main package
pylint $t

sort requirements.txt -o requirements.txt

ctags $t
