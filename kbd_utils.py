#!/usr/bin/env python3
"""
Keyboard layout utilities for dictation app.
"""

import logging
import re
import subprocess

import yaml
from box import Box

logger = logging.getLogger(__name__)

try:
    with open("keyboard.yaml", "r", encoding="utf-8") as f:
        _kbd = yaml.safe_load(f) or {}
    kbd_cfg = Box(_kbd, default_box=True)
except Exception as e:
    logger.warning(f"Failed to load keyboard.yaml: {e}")
    kbd_cfg = Box({}, default_box=True)


def convert_keysym_to_char(sym):
    """
    Convert XKB keysym name or xkbcomp output to actual character.

    Args:
        sym: XKB keysym name (e.g., 'a', 'A', 'grave', 'exclam') or quoted string

    Returns:
        str: Actual character or empty string if not convertible
    """
    sym = sym.strip()

    if sym.startswith('"') and sym.endswith('"'):
        return sym[1:-1]
    elif sym.startswith("'") and sym.endswith("'"):
        return sym[1:-1]

    if len(sym) == 1 and (sym.isalnum() or sym in "!@#$%^&*()-_=+[]{}\\|;:'\",.<>/?`~"):
        return sym

    mapping = kbd_cfg.keysym_mappings
    if sym in mapping:
        return mapping[sym]

    # Check for dead keys and other special cases
    if sym.startswith("dead_") or sym.startswith("ISO_") or sym.startswith("KP_"):
        return ""

    return ""


def get_layout_key_mapping(layout_code):
    """
    Get keyboard key mapping for a specific layout by querying the system.

    Uses setxkbmap and xkbcomp to get the actual key mappings from the system.

    Args:
        layout_code: Layout code (e.g., 'us', 'de', 'fr')

    Returns:
        dict: Mapping of physical positions to characters for each shift level
    """
    kcp = kbd_cfg.keycode_positions
    try:
        # Generate XKB keymap for the specific layout and compile it
        cmd = f"setxkbmap -layout {layout_code} -print | xkbcomp -xkb - -"
        res = subprocess.run(cmd, shell=True, capture_output=True, text=True, check=True)

        if res.stderr and "WARNING: Running setxkbmap against an Xwayland server" not in res.stderr:
            logger.warning(f"xkbcomp warning: {res.stderr}")

        keymap_text = res.stdout

        if not kcp:
            logger.error("No keycode positions provided")
            return {}

        keycode_positions = {k: tuple(v) if isinstance(v, list) else v for k, v in kcp.items()}

        # Parse key definitions from xkbcomp output
        # Pattern: key <KEYCODE> { [ symbol1, symbol2, symbol3, symbol4 ] };
        # or: key <KEYCODE> { type= "ALPHABETIC", symbols[Group1]= [ symbol1, symbol2 ] };

        mapping = {}

        def process_key_match(match):
            """Process a regex match for key definition."""
            keycode = match.group(1)
            if keycode not in keycode_positions:
                return

            symbols_str = match.group(2).strip()
            symbols = [convert_keysym_to_char(sym) for sym in re.split(r",\s*", symbols_str)]

            if symbols:
                row, col = keycode_positions[keycode]
                if len(symbols) >= 1 and symbols[0]:
                    mapping[(row, col, 0)] = symbols[0]  # Unshifted
                if len(symbols) >= 2 and symbols[1]:
                    mapping[(row, col, 1)] = symbols[1]  # Shifted

        # Simple pattern for non-alphabetic keys
        for m in re.finditer(r"key\s+<([A-Z0-9]+)>\s*{\s*\[([^\]]+)\]\s*}", keymap_text):
            process_key_match(m)

        # Pattern for keys with type and symbols[Group1]
        p = r'key\s+<([A-Z0-9]+)>\s*{\s*type\s*=\s*"[^"]+",\s*symbols\[Group1\]\s*=\s*\[([^\]]+)\]'
        for m in re.finditer(p, keymap_text):
            process_key_match(m)

        return mapping

    except Exception as e:
        logger.error(f"Failed to get key mapping for layout {layout_code}: {e}")
        return {}


def get_current_keyboard_layout():
    """
    Get the current keyboard layout on GNOME/Wayland.
    Uses the MRU (Most Recently Used) sources - the first entry is the current layout.

    Returns:
        str: Current layout code (e.g., 'us', 'gb') or 'us' if unable to detect
    """
    try:
        r = subprocess.run(
            ["gsettings", "get", "org.gnome.desktop.input-sources", "mru-sources"],
            capture_output=True,
            text=True,
            check=True,
        )
        m = re.search(r"\('\w+', '(\w+)'\)", r.stdout)
        return m.group(1) if m else "us"
    except Exception:
        return "us"


# Cache for layout mappings
_layout_mappings_cache = {}


