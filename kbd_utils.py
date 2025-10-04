#!/usr/bin/env python3
"""
Keyboard layout utilities for dictation app.
"""

import logging
import re
import subprocess

logger = logging.getLogger(__name__)


def get_current_keyboard_layout():
    """
    Get the current keyboard layout on GNOME/Wayland.
    Uses the MRU (Most Recently Used) sources - the first entry is the current layout.

    Returns:
        str: Current layout code (e.g., 'us', 'gb') or 'us' if unable to detect
    """
    try:
        result = subprocess.run(
            ["gsettings", "get", "org.gnome.desktop.input-sources", "mru-sources"],
            capture_output=True,
            text=True,
            check=True,
        )
        # Parse first entry from MRU list: [('xkb', 'us'), ('xkb', 'gb'), ...]
        match = re.search(r"\('\w+', '(\w+)'\)", result.stdout)
        return match.group(1) if match else "us"
    except Exception:
        return "us"


def build_layout_mappings(layouts):
    """
    Build all keyboard layout mappings from configuration.

    Args:
        layouts: Dictionary of layout definitions

    Returns:
        Dictionary of layout_name -> character mappings
    """
    mappings = {}

    if not layouts:
        logger.warning("No layouts provided")
        return mappings

    if "us" not in layouts:
        logger.error("US layout required but not found in configuration")
        return mappings

    try:
        us_rows = layouts["us"]["keys"]
    except KeyError:
        logger.error("US layout missing 'keys' field")
        return mappings

    for layout_name, layout_data in layouts.items():
        if layout_name == "us":
            continue

        layout_rows = layout_data["keys"]
        mapping = {}

        # Map all characters to their US QWERTY equivalents
        for layout_row, us_row in zip(layout_rows, us_rows):
            for layout_char, us_char in zip(layout_row, us_row):
                mapping[layout_char] = us_char
                # Add uppercase mapping if the character has a different uppercase form
                upper_layout = layout_char.upper()
                upper_us = us_char.upper()
                if upper_layout != layout_char and upper_us != us_char:
                    mapping[upper_layout] = upper_us

        mappings[layout_name] = mapping
        logger.info(f"Built {len(mapping)} character mappings for layout '{layout_name}'")

    return mappings
