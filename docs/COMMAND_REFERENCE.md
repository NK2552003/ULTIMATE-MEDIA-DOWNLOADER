
# Command Reference - Ultimate Media Downloader

## Basic Commands

### Interactive Mode
```bash
umd
```
Guided download with prompts (recommended for beginners).

### Download Media
```bash
umd "URL"                     # Download video
umd "URL" --audio-only        # Download audio only
umd "URL" --quality 1080p     # Specify video quality
umd "URL" --format mp4        # Specify format
```

## Quality Options

| Quality | Description |
|---------|-------------|
| `best` | Highest available (default) |
| `4k` / `2160p` | 4K resolution |
| `1440p` | 2K resolution |
| `1080p` | Full HD |
| `720p` | HD |
| `480p` | SD |
| `360p` | Low quality |
| `worst` | Lowest available |

## Format Options

### Video Formats
- `mp4` - Universal compatibility
- `mkv` - High quality container
- `webm` - Web optimized

### Audio Formats
- `mp3` - Universal compatibility
- `flac` - Lossless quality
- `m4a` - Apple devices
- `opus` - High efficiency
- `wav` - Uncompressed
- `aac` - Good compression

## Advanced Options

### Output Control
```bash
--output DIR              # Custom output directory
--embed-metadata          # Embed metadata in audio files
--embed-thumbnail         # Embed thumbnail in audio files
--verbose                 # Detailed output
--no-interactive          # Disable prompts
```

### Playlist Options
```bash
--playlist                # Download entire playlist
--max-downloads N         # Limit playlist items
--start-index N           # Start from specific index
```

### Batch Downloads
```bash
--batch-file FILE         # Download from URL list file
--optimized-batch         # Parallel downloads
--max-concurrent N        # Max parallel downloads (default: 3)
```

### Information Commands
```bash
--info                    # Show media information
--show-formats            # List available formats
--list-platforms          # Show supported platforms
--version                 # Show version
--help                    # Show help
```

## Platform-Specific Examples

### YouTube
```bash
umd "https://youtube.com/watch?v=VIDEO_ID"
umd "https://youtube.com/playlist?list=PLAYLIST_ID" --playlist
```

### Spotify
```bash
umd "https://open.spotify.com/track/TRACK_ID" --audio-only --format mp3
umd "https://open.spotify.com/album/ALBUM_ID" --audio-only --format flac
```

### Social Media
```bash
umd "https://instagram.com/reel/REEL_ID"
umd "https://tiktok.com/@user/video/VIDEO_ID"
umd "https://twitter.com/user/status/TWEET_ID"
```

### Other Platforms
```bash
umd "https://soundcloud.com/artist/track"
umd "https://vimeo.com/VIDEO_ID"
```

## Command Combinations

### High-Quality Audio
```bash
umd "URL" --audio-only --format flac --embed-metadata --embed-thumbnail
```

### Batch Audio Download
```bash
umd --batch-file urls.txt --audio-only --format mp3 --optimized-batch
```

### 4K Video Download
```bash
umd "URL" --quality 4k --format mp4
```

### Complete Example
```bash
umd "URL" \
    --audio-only \
    --format mp3 \
    --embed-metadata \
    --embed-thumbnail \
    --output ~/Music \
    --verbose
```

## Shortcuts

| Long Form | Short Form |
|-----------|------------|
| `--audio-only` | `-a` |
| `--quality` | `-q` |
| `--format` | `-f` |
| `--output` | `-o` |
| `--playlist` | `-p` |
| `--max-downloads` | `-m` |
| `--start-index` | `-s` |
| `--info` | `-i` |
| `--version` | `-v` |
| `--help` | `-h` |

## Notes

- **Default output**: `~/Downloads/UltimateDownloader/`
- **Default quality**: `best`
- **Default audio quality**: Highest available
- **Platform detection**: Automatic from URL
- **Supported platforms**: 1000+ via yt-dlp

## See Also

- [USAGE.md](USAGE.md) - Usage examples
- [INSTALL.md](INSTALL.md) - Installation guide
- [ARCHITECTURE.md](ARCHITECTURE.md) - Technical details
