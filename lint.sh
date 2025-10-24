#!/bin/bash

# Files to lint
files="multi_dictate/*.py test_*.py *.py"


# Remove trailing whitespace
sed -i 's/[[:space:]]*$//' $files README.md *.sh 2>/dev/null

# Format and check
isort $files 2>/dev/null || echo "Install isort: pip install isort"
#black --line-length 100 --skip-string-normalization $files 2>/dev/null || echo "Install black: pip install black"

#autopep8 --max-line-length 100 --in-place  $files

#flake8 --max-line-length=100 --ignore=E203,W503 $files

#pylint -d C0415,W1203,R1722

sort requirements.txt -o requirements.txt

ctags $files
