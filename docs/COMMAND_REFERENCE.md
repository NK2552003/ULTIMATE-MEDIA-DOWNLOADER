# Ultimate Media Downloader - Command Reference

## All Working Commands

This document lists all confirmed working commands for Ultimate Media Downloader (`umd`).

---

## Basic Commands

### Interactive Mode
```bash
umd
```
Starts interactive mode with step-by-step guidance (best for beginners).

### Download Video
```bash
umd "https://youtube.com/watch?v=VIDEO_ID"
```
Downloads video in best available quality.

### Download Audio Only
```bash
umd "URL" --audio-only
# Shorthand
umd "URL" -a
```
Downloads audio only in best quality.

---

## Quality & Format Options

### Specify Quality
```bash
umd "URL" --quality 1080p
# Available options: best, worst, 4k, 2160p, 1440p, 1080p, 720p, 480p, 360p
```

### Specify Format
```bash
# Video formats
umd "URL" --format mp4
umd "URL" --format mkv

# Audio formats
umd "URL" --audio-only --format mp3
umd "URL" --audio-only --format flac
umd "URL" --audio-only --format m4a
umd "URL" --audio-only --format opus
umd "URL" --audio-only --format wav
```

### Audio Quality Options
```bash
umd "URL" --audio-only --audio-quality best
umd "URL" --audio-only --audio-quality high
umd "URL" --audio-only --audio-quality medium
umd "URL" --audio-only --audio-quality low
```

### Audio Format Specific
```bash
umd "URL" --audio-only --audio-format mp3
# Available: mp3, flac, opus, m4a, aac, wav
```

---

## Information Commands

### Show Media Info
```bash
umd "URL" --info
```
Displays media information without downloading.

### Show Available Formats
```bash
umd "URL" --show-formats
```
Lists all available formats and qualities for the media.

### Combine Info and Formats
```bash
umd "URL" --info --show-formats
```
Shows complete media information including all available formats.

### Check Version
```bash
umd --version
# or
umd -v
```
Displays the installed version of Ultimate Media Downloader.

### List Supported Platforms
```bash
umd --list-platforms
```
Shows all 1000+ supported platforms.

### Check URL Support
```bash
umd "URL" --check-support
```
Checks if a specific URL/platform is supported.

---

## Advanced Options

### Custom Output Directory
```bash
umd "URL" --output /path/to/folder
# or
umd "URL" -o /path/to/folder
```
Downloads to a specific directory instead of default.

### Verbose Mode (Debugging)
```bash
umd "URL" --verbose
```
Enables verbose output for debugging and detailed logging.

### Embed Metadata
```bash
umd "URL" --audio-only --embed-metadata
```
Embeds metadata (title, artist, album) in audio files.

### Embed Thumbnail/Cover Art
```bash
umd "URL" --audio-only --embed-thumbnail
```
Embeds thumbnail/cover art in audio files.

### Combine Metadata and Thumbnail
```bash
umd "URL" --audio-only --embed-metadata --embed-thumbnail
```
Embeds both metadata and thumbnail in audio files.

### Custom Format String (Advanced)
```bash
umd "URL" --custom-format "bestvideo+bestaudio/best"
```
Uses custom yt-dlp format selector string.

---

## Playlist Options

### Download Entire Playlist
```bash
umd "PLAYLIST_URL" --playlist
# or
umd "PLAYLIST_URL" -p
```
Downloads all videos from a playlist (with interactive options).

### Download Single Video from Playlist
```bash
umd "PLAYLIST_URL" --no-playlist
```
Downloads only the specified video, ignoring the playlist.

### Limit Playlist Downloads
```bash
umd "PLAYLIST_URL" --max-downloads 10
# or
umd "PLAYLIST_URL" -m 10
```
Downloads only the first 10 videos from the playlist.

### Start from Specific Index
```bash
umd "PLAYLIST_URL" --start-index 5
# or
umd "PLAYLIST_URL" -s 5
```
Starts downloading from the 5th video in the playlist.

### Combine Playlist Options
```bash
umd "PLAYLIST_URL" --start-index 5 --max-downloads 10
```
Downloads 10 videos starting from the 5th video.

---

## Batch Download Options

### Batch Download from File
```bash
umd --batch-file urls.txt
```
Downloads all URLs listed in `urls.txt` (one URL per line).

### Optimized Batch Download (Parallel)
```bash
umd --batch-file urls.txt --optimized-batch
```
Uses parallel processing for faster batch downloads.

### Set Maximum Concurrent Downloads
```bash
umd --batch-file urls.txt --optimized-batch --max-concurrent 5
```
Downloads up to 5 videos simultaneously (default: 3).

### Batch Download with Options
```bash
umd --batch-file urls.txt --audio-only --format mp3 --embed-metadata
```
Applies options to all URLs in the batch file.

