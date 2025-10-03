# Project Structure - Ultimate Media Downloader

**Version**: 2.0.0  
**Last Updated**: October 3, 2025  
**Repository**: [ULTIMATE-MEDIA-DOWNLOADER](https://github.com/NK2552003/ULTIMATE-MEDIA-DOWNLOADER)

This document provides a comprehensive overview of the project structure, file organization, and module descriptions based on the actual codebase.

---

## 📑 Table of Contents

1. [Directory Tree](#directory-tree)
2. [Core Python Modules](#core-python-modules)
3. [Configuration Files](#configuration-files)
4. [Documentation](#documentation)
5. [Scripts & Utilities](#scripts--utilities)
6. [Dependencies](#dependencies)

---

## Directory Tree

```
ULTIMATE-MEDIA-DOWNLOADER/
├── 📄 README.md                    # Main project documentation (728 lines)
├── 📄 LICENSE                      # MIT License
├── 📄 CHANGELOG.md                 # Version history and changes
├── 📄 CONTRIBUTING.md              # Contribution guidelines
├── 📄 QUICK_REFERENCE.md           # Quick command reference
├── 📄 .gitignore                   # Git ignore patterns
│
├── � requirements.txt             # Production dependencies (79 lines)
├── � requirements-dev.txt         # Development dependencies
├── ⚙️  config.json                  # Application configuration (77 lines)
│
├── 🔧 setup.sh                     # Automated setup script
├── 🔧 activate-env.sh              # Virtual environment activation
│
├── 🐍 ultimate_downloader.py       # Main application entry point (6,324 lines)
├── 🐍 generic_downloader.py        # Generic site handler (1,219 lines)
├── 🐍 logger.py                    # Custom logging module (58 lines)
├── 🐍 ui_components.py             # UI components & styling (280 lines)
├── 🐍 utils.py                     # Utility functions (314 lines)
│
├── 📁 docs/                        # Documentation directory
│   ├── 📄 INDEX.md                 # Documentation index
│   ├── 📄 ARCHITECTURE.md          # System architecture design
│   ├── 📄 PROJECT_STRUCTURE.md     # This file
│   ├── 📄 USER_GUIDE.md            # Comprehensive user manual
│   ├── 📄 API_REFERENCE.md         # API documentation
│   ├── 📄 FLOWCHARTS.md            # Process flow diagrams
│   └── 📄 HOW_IT_WAS_CREATED.md    # Development history
│
├── 📁 downloads/                   # Default download directory
├── 📁 __pycache__/                 # Python bytecode cache
│   ├── generic_downloader.cpython-313.pyc
│   ├── logger.cpython-313.pyc
│   ├── ui_components.cpython-313.pyc
│   ├── ultimate_downloader.cpython-313.pyc
│   └── utils.cpython-313.pyc
│
├── 📁 venv/                        # Virtual environment (created by setup)
└── 📁 .cache/                      # yt-dlp cache directory (runtime)
```

---

## Core Python Modules

### 🐍 ultimate_downloader.py (6,324 lines)

**Purpose**: Main application module - orchestrates all download operations

**Key Components**:

#### Class: `UltimateMediaDownloader`
Main downloader class handling all platforms and operations.

**Key Methods**:
- `__init__(output_dir)` - Initialize downloader
- `download(url, **options)` - Main download method
- `download_youtube(url, options)` - YouTube-specific handler
- `download_spotify(url, options)` - Spotify handler with YouTube fallback
- `download_soundcloud(url, options)` - SoundCloud handler
- `download_generic(url, options)` - Generic site handler
- `download_playlist(url, options)` - Playlist/album downloader
- `search_and_download(query, platform)` - Search and download
- `_embed_metadata(file_path, metadata)` - Embed ID3 tags
- `_embed_thumbnail(file_path, thumbnail_url)` - Embed album art
- `_extract_spotify_track_info(url)` - Scrape Spotify metadata
- `_download_spotify_track(url)` - Spotify track downloader
- `_download_spotify_album(url)` - Spotify album downloader
- `_download_spotify_playlist(url)` - Spotify playlist downloader
- `_fallback_spotify_search(url)` - Fallback search mechanism
- `detect_platform(url)` - Auto-detect platform from URL
- `get_supported_sites()` - List all supported platforms

**Functions**:
- `interactive_mode()` - CLI interactive interface
- `show_help_menu(ui)` - Display help menu
- `create_banner()` - Generate ASCII art banner
- `main()` - Application entry point

**Dependencies**:
- `yt_dlp` - Core download engine
- `spotipy` - Spotify API client
- `mutagen` - Audio metadata handling
- `requests` - HTTP operations
- `rich` - Beautiful CLI interface

---

### � generic_downloader.py (1,219 lines)

**Purpose**: Advanced generic website downloader with multiple fallback methods

**Key Components**:

#### Class: `GenericSiteDownloader`
Handles downloads from websites not directly supported by yt-dlp.

**Key Methods**:
- `__init__(output_dir, verbose, proxies)` - Initialize downloader
- `download(url, output_filename)` - Main download orchestrator
- `_download_with_ytdlp(url, filename)` - Try yt-dlp first
- `_download_with_system_curl(url, filename)` - Use system curl command
- `_download_with_curl_cffi(url, filename)` - Use curl-cffi library
- `_download_with_cloudscraper(url, filename)` - Cloudflare bypass
- `_download_with_streamlink(url, filename)` - Stream extraction
- `_download_with_httpx(url, filename)` - Modern HTTP client
- `_download_with_selenium(url, filename)` - Browser automation
- `_download_with_playwright(url, filename)` - Playwright automation
- `_download_with_requests_html(url, filename)` - HTML with JS
- `_download_with_advanced_scraping(url, filename)` - Advanced scraping
- `_extract_video_url_from_html(html, base_url)` - Find video URLs
- `_download_direct_video(url, filename)` - Direct video download
- `_create_permissive_ssl_context()` - SSL/TLS handling
- `_get_random_headers()` - Random user agent rotation
- `_get_proxy()` - Proxy rotation

**Features**:
- Multiple fallback mechanisms (10+ methods)
- SSL/TLS issue handling
- Cloudflare bypass
- Anti-bot protection evasion
- Proxy rotation
- User agent randomization
- Browser automation (Selenium & Playwright)

---

### 🐍 logger.py (58 lines)

**Purpose**: Custom logging module for clean terminal output

**Key Components**:

#### Class: `QuietLogger`
Suppresses verbose yt-dlp output while showing important messages.

**Methods**:
- `debug(msg)` - Suppress debug messages
- `info(msg)` - Show selective info messages
- `warning(msg)` - Display warnings with formatting
- `error(msg)` - Display errors with formatting

**Features**:
- Rich formatting integration
- Selective message filtering
- Clean progress display
- Error highlighting

---

### 🐍 ui_components.py (280 lines)

**Purpose**: Modern UI components and styling for CLI interface

**Key Components**:

#### Class: `Icons`
Modern flat design icon system.

**Methods**:
- `get(name)` - Get icon by name

**Available Icons**:
- Status: ✓ ✗ ⚠ ℹ →
- Media: ▶ ♫ ♪ ≡ ↓ ▸
- Platforms: ▶ ♪ ☁ ◉
- Progress: ⟳ ⚙ ✓ ✗
- Quality: ⚡ ★ ▭

#### Class: `Messages`
Centralized message templates with Rich formatting.

**Methods**:
- `success(text)` - Success message (green)
- `error(text)` - Error message (red)
- `warning(text)` - Warning message (yellow)
- `info(text)` - Info message (cyan)
- `tip(text)` - Tip message (magenta)
- `downloading(text)` - Download message (blue)

#### Class: `ModernUI`
Complete UI system with panels, progress bars, and tables.

**Methods**:
- `__init__()` - Initialize UI system
- `print_banner(title, subtitle)` - Display banner
- `print_panel(content, title, style)` - Display panel
- `print_table(title, headers, rows)` - Display table
- `print_section_header(title)` - Section header
- `create_progress()` - Create progress bar
- `prompt(question, choices)` - Interactive prompt
- `confirm(question, default)` - Confirmation dialog
- `show_stats(data)` - Display statistics

**Features**:
- Pyfiglet ASCII art integration
- Rich panels and tables
- Animated progress bars
- Interactive prompts
- Color-coded messages

---

### 🐍 utils.py (314 lines)

**Purpose**: Utility functions used across the application

**Key Functions**:

#### File Operations
- `sanitize_filename(filename)` - Make filename safe for filesystem
- `ensure_directory(path)` - Create directory if not exists
- `get_file_size(filepath)` - Get file size in bytes
- `delete_file(filepath)` - Safely delete file

#### Formatting
- `format_bytes(bytes_value)` - Convert bytes to human-readable (e.g., "10.5 MB")
- `format_duration(seconds)` - Convert seconds to time format (e.g., "1:23:45")
- `format_bitrate(bitrate)` - Format bitrate (e.g., "320 kbps")
- `truncate_string(text, length)` - Truncate with ellipsis
- `clean_string(text)` - Remove special characters

#### URL Analysis
- `detect_platform(url)` - Detect platform from URL
- `is_playlist_url(url)` - Check if URL is a playlist
- `extract_video_id(url)` - Extract video ID from URL
- `validate_url(url)` - Validate URL format
- `normalize_url(url)` - Normalize URL format

#### Configuration
- `load_config(config_path)` - Load JSON configuration
- `save_config(config, config_path)` - Save configuration
- `merge_configs(default, user)` - Merge configuration dictionaries
- `validate_config(config)` - Validate configuration structure

#### Data Processing
- `parse_quality(quality_str)` - Parse quality string
- `parse_duration(duration_str)` - Parse duration string
- `extract_metadata(data)` - Extract metadata from response
- `sanitize_metadata(metadata)` - Clean metadata for embedding

**Supported Platforms Detection**:
- YouTube, Spotify, SoundCloud
- Apple Music, Instagram, TikTok
- Twitter/X, Facebook, Vimeo
- Dailymotion, Twitch, and more

---

## Configuration Files

### ⚙️ config.json (77 lines)

**Purpose**: Application-wide configuration settings

**Structure**:

```json
{
  "spotify": {
    "client_id": "",
    "client_secret": "",
    "enabled": false
  },
  "apple_music": {
    "enabled": false,
    "cookie_file": "",
    "media_user_token": ""
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
    "https": "",
    "socks5": ""
  },
  "authentication": {
    "youtube": { "cookies_file": "" },
    "instagram": { "username": "", "password": "" },
    "facebook": { "cookies_file": "" }
  },
  "advanced": {
    "concurrent_downloads": 3,
    "retry_attempts": 3,
    "timeout": 300,
    "rate_limit": null,
    "user_agent": "Mozilla/5.0...",
    "cookies_file": "",
    "archive_file": "archive.txt"
  }
}
```

**Configuration Sections**:
1. **Spotify** - Spotify API credentials
2. **Apple Music** - Apple Music authentication
3. **Download** - Default download settings
4. **Proxy** - Proxy server configuration
5. **Authentication** - Platform-specific auth
6. **Advanced** - Advanced options

---

## Documentation

### 📁 docs/ Directory

#### 📄 INDEX.md
**Purpose**: Documentation navigation hub  
**Contents**: Links to all documentation with descriptions

#### 📄 ARCHITECTURE.md
**Purpose**: System architecture documentation  
**Contents**:
- Architecture layers and patterns
- Component diagrams
- Data flow diagrams
- Design decisions
- Module interactions

#### 📄 PROJECT_STRUCTURE.md
**Purpose**: This file - project organization  
**Contents**:
- Directory tree
- File descriptions
- Module documentation
- Dependencies mapping

#### 📄 USER_GUIDE.md
**Purpose**: Comprehensive user manual  
**Contents**:
- Installation guide
- Usage examples
- Command-line options
- Platform-specific guides
- Configuration guide
- Tips & tricks
- FAQ

#### 📄 API_REFERENCE.md
**Purpose**: API documentation  
**Contents**:
- Class definitions
- Method signatures
- Parameters & return values
- Usage examples
- Code samples

#### 📄 FLOWCHARTS.md
**Purpose**: Process flow diagrams  
**Contents**:
- Download flow
- Platform detection flow
- Error handling flow
- Metadata embedding flow

#### 📄 HOW_IT_WAS_CREATED.md
**Purpose**: Development journey  
**Contents**:
- Project evolution
- Technical decisions
- Challenges faced
- Solutions implemented

---

## Scripts & Utilities

### 🔧 setup.sh

**Purpose**: Automated environment setup script

**Operations**:
1. Check Python version (3.9+)
2. Create virtual environment
3. Activate environment
4. Install dependencies
5. Verify installations
6. Create necessary directories
7. Display setup summary

**Usage**:
```bash
bash setup.sh
```

---

### 🔧 activate-env.sh

**Purpose**: Virtual environment activation with banner

**Operations**:
1. Check if venv exists
2. Activate virtual environment
3. Display welcome banner
4. Show quick commands

**Usage**:
```bash
source activate-env.sh
```

---

## Dependencies

### 📦 requirements.txt (79 lines)

**Categories**:

#### Core Video/Audio Downloading
- `yt-dlp>=2025.09.26` - Main download engine (1000+ sites)
- `requests>=2.32.5` - HTTP library

#### Rich CLI Interface
- `rich>=13.9.4,<14` - Terminal formatting
- `colorama>=0.4.6` - Cross-platform colors
- `pyfiglet>=1.0.2` - ASCII art
- `emoji>=2.9.0` - Emoji support
- `halo>=0.0.31` - Terminal spinners

#### Audio/Video Processing
- `mutagen>=1.47.0` - Audio metadata editing
- `Pillow>=11.2.1` - Image processing

#### Music Platform Support
- `spotipy>=2.25.1` - Spotify API
- `youtube-search-python>=1.6.6` - YouTube search
- `spotdl>=4.4.2` - Spotify downloader

#### Advanced Web Scraping
- `cloudscraper>=1.2.71` - Cloudflare bypass
- `httpx>=0.25.2` - Modern HTTP client
- `curl-cffi>=0.6.2` - curl bindings
- `fake-useragent>=1.4.0` - User agent rotation
- `requests-html>=0.10.0` - HTML with JS
- `beautifulsoup4>=4.12.2` - HTML parser
- `lxml>=4.9.3` - XML/HTML parser

#### Browser Automation
- `selenium>=4.16.0` - Browser automation
- `undetected-chromedriver>=3.5.4` - Undetected Chrome
- `webdriver-manager>=4.0.1` - Webdriver management
- `playwright>=1.40.0` - Modern automation

#### Stream Extraction
- `streamlink>=6.5.0` - Stream extraction

#### Utilities
- `python-dateutil>=2.8.2` - Date/time utilities
- `pytz>=2023.3` - Timezone support

---

### � requirements-dev.txt

**Development Dependencies**:
- `pytest>=7.4.3` - Testing framework
- `black>=23.12.0` - Code formatter
- `flake8>=6.1.0` - Linting
- `mypy>=1.7.1` - Static type checking

---

## File Size Summary

| File | Lines | Size | Purpose |
|------|-------|------|---------|
| ultimate_downloader.py | 6,324 | ~250 KB | Main application |
| generic_downloader.py | 1,219 | ~55 KB | Generic handler |
| ui_components.py | 280 | ~12 KB | UI components |
| utils.py | 314 | ~14 KB | Utilities |
| logger.py | 58 | ~2 KB | Logging |
| requirements.txt | 79 | ~3 KB | Dependencies |
| config.json | 77 | ~2 KB | Configuration |
| README.md | 728 | ~35 KB | Documentation |

**Total Code**: ~8,000 lines of Python  
**Documentation**: ~3,000+ lines across all docs

---

## Module Dependencies Graph

```
ultimate_downloader.py
    ├── logger.py (QuietLogger)
    ├── ui_components.py (Icons, Messages, ModernUI)
    ├── utils.py (all utility functions)
    ├── generic_downloader.py (GenericSiteDownloader)
    ├── yt_dlp (external)
    ├── spotipy (external)
    ├── mutagen (external)
    ├── rich (external)
    └── requests (external)

generic_downloader.py
    ├── requests (external)
    ├── beautifulsoup4 (external)
    ├── selenium (external)
    ├── playwright (external)
    ├── cloudscraper (external)
    └── streamlink (external)

ui_components.py
    ├── rich (external)
    ├── pyfiglet (external)
    └── halo (external)

logger.py
    └── rich (external)

utils.py
    ├── pathlib (stdlib)
    ├── urllib.parse (stdlib)
    └── json (stdlib)
```

---

## Runtime Directories

### 📁 downloads/
**Purpose**: Default download output directory  
**Created**: At first run  
**Contains**: Downloaded media files

### 📁 __pycache__/
**Purpose**: Python bytecode cache  
**Created**: Automatically by Python  
**Contains**: .pyc compiled files

### 📁 .cache/
**Purpose**: yt-dlp cache directory  
**Created**: At runtime by yt-dlp  
**Contains**: Download cache and fragments

### 📁 venv/
**Purpose**: Python virtual environment  
**Created**: By setup.sh  
**Contains**: Isolated Python packages

---

## Notes

- All Python files use UTF-8 encoding
- Python 3.9+ required for compatibility
- Cross-platform support: Linux, macOS, Windows
- Modular design allows easy extension
- Type hints used where applicable
- PEP 8 compliant code style

---

**Last Updated**: October 3, 2025  
**Maintainer**: Nitish Kumar  
**Repository**: [GitHub](https://github.com/NK2552003/ULTIMATE-MEDIA-DOWNLOADER)
- Optional dependencies
- Commented explanations

**Usage**: `pip install -r requirements.txt`

#### 📄 requirements-dev.txt (30+ lines)
**Purpose**: Development dependencies  
**Contents**:
- Testing frameworks
- Code quality tools
- Documentation generators
- Build tools

**Usage**: `pip install -r requirements-dev.txt`

#### 📄 config.json (80+ lines)
**Purpose**: Application configuration  
**Format**: JSON
**Sections**:
- Platform credentials (Spotify, Apple Music)
- Download settings
- Proxy configuration
- Advanced options
- UI preferences
- Post-processing settings

**Security**: Don't commit with real credentials

### Scripts

#### 🔧 setup.sh (500+ lines)
**Purpose**: Automated installation  
**Features**:
- OS detection
- Dependency installation
- Virtual environment creation
- Configuration setup
- Testing
- Beautiful colored output

**Platforms**: Linux, macOS, Windows (Git Bash)

**Usage**:
```bash
chmod +x setup.sh
./setup.sh
```

#### 🔧 activate-env.sh (100+ lines)
**Purpose**: Environment activation  
**Features**:
- Virtual environment activation
- Status display
- Usage hints
- Custom prompt

**Usage**:
```bash
source activate-env.sh
```

### Core Python Files

#### 🐍 ultimate_downloader.py (6,400+ lines)
**Purpose**: Main application logic  
**Key Components**:

1. **Classes**:
   - `UltimateDownloader` - Main application class

2. **Handlers**:
   - YouTube handler
   - Spotify handler
   - Instagram handler
   - TikTok handler
   - SoundCloud handler
   - Twitter handler
   - And more...

3. **Features**:
   - URL parsing and validation
   - Platform detection
   - Download management
   - Progress tracking
   - Error handling
   - Configuration management

**Structure**:
```python
# Imports (lines 1-120) - Now imports from modular components
# Main downloader class (lines 121-6000)
# CLI interface (lines 6001-6400+)
```

**Note**: UI components, logging, and utilities have been extracted to separate modules.

#### 🐍 generic_downloader.py (1,219 lines)
**Purpose**: Universal site handler  
**Key Components**:

1. **Class**: `GenericSiteDownloader`
2. **Methods**:
   - Multiple fallback download methods
   - SSL/TLS bypass
   - User agent rotation
   - Proxy support
   - Video URL extraction

3. **Supported Methods**:
   - yt-dlp (primary)
   - requests (HTTP)
   - Selenium (browser)
   - Playwright (advanced browser)
   - Streamlink (streams)

**Use Cases**:
- Sites not explicitly supported
- Complex JavaScript sites
- Protected content
- Stream extraction

---

## Reusable Component Modules (NEW)

### 🐍 logger.py (~60 lines)
**Purpose**: Custom logging functionality  
**Key Components**:

1. **Class**: `QuietLogger`
   - Custom logger for yt-dlp integration
   - Suppresses verbose output
   - Shows important messages only
   - Rich formatting support

**Usage**:
```python
from logger import QuietLogger
logger = QuietLogger()
logger.info("Download started")
logger.warning("Quality limited")
logger.error("Download failed")
```

### 🐍 ui_components.py (~300 lines)
**Purpose**: Professional UI elements  
**Key Components**:

1. **Class**: `Icons`
   - 40+ modern flat design icons
   - Platform icons (YouTube, Spotify, etc.)
   - Status icons (success, error, warning)
   - Media icons (video, audio, playlist)

2. **Class**: `Messages`
   - Centralized message templates
   - Rich formatting support
   - Consistent styling
   - 9 message types

3. **Class**: `ModernUI`
   - Welcome banners
   - Progress bars
   - Spinners
   - Input prompts
   - Status messages
   - ASCII art logos

**Usage**:
```python
from ui_components import Icons, Messages, ModernUI

# Get icons
icon = Icons.get('success')

# Format messages
msg = Messages.success("Download complete!")

# Create UI
ui = ModernUI()
ui.show_welcome_banner()
```

### 🐍 utils.py (~250 lines)
**Purpose**: Common utility functions  
**Key Functions**:

1. **File Operations**:
   - `sanitize_filename()` - Clean filenames
   - `ensure_directory()` - Create directories
   - `get_file_extension()` - Extract extensions

2. **Formatting**:
   - `format_bytes()` - Human-readable sizes
   - `format_duration()` - Time formatting
   - `truncate_string()` - String truncation

3. **URL Detection**:
   - `detect_platform()` - Platform identification
   - `is_playlist_url()` - Playlist detection
   - `extract_video_id()` - ID extraction
   - `validate_url()` - URL validation

4. **Configuration**:
   - `load_config()` - Load JSON config
   - `save_config()` - Save JSON config

5. **String Processing**:
   - `clean_string()` - Remove extra whitespace

**Usage**:
```python
from utils import (
    sanitize_filename, 
    format_bytes, 
    detect_platform
)

# Clean filename
safe_name = sanitize_filename("My Video: Part 1")

# Format size
size = format_bytes(1048576)  # "1.00 MB"

# Detect platform
platform = detect_platform(url)  # "youtube"
```

### 🐍 example_components_usage.py (~350 lines)
**Purpose**: Component usage examples  
**Contents**:
- Logger examples
- Icon examples
- Message examples
- UI examples
- Utility function examples
- Complete workflow example

**Usage**:
```bash
python3 example_components_usage.py
```

**Features**:
- Demonstrates all components
- Shows best practices
- Provides working code examples
- Educational resource

---

## Documentation Directory

### 📁 docs/

#### 📄 ARCHITECTURE.md (800+ lines)
**Purpose**: System design documentation  
**Contents**:
- Architecture overview
- Design patterns used
- Component descriptions
- Data flow diagrams
- Technology decisions
- Scalability considerations
- Security architecture

**Audience**: Developers, contributors

#### 📄 FLOWCHARTS.md (600+ lines)
**Purpose**: Visual process documentation  
**Contents**:
- 8+ detailed flowcharts using Mermaid
- Main application flow
- Download process flow
- Platform detection flow
- Authentication flow
- Post-processing flow
- Error handling flow
- Playlist processing flow
- Configuration flow

**Format**: Mermaid syntax (renders on GitHub)

#### 📄 USER_GUIDE.md (700+ lines)
**Purpose**: Comprehensive user manual  
**Contents**:
- Getting started guide
- Basic usage examples
- Advanced features
- Platform-specific guides
- Configuration instructions
- Tips and tricks
- FAQ

**Audience**: End users

#### 📄 CONTRIBUTING.md (500+ lines)
**Purpose**: Contribution guidelines  
**Contents**:
- Code of conduct
- How to contribute
- Development setup
- Coding standards
- Commit guidelines
- Pull request process
- Testing guidelines

**Audience**: Contributors

#### 📄 HOW_IT_WAS_CREATED.md (600+ lines)
**Purpose**: Development journey  
**Contents**:
- Project inception
- Development timeline
- Technical decisions
- Challenges faced
- Tools used
- Lessons learned
- Future vision

**Audience**: Developers, interested users

#### 📄 PROJECT_STRUCTURE.md (This file)
**Purpose**: Repository organization  
**Contents**:
- Directory tree
- File descriptions
- Purpose of each component
- Usage guidelines

**Audience**: Developers, contributors

---

## Runtime Directories

### 📁 downloads/ (Created by setup)
**Purpose**: Default download location  
**Contents**: Downloaded media files  
**Structure**:
```
downloads/
├── YouTube/
├── Spotify/
├── Instagram/
└── ...
```
**Configurable**: Yes, via config.json

### 📁 venv/ (Created by setup)
**Purpose**: Python virtual environment  
**Contents**:
- Python interpreter
- Installed packages
- Scripts and binaries

**Size**: ~100-500 MB  
**Should commit?**: No (in .gitignore)

### 📁 .cache/ (Created at runtime)
**Purpose**: Application cache  
**Contents**:
- API responses
- Metadata cache
- Temporary files

**Should commit?**: No (in .gitignore)

---

## File Statistics

### Code Files

| File | Lines | Type | Purpose |
|------|-------|------|---------|
| ultimate_downloader.py | 6,454 | Python | Main application |
| generic_downloader.py | 1,219 | Python | Generic handler |
| setup.sh | 500+ | Bash | Setup script |
| activate-env.sh | 100+ | Bash | Activation script |

### Documentation Files

| File | Lines | Type | Purpose |
|------|-------|------|---------|
| README.md | 1,000+ | Markdown | Main docs |
| ARCHITECTURE.md | 800+ | Markdown | Design docs |
| USER_GUIDE.md | 700+ | Markdown | User manual |
| FLOWCHARTS.md | 600+ | Markdown | Flowcharts |
| HOW_IT_WAS_CREATED.md | 600+ | Markdown | Dev journey |
| CONTRIBUTING.md | 500+ | Markdown | Guidelines |
| CHANGELOG.md | 200+ | Markdown | Version history |
| PROJECT_STRUCTURE.md | 400+ | Markdown | This file |

### Configuration Files

| File | Lines | Type | Purpose |
|------|-------|------|---------|
| config.json | 80+ | JSON | Configuration |
| requirements.txt | 50+ | Text | Dependencies |
| requirements-dev.txt | 30+ | Text | Dev dependencies |
| .gitignore | 100+ | Text | Git exclusions |

### Total Statistics

```
Total Files: 20+
Total Lines: 12,000+
Code: 8,000+ lines
Documentation: 4,000+ lines
Total Size: ~500 KB (excluding dependencies)
```

---

## Dependencies Structure

### Core Dependencies
```
yt-dlp (download engine)
├── requests
├── urllib3
└── certifi

requests (HTTP)
└── urllib3

rich (UI)
├── colorama
└── pygments

mutagen (metadata)
└── (standalone)
```

### Optional Dependencies
```
spotipy (Spotify)
├── requests
└── urllib3

selenium (browser)
└── urllib3

playwright (browser)
└── greenlet
```

---

## Build & Deployment Structure

### Development Build
```
Source Code
├── Python files
├── Documentation
└── Configuration

Virtual Environment
├── Python interpreter
└── Dependencies

Output
└── downloads/
```

### Distribution Build
```
Release Package
├── Source code (tar.gz)
├── Documentation
├── Setup scripts
└── Requirements
```

---

## Git Repository Structure

### Branches
- `main` - Stable releases
- `develop` - Active development
- `feature/*` - Feature branches
- `hotfix/*` - Urgent fixes

### Tags
- `v2.0.0` - Major release
- `v2.0.1` - Patch release
- `v2.1.0` - Minor release

### Commits
Format: `type(scope): description`
- `feat:` - New features
- `fix:` - Bug fixes
- `docs:` - Documentation
- `style:` - Code style
- `refactor:` - Code refactoring
- `test:` - Tests
- `chore:` - Maintenance

---

## Module Import Structure

```python
# Main application
ultimate_downloader
├── QuietLogger
├── Icons
├── Messages
├── ModernUI
└── UltimateDownloader

# Generic handler
generic_downloader
└── GenericSiteDownloader

# External
├── yt_dlp
├── requests
├── rich
├── mutagen
└── ...
```

---

## Configuration Hierarchy

```
1. Default Values (in code)
   ↓
2. config.json (file)
   ↓
3. Environment Variables
   ↓
4. Command Line Arguments (highest priority)
```

---

## Data Flow Structure

```
User Input
    ↓
CLI Parser
    ↓
Configuration Loader
    ↓
Platform Detector
    ↓
Handler Selection
    ↓
Download Process
    ↓
Post-Processing
    ↓
File Output
```

---

## Best Practices

### Adding New Files

1. **Code Files**: Add to root or create appropriate subdirectory
2. **Documentation**: Add to `docs/` directory
3. **Tests**: Add to `tests/` directory (when created)
4. **Update**: Add to this document
5. **Git**: Update `.gitignore` if needed

### Naming Conventions

- **Python files**: `lowercase_with_underscores.py`
- **Documentation**: `UPPERCASE_WITH_UNDERSCORES.md`
- **Scripts**: `lowercase-with-hyphens.sh`
- **Directories**: `lowercase/`

### File Organization

- Keep root directory clean
- Group related files in subdirectories
- Use clear, descriptive names
- Add README.md to new directories

---

## Maintenance

### Regular Updates

- **Dependencies**: Monthly security updates
- **Documentation**: Update with each feature
- **CHANGELOG**: Update with each version
- **README**: Keep examples current

### Cleanup Tasks

- Remove old cache files
- Update outdated documentation
- Archive old branches
- Clean up test files

---

## Future Structure (Planned)

```
ULTIMATE-MEDIA-DOWNLOADER/
├── src/                    # Source code
│   ├── core/
│   ├── handlers/
│   ├── processors/
│   └── utils/
├── tests/                  # Test suite
│   ├── unit/
│   └── integration/
├── docs/                   # Documentation
├── scripts/                # Build scripts
├── examples/               # Usage examples
└── assets/                 # Media assets
```

---

**Last Updated**: October 2, 2025  
**Version**: 2.0.0  
**Maintainer**: Nitish Kumar (NK2552003)
