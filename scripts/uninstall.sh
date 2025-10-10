#!/bin/bash
# =============================================================================
# Ultimate Media Downloader - Uninstall Script
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
NC='\033[0m' # No Color

echo -e "${YELLOW}This will remove the Ultimate Media Downloader installation.${NC}"
echo -e "${YELLOW}Your downloaded files will NOT be deleted.${NC}"
echo ""
read -p "Continue? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Uninstall cancelled."
    exit 0
fi

echo ""
echo -e "${BLUE}[1/2]${NC} Uninstalling Python package..."

python3 -m pip uninstall -y ultimate-downloader || pip3 uninstall -y ultimate-downloader || {
    echo -e "${YELLOW}Warning: Package not found or already uninstalled${NC}"
}

echo -e "${GREEN}✓${NC} Package uninstalled"

echo ""
echo -e "${BLUE}[2/2]${NC} Cleanup complete"

echo ""
echo "======================================================================"
echo -e "${GREEN}  Uninstallation Complete${NC}"
echo "======================================================================"
echo ""
echo "Your downloaded files are still in: ~/Downloads/UltimateDownloader"
echo ""
