#!/bin/bash
# =============================================================================
# Ultimate Media Downloader - Environment Activation Script
# Version: 2.0.0
# Date: October 2025
# Description: Activates the virtual environment with all modules and deps
# =============================================================================

# Colors
CYAN='\033[0;36m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR/.."

echo -e "${CYAN}╔════════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║    Activating Ultimate Media Downloader Environment                ║${NC}"
echo -e "${CYAN}╚════════════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Activate virtual environment
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
    echo -e "${GREEN}✓ Virtual environment activated${NC}"
    echo ""
    
    # Display installed modules
    echo -e "${BLUE}Loaded Core Modules:${NC}"
    echo "  ✓ ultimate_downloader    - Main downloader engine"
    echo "  ✓ cli_args              - Command-line argument parser"
    echo "  ✓ ui_components         - UI component library"
    echo "  ✓ ui_display            - Display and formatting utilities"
    echo "  ✓ logger                - Logging and output system"
    echo "  ✓ utils                 - Utility functions"
    echo "  ✓ spotify_handler       - Spotify integration"
    echo "  ✓ apple_music_handler   - Apple Music support"
    echo "  ✓ youtube_scorer        - YouTube search scoring"
    echo "  ✓ generic_downloader    - Generic download handler"
    echo ""
    
    echo -e "${BLUE}You can now run:${NC}"
    echo "  ${GREEN}•${NC} ${BLUE}python ultimate_downloader.py --help${NC}       Show help and options"
    echo "  ${GREEN}•${NC} ${BLUE}python ultimate_downloader.py <URL>${NC}         Download from URL"
    echo "  ${GREEN}•${NC} ${BLUE}python ultimate_downloader.py -i${NC}            Interactive mode"
    echo "  ${GREEN}•${NC} ${BLUE}python -m pytest${NC}                         Run tests"
    echo ""
    echo -e "${BLUE}Supported Platforms:${NC}"
    echo "  • YouTube, YouTube Music"
    echo "  • Spotify (via YouTube search)"
    echo "  • Apple Music (with setup)"
    echo "  • Instagram, TikTok, Twitter"
    echo "  • SoundCloud, Bandcamp"
    echo "  • 1000+ other platforms (via yt-dlp)"
    echo ""
    echo -e "${YELLOW}To deactivate environment, type:${NC} ${BLUE}deactivate${NC}"
    echo ""
else
    echo -e "${CYAN}✗ Virtual environment not found!${NC}"
    echo "Please run ./scripts/setup.sh first"
    return 1
fi
