#!/bin/bash

# Ultimate Media Downloader - Complete Setup Script
# This script sets up the entire environment from scratch

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
NC='\033[0m' # No Color

# Function to print colored messages
print_header() {
    echo ""
    echo -e "${CYAN}════════════════════════════════════════════════════════════════${NC}"
    echo -e "${CYAN}$1${NC}"
    echo -e "${CYAN}════════════════════════════════════════════════════════════════${NC}"
    echo ""
}

print_message() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
}

print_info() {
    echo -e "${BLUE}[ℹ]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[⚠]${NC} $1"
}

print_step() {
    echo -e "${MAGENTA}[→]${NC} $1"
}

# Print welcome banner
print_header "▶ Ultimate Media Downloader v2.0 - Setup"

# Step 1: Check Python installation
print_step "Step 1/6: Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is not installed!"
    print_info "Please install Python 3.8 or higher from https://www.python.org/"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
print_message "Python $PYTHON_VERSION found"

# Check Python version (require 3.8+)
PYTHON_MAJOR=$(python3 -c 'import sys; print(sys.version_info[0])')
PYTHON_MINOR=$(python3 -c 'import sys; print(sys.version_info[1])')

if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 8 ]); then
    print_error "Python 3.8 or higher is required (found $PYTHON_VERSION)"
    exit 1
fi

# Step 2: Check pip installation
print_step "Step 2/6: Checking pip installation..."
if ! command -v pip3 &> /dev/null; then
    print_error "pip3 is not installed!"
    print_info "Installing pip..."
    python3 -m ensurepip --upgrade
fi

PIP_VERSION=$(pip3 --version | cut -d' ' -f2)
print_message "pip $PIP_VERSION found"

# Step 3: Create virtual environment
print_step "Step 3/6: Creating virtual environment..."

# Remove old virtual environment if exists
if [ -d "venv" ]; then
    print_warning "Existing virtual environment found. Removing..."
    rm -rf venv
fi

python3 -m venv venv
print_message "Virtual environment created successfully"

# Activate virtual environment
print_info "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip in virtual environment
print_info "Upgrading pip..."
pip install --upgrade pip setuptools wheel

# Step 4: Install Python dependencies
print_step "Step 4/6: Installing Python dependencies..."
print_info "This may take a few minutes..."

if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
    print_message "All Python dependencies installed successfully"
else
    print_error "requirements.txt not found!"
    exit 1
fi

# Step 5: Check FFmpeg installation
print_step "Step 5/6: Checking FFmpeg installation..."
if ! command -v ffmpeg &> /dev/null; then
    print_warning "FFmpeg is not installed!"
    echo ""
    print_info "FFmpeg is required for audio/video conversion."
    print_info "Please install FFmpeg:"
    echo ""
    echo "  macOS:     brew install ffmpeg"
    echo "  Ubuntu:    sudo apt-get install ffmpeg"
    echo "  Fedora:    sudo dnf install ffmpeg"
    echo "  Arch:      sudo pacman -S ffmpeg"
    echo "  Windows:   Download from https://ffmpeg.org/download.html"
    echo ""
    print_warning "The downloader will still work, but some features may be limited."
else
    FFMPEG_VERSION=$(ffmpeg -version | head -n1 | cut -d' ' -f3)
    print_message "FFmpeg $FFMPEG_VERSION found"
fi

# Step 6: Make scripts executable
print_step "Step 6/6: Setting up executable permissions..."
chmod +x activate_env.sh
chmod +x install.sh
chmod +x setup.sh 2>/dev/null || true
chmod +x ultimate_downloader.py
print_message "Scripts are now executable"

# Deactivate virtual environment
deactivate

# Print success message
echo ""
print_header "✓ Setup Complete!"

echo -e "${GREEN}Installation successful!${NC}"
echo ""
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}QUICK START GUIDE${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "${BLUE}1. Activate the environment:${NC}"
echo "   source activate_env.sh"
echo ""
echo -e "${BLUE}2. Run in interactive mode:${NC}"
echo "   python ultimate_downloader.py"
echo ""
echo -e "${BLUE}3. Download a video:${NC}"
echo "   python ultimate_downloader.py \"https://www.youtube.com/watch?v=VIDEO_ID\""
echo ""
echo -e "${BLUE}4. Download audio only:${NC}"
echo "   python ultimate_downloader.py \"URL\" --audio-only --format mp3"
echo ""
echo -e "${BLUE}5. See all options:${NC}"
echo "   python ultimate_downloader.py --help"
echo ""
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
print_info "For detailed documentation, see README.md"
print_info "For troubleshooting, see DOCUMENTATION.md"
echo ""
