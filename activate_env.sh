#!/bin/bash
# Ultimate Downloader - Environment Activation Script

echo "🎬 Ultimate Multi-Platform Media Downloader"
echo "Activating virtual environment..."

# Check if virtual environment exists
if [ ! -d "youtube_downloader_env" ] && [ ! -d "downloader_env" ]; then
    echo "❌ Virtual environment not found!"
    echo "Run setup script first: ./setup.sh"
    exit 1
fi

# Activate virtual environment (prefer youtube_downloader_env if present for backward compatibility)
if [ -d "youtube_downloader_env" ]; then
    source youtube_downloader_env/bin/activate
else
    source downloader_env/bin/activate
fi

echo "✅ Virtual environment activated!"
echo "🐍 Python: $(which python)"
echo "📦 Pip: $(which pip)"
echo ""
echo "🚀 Ready to use Ultimate Downloader:"
echo "   python3 ultimate_downloader.py              # Interactive mode"
echo "   python3 ultimate_downloader.py 'URL'        # Download URL"
echo "   python3 ultimate_downloader.py --help       # Show all options"
echo ""
echo "🔧 To install additional packages: pip install <package_name>"
echo "🔚 To deactivate: deactivate"
echo ""

# Check if Ultimate Downloader exists
if [ -f "ultimate_downloader.py" ]; then
    echo "✅ Ultimate Downloader ready!"
else
    echo "⚠️  ultimate_downloader.py not found in current directory"
fi