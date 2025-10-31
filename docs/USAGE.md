# Usage Guide - Ultimate Media Downloader

## Quick Start

### Interactive Mode (Easiest)
```bash
umd
```
Follow the prompts - perfect for beginners!

### Download from URL
```bash
umd "https://youtube.com/watch?v=VIDEO_ID"
```

### Download Audio Only
```bash
umd "URL" --audio-only --format mp3
```

### Download with Quality
```bash
umd "URL" --quality 1080p
```

## Download Location

All files save to:
```
~/Downloads/UltimateDownloader/
```

## Common Examples

### YouTube
```bash
# Video
umd "https://youtube.com/watch?v=VIDEO_ID"

# Audio only
umd "URL" --audio-only --format mp3

# Playlist
umd "https://youtube.com/playlist?list=PLAYLIST_ID"

# High quality
umd "URL" --quality 4k --format mp4
```

### Spotify
```bash
# Track (downloads from YouTube)
umd "https://open.spotify.com/track/TRACK_ID" --audio-only --format mp3

# Album
umd "https://open.spotify.com/album/ALBUM_ID" --audio-only --format flac

# Playlist
umd "SPOTIFY_PLAYLIST_URL" --audio-only --format mp3
```

### Social Media
```bash
# Instagram Reel
umd "https://instagram.com/reel/REEL_ID"

# TikTok Video
umd "https://tiktok.com/@user/video/VIDEO_ID"

# Twitter Video
umd "https://twitter.com/user/status/TWEET_ID"
```

### Other Platforms
```bash
# SoundCloud
umd "https://soundcloud.com/artist/track"

# Vimeo
umd "https://vimeo.com/VIDEO_ID"

# Facebook
umd "https://facebook.com/video/VIDEO_ID"
```

## Quality & Format Options

### Video Quality
- `best` - Highest available (default)
- `4k` / `2160p` - 4K resolution
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

## Advanced Features

### Batch Downloads
Create `urls.txt` with one URL per line:
```
https://youtube.com/watch?v=VIDEO1
https://youtube.com/watch?v=VIDEO2
https://youtube.com/watch?v=VIDEO3
```

Then run:
```bash
umd --batch-file urls.txt --audio-only --format mp3
```

### Parallel Downloads
```bash
umd --batch-file urls.txt --optimized-batch --max-concurrent 5
```

### Metadata & Thumbnails
```bash
umd "URL" --audio-only --embed-metadata --embed-thumbnail
```

### Custom Output Directory
```bash
umd "URL" --output /path/to/folder
```

### Verbose Mode
```bash
umd "URL" --verbose
```

## Information Commands

### Check URL Support
```bash
umd "URL" --info
```

### Show Available Formats
```bash
umd "URL" --show-formats
```

### List All Platforms
```bash
umd --list-platforms
```

## Command Reference

### Basic Commands
```bash
umd                           # Interactive mode
umd "URL"                     # Download video
umd "URL" --audio-only        # Download audio
umd "URL" --quality 1080p     # Specify quality
umd "URL" --format mp4        # Specify format
umd --batch-file urls.txt     # Batch download
umd --help                    # Show help
umd --version                 # Show version
```

### Advanced Options
```bash
--output DIR                  # Custom output directory
--embed-metadata              # Embed metadata in audio
--embed-thumbnail             # Embed thumbnail in audio
--playlist                    # Download playlist
--max-downloads N             # Limit playlist downloads
--start-index N               # Start from playlist index
--verbose                     # Detailed output
--no-interactive              # Disable prompts
```

## Supported Platforms

### Video Platforms
- YouTube (videos, playlists, live streams, shorts)
- Vimeo
- Dailymotion
- Twitch (VODs, clips, streams)
- Facebook (videos, live)

### Audio Platforms
- Spotify (via YouTube search)
- SoundCloud
- Apple Music (via YouTube search)
- Bandcamp

### Social Media
- Instagram (posts, reels, IGTV, stories)
- TikTok
- Twitter/X
- Reddit
- Snapchat

### Generic Support
- 1000+ sites via yt-dlp

## Pro Tips

1. **Start with interactive mode** (`umd`) to learn options
2. **Use `--info`** before downloading to check formats
3. **Batch downloads** are more efficient than individual commands
4. **Enable parallel downloads** with `--optimized-batch`
5. **Embed metadata** for better audio file organization

## Troubleshooting

### Download fails
- Check internet connection
- Verify URL is correct and accessible
- Try with `--verbose` for details

### Poor quality
- Use `--show-formats` to see available options
- Specify quality explicitly: `--quality 1080p`

### Command not found
- Restart terminal
- Check installation: `umd --version`

### FFmpeg errors
- Install FFmpeg (see [INSTALL.md](INSTALL.md))

## Next Steps

- See [COMMAND_REFERENCE.md](COMMAND_REFERENCE.md) for all options
- Check [ARCHITECTURE.md](ARCHITECTURE.md) for technical details
- Report issues on [GitHub](https://github.com/NK2552003/ULTIMATE-MEDIA-DOWNLOADER/issues)