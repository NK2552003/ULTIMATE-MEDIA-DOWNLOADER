# Ultimate Media Downloader 🎬🎵

<div align="center">

[![Python Version](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-Linux%20%7C%20macOS%20%7C%20Windows-lightgrey.svg)](https://github.com/NK2552003/ULTIMATE-MEDIA-DOWNLOADER)
[![Maintained](https://img.shields.io/badge/maintained-yes-brightgreen.svg)](https://github.com/NK2552003/ULTIMATE-MEDIA-DOWNLOADER/commits/main)
[![Last Updated](https://img.shields.io/badge/updated-October%202025-blue.svg)](https://github.com/NK2552003/ULTIMATE-MEDIA-DOWNLOADER)

**A powerful, feature-rich media downloader supporting 1000+ platforms**

[Features](#-features) • [Installation](#-installation) • [Usage](#-usage) • [Documentation](#-documentation) • [Contributing](#-contributing)

</div>

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [Supported Platforms](#-supported-platforms)
- [System Requirements](#-system-requirements)
- [Installation](#-installation)
- [Quick Start](#-quick-start)
- [Usage Examples](#-usage-examples)
- [Configuration](#-configuration)
- [Architecture](#-architecture)
- [Documentation](#-documentation)
- [Troubleshooting](#-troubleshooting)
- [Contributing](#-contributing)
- [License](#-license)
- [Disclaimer](#-disclaimer)

---

## 🌟 Overview

**Ultimate Media Downloader** is a professional-grade, open-source media downloading tool that supports over 1000+ platforms including YouTube, Spotify, SoundCloud, Instagram, TikTok, and many more. Built with Python and featuring a beautiful Rich CLI interface, it provides enterprise-level features with consumer-friendly simplicity.

### Why Choose Ultimate Media Downloader?

- ✅ **1000+ Platforms**: Download from virtually any media platform
- ✅ **High Quality**: Support for 4K/8K video and 320kbps audio
- ✅ **Smart Metadata**: Automatic thumbnail embedding and metadata tagging
- ✅ **Playlist Support**: Download entire playlists and channels
- ✅ **Advanced Features**: Proxy support, concurrent downloads, retry logic
- ✅ **Beautiful UI**: Modern CLI with progress bars and rich formatting
- ✅ **Cross-Platform**: Works on Linux, macOS, and Windows
- ✅ **Active Development**: Regular updates and improvements

---

## ✨ Features

### Core Features

- 🎥 **Video Downloads**: Support for all major video platforms
- 🎵 **Audio Extraction**: Convert videos to high-quality audio
- 📱 **Social Media**: Download from Instagram, TikTok, Twitter, Facebook
- 🎼 **Music Platforms**: Spotify, SoundCloud, Apple Music support
- 📺 **Streaming Services**: Twitch, Dailymotion, Vimeo, and more
- 🔄 **Batch Processing**: Download multiple URLs or entire playlists
- ⚡ **Concurrent Downloads**: Multiple simultaneous downloads
- 🎨 **Format Conversion**: Multiple output formats (MP4, MKV, MP3, FLAC, etc.)

### Advanced Features

- 🖼️ **Thumbnail Embedding**: Automatic album art and video thumbnails
- 🏷️ **Metadata Tagging**: ID3 tags, artist, album, year, genre
- 🌐 **Proxy Support**: HTTP/HTTPS/SOCKS proxy configuration
- 🔐 **Authentication**: Login support for premium content
- 🎯 **Quality Selection**: Choose specific quality (4K, 1080p, 720p, etc.)
- 📊 **Progress Tracking**: Real-time download progress with ETA
- 🔁 **Auto Retry**: Intelligent retry logic for failed downloads
- 🌍 **Subtitle Support**: Download and embed subtitles
- 🎚️ **Audio Normalization**: Consistent audio levels
- 📦 **Archive Mode**: Skip previously downloaded files

### User Interface

- 🎨 **Rich CLI**: Beautiful terminal interface with colors and formatting
- 📊 **Progress Bars**: Real-time download progress visualization
- 🔍 **Search Integration**: Search and download directly
- 💬 **Interactive Mode**: User-friendly interactive prompts
- 📝 **Verbose Logging**: Detailed logs for troubleshooting
- 🎭 **ASCII Art**: Modern, professional visual design

---

## 🌐 Supported Platforms

### Video Platforms
- **YouTube**: Videos, playlists, channels, live streams
- **Vimeo**: Videos and playlists
- **Dailymotion**: Videos and playlists
- **Twitch**: VODs and clips
- **Facebook**: Videos
- **Reddit**: Video posts
- **Twitter/X**: Videos and GIFs
- **Imgur**: Videos and GIFs

### Social Media
- **Instagram**: Posts, Reels, Stories, IGTV
- **TikTok**: Videos and profiles
- **Snapchat**: Stories (public)
- **Pinterest**: Video pins

### Music Platforms
- **Spotify**: Tracks, albums, playlists (requires API)
- **SoundCloud**: Tracks and playlists
- **Apple Music**: Tracks and albums (requires gamdl)
- **Bandcamp**: Tracks and albums
- **Mixcloud**: Mixes and shows

### Streaming Services
- **Twitch**: Clips, VODs, highlights
- **Streamable**: Videos
- **Vidme**: Videos
- **Coub**: Loops

### Educational & Professional
- **Udemy**: Course videos (owned courses)
- **Coursera**: Lecture videos
- **Khan Academy**: Videos
- **TED Talks**: Videos
- **Lynda**: Training videos

### Adult Content (18+)
- Various adult platforms supported through yt-dlp

### Generic Support
- **1000+ Sites**: Via yt-dlp, supports most sites with embedded videos
- **M3U8 Streams**: HLS stream downloads
- **DASH/MPD**: MPEG-DASH support
- **Direct URLs**: Direct video/audio file URLs

---

## 💻 System Requirements

### Minimum Requirements

- **Operating System**: Linux, macOS 10.12+, Windows 10+
- **Python**: 3.9 or higher
- **RAM**: 2GB minimum, 4GB recommended
- **Storage**: 100MB for installation + space for downloads
- **Internet**: Stable internet connection

### Recommended Requirements

- **Python**: 3.11 or higher
- **RAM**: 8GB or more
- **Storage**: SSD with sufficient space
- **CPU**: Multi-core processor for concurrent downloads

### Required Software

- **Python 3.9+**: Core runtime
- **FFmpeg**: Video/audio processing (auto-installed)
- **pip**: Python package manager

### Optional Software

- **Chrome/Chromium**: For sites requiring browser automation
- **ChromeDriver**: Automated browser control

---

## 🚀 Installation

### Method 1: Automated Setup (Recommended)

```bash
# Clone the repository
git clone https://github.com/NK2552003/ULTIMATE-MEDIA-DOWNLOADER.git
cd ULTIMATE-MEDIA-DOWNLOADER

# Run setup script
chmod +x setup.sh
./setup.sh

# Activate environment
source activate-env.sh
```

The setup script will:
- ✅ Detect your operating system
- ✅ Install Python dependencies
- ✅ Install FFmpeg
- ✅ Create virtual environment
- ✅ Configure the application
- ✅ Run tests

### Method 2: Manual Installation

#### Linux (Ubuntu/Debian)

```bash
# Install system dependencies
sudo apt update
sudo apt install python3 python3-pip python3-venv ffmpeg

# Clone repository
git clone https://github.com/NK2552003/ULTIMATE-MEDIA-DOWNLOADER.git
cd ULTIMATE-MEDIA-DOWNLOADER

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python packages
pip3 install -r requirements.txt
```

#### macOS

```bash
# Install Homebrew if not installed
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install dependencies
brew install python@3.11 ffmpeg

# Clone repository
git clone https://github.com/NK2552003/ULTIMATE-MEDIA-DOWNLOADER.git
cd ULTIMATE-MEDIA-DOWNLOADER

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python packages
pip3 install -r requirements.txt
```

#### Windows

```powershell
# Install Python from python.org (check "Add to PATH")
# Install FFmpeg from ffmpeg.org

# Clone repository
git clone https://github.com/NK2552003/ULTIMATE-MEDIA-DOWNLOADER.git
cd ULTIMATE-MEDIA-DOWNLOADER

# Create virtual environment
python3 -m venv venv
.\venv\Scripts\activate

# Install Python packages
pip3 install -r requirements.txt
```

---

## 🎯 Quick Start

### Basic Usage

```bash
# Use
source activate-env.sh
python3 ultimate_downloader.py "YOUR_VIDEO_URL"

# Download audio only
python3 ultimate_downloader.py -a "https://www.youtube.com/watch?v=VIDEO_ID"

# Download playlist
python3 ultimate_downloader.py -p "https://www.youtube.com/playlist?list=PLAYLIST_ID"

# Interactive mode
python3 ultimate_downloader.py -i
```

### First Time Setup

1. **Configure Spotify (Optional)**:
   ```bash
   # Edit config.json
   nano config.json
   
   # Add your Spotify credentials:
   {
     "spotify": {
       "client_id": "YOUR_CLIENT_ID",
       "client_secret": "YOUR_CLIENT_SECRET"
     }
   }
   ```

2. **Test Installation**:
   ```bash
   python3 ultimate_downloader.py --help
   ```

---

## 📖 Usage Examples

### Video Downloads

```bash
# Download best quality video
python3 ultimate_downloader.py "VIDEO_URL"

# Download specific quality
python3 ultimate_downloader.py --quality 1080 "VIDEO_URL"

# Download with subtitles
python3 ultimate_downloader.py --subtitles "VIDEO_URL"

# Download specific format
python3 ultimate_downloader.py --format mp4 "VIDEO_URL"
```

### Audio Downloads

```bash
# Extract audio as MP3
python3 ultimate_downloader.py -a "VIDEO_URL"

# High-quality audio
python3 ultimate_downloader.py -a --audio-quality 320 "VIDEO_URL"

# Audio in FLAC format
python3 ultimate_downloader.py -a --audio-format flac "VIDEO_URL"
```

### Playlist Downloads

```bash
# Download entire playlist
python3 ultimate_downloader.py -p "PLAYLIST_URL"

# Download playlist items 1-10
python3 ultimate_downloader.py -p --playlist-items 1-10 "PLAYLIST_URL"

# Download playlist in reverse
python3 ultimate_downloader.py -p --playlist-reverse "PLAYLIST_URL"
```

### Advanced Features

```bash
# Download with proxy
python3 ultimate_downloader.py --proxy "http://proxy:port" "VIDEO_URL"

# Concurrent downloads
python3 ultimate_downloader.py --concurrent 5 "PLAYLIST_URL"

# Custom output directory
python3 ultimate_downloader.py -o ~/Downloads/Videos "VIDEO_URL"

# Embed thumbnail and metadata
python3 ultimate_downloader.py --embed-thumbnail --embed-metadata "VIDEO_URL"

# Archive mode (skip downloaded)
python3 ultimate_downloader.py --archive archive.txt "PLAYLIST_URL"
```

### Search and Download

```bash
# Search YouTube and download
python3 ultimate_downloader.py --search "song name"

# Search and download first result
python3 ultimate_downloader.py --search "song name" --first
```

---

## ⚙️ Configuration

### Configuration File: `config.json`

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
        "embed_metadata": true
    },
    "proxy": {
        "enabled": false,
        "http": "",
        "https": ""
    },
    "advanced": {
        "concurrent_downloads": 3,
        "retry_attempts": 3,
        "timeout": 300
    }
}
```

### Command Line Options

```
positional arguments:
  url                   URL to download

optional arguments:
  -h, --help            Show help message
  -v, --version         Show version
  -i, --interactive     Interactive mode
  -a, --audio           Audio only
  -p, --playlist        Playlist mode
  -o, --output DIR      Output directory
  --quality QUALITY     Video quality (4K, 1080, 720, 480, 360)
  --format FORMAT       Output format (mp4, mkv, webm)
  --audio-format FMT    Audio format (mp3, flac, wav, aac)
  --audio-quality Q     Audio quality (320, 256, 192, 128)
  --subtitles           Download subtitles
  --embed-thumbnail     Embed thumbnail
  --embed-metadata      Embed metadata
  --proxy PROXY         Proxy URL
  --concurrent N        Concurrent downloads
  --search QUERY        Search and download
  --first               Download first search result
  --verbose             Verbose output
```

---

## 🏗️ Architecture

### System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     User Interface Layer                     │
│  ┌────────────┐  ┌────────────┐  ┌─────────────────────┐   │
│  │  CLI Args  │  │ Interactive│  │   Rich UI Display   │   │
│  └────────────┘  └────────────┘  └─────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                   Core Processing Layer                      │
│  ┌────────────┐  ┌────────────┐  ┌─────────────────────┐   │
│  │ URL Parser │  │ Validator  │  │  Queue Manager      │   │
│  └────────────┘  └────────────┘  └─────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                  Platform Handler Layer                      │
│  ┌──────────┐ ┌──────────┐ ┌─────────┐ ┌────────────────┐  │
│  │ YouTube  │ │ Spotify  │ │ Generic │ │ Social Media   │  │
│  └──────────┘ └──────────┘ └─────────┘ └────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                   Download Engine Layer                      │
│  ┌────────────┐  ┌────────────┐  ┌─────────────────────┐   │
│  │  yt-dlp    │  │  Requests  │  │  Browser Automation │   │
│  └────────────┘  └────────────┘  └─────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                 Post-Processing Layer                        │
│  ┌────────────┐  ┌────────────┐  ┌─────────────────────┐   │
│  │   FFmpeg   │  │  Metadata  │  │  Format Conversion  │   │
│  └────────────┘  └────────────┘  └─────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                      Storage Layer                           │
│                   [Downloaded Files]                         │
└─────────────────────────────────────────────────────────────┘
```

### Component Details

See [ARCHITECTURE.md](docs/ARCHITECTURE.md) for detailed architecture documentation.

---

## 📚 Documentation

### Available Documentation

- 📘 [Architecture Guide](docs/ARCHITECTURE.md) - System design and components
- 📗 [API Reference](docs/API.md) - Developer API documentation
- 📕 [User Guide](docs/USER_GUIDE.md) - Comprehensive user manual
- 📙 [Troubleshooting](docs/TROUBLESHOOTING.md) - Common issues and solutions
- 📓 [Development](docs/DEVELOPMENT.md) - Contributing and development guide
- 📊 [Flowcharts](docs/FLOWCHARTS.md) - Visual process flows

### Flowcharts

All process flowcharts are available in the `docs/` directory using Mermaid syntax.

---

## 🔧 Troubleshooting

### Common Issues

#### 1. FFmpeg Not Found
```bash
# Linux
sudo apt install ffmpeg

# macOS
brew install ffmpeg

# Windows
# Download from ffmpeg.org and add to PATH
```

#### 2. Permission Errors
```bash
# Make scripts executable
chmod +x setup.sh activate-env.sh

# Fix Python permissions
sudo chown -R $USER:$USER venv/
```

#### 3. SSL Certificate Errors
```bash
# Update certificates
pip3 install --upgrade certifi

# Or disable SSL verification (not recommended)
python3 ultimate_downloader.py --no-check-certificate "URL"
```

#### 4. Module Import Errors
```bash
# Reinstall requirements
pip3 install --force-reinstall -r requirements.txt

# Or install specific package
pip3 install package-name
```

For more issues, see [TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)

---

## 🤝 Contributing

We welcome contributions! Here's how you can help:

### Ways to Contribute

1. 🐛 **Report Bugs**: Open an issue with details
2. 💡 **Suggest Features**: Share your ideas
3. 📝 **Improve Documentation**: Fix typos, add examples
4. 🔧 **Submit Code**: Fix bugs or add features
5. 🌍 **Translations**: Help translate the UI

### Contribution Process

```bash
# Fork the repository
# Clone your fork
git clone https://github.com/YOUR_USERNAME/ULTIMATE-MEDIA-DOWNLOADER.git

# Create a branch
git checkout -b feature/your-feature-name

# Make changes and commit
git add .
git commit -m "Description of changes"

# Push and create pull request
git push origin feature/your-feature-name
```

### Development Setup

```bash
# Install development dependencies
pip3 install -r requirements-dev.txt

# Run tests
pytest tests/

# Format code
black .

# Lint code
flake8 .
```

See [CONTRIBUTING.md](docs/CONTRIBUTING.md) for detailed guidelines.

---

## 📊 Project Statistics

- **Lines of Code**: ~8000+
- **Supported Platforms**: 1000+
- **Dependencies**: 20+ packages
- **Languages**: Python 3.9+
- **Development Time**: Ongoing since 2024

---

## 🗺️ Roadmap

### Version 2.1 (Q1 2026)
- [ ] Proper Folder Structure for Project
- [ ] GUI interface (Tkinter/PyQt)
- [ ] Browser extension
- [ ] Mobile app (React Native)
- [ ] Cloud storage integration
- [ ] Better playlist management

### Version 2.2 (Q3 2026)
- [ ] AI-powered quality enhancement
- [ ] Automatic subtitle generation
- [ ] Advanced scheduling
- [ ] Web interface
- [ ] API server mode

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

### Third-Party Licenses

This project uses several open-source libraries. See [LICENSE](LICENSE) for full details.

---

## ⚠️ Disclaimer

**IMPORTANT**: This tool is provided for educational and personal use only.

### Legal Considerations

- ✅ **Allowed**: Downloading content you own or have permission to download
- ✅ **Allowed**: Downloading public domain or Creative Commons content
- ✅ **Allowed**: Personal backups of purchased content
- ❌ **Not Allowed**: Downloading copyrighted content without permission
- ❌ **Not Allowed**: Redistributing downloaded content
- ❌ **Not Allowed**: Commercial use without proper licenses

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

## 📞 Contact & Support

### Get Help

- 📧 **Issues**: [GitHub Issues](https://github.com/NK2552003/ULTIMATE-MEDIA-DOWNLOADER/issues)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/NK2552003/ULTIMATE-MEDIA-DOWNLOADER/discussions)
- 🐛 **Bug Reports**: Use issue templates
- 💡 **Feature Requests**: Open a discussion

### Links

- 🌐 **Repository**: https://github.com/NK2552003/ULTIMATE-MEDIA-DOWNLOADER
- 📖 **Documentation**: https://github.com/NK2552003/ULTIMATE-MEDIA-DOWNLOADER/tree/main/docs
- 🚀 **Releases**: https://github.com/NK2552003/ULTIMATE-MEDIA-DOWNLOADER/releases

---

## 🙏 Acknowledgments

### Special Thanks

- **yt-dlp team** - Amazing video download library
- **Rich library** - Beautiful terminal formatting
- **Open Source Community** - For invaluable tools and libraries
- **Contributors** - Everyone who has contributed to this project

### Built With

- [Python](https://www.python.org/) - Core language
- [yt-dlp](https://github.com/yt-dlp/yt-dlp) - Download engine
- [Rich](https://github.com/Textualize/rich) - Terminal UI
- [FFmpeg](https://ffmpeg.org/) - Media processing
- [Requests](https://requests.readthedocs.io/) - HTTP library
- [Beautiful Soup](https://www.crummy.com/software/BeautifulSoup/) - HTML parsing

---

## ⭐ Star History

If you find this project useful, please consider giving it a star! ⭐

---

<div align="center">

**Made with ❤️ by Nitish Kumar**

[⬆ Back to Top](#ultimate-media-downloader-)

</div>
