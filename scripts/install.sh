#!/bin/bash
# =============================================================================
# Ultimate Media Downloader - Local Installation Script
# Installs the package locally so you can run it with just 'umd'
# =============================================================================

set -e  # Exit on error

echo "======================================================================"
echo "  Ultimate Media Downloader - Local Installation"
echo "======================================================================"
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

echo -e "${BLUE}[1/5]${NC} Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: Python 3 is not installed.${NC}"
    echo "Please install Python 3.9 or higher from https://www.python.org/"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
echo -e "${GREEN}✓${NC} Python $PYTHON_VERSION found"

echo ""
echo -e "${BLUE}[2/5]${NC} Checking FFmpeg installation..."
if ! command -v ffmpeg &> /dev/null; then
    echo -e "${YELLOW}Warning: FFmpeg is not installed.${NC}"
    echo "FFmpeg is required for audio conversion and video processing."
    echo ""
    echo "To install FFmpeg:"
    echo "  macOS:   brew install ffmpeg"
    echo "  Linux:   sudo apt install ffmpeg  (Ubuntu/Debian)"
    echo "           sudo yum install ffmpeg  (CentOS/RHEL)"
    echo "  Windows: Download from https://ffmpeg.org/download.html"
    echo ""
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
else
    echo -e "${GREEN}✓${NC} FFmpeg found"
fi

echo ""
echo -e "${BLUE}[3/5]${NC} Installing Python package..."
cd "$SCRIPT_DIR/.."

# Check if pipx is available
if command -v pipx &> /dev/null; then
    echo "Using pipx for installation..."
    pipx install -e . --force || {
        echo -e "${RED}Error: pipx installation failed${NC}"
        exit 1
    }
elif [[ "$OSTYPE" == "darwin"* ]] && command -v brew &> /dev/null; then
    echo "Installing pipx via Homebrew..."
    brew install pipx
    pipx ensurepath
    echo -e "${YELLOW}Please restart your terminal or run: source ~/.zshrc${NC}"
    echo "Then run this installation script again."
    exit 0
else
    # Try with --break-system-packages flag for Homebrew Python
    python3 -m pip install --user --break-system-packages -e . || {
        echo -e "${RED}Error: Failed to install package${NC}"
        echo ""
        echo "Please install pipx first:"
        echo "  macOS:  brew install pipx"
        echo "  Linux:  python3 -m pip install --user pipx"
        echo ""
        echo "Then run this installation script again."
        exit 1
    }
fi

echo -e "${GREEN}✓${NC} Package installed successfully"

echo ""
echo -e "${BLUE}[4/5]${NC} Verifying installation..."

# Check if umd command is available
if command -v umd &> /dev/null; then
    echo -e "${GREEN}✓${NC} 'umd' command is available"
else
    echo -e "${YELLOW}Warning: 'umd' command not found in PATH${NC}"
    echo ""
    echo "You may need to add the Python bin directory to your PATH:"
    
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        PYTHON_BIN="$HOME/Library/Python/$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')/bin"
        echo "  export PATH=\"\$PATH:$PYTHON_BIN\""
        echo ""
        echo "Add this line to your ~/.zshrc or ~/.bash_profile:"
        echo "  echo 'export PATH=\"\$PATH:$PYTHON_BIN\"' >> ~/.zshrc"
        echo "  source ~/.zshrc"
    else
        # Linux
        echo "  export PATH=\"\$PATH:\$HOME/.local/bin\""
        echo ""
        echo "Add this line to your ~/.bashrc or ~/.zshrc:"
        echo "  echo 'export PATH=\"\$PATH:\$HOME/.local/bin\"' >> ~/.bashrc"
        echo "  source ~/.bashrc"
    fi
fi

echo ""
echo -e "${BLUE}[5/5]${NC} Creating downloads directory..."
DOWNLOADS_DIR="$HOME/Downloads/UltimateDownloader"
mkdir -p "$DOWNLOADS_DIR"
echo -e "${GREEN}✓${NC} Downloads directory created: $DOWNLOADS_DIR"

echo ""
echo "======================================================================"
echo -e "${GREEN}  Installation Complete! 🎉${NC}"
echo "======================================================================"
echo ""
echo "Usage:"
echo "  umd <URL>                    # Download media from URL"
echo "  umd                          # Start interactive mode"
echo "  umd <URL> --audio-only       # Download audio only"
echo "  umd <URL> --quality 1080p    # Download specific quality"
echo "  umd --help                   # Show all options"
echo ""
echo "Downloads will be saved to:"
echo "  $DOWNLOADS_DIR"
echo ""
echo "For more information, see README.md or run: umd --help"
echo "======================================================================"
