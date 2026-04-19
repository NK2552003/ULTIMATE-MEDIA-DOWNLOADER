#!/bin/bash
# Auto-Update Script for Ultimate Media Downloader (macOS/Linux)
# This script checks for updates and installs the latest version

echo "╔══════════════════════════════════════════════════════╗"
echo "║   Ultimate Media Downloader - Auto Update Script    ║"
echo "╚══════════════════════════════════════════════════════╝"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Python 3 is not installed. Please install Python 3.9 or higher.${NC}"
    exit 1
fi

# Check if git is available
if ! command -v git &> /dev/null; then
    echo -e "${YELLOW} Git is not installed. Installing from PyPI instead...${NC}"
    USE_GIT=false
else
    USE_GIT=true
fi

echo -e "${BLUE}Checking current version...${NC}"

# Get current version
CURRENT_VERSION=$(python3 -c "try:
    import ultimate_downloader
    print(ultimate_downloader.__version__)
except:
    print('0.0.0')" 2>/dev/null)

if [ -z "$CURRENT_VERSION" ]; then
    CURRENT_VERSION="Not installed"
fi

echo -e "${BLUE}   Current version: ${GREEN}$CURRENT_VERSION${NC}"
echo ""

echo -e "${BLUE} Updating Ultimate Media Downloader...${NC}"
echo ""

# Update using pipx (matching installation method)
if command -v pipx &> /dev/null; then
    echo -e "${GREEN}Using pipx for update...${NC}"
    
    # Remove old installation if exists
    echo -e "${YELLOW}Checking for existing installation...${NC}"
    if pipx list 2>/dev/null | grep -q "ultimate-downloader"; then
        echo -e "${YELLOW}Removing previous installation...${NC}"
        pipx uninstall ultimate-downloader
        
        # Verify uninstall
        if [ -d "$HOME/.local/pipx/venvs/ultimate-downloader" ]; then
            echo -e "${YELLOW}Cleaning up leftover files...${NC}"
            rm -rf "$HOME/.local/pipx/venvs/ultimate-downloader"
        fi
        
        # Remove command symlink if it still exists
        if [ -f "$HOME/.local/bin/umd" ]; then
            rm -f "$HOME/.local/bin/umd"
        fi
        
        echo -e "${GREEN}✓ Old version completely removed${NC}"
    else
        echo -e "${BLUE}No previous installation found${NC}"
    fi
    
    # Install fresh version
    echo -e "${GREEN}Installing new version...${NC}"
    if [ "$USE_GIT" = true ]; then
        pipx install git+https://codeberg.org/nk2552003/umd.git
    else
        # Update from local directory
        SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && cd .. && pwd)"
        if [ -f "$SCRIPT_DIR/setup.py" ]; then
            pipx install "$SCRIPT_DIR"
        else
            echo -e "${RED}Unable to update: setup.py not in expected location${NC}"
            exit 1
        fi
    fi
else
    echo -e "${YELLOW}Warning: pipx not found. Attempting pip installation...${NC}"
    
    # Uninstall old version first with pip
    echo -e "${YELLOW}Removing previous installation...${NC}"
    python3 -m pip uninstall -y ultimate-downloader 2>/dev/null || true
    
    # Also clean up any leftover files in user site-packages
    USER_SITE=$(python3 -c "import site; print(site.USER_SITE)" 2>/dev/null)
    if [ -n "$USER_SITE" ] && [ -d "$USER_SITE" ]; then
        if [ -f "$USER_SITE/ultimate_downloader.py" ]; then
            echo -e "${YELLOW}Cleaning up leftover files in $USER_SITE...${NC}"
            rm -f "$USER_SITE/ultimate_downloader.py"
            rm -f "$USER_SITE/cli_args.py"
            rm -f "$USER_SITE/logger.py"
            rm -f "$USER_SITE/youtube_scorer.py"
            rm -f "$USER_SITE/generic_downloader.py"
            rm -f "$USER_SITE/platform_info.py"
            rm -f "$USER_SITE/version_checker.py"
            rm -rf "$USER_SITE/handlers"
            rm -rf "$USER_SITE/utils"
            rm -rf "$USER_SITE/ultimate_downloader-"*.dist-info
        fi
    fi
    
    echo -e "${GREEN}✓ Old version removed${NC}"
    echo -e "${GREEN}Installing new version...${NC}"
    
    if [ "$USE_GIT" = true ]; then
        # Try with --user flag first for externally-managed environments
        python3 -m pip install --user git+https://codeberg.org/nk2552003/umd.git 2>/dev/null
        if [ $? -ne 0 ]; then
            # Try with --break-system-packages
            python3 -m pip install --user --break-system-packages git+https://codeberg.org/nk2552003/umd.git
        fi
    else
        # Fallback: Try to upgrade from local directory
        SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && cd .. && pwd)"
        if [ -f "$SCRIPT_DIR/setup.py" ]; then
            python3 -m pip install --user --break-system-packages "$SCRIPT_DIR"
        else
            echo -e "${RED}Unable to update: Git not found and setup.py not in expected location${NC}"
            exit 1
        fi
    fi
fi

# Check if update was successful
if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}Update completed successfully!${NC}"
    
    # Get new version
    NEW_VERSION=$(python3 -c "try:
    import ultimate_downloader
    print(ultimate_downloader.__version__)
except:
    print('Unknown')" 2>/dev/null)
    
    if [ ! -z "$NEW_VERSION" ]; then
        echo -e "${GREEN}   New version: $NEW_VERSION${NC}"
    fi
    
    echo ""
    echo -e "${BLUE}ℹ You can now run 'umd' to use Ultimate Media Downloader${NC}"
    echo ""
else
    echo ""
    echo -e "${RED} Update failed. Please check the error messages above.${NC}"
    echo ""
    echo -e "${YELLOW} Try running manually:${NC}"
    echo -e "   python3 -m pip install --upgrade git+https://codeberg.org/nk2552003/umd.git"
    echo ""
    exit 1
fi
