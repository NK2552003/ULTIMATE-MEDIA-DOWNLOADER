# Installation Guide

This guide will walk you through installing the Ultimate Media Downloader on your system. Whether you are using macOS, Linux, or Windows, this document covers everything you need to get started.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Quick Installation](#quick-installation)
3. [Installation by Platform](#installation-by-platform)
4. [Alternative Installation Methods](#alternative-installation-methods)
5. [Verifying Installation](#verifying-installation)
6. [Troubleshooting](#troubleshooting)
7. [Uninstallation](#uninstallation)

---

## Prerequisites

Before installing, make sure you have the following software on your system.

### Required Software

| Software | Minimum Version | Purpose |
|----------|-----------------|---------|
| Python | 3.9 or higher | Core runtime for the application |
| pip | Latest | Python package manager |
| Git | Any recent version | Cloning the repository |

### Recommended Software

| Software | Purpose |
|----------|---------|
| FFmpeg | Processing audio and video files |
| pipx | Clean isolated installation |

### Checking Your System

Run these commands to check if you have the prerequisites:

```bash
# Check Python version
python3 --version

# Check pip
pip3 --version

# Check Git
git --version

# Check FFmpeg (optional but recommended)
ffmpeg -version
```

If any of these are missing, follow the instructions in the next section for your operating system.

---

## Quick Installation

The fastest way to install is using the provided scripts.

### On macOS and Linux

```bash
# Clone the repository
git clone https://codeberg.org/nk2552003/umd.git

# Enter the directory
cd umd

# Run the install script
./scripts/setup.sh
```

### On Windows

```batch
:: Clone the repository
git clone https://codeberg.org/nk2552003/umd.git

:: Enter the directory
cd umd

:: Run the install script
scripts\setup.bat
```

After installation, you can use the tool from anywhere with the `umd` command:

```bash
umd --help
```

---

## Installation by Platform

### macOS Installation

#### Step 1: Install Homebrew (if not installed)

Homebrew is a package manager for macOS that makes installing software easy.

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

#### Step 2: Install Prerequisites

```bash
# Install Python
brew install python@3.11

# Install FFmpeg
brew install ffmpeg

# Install pipx for clean package installation
brew install pipx
pipx ensurepath
```

#### Step 3: Install Ultimate Media Downloader

```bash
# Clone the repository
git clone https://codeberg.org/nk2552003/umd.git
cd umd

# Run the installer
./scripts/setup.sh
```

#### Step 4: Update PATH (if needed)

If the `umd` command is not found after installation, add the Python bin directory to your PATH:

```bash
echo 'export PATH="$PATH:$HOME/Library/Python/3.11/bin"' >> ~/.zshrc
source ~/.zshrc
```

---

### Linux Installation (Ubuntu/Debian)

#### Step 1: Update Package Lists

```bash
sudo apt update
```

#### Step 2: Install Prerequisites

```bash
# Install Python and pip
sudo apt install -y python3 python3-pip python3-venv

# Install Git
sudo apt install -y git

# Install FFmpeg
sudo apt install -y ffmpeg
```

#### Step 3: Install pipx (Recommended)

```bash
# Install pipx
python3 -m pip install --user pipx
python3 -m pipx ensurepath

# Restart your terminal or run
source ~/.bashrc
```

#### Step 4: Install Ultimate Media Downloader

```bash
# Clone the repository
git clone https://codeberg.org/nk2552003/umd.git
cd umd

# Run the installer
./scripts/setup.sh
```

#### Step 5: Update PATH (if needed)

```bash
echo 'export PATH="$PATH:$HOME/.local/bin"' >> ~/.bashrc
source ~/.bashrc
```

---

### Windows Installation

#### Step 1: Install Python

1. Download Python from [python.org](https://www.python.org/downloads/)
2. Run the installer
3. Check the box that says "Add Python to PATH"
4. Click "Install Now"

#### Step 2: Install Git

1. Download Git from [git-scm.com](https://git-scm.com/downloads)
2. Run the installer with default options

#### Step 3: Install FFmpeg

Option A: Using Chocolatey (if you have it)

```batch
choco install ffmpeg
```

Option B: Manual Installation

1. Download FFmpeg from [ffmpeg.org](https://ffmpeg.org/download.html)
2. Extract to `C:\ffmpeg`
3. Add `C:\ffmpeg\bin` to your system PATH

#### Step 4: Install Ultimate Media Downloader

Open Command Prompt or PowerShell:

```batch
:: Clone the repository
git clone https://codeberg.org/nk2552003/umd.git

:: Enter the directory
cd umd

:: Run the installer
scripts\setup.bat
```

---

## Alternative Installation Methods

### Method 1: Using pip Directly

If you prefer not to use pipx, you can install with pip:

```bash
git clone https://codeberg.org/nk2552003/umd.git
cd umd
pip3 install -e .
```

### Method 2: Using Virtual Environment

For a completely isolated installation:

```bash
# Clone the repository
git clone https://codeberg.org/nk2552003/umd.git
cd umd

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the application
python ultimate_downloader.py --help
```

### Method 3: Using pipx Manually

```bash
# Install pipx if not installed
pip install --user pipx
pipx ensurepath

# Clone and install
git clone https://codeberg.org/nk2552003/umd.git
cd umd
pipx install -e .
```

---

## Verifying Installation

After installation, run these commands to verify everything is working:

```bash
# Check version
umd --version

# Show help
umd --help

# Test with a video (shows info without downloading)
umd "https://www.youtube.com/watch?v=dQw4w9WgXcQ" --info
```

### Expected Output

When you run `umd --help`, you should see output similar to:

```
usage: umd [-h] [-q QUALITY] [-a] [-f FORMAT] [-o OUTPUT] ...

Ultimate Multi-Platform Media Downloader

A powerful, feature-rich downloader supporting many platforms including 
YouTube, Spotify, Instagram, TikTok, SoundCloud, Apple Music, JioSaavn, and more!
```

---

## Troubleshooting

### Common Issues

#### Issue: "command not found: umd"

The `umd` command is not in your PATH.

Solution:

```bash
# macOS
echo 'export PATH="$PATH:$HOME/Library/Python/3.11/bin"' >> ~/.zshrc
source ~/.zshrc

# Linux
echo 'export PATH="$PATH:$HOME/.local/bin"' >> ~/.bashrc
source ~/.bashrc
```

#### Issue: "No module named 'yt_dlp'"

Dependencies were not installed correctly.

Solution:

```bash
pip3 install -r requirements.txt
```

#### Issue: "FFmpeg not found"

FFmpeg is required for audio/video processing.

Solution:

```bash
# macOS
brew install ffmpeg

# Ubuntu/Debian
sudo apt install ffmpeg

# Windows (with Chocolatey)
choco install ffmpeg
```

#### Issue: SSL Certificate Errors

Some platforms have SSL issues.

Solution: The application handles this automatically, but you can also try:

```bash
pip3 install --upgrade certifi
```

#### Issue: "Permission denied" on Linux/macOS

The install script does not have execute permission.

Solution:

```bash
chmod +x scripts/install.sh
./scripts/install.sh
```

### Getting Help

If you encounter issues not covered here:

1. Check the [Issues](https://codeberg.org/nk2552003/umd/issues)
2. Run with verbose mode for more details: `umd --verbose "URL"`
3. Create a new issue with the error message and your system information

---

## Uninstallation

### Using the Uninstall Script

```bash
# macOS/Linux
./scripts/uninstall.sh

# Windows
scripts\uninstall.bat
```

### Manual Uninstallation

If you installed with pipx:

```bash
pipx uninstall ultimate-downloader
```

If you installed with pip:

```bash
pip3 uninstall ultimate-downloader
```

To remove the cloned directory:

```bash
rm -rf umd
```

### Cleaning Up Downloads

The default download location is:

```
~/Downloads/UltimateDownloader/
```

You can remove this folder to clean up downloaded files.

---

## Post-Installation Configuration

### Optional: Set Up Spotify API

For better Spotify metadata extraction:

1. Go to [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
2. Create a new application
3. Get your Client ID and Client Secret
4. Set environment variables:

```bash
export SPOTIFY_CLIENT_ID="your_client_id"
export SPOTIFY_CLIENT_SECRET="your_client_secret"
```

Add these to your shell profile (`.zshrc` or `.bashrc`) to make them permanent.

### Optional: Configure Download Directory

Edit `config.json` in the installation directory to change the default download location:

```json
{
    "download": {
        "output_dir": "/your/custom/path"
    }
}
```

Or use the `--output` flag when running commands:

```bash
umd "URL" --output /path/to/downloads
```

---

## Summary

You now have the Ultimate Media Downloader installed on your system. The installation process:

1. Installed Python dependencies
2. Set up the `umd` command globally
3. Configured the default download directory

For usage instructions, see the [Usage Guide](USAGE.md).

For architecture details, see the [Architecture Documentation](ARCHITECTURE.md).
