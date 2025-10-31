#!/bin/bash
# =============================================================================
# Ultimate Media Downloader - Uninstall Script
# Version: 2.0.0
# Date: October 2025
# Removes the Ultimate Media Downloader installation
# =============================================================================

set -e  # Exit on error

echo "======================================================================"
echo "  Ultimate Media Downloader - Uninstaller"
echo "======================================================================"
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Helper functions
print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_info() {
    echo -e "${CYAN}ℹ${NC} $1"
}

echo -e "${YELLOW}This will remove the Ultimate Media Downloader installation.${NC}"
echo -e "${YELLOW}${BOLD}Your downloaded files will NOT be deleted.${NC}"
echo ""
read -p "Continue? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    print_info "Uninstall cancelled."
    exit 0
fi

echo ""
echo -e "${BLUE}[1/3]${NC} Uninstalling Python package..."

# Try multiple methods to uninstall
if python3 -m pip uninstall -y ultimate-downloader 2>/dev/null || pip3 uninstall -y ultimate-downloader 2>/dev/null; then
    print_success "Package uninstalled via pip"
elif pipx uninstall ultimate-downloader 2>/dev/null; then
    print_success "Package uninstalled via pipx"
else
    print_warning "Package not found or already uninstalled"
fi

echo ""
echo -e "${BLUE}[2/3]${NC} Removing virtual environment (if local setup)..."

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR/.."

if [ -d "venv" ]; then
    rm -rf venv
    print_success "Virtual environment removed"
else
    print_info "No local virtual environment found (using system installation)"
fi

echo ""
echo -e "${BLUE}[3/3]${NC} Removing activation script..."

if [ -f "scripts/activate-env.sh" ]; then
    rm -f scripts/activate-env.sh
    print_success "Activation script removed"
fi

echo ""
echo "======================================================================"
echo -e "${GREEN}  Uninstallation Complete ✓${NC}"
echo "======================================================================"
echo ""
print_info "Modules removed:"
echo "  • ultimate_downloader    - Main downloader engine"
echo "  • cli_args              - Command-line argument parser"
echo "  • ui_components         - UI component library"
echo "  • ui_display            - Display and formatting utilities"
echo "  • logger                - Logging system"
echo "  • utils                 - Utility functions"
echo "  • spotify_handler       - Spotify integration"
echo "  • apple_music_handler   - Apple Music support"
echo "  • youtube_scorer        - YouTube search scoring"
echo "  • generic_downloader    - Generic download handler"
echo ""
print_info "Your downloaded files are still in: ~/Downloads/UltimateDownloader"
print_info "To remove downloads too, run: rm -rf ~/Downloads/UltimateDownloader"
echo ""
