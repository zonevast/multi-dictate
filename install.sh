#!/bin/bash
# Installation script for voice dictation tool
#
# This script uses a DRY approach:
# - Common packages are listed once in COMMON_PACKAGES
# - Distribution-specific package names are mapped in associative arrays
# - No package names are duplicated

echo "Voice Dictation Tool - Installation Script"

common_packages=(
    sox
    xdotool
    gsettings-desktop-schemas
    pulseaudio
)

# Detect distribution and install packages
if [ -f /etc/fedora-release ]; then
    echo "Detected distribution: Fedora"
    echo "Installing system packages..."
    sudo dnf install -y \
        "${common_packages[@]}" \
        xorg-x11-xkb-utils \
        python3-tkinter \
        python3-devel \
        pulseaudio-utils
        
elif [ -f /etc/debian_version ]; then
    echo "Detected distribution: Debian/Ubuntu"
    echo "Installing system packages..."
    sudo apt update
    sudo apt install -y \
        "${common_packages[@]}" \
        x11-xkb-utils \
        python3-tk \
        python3-dev \
        pulseaudio-utils
        
elif [ -f /etc/arch-release ]; then
    echo "Detected distribution: Arch"
    echo "Installing system packages..."
    sudo pacman -S --needed \
        "${common_packages[@]}" \
        xorg-xkbcomp \
        xorg-setxkbmap \
        tk \
        python
        
else
    echo "Warning: Unknown distribution. Please install dependencies manually."
    echo "Common packages needed: ${common_packages[@]}"
    echo "Plus XKB tools, Python GUI toolkit, and PulseAudio utilities for your distribution."
fi

# Install Python dependencies
echo ""
echo "Installing Python dependencies..."
pip install --user -r requirements.txt

# Test for missing components
if ! command -v setxkbmap &> /dev/null || ! command -v xkbcomp &> /dev/null; then
    echo "WARNING: XKB tools missing - keyboard layout detection may not work"
fi

if ! command -v pactl &> /dev/null; then
    echo "WARNING: PulseAudio missing - audio recording will not work"
fi

if ! python3 -c "from kbd_utils import get_current_keyboard_layout" 2>/dev/null; then
    echo "WARNING: Layout detection failed"
fi

echo "Run 'python3 dictate.py' to start the dictation service."