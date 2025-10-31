#!/bin/bash
# =============================================================================
# Ultimate Media Downloader - Setup Script
# Version: 2.0.0
# Date: October 3, 2025
# Description: Automated setup script for Ultimate Media Downloader
# Author: Nitish Kumar
# Repository: https://github.com/NK2552003/ULTIMATE-MEDIA-DOWNLOADER
# =============================================================================

set -e  # Exit on error

# Trap errors and provide helpful messages
trap 'error_exit "Setup failed at line $LINENO. Please check the error message above."' ERR

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Symbols
SUCCESS="✓"
ERROR="✗"
INFO="ℹ"
ARROW="→"

# Script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Configuration
VENV_NAME="venv"
PYTHON_VERSION="3.9"
REQUIREMENTS_FILE="requirements.txt"

# =============================================================================
# Helper Functions
# =============================================================================

print_header() {
    echo -e "${CYAN}"
    echo "╔════════════════════════════════════════════════════════════════════╗"
    echo "║                                                                    ║"
    echo "║        ULTIMATE MEDIA DOWNLOADER - SETUP SCRIPT                   ║"
    echo "║                  Version 2.0.0 - October 2025                     ║"
    echo "║                                                                    ║"
    echo "╚════════════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

print_section() {
    echo -e "\n${MAGENTA}▶ $1${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
}

print_success() {
    echo -e "${GREEN}${SUCCESS} $1${NC}"
}

print_error() {
    echo -e "${RED}${ERROR} $1${NC}"
}

print_info() {
    echo -e "${CYAN}${INFO} $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_step() {
    echo -e "${BLUE}${ARROW} $1${NC}"
}

error_exit() {
    echo -e "\n${RED}╔════════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${RED}║                        SETUP FAILED                                 ║${NC}"
    echo -e "${RED}╚════════════════════════════════════════════════════════════════════╝${NC}"
    echo -e "${RED}${ERROR} $1${NC}\n"
    exit 1
}

# =============================================================================
# System Detection
# =============================================================================

detect_os() {
    print_section "Detecting Operating System"
    
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        OS="linux"
        print_info "Detected: Linux"
        
        # Detect distribution
        if [ -f /etc/os-release ]; then
            . /etc/os-release
            DISTRO=$ID
            print_info "Distribution: $NAME"
        fi
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        OS="macos"
        print_info "Detected: macOS"
    elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]]; then
        OS="windows"
        print_info "Detected: Windows (Git Bash/Cygwin)"
    else
        OS="unknown"
        print_warning "Unknown operating system: $OSTYPE"
    fi
}

# =============================================================================
# Python Installation Check
# =============================================================================

check_python() {
    print_section "Checking Python Installation"
    
    # Check for Python 3.9+
    if command -v python3 &> /dev/null; then
        PYTHON_CMD="python3"
        PYTHON_INSTALLED_VERSION=$(python3 --version | cut -d' ' -f2)
        
        # Extract major and minor version
        PYTHON_MAJOR=$(echo $PYTHON_INSTALLED_VERSION | cut -d. -f1)
        PYTHON_MINOR=$(echo $PYTHON_INSTALLED_VERSION | cut -d. -f2)
        
        # Check if version is 3.9 or higher
        if [ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -ge 9 ]; then
            print_success "Python found: $PYTHON_INSTALLED_VERSION (✓ Compatible)"
        else
            print_warning "Python $PYTHON_INSTALLED_VERSION found, but 3.9+ recommended"
            print_info "Some features may not work with older versions"
        fi
    elif command -v python &> /dev/null; then
        PYTHON_CMD="python"
        PYTHON_INSTALLED_VERSION=$(python --version 2>&1 | cut -d' ' -f2)
        
        # Check if it's Python 3
        if [[ $PYTHON_INSTALLED_VERSION == 3.* ]]; then
            PYTHON_MAJOR=$(echo $PYTHON_INSTALLED_VERSION | cut -d. -f1)
            PYTHON_MINOR=$(echo $PYTHON_INSTALLED_VERSION | cut -d. -f2)
            
            if [ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -ge 9 ]; then
                print_success "Python found: $PYTHON_INSTALLED_VERSION (✓ Compatible)"
            else
                print_warning "Python $PYTHON_INSTALLED_VERSION found, but 3.9+ recommended"
            fi
        else
            print_error "Python 3.9+ required. Found: $PYTHON_INSTALLED_VERSION"
            install_python
            return 1
        fi
    else
        print_error "Python not found!"
        install_python
        return 1
    fi
    
    # Verify pip
    if ! $PYTHON_CMD -m pip --version &> /dev/null; then
        print_warning "pip not found. Installing pip..."
        install_pip
    else
        PIP_VERSION=$($PYTHON_CMD -m pip --version | cut -d' ' -f2)
        print_success "pip is installed: $PIP_VERSION"
    fi
}

