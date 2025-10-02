#!/bin/bash
# Installation script for Ultimate Media Downloader v2.0

echo "════════════════════════════════════════════════════════════════"
echo "    🎬 Ultimate Media Downloader v2.0 - Installation"
echo "════════════════════════════════════════════════════════════════"
echo ""

# Check Python version
echo "✓ Checking Python version..."
python3 --version

# Check if pip3 is available
echo "✓ Checking pip3..."
if ! command -v pip3 &> /dev/null; then
    echo "✗ pip3 not found. Please install pip3."
    exit 1
fi

# Install dependencies
echo ""
echo "✓ Installing Python dependencies..."
pip3 install -r requirements.txt

# Check FFmpeg
echo ""
echo "✓ Checking FFmpeg installation..."
if ! command -v ffmpeg &> /dev/null; then
    echo "⚠ FFmpeg not found!"
    echo ""
    echo "FFmpeg is required for audio conversion."
    echo "Please install it:"
    echo ""
    echo "  macOS:   brew install ffmpeg"
    echo "  Linux:   sudo apt install ffmpeg"
    echo "  Windows: Download from https://ffmpeg.org/"
    echo ""
else
    echo "✓ FFmpeg is installed"
fi

# Make scripts executable
echo ""
echo "✓ Making scripts executable..."
chmod +x demo.py
chmod +x show_improvements.py
chmod +x activate_env.sh

echo ""
echo "════════════════════════════════════════════════════════════════"
echo "    ✅ Installation Complete!"
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "Next steps:"
echo ""
echo "  1. Run the demo:"
echo "     python3 show_improvements.py"
echo ""
echo "  2. Start the downloader:"
echo "     python3 ultimate_downloader.py"
echo ""
echo "  3. Read the documentation:"
echo "     cat README.md"
echo ""
echo "════════════════════════════════════════════════════════════════"
