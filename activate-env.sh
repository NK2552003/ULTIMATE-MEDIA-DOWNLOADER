#!/bin/bash
# =============================================================================
# Ultimate Media Downloader - Environment Activation Script
# Version: 2.0.0
# Date: October 2, 2025
# =============================================================================

# Colors
CYAN='\033[0;36m'
GREEN='\033[0;32m'
NC='\033[0m'

# Script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

echo -e "${CYAN}╔════════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║    Activating Ultimate Media Downloader Environment                ║${NC}"
echo -e "${CYAN}╚════════════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Activate virtual environment
if [ -f "$SCRIPT_DIR/venv/bin/activate" ]; then
    source "$SCRIPT_DIR/venv/bin/activate"
    echo -e "${GREEN}✓ Virtual environment activated${NC}"
    echo ""
    echo "You can now run:"
    echo "  • python ultimate_downloader.py --help"
    echo "  • python ultimate_downloader.py <URL>"
    echo ""
    echo "To deactivate, type: deactivate"
    echo ""
else
    echo -e "\033[0;31m✗ Virtual environment not found!${NC}"
    echo "Please run ./setup.sh first"
    return 1
fi