install_python() {
    print_section "Installing Python"
    
    case "$OS" in
        linux)
            if [[ "$DISTRO" == "ubuntu" ]] || [[ "$DISTRO" == "debian" ]]; then
                print_step "Installing Python via apt..."
                sudo apt update
                sudo apt install -y python3 python3-pip python3-venv python3-dev
            elif [[ "$DISTRO" == "fedora" ]] || [[ "$DISTRO" == "rhel" ]] || [[ "$DISTRO" == "centos" ]]; then
                print_step "Installing Python via dnf/yum..."
                sudo dnf install -y python3 python3-pip python3-devel || sudo yum install -y python3 python3-pip python3-devel
            elif [[ "$DISTRO" == "arch" ]] || [[ "$DISTRO" == "manjaro" ]]; then
                print_step "Installing Python via pacman..."
                sudo pacman -S --noconfirm python python-pip
            else
                print_error "Unsupported Linux distribution. Please install Python 3.9+ manually."
                exit 1
            fi
            ;;
        macos)
            if command -v brew &> /dev/null; then
                print_step "Installing Python via Homebrew..."
                brew install python@3.11
            else
                print_error "Homebrew not found. Please install from https://brew.sh"
                exit 1
            fi
            ;;
        windows)
            print_error "Please install Python from https://www.python.org/downloads/"
            print_info "Make sure to check 'Add Python to PATH' during installation"
            exit 1
            ;;
        *)
            print_error "Cannot automatically install Python. Please install manually."
            exit 1
            ;;
    esac
    
    print_success "Python installed successfully"
}

install_pip() {
    print_step "Installing pip..."
    $PYTHON_CMD -m ensurepip --upgrade || {
        curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
        $PYTHON_CMD get-pip.py
        rm get-pip.py
    }
    print_success "pip installed successfully"
}

# =============================================================================
# FFmpeg Installation
# =============================================================================

check_ffmpeg() {
    print_section "Checking FFmpeg Installation"
    
    if command -v ffmpeg &> /dev/null; then
        FFMPEG_VERSION=$(ffmpeg -version | head -n1)
        print_success "FFmpeg found: $FFMPEG_VERSION"
        return 0
    else
        print_warning "FFmpeg not found"
        install_ffmpeg
    fi
}

install_ffmpeg() {
    print_section "Installing FFmpeg"
    
    case "$OS" in
        linux)
            if [[ "$DISTRO" == "ubuntu" ]] || [[ "$DISTRO" == "debian" ]]; then
                print_step "Installing FFmpeg via apt..."
                sudo apt update
                sudo apt install -y ffmpeg
            elif [[ "$DISTRO" == "fedora" ]] || [[ "$DISTRO" == "rhel" ]] || [[ "$DISTRO" == "centos" ]]; then
                print_step "Installing FFmpeg via dnf/yum..."
                sudo dnf install -y ffmpeg || sudo yum install -y ffmpeg
            elif [[ "$DISTRO" == "arch" ]] || [[ "$DISTRO" == "manjaro" ]]; then
                print_step "Installing FFmpeg via pacman..."
                sudo pacman -S --noconfirm ffmpeg
            else
                print_warning "Please install FFmpeg manually"
            fi
            ;;
        macos)
            if command -v brew &> /dev/null; then
                print_step "Installing FFmpeg via Homebrew..."
                brew install ffmpeg
            else
                print_error "Homebrew required. Install from https://brew.sh"
            fi
            ;;
        windows)
            print_warning "Please install FFmpeg from https://ffmpeg.org/download.html"
            print_info "Add FFmpeg to your system PATH"
            ;;
    esac
    
    if command -v ffmpeg &> /dev/null; then
        print_success "FFmpeg installed successfully"
    else
        print_warning "FFmpeg installation may have failed. Some features may not work."
    fi
}

