#!/bin/bash
# Restart multi-dictate service

echo "🔄 Restarting multi-dictate..."

# Kill existing processes
pkill -f "multi_dictate.dictate" 2>/dev/null
sleep 1

# Start the service
cd /home/yousef/multi-dictate
python3 -m multi_dictate.dictate &

sleep 2

# Check if running
if pgrep -f "multi_dictate.dictate" > /dev/null; then
    echo "✅ multi-dictate started successfully!"
    echo "📊 Process ID: $(pgrep -f 'multi_dictate.dictate')"
    echo ""
    echo "Configuration:"
    echo "  - Model: gemini-2.5-flash"
    echo "  - API Keys: 2 keys with automatic fallback"
    echo ""
    echo "Keyboard shortcuts:"
    echo "  - Super+F8: AI-enhanced recording (with clipboard)"
    echo "  - Super+F7: AI-enhanced recording (clean)"
else
    echo "❌ Failed to start multi-dictate"
    exit 1
fi
