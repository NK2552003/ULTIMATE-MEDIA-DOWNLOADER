# Installation Troubleshooting Guide

## 🔧 Common Installation Issues and Solutions

This guide helps you resolve common installation problems with Ultimate Media Downloader.

---

## Issue 1: Package Version Conflicts

### Problem
```
ERROR: Could not find a version that satisfies the requirement package>=X.X.X
```

### Solutions

#### Option A: Use Minimal Requirements
```bash
pip install -r requirements-minimal.txt
```

#### Option B: Install Without Version Constraints
```bash
pip install yt-dlp ffmpeg-python requests Pillow beautifulsoup4 lxml mutagen rich pyfiglet spotipy
```

#### Option C: Update pip and setuptools
```bash
python -m pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

---

## Issue 2: pyfiglet Version Error

### Problem
```
ERROR: Could not find a version that satisfies the requirement pyfiglet>=1.0.2
```

### Solution
The correct version is 0.8+. This has been fixed in the repository. Pull the latest changes:
```bash
git pull origin main
pip install -r requirements.txt
```

Or install manually:
```bash
pip install pyfiglet
```

---

## Issue 3: Python Version Compatibility

### Problem
Some packages don't work with your Python version.

### Solution

**Check Python version:**
```bash
python --version
```

**Required:** Python 3.8 or higher

**If Python is too old:**
- macOS: `brew install python@3.11`
- Ubuntu: `sudo apt install python3.11`
- Windows: Download from python.org

Then create a new virtual environment with the correct Python version.

---

## Issue 4: FFmpeg Not Found

### Problem
```
ERROR: FFmpeg is not installed
```

### Solutions

#### macOS
```bash
brew install ffmpeg
```

#### Ubuntu/Debian
```bash
sudo apt update
sudo apt install ffmpeg
```

#### Fedora
```bash
sudo dnf install ffmpeg
```

#### Windows
1. Download from: https://ffmpeg.org/download.html
2. Extract to `C:\ffmpeg`
3. Add `C:\ffmpeg\bin` to PATH

**Verify installation:**
```bash
ffmpeg -version
```

---

## Issue 5: Permission Denied Errors

### Problem
```
PermissionError: [Errno 13] Permission denied
```

### Solutions

#### Linux/macOS
```bash
# Make scripts executable
chmod +x setup.sh install.sh activate_env.sh

# Don't use sudo with pip (use virtual environment instead)
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### Windows
Run Command Prompt or PowerShell as Administrator.

---

## Issue 6: SSL Certificate Errors

### Problem
```
SSLError: certificate verify failed
```

### Solutions

#### Option A: Update certificates
```bash
# macOS
/Applications/Python\ 3.X/Install\ Certificates.command

# Ubuntu
sudo apt install ca-certificates
sudo update-ca-certificates
```

#### Option B: Install with pip trusted host (not recommended for production)
```bash
pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org -r requirements.txt
```

---

## Issue 7: Selenium/ChromeDriver Issues

### Problem
```
WebDriverException: Message: 'chromedriver' executable needs to be in PATH
```

### Solutions

#### Option A: Skip browser automation (recommended)
The downloader works fine without Selenium for most platforms.

#### Option B: Install ChromeDriver
```bash
# macOS
brew install chromedriver

# Ubuntu
sudo apt install chromium-chromedriver

# Or let webdriver-manager handle it automatically (already in requirements)
```

---

## Issue 8: Memory Errors During Installation

### Problem
```
MemoryError: Unable to allocate array
```

### Solution
Install packages one at a time:
```bash
pip install yt-dlp
pip install ffmpeg-python
pip install requests
pip install Pillow
pip install beautifulsoup4
pip install lxml
pip install mutagen
pip install rich
pip install pyfiglet
pip install spotipy
```

---

## Issue 9: Windows Long Path Issues

### Problem
```
FileNotFoundError: [Errno 2] No such file or directory (path too long)
```

### Solution

