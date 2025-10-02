# Quick Reference - Ultimate Media Downloader

**Version**: 2.0.0 | **Updated**: October 2, 2025

---

## 🚀 Quick Start

```bash
# Setup (first time only)
./setup.sh

# Activate environment
source activate-env.sh

# Download
python ultimate_downloader.py "URL"
```

---

## 📖 Common Commands

### Basic Downloads
```bash
# Video
python ultimate_downloader.py "VIDEO_URL"

# Audio only
python ultimate_downloader.py -a "VIDEO_URL"

# Playlist
python ultimate_downloader.py -p "PLAYLIST_URL"

# Interactive
python ultimate_downloader.py -i
```

### Quality Selection
```bash
# 4K
python ultimate_downloader.py --quality 4K "URL"

# 1080p
python ultimate_downloader.py --quality 1080 "URL"

# Best available
python ultimate_downloader.py --quality best "URL"
```

### Format Options
```bash
# MP4 video
python ultimate_downloader.py --format mp4 "URL"

# MP3 audio
python ultimate_downloader.py -a --audio-format mp3 "URL"

# FLAC audio (lossless)
python ultimate_downloader.py -a --audio-format flac "URL"
```

### Advanced
```bash
# With metadata & thumbnail
python ultimate_downloader.py --embed-metadata --embed-thumbnail "URL"

# With subtitles
python ultimate_downloader.py --subtitles "URL"

# Using proxy
python ultimate_downloader.py --proxy "http://proxy:port" "URL"

# Concurrent downloads
python ultimate_downloader.py -p --concurrent 5 "PLAYLIST_URL"
```

---

## 📂 File Locations

```
setup.sh              → Setup script
activate-env.sh       → Activation script
config.json           → Configuration
requirements.txt      → Dependencies
downloads/            → Downloaded files
venv/                 → Virtual environment
docs/                 → Documentation
```

---

## ⚙️ Configuration

**File**: `config.json`

```json
{
    "download": {
        "output_dir": "downloads",
        "video_quality": "1080",
        "audio_quality": "320"
    }
}
```

---

## 🌐 Supported Platforms

- ✅ YouTube
- ✅ Spotify  
- ✅ Instagram
- ✅ TikTok
- ✅ SoundCloud
- ✅ Twitter/X
- ✅ Facebook
- ✅ Vimeo
- ✅ Twitch
- ✅ 1000+ more

---

## 📊 Command Line Options

| Option | Description |
|--------|-------------|
| `-a, --audio` | Audio only |
| `-p, --playlist` | Playlist mode |
| `-i, --interactive` | Interactive mode |
| `-o DIR` | Output directory |
| `--quality Q` | Video quality |
| `--format F` | Output format |
| `--subtitles` | Download subtitles |
| `--proxy URL` | Use proxy |
| `--concurrent N` | Concurrent downloads |
| `--verbose` | Verbose output |
| `--help` | Show help |

---

## 🆘 Troubleshooting

**FFmpeg not found?**
```bash
# macOS
brew install ffmpeg

# Ubuntu/Debian
sudo apt install ffmpeg
```

**Permission denied?**
```bash
chmod +x setup.sh activate-env.sh
```

**Module not found?**
```bash
source activate-env.sh
pip install -r requirements.txt
```

---

## 📚 Documentation

| Document | Purpose |
|----------|---------|
| README.md | Main documentation |
| docs/USER_GUIDE.md | User manual |
| docs/ARCHITECTURE.md | Technical design |
| docs/FLOWCHARTS.md | Process flows |
| docs/CONTRIBUTING.md | How to contribute |

---

## 🔗 Quick Links

- **GitHub**: [Repository](https://github.com/NK2552003/ULTIMATE-MEDIA-DOWNLOADER)
- **Issues**: [Report Bug](https://github.com/NK2552003/ULTIMATE-MEDIA-DOWNLOADER/issues)
- **Docs**: `/docs` directory
- **License**: MIT

---

## 💡 Tips

1. Use `--quality best` for highest quality
2. Archive mode prevents re-downloading: `--archive archive.txt`
3. Interactive mode is beginner-friendly: `-i`
4. Check config.json for defaults
5. Use verbose for debugging: `--verbose`

---

**For full documentation, see README.md and docs/**

Last Updated: October 2, 2025
