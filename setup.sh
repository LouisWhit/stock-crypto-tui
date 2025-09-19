#!/bin/bash

# Stock & Crypto TUI Setup Script

echo "🚀 Setting up Stock & Crypto TUI..."

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

# Check Python version
python_version=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
required_version="3.8"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "❌ Python 3.8 or higher is required. Current version: $python_version"
    exit 1
fi

echo "✅ Python $python_version detected"

# Install dependencies
echo "📦 Installing Python dependencies..."
pip3 install -r requirements.txt

if [ $? -eq 0 ]; then
    echo "✅ Dependencies installed successfully"
else
    echo "❌ Failed to install dependencies"
    exit 1
fi

# Make the script executable
chmod +x stock_crypto_tui.py

# Get the current directory
current_dir=$(pwd)

# Create alias in bashrc
echo "🔧 Setting up bash alias..."

# Check if alias already exists
if grep -q "alias price=" ~/.bashrc; then
    echo "⚠️  Alias already exists in ~/.bashrc"
    read -p "Do you want to update it? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        # Remove existing alias
        sed -i '/alias price=/d' ~/.bashrc
    else
        echo "Skipping alias setup"
        exit 0
    fi
fi

# Add new alias
echo "alias price='python3 $current_dir/stock_crypto_tui.py'" >> ~/.bashrc

echo "✅ Alias added to ~/.bashrc"
echo ""
echo "🎉 Setup complete!"
echo ""
echo "To use the tool:"
echo "1. Reload your shell: source ~/.bashrc"
echo "2. Run: price AAPL BTC ETH"
echo "3. For watch mode: price --watch AAPL BTC ETH"
echo ""
echo "Configuration file: $current_dir/config.json"
echo "You can customize colors, display options, and symbols in the config file."