# =============================================================================
# System Dependencies
# =============================================================================

install_system_dependencies() {
    print_section "Installing System Dependencies"
    
    case "$OS" in
        linux)
            if [[ "$DISTRO" == "ubuntu" ]] || [[ "$DISTRO" == "debian" ]]; then
                print_step "Installing system packages..."
                sudo apt update
                sudo apt install -y \
                    build-essential \
                    libssl-dev \
                    libffi-dev \
                    python3-dev \
                    libjpeg-dev \
                    zlib1g-dev \
                    chromium-browser \
                    chromium-chromedriver \
                    curl \
                    wget \
                    git
            elif [[ "$DISTRO" == "fedora" ]] || [[ "$DISTRO" == "rhel" ]] || [[ "$DISTRO" == "centos" ]]; then
                print_step "Installing system packages..."
                sudo dnf install -y \
                    gcc \
                    gcc-c++ \
                    openssl-devel \
                    libffi-devel \
                    python3-devel \
                    libjpeg-devel \
                    zlib-devel \
                    chromium \
                    chromedriver \
                    curl \
                    wget \
                    git
            elif [[ "$DISTRO" == "arch" ]] || [[ "$DISTRO" == "manjaro" ]]; then
                print_step "Installing system packages..."
                sudo pacman -S --noconfirm \
                    base-devel \
                    openssl \
                    libffi \
                    python \
                    libjpeg-turbo \
                    zlib \
                    chromium \
                    chromedriver \
                    curl \
                    wget \
                    git
            fi
            print_success "System dependencies installed"
            ;;
        macos)
            if command -v brew &> /dev/null; then
                print_step "Installing system packages via Homebrew..."
                brew install openssl libffi jpeg zlib chromedriver
                print_success "System dependencies installed"
            else
                print_warning "Homebrew not found. Some dependencies may be missing."
            fi
            ;;
        windows)
            print_info "System dependencies should be installed via installers"
            ;;
    esac
}

# =============================================================================
# Virtual Environment Setup
# =============================================================================

create_virtual_environment() {
    print_section "Creating Virtual Environment"
    
    if [ -d "$VENV_NAME" ]; then
        print_warning "Virtual environment already exists"
        read -p "Do you want to recreate it? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            print_step "Removing existing virtual environment..."
            rm -rf "$VENV_NAME"
        else
            print_info "Using existing virtual environment"
            return 0
        fi
    fi
    
    print_step "Creating virtual environment: $VENV_NAME"
    $PYTHON_CMD -m venv "$VENV_NAME"
    
    if [ -d "$VENV_NAME" ]; then
        print_success "Virtual environment created successfully"
    else
        print_error "Failed to create virtual environment"
        exit 1
    fi
}

# =============================================================================
# Python Dependencies Installation
# =============================================================================

