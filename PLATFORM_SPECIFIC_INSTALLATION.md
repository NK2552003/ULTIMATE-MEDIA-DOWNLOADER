# Platform-Specific Installation Guide

This document provides platform-specific installation instructions for **Ultimate Media Downloader (UMD)**.

## Table of Contents

- [macOS](#macos)
- [Linux](#linux)
  - [Ubuntu/Debian](#ubuntudebian)
  - [Fedora/RHEL/CentOS](#fedorarhel-centos)
  - [Arch Linux](#arch-linux)
- [Windows](#windows)
  - [Windows 10/11 (x86/x64)](#windows-1011-x86x64)
- [Docker](#docker)

---

## macOS

### Prerequisites

- macOS 10.13 or later
- Homebrew installed ([brew.sh](https://brew.sh))
- Python 3.9+ (can be installed via Homebrew)

### Installation Methods

#### Option 1: Using Homebrew Tap (Recommended)

```bash
# Add the UMD tap
brew tap NK2552003/umd

# Install UMD
brew install umd

# Verify installation
umd --version
```

#### Option 2: Direct Installation

```bash
# Install directly from formula
brew install --build-from-source https://raw.githubusercontent.com/NK2552003/homebrew-umd/main/Formula/umd.rb

# Verify installation
umd --version
```

#### Option 3: Manual Installation

```bash
# Clone the repository
git clone https://github.com/NK2552003/ULTIMATE-MEDIA-DOWNLOADER.git
cd ULTIMATE-MEDIA-DOWNLOADER

# Run the setup script
bash scripts/setup.sh

# Activate the virtual environment
source venv/bin/activate

# Run UMD
python ultimate_downloader.py
```

### Dependencies

The setup script will automatically install:

- FFmpeg (via Homebrew)
- Python 3.9+ dependencies
- yt-dlp
- Spotipy
- spotdl
- Rich CLI libraries

### Uninstall

```bash
# If installed via Homebrew
brew uninstall umd

# Remove tap (optional)
brew untap NK2552003/umd
```

### Troubleshooting

**Problem**: `umd: command not found`

```bash
# Check if installed
brew list | grep umd

# Reinstall
brew reinstall umd
```

**Problem**: FFmpeg not found

```bash
# Install FFmpeg
brew install ffmpeg
```

**Problem**: Python version too old

```bash
# Upgrade Python
brew upgrade python@3.11

# Check version
python3 --version
```

---

## Linux

### Ubuntu/Debian

#### Prerequisites

- Ubuntu 18.04+ or Debian 10+
- `sudo` access
- APT package manager

#### Installation

```bash
# Clone the repository
git clone https://github.com/NK2552003/ULTIMATE-MEDIA-DOWNLOADER.git
cd ULTIMATE-MEDIA-DOWNLOADER

# Run the setup script
sudo bash scripts/setup.sh
```

#### Manual Installation Steps

```bash
# Update package manager
sudo apt update
sudo apt upgrade -y

# Install Python 3.9+
sudo apt install -y python3.9 python3-pip python3-venv python3-dev

# Install FFmpeg
sudo apt install -y ffmpeg

# Install yt-dlp
sudo apt install -y yt-dlp

# Clone and setup
git clone https://github.com/NK2552003/ULTIMATE-MEDIA-DOWNLOADER.git
cd ULTIMATE-MEDIA-DOWNLOADER

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install Python dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Create symlink for easy access
sudo ln -sf "$(pwd)/ultimate_downloader.py" /usr/local/bin/umd
```

#### Uninstall

```bash
# Remove symlink
sudo rm /usr/local/bin/umd

# Remove virtual environment
rm -rf venv

# Remove dependencies (optional)
sudo apt remove -y python3-pip ffmpeg yt-dlp
```

---

### Fedora/RHEL/CentOS

#### Prerequisites

- Fedora 30+, RHEL 7+, or CentOS 7+
- `sudo` access
- DNF or YUM package manager

#### Installation

```bash
# Clone the repository
git clone https://github.com/NK2552003/ULTIMATE-MEDIA-DOWNLOADER.git
cd ULTIMATE-MEDIA-DOWNLOADER

# Run the setup script
sudo bash scripts/setup.sh
```

#### Manual Installation Steps

```bash
# Update package manager
sudo dnf update -y  # or: sudo yum update -y

# Install Python 3.9+
sudo dnf install -y python3.9 python3-pip python3-devel

# Install FFmpeg (from rpmfusion repo)
sudo dnf install -y https://download1.rpmfusion.org/free/fedora/rpmfusion-free-release-$(rpm -E %fedora).noarch.rpm
sudo dnf install -y ffmpeg

# Install yt-dlp
sudo dnf install -y yt-dlp

# Clone and setup
git clone https://github.com/NK2552003/ULTIMATE-MEDIA-DOWNLOADER.git
cd ULTIMATE-MEDIA-DOWNLOADER

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install Python dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Create symlink
sudo ln -sf "$(pwd)/ultimate_downloader.py" /usr/local/bin/umd
```

---

### Arch Linux

#### Prerequisites

- Arch Linux or Manjaro
- `sudo` access (for Manjaro)
- Pacman package manager

#### Installation

```bash
# Clone the repository
git clone https://github.com/NK2552003/ULTIMATE-MEDIA-DOWNLOADER.git
cd ULTIMATE-MEDIA-DOWNLOADER

# Run the setup script
bash scripts/setup.sh
```

#### Manual Installation Steps

```bash
# Update package manager
sudo pacman -Syu

# Install Python and dependencies
sudo pacman -S --noconfirm python python-pip

# Install FFmpeg
sudo pacman -S --noconfirm ffmpeg

# Install yt-dlp (from AUR or pacman)
sudo pacman -S --noconfirm yt-dlp

# Clone and setup
git clone https://github.com/NK2552003/ULTIMATE-MEDIA-DOWNLOADER.git
cd ULTIMATE-MEDIA-DOWNLOADER

# Create virtual environment
python -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install Python dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Create symlink
sudo ln -sf "$(pwd)/ultimate_downloader.py" /usr/local/bin/umd
```

---

## Windows

### Windows 10/11 (x86/x64)

#### Prerequisites

- Windows 10 or 11 (both 32-bit and 64-bit supported)
- PowerShell or Command Prompt
- Administrator access (optional, for system-wide installation)
- Python 3.9+ for Windows ([download](https://www.python.org/downloads/))

#### Installation Method 1: Automatic Setup Script (Recommended)

```batch
REM Download or clone the repository
git clone https://github.com/NK2552003/ULTIMATE-MEDIA-DOWNLOADER.git
cd ULTIMATE-MEDIA-DOWNLOADER

REM Run the setup script
scripts\setup.bat
```

#### Installation Method 2: Manual Installation (x64)

```batch
REM 1. Install Python 3.9+ from https://www.python.org/downloads/
REM    Make sure to check "Add Python to PATH" during installation

REM 2. Download and install FFmpeg
REM    Option A: Using Chocolatey (if installed)
REM    choco install ffmpeg

REM    Option B: Download from https://ffmpeg.org/download.html
REM    And add to PATH

REM 3. Open Command Prompt or PowerShell as Administrator

REM 4. Navigate to the project directory
cd C:\Users\YourUsername\Downloads\ULTIMATE-MEDIA-DOWNLOADER

REM 5. Create virtual environment
python -m venv venv

REM 6. Activate virtual environment
REM    For Command Prompt:
venv\Scripts\activate.bat
REM    For PowerShell:
REM    venv\Scripts\Activate.ps1

REM 7. Upgrade pip
python -m pip install --upgrade pip

REM 8. Install dependencies
pip install -r requirements.txt

REM 9. Test installation
python ultimate_downloader.py --version
```

#### Installation Method 3: Using Chocolatey (x64)

```batch
REM Install Chocolatey (if not already installed)
REM Run as Administrator

REM Install dependencies via Chocolatey
choco install python ffmpeg git -y

REM Clone repository
git clone https://github.com/NK2552003/ULTIMATE-MEDIA-DOWNLOADER.git
cd ULTIMATE-MEDIA-DOWNLOADER

REM Create virtual environment
python -m venv venv
venv\Scripts\activate.bat

REM Install requirements
pip install --upgrade pip
pip install -r requirements.txt
```

#### Installation Method 4: Using Scoop (x64)

```batch
REM Install Scoop (PowerShell as Administrator)
iwr -useb get.scoop.sh | iex

REM Install dependencies
scoop install python ffmpeg git

REM Clone and setup
git clone https://github.com/NK2552003/ULTIMATE-MEDIA-DOWNLOADER.git
cd ULTIMATE-MEDIA-DOWNLOADER

REM Create virtual environment
python -m venv venv
venv\Scripts\Activate.ps1

REM Install requirements
pip install --upgrade pip
pip install -r requirements.txt
```

#### x86 (32-bit) Installation

Windows 32-bit support is the same as x64, but:

1. Download **Python 3.9+ 32-bit** version
2. Download **FFmpeg 32-bit** build
3. The rest of the installation is identical

#### Adding to System PATH (Optional)

To use `umd` from any directory:

```batch
REM Run as Administrator in Command Prompt
setx PATH "%PATH%;C:\path\to\ULTIMATE-MEDIA-DOWNLOADER\venv\Scripts"
```

#### Creating a Shortcut

1. Right-click on Desktop
2. New → Shortcut
3. Enter: `C:\path\to\ULTIMATE-MEDIA-DOWNLOADER\venv\Scripts\python.exe C:\path\to\ultimate_downloader.py`
4. Name it: `Ultimate Media Downloader`

#### Uninstall

```batch
REM Remove virtual environment
rmdir /s /q venv

REM Remove FFmpeg (if via Chocolatey)
choco uninstall ffmpeg -y

REM Or delete the project folder entirely
cd ..
rmdir /s /q ULTIMATE-MEDIA-DOWNLOADER
```

#### Troubleshooting

**Problem**: Python not found

```batch
REM Reinstall Python from https://www.python.org/downloads/
REM IMPORTANT: Check "Add Python to PATH" during installation
```

**Problem**: FFmpeg not found

```batch
REM Install via Chocolatey
choco install ffmpeg -y

REM Or download from https://ffmpeg.org/download.html#build-windows
REM And add to system PATH
```

**Problem**: Virtual environment won't activate

```batch
REM For PowerShell, enable script execution:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

REM Then activate:
venv\Scripts\Activate.ps1
```

**Problem**: ModuleNotFoundError

```batch
REM Ensure venv is activated and reinstall requirements
venv\Scripts\activate.bat
pip install --upgrade pip
pip install -r requirements.txt
```

---

## Docker

For containerized deployment across all platforms:

### Prerequisites

- Docker installed ([docker.com](https://docker.com))
- Docker daemon running

### Dockerfile

Create a `Dockerfile` in the project root:

```dockerfile
FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    ffmpeg \
    git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENTRYPOINT ["python", "ultimate_downloader.py"]
CMD ["--help"]
```

### Build and Run

```bash
# Build image
docker build -t umd:latest .

# Run container
docker run --rm -v ~/Downloads:/downloads umd:latest --help

# Download a file
docker run --rm -v ~/Downloads:/downloads umd:latest "https://youtube.com/watch?v=..."
```

---

## Summary Table

| Platform | Recommended | Alternative | Package Manager |
|----------|-------------|-------------|-----------------|
| **macOS** | Homebrew Tap | Manual | Homebrew |
| **Ubuntu/Debian** | Setup Script | Manual | APT |
| **Fedora/RHEL** | Setup Script | Manual | DNF/YUM |
| **Arch Linux** | Setup Script | Manual | Pacman |
| **Windows 10/11 x64** | Setup Script | Manual | Chocolatey/Scoop |
| **Windows 10/11 x86** | Manual | Docker | Manual/Docker |

---

## Getting Help

If you encounter issues:

1. Check the [Troubleshooting](#troubleshooting) sections above
2. Visit GitHub Issues: https://github.com/NK2552003/ULTIMATE-MEDIA-DOWNLOADER/issues
3. Check system requirements are met
4. Ensure all dependencies are properly installed

---

**Last Updated**: December 5, 2025
**Supported Platforms**: macOS, Linux (Ubuntu/Debian/Fedora/Arch), Windows 10/11 (x86/x64), Docker
