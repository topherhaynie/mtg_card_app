#!/bin/bash
# Quick setup script for MTG Card App

set -e  # Exit on error

echo "🎴 MTG Card App - Environment Setup"
echo "===================================="
echo ""

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "❌ uv is not installed!"
    echo "📦 Install it with: curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

echo "✅ uv is installed"

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "📦 Creating virtual environment..."
    uv venv .venv
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment already exists"
fi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source .venv/bin/activate

# Install dependencies
echo "📦 Installing dependencies..."
uv pip install -e ".[dev]"

echo ""
echo "✅ Setup complete!"
echo ""
echo "📋 Next steps:"
echo "  1. Activate the environment: source .venv/bin/activate"
echo "  2. Run the demo: python -m examples.data_layer_demo"
echo "  3. Read the docs: cat DATA_LAYER_SETUP.md"
echo ""
echo "🚀 Happy coding!"
