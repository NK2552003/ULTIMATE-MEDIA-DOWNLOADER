# Installation Guide - Ultimate Media Downloader

This guide provides step-by-step instructions to install Ultimate Media Downloader from GitHub.

---

## Table of Contents

- [Prerequisites](#prerequisites)
- [Quick Install (Recommended)](#quick-install-recommended)
- [Manual Installation Methods](#manual-installation-methods)
- [Platform-Specific Instructions](#platform-specific-instructions)
- [Verification](#verification)
- [Troubleshooting](#troubleshooting)
- [Uninstallation](#uninstallation)

---

## Prerequisites

### System Requirements

- **Operating System**: Linux, macOS 10.12+, or Windows 10+
- **Python**: Version 3.9 or higher
- **Git**: For cloning the repository
- **Internet Connection**: For downloading dependencies
- **Disk Space**: ~100MB for installation + space for downloads

### Required Software

Before installing, ensure you have:

1. **Python 3.9+** - [Download here](https://www.python.org/downloads/)
2. **Git** - [Download here](https://git-scm.com/downloads)
3. **FFmpeg** (will be checked during installation)

To verify your Python version:

```bash
python3 --version
```

---

## Quick Install (Recommended)

This is the **easiest and fastest** method. It installs the package globally using `pipx`, allowing you to run `umd` from anywhere.

### Step 1: Clone the Repository

```bash
git clone https://github.com/NK2552003/ULTIMATE-MEDIA-DOWNLOADER.git
cd ULTIMATE-MEDIA-DOWNLOADER
```

### Step 2: Run the Installer

```bash
./scripts/install.sh
```

**For Windows users:**

```batch
scripts\install.bat
```

### Step 3: Start Using

That's it! Now you can use the `umd` command from anywhere:

```bash
umd <URL>
```

### What the Installer Does

 Checks for Python 3.9+ installation  
 Verifies FFmpeg (prompts to install if missing)  
 Installs `pipx` if not present  
 Installs the package globally  
 Creates the `umd` command  
 Sets up downloads directory at `~/Downloads/UltimateDownloader`  

**Installation time**: 2-5 minutes

---

## Manual Installation Methods

### Method 1: Using pipx (No Virtual Environment)

`pipx` installs Python applications in isolated environments while making them globally accessible.

#### Install pipx

**macOS:**
```bash
brew install pipx
pipx ensurepath
```

**Linux:**
```bash
python3 -m pip install --user pipx
python3 -m pipx ensurepath
```

**Windows:**
```batch
python -m pip install --user pipx
python -m pipx ensurepath
```

#### Install Ultimate Media Downloader

```bash
# Clone the repository
git clone https://github.com/NK2552003/ULTIMATE-MEDIA-DOWNLOADER.git
cd ULTIMATE-MEDIA-DOWNLOADER

# Install with pipx
pipx install -e .
```

Now use `umd` from anywhere!

---

### Method 2: Using pip (System-wide)

```bash
# Clone the repository
git clone https://github.com/NK2552003/ULTIMATE-MEDIA-DOWNLOADER.git
cd ULTIMATE-MEDIA-DOWNLOADER

# Install with pip
pip3 install -e .
```

**Note:** You may need to use `--user` flag or `sudo` depending on your system.

---

### Method 3: Virtual Environment (Traditional)

For isolated development or if you prefer traditional virtual environments:

```bash
# Clone the repository
git clone https://github.com/NK2552003/ULTIMATE-MEDIA-DOWNLOADER.git
cd ULTIMATE-MEDIA-DOWNLOADER

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Run directly
python ultimate_downloader.py <URL>
```

---

## Platform-Specific Instructions

### macOS

#### Prerequisites Installation

```bash
# Install Homebrew (if not already installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python and FFmpeg
brew install python@3.11 ffmpeg

# Install pipx
brew install pipx
pipx ensurepath
```

#### Install Ultimate Media Downloader

```bash
git clone https://github.com/NK2552003/ULTIMATE-MEDIA-DOWNLOADER.git
cd ULTIMATE-MEDIA-DOWNLOADER
./scripts/install.sh
```

#### Add to PATH (if needed)

Add this to your `~/.zshrc` or `~/.bash_profile`:

```bash
export PATH="$PATH:$HOME/Library/Python/3.11/bin"
```

Then reload:
```bash
source ~/.zshrc
```

---

### Linux

#### Ubuntu/Debian

```bash
# Update package list
sudo apt update

# Install prerequisites
sudo apt install -y python3 python3-pip python3-venv ffmpeg git

# Clone and install
git clone https://github.com/NK2552003/ULTIMATE-MEDIA-DOWNLOADER.git
cd ULTIMATE-MEDIA-DOWNLOADER
./scripts/install.sh
```

#### Fedora/RHEL/CentOS

```bash
# Install prerequisites
sudo dnf install -y python3 python3-pip ffmpeg git

# Clone and install
git clone https://github.com/NK2552003/ULTIMATE-MEDIA-DOWNLOADER.git
cd ULTIMATE-MEDIA-DOWNLOADER
./scripts/install.sh
```

#### Arch Linux

```bash
# Install prerequisites
sudo pacman -S python python-pip ffmpeg git

# Clone and install
git clone https://github.com/NK2552003/ULTIMATE-MEDIA-DOWNLOADER.git
cd ULTIMATE-MEDIA-DOWNLOADER
./scripts/install.sh
```

#### Add to PATH (if needed)

Add this to your `~/.bashrc` or `~/.zshrc`:

```bash
export PATH="$PATH:$HOME/.local/bin"
```

Then reload:
```bash
source ~/.bashrc
```

---

### 🪟 Windows

#### Prerequisites Installation

1. **Install Python**
   - Download from [python.org](https://www.python.org/downloads/)
   - ️ **Important**: Check "Add Python to PATH" during installation

2. **Install Git**
   - Download from [git-scm.com](https://git-scm.com/downloads)

3. **Install FFmpeg**
   
   **Option A: Using Chocolatey (Recommended)**
   ```batch
   choco install ffmpeg
   ```

   **Option B: Using Scoop**
   ```batch
   scoop install ffmpeg
   ```

   **Option C: Manual Installation**
   - Download from [ffmpeg.org](https://ffmpeg.org/download.html)
   - Extract and add to PATH

#### Install Ultimate Media Downloader

Open Command Prompt or PowerShell:

```batch
# Clone the repository
git clone https://github.com/NK2552003/ULTIMATE-MEDIA-DOWNLOADER.git
cd ULTIMATE-MEDIA-DOWNLOADER

# Run the installer
scripts\install.bat
```

Or use the setup script:

```batch
scripts\setup.bat
```

---

## Verification

After installation, verify everything is working:

### Check Installation

```bash
# Check if umd command is available
umd --version

# Show help
umd --help

# List supported platforms
umd --list-platforms
```

### Test Download

```bash
# Start interactive mode
umd

# Or download a test video
umd "https://www.youtube.com/watch?v=dQw4w9WgXcQ" --info
```

---

## Troubleshooting

### Command Not Found: umd

**Solution 1**: Reload your shell configuration

```bash
# macOS/Linux
source ~/.zshrc  # or ~/.bashrc

# Windows (restart Command Prompt)
```

**Solution 2**: Add Python bin to PATH manually

**macOS:**
```bash
export PATH="$PATH:$HOME/Library/Python/3.11/bin"
```

**Linux:**
```bash
export PATH="$PATH:$HOME/.local/bin"
```

**Windows:** Add `%APPDATA%\Python\Python311\Scripts` to PATH

---

### FFmpeg Not Found

**macOS:**
```bash
brew install ffmpeg
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt install ffmpeg
```

**Windows:**
```batch
choco install ffmpeg
```

---

### Permission Denied

**Linux/macOS:**

Make the script executable:
```bash
chmod +x scripts/install.sh
./scripts/install.sh
```

Or run with bash:
```bash
bash scripts/install.sh
```

---

### Python Version Too Old

Check your Python version:
```bash
python3 --version
```

If it's below 3.9, install a newer version:

**macOS:**
```bash
brew install python@3.11
```

**Ubuntu/Debian:**
```bash
sudo apt install python3.11
```

**Windows:** Download from [python.org](https://www.python.org/downloads/)

---

### Module Not Found Errors

Reinstall dependencies:

```bash
pip3 install -r requirements.txt --upgrade
```

Or reinstall the package:

```bash
pipx reinstall ultimate-downloader
```

---

### Installation Failed

**Try alternative installation methods:**

1. Use pip instead of pipx:
   ```bash
   pip3 install --user -e .
   ```

2. Use virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. Check for conflicting installations:
   ```bash
   which umd
   pip3 list | grep ultimate
   ```

---

## Uninstallation

See the [UNINSTALL.md](UNINSTALL.md) guide for complete uninstallation instructions.

### Quick Uninstall

```bash
# Run the uninstall script
./scripts/uninstall.sh
```

Or manually:

```bash
# If installed with pipx
pipx uninstall ultimate-downloader

# If installed with pip
pip3 uninstall ultimate-downloader
```

---

## Getting Help

If you encounter issues not covered here:

1. Check the [User Guide](docs/USER_GUIDE.md)
2. See [Troubleshooting Guide](docs/guides/TROUBLESHOOTING.md)
3. [Open an issue](https://github.com/NK2552003/ULTIMATE-MEDIA-DOWNLOADER/issues) on GitHub
4. Include:
   - Your OS and version
   - Python version (`python3 --version`)
   - Error messages
   - Installation method used

---

## Next Steps

After successful installation:

- Read the [Quick Start Guide](QUICKSTART.md)
- Explore the [User Guide](docs/USER_GUIDE.md)
- Check [What's New](WHATS_NEW.md) for latest features
- Star the project on [GitHub](https://github.com/NK2552003/ULTIMATE-MEDIA-DOWNLOADER)

---

**Happy Downloading! **
