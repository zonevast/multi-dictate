#!/usr/bin/env python3
"""Convenience script to run multi-dictate from development directory."""

import os
import sys

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import and run
from multi_dictate.dictate import main

if __name__ == "__main__":
    main()
