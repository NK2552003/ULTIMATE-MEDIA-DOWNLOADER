# User Guide - Ultimate Media Downloader

**Version**: 2.0.0  
**Last Updated**: October 3, 2025  
**Repository**: [ULTIMATE-MEDIA-DOWNLOADER](https://github.com/NK2552003/ULTIMATE-MEDIA-DOWNLOADER)

Welcome to the comprehensive user guide for Ultimate Media Downloader. This guide will help you master all features and capabilities of the application.

---

## 📑 Table of Contents

1. [Getting Started](#getting-started)
2. [Installation](#installation)
3. [Basic Usage](#basic-usage)
4. [Advanced Features](#advanced-features)
5. [Platform-Specific Guides](#platform-specific-guides)
6. [Configuration](#configuration)
7. [Command-Line Reference](#command-line-reference)
8. [Tips & Tricks](#tips--tricks)
9. [Troubleshooting](#troubleshooting)
10. [FAQ](#faq)

---

## Getting Started

### Prerequisites

- **Operating System**: Linux, macOS, or Windows
- **Python**: Version 3.9 or higher
- **Disk Space**: At least 1GB free space
- **Internet**: Stable internet connection

### Installation

#### Quick Setup (Recommended)

```bash
# Clone the repository
git clone https://github.com/NK2552003/ULTIMATE-MEDIA-DOWNLOADER.git
cd ULTIMATE-MEDIA-DOWNLOADER

# Run automated setup
bash setup.sh

# Activate environment
source activate-env.sh
```

The setup script will:
1. ✓ Check Python version
2. ✓ Create virtual environment
3. ✓ Install all dependencies
4. ✓ Create necessary directories
5. ✓ Verify installation

#### Manual Setup

```bash
# Create virtual environment
python3 -m venv venv

# Activate environment
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt
```

### First Launch

After installation, activate the environment:

```bash
source activate-env.sh
```

You should see a welcome banner:

```
╔════════════════════════════════════════════════════════════════════╗
║        ULTIMATE MEDIA DOWNLOADER - Environment Active              ║
║                    Version 2.0.0 - October 2025                    ║
╚════════════════════════════════════════════════════════════════════╝

✓ Environment activated
✓ Python 3.9+ detected
✓ All dependencies installed

Quick Commands:
  python3 ultimate_downloader.py -i          # Interactive mode
  python3 ultimate_downloader.py --help      # Show help
  python3 ultimate_downloader.py "URL"       # Quick download
```

### Quick Test

Test your installation with a simple download:

```bash
python3 ultimate_downloader.py "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
```

If successful, you'll see:
```
▶ Detecting platform... YouTube
↓ Downloading: Rick Astley - Never Gonna Give You Up
⚙ [===================>              ] 45% 125.3 MB/s ETA: 00:15
✓ Download complete: Rick Astley - Never Gonna Give You Up.mp4
```

---

## Basic Usage

### Downloading Videos

#### Simple Download

Download video in best available quality:

```bash
python3 ultimate_downloader.py "VIDEO_URL"
```

**Example**:
```bash
python3 ultimate_downloader.py "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
```

#### Specify Output Directory

```bash
python3 ultimate_downloader.py -o ~/Videos "VIDEO_URL"
```

**Example**:
```bash
python3 ultimate_downloader.py -o ~/Desktop/Downloads "https://youtube.com/watch?v=xxx"
```

#### Choose Video Quality

```bash
python3 ultimate_downloader.py --quality 1080 "VIDEO_URL"
```

**Available Quality Options**:
- `best` - Highest available quality (default)
- `2160` - 4K (2160p)
- `1440` - 2K (1440p)
- `1080` - Full HD (1080p)
- `720` - HD (720p)
- `480` - SD (480p)
- `360` - Low quality (360p)

**Example**:
```bash
# Download in 720p
python3 ultimate_downloader.py --quality 720 "https://youtube.com/watch?v=xxx"
```

---

### Downloading Audio

#### Extract Audio from Video

```bash
python3 ultimate_downloader.py -a "VIDEO_URL"
```

**Example**:
```bash
python3 ultimate_downloader.py -a "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
# Output: Rick Astley - Never Gonna Give You Up.mp3
```

#### High-Quality Audio

```bash
python3 ultimate_downloader.py -a --audio-quality 320 "VIDEO_URL"
```

**Audio Quality Options**:
- `320` - 320 kbps (highest quality, default)
- `256` - 256 kbps (high quality)
- `192` - 192 kbps (good quality)
- `128` - 128 kbps (standard quality)

**Example**:
```bash
python3 ultimate_downloader.py -a --audio-quality 320 "https://youtube.com/watch?v=xxx"
```

#### Choose Audio Format

```bash
python3 ultimate_downloader.py -a --audio-format flac "VIDEO_URL"
```

**Supported Audio Formats**:
- `mp3` - MP3 (most compatible, default)
- `wav` - WAV (lossless, large files)
- `flac` - FLAC (lossless compression)
- `m4a` - M4A/AAC (good quality, smaller files)
- `opus` - Opus (efficient compression)

**Example**:
```bash
# Download as FLAC
python3 ultimate_downloader.py -a --audio-format flac "https://youtube.com/watch?v=xxx"
```

---

### Downloading Playlists

#### Download Entire Playlist

```bash
python3 ultimate_downloader.py -p "PLAYLIST_URL"
```

**Example**:
```bash
python3 ultimate_downloader.py -p "https://www.youtube.com/playlist?list=PLxxxxxx"
```

#### Playlist as Audio

```bash
python3 ultimate_downloader.py -p -a "PLAYLIST_URL"
```

**Example**:
```bash
python3 ultimate_downloader.py -p -a --audio-format mp3 "https://youtube.com/playlist?list=xxx"
```

#### Playlist with Quality Selection

```bash
python3 ultimate_downloader.py -p --quality 720 "PLAYLIST_URL"
```

---

### Interactive Mode

For a user-friendly experience, use interactive mode:

```bash
python3 ultimate_downloader.py -i
```

**Interactive Mode Features**:
- ✓ Guided prompts for all options
- ✓ Auto-detection of platform
- ✓ Quality suggestions based on platform
- ✓ Real-time validation
- ✓ Beautiful progress display

**Interactive Mode Flow**:

```
╔══════════════════════════════════════════════════════════════╗
║         ULTIMATE MEDIA DOWNLOADER - Interactive Mode         ║
╚══════════════════════════════════════════════════════════════╝

? Enter URL to download: https://www.youtube.com/watch?v=xxx
▶ Platform detected: YouTube

? What would you like to download?
  1. Video (best quality)
  2. Audio only
  3. Playlist
> 2

? Select audio format:
  1. MP3 (320 kbps) - Recommended
  2. FLAC (lossless)
  3. WAV (lossless)
  4. M4A (efficient)
> 1

? Output directory: (./downloads)
./downloads

✓ Starting download...
```

---

## Advanced Features

### Spotify Integration

Download Spotify tracks with full metadata embedding.

#### Download Spotify Track

```bash
python3 ultimate_downloader.py "https://open.spotify.com/track/xxx"
```

**Process**:
1. Extract metadata from Spotify
2. Search for track on YouTube
3. Download best audio quality
4. Embed Spotify metadata (artist, album, year)
5. Embed high-resolution album art
6. Rename file to match Spotify track

**Example**:
```bash
python3 ultimate_downloader.py "https://open.spotify.com/track/6rqhFgbbKwnb9MLmUQDhG6"
# Output: Harry Styles - Watermelon Sugar.mp3
# With embedded metadata and album art
```

#### Download Spotify Album

```bash
python3 ultimate_downloader.py -p "https://open.spotify.com/album/xxx"
```

#### Download Spotify Playlist

```bash
python3 ultimate_downloader.py -p "https://open.spotify.com/playlist/xxx"
```

**Note**: For faster Spotify downloads, configure API credentials in `config.json`:

```json
{
  "spotify": {
    "client_id": "YOUR_CLIENT_ID",
    "client_secret": "YOUR_CLIENT_SECRET",
    "enabled": true
  }
}
```

Get credentials from: https://developer.spotify.com/dashboard

---

### Metadata Embedding

Automatically embed rich metadata into audio files.

#### Default Metadata

By default, the downloader embeds:
- Title
- Artist
- Album
- Album art/thumbnail
- Duration
- Year
- Track number (for playlists/albums)

#### Disable Metadata Embedding

```bash
python3 ultimate_downloader.py -a --no-metadata "VIDEO_URL"
```

#### Disable Thumbnail Embedding

```bash
python3 ultimate_downloader.py -a --no-thumbnail "VIDEO_URL"
```

---

### Proxy Support

Use proxy servers for downloads.

#### Configure Proxy in config.json

```json
{
  "proxy": {
    "enabled": true,
    "http": "http://proxy.example.com:8080",
    "https": "https://proxy.example.com:8080",
    "socks5": "socks5://proxy.example.com:1080"
  }
}
```

#### Command-Line Proxy

```bash
export HTTP_PROXY="http://proxy.example.com:8080"
export HTTPS_PROXY="https://proxy.example.com:8080"
python3 ultimate_downloader.py "VIDEO_URL"
```

---

### Concurrent Downloads

Download multiple URLs simultaneously.

Create a file `urls.txt`:
```
https://www.youtube.com/watch?v=xxx1
https://www.youtube.com/watch?v=xxx2
https://www.youtube.com/watch?v=xxx3
```

Download all:
```bash
while read url; do
    python3 ultimate_downloader.py "$url" &
done < urls.txt
wait
```

---

### Archive Mode

Keep track of downloaded URLs to avoid duplicates.

Enable in `config.json`:
```json
{
  "advanced": {
    "archive_file": "archive.txt"
  }
}
```

All downloaded URLs are saved to `archive.txt` and skipped on future runs.

---

## Platform-Specific Guides

### YouTube

#### Download Single Video

```bash
python3 ultimate_downloader.py "https://www.youtube.com/watch?v=xxx"
```

#### Download Playlist

```bash
python3 ultimate_downloader.py -p "https://www.youtube.com/playlist?list=xxx"
```

#### Download Channel Videos

```bash
python3 ultimate_downloader.py -p "https://www.youtube.com/@ChannelName/videos"
```

#### Download with Subtitles

Configure in `config.json`:
```json
{
  "download": {
    "subtitles": true,
    "subtitle_language": "en"
  }
}
```

#### Age-Restricted Videos

Use cookies file for authentication:
```json
{
  "authentication": {
    "youtube": {
      "cookies_file": "cookies.txt"
    }
  }
}
```

Export cookies from browser using extension like "Get cookies.txt"

---

### Spotify

#### Track Download

```bash
python3 ultimate_downloader.py "https://open.spotify.com/track/xxx"
```

#### Album Download

```bash
python3 ultimate_downloader.py -p "https://open.spotify.com/album/xxx"
```

#### Playlist Download

```bash
python3 ultimate_downloader.py -p "https://open.spotify.com/playlist/xxx"
```

**Features**:
- ✓ High-quality audio (320 kbps)
- ✓ Full metadata embedding
- ✓ Album art from Spotify
- ✓ Proper file naming
- ✓ Batch downloads

---

### SoundCloud

#### Track Download

```bash
python3 ultimate_downloader.py "https://soundcloud.com/artist/track"
```

#### Playlist/Set Download

```bash
python3 ultimate_downloader.py -p "https://soundcloud.com/artist/sets/playlist"
```

**Features**:
- ✓ Original quality preservation
- ✓ Metadata extraction
- ✓ Cover art embedding

---

### Instagram

#### Post/Reel Download

```bash
python3 ultimate_downloader.py "https://www.instagram.com/p/xxx/"
```

#### Private Content

Configure credentials in `config.json`:
```json
{
  "authentication": {
    "instagram": {
      "username": "your_username",
      "password": "your_password"
    }
  }
}
```

---

### TikTok

```bash
python3 ultimate_downloader.py "https://www.tiktok.com/@user/video/xxx"
```

**Features**:
- ✓ No watermark (when possible)
- ✓ Original quality
- ✓ Audio extraction supported

---

### Twitter/X

```bash
python3 ultimate_downloader.py "https://twitter.com/user/status/xxx"
```

**Supported**:
- Videos
- GIFs
- Images

---

### Generic Sites

For sites not explicitly supported, the generic downloader tries 10+ methods:

```bash
python3 ultimate_downloader.py "https://example.com/video.mp4"
```

**Methods Tried**:
1. yt-dlp (1000+ sites)
2. Direct download
3. System curl/wget
4. curl-cffi (TLS bypass)
5. cloudscraper (Cloudflare bypass)
6. streamlink (live streams)
7. httpx (HTTP/2)
8. Selenium (browser automation)
9. Playwright (advanced automation)
10. HTML parsing and extraction

---

## Configuration

### Configuration File

Edit `config.json` to customize behavior:

```json
{
  "spotify": {
    "client_id": "",
    "client_secret": "",
    "enabled": false
  },
  "download": {
    "output_dir": "downloads",
    "format": "best",
    "audio_format": "mp3",
    "audio_quality": "320",
    "video_quality": "1080",
    "embed_thumbnail": true,
    "embed_metadata": true,
    "subtitles": false
  },
  "proxy": {
    "enabled": false,
    "http": "",
    "https": ""
  },
  "advanced": {
    "concurrent_downloads": 3,
    "retry_attempts": 3,
    "timeout": 300,
    "archive_file": "archive.txt"
  }
}
```

### Environment Variables

Override settings with environment variables:

```bash
export SPOTIFY_CLIENT_ID="your_id"
export SPOTIFY_CLIENT_SECRET="your_secret"
export OUTPUT_DIR="~/Downloads"
```

---

## Command-Line Reference

### Complete Syntax

```bash
python3 ultimate_downloader.py [OPTIONS] URL
```

### Options

| Option | Description | Example |
|--------|-------------|---------|
| `-h, --help` | Show help message | `--help` |
| `-o, --output DIR` | Output directory | `-o ~/Music` |
| `-a, --audio` | Extract audio only | `-a` |
| `-q, --quality Q` | Video quality | `-q 1080` |
| `--audio-format FMT` | Audio format | `--audio-format flac` |
| `--audio-quality Q` | Audio quality | `--audio-quality 320` |
| `-p, --playlist` | Download playlist | `-p` |
| `-i, --interactive` | Interactive mode | `-i` |
| `-v, --verbose` | Verbose output | `-v` |
| `--version` | Show version | `--version` |
| `--no-metadata` | Skip metadata | `--no-metadata` |
| `--no-thumbnail` | Skip thumbnail | `--no-thumbnail` |

### Examples

```bash
# Download video in 720p
python3 ultimate_downloader.py -q 720 "URL"

# Download audio as FLAC
python3 ultimate_downloader.py -a --audio-format flac "URL"

# Download playlist to specific folder
python3 ultimate_downloader.py -p -o ~/Music/Playlists "URL"

# Interactive mode
python3 ultimate_downloader.py -i

# Verbose mode for debugging
python3 ultimate_downloader.py -v "URL"
```

---

## Tips & Tricks

### 1. Batch Downloads

Create `download_list.sh`:
```bash
#!/bin/bash
urls=(
    "https://youtube.com/watch?v=xxx1"
    "https://youtube.com/watch?v=xxx2"
    "https://youtube.com/watch?v=xxx3"
)

for url in "${urls[@]}"; do
    python3 ultimate_downloader.py -a "$url"
done
```

Run:
```bash
bash download_list.sh
```

---

### 2. Organize Downloads

```bash
# Music downloads
python3 ultimate_downloader.py -a -o ~/Music "SPOTIFY_URL"

# Video downloads
python3 ultimate_downloader.py -o ~/Videos "YOUTUBE_URL"

# Podcasts
python3 ultimate_downloader.py -a -o ~/Podcasts "PODCAST_URL"
```

---

### 3. Quality vs Speed

| Priority | Command | Description |
|----------|---------|-------------|
| Best Quality | `-q best` | Slowest, largest files |
| Balanced | `-q 1080` | Good quality, reasonable size |
| Fast | `-q 720` | Faster, smaller files |
| Fastest | `-q 480` | Quick downloads |

---

### 4. Storage Optimization

```bash
# Lower quality for storage saving
python3 ultimate_downloader.py -a --audio-quality 192 "URL"

# Use efficient formats
python3 ultimate_downloader.py -a --audio-format opus "URL"
```

---

### 5. Automation

Add to cron for scheduled downloads:

```bash
# Edit crontab
crontab -e

# Add job (daily at 2 AM)
0 2 * * * cd /path/to/ULTIMATE-MEDIA-DOWNLOADER && source activate-env.sh && python3 ultimate_downloader.py "URL"
```

---

## Troubleshooting

### Common Issues

#### 1. "Command not found: python3"

**Solution**: Install Python 3.9+
```bash
# macOS
brew install python3

# Ubuntu/Debian
sudo apt install python3

# Check version
python3 --version
```

---

#### 2. "Module not found" errors

**Solution**: Reinstall dependencies
```bash
source activate-env.sh
pip install -r requirements.txt --upgrade
```

---

#### 3. Download fails with "Unable to extract"

**Solution**: Update yt-dlp
```bash
pip install yt-dlp --upgrade
```

---

#### 4. Slow downloads

**Solutions**:
- Try lower quality: `-q 720`
- Check internet connection
- Use proxy if blocked
- Try different time

---

#### 5. Age-restricted content fails

**Solution**: Use cookies file
1. Install browser extension "Get cookies.txt"
2. Export cookies to `cookies.txt`
3. Configure in `config.json`:
```json
{
  "authentication": {
    "youtube": {
      "cookies_file": "cookies.txt"
    }
  }
}
```

---

#### 6. Spotify tracks not found

**Solutions**:
- Check Spotify URL is correct
- Track might be region-restricted
- Try configuring Spotify API credentials
- Manual search alternative on YouTube

---

## FAQ

### Q: Is this legal?

**A**: The tool itself is legal. However, downloading copyrighted content without permission may violate copyright laws. Only download content you have rights to or that is in the public domain.

---

### Q: Which platforms are supported?

**A**: 1000+ platforms including:
- YouTube, Spotify, SoundCloud
- Instagram, TikTok, Twitter
- Facebook, Vimeo, Dailymotion
- Twitch, and many more

See README.md for complete list.

---

### Q: Can I download private/deleted videos?

**A**: No. The downloader can only access publicly available content. Private or deleted content cannot be downloaded.

---

### Q: Why is audio quality limited to 320kbps?

**A**: Most platforms don't provide audio above 320kbps. This is the highest quality available from YouTube and most sources.

---

### Q: Can I download 4K videos?

**A**: Yes! Use `--quality 2160` for 4K downloads (if available).

---

### Q: How do I cancel a download?

**A**: Press `Ctrl+C` to cancel the current download.

---

### Q: Where are files saved?

**A**: By default in `./downloads/`. Change with `-o` option or in `config.json`.

---

### Q: Can I resume interrupted downloads?

**A**: Yes! The downloader automatically resumes interrupted downloads.

---

### Q: How do I update the tool?

**A**:
```bash
cd ULTIMATE-MEDIA-DOWNLOADER
git pull origin main
pip install -r requirements.txt --upgrade
```

---

### Q: Does it work on Windows?

**A**: Yes! Supports Windows, macOS, and Linux.

---

## Getting Help

### Support Channels

- **Documentation**: Check all files in `docs/` folder
- **Issues**: https://github.com/NK2552003/ULTIMATE-MEDIA-DOWNLOADER/issues
- **Discussions**: https://github.com/NK2552003/ULTIMATE-MEDIA-DOWNLOADER/discussions

### Reporting Bugs

When reporting bugs, include:
1. Operating system and version
2. Python version (`python3 --version`)
3. Complete error message
4. Command used
5. URL (if public)

---

## Quick Reference Card

```
QUICK COMMANDS:
  python3 ultimate_downloader.py -i              # Interactive mode
  python3 ultimate_downloader.py "URL"           # Quick download
  python3 ultimate_downloader.py -a "URL"        # Audio only
  python3 ultimate_downloader.py -p "URL"        # Playlist
  python3 ultimate_downloader.py -q 720 "URL"    # 720p video
  python3 ultimate_downloader.py --help          # Show all options

COMMON OPTIONS:
  -o DIR          Output directory
  -a              Audio only
  -p              Playlist
  -q QUALITY      Video quality (360, 720, 1080, best)
  --audio-format  Audio format (mp3, flac, wav)
  -v              Verbose mode
  -i              Interactive mode
```

---

**Last Updated**: October 3, 2025  
**Maintainer**: Nitish Kumar  
**Repository**: [GitHub](https://github.com/NK2552003/ULTIMATE-MEDIA-DOWNLOADER)

---

## Advanced Features

### Playlist Downloads

**Download entire playlist:**
```bash
python3 ultimate_downloader.py -p "PLAYLIST_URL"
```

**Download specific range:**
```bash
python3 ultimate_downloader.py -p --playlist-items 1-10 "PLAYLIST_URL"
```

**Reverse order:**
```bash
python3 ultimate_downloader.py -p --playlist-reverse "PLAYLIST_URL"
```

**Skip already downloaded:**
```bash
python3 ultimate_downloader.py -p --archive archive.txt "PLAYLIST_URL"
```

### Quality Selection

**Available qualities:**
- `4K` or `2160` - 4K resolution
- `1440` - 1440p (2K)
- `1080` - Full HD
- `720` - HD
- `480` - SD
- `360` - Low quality
- `best` - Highest available
- `worst` - Lowest available

**Examples:**
```bash
# Download in 4K
python3 ultimate_downloader.py --quality 4K "VIDEO_URL"

# Always best quality
python3 ultimate_downloader.py --quality best "VIDEO_URL"
```

### Format Selection

**Video formats:**
- `mp4` - MP4 (default, best compatibility)
- `mkv` - Matroska (high quality)
- `webm` - WebM (efficient)
- `avi` - AVI (legacy)

**Audio formats:**
- `mp3` - MP3 (default, best compatibility)
- `flac` - FLAC (lossless)
- `aac` - AAC (efficient)
- `wav` - WAV (uncompressed)
- `opus` - Opus (modern codec)

**Examples:**
```bash
# Download as MKV
python3 ultimate_downloader.py --format mkv "VIDEO_URL"

# Audio as FLAC
python3 ultimate_downloader.py -a --audio-format flac "VIDEO_URL"
```

### Subtitles

**Download with subtitles:**
```bash
python3 ultimate_downloader.py --subtitles "VIDEO_URL"
```

**Auto-generated subtitles:**
```bash
python3 ultimate_downloader.py --subtitles --auto-subs "VIDEO_URL"
```

**Specific language:**
```bash
python3 ultimate_downloader.py --subtitles --sub-lang en "VIDEO_URL"
```

**All available subtitles:**
```bash
python3 ultimate_downloader.py --all-subs "VIDEO_URL"
```

### Metadata & Thumbnails

**Embed thumbnail:**
```bash
python3 ultimate_downloader.py --embed-thumbnail "VIDEO_URL"
```

**Embed metadata:**
```bash
python3 ultimate_downloader.py --embed-metadata "VIDEO_URL"
```

**Both:**
```bash
python3 ultimate_downloader.py --embed-thumbnail --embed-metadata "VIDEO_URL"
```

### Concurrent Downloads

**Download multiple items simultaneously:**
```bash
python3 ultimate_downloader.py -p --concurrent 5 "PLAYLIST_URL"
```

**Adjust based on your connection:**
- Slow connection: `--concurrent 1-2`
- Medium connection: `--concurrent 3-5`
- Fast connection: `--concurrent 5-10`

### Proxy Support

**Use HTTP proxy:**
```bash
python3 ultimate_downloader.py --proxy "http://proxy:port" "VIDEO_URL"
```

**SOCKS proxy:**
```bash
python3 ultimate_downloader.py --proxy "socks5://proxy:port" "VIDEO_URL"
```

**With authentication:**
```bash
python3 ultimate_downloader.py --proxy "http://user:pass@proxy:port" "VIDEO_URL"
```

### Search and Download

**Search YouTube:**
```bash
python3 ultimate_downloader.py --search "song name artist"
```

**Download first result:**
```bash
python3 ultimate_downloader.py --search "song name" --first
```

**Search with filters:**
```bash
python3 ultimate_downloader.py --search "tutorial python" --filter duration:short
```

---

## Platform-Specific Guides

### YouTube

**Single video:**
```bash
python3 ultimate_downloader.py "https://www.youtube.com/watch?v=VIDEO_ID"
```

**Short URL:**
```bash
python3 ultimate_downloader.py "https://youtu.be/VIDEO_ID"
```

**Playlist:**
```bash
python3 ultimate_downloader.py -p "https://www.youtube.com/playlist?list=PLAYLIST_ID"
```

**Channel (all videos):**
```bash
python3 ultimate_downloader.py -p "https://www.youtube.com/c/CHANNEL_NAME/videos"
```

**Live stream:**
```bash
python3 ultimate_downloader.py "https://www.youtube.com/watch?v=LIVE_ID"
```

### Spotify

**Setup (first time):**

1. Go to [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
2. Create an app
3. Get Client ID and Client Secret
4. Edit `config.json`:

```json
{
    "spotify": {
        "client_id": "your_client_id_here",
        "client_secret": "your_client_secret_here"
    }
}
```

**Download track:**
```bash
python3 ultimate_downloader.py "https://open.spotify.com/track/TRACK_ID"
```

**Download album:**
```bash
python3 ultimate_downloader.py -p "https://open.spotify.com/album/ALBUM_ID"
```

**Download playlist:**
```bash
python3 ultimate_downloader.py -p "https://open.spotify.com/playlist/PLAYLIST_ID"
```

### Instagram

**Post:**
```bash
python3 ultimate_downloader.py "https://www.instagram.com/p/POST_ID/"
```

**Reel:**
```bash
python3 ultimate_downloader.py "https://www.instagram.com/reel/REEL_ID/"
```

**IGTV:**
```bash
python3 ultimate_downloader.py "https://www.instagram.com/tv/VIDEO_ID/"
```

**Note:** Private accounts require authentication (not yet implemented).

### TikTok

**Video:**
```bash
python3 ultimate_downloader.py "https://www.tiktok.com/@user/video/VIDEO_ID"
```

**User profile (all videos):**
```bash
python3 ultimate_downloader.py -p "https://www.tiktok.com/@username"
```

**Without watermark:**
```bash
python3 ultimate_downloader.py --no-watermark "TIKTOK_URL"
```

### SoundCloud

**Track:**
```bash
python3 ultimate_downloader.py "https://soundcloud.com/artist/track"
```

**Playlist:**
```bash
python3 ultimate_downloader.py -p "https://soundcloud.com/artist/sets/playlist"
```

**User (all tracks):**
```bash
python3 ultimate_downloader.py -p "https://soundcloud.com/username"
```

### Twitter/X

**Video tweet:**
```bash
python3 ultimate_downloader.py "https://twitter.com/user/status/TWEET_ID"
```

**Video with highest quality:**
```bash
python3 ultimate_downloader.py --quality best "TWITTER_URL"
```

### Facebook

**Video:**
```bash
python3 ultimate_downloader.py "https://www.facebook.com/watch/?v=VIDEO_ID"
```

**Story (if public):**
```bash
python3 ultimate_downloader.py "https://www.facebook.com/stories/VIDEO_ID"
```

### Vimeo

**Video:**
```bash
python3 ultimate_downloader.py "https://vimeo.com/VIDEO_ID"
```

**With password:**
```bash
python3 ultimate_downloader.py --video-password PASSWORD "VIMEO_URL"
```

### Twitch

**VOD:**
```bash
python3 ultimate_downloader.py "https://www.twitch.tv/videos/VIDEO_ID"
```

**Clip:**
```bash
python3 ultimate_downloader.py "https://www.twitch.tv/username/clip/CLIP_ID"
```

**Live stream (saves current stream):**
```bash
python3 ultimate_downloader.py "https://www.twitch.tv/username"
```

---

## Configuration

### Configuration File

Location: `config.json` in the application directory.

**Full configuration example:**

```json
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
        "embed_metadata": true,
        "subtitles": false,
        "auto_subtitles": false
    },
    "proxy": {
        "enabled": false,
        "http": "",
        "https": "",
        "socks": ""
    },
    "advanced": {
        "concurrent_downloads": 3,
        "retry_attempts": 3,
        "timeout": 300,
        "rate_limit": null,
        "user_agent": "Mozilla/5.0...",
        "cookies_file": ""
    },
    "ui": {
        "show_progress": true,
        "verbose": false,
        "quiet": false,
        "colors": true
    }
}
```

### Environment Variables

You can also use environment variables:

```bash
# Spotify credentials
export SPOTIFY_CLIENT_ID="your_client_id"
export SPOTIFY_CLIENT_SECRET="your_client_secret"

# Output directory
export DOWNLOADER_OUTPUT_DIR="~/Downloads"

# Proxy
export DOWNLOADER_PROXY="http://proxy:port"
```

---

## Tips & Tricks

### 1. Organize Downloads Automatically

Create a custom output template:

```bash
python3 ultimate_downloader.py -o "~/Music/%(artist)s/%(album)s/%(title)s.%(ext)s" "MUSIC_URL"
```

### 2. Batch Download from File

Create a file with URLs (one per line):

```bash
# urls.txt
https://www.youtube.com/watch?v=video1
https://www.youtube.com/watch?v=video2
https://www.youtube.com/watch?v=video3
```

Download all:

```bash
python3 ultimate_downloader.py --batch-file urls.txt
```

### 3. Resume Failed Downloads

Use archive mode:

```bash
python3 ultimate_downloader.py -p --archive archive.txt "PLAYLIST_URL"
```

If interrupted, run again - it will skip completed downloads.

### 4. Download Audio with Best Quality

```bash
python3 ultimate_downloader.py -a --audio-quality 0 "VIDEO_URL"
```

`0` means "best available".

### 5. Limit Download Speed

```bash
python3 ultimate_downloader.py --rate-limit 1M "VIDEO_URL"
```

Useful for preventing bandwidth exhaustion.

### 6. Keep Video and Audio Separate

```bash
python3 ultimate_downloader.py --keep-video --keep-audio "VIDEO_URL"
```

Saves both merged and separate files.

### 7. Download Only New Videos

For following channels:

```bash
python3 ultimate_downloader.py -p --dateafter 20251001 "CHANNEL_URL"
```

Downloads only videos from October 1, 2025 onwards.

### 8. Custom File Names

```bash
python3 ultimate_downloader.py -o "%(title)s-%(id)s.%(ext)s" "VIDEO_URL"
```

Available fields:
- `%(title)s` - Video title
- `%(id)s` - Video ID
- `%(ext)s` - Extension
- `%(uploader)s` - Uploader name
- `%(upload_date)s` - Upload date
- `%(duration)s` - Duration

### 9. Download Thumbnails Only

```bash
python3 ultimate_downloader.py --skip-download --write-thumbnail "VIDEO_URL"
```

### 10. Verify Downloads

Enable checksum verification:

```bash
python3 ultimate_downloader.py --verify "VIDEO_URL"
```

---

## FAQ

### Q: Why is my download slow?

**A:** Several factors:
- Server throttling
- Network congestion
- Try using `--concurrent 1` for single-threaded download
- Try different quality: `--quality 720`

### Q: How do I download age-restricted YouTube videos?

**A:** Provide cookies:

```bash
# Export cookies from browser
python3 ultimate_downloader.py --cookies cookies.txt "VIDEO_URL"
```

### Q: Can I download private videos?

**A:** Only if you're authenticated:
- YouTube: Use `--cookies` with logged-in session
- Instagram: Not yet supported
- Facebook: Use `--cookies`

### Q: The download fails with "Video unavailable"

**A:** Possible reasons:
- Video is geo-restricted (try proxy)
- Video is private
- URL is incorrect
- Platform changed their API

### Q: How do I update the application?

**A:**
```bash
cd ULTIMATE-MEDIA-DOWNLOADER
git pull
pip3 install -r requirements.txt --upgrade
```

### Q: Can I use this on a server without display?

**A:** Yes, use `--quiet` mode:

```bash
python3 ultimate_downloader.py --quiet "VIDEO_URL"
```

### Q: How much disk space do I need?

**A:** Depends on content:
- Audio: ~5-10 MB per song
- 720p video: ~50-100 MB per hour
- 1080p video: ~100-300 MB per hour
- 4K video: ~1-3 GB per hour

Always ensure extra space for temporary files.

### Q: Is this legal?

**A:** Legal considerations:
- ✅ Downloading your own content
- ✅ Public domain content
- ✅ Content with explicit permission
- ❌ Copyrighted content without permission
- ❌ Bypassing DRM

**You are responsible for legal compliance.**

### Q: Can I use this commercially?

**A:** The software is MIT licensed, but:
- Respect copyright of downloaded content
- Follow platform terms of service
- Don't redistribute copyrighted content

---

## Getting Help

If you encounter issues:

1. Check this user guide
2. Check [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
3. Search existing [GitHub Issues](https://github.com/NK2552003/ULTIMATE-MEDIA-DOWNLOADER/issues)
4. Create a new issue with:
   - Exact command used
   - Error message
   - Platform and Python version
   - Log output (use `--verbose`)

---

## Next Steps

- Explore [Advanced Configuration](CONFIGURATION.md)
- Read [Architecture Documentation](ARCHITECTURE.md)
- Contribute: See [CONTRIBUTING.md](CONTRIBUTING.md)
- View [Flowcharts](FLOWCHARTS.md) for technical details

---

**Happy Downloading! 🎉**

---

**Last Updated**: October 2, 2025  
**Version**: 2.0.0
