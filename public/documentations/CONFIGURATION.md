# Configuration Guide

This document explains how to configure the Ultimate Media Downloader to suit your needs. The application uses a JSON configuration file and environment variables for different settings.

## Table of Contents

1. [Configuration File](#configuration-file)
2. [Configuration Sections](#configuration-sections)
3. [Environment Variables](#environment-variables)
4. [Common Configurations](#common-configurations)

---

## Configuration File

The main configuration file is `config.json` located in the project root directory.

### File Location

```text
umd/
    config.json        <-- Main configuration file
    ultimate_downloader.py
    ...
```

### Configuration Structure

```mermaid
graph TD
    CONFIG[config.json] --> A[spotify]
    CONFIG --> B[apple_music]
    CONFIG --> C[download]
    CONFIG --> D[proxy]
    CONFIG --> E[authentication]
    CONFIG --> F[advanced]
    CONFIG --> G[ui]
    CONFIG --> H[post_processing]
    CONFIG --> I[filters]
```

---

## Configuration Sections

### Spotify Settings

```json
{
    "spotify": {
        "client_id": "",
        "client_secret": "",
        "enabled": false
    }
}
```

| Setting | Type | Description |
|---------|------|-------------|
| `client_id` | string | Spotify API client ID |
| `client_secret` | string | Spotify API client secret |
| `enabled` | boolean | Whether Spotify API is enabled |

To get Spotify API credentials:

1. Go to [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
2. Create a new application
3. Copy the Client ID and Client Secret

### Apple Music Settings

```json
{
    "apple_music": {
        "enabled": false,
        "cookie_file": "",
        "media_user_token": ""
    }
}
```

| Setting | Type | Description |
|---------|------|-------------|
| `enabled` | boolean | Whether Apple Music direct download is enabled |
| `cookie_file` | string | Path to cookies file |
| `media_user_token` | string | Apple Music media user token |

### Download Settings

```json
{
    "download": {
        "output_dir": "downloads",
        "format": "best",
        "audio_format": "mp3",
        "audio_quality": "320",
        "video_quality": "1080",
        "embed_thumbnail": true,
        "embed_metadata": true,
        "subtitles": false,
        "auto_subtitles": false,
        "all_subtitles": false,
        "subtitle_language": "en"
    }
}
```

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `output_dir` | string | "downloads" | Default download directory |
| `format` | string | "best" | Default video format |
| `audio_format` | string | "mp3" | Default audio format |
| `audio_quality` | string | "320" | Audio bitrate in kbps |
| `video_quality` | string | "1080" | Default video quality |
| `embed_thumbnail` | boolean | true | Embed cover art in audio files |
| `embed_metadata` | boolean | true | Embed metadata in files |
| `subtitles` | boolean | false | Download subtitles |
| `subtitle_language` | string | "en" | Subtitle language code |

### Proxy Settings

```json
{
    "proxy": {
        "enabled": false,
        "http": "",
        "https": "",
        "socks5": ""
    }
}
```

| Setting | Type | Description |
|---------|------|-------------|
| `enabled` | boolean | Whether to use proxy |
| `http` | string | HTTP proxy URL |
| `https` | string | HTTPS proxy URL |
| `socks5` | string | SOCKS5 proxy URL |

Example proxy formats:

```text
http://username:password@proxy.example.com:8080
socks5://127.0.0.1:1080
```

### Authentication Settings

```json
{
    "authentication": {
        "youtube": {
            "cookies_file": ""
        },
        "instagram": {
            "username": "",
            "password": ""
        },
        "facebook": {
            "cookies_file": ""
        }
    }
}
```

Using cookies allows downloading age-restricted or private content that you have access to.

### Advanced Settings

```json
{
    "advanced": {
        "concurrent_downloads": 3,
        "retry_attempts": 3,
        "timeout": 300,
        "rate_limit": null,
        "user_agent": "Mozilla/5.0 ...",
        "cookies_file": "",
        "archive_file": "archive.txt",
        "use_cache": true,
        "cache_dir": ".cache"
    }
}
```

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `concurrent_downloads` | integer | 3 | Max parallel downloads |
| `retry_attempts` | integer | 3 | Retries on failure |
| `timeout` | integer | 300 | Request timeout in seconds |
| `rate_limit` | integer/null | null | Download speed limit in KB/s |
| `user_agent` | string | Chrome UA | Browser user agent |
| `archive_file` | string | "archive.txt" | Downloaded URLs record |
| `use_cache` | boolean | true | Enable caching |
| `cache_dir` | string | ".cache" | Cache directory |

### UI Settings

```json
{
    "ui": {
        "show_progress": true,
        "verbose": false,
        "quiet": false,
        "colors": true,
        "ascii_banner": true
    }
}
```

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `show_progress` | boolean | true | Show download progress |
| `verbose` | boolean | false | Enable verbose output |
| `quiet` | boolean | false | Suppress output |
| `colors` | boolean | true | Use colored output |
| `ascii_banner` | boolean | true | Show ASCII art banner |

### Post-Processing Settings

```json
{
    "post_processing": {
        "convert_format": false,
        "target_format": "mp4",
        "normalize_audio": false,
        "organize_files": true,
        "file_template": "%(title)s.%(ext)s"
    }
}
```

| Setting | Type | Description |
|---------|------|-------------|
| `convert_format` | boolean | Convert after download |
| `target_format` | string | Target format for conversion |
| `normalize_audio` | boolean | Normalize audio levels |
| `organize_files` | boolean | Organize into folders |
| `file_template` | string | Filename template |

### Filter Settings

```json
{
    "filters": {
        "min_duration": null,
        "max_duration": null,
        "date_after": null,
        "date_before": null,
        "min_views": null,
        "max_views": null
    }
}
```

These filters skip downloads that do not match criteria:

| Setting | Type | Description |
|---------|------|-------------|
| `min_duration` | integer/null | Minimum duration in seconds |
| `max_duration` | integer/null | Maximum duration in seconds |
| `date_after` | string/null | Only after date (YYYYMMDD) |
| `date_before` | string/null | Only before date (YYYYMMDD) |
| `min_views` | integer/null | Minimum view count |
| `max_views` | integer/null | Maximum view count |

---

## Environment Variables

Some settings can be configured through environment variables, which override config file settings.

### Available Variables

| Variable | Purpose |
|----------|---------|
| `SPOTIFY_CLIENT_ID` | Spotify API client ID |
| `SPOTIFY_CLIENT_SECRET` | Spotify API client secret |
| `APPLE_MUSIC_TOKEN` | Apple Music API token |
| `APPLE_MUSIC_STOREFRONT` | Apple Music region (default: "us") |

### Setting Environment Variables

On macOS and Linux, add to your shell profile:

```bash
# ~/.zshrc or ~/.bashrc
export SPOTIFY_CLIENT_ID="your_client_id"
export SPOTIFY_CLIENT_SECRET="your_client_secret"
```

Then reload:

```bash
source ~/.zshrc
```

On Windows, use System Properties or PowerShell:

```powershell
[Environment]::SetEnvironmentVariable("SPOTIFY_CLIENT_ID", "your_client_id", "User")
```

---

## Common Configurations

### Configuration for Music Downloads

If you primarily download music:

```json
{
    "download": {
        "audio_format": "flac",
        "audio_quality": "320",
        "embed_thumbnail": true,
        "embed_metadata": true
    },
    "post_processing": {
        "organize_files": true,
        "file_template": "%(artist)s - %(title)s.%(ext)s"
    }
}
```

### Configuration for Video Archiving

If you download videos for archival:

```json
{
    "download": {
        "format": "best",
        "video_quality": "2160",
        "subtitles": true,
        "all_subtitles": true
    },
    "advanced": {
        "archive_file": "archive.txt"
    }
}
```

### Configuration for Slow Connections

If you have limited bandwidth:

```json
{
    "download": {
        "video_quality": "720"
    },
    "advanced": {
        "concurrent_downloads": 1,
        "rate_limit": 500,
        "retry_attempts": 5
    }
}
```

### Configuration with Proxy

If you need to use a proxy:

```json
{
    "proxy": {
        "enabled": true,
        "https": "http://proxy.example.com:8080"
    }
}
```

---

## Summary

The configuration system allows you to customize:

- Default download settings
- Audio and video quality preferences
- Proxy and authentication
- UI appearance
- Post-processing behavior
- Content filters

Most users will not need to change the defaults, but power users can fine-tune every aspect of the application's behavior.

For usage instructions, see the [Usage Guide](USAGE.md).
