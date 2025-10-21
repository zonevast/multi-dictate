#!/bin/bash
# Installation script for voice dictation tool
#
# This script:
# - Installs system dependencies
# - Installs Python dependencies
# - Sets up the application in /opt/dictate
# - Creates a systemd service for auto-start on boot
# - Creates system-wide command 'dictate'

set -e  # Exit on error

echo "Multi-Dictate - Installation Script"
echo "==================================="

# Check if running with proper permissions
if [ "$EUID" -eq 0 ]; then
   echo "Please run this script as a normal user (without sudo)."
   echo "The script will ask for sudo permission when needed."
   exit 1
fi

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

echo ""
echo "Setting up application..."

# Create user config directory
CONFIG_DIR="$HOME/.config/multi-dictate"
echo "Creating configuration directory..."
mkdir -p "$CONFIG_DIR"

# Copy configuration files to user directory
if [ ! -f "$CONFIG_DIR/dictate.yaml" ]; then
    echo "Installing default configuration..."
    cp dictate.yaml "$CONFIG_DIR/"
fi

# Copy keyboard configuration
cp keyboard.yaml "$CONFIG_DIR/"

# Install the Python package
echo "Installing multi-dictate package..."
pip install --user -e .

# Install desktop entry for GUI launchers
if [ -f dictate.desktop ]; then
    echo "Installing desktop entry..."
    DESKTOP_DIR="$HOME/.local/share/applications"
    mkdir -p "$DESKTOP_DIR"
    sed "s|Exec=%h/.local/bin/multi-dictate|Exec=$HOME/.local/bin/multi-dictate|g" dictate.desktop > "$DESKTOP_DIR/multi-dictate.desktop"
fi

# Set up systemd service
echo ""
echo "Setting up systemd service..."

# Create user systemd directory if it doesn't exist
mkdir -p ~/.config/systemd/user/

# Copy service file to user directory
cp dictate.service ~/.config/systemd/user/

# Reload systemd daemon
systemctl --user daemon-reload

# Enable the service to start on boot
echo "Enabling dictate service to start on boot..."
systemctl --user enable dictate.service

# Start the service now
echo "Starting dictate service..."
systemctl --user start dictate.service

# Check service status
sleep 2
if systemctl --user is-active --quiet dictate.service; then
    echo ""
    echo "✅ Installation successful!"
    echo ""
    echo "The dictation service is now running and will start automatically on boot."
    echo ""
    echo "Usage:"
    echo "  - Service status: systemctl --user status dictate.service"
    echo "  - Stop service:   systemctl --user stop dictate.service"
    echo "  - Start service:  systemctl --user start dictate.service"
    echo "  - View logs:      journalctl --user -u dictate.service -f"
    echo "  - Run manually:   multi-dictate [options]"
    echo ""
    echo "Default keybindings:"
    echo "  - Super+F11:     Start manual recording"
    echo "  - Super+F12:     Stop recording"
    echo "  - Super+Insert:  Toggle recording (press to talk)"
    echo "  - Ctrl+Shift+S:  Record until silence detected"
    echo ""
    echo "Configuration file: $CONFIG_DIR/dictate.yaml"
else
    echo ""
    echo "⚠️  Warning: Service installation completed but the service failed to start."
    echo "Check the logs with: journalctl --user -u dictate.service -xe"
fi
