# User Guide - Ultimate Media Downloader

**Version**: 2.0.0  
**Last Updated**: October 2, 2025

Welcome to the comprehensive user guide for Ultimate Media Downloader. This guide will help you get the most out of the application.

---

## Table of Contents

1. [Getting Started](#getting-started)
2. [Basic Usage](#basic-usage)
3. [Advanced Features](#advanced-features)
4. [Platform-Specific Guides](#platform-specific-guides)
5. [Configuration](#configuration)
6. [Tips & Tricks](#tips--tricks)
7. [FAQ](#faq)

---

## Getting Started

### First Launch

After installation, activate the environment:

```bash
source activate-env.sh
```

You should see a welcome banner:

```
╔════════════════════════════════════════════════════════════════════╗
║        ULTIMATE MEDIA DOWNLOADER - Environment                     ║
║                    Version 2.0.0 - October 2025                    ║
╚════════════════════════════════════════════════════════════════════╝
```

### Quick Test

Test your installation with a simple download:

```bash
python ultimate_downloader.py "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
```

---

## Basic Usage

### Downloading a Video

**Simple download:**
```bash
python ultimate_downloader.py "VIDEO_URL"
```

**Specify output directory:**
```bash
python ultimate_downloader.py -o ~/Videos "VIDEO_URL"
```

**Choose quality:**
```bash
python ultimate_downloader.py --quality 1080 "VIDEO_URL"
```

### Downloading Audio

**Extract audio from video:**
```bash
python ultimate_downloader.py -a "VIDEO_URL"
```

**High-quality audio:**
```bash
python ultimate_downloader.py -a --audio-quality 320 "VIDEO_URL"
```

**Specific audio format:**
```bash
python ultimate_downloader.py -a --audio-format flac "VIDEO_URL"
```

### Interactive Mode

For a user-friendly experience, use interactive mode:

```bash
python ultimate_downloader.py -i
```

You'll be prompted for:
- URL to download
- Download type (video/audio)
- Quality preferences
- Output location

---

## Advanced Features

### Playlist Downloads

**Download entire playlist:**
```bash
python ultimate_downloader.py -p "PLAYLIST_URL"
```

**Download specific range:**
```bash
python ultimate_downloader.py -p --playlist-items 1-10 "PLAYLIST_URL"
```

**Reverse order:**
```bash
python ultimate_downloader.py -p --playlist-reverse "PLAYLIST_URL"
```

**Skip already downloaded:**
```bash
python ultimate_downloader.py -p --archive archive.txt "PLAYLIST_URL"
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
python ultimate_downloader.py --quality 4K "VIDEO_URL"

# Always best quality
python ultimate_downloader.py --quality best "VIDEO_URL"
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
python ultimate_downloader.py --format mkv "VIDEO_URL"

# Audio as FLAC
python ultimate_downloader.py -a --audio-format flac "VIDEO_URL"
```

### Subtitles

**Download with subtitles:**
```bash
python ultimate_downloader.py --subtitles "VIDEO_URL"
```

**Auto-generated subtitles:**
```bash
python ultimate_downloader.py --subtitles --auto-subs "VIDEO_URL"
```

**Specific language:**
```bash
python ultimate_downloader.py --subtitles --sub-lang en "VIDEO_URL"
```

**All available subtitles:**
```bash
python ultimate_downloader.py --all-subs "VIDEO_URL"
```

### Metadata & Thumbnails

**Embed thumbnail:**
```bash
python ultimate_downloader.py --embed-thumbnail "VIDEO_URL"
```

**Embed metadata:**
```bash
python ultimate_downloader.py --embed-metadata "VIDEO_URL"
```

**Both:**
```bash
python ultimate_downloader.py --embed-thumbnail --embed-metadata "VIDEO_URL"
```

### Concurrent Downloads

**Download multiple items simultaneously:**
```bash
python ultimate_downloader.py -p --concurrent 5 "PLAYLIST_URL"
```

**Adjust based on your connection:**
- Slow connection: `--concurrent 1-2`
- Medium connection: `--concurrent 3-5`
- Fast connection: `--concurrent 5-10`

### Proxy Support

**Use HTTP proxy:**
```bash
python ultimate_downloader.py --proxy "http://proxy:port" "VIDEO_URL"
```

**SOCKS proxy:**
```bash
python ultimate_downloader.py --proxy "socks5://proxy:port" "VIDEO_URL"
```

**With authentication:**
```bash
python ultimate_downloader.py --proxy "http://user:pass@proxy:port" "VIDEO_URL"
```

### Search and Download

**Search YouTube:**
```bash
python ultimate_downloader.py --search "song name artist"
```

**Download first result:**
```bash
python ultimate_downloader.py --search "song name" --first
```

**Search with filters:**
```bash
python ultimate_downloader.py --search "tutorial python" --filter duration:short
```

---

## Platform-Specific Guides

### YouTube

**Single video:**
```bash
python ultimate_downloader.py "https://www.youtube.com/watch?v=VIDEO_ID"
```

**Short URL:**
```bash
python ultimate_downloader.py "https://youtu.be/VIDEO_ID"
```

**Playlist:**
```bash
python ultimate_downloader.py -p "https://www.youtube.com/playlist?list=PLAYLIST_ID"
```

**Channel (all videos):**
```bash
python ultimate_downloader.py -p "https://www.youtube.com/c/CHANNEL_NAME/videos"
```

**Live stream:**
```bash
python ultimate_downloader.py "https://www.youtube.com/watch?v=LIVE_ID"
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
python ultimate_downloader.py "https://open.spotify.com/track/TRACK_ID"
```

**Download album:**
```bash
python ultimate_downloader.py -p "https://open.spotify.com/album/ALBUM_ID"
```

**Download playlist:**
```bash
python ultimate_downloader.py -p "https://open.spotify.com/playlist/PLAYLIST_ID"
```

### Instagram

**Post:**
```bash
python ultimate_downloader.py "https://www.instagram.com/p/POST_ID/"
```

**Reel:**
```bash
python ultimate_downloader.py "https://www.instagram.com/reel/REEL_ID/"
```

**IGTV:**
```bash
python ultimate_downloader.py "https://www.instagram.com/tv/VIDEO_ID/"
```

**Note:** Private accounts require authentication (not yet implemented).

### TikTok

**Video:**
```bash
python ultimate_downloader.py "https://www.tiktok.com/@user/video/VIDEO_ID"
```

**User profile (all videos):**
```bash
python ultimate_downloader.py -p "https://www.tiktok.com/@username"
```

**Without watermark:**
```bash
python ultimate_downloader.py --no-watermark "TIKTOK_URL"
```

### SoundCloud

**Track:**
```bash
python ultimate_downloader.py "https://soundcloud.com/artist/track"
```

**Playlist:**
```bash
python ultimate_downloader.py -p "https://soundcloud.com/artist/sets/playlist"
```

**User (all tracks):**
```bash
python ultimate_downloader.py -p "https://soundcloud.com/username"
```

### Twitter/X

**Video tweet:**
```bash
python ultimate_downloader.py "https://twitter.com/user/status/TWEET_ID"
```

**Video with highest quality:**
```bash
python ultimate_downloader.py --quality best "TWITTER_URL"
```

### Facebook

**Video:**
```bash
python ultimate_downloader.py "https://www.facebook.com/watch/?v=VIDEO_ID"
```

**Story (if public):**
```bash
python ultimate_downloader.py "https://www.facebook.com/stories/VIDEO_ID"
```

### Vimeo

**Video:**
```bash
python ultimate_downloader.py "https://vimeo.com/VIDEO_ID"
```

**With password:**
```bash
python ultimate_downloader.py --video-password PASSWORD "VIMEO_URL"
```

### Twitch

**VOD:**
```bash
python ultimate_downloader.py "https://www.twitch.tv/videos/VIDEO_ID"
```

**Clip:**
```bash
python ultimate_downloader.py "https://www.twitch.tv/username/clip/CLIP_ID"
```

**Live stream (saves current stream):**
```bash
python ultimate_downloader.py "https://www.twitch.tv/username"
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
python ultimate_downloader.py -o "~/Music/%(artist)s/%(album)s/%(title)s.%(ext)s" "MUSIC_URL"
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
python ultimate_downloader.py --batch-file urls.txt
```

### 3. Resume Failed Downloads

Use archive mode:

```bash
python ultimate_downloader.py -p --archive archive.txt "PLAYLIST_URL"
```

If interrupted, run again - it will skip completed downloads.

### 4. Download Audio with Best Quality

```bash
python ultimate_downloader.py -a --audio-quality 0 "VIDEO_URL"
```

`0` means "best available".

### 5. Limit Download Speed

```bash
python ultimate_downloader.py --rate-limit 1M "VIDEO_URL"
```

Useful for preventing bandwidth exhaustion.

### 6. Keep Video and Audio Separate

```bash
python ultimate_downloader.py --keep-video --keep-audio "VIDEO_URL"
```

Saves both merged and separate files.

### 7. Download Only New Videos

For following channels:

```bash
python ultimate_downloader.py -p --dateafter 20251001 "CHANNEL_URL"
```

Downloads only videos from October 1, 2025 onwards.

### 8. Custom File Names

```bash
python ultimate_downloader.py -o "%(title)s-%(id)s.%(ext)s" "VIDEO_URL"
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
python ultimate_downloader.py --skip-download --write-thumbnail "VIDEO_URL"
```

### 10. Verify Downloads

Enable checksum verification:

```bash
python ultimate_downloader.py --verify "VIDEO_URL"
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
python ultimate_downloader.py --cookies cookies.txt "VIDEO_URL"
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
pip install -r requirements.txt --upgrade
```

### Q: Can I use this on a server without display?

**A:** Yes, use `--quiet` mode:

```bash
python ultimate_downloader.py --quiet "VIDEO_URL"
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
