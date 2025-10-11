# Windows Batch Files - Documentation

## Overview

Complete set of Windows batch files for installing and managing Ultimate Media Downloader on Windows systems.

---

## Files Created/Available

### 1. **install.bat**  (NEW)
**Location**: `scripts/install.bat`  
**Purpose**: Quick installation with pipx (recommended method)  
**Size**: ~4.1 KB

**Features**:
- Checks Python installation and version
- Verifies FFmpeg (with installation instructions if missing)
- Installs using pipx (or falls back to pip)
- Creates global `umd` command
- Sets up downloads directory
- Provides PATH configuration instructions
- User-friendly error messages

**Usage**:
```batch
cd ULTIMATE-MEDIA-DOWNLOADER
scripts\install.bat
```

---

### 2. **uninstall.bat**  (NEW)
**Location**: `scripts/uninstall.bat`  
**Purpose**: Clean uninstallation  
**Size**: ~1.5 KB

**Features**:
- Confirms before uninstalling
- Tries pipx first, falls back to pip
- Preserves downloaded files
- Clear success messages

**Usage**:
```batch
cd ULTIMATE-MEDIA-DOWNLOADER
scripts\uninstall.bat
```

---

### 3. **setup.bat** (Existing)
**Location**: `scripts/setup.bat`  
**Purpose**: Traditional virtual environment setup  
**Size**: ~16 KB

**Features**:
- Creates virtual environment
- Installs all dependencies
- Creates config.json
- More control for developers

**Usage**:
```batch
cd ULTIMATE-MEDIA-DOWNLOADER
scripts\setup.bat
```

---

### 4. **activate-env.bat** (Existing)
**Location**: `scripts/activate-env.bat`  
**Purpose**: Activate virtual environment  
**Size**: ~944 B

**Usage**:
```batch
scripts\activate-env.bat
```

---

## Which Script to Use?

### For End Users (Recommended)
```batch
scripts\install.bat
```
**Why?**
- Simplest installation
- No need to activate environment
- Global `umd` command
- Works from any directory

### For Developers
```batch
scripts\setup.bat
```
**Why?**
- Isolated environment
- Full control
- Good for development/testing

---

## Installation Comparison

| Feature | install.bat | setup.bat |
|---------|-------------|-----------|
| Virtual Environment | No | Yes |
| Global Command | Yes (`umd`) | No |
| Activation Needed | No | Yes |
| Good For | End Users | Developers |
| Installation Time | 2-3 min | 3-5 min |
| Ease of Use | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |

---

## Quick Start for Windows Users

### Step 1: Install Git & Python
1. Install Python from [python.org](https://www.python.org/downloads/)
   - ️ Check "Add Python to PATH"
2. Install Git from [git-scm.com](https://git-scm.com/downloads)

### Step 2: Clone Repository
```batch
git clone https://github.com/NK2552003/ULTIMATE-MEDIA-DOWNLOADER.git
cd ULTIMATE-MEDIA-DOWNLOADER
```

### Step 3: Run Installer
```batch
scripts\install.bat
```

### Step 4: Use It
```batch
umd <URL>
```

---

## ️ Troubleshooting

### "Python is not recognized"
**Solution**: Add Python to PATH
1. Find Python installation (usually `C:\Users\<User>\AppData\Local\Programs\Python\Python311`)
2. Add to PATH:
   - Open System Properties → Environment Variables
   - Add `C:\Users\<User>\AppData\Local\Programs\Python\Python311`
   - Add `C:\Users\<User>\AppData\Local\Programs\Python\Python311\Scripts`

### "FFmpeg is not recognized"
**Option 1 - Chocolatey** (Recommended):
```batch
choco install ffmpeg
```

**Option 2 - Scoop**:
```batch
scoop install ffmpeg
```

**Option 3 - Manual**:
1. Download from [ffmpeg.org](https://ffmpeg.org/download.html)
2. Extract to `C:\ffmpeg`
3. Add `C:\ffmpeg\bin` to PATH

### "'umd' is not recognized"
**Solution 1**: Restart Command Prompt/PowerShell

**Solution 2**: Add Python Scripts to PATH
```powershell
# In PowerShell (as Administrator)
[Environment]::SetEnvironmentVariable("Path", $env:Path + ";$env:APPDATA\Python\Python311\Scripts", "User")
```

### "Permission Denied"
**Solution**: Run Command Prompt as Administrator

---

## Update Process

To update to latest version:

```batch
cd ULTIMATE-MEDIA-DOWNLOADER
git pull
scripts\install.bat
```

---

## ️ Uninstallation

### Quick Uninstall
```batch
cd ULTIMATE-MEDIA-DOWNLOADER
scripts\uninstall.bat
```

### Manual Uninstall
```batch
pipx uninstall ultimate-downloader
```
or
```batch
pip uninstall ultimate-downloader
```

---

## Batch File Features

### Error Handling
All batch files include:
- Exit codes for automation
- Error messages with solutions
- Graceful fallbacks

### User Experience
- Clear progress indicators ([1/5], [2/5], etc.)
- Color-coded output (OK, WARNING, ERROR)
- Pause at the end for reading
- Confirmation prompts for destructive actions

### Compatibility
- Works on Windows 10/11
- Compatible with Command Prompt
- Compatible with PowerShell
- Supports both Python 3.9-3.13

---

## Batch File Structure

Each batch file follows this structure:

```batch
@echo off
REM Description
setlocal enabledelayedexpansion

echo Header
echo [Step X/Y] Action...
[Commands]
echo [OK] Success message

pause  # So user can read output
```

---

## Testing Checklist

Before committing:
- [x] install.bat creates global `umd` command
- [x] uninstall.bat removes package cleanly
- [x] Error messages are helpful
- [x] FFmpeg check works
- [x] Python version check works
- [x] PATH instructions are correct
- [x] Works on Windows 10
- [x] Works on Windows 11
- [x] Works with PowerShell
- [x] Works with Command Prompt

---

## File Sizes

- `install.bat`: 4.1 KB
- `uninstall.bat`: 1.5 KB
- `setup.bat`: 16 KB
- `activate-env.bat`: 944 B

**Total**: ~22.5 KB

---

## Key Improvements in New Files

### install.bat
- Uses pipx for better isolation
- Automatic PATH detection
- Better FFmpeg instructions
- Clearer error messages
- Matches install.sh functionality

### uninstall.bat
- Tries multiple methods
- Confirms before action
- Clear about what's preserved
- Matches uninstall.sh functionality

---

## Documentation References

These batch files are documented in:
- [README.md](../README.md) - Main documentation
- [INSTALLATION_GUIDE.md](../INSTALLATION_GUIDE.md) - Detailed Windows instructions
- [GITHUB_QUICKSTART.md](../GITHUB_QUICKSTART.md) - Quick start guide

---

## Consistency with Unix Scripts

The Windows batch files mirror the Unix shell scripts:

| Unix | Windows | Purpose |
|------|---------|---------|
| `install.sh` | `install.bat` | Quick install with pipx |
| `uninstall.sh` | `uninstall.bat` | Clean uninstall |
| `setup.sh` | `setup.bat` | Virtual environment setup |
| `activate-env.sh` | `activate-env.bat` | Activate environment |

**Result**: Consistent experience across all platforms! 

---

## Usage Tips

1. **Always run from project root or scripts folder**
2. **Use install.bat for simplest experience**
3. **Keep Command Prompt open to read messages**
4. **Restart terminal after installation**
5. **Add FFmpeg before installing if possible**

---

**All Windows batch files are ready for production use!** 

Users can now install Ultimate Media Downloader on Windows as easily as on macOS/Linux!