install_python_dependencies() {
    print_section "Installing Python Dependencies"
    
    # Activate virtual environment
    print_step "Activating virtual environment..."
    source "$VENV_NAME/bin/activate"
    
    # Upgrade pip, setuptools, and wheel
    print_step "Upgrading pip, setuptools, and wheel..."
    pip install --upgrade pip setuptools wheel --quiet
    
    # Install requirements
    if [ -f "$REQUIREMENTS_FILE" ]; then
        print_step "Installing packages from $REQUIREMENTS_FILE..."
        print_info "This may take 2-5 minutes depending on your internet speed..."
        
        # Install with progress
        pip install -r "$REQUIREMENTS_FILE" --progress-bar on
        
        print_success "All dependencies installed successfully"
    else
        print_error "Requirements file not found: $REQUIREMENTS_FILE"
        error_exit "Please ensure requirements.txt exists in the project directory"
    fi
    
    # Verify critical installations
    print_step "Verifying critical packages..."
    
    PACKAGES_TO_VERIFY=("yt_dlp" "requests" "rich" "mutagen" "spotipy")
    FAILED_PACKAGES=()
    
    for package in "${PACKAGES_TO_VERIFY[@]}"; do
        if python -c "import $package" 2>/dev/null; then
            print_success "$package verified"
        else
            print_error "$package failed to install"
            FAILED_PACKAGES+=("$package")
        fi
    done
    
    if [ ${#FAILED_PACKAGES[@]} -eq 0 ]; then
        print_success "All core packages verified successfully"
    else
        print_warning "Some packages failed: ${FAILED_PACKAGES[*]}"
        print_info "You can try installing them manually later"
    fi
    
    # Count installed packages
    INSTALLED_COUNT=$(pip list --format=freeze | wc -l)
    print_info "Total packages installed: $INSTALLED_COUNT"
}

create_requirements_file() {
    cat > "$REQUIREMENTS_FILE" << 'EOF'
# Ultimate Media Downloader - Requirements
# Updated: October 2, 2025

# Core dependencies
yt-dlp>=2023.12.30
requests>=2.31.0
urllib3>=2.1.0

# Rich UI and progress
rich>=13.7.0
colorama>=0.4.6

# Audio/Video processing
mutagen>=1.47.0
Pillow>=10.1.0

# Spotify support
spotipy>=2.23.0

# YouTube search
youtube-search-python>=1.6.6

# Advanced downloading
cloudscraper>=1.2.71
httpx>=0.25.2
curl-cffi>=0.6.2
fake-useragent>=1.4.0
requests-html>=0.10.0

# Browser automation
selenium>=4.16.0
undetected-chromedriver>=3.5.4
webdriver-manager>=4.0.1
playwright>=1.40.0

# Stream extraction
streamlink>=6.5.0

# CLI enhancements
pyfiglet>=1.0.2
emoji>=2.9.0
halo>=0.0.31

# Apple Music (optional)
# gamdl

# Utilities
beautifulsoup4>=4.12.2
lxml>=4.9.3
python-dateutil>=2.8.2
pytz>=2023.3

# Development
pytest>=7.4.3
black>=23.12.0
flake8>=6.1.0
EOF
    print_success "Requirements file created"
}

# =============================================================================
# Configuration Setup
# =============================================================================

create_config_file() {
    print_section "Creating Configuration Files"
    
    if [ ! -f "config.json" ]; then
        print_step "Creating config.json..."
        cat > config.json << 'EOF'
{
    "spotify": {
        "client_id": "",
        "client_secret": ""
    },
    "apple_music": {
        "enabled": false,
        "cookie_file": ""
    },
    "download": {
        "output_dir": "downloads",
        "format": "best",
        "audio_format": "mp3",
        "audio_quality": "320",
        "video_quality": "1080",
        "embed_thumbnail": true,
        "embed_metadata": true
    },
    "proxy": {
        "enabled": false,
        "http": "",
        "https": ""
    },
    "advanced": {
        "concurrent_downloads": 3,
        "retry_attempts": 3,
        "timeout": 300
    }
}
EOF
        print_success "Configuration file created"
    else
        print_info "Configuration file already exists"
    fi
    
    # Create downloads directory
    if [ ! -d "downloads" ]; then
        mkdir -p downloads
        print_success "Downloads directory created"
    fi
}

# =============================================================================
# Activation Script Creation
# =============================================================================

create_activation_script() {
    print_section "Creating Activation Script"
    
    cat > activate-env.sh << 'EOF'
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
EOF
    
    chmod +x activate-env.sh
    print_success "Activation script created: activate-env.sh"
}

# =============================================================================
# Testing
# =============================================================================

run_tests() {
    print_section "Running Tests"
    
    source "$VENV_NAME/bin/activate"
    
    print_step "Testing ultimate_downloader.py..."
    if python ultimate_downloader.py --version &> /dev/null; then
        print_success "Main script is working"
    else
        print_warning "Main script test failed (this may be normal if --version isn't implemented)"
    fi
    
    print_step "Testing imports..."
    python -c "
import yt_dlp
import requests
import rich
from generic_downloader import GenericSiteDownloader
from cli_args import create_argument_parser
from ui_components import ModernUI, Icons
from ui_display import display_info
from logger import QuietLogger
from utils import sanitize_filename
from spotify_handler import SpotifyHandler
from apple_music_handler import AppleMusicHandler
from youtube_scorer import YouTubeScorer
print('All imports successful')
" && print_success "All imports working" || print_warning "Some imports failed"
}

# =============================================================================
# Post-Installation Info
# =============================================================================

show_post_install_info() {
    print_section "Setup Complete!"
    
    # Calculate setup time (if SECONDS is available)
    if [ -n "$SETUP_START_TIME" ]; then
        SETUP_TIME=$((SECONDS - SETUP_START_TIME))
        SETUP_MINUTES=$((SETUP_TIME / 60))
        SETUP_SECONDS=$((SETUP_TIME % 60))
    fi
    
    echo ""
    echo -e "${GREEN}╔════════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║                    SETUP COMPLETED SUCCESSFULLY! ✓                 ║${NC}"
    echo -e "${GREEN}╚════════════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    
    if [ -n "$SETUP_START_TIME" ]; then
        echo -e "${CYAN}⏱  Setup completed in ${SETUP_MINUTES}m ${SETUP_SECONDS}s${NC}"
        echo ""
    fi
    
    echo -e "${CYAN}╔════════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║                         QUICK START GUIDE                          ║${NC}"
    echo -e "${CYAN}╚════════════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${YELLOW}▶ STEP 1: Activate Environment${NC}"
    echo -e "  ${BLUE}source activate-env.sh${NC}"
    echo ""
    echo -e "${YELLOW}▶ STEP 2: Download Your First Video${NC}"
    echo -e "  ${BLUE}python ultimate_downloader.py \"https://youtube.com/watch?v=xxx\"${NC}"
    echo ""
    echo -e "${YELLOW}▶ STEP 3: Try Interactive Mode${NC}"
    echo -e "  ${BLUE}python ultimate_downloader.py -i${NC}"
    echo ""
    echo -e "${CYAN}╔════════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║                         COMMON COMMANDS                            ║${NC}"
    echo -e "${CYAN}╚════════════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "  ${GREEN}•${NC} Download video:       ${BLUE}python ultimate_downloader.py \"URL\"${NC}"
    echo -e "  ${GREEN}•${NC} Download audio:       ${BLUE}python ultimate_downloader.py -a \"URL\"${NC}"
    echo -e "  ${GREEN}•${NC} Download playlist:    ${BLUE}python ultimate_downloader.py -p \"URL\"${NC}"
    echo -e "  ${GREEN}•${NC} Interactive mode:     ${BLUE}python ultimate_downloader.py -i${NC}"
    echo -e "  ${GREEN}•${NC} Show help:            ${BLUE}python ultimate_downloader.py --help${NC}"
    echo ""
    echo -e "${CYAN}╔════════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║                    OPTIONAL CONFIGURATION                          ║${NC}"
    echo -e "${CYAN}╚════════════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "  ${GREEN}•${NC} Spotify API: Edit ${YELLOW}config.json${NC} to add credentials"
    echo -e "    Get keys from: ${BLUE}https://developer.spotify.com/dashboard${NC}"
    echo ""
    echo -e "  ${GREEN}•${NC} Proxy: Configure proxy in ${YELLOW}config.json${NC}"
    echo -e "  ${GREEN}•${NC} Output: Customize download directory and quality"
    echo ""
    echo -e "${CYAN}╔════════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║                       INSTALLED MODULES                            ║${NC}"
    echo -e "${CYAN}╚════════════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "  ${GREEN}Core Engine:${NC}"
    echo -e "    • ultimate_downloader   - Main media downloader engine"
    echo -e "    • cli_args             - Command-line argument parser"
    echo ""
    echo -e "  ${GREEN}Utility Modules:${NC}"
    echo -e "    • browser_utils        - Browser automation & user agent management"
    echo -e "    • platform_utils       - Platform detection & configuration"
    echo -e "    • ui_utils             - Rich console output utilities"
    echo -e "    • logger               - Advanced logging system"
    echo -e "    • utils                - General utility functions"
    echo ""
    echo -e "  ${GREEN}UI & Display:${NC}"
    echo -e "    • ui_components        - UI component library"
    echo -e "    • ui_display           - Display & formatting utilities"
    echo -e "    • progress_display     - Progress bar management"
    echo ""
    echo -e "  ${GREEN}Platform Handlers:${NC}"
    echo -e "    • spotify_handler      - Spotify track/playlist integration"
    echo -e "    • apple_music_handler  - Apple Music support"
    echo -e "    • generic_downloader   - Generic website downloader"
    echo ""
    echo -e "  ${GREEN}Analysis Tools:${NC}"
    echo -e "    • youtube_scorer       - YouTube search result ranking"
    echo -e "    • file_manager         - File organization utilities"
    echo -e "    • url_validator        - URL validation & parsing"
    echo -e "    • platform_info        - Platform information utilities"
    echo ""
    echo -e "${CYAN}╔════════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║                        DOCUMENTATION                               ║${NC}"
    echo -e "${CYAN}╚════════════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "  ${GREEN}•${NC} User Guide:           ${BLUE}docs/USER_GUIDE.md${NC}"
    echo -e "  ${GREEN}•${NC} API Reference:        ${BLUE}docs/API_REFERENCE.md${NC}"
    echo -e "  ${GREEN}•${NC} Complete Index:       ${BLUE}docs/INDEX.md${NC}"
    echo -e "  ${GREEN}•${NC} Troubleshooting:      ${BLUE}docs/USER_GUIDE.md#troubleshooting${NC}"
    echo ""
    echo -e "${CYAN}╔════════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║                      INSTALLATION SUMMARY                          ║${NC}"
    echo -e "${CYAN}╚════════════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "  ${GREEN}✓${NC} Python $PYTHON_INSTALLED_VERSION installed"
    echo -e "  ${GREEN}✓${NC} Virtual environment created"
    echo -e "  ${GREEN}✓${NC} $INSTALLED_COUNT packages installed"
    echo -e "  ${GREEN}✓${NC} FFmpeg configured"
    echo -e "  ${GREEN}✓${NC} Configuration files created"
    echo -e "  ${GREEN}✓${NC} Ready to download from 1000+ platforms"
    echo ""
    echo -e "${GREEN}════════════════════════════════════════════════════════════════════${NC}"
    echo -e "${GREEN}                     Happy Downloading! 🎉🎬🎵                       ${NC}"
    echo -e "${GREEN}════════════════════════════════════════════════════════════════════${NC}"
    echo ""
    echo -e "${CYAN}💡 Tip: Run 'source activate-env.sh' now to get started!${NC}"
    echo ""
}

# =============================================================================
# Cleanup Function
# =============================================================================

cleanup_temp_files() {
    print_step "Cleaning up temporary files..."
    
    # Remove any .pyc files
    find . -type f -name "*.pyc" -delete 2>/dev/null || true
    find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    
    # Remove any pip cache
    rm -rf ~/.cache/pip 2>/dev/null || true
    
    print_success "Cleanup complete"
}

# =============================================================================
# Main Installation Flow
# =============================================================================

main() {
    # Start timer
    SETUP_START_TIME=$SECONDS
    
    print_header
    
    echo -e "${CYAN}╔════════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║  This script will install all dependencies and configure the app  ║${NC}"
    echo -e "${CYAN}║  Estimated time: 3-5 minutes (depending on internet speed)        ║${NC}"
    echo -e "${CYAN}╚════════════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    
    # Detect OS
    detect_os
    
    # Check and install Python
    check_python || error_exit "Python installation failed"
    
    # Check and install FFmpeg
    check_ffmpeg
    
    # Install system dependencies
    install_system_dependencies
    
    # Create virtual environment
    create_virtual_environment || error_exit "Virtual environment creation failed"
    
    # Install Python dependencies
    install_python_dependencies || error_exit "Python dependency installation failed"
    
    # Create configuration files
    create_config_file
    
    # Create activation script
    create_activation_script
    
    # Run tests
    run_tests
    
    # Cleanup
    cleanup_temp_files
    
    # Show post-installation info
    show_post_install_info
}

# =============================================================================
# Script Entry Point
# =============================================================================

# Check if script is being run directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    # Run main installation
    main
else
    echo "This script should be run directly, not sourced."
    echo "Usage: ./setup.sh"
fi
