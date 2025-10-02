#!/bin/bash
# =============================================================================
# Ultimate Media Downloader - Environment Activation Script
# Version: 2.0.0
# Date: October 2, 2025
# Description: Activates the Python virtual environment for the downloader
# =============================================================================

# Colors
CYAN='\033[0;36m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

# Symbols
SUCCESS="✓"
ERROR="✗"
INFO="ℹ"
ARROW="→"

# Script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Banner
print_banner() {
    clear
    echo -e "${CYAN}╔════════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║                                                                    ║${NC}"
    echo -e "${CYAN}║        ${GREEN}ULTIMATE MEDIA DOWNLOADER${CYAN} - Environment                    ║${NC}"
    echo -e "${CYAN}║                    Version 2.0.0 - October 2025                   ║${NC}"
    echo -e "${CYAN}║                                                                    ║${NC}"
    echo -e "${CYAN}╚════════════════════════════════════════════════════════════════════╝${NC}"
    echo ""
}

# Check if virtual environment exists
check_venv() {
    if [ ! -d "$SCRIPT_DIR/venv" ]; then
        echo -e "${RED}${ERROR} Virtual environment not found!${NC}"
        echo ""
        echo -e "${YELLOW}${INFO} Please run setup first:${NC}"
        echo -e "   ${BLUE}./setup.sh${NC}"
        echo ""
        return 1
    fi
    return 0
}

# Activate environment
activate() {
    print_banner
    
    if ! check_venv; then
        return 1
    fi
    
    echo -e "${BLUE}${ARROW} Activating virtual environment...${NC}"
    echo ""
    
    # Activate virtual environment
    source "$SCRIPT_DIR/venv/bin/activate"
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}${SUCCESS} Environment activated successfully!${NC}"
        echo ""
        
        # Show environment info
        echo -e "${CYAN}╭──────────────────────────────────────────────────────────────────╮${NC}"
        echo -e "${CYAN}│${NC} ${YELLOW}Environment Information${NC}                                         ${CYAN}│${NC}"
        echo -e "${CYAN}├──────────────────────────────────────────────────────────────────┤${NC}"
        echo -e "${CYAN}│${NC} Python:     $(python --version | cut -d' ' -f2)                                      ${CYAN}│${NC}"
        echo -e "${CYAN}│${NC} Location:   $SCRIPT_DIR/venv${NC}"
        echo -e "${CYAN}╰──────────────────────────────────────────────────────────────────╯${NC}"
        echo ""
        
        # Show available commands
        echo -e "${CYAN}╭──────────────────────────────────────────────────────────────────╮${NC}"
        echo -e "${CYAN}│${NC} ${YELLOW}Available Commands${NC}                                              ${CYAN}│${NC}"
        echo -e "${CYAN}├──────────────────────────────────────────────────────────────────┤${NC}"
        echo -e "${CYAN}│${NC}                                                                  ${CYAN}│${NC}"
        echo -e "${CYAN}│${NC}  ${GREEN}Download from URL:${NC}                                             ${CYAN}│${NC}"
        echo -e "${CYAN}│${NC}    ${BLUE}python ultimate_downloader.py <URL>${NC}                          ${CYAN}│${NC}"
        echo -e "${CYAN}│${NC}                                                                  ${CYAN}│${NC}"
        echo -e "${CYAN}│${NC}  ${GREEN}Show help:${NC}                                                     ${CYAN}│${NC}"
        echo -e "${CYAN}│${NC}    ${BLUE}python ultimate_downloader.py --help${NC}                         ${CYAN}│${NC}"
        echo -e "${CYAN}│${NC}                                                                  ${CYAN}│${NC}"
        echo -e "${CYAN}│${NC}  ${GREEN}Interactive mode:${NC}                                              ${CYAN}│${NC}"
        echo -e "${CYAN}│${NC}    ${BLUE}python ultimate_downloader.py -i${NC}                             ${CYAN}│${NC}"
        echo -e "${CYAN}│${NC}                                                                  ${CYAN}│${NC}"
        echo -e "${CYAN}│${NC}  ${GREEN}Download playlist:${NC}                                             ${CYAN}│${NC}"
        echo -e "${CYAN}│${NC}    ${BLUE}python ultimate_downloader.py -p <PLAYLIST_URL>${NC}              ${CYAN}│${NC}"
        echo -e "${CYAN}│${NC}                                                                  ${CYAN}│${NC}"
        echo -e "${CYAN}│${NC}  ${GREEN}Audio only:${NC}                                                    ${CYAN}│${NC}"
        echo -e "${CYAN}│${NC}    ${BLUE}python ultimate_downloader.py -a <URL>${NC}                       ${CYAN}│${NC}"
        echo -e "${CYAN}│${NC}                                                                  ${CYAN}│${NC}"
        echo -e "${CYAN}│${NC}  ${GREEN}Deactivate environment:${NC}                                        ${CYAN}│${NC}"
        echo -e "${CYAN}│${NC}    ${BLUE}deactivate${NC}                                                 ${CYAN}│${NC}"
        echo -e "${CYAN}│${NC}                                                                  ${CYAN}│${NC}"
        echo -e "${CYAN}╰──────────────────────────────────────────────────────────────────╯${NC}"
        echo ""
        
        # Show tips
        echo -e "${YELLOW}${INFO} Tips:${NC}"
        echo -e "   • Use ${BLUE}--quality${NC} to specify video quality (e.g., 1080, 720, 480)"
        echo -e "   • Use ${BLUE}--format${NC} to choose output format (mp4, mkv, webm)"
        echo -e "   • Check ${BLUE}config.json${NC} for advanced settings"
        echo ""
        
        # Export PS1 for custom prompt
        export PS1="${GREEN}(downloader)${NC} ${BLUE}\w${NC} ${CYAN}❯${NC} "
        
    else
        echo -e "${RED}${ERROR} Failed to activate environment${NC}"
        echo ""
        return 1
    fi
}

# Run activation
activate

# Note: This script should be sourced, not executed directly
# Usage: source activate-env.sh
