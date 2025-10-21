#!/bin/bash
# Uninstallation script for voice dictation tool

set -e

echo "Multi-Dictate - Uninstallation Script"
echo "====================================="

# Check if running with proper permissions
if [ "$EUID" -eq 0 ]; then
   echo "Please run this script as a normal user (without sudo)."
   echo "The script will ask for sudo permission when needed."
   exit 1
fi

echo ""
echo "This will remove the dictation service and all installed files."
read -p "Continue? (y/N) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Uninstallation cancelled."
    exit 0
fi

# Stop and disable the service
echo ""
echo "Stopping dictate service..."
systemctl --user stop dictate.service 2>/dev/null || true

echo "Disabling dictate service..."
systemctl --user disable dictate.service 2>/dev/null || true

# Remove service file
echo "Removing service file..."
rm -f ~/.config/systemd/user/dictate.service

# Reload systemd
systemctl --user daemon-reload

# Uninstall the Python package
echo "Uninstalling multi-dictate package..."
pip uninstall -y multi-dictate 2>/dev/null || true

# Remove desktop entry
DESKTOP_FILE="$HOME/.local/share/applications/multi-dictate.desktop"
if [ -f "$DESKTOP_FILE" ]; then
    echo "Removing desktop entry..."
    rm -f "$DESKTOP_FILE"
fi

# Ask about removing configuration files
echo ""
read -p "Remove configuration files? (y/N) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    CONFIG_DIR="$HOME/.config/multi-dictate"
    if [ -d "$CONFIG_DIR" ]; then
        echo "Removing configuration directory..."
        rm -rf "$CONFIG_DIR"
    fi
fi

# Remove FIFO if it exists
if [ -p /tmp/dictate_trigger ]; then
    echo "Removing FIFO pipe..."
    rm -f /tmp/dictate_trigger
fi

# Remove PID file if it exists
if [ -f /tmp/dictate.pid ]; then
    echo "Removing PID file..."
    rm -f /tmp/dictate.pid
fi

echo ""
echo "✅ Uninstallation complete!"
echo ""
echo "Note: System packages and Python dependencies were not removed."
echo "To remove Python dependencies, run: pip uninstall -r requirements.txt"
