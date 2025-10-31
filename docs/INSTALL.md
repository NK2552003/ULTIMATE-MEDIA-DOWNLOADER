# Installation Guide - Ultimate Media Downloader

## Quick Install (Recommended)

Install globally in just **2 commands** - no virtual environment needed!

```bash
git clone https://github.com/NK2552003/ULTIMATE-MEDIA-DOWNLOADER.git
cd ULTIMATE-MEDIA-DOWNLOADER
./scripts/install.sh
```

**Windows users:**
```batch
git clone https://github.com/NK2552003/ULTIMATE-MEDIA-DOWNLOADER.git
cd ULTIMATE-MEDIA-DOWNLOADER
scripts\install.bat
```

**What happens:**
- ✅ Checks Python 3.9+ and FFmpeg
- ✅ Installs with pipx (global access)
- ✅ Creates `umd` command everywhere
- ✅ Sets up `~/Downloads/UltimateDownloader/`
- ⏱️ Takes 2-5 minutes

## Prerequisites

### Required Software
- **Python 3.9+** - [Download here](https://www.python.org/downloads/)
- **Git** - [Download here](https://git-scm.com/downloads)
- **FFmpeg** (auto-installed if missing)

Check Python version:
```bash
python3 --version
```

### System Requirements
- **OS**: Linux, macOS 10.12+, Windows 10+
- **RAM**: 2GB minimum, 4GB recommended
- **Storage**: 100MB for install + space for downloads

## Installation Methods

### Method 1: Quick Install (Recommended)

**macOS/Linux:**
```bash
git clone https://github.com/NK2552003/ULTIMATE-MEDIA-DOWNLOADER.git
cd ULTIMATE-MEDIA-DOWNLOADER
./scripts/install.sh
```

**Windows:**
```batch
git clone https://github.com/NK2552003/ULTIMATE-MEDIA-DOWNLOADER.git
cd ULTIMATE-MEDIA-DOWNLOADER
scripts\install.bat
```

### Method 2: Using pipx (Manual)

```bash
# Install pipx if needed
python3 -m pip install --user pipx

# Clone and install
git clone https://github.com/NK2552003/ULTIMATE-MEDIA-DOWNLOADER.git
cd ULTIMATE-MEDIA-DOWNLOADER
pipx install -e .
```

### Method 3: Using pip

```bash
git clone https://github.com/NK2552003/ULTIMATE-MEDIA-DOWNLOADER.git
cd ULTIMATE-MEDIA-DOWNLOADER
pip3 install -e .
```

### Method 4: Virtual Environment

```bash
git clone https://github.com/NK2552003/ULTIMATE-MEDIA-DOWNLOADER.git
cd ULTIMATE-MEDIA-DOWNLOADER
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# or: venv\Scripts\activate  # Windows
pip install -r requirements.txt
python ultimate_downloader.py <URL>
```

## Platform-Specific Setup

### macOS

**Prerequisites:**
```bash
brew install python@3.11 ffmpeg pipx
```

**Install:**
```bash
git clone https://github.com/NK2552003/ULTIMATE-MEDIA-DOWNLOADER.git
cd ULTIMATE-MEDIA-DOWNLOADER
./scripts/install.sh
```

**Add to PATH if needed:**
```bash
echo 'export PATH="$PATH:$HOME/Library/Python/3.11/bin"' >> ~/.zshrc
source ~/.zshrc
```

### Linux (Ubuntu/Debian)

**Prerequisites:**
```bash
sudo apt update
sudo apt install -y python3 python3-pip ffmpeg git
```

**Install:**
```bash
git clone https://github.com/NK2552003/ULTIMATE-MEDIA-DOWNLOADER.git
cd ULTIMATE-MEDIA-DOWNLOADER
./scripts/install.sh
```

**Add to PATH if needed:**
```bash
echo 'export PATH="$PATH:$HOME/.local/bin"' >> ~/.bashrc
source ~/.bashrc
```

### Windows

**Prerequisites:**
1. Install Python from [python.org](https://www.python.org/downloads/) (check "Add to PATH")
2. Install Git from [git-scm.com](https://git-scm.com/downloads)
3. Install FFmpeg:
   - `choco install ffmpeg` (Chocolatey)
   - Or download from [ffmpeg.org](https://ffmpeg.org/download.html)

**Install:**
```batch
git clone https://github.com/NK2552003/ULTIMATE-MEDIA-DOWNLOADER.git
cd ULTIMATE-MEDIA-DOWNLOADER
scripts\install.bat
```

## Verification

After installation, verify everything works:

```bash
# Check command is available
umd --version

# Show help
umd --help

# Test download (optional)
umd "https://www.youtube.com/watch?v=dQw4w9WgXcQ" --info
```

## Download Location

All downloads are automatically saved to:
```
~/Downloads/UltimateDownloader/
```

## Troubleshooting

### "Command not found: umd"
**Solution:** Restart terminal or add to PATH

**macOS/Linux:**
```bash
source ~/.zshrc  # or ~/.bashrc
```

**Windows:** Restart Command Prompt

### "FFmpeg not found"
**macOS:**
```bash
brew install ffmpeg
```

**Linux:**
```bash
sudo apt install ffmpeg
```

**Windows:**
```batch
choco install ffmpeg
```

### Permission denied
**Linux/macOS:**
```bash
chmod +x scripts/install.sh
./scripts/install.sh
```

### Python version too old
Install Python 3.9+ from [python.org](https://www.python.org/downloads/)

## Uninstallation

To uninstall:
```bash
./scripts/uninstall.sh
```

Or manually:
```bash
pipx uninstall ultimate-downloader
# or
pip3 uninstall ultimate-downloader
```

## Next Steps

After installation:
- Read [USAGE.md](USAGE.md) for examples
- Run `umd --help` for all options
- Try `umd` for interactive mode

## Support

- **Issues**: [GitHub Issues](https://github.com/NK2552003/ULTIMATE-MEDIA-DOWNLOADER/issues)
- **Discussions**: [GitHub Discussions](https://github.com/NK2552003/ULTIMATE-MEDIA-DOWNLOADER/discussions)
