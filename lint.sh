#!/bin/bash
t=dictate.py

# Format imports
isort --check-only --quiet $t || isort $t

# Format code
black --line-length 120 $t

# Check code style
flake8 --max-line-length=120 $t

# Run static analysis on main package
pylint $t

