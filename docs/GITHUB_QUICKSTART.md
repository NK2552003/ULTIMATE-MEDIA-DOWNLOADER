# Quick Start from GitHub

Get Ultimate Media Downloader up and running in **under 5 minutes**!

---

## Installation (3 Steps)

### Step 1: Prerequisites

Make sure you have:
- **Python 3.9+** installed ([Download](https://www.python.org/downloads/))
- **Git** installed ([Download](https://git-scm.com/downloads))
- **ffmpeg** installed ([Download](https://ffmpeg.org/))
Check your Python version:
```bash
python3 --version
```

---

### Step 2: Clone and Install

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

The installer will:
- Check Python and FFmpeg
- Install all dependencies
- Create the `umd` command
- Set up downloads folder

**Time required**: 2-5 minutes

---

### Step 3: Verify Installation

```bash
umd --help
```

If you see the help menu, you're ready to go! 

---

## First Download

Try these commands:

### Interactive Mode (Easiest)
```bash
umd
```
Follow the prompts to download your first video!

### Download a YouTube Video
```bash
umd "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
```

### Download Audio Only
```bash
umd "https://www.youtube.com/watch?v=dQw4w9WgXcQ" --audio-only --format mp3
```

### Download Instagram Reel
```bash
umd "https://www.instagram.com/reel/REEL_ID"
```

---

## Where Are My Downloads?

All downloads are saved to:
```
~/Downloads/UltimateDownloader/
```

On Windows:
```
C:\Users\YourUsername\Downloads\UltimateDownloader\
```

---

## 🆘 Troubleshooting

### "Command not found: umd"

**Solution**: Reload your shell or add Python bin to PATH

**macOS/Linux:**
```bash
source ~/.zshrc  # or ~/.bashrc
```

**Windows:** Restart Command Prompt

---

### "FFmpeg not found"

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

**macOS/Linux:**
```bash
chmod +x scripts/install.sh
./scripts/install.sh
```

---

### Still Having Issues?

1. See [INSTALLATION_GUIDE.md](INSTALLATION_GUIDE.md) for detailed instructions
2. Check [Troubleshooting Guide](docs/guides/TROUBLESHOOTING.md)
3. [Open an issue](https://github.com/NK2552003/ULTIMATE-MEDIA-DOWNLOADER/issues)

---

## Next Steps

Now that you're set up:

### Learn More
- [Quick Start Guide](QUICKSTART.md) - Common usage examples
- [User Guide](docs/USER_GUIDE.md) - Complete manual
- [What's New](WHATS_NEW.md) - Latest features

### Common Commands
```bash
# Show all options
umd --help

# List supported platforms
umd --list-platforms

# Download playlist
umd "PLAYLIST_URL"

# Batch download from file
umd --batch-file urls.txt

# High quality audio
umd "URL" --audio-only --format flac

# 4K video
umd "URL" --quality 4k
```

### Get Help
```bash
# Check if URL is supported
umd --check-support "URL"

# Show available formats
umd "URL" --show-formats

# Get info without downloading
umd "URL" --info
```

---

## Supported Platforms

- YouTube (Videos, Playlists, Live, Shorts)
- Spotify (via YouTube search)
- Instagram (Posts, Reels, Stories)
- TikTok
- Twitter/X
- Facebook
- SoundCloud
- Twitch
- Vimeo
- And 1000+ more!

Full list: `umd --list-platforms`

---

## Pro Tips

1. **Use Interactive Mode** when starting out - it guides you through options
2. **Batch downloads** - Create a text file with URLs (one per line) and use `--batch-file`
3. **Parallel downloads** - Use `--optimized-batch` for faster batch downloads
4. **Embed metadata** - Use `--embed-metadata` for audio files to auto-tag
5. **Custom location** - Use `--output /path` to specify download folder

---

## Updating

To update to the latest version:

```bash
cd ULTIMATE-MEDIA-DOWNLOADER
git pull
./scripts/install.sh
```

---

## ️ Uninstalling

To uninstall:

```bash
./scripts/uninstall.sh
```

Or see [UNINSTALL.md](UNINSTALL.md) for complete instructions.

---

## Contributing

Want to contribute? Great! See [CONTRIBUTING.md](CONTRIBUTING.md)

---

## ⭐ Show Your Support

If you find this useful:
- ⭐ Star the repository
- Report bugs
- Suggest features
- Share with others

---

**Happy Downloading! **

[View Full Documentation](docs/INDEX.md) | [Report Issues](https://github.com/NK2552003/ULTIMATE-MEDIA-DOWNLOADER/issues) | [GitHub](https://github.com/NK2552003/ULTIMATE-MEDIA-DOWNLOADER)
