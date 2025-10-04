<div align="center">
<h1>Ultimate Media Downloader</h1>
</div>
<div align="center">

[![Python Version](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-Linux%20%7C%20macOS%20%7C%20Windows-lightgrey.svg)](https://github.com/NK2552003/ULTIMATE-MEDIA-DOWNLOADER)
[![Maintained](https://img.shields.io/badge/maintained-yes-brightgreen.svg)](https://github.com/NK2552003/ULTIMATE-MEDIA-DOWNLOADER/commits/main)
[![Last Updated](https://img.shields.io/badge/updated-October%202025-blue.svg)](https://github.com/NK2552003/ULTIMATE-MEDIA-DOWNLOADER)
[![Documentation](https://img.shields.io/badge/docs-comprehensive-brightgreen.svg)](docs/INDEX.md)

**A powerful, feature-rich media downloader supporting 1000+ platforms**

**Version 2.0.0** | [Documentation](docs/INDEX.md) • [Installation](#installation) • [Quick Start](#quick-start) • [Contributing](CONTRIBUTING.md)

</div>

---

## Demo

<div align="center">

https://github.com/NK2552003/ULTIMATE-MEDIA-DOWNLOADER/blob/main/demo_video/demo.mp4

*Watch the Ultimate Media Downloader in action*

</div>

---

## Table of Contents

- [Demo](#demo)
- [Overview](#overview)
- [Features](#features)
- [Supported Platforms](#supported-platforms)
- [System Requirements](#system-requirements)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Documentation](#documentation)
- [Contributing](#contributing)
- [License](#license)
- [Disclaimer](#disclaimer)

---

## Overview

**Ultimate Media Downloader** is a professional-grade, open-source media downloading tool that supports over 1000+ platforms including YouTube, Spotify, SoundCloud, Instagram, TikTok, and many more. Built with Python and featuring a beautiful Rich CLI interface, it provides enterprise-level features with consumer-friendly simplicity.

### Why Choose Ultimate Media Downloader?

- **1000+ Platforms**: Download from virtually any media platform
- **High Quality**: Support for 4K/8K video and 320kbps audio
- **Smart Metadata**: Automatic thumbnail embedding and metadata tagging
- **Playlist Support**: Download entire playlists and channels
- **Advanced Features**: Proxy support, concurrent downloads, retry logic
- **Beautiful UI**: Modern CLI with progress bars and rich formatting
- **Cross-Platform**: Works on Linux, macOS, and Windows
- **Active Development**: Regular updates and improvements
- **Comprehensive Docs**: Extensive documentation with examples
- **Modular Design**: Clean, maintainable codebase

---

## Features

### Core Features

- **Video Downloads**: Support for all major video platforms
- **Audio Extraction**: Convert videos to high-quality audio
- **Social Media**: Download from Instagram, TikTok, Twitter, Facebook
- **Music Platforms**: Spotify, SoundCloud, Apple Music support
- **Streaming Services**: Twitch, Dailymotion, Vimeo, and more
- **Batch Processing**: Download multiple URLs or entire playlists
- **Concurrent Downloads**: Multiple simultaneous downloads
- **Format Conversion**: Multiple output formats (MP4, MKV, MP3, FLAC, etc.)

### Advanced Features

- **Thumbnail Embedding**: Automatic album art and video thumbnails
- **Metadata Tagging**: ID3 tags, artist, album, year, genre
- **Proxy Support**: HTTP/HTTPS/SOCKS proxy configuration
- **Authentication**: Login support for premium content
- **Quality Selection**: Choose specific quality (4K, 1080p, 720p, etc.)
- **Progress Tracking**: Real-time download progress with ETA
- **Auto Retry**: Intelligent retry logic for failed downloads
- **Subtitle Support**: Download and embed subtitles
- **Archive Mode**: Skip previously downloaded files

### User Interface

- **Rich CLI**: Beautiful terminal interface with colors and formatting
- **Progress Bars**: Real-time download progress visualization
- **Search Integration**: Search and download directly
- **Interactive Mode**: User-friendly interactive prompts
- **Verbose Logging**: Detailed logs for troubleshooting

---

## Supported Platforms

### Video Platforms
YouTube, Vimeo, Dailymotion, Twitch, Facebook, Reddit, Twitter/X, Imgur

### Social Media
Instagram, TikTok, Snapchat, Pinterest

### Music Platforms
Spotify, SoundCloud, Apple Music, Bandcamp, Mixcloud

### Streaming Services
Twitch, Streamable, Vidme, Coub

### Educational & Professional
TED Talks, Lynda

### Generic Support
- **1000+ Sites**: Via yt-dlp, supports most sites with embedded videos
- **M3U8 Streams**: HLS stream downloads
- **DASH/MPD**: MPEG-DASH support
- **Direct URLs**: Direct video/audio file URLs

For the complete list and platform-specific guides, see [USER_GUIDE.md](docs/USER_GUIDE.md#platform-specific-guides)

---

## System Requirements

### Minimum Requirements

- **Operating System**: Linux, macOS 10.12+, Windows 10+
- **Python**: 3.9 or higher
- **RAM**: 2GB minimum, 4GB recommended
- **Storage**: 100MB for installation + space for downloads
- **Internet**: Stable internet connection

### Required Software

- **Python 3.9+**: Core runtime
- **FFmpeg**: Video/audio processing (auto-installed by setup script)
- **pip**: Python package manager

For detailed requirements, see [USER_GUIDE.md](docs/USER_GUIDE.md#prerequisites)

---

## Installation

### Method 1: Automated Setup (Recommended)

The easiest way to get started:

```bash
# Clone the repository
git clone https://github.com/NK2552003/ULTIMATE-MEDIA-DOWNLOADER.git
cd ULTIMATE-MEDIA-DOWNLOADER

# Run setup script (one command does everything!)
chmod +x setup.sh
./setup.sh

# Activate environment
source activate-env.sh
```

**The setup script automatically:**
- [x] Detects your operating system (Linux/macOS/Windows)
- [x] Checks and installs Python 3.9+ if needed
- [x] Installs FFmpeg for video processing
- [x] Creates isolated virtual environment
- [x] Installs all Python packages
- [x] Creates configuration files
- [x] Runs verification tests

**Estimated time**: 3-5 minutes

### Method 2: Manual Installation

<details>
<summary>Click to expand manual installation instructions</summary>

#### Linux (Ubuntu/Debian)

```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv ffmpeg
git clone https://github.com/NK2552003/ULTIMATE-MEDIA-DOWNLOADER.git
cd ULTIMATE-MEDIA-DOWNLOADER
python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt
```

#### macOS

```bash
brew install python@3.11 ffmpeg
git clone https://github.com/NK2552003/ULTIMATE-MEDIA-DOWNLOADER.git
cd ULTIMATE-MEDIA-DOWNLOADER
python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt
```

#### Windows

```powershell
# Install Python from python.org and FFmpeg from ffmpeg.org
git clone https://github.com/NK2552003/ULTIMATE-MEDIA-DOWNLOADER.git
cd ULTIMATE-MEDIA-DOWNLOADER
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
```

</details>

For troubleshooting installation issues, see [USER_GUIDE.md](docs/USER_GUIDE.md#troubleshooting)

---

## Quick Start

### Basic Usage

```bash
# Activate environment (if not already activated)
source activate-env.sh

# Download a video
python3 ultimate_downloader.py "YOUR_VIDEO_URL"

# Download audio only
python3 ultimate_downloader.py -a "https://www.youtube.com/watch?v=VIDEO_ID"

# Download playlist
python3 ultimate_downloader.py -p "https://www.youtube.com/playlist?list=PLAYLIST_ID"

# Interactive mode
python3 ultimate_downloader.py -i
```

### Common Examples

```bash
# Download best quality video
python3 ultimate_downloader.py "VIDEO_URL"

# Download specific quality
python3 ultimate_downloader.py --quality 1080 "VIDEO_URL"

# Extract audio as MP3
python3 ultimate_downloader.py -a "VIDEO_URL"

# Download with subtitles
python3 ultimate_downloader.py --subtitles "VIDEO_URL"

# Custom output directory
python3 ultimate_downloader.py -o ~/Downloads/Videos "VIDEO_URL"

# Download with proxy
python3 ultimate_downloader.py --proxy "http://proxy:port" "VIDEO_URL"
```

For more examples and advanced usage, see [USER_GUIDE.md](docs/USER_GUIDE.md) and [QUICK_REFERENCE.md](QUICK_REFERENCE.md)

---

## Documentation

### Quick Access

- **[Documentation Index](docs/INDEX.md)** - Central hub for all documentation
- **[User Guide](docs/USER_GUIDE.md)** - Comprehensive user manual
- **[Quick Reference](QUICK_REFERENCE.md)** - Common commands cheat sheet
- **[API Reference](docs/API_REFERENCE.md)** - Developer API documentation
- **[Architecture](docs/ARCHITECTURE.md)** - System design and components
- **[Project Structure](docs/PROJECT_STRUCTURE.md)** - Code organization
- **[Flowcharts](docs/FLOWCHARTS.md)** - Visual process flows

### For Different Users

- **New User?** → Start with [Installation](docs/USER_GUIDE.md#installation) and [Quick Start](#-quick-start)
- **Developer?** → Check [API Reference](docs/API_REFERENCE.md) and [Architecture](docs/ARCHITECTURE.md)
- **Contributor?** → Read [Contributing Guide](CONTRIBUTING.md)
- **Need Help?** → See [Troubleshooting](docs/USER_GUIDE.md#troubleshooting) and [FAQ](docs/USER_GUIDE.md#faq)

---

## Contributing

We welcome contributions! Here's how you can help:

### Ways to Contribute

1. **Report Bugs**: Open an issue with details
2. **Suggest Features**: Share your ideas
3. **Improve Documentation**: Fix typos, add examples
4. **Submit Code**: Fix bugs or add features
5. **Translations**: Help translate the UI

### Quick Start for Contributors

```bash
# Fork the repository and clone your fork
git clone https://github.com/YOUR_USERNAME/ULTIMATE-MEDIA-DOWNLOADER.git
cd ULTIMATE-MEDIA-DOWNLOADER

# Create a branch
git checkout -b feature/your-feature-name

# Make changes and commit
git add .
git commit -m "Description of changes"

# Push and create pull request
git push origin feature/your-feature-name
```

For detailed guidelines, see [CONTRIBUTING.md](CONTRIBUTING.md)

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## Disclaimer

**IMPORTANT**: This tool is provided for educational and personal use only.

### Legal Considerations

- [x] **Allowed**: Downloading content you own or have permission to download
- [x] **Allowed**: Downloading public domain or Creative Commons content
- [x] **Allowed**: Personal backups of purchased content
- [ ] **Not Allowed**: Downloading copyrighted content without permission
- [ ] **Not Allowed**: Redistributing downloaded content
- [ ] **Not Allowed**: Commercial use without proper licenses

### User Responsibilities

By using this software, you agree to:
1. Comply with all applicable laws and regulations
2. Respect copyright and intellectual property rights
3. Follow the terms of service of content platforms
4. Use the tool ethically and responsibly
5. Not use it for piracy or unauthorized distribution

### No Warranty

This software is provided "as is" without warranty of any kind. The authors are not responsible for any misuse or legal consequences.

---

## Acknowledgments

This project is built with amazing open-source tools:

- [yt-dlp](https://github.com/yt-dlp/yt-dlp) - Core download engine
- [Rich](https://github.com/Textualize/rich) - Beautiful terminal formatting
- [Mutagen](https://github.com/quodlibet/mutagen) - Audio metadata
- [Spotipy](https://github.com/plamere/spotipy) - Spotify API
- [FFmpeg](https://ffmpeg.org/) - Media processing

Special thanks to all contributors and the open-source community!

---

## Contact & Support

- **Bug Reports**: [GitHub Issues](https://github.com/NK2552003/ULTIMATE-MEDIA-DOWNLOADER/issues)
- **Feature Requests**: [GitHub Discussions](https://github.com/NK2552003/ULTIMATE-MEDIA-DOWNLOADER/discussions)
- **Documentation**: [docs/INDEX.md](docs/INDEX.md)
- **Repository**: https://github.com/NK2552003/ULTIMATE-MEDIA-DOWNLOADER

---

## Project Statistics

| Metric | Count |
|--------|-------|
| **Total Lines of Code** | 8,195+ lines |
| **Python Modules** | 5 core modules |
| **Supported Platforms** | 1000+ |
| **Documentation Lines** | 4,000+ lines |
| **Code Examples** | 50+ examples |

For detailed statistics, see [PROJECT_STRUCTURE.md](docs/PROJECT_STRUCTURE.md)

---

## Recent Updates

### Version 2.0.0 (October 2025) - Current
- [x] Complete documentation overhaul
- [x] New API Reference documentation
- [x] Modular code structure
- [x] Enhanced Spotify integration
- [x] Improved error handling
- [x] Rich CLI interface

📖 For complete version history, see [CHANGELOG.md](CHANGELOG.md)

---

<div align="center">

**Made with ❤️ by [Nitish Kumar](https://github.com/NK2552003)**

If you find this project useful, please consider giving it a star!

[⬆ Back to Top](#ultimate-media-downloader-)

</div>
