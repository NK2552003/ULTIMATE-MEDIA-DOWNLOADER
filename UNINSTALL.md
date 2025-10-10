# Uninstallation Guide - Ultimate Media Downloader

## Quick Uninstall (Recommended)

Run this single command to uninstall:

```bash
./scripts/uninstall.sh
```

This will:
- Remove the `umd` command from your system
- Uninstall the package and all its dependencies
- Clean up Python packages
- **Keep your downloaded files safe** - they won't be deleted!

---

## Manual Uninstallation

If you prefer to uninstall manually or the script doesn't work, follow these steps:

### Step 1: Uninstall the Python Package

```bash
pip3 uninstall -y ultimate-downloader
```

or if you used `pipx`:

```bash
pipx uninstall ultimate-downloader
```

### Step 2: Remove the Command (Optional)

If the `umd` command is still accessible, check where it's installed:

```bash
which umd
```

Then remove it manually:

```bash
# macOS/Linux
sudo rm $(which umd)

# Or find and remove from your local bin
rm ~/.local/bin/umd
```

### Step 3: Clean Up Dependencies (Optional)

If you want to remove yt-dlp and other dependencies:

```bash
pip3 uninstall -y yt-dlp spotdl colorama requests
```

---

## What Gets Removed

When you uninstall, the following are removed:

- ✅ The `umd` command
- ✅ Python package `ultimate-downloader`
- ✅ Package dependencies (if installed via script)
- ✅ Virtual environment (if created)

## What Stays on Your System

These items are **NOT** removed during uninstallation:

- ✅ **Your downloaded files** in `~/Downloads/UltimateDownloader`
- ✅ Configuration files (if you created any)
- ✅ Python itself
- ✅ ffmpeg (if you installed it)

---

## Complete Cleanup (Optional)

If you want to completely remove everything including downloaded files:

### Remove Downloaded Files

```bash
rm -rf ~/Downloads/UltimateDownloader
```

⚠️ **Warning**: This will permanently delete all your downloaded media files!

### Remove Configuration Files

```bash
# Remove config if you created one
rm -f ~/.config/ultimate-downloader/config.json
rm -rf ~/.config/ultimate-downloader
```

### Remove ffmpeg (Optional)

If you want to uninstall ffmpeg:

**macOS:**
```bash
brew uninstall ffmpeg
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt remove ffmpeg
```

**Linux (Fedora/RHEL):**
```bash
sudo dnf remove ffmpeg
```

**Windows:**
- Uninstall via Settings > Apps > ffmpeg
- Or delete the ffmpeg folder from your Program Files

---

## Uninstall from Homebrew (macOS)

If you installed via Homebrew:

```bash
brew uninstall ultimate-downloader
```

To remove the tap:

```bash
brew untap NK2552003/ultimate-downloader
```

---

## Troubleshooting Uninstallation

### "Command not found: umd" after uninstall
✅ **Good!** This means the uninstallation was successful.

### Package still appears when running `pip list`
Try:
```bash
pip3 uninstall ultimate-downloader
python3 -m pip uninstall ultimate-downloader
```

### Permission denied errors
Use `sudo` for system-wide installations:
```bash
sudo pip3 uninstall ultimate-downloader
```

### Can't find the uninstall script
Navigate to the project directory first:
```bash
cd /path/to/ULTIMATE-MEDIA-DOWNLOADER
./scripts/uninstall.sh
```

Or download it directly:
```bash
curl -O https://raw.githubusercontent.com/NK2552003/ULTIMATE-MEDIA-DOWNLOADER/main/scripts/uninstall.sh
chmod +x uninstall.sh
./uninstall.sh
```

---

## Reinstalling After Uninstall

If you want to reinstall the application:

```bash
./scripts/install.sh
```

Or see the [Installation Guide](INSTALL.md) for more options.

---

## Need Help?

If you experience issues during uninstallation:

1. 📖 Check the [Troubleshooting Section](#troubleshooting-uninstallation) above
2. 🐛 [Open an issue](https://github.com/NK2552003/ULTIMATE-MEDIA-DOWNLOADER/issues) on GitHub
3. 💬 Include:
   - Your operating system
   - Python version (`python3 --version`)
   - Installation method you used
   - Error messages (if any)

---

## Feedback

Before you go, we'd love to hear why you're uninstalling:

- 🐛 Found a bug? [Report it](https://github.com/NK2552003/ULTIMATE-MEDIA-DOWNLOADER/issues)
- 💡 Missing a feature? [Request it](https://github.com/NK2552003/ULTIMATE-MEDIA-DOWNLOADER/issues)
- 📝 Just sharing feedback? [Start a discussion](https://github.com/NK2552003/ULTIMATE-MEDIA-DOWNLOADER/discussions)

Thank you for trying Ultimate Media Downloader! 🙏

---

## See Also

- [Installation Guide](INSTALL.md) - To reinstall
- [Quick Start Guide](QUICKSTART.md) - Getting started
- [User Guide](docs/USER_GUIDE.md) - Full documentation
- [FAQ](docs/FAQ.md) - Common questions