---

## Audio-Specific Options

### Prefer Artist Cover Art
```bash
umd "URL" --audio-only --prefer-artist-art
```
Tries to fetch artist cover art instead of video thumbnail.

### Audio Language Selection
```bash
umd "URL" --audio-language en
# or
umd "URL" --audio-lang es
```
Selects specific audio language for videos with multiple audio tracks.

---

## Performance & Timeout Options

### Set Timeout
```bash
umd "URL" --timeout 120
```
Sets operation timeout to 120 seconds (default: 60).

---

## Interactive Mode Options

### Force Interactive Mode with URL
```bash
umd "URL" --interactive
```
Starts interactive mode for the provided URL.

### Non-Interactive Mode (Automation)
```bash
umd "URL" --no-interactive
```
Disables all interactive prompts (uses only provided arguments).

---

## Spotify & Music Platforms

### Download Spotify Track/Album/Playlist
```bash
umd "SPOTIFY_URL" --audio-only
umd "SPOTIFY_URL" --audio-only --format mp3 --embed-metadata
```
Downloads from Spotify by searching YouTube for matching track.

### Download with Full Metadata
```bash
umd "SPOTIFY_URL" --audio-only --format mp3 --embed-metadata --embed-thumbnail
```
Downloads Spotify music with complete metadata and cover art.

---

## Real-World Examples

### High-Quality Music Download
```bash
umd "URL" --audio-only --audio-format flac --embed-metadata --embed-thumbnail
```

### Quick MP3 Download
```bash
umd "URL" -a --format mp3
```

### 4K Video Download
```bash
umd "URL" --quality 4k --format mp4
```

### Download Entire YouTube Playlist as MP3
```bash
umd "PLAYLIST_URL" --playlist --audio-only --format mp3 --embed-metadata
```

### Batch Download with Custom Settings
```bash
umd --batch-file music.txt --audio-only --format mp3 --embed-metadata --optimized-batch --max-concurrent 5
```

### Debug Download Issues
```bash
umd "URL" --verbose --info
```

### Download to Specific Folder
```bash
umd "URL" --audio-only --output ~/Music/Downloads --format mp3 --embed-metadata
```

---

## Command Combinations

All commands can be combined as needed:

```bash
# Complete example with all features
umd "URL" \
    --audio-only \
    --audio-format flac \
    --audio-quality best \
    --embed-metadata \
    --embed-thumbnail \
    --output ~/Music \
    --verbose

# Playlist with quality and format
umd "PLAYLIST_URL" \
    --playlist \
    --quality 1080p \
    --format mp4 \
    --start-index 1 \
    --max-downloads 20

# Batch optimized download
umd --batch-file urls.txt \
    --optimized-batch \
    --max-concurrent 5 \
    --audio-only \
    --format mp3 \
    --embed-metadata \
    --no-interactive
```

---

## Help Command

### Show All Options
```bash
umd --help
# or
umd -h
```
Displays complete help with all available options.

---

## Notes

- **Default Output Directory**: `~/Downloads/UltimateDownloader`
- **Default Quality**: `best` (highest available)
- **Default Audio Quality**: `best` (320kbps for MP3, highest for others)
- **Default Timeout**: 60 seconds
- **Default Max Concurrent**: 3 (for optimized batch downloads)

---

## Tips

1. **Always check formats first**: `umd "URL" --show-formats` before downloading
2. **Use verbose mode for debugging**: Add `--verbose` to see detailed error messages
3. **Test with `--info` first**: Check media info before downloading large files
4. **Use batch files for multiple downloads**: More efficient than running commands separately
5. **Enable optimized batch for speed**: Use `--optimized-batch` for parallel downloads
6. **Embed metadata for music**: Use `--embed-metadata --embed-thumbnail` for complete audio files

---

## Quick Reference Table

| Command | Shorthand | Description |
|---------|-----------|-------------|
| `--audio-only` | `-a` | Download audio only |
| `--quality` | `-q` | Specify video quality |
| `--format` | `-f` | Output format |
| `--output` | `-o` | Output directory |
| `--playlist` | `-p` | Download playlist |
| `--max-downloads` | `-m` | Max playlist downloads |
| `--start-index` | `-s` | Playlist start index |
| `--info` | `-i` | Show media info |
| `--version` | `-v` | Show version |
| `--help` | `-h` | Show help |

---

**All commands listed in this document are tested and working!** ✅

For more information, see:
- [README.md](README.md) - Full documentation
- [QUICKSTART.md](QUICKSTART.md) - Quick start guide
- [GETTING_STARTED.md](GETTING_STARTED.md) - Getting started guide

---

<div align="center">

Made with ❤️ by [NK2552003](https://github.com/NK2552003)

[⬆ Back to Top](#ultimate-media-downloader---command-reference)

</div>
