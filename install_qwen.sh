#!/bin/bash
# Installation script for Ollama and Qwen models

echo "🤖 Installing Ollama and Qwen Models"
echo "=================================="

# Check if Ollama is already installed
if command -v ollama &> /dev/null; then
    echo "✅ Ollama is already installed"
    ollama --version
else
    echo "📥 Installing Ollama..."

    # Download and install Ollama
    curl -fsSL https://ollama.ai/install.sh | sh

    # Check if installation was successful
    if command -v ollama &> /dev/null; then
        echo "✅ Ollama installed successfully!"
    else
        echo "❌ Ollama installation failed"
        echo "Please install manually from: https://ollama.ai/download"
        exit 1
    fi
fi

echo ""
echo "📥 Downloading Qwen models..."

# Download Qwen Turbo (fast, 7B)
echo "Downloading Qwen Turbo (7B parameters)..."
ollama pull qwen-turbo

# Check if download was successful
if ollama list | grep -q "qwen-turbo"; then
    echo "✅ Qwen Turbo downloaded successfully!"
else
    echo "⚠️  Qwen Turbo download may have failed"
fi

echo ""
echo "🎯 Testing Qwen installation..."
ollama list

echo ""
echo "📋 Usage Examples:"
echo "  # Quick optimization:"
echo "  python3 optimize.py \"your prompt\" --clipboard \"/path/to/project\""
echo ""
echo "  # Qwen with AI response (if Ollama working):"
echo "  python3 qwen_optimize.py prompt \"your prompt\" --clipboard \"/path/to/project\""
echo ""
echo "  # Test models:"
echo "  python3 qwen_optimize.py models"
echo ""
echo "  # Interactive mode:"
echo "  python3 qwen_optimize.py interactive"
echo ""
echo "✅ Installation complete! Ready to optimize prompts with Qwen!"