def for_typewrite(text, layout=None):
    """
    Convert text for typewriting by mapping from current layout to US layout.

    Args:
        text: Text to convert
        layout: Source layout code. If None, uses current keyboard layout

    Returns:
        str: Converted text ready for typewriting
    """
    if layout is None:
        layout = get_current_keyboard_layout()

    if layout == "us":
        return text

    # Get or build mapping for this layout
    if layout not in _layout_mappings_cache:
        # Build mapping for this specific layout

        # Get US layout mapping first as reference
        us_mapping = get_layout_key_mapping("us")
        if not us_mapping:
            logger.error("Failed to get US layout mapping")
            return text

        # Get the source layout mapping
        lm = get_layout_key_mapping(layout)
        if not lm:
            logger.warning(f"Failed to get mapping for layout {layout}")
            return text

        # Create character-to-character mapping
        char_mapping = {}
        for pos, us_char in us_mapping.items():
            if pos in lm:
                lc = lm[pos]
                if lc and not lc.startswith("U+"):
                    char_mapping[lc] = us_char

        _layout_mappings_cache[layout] = char_mapping
        logger.info(f"Built {len(char_mapping)} character mappings for layout '{layout}'")

    mapping = _layout_mappings_cache[layout]
    if not mapping:
        return text

    return "".join(mapping.get(c, c) for c in text)


def get_dictate_bindings():
    """Get dictation keybindings from dconf."""
    try:
        result = subprocess.run(
            ["dconf", "dump", "/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/"],
            capture_output=True,
            text=True,
            check=False,
        )
        if not result.stdout:
            return []

        dictate_bindings = []
        section = {}

        for line in result.stdout.strip().split("\n"):
            line = line.strip()
            if line.startswith("[") and line.endswith("]"):
                if section and "dictate_trigger" in section.get("command", ""):
                    dictate_bindings.append(section)
                section = {}
            elif "=" in line:
                m = re.match(r"^(\w+)=(.*)$", line)
                if not m:
                    continue
                key = m.group(1)
                value = m.group(2)
                # Remove outer quotes if present
                value = re.sub(r'^(["\'])(.*)(\1)$', r"\2", value)
                section[key] = value

        if section and "dictate_trigger" in section.get("command", ""):
            dictate_bindings.append(section)

        return dictate_bindings
    except Exception:
        return []


def check_dictation_keybindings():
    """Check and display custom keybindings for dictation."""
    available_commands = ["record", "stop", "toggle", "record till pause", "echo"]
    bound_commands = set()

    dictate_bindings = get_dictate_bindings()

    if dictate_bindings:
        print("\nDictation keybindings:")
        for binding in dictate_bindings:
            key = binding.get("binding", "")
            if not key:
                continue
            name = binding.get("name", "Unnamed")
            cmd = binding.get("command", "")

            # Extract the command being sent to dictate_trigger
            m = re.search(r"echo\s+([^>]+?)\s*>>", cmd)
            if m:
                bound_commands.add(m.group(1).strip())

            if key == "<Super>Insert" and cmd == 'sh -c "echo toggle >> /tmp/dictate_trigger"':
                print(f"  {key}: {name} (press to talk)")
            else:
                print(f"  {key}: {name} {cmd}")

    # Check for unbound commands
    unbound = set(available_commands) - bound_commands
    if unbound:
        print("\nCommands without keybindings:")
        for cmd in sorted(unbound):
            print(f"  {cmd}")


def test_for_typewrite():
    """Test specific known conversions for various keyboard layouts."""

    test_cases = [
        # German layout
        ("Straße", "de", "Stra-e"),
        ("Übung", "de", "{bung"),
        ("schön", "de", "sch;n"),
        ("äöü", "de", "';["),
        ("ÄÖÜ", "de", '":{'),
        ("yz", "de", "zy"),
        # Spanish layout
        ("niño", "es", "ni;o"),
        ("¿Qué?", "es", "+Qué_"),
        ("¡Hola!", "es", "=Hola!"),
        # Italian layout
        ("città", "it", "citt'"),
        ("perché", "it", "perch{"),
        ("più", "it", "pi\\"),
        # French layout
        ("café", "fr", "cqf2"),
        ("française", "fr", "frqn9qise"),
        # Russian layout
        ("Эхо", "ru", '"[j'),
        ("эхо", "ru", "'[j"),
        ("Привет", "ru", "Ghbdtn"),
        ("ёжик", "ru", "`;br"),
        # Hebrew layout
        ("שלום", "il", "akuo"),
        ("עברית", "il", "gcrh,"),
    ]

    failed = 0

    print("Testing for_typewrite() conversions:")

    for text, layout, expected in test_cases:
        try:
            result = for_typewrite(text, layout)
            if result != expected:
                print(f"{layout} <{text}> → <{result}> expected: <{expected}>")
                failed += 1
        except Exception as e:
            print(f"✗ {layout:3} {text:15} → ERROR: {e}")
            failed += 1

    print(f"{failed} fails")

    return failed == 0


if __name__ == "__main__":
    import sys

    success = test_for_typewrite()
    sys.exit(0 if success else 1)
