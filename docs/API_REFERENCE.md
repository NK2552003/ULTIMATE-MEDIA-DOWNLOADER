# API Reference - Ultimate Media Downloader

**Version**: 2.0.0  
**Last Updated**: October 3, 2025  
**Python Version**: 3.9+

Complete API documentation for all modules, classes, and functions in the Ultimate Media Downloader project.

---

## Table of Contents

1. [ultimate_downloader Module](#ultimate_downloader-module)
2. [generic_downloader Module](#generic_downloader-module)
3. [logger Module](#logger-module)
4. [ui_components Module](#ui_components-module)
5. [utils Module](#utils-module)
6. [Usage Examples](#usage-examples)

---

## ultimate_downloader Module

Main application module providing the core download functionality.

### Class: `UltimateMediaDownloader`

Primary class handling all media download operations across multiple platforms.

#### Constructor

```python
def __init__(self, output_dir="downloads")
```

**Parameters**:
- `output_dir` (str, optional): Output directory for downloads. Default: "downloads"

**Attributes**:
- `output_dir` (Path): Download output directory
- `console` (Console): Rich console instance
- `spotify_client` (Spotify|None): Spotify API client
- `cancelled` (bool): Cancellation flag
- `default_ydl_opts` (dict): Default yt-dlp options

**Example**:
```python
downloader = UltimateMediaDownloader(output_dir="~/Music")
```

---

#### Method: `download`

```python
def download(self, url: str, **options) -> bool
```

Main download method that handles all platforms.

**Parameters**:
- `url` (str): Media URL to download
- `**options`: Additional download options
  - `audio_only` (bool): Extract audio only
  - `quality` (str): Video quality ('1080', '720', 'best')
  - `audio_format` (str): Audio format ('mp3', 'wav', 'flac')
  - `audio_quality` (str): Audio quality ('320', '256', '128')
  - `playlist` (bool): Download entire playlist
  - `embed_thumbnail` (bool): Embed thumbnail/album art
  - `embed_metadata` (bool): Embed metadata tags

**Returns**:
- `bool`: True if successful, False otherwise

**Example**:
```python
# Download video
downloader.download("https://youtube.com/watch?v=xxx")

# Download audio only
downloader.download("https://youtube.com/watch?v=xxx", audio_only=True)

# High quality audio
downloader.download("https://youtube.com/watch?v=xxx", 
                   audio_only=True, 
                   audio_format='flac',
                   audio_quality='320')
```

---

#### Method: `detect_platform`

```python
def detect_platform(self, url: str) -> str
```

Automatically detect the platform from a URL.

**Parameters**:
- `url` (str): URL to analyze

**Returns**:
- `str`: Platform name ('youtube', 'spotify', 'soundcloud', etc.)

**Example**:
```python
platform = downloader.detect_platform("https://open.spotify.com/track/xxx")
# Returns: 'spotify'
```

---

#### Method: `download_youtube`

```python
def download_youtube(self, url: str, options: dict) -> bool
```

Download from YouTube with optimized settings.

**Parameters**:
- `url` (str): YouTube URL
- `options` (dict): Download options

**Returns**:
- `bool`: Success status

**Features**:
- Supports videos, playlists, channels
- Age-restricted content handling
- Premium quality extraction
- Automatic subtitle download (optional)
- Thumbnail embedding

---

#### Method: `download_spotify`

```python
def download_spotify(self, url: str, options: dict) -> bool
```

Download Spotify tracks by searching on YouTube.

**Parameters**:
- `url` (str): Spotify URL (track/album/playlist)
- `options` (dict): Download options

**Returns**:
- `bool`: Success status

**Process**:
1. Extract Spotify metadata via API or scraping
2. Search for track on YouTube
3. Download highest quality audio
4. Embed Spotify metadata and album art
5. Rename file to match Spotify track

---

#### Method: `search_and_download_spotify_track`

```python
def search_and_download_spotify_track(self, spotify_url: str) -> bool
```

Search YouTube and download Spotify track with metadata.

**Parameters**:
- `spotify_url` (str): Spotify track URL

**Returns**:
- `bool`: Success status

**Example**:
```python
downloader.search_and_download_spotify_track(
    "https://open.spotify.com/track/6rqhFgbbKwnb9MLmUQDhG6"
)
```

---

#### Method: `_extract_spotify_track_info`

```python
def _extract_spotify_track_info(self, spotify_url: str) -> dict
```

Extract track information from Spotify URL.

**Parameters**:
- `spotify_url` (str): Spotify track URL

**Returns**:
- `dict`: Track information
  ```python
  {
      'title': str,
      'artist': str,
      'album': str,
      'year': str,
      'duration': int,
      'album_art': str,  # URL
      'isrc': str
  }
  ```

**Methods Used**:
1. Spotify API (if configured)
2. Web scraping fallback
3. Multiple retry attempts

---

#### Method: `_embed_metadata`

```python
def _embed_metadata(self, file_path: str, metadata: dict) -> bool
```

Embed ID3 metadata tags into audio file.

**Parameters**:
- `file_path` (str): Path to audio file
- `metadata` (dict): Metadata dictionary
  ```python
  {
      'title': str,
      'artist': str,
      'album': str,
      'year': str,
      'track_number': int,
      'genre': str
  }
  ```

**Returns**:
- `bool`: Success status

**Supported Formats**:
- MP3 (ID3v2)
- MP4/M4A (iTunes tags)
- FLAC (Vorbis comments)
- WAV (ID3v2)

---

#### Method: `_embed_thumbnail`

```python
def _embed_thumbnail(self, file_path: str, thumbnail_url: str) -> bool
```

Embed album art/thumbnail into audio file.

**Parameters**:
- `file_path` (str): Path to audio file
- `thumbnail_url` (str): URL or path to image

**Returns**:
- `bool`: Success status

**Features**:
- Automatic image download
- Image resizing (optimal size)
- Format conversion to JPEG/PNG
- High-quality embedding

---

#### Method: `get_supported_sites`

```python
def get_supported_sites(self) -> List[str]
```

Get list of all supported platforms.

**Returns**:
- `List[str]`: List of supported platform names

**Example**:
```python
sites = downloader.get_supported_sites()
print(f"Supported sites: {', '.join(sites)}")
```

---

### Functions

#### Function: `interactive_mode`

```python
def interactive_mode() -> None
```

Launch interactive CLI mode with user prompts.

**Features**:
- URL input with validation
- Platform auto-detection
- Quality selection menu
- Format selection
- Progress display
- Error handling

**Example**:
```bash
python ultimate_downloader.py -i
```

---

#### Function: `main`

```python
def main() -> int
```

Application entry point with argument parsing.

**Returns**:
- `int`: Exit code (0 for success)

**Command-line Arguments**:
```
positional arguments:
  url                   URL to download

optional arguments:
  -h, --help           Show help message
  -o, --output DIR     Output directory
  -a, --audio          Audio only
  -q, --quality Q      Video quality
  --audio-format FMT   Audio format
  --audio-quality Q    Audio quality
  -p, --playlist       Download playlist
  -i, --interactive    Interactive mode
  -v, --verbose        Verbose output
  --version            Show version
```

---

## generic_downloader Module

Advanced generic website downloader with multiple fallback methods.

### Class: `GenericSiteDownloader`

Handles downloads from websites not directly supported by yt-dlp.

#### Constructor

```python
def __init__(self, output_dir: Path, verbose: bool = False, 
             proxies: Optional[List[str]] = None)
```

**Parameters**:
- `output_dir` (Path): Output directory
- `verbose` (bool, optional): Enable verbose logging. Default: False
- `proxies` (List[str], optional): List of proxy URLs

**Example**:
```python
from pathlib import Path

downloader = GenericSiteDownloader(
    output_dir=Path("downloads"),
    verbose=True,
    proxies=["http://proxy1:8080", "http://proxy2:8080"]
)
```

---

#### Method: `download`

```python
def download(self, url: str, output_filename: Optional[str] = None) -> Optional[str]
```

Main download method with multiple fallback strategies.

**Parameters**:
- `url` (str): URL to download
- `output_filename` (str, optional): Custom filename

**Returns**:
- `Optional[str]`: Path to downloaded file or None if failed

**Fallback Order**:
1. yt-dlp (fastest, most compatible)
2. System curl command (reliable)
3. curl-cffi (bypass TLS fingerprinting)
4. cloudscraper (Cloudflare bypass)
5. streamlink (live streams)
6. httpx (modern HTTP/2)
7. selenium (JavaScript rendering)
8. playwright (advanced automation)
9. requests-html (HTML with JS)
10. Direct video download

**Example**:
```python
file_path = downloader.download(
    "https://example.com/video.mp4",
    output_filename="my_video.mp4"
)

if file_path:
    print(f"Downloaded to: {file_path}")
```

---

#### Method: `_download_with_ytdlp`

```python
def _download_with_ytdlp(self, url: str, output_filename: Optional[str]) -> Optional[str]
```

Download using yt-dlp library.

**Parameters**:
- `url` (str): Video URL
- `output_filename` (str, optional): Output filename

**Returns**:
- `Optional[str]`: Downloaded file path or None

**Features**:
- 1000+ site support
- Quality selection
- Format conversion
- Metadata extraction

---

#### Method: `_download_with_selenium`

```python
def _download_with_selenium(self, url: str, output_filename: Optional[str]) -> Optional[str]
```

Download using Selenium browser automation.

**Parameters**:
- `url` (str): Page URL
- `output_filename` (str, optional): Output filename

**Returns**:
- `Optional[str]`: Downloaded file path or None

**Features**:
- JavaScript rendering
- Dynamic content handling
- Undetected ChromeDriver
- Screenshot capture
- Network interception

---

#### Method: `_download_with_cloudscraper`

```python
def _download_with_cloudscraper(self, url: str, output_filename: Optional[str]) -> Optional[str]
```

Download using cloudscraper (Cloudflare bypass).

**Parameters**:
- `url` (str): Protected URL
- `output_filename` (str, optional): Output filename

**Returns**:
- `Optional[str]`: Downloaded file path or None

**Features**:
- Cloudflare challenge solving
- Browser fingerprint emulation
- Cookie handling

---

#### Method: `_create_permissive_ssl_context`

```python
def _create_permissive_ssl_context(self) -> ssl.SSLContext
```

Create SSL context that accepts any certificate.

**Returns**:
- `ssl.SSLContext`: Configured SSL context

**Use Case**: Sites with self-signed or expired certificates

---

#### Method: `_get_random_headers`

```python
def _get_random_headers(self) -> Dict[str, str]
```

Generate random HTTP headers with user agent rotation.

**Returns**:
- `Dict[str, str]`: HTTP headers dictionary

**Example**:
```python
{
    'User-Agent': 'Mozilla/5.0 ...',
    'Accept': 'text/html,...',
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
    'DNT': '1',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1'
}
```

---

## logger Module

Custom logging module for clean terminal output.

### Class: `QuietLogger`

Suppresses verbose yt-dlp output while showing important messages.

#### Methods

```python
def debug(self, msg: str) -> None
```
Suppress debug messages (no output).

```python
def info(self, msg: str) -> None
```
Show selective info messages (downloads, important events).

```python
def warning(self, msg: str) -> None
```
Show warnings with yellow formatting.

```python
def error(self, msg: str) -> None
```
Show errors with red formatting.

**Example**:
```python
from logger import QuietLogger

logger = QuietLogger()
logger.info("Downloading video...")  # May show
logger.debug("Extracting metadata...")  # Suppressed
logger.warning("Low bandwidth detected")  # Shows in yellow
logger.error("Download failed")  # Shows in red
```

---

## ui_components Module

Modern UI components and styling for CLI interface.

### Class: `Icons`

Modern flat design icon system.

#### Method: `get`

```python
@staticmethod
def get(name: str) -> str
```

Get icon by name.

**Parameters**:
- `name` (str): Icon name

**Returns**:
- `str`: Unicode icon character

**Available Icons**:

| Category | Icons | Names |
|----------|-------|-------|
| Status | ✓ ✗ ⚠ ℹ → | success, error, warning, info, tip |
| Media | ▶ ♫ ♪ ≡ ↓ | video, audio, music, playlist, download |
| Progress | ⟳ ⚙ ✓ ✗ | loading, processing, completed, failed |
| Quality | ⚡ ★ ▭ | hd, quality, format |

**Example**:
```python
from ui_components import Icons

print(f"{Icons.get('success')} Download complete!")
print(f"{Icons.get('download')} Downloading...")
```

---

### Class: `Messages`

Centralized message templates with Rich formatting.

#### Methods

```python
@staticmethod
def success(text: str) -> str
```
Returns success message in green.

```python
@staticmethod
def error(text: str) -> str
```
Returns error message in red.

```python
@staticmethod
def warning(text: str) -> str
```
Returns warning message in yellow.

```python
@staticmethod
def info(text: str) -> str
```
Returns info message in cyan.

```python
@staticmethod
def tip(text: str) -> str
```
Returns tip message in magenta.

**Example**:
```python
from ui_components import Messages
from rich.console import Console

console = Console()
console.print(Messages.success("Download completed!"))
console.print(Messages.error("Failed to connect"))
console.print(Messages.warning("Low disk space"))
console.print(Messages.info("Processing video..."))
console.print(Messages.tip("Try using --quality 720 for faster downloads"))
```

---

### Class: `ModernUI`

Complete UI system with panels, progress bars, and tables.

#### Constructor

```python
def __init__(self)
```

Initialize UI system with Rich console.

#### Method: `print_banner`

```python
def print_banner(self, title: str, subtitle: str = "") -> None
```

Display ASCII art banner.

**Parameters**:
- `title` (str): Main title text
- `subtitle` (str, optional): Subtitle text

**Example**:
```python
from ui_components import ModernUI

ui = ModernUI()
ui.print_banner("ULTIMATE DOWNLOADER", "v2.0.0")
```

---

#### Method: `print_panel`

```python
def print_panel(self, content: str, title: str = None, 
                style: str = "cyan", border_style: str = "blue") -> None
```

Display content in a beautiful panel.

**Parameters**:
- `content` (str): Panel content
- `title` (str, optional): Panel title
- `style` (str, optional): Content style. Default: "cyan"
- `border_style` (str, optional): Border color. Default: "blue"

**Example**:
```python
ui.print_panel(
    "Download completed successfully!",
    title="Success",
    style="green",
    border_style="green"
)
```

---

#### Method: `print_table`

```python
def print_table(self, title: str, headers: List[str], 
                rows: List[List[str]], style: str = "cyan") -> None
```

Display data in a formatted table.

**Parameters**:
- `title` (str): Table title
- `headers` (List[str]): Column headers
- `rows` (List[List[str]]): Table data rows
- `style` (str, optional): Table style. Default: "cyan"

**Example**:
```python
ui.print_table(
    title="Download Statistics",
    headers=["File", "Size", "Duration"],
    rows=[
        ["video1.mp4", "125 MB", "10:23"],
        ["audio1.mp3", "8.5 MB", "5:45"]
    ]
)
```

---

#### Method: `create_progress`

```python
def create_progress(self) -> Progress
```

Create Rich progress bar.

**Returns**:
- `Progress`: Configured progress bar instance

**Example**:
```python
progress = ui.create_progress()

with progress:
    task = progress.add_task("Downloading...", total=100)
    for i in range(100):
        progress.update(task, advance=1)
        time.sleep(0.1)
```

---

#### Method: `prompt`

```python
def prompt(self, question: str, choices: List[str] = None) -> str
```

Interactive prompt with optional choices.

**Parameters**:
- `question` (str): Question to ask
- `choices` (List[str], optional): Valid choices

**Returns**:
- `str`: User input

**Example**:
```python
format_choice = ui.prompt(
    "Select format:",
    choices=["mp3", "mp4", "flac"]
)
```

---

#### Method: `confirm`

```python
def confirm(self, question: str, default: bool = True) -> bool
```

Confirmation dialog.

**Parameters**:
- `question` (str): Question to ask
- `default` (bool, optional): Default answer. Default: True

**Returns**:
- `bool`: User confirmation

**Example**:
```python
if ui.confirm("Download entire playlist?"):
    download_playlist()
```

---

## utils Module

Utility functions used across the application.

### File Operations

#### Function: `sanitize_filename`

```python
def sanitize_filename(filename: str) -> str
```

Make filename safe for all operating systems.

**Parameters**:
- `filename` (str): Original filename

**Returns**:
- `str`: Sanitized filename

**Operations**:
- Removes invalid characters: `< > : " / \ | ? *`
- Removes control characters
- Trims whitespace and dots
- Limits length to 200 characters

**Example**:
```python
from utils import sanitize_filename

safe_name = sanitize_filename('My Video: "Amazing" <2024>')
# Returns: 'My Video_ _Amazing_ _2024_'
```

---

#### Function: `ensure_directory`

```python
def ensure_directory(path: str) -> Path
```

Create directory if it doesn't exist.

**Parameters**:
- `path` (str): Directory path

**Returns**:
- `Path`: Path object of created directory

**Example**:
```python
from utils import ensure_directory

downloads_dir = ensure_directory("~/Downloads/Music")
```

---

### Formatting Functions

#### Function: `format_bytes`

```python
def format_bytes(bytes_value: int) -> str
```

Convert bytes to human-readable format.

**Parameters**:
- `bytes_value` (int): Number of bytes

**Returns**:
- `str`: Formatted string (e.g., "10.5 MB")

**Example**:
```python
from utils import format_bytes

size = format_bytes(1048576)
# Returns: "1.00 MB"

size = format_bytes(1536000)
# Returns: "1.46 MB"
```

---

#### Function: `format_duration`

```python
def format_duration(seconds: int) -> str
```

Convert seconds to time format.

**Parameters**:
- `seconds` (int): Duration in seconds

**Returns**:
- `str`: Formatted duration (e.g., "1:23:45")

**Example**:
```python
from utils import format_duration

time = format_duration(3665)
# Returns: "1:01:05"

time = format_duration(125)
# Returns: "2:05"
```

---

#### Function: `truncate_string`

```python
def truncate_string(text: str, length: int = 50) -> str
```

Truncate string with ellipsis.

**Parameters**:
- `text` (str): Text to truncate
- `length` (int, optional): Max length. Default: 50

**Returns**:
- `str`: Truncated string

**Example**:
```python
from utils import truncate_string

short = truncate_string("This is a very long title that needs truncation", 20)
# Returns: "This is a very lo..."
```

---

### URL Analysis Functions

#### Function: `detect_platform`

```python
def detect_platform(url: str) -> str
```

Detect platform from URL.

**Parameters**:
- `url` (str): URL to analyze

**Returns**:
- `str`: Platform name

**Supported Platforms**:
- `'youtube'` - YouTube
- `'spotify'` - Spotify
- `'soundcloud'` - SoundCloud
- `'apple_music'` - Apple Music
- `'instagram'` - Instagram
- `'tiktok'` - TikTok
- `'twitter'` - Twitter/X
- `'facebook'` - Facebook
- `'vimeo'` - Vimeo
- `'dailymotion'` - Dailymotion
- `'twitch'` - Twitch
- `'generic'` - Unknown/other

**Example**:
```python
from utils import detect_platform

platform = detect_platform("https://www.youtube.com/watch?v=xxx")
# Returns: 'youtube'

platform = detect_platform("https://open.spotify.com/track/xxx")
# Returns: 'spotify'
```

---

#### Function: `is_playlist_url`

```python
def is_playlist_url(url: str) -> bool
```

Check if URL is a playlist/album.

**Parameters**:
- `url` (str): URL to check

**Returns**:
- `bool`: True if playlist URL

**Example**:
```python
from utils import is_playlist_url

is_pl = is_playlist_url("https://youtube.com/playlist?list=xxx")
# Returns: True

is_pl = is_playlist_url("https://youtube.com/watch?v=xxx")
# Returns: False
```

---

#### Function: `extract_video_id`

```python
def extract_video_id(url: str) -> Optional[str]
```

Extract video ID from URL.

**Parameters**:
- `url` (str): Video URL

**Returns**:
- `Optional[str]`: Video ID or None

**Example**:
```python
from utils import extract_video_id

video_id = extract_video_id("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
# Returns: 'dQw4w9WgXcQ'

video_id = extract_video_id("https://youtu.be/dQw4w9WgXcQ")
# Returns: 'dQw4w9WgXcQ'
```

---

#### Function: `validate_url`

```python
def validate_url(url: str) -> bool
```

Validate URL format.

**Parameters**:
- `url` (str): URL to validate

**Returns**:
- `bool`: True if valid URL

**Example**:
```python
from utils import validate_url

is_valid = validate_url("https://example.com/video")
# Returns: True

is_valid = validate_url("not a url")
# Returns: False
```

---

### Configuration Functions

#### Function: `load_config`

```python
def load_config(config_path: str = 'config.json') -> dict
```

Load configuration from JSON file.

**Parameters**:
- `config_path` (str, optional): Config file path. Default: 'config.json'

**Returns**:
- `dict`: Configuration dictionary

**Example**:
```python
from utils import load_config

config = load_config('config.json')
output_dir = config['download']['output_dir']
```

---

#### Function: `save_config`

```python
def save_config(config: dict, config_path: str = 'config.json') -> bool
```

Save configuration to JSON file.

**Parameters**:
- `config` (dict): Configuration dictionary
- `config_path` (str, optional): Config file path. Default: 'config.json'

**Returns**:
- `bool`: Success status

**Example**:
```python
from utils import save_config

config = {
    'download': {
        'output_dir': '~/Music',
        'quality': '1080'
    }
}
save_config(config)
```

---

## Usage Examples

### Example 1: Simple Video Download

```python
from ultimate_downloader import UltimateMediaDownloader

# Initialize downloader
downloader = UltimateMediaDownloader(output_dir="downloads")

# Download video
success = downloader.download("https://www.youtube.com/watch?v=dQw4w9WgXcQ")

if success:
    print("Download completed!")
```

---

### Example 2: Audio Extraction with Metadata

```python
from ultimate_downloader import UltimateMediaDownloader

downloader = UltimateMediaDownloader()

# Download audio with metadata
success = downloader.download(
    "https://www.youtube.com/watch?v=xxx",
    audio_only=True,
    audio_format='mp3',
    audio_quality='320',
    embed_thumbnail=True,
    embed_metadata=True
)
```

---

### Example 3: Spotify Track Download

```python
from ultimate_downloader import UltimateMediaDownloader

downloader = UltimateMediaDownloader()

# Download Spotify track (searches YouTube and embeds metadata)
success = downloader.search_and_download_spotify_track(
    "https://open.spotify.com/track/6rqhFgbbKwnb9MLmUQDhG6"
)
```

---

### Example 4: Playlist Download

```python
from ultimate_downloader import UltimateMediaDownloader

downloader = UltimateMediaDownloader()

# Download entire playlist
success = downloader.download(
    "https://www.youtube.com/playlist?list=PLxxxxxx",
    playlist=True,
    audio_only=True,
    audio_format='mp3'
)
```

---

### Example 5: Generic Site Download

```python
from pathlib import Path
from generic_downloader import GenericSiteDownloader

# Initialize generic downloader
downloader = GenericSiteDownloader(
    output_dir=Path("downloads"),
    verbose=True
)

# Download from any site
file_path = downloader.download("https://example.com/video.mp4")

if file_path:
    print(f"Downloaded: {file_path}")
```

---

### Example 6: Custom UI with Progress

```python
from ui_components import ModernUI
from ultimate_downloader import UltimateMediaDownloader
import time

ui = ModernUI()
downloader = UltimateMediaDownloader()

# Display banner
ui.print_banner("My Downloader", "v1.0")

# Create progress bar
progress = ui.create_progress()

with progress:
    task = progress.add_task("Downloading...", total=100)
    
    # Simulate download
    for i in range(100):
        progress.update(task, advance=1)
        time.sleep(0.05)

ui.print_panel("Download complete!", title="Success", style="green")
```

---

### Example 7: Using Utilities

```python
from utils import (
    sanitize_filename,
    format_bytes,
    format_duration,
    detect_platform,
    is_playlist_url
)

# Sanitize filename
safe_name = sanitize_filename("My Song: Amazing! <2024>")

# Format file size
size = format_bytes(10485760)  # "10.00 MB"

# Format duration
duration = format_duration(245)  # "4:05"

# Detect platform
platform = detect_platform("https://spotify.com/track/xxx")  # 'spotify'

# Check if playlist
is_pl = is_playlist_url("https://youtube.com/playlist?list=xxx")  # True
```

---

### Example 8: Custom Logging

```python
from logger import QuietLogger
import yt_dlp

logger = QuietLogger()

ydl_opts = {
    'logger': logger,
    'quiet': False,
    'no_warnings': False
}

with yt_dlp.YoutubeDL(ydl_opts) as ydl:
    ydl.download(['https://www.youtube.com/watch?v=xxx'])
```

---

## Type Hints Reference

### Common Types

```python
from typing import Optional, List, Dict, Any, Union
from pathlib import Path

# Download options
DownloadOptions = Dict[str, Union[str, bool, int]]

# Metadata
Metadata = Dict[str, Union[str, int, List[str]]]

# Track info
TrackInfo = Dict[str, Any]

# Result
Result = Optional[str]  # File path or None
```

---

## Error Handling

All methods handle errors gracefully and return appropriate values:

- **Success**: Returns `True`, file path, or expected value
- **Failure**: Returns `False`, `None`, or empty value
- **Exceptions**: Caught internally, logged, and converted to return values

### Example Error Handling

```python
from ultimate_downloader import UltimateMediaDownloader

downloader = UltimateMediaDownloader()

try:
    success = downloader.download("https://invalid-url.com")
    if not success:
        print("Download failed - check URL and try again")
except Exception as e:
    print(f"Unexpected error: {e}")
```

---

## Configuration Reference

### yt-dlp Options

Common yt-dlp options used in `default_ydl_opts`:

```python
{
    'format': 'bestvideo+bestaudio/best',
    'outtmpl': '%(title)s.%(ext)s',
    'quiet': False,
    'no_warnings': False,
    'extract_audio': False,
    'audio_format': 'mp3',
    'audio_quality': '320K',
    'embed_thumbnail': True,
    'add_metadata': True,
    'concurrent_fragments': 8,
    'retries': 10,
    'fragment_retries': 10
}
```

---

## Platform-Specific Notes

### YouTube
- Supports videos, playlists, channels, live streams
- Age-restricted content requires authentication
- Subtitles available in multiple languages

### Spotify
- Requires web scraping or API credentials
- Downloads via YouTube search fallback
- Preserves high-quality album art and metadata

### SoundCloud
- Direct download support via yt-dlp
- Preserves original quality
- Supports Go+ premium tracks (with auth)

### Instagram
- Requires authentication for private content
- Supports photos, videos, reels, IGTV
- Stories require quick access

---

## Performance Tips

1. **Use concurrent downloads**: Set `concurrent_fragments` in yt-dlp options
2. **Cache enabled**: Speeds up repeated operations
3. **Quality selection**: Lower quality = faster downloads
4. **Proxy rotation**: Distribute load across multiple proxies
5. **Resume support**: Automatically resumes interrupted downloads

---

## Best Practices

1. **Always validate URLs** before downloading
2. **Handle errors gracefully** with try-except
3. **Use sanitize_filename** for all user-provided names
4. **Check available disk space** before large downloads
5. **Respect rate limits** and robots.txt
6. **Use appropriate quality** based on use case
7. **Clean up temporary files** after operations

---

**Last Updated**: October 3, 2025  
**Maintainer**: Nitish Kumar  
**Repository**: [GitHub](https://github.com/NK2552003/ULTIMATE-MEDIA-DOWNLOADER)