1. Enable long paths in Windows:
```powershell
# Run as Administrator
New-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\FileSystem" -Name "LongPathsEnabled" -Value 1 -PropertyType DWORD -Force
```

2. Or use shorter output directory:
```bash
python ultimate_downloader.py --output C:\dl
```

---

## Issue 10: Virtual Environment Not Activating

### Problem
Virtual environment activation fails or doesn't work.

### Solutions

#### macOS/Linux
```bash
# If using bash
source venv/bin/activate

# If using zsh
source venv/bin/activate

# If using fish
source venv/bin/activate.fish
```

#### Windows
```powershell
# PowerShell
.\venv\Scripts\Activate.ps1

# If ExecutionPolicy error:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# CMD
venv\Scripts\activate.bat
```

---

## Issue 11: Import Errors After Installation

### Problem
```python
ModuleNotFoundError: No module named 'module_name'
```

### Solutions

1. **Verify you're in virtual environment:**
```bash
which python  # Should show venv path
```

2. **Reinstall the missing package:**
```bash
pip install module_name
```

3. **Check Python path:**
```python
import sys
print(sys.path)
```

---

## Issue 12: Dependencies Conflict

### Problem
```
ERROR: pip's dependency resolver does not currently take into account all the packages that are installed
```

### Solution

#### Option A: Fresh virtual environment
```bash
# Remove old environment
rm -rf venv

# Create new one
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

#### Option B: Use pip-tools
```bash
pip install pip-tools
pip-compile requirements.txt
pip-sync
```

---

## Platform-Specific Issues

### macOS Catalina+

**Issue:** Command Line Tools not installed
```bash
xcode-select --install
```

**Issue:** Homebrew not found
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

### Ubuntu/Debian

**Issue:** Python3-pip not found
```bash
sudo apt update
sudo apt install python3-pip python3-venv
```

**Issue:** Missing development headers
```bash
sudo apt install python3-dev build-essential
```

### Windows

**Issue:** Microsoft Visual C++ required
Download and install: https://visualstudio.microsoft.com/downloads/

**Issue:** Python not in PATH
Reinstall Python and check "Add Python to PATH" during installation.

---

## Testing Your Installation

After resolving issues, test your installation:

```bash
# Activate environment
source venv/bin/activate  # macOS/Linux
# or
venv\Scripts\activate  # Windows

# Test import
python -c "import yt_dlp, rich, mutagen; print('✓ All core modules loaded')"

# Test application
python ultimate_downloader.py --help

# Test download (optional)
python ultimate_downloader.py --check-support "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
```

---

## Still Having Issues?

1. **Check Python version:** Must be 3.8+
   ```bash
   python --version
   ```

2. **Update all tools:**
   ```bash
   python -m pip install --upgrade pip setuptools wheel
   ```

3. **Try minimal installation:**
   ```bash
   pip install -r requirements-minimal.txt
   ```

4. **Check GitHub Issues:**
   https://github.com/NK2552003/ULTIMATE-MEDIA-DOWNLOADER/issues

5. **Create a new issue with:**
   - Your Python version
   - Your OS and version
   - Complete error message
   - Steps you've tried

---

## Quick Reinstall Script

If all else fails, try a complete fresh install:

```bash
#!/bin/bash
# Fresh installation script

# Remove old environment
rm -rf venv

# Create new virtual environment
python3 -m venv venv

# Activate
source venv/bin/activate

# Upgrade pip
python -m pip install --upgrade pip setuptools wheel

# Install minimal requirements first
pip install yt-dlp requests rich beautifulsoup4

# Then install remaining packages
pip install -r requirements.txt

# Test
python ultimate_downloader.py --help

echo "✓ Installation complete!"
```

Save as `fresh_install.sh` and run with `bash fresh_install.sh`

---

## Success Indicators

You'll know installation is successful when:

✅ `pip list` shows all required packages
✅ `python ultimate_downloader.py --help` runs without errors
✅ `ffmpeg -version` shows FFmpeg is installed
✅ Virtual environment activates without errors

---

*Last Updated: October 2, 2024*
