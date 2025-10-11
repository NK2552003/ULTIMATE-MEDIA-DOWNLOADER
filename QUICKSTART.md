# Ultimate Media Downloader - Quick Start Guide

## Installation Complete!

Your Ultimate Media Downloader is now installed and ready to use with a single command: **`umd`**

## Quick Start

### 1. Interactive Mode (Easiest)
```bash
umd
```
Just type `umd` and follow the prompts - perfect for beginners!

### 2. Download from URL
```bash
umd "https://www.youtube.com/watch?v=VIDEO_ID"
```

### 3. Download Audio Only
```bash
umd "https://www.youtube.com/watch?v=VIDEO_ID" --audio-only
```

### 4. Download with Specific Quality
```bash
umd "https://www.youtube.com/watch?v=VIDEO_ID" --quality 1080p
```

## Where are my downloads?

All files are automatically saved to:
```
~/Downloads/UltimateDownloader/
```

## Common Use Cases

### Download YouTube Music as MP3
```bash
umd "YOUTUBE_URL" --audio-only --format mp3
```

### Download Spotify Track
```bash
umd "https://open.spotify.com/track/TRACK_ID" --audio-only --format mp3
```

### Download Instagram Video
```bash
umd "https://www.instagram.com/reel/REEL_ID"
```

### Download TikTok Video
```bash
umd "https://www.tiktok.com/@user/video/VIDEO_ID"
```

### Download Entire Playlist
```bash
umd "https://www.youtube.com/playlist?list=PLAYLIST_ID"
```

### Download Best Quality Video
```bash
umd "YOUTUBE_URL" --quality best --format mp4
```

### Download High-Quality Audio (FLAC)
```bash
umd "YOUTUBE_URL" --audio-only --format flac
```

## Pro Tips

### Batch Download Multiple URLs
Create a text file with one URL per line (e.g., `urls.txt`):
```
https://www.youtube.com/watch?v=VIDEO1
https://www.youtube.com/watch?v=VIDEO2
https://www.youtube.com/watch?v=VIDEO3
```

Then run:
```bash
umd --batch-file urls.txt --audio-only
```

### Download with Metadata & Thumbnails
```bash
umd "URL" --audio-only --embed-metadata --embed-thumbnail
```

### Custom Output Directory
```bash
umd "URL" --output /path/to/your/folder
```

### Check Available Formats
```bash
umd "URL" --show-formats
```

### Get Video Information
```bash
umd "URL" --info
```

## ️ All Options

View all available options:
```bash
umd --help
```

### Quality Options
- `best` - Best available quality (default)
- `4k` or `2160p` - 4K resolution
- `1440p` - 2K resolution
- `1080p` - Full HD
- `720p` - HD
- `480p` - SD
- `360p` - Low quality

### Audio Formats
- `mp3` - Universal compatibility
- `flac` - Lossless quality
- `m4a` - Apple devices
- `opus` - High efficiency
- `wav` - Uncompressed
- `aac` - Good compression

### Video Formats
- `mp4` - Universal compatibility
- `mkv` - High quality container
- `webm` - Web optimized

## Supported Platforms

- YouTube (videos, playlists, live streams)
- Spotify (via YouTube search)
- Instagram (videos, reels, IGTV)
- TikTok
- Twitter/X
- Facebook
- SoundCloud
- Vimeo
- Twitch
- Apple Music (via YouTube search)
- And 1000+ more!

## Troubleshooting

### Command not found: umd
Restart your terminal or run:
```bash
source ~/.zshrc
```

### FFmpeg errors
Install FFmpeg:
```bash
brew install ffmpeg
```

### Update the downloader
```bash
pipx upgrade ultimate-downloader
```

### Uninstall
```bash
./uninstall.sh
```
or
```bash
pipx uninstall ultimate-downloader
```

## More Information

- Full Documentation: See `docs/` folder
- GitHub: https://github.com/NK2552003/ULTIMATE-MEDIA-DOWNLOADER
- Issues: Report on GitHub Issues page

## Enjoy!

You can now download media from 1000+ platforms with just one command: **`umd`**

No more:
- Activating virtual environments
- Running long Python commands
- Navigating to project directories
- Specifying download folders

Just type: **`umd <URL>`** and you're done! 
