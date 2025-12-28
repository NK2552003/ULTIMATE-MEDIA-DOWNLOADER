<div align="center">
    <h1>Ultimate Media Downloader</h1>
    <b>Download media from 1000+ platforms with one command: <code>umd</code></b></br></br>
    <a href="https://www.python.org/downloads/"><img src="https://img.shields.io/badge/python-3.9%2B-blue.svg" alt="Python Version"></a>
    <a href="LICENSE"><img src="https://img.shields.io/badge/license-Apache%202.0-blue.svg" alt="License"></a>
    <a href="https://github.com/NK2552003/ULTIMATE-MEDIA-DOWNLOADER"><img src="https://img.shields.io/github/stars/NK2552003/ULTIMATE-MEDIA-DOWNLOADER?style=social" alt="GitHub Stars"></a>
    <a href="https://github.com/NK2552003/ULTIMATE-MEDIA-DOWNLOADER/commits/main"><img src="https://img.shields.io/github/last-commit/NK2552003/ULTIMATE-MEDIA-DOWNLOADER.svg" alt="Last Commit"></a><br/><br/>
    <a href="#features">Features</a> - <a href="#installation">Installation</a> - <a href="#quick-start">Quick Start</a> - <a href="#documentation">Documentation</a> - <a href="CONTRIBUTING.md">Contributing</a> - <a href="CODE_OF_CONDUCT.md">Code of Conduct</a>
</div>

---
><strong>⚠️ Disclaimer</strong>
This software is provided for educational and personal use only. Users are responsible for complying with the terms of service of any websites or platforms from which they download content. The authors and contributors of this software:
 >- Do not endorse or encourage copyright infringement
 >- Are not responsible for any misuse of this software
 >- Recommend users only download content they have the right to access
 >- Advise users to respect intellectual property rights and applicable laws
 >
>By using this software, you agree to use it responsibly and in compliance with all applicable laws and regulations in your jurisdiction.

## Overview

Ultimate Media Downloader is a professional-grade, open-source media downloading tool supporting 100+ platforms (YouTube, Spotify, SoundCloud, Instagram, TikTok,Apple Music and more). Built with Python, it features a beautiful Rich CLI interface and enterprise-level capabilities with consumer-friendly simplicity.

### Why Choose Ultimate Media Downloader?

| Feature                | Description |
|------------------------|-------------|
| **One Command**        | Install once, use <code>umd</code> from anywhere |
| **100+ Platforms**    | YouTube, Spotify,Apple Music, Instagram, TikTok, SoundCloud, and more |
| **No Virtual Env**     | Clean installation with <code>pipx</code> |
| **Auto Organization**  | Downloads saved to <code>~/Downloads/UltimateDownloader</code> |
| **Beautiful UI**       | Modern CLI with progress bars and rich formatting |
| **Fast Downloads**     | Concurrent downloads with resume support |
| **High Quality**       | 4K/8K video, 320kbps audio, metadata embedding |
| **Active Development** | Regular updates and improvements |

---
## Features
### Core Capabilities

| Type   | Platforms & Features |
|--------|---------------------|
| **Video** | YouTube (4K/8K), Vimeo, Dailymotion, Live streams, Age-restricted, Custom quality, HiAnime|
| **Audio** | Spotify (via YouTube search), SoundCloud, Apple Music, 320kbps, FLAC, MP3 |
| **Playlists** | YouTube, Spotify, SoundCloud, TikTok, Instagram, Batch download |
| **Social** | Instagram, TikTok, Facebook, Twitter/X, Twitch, IGTV, Reels, Stories |
| **Generic** | 1000+ sites via yt-dlp, SSL/TLS bypass, proxy rotation |

---

## Installation

### Quick Install (Recommended)

Install in just **2 commands** - no virtual environment needed!

```bash
git clone https://github.com/NK2552003/ULTIMATE-MEDIA-DOWNLOADER.git
cd ULTIMATE-MEDIA-DOWNLOADER
./scripts/install.sh
```

**Windows users:**
```batch
git clone https://github.com/NK2552003/ULTIMATE-MEDIA-DOWNLOADER.git
cd ULTIMATE-MEDIA-DOWNLOADER
scripts\install.bat
```

That's it! Now use from anywhere:

```bash
umd <URL>
```

### What Gets Installed

 No virtual environment needed  
 Global `umd` command available everywhere  
 All dependencies handled automatically  
 FFmpeg installed/verified  
 Downloads directory created at `~/Downloads/UltimateDownloader`  

**Installation time**: 2-5 minutes

---

### Prerequisites

Before installing, ensure you have:

- **Python 3.9+** - [Download here](https://www.python.org/downloads/)
- **Git** - [Download here](https://git-scm.com/downloads)
- **FFmpeg** (optional, will be prompted during installation)

Check your Python version:
```bash
python3 --version
```

---

### Alternative Installation Methods

<details>
<summary><b>Method 1: Using pipx (Manual)</b></summary>

```bash
# Install pipx if not already installed
brew install pipx  # macOS
# or
pip install --user pipx  # Linux/Windows

# Clone and install
git clone https://github.com/NK2552003/ULTIMATE-MEDIA-DOWNLOADER.git
cd ULTIMATE-MEDIA-DOWNLOADER
pipx install -e .
```

</details>

<details>
<summary><b>Method 2: Using pip</b></summary>

```bash
git clone https://github.com/NK2552003/ULTIMATE-MEDIA-DOWNLOADER.git
cd ULTIMATE-MEDIA-DOWNLOADER
pip3 install -e .
```

</details>

<details>
<summary><b>Method 3: Virtual Environment</b></summary>

```bash
git clone https://github.com/NK2552003/ULTIMATE-MEDIA-DOWNLOADER.git
cd ULTIMATE-MEDIA-DOWNLOADER
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python ultimate_downloader.py <URL>
```

</details>

---

### ️ Platform-Specific Installation

<details>
<summary><b> macOS</b></summary>

```bash
# Install prerequisites
brew install python@3.11 ffmpeg pipx

# Clone and install
git clone https://github.com/NK2552003/ULTIMATE-MEDIA-DOWNLOADER.git
cd ULTIMATE-MEDIA-DOWNLOADER
./scripts/setup.sh
```

If `umd` command not found, add to PATH:
```bash
echo 'export PATH="$PATH:$HOME/Library/Python/3.11/bin"' >> ~/.zshrc
source ~/.zshrc
```

</details>

<details>
<summary><b> Linux (Ubuntu/Debian)</b></summary>

```bash
# Install prerequisites
sudo apt update
sudo apt install -y python3 python3-pip ffmpeg git

# Clone and install
git clone https://github.com/NK2552003/ULTIMATE-MEDIA-DOWNLOADER.git
cd ULTIMATE-MEDIA-DOWNLOADER
./scripts/install.sh
```

If `umd` command not found, add to PATH:
```bash
echo 'export PATH="$PATH:$HOME/.local/bin"' >> ~/.bashrc
source ~/.bashrc
```

</details>

<details>
<summary><b>🪟 Windows</b></summary>

**Step 1: Install Prerequisites**
1. Install Python from [python.org](https://www.python.org/downloads/) (Check "Add Python to PATH")
2. Install Git from [git-scm.com](https://git-scm.com/downloads)
3. Install FFmpeg:
   - Using Chocolatey: `choco install ffmpeg`
   - Or download from [ffmpeg.org](https://ffmpeg.org/download.html)

**Step 2: Install Ultimate Media Downloader**
```batch
git clone https://github.com/NK2552003/ULTIMATE-MEDIA-DOWNLOADER.git
cd ULTIMATE-MEDIA-DOWNLOADER
scripts\setup.bat
```

</details>

---

### Verify Installation

```bash
# Check if installed
umd --version

# Show help
umd --help

# Test with a video
umd "https://www.youtube.com/watch?v=dQw4w9WgXcQ" --info
```

---

### Detailed Installation Guide

For comprehensive installation instructions, troubleshooting, and platform-specific guides, see:

**[📖 Installation Guide](documentations/INSTALLATION.md)**

---

## Quick Start

### Basic Usage

```bash
# Interactive mode (easiest for beginners)
umd

# Download a video
umd "https://youtube.com/watch?v=VIDEO_ID"

# Download audio only as MP3
umd "https://youtube.com/watch?v=VIDEO_ID" --audio-only --format mp3

# Download in specific quality
umd "URL" --quality 1080p

# Download entire playlist
umd "https://youtube.com/playlist?list=PLAYLIST_ID"

# Show all available options
umd --help
```

### Advanced Examples

```bash
# Download with metadata and thumbnail
umd "URL" --audio-only --embed-metadata --embed-thumbnail

# Batch download from file
umd --batch-file urls.txt --audio-only

# Parallel batch download
umd --batch-file urls.txt --optimized-batch --max-concurrent 5

# Custom output directory
umd "URL" --output /path/to/folder

# Show available formats
umd "URL" --show-formats

# Download specific quality video
umd "URL" --quality 1080p --format mp4
```

### Download Locations

Downloads are automatically saved to:
```
~/Downloads/UltimateDownloader/
├── Artist Name - Song Title.mp3
├── Video Title.mp4
├── Playlist Name/
│   ├── Song 1.mp3
│   ├── Song 2.mp3
│   └── Song 3.mp3
└── Album Name/
    └── tracks...
```

For more examples and detailed usage, see **[Usage Guide](docs/USAGE.md)**

---

## Documentation


- **[Installation Guide](documentations/INSTALLATION.md)** - Comprehensive installation instructions
- **[Usage Guide](documentations/USAGE.md)** - Get started in 5 minutes
- **[Architecture](documentations/ARCHITECTURE.md)** - System design and components
- **[File Structure](documentations/FILE_STRUCTURE.md)** - Project file organization
- **[Contributing Guide](CONTRIBUTING.md)** - How to contribute
- **[Changelog](documentations/CHANGELOG.md)** - Version history and updates

## ️ System Requirements

### Minimum Requirements
- **Operating System**: Linux, macOS 10.12+, Windows 10+
- **Python**: 3.9 or higher
- **RAM**: 2GB minimum, 4GB recommended
- **Storage**: 100MB for installation + space for downloads
- **Internet**: Stable internet connection

### Required Software
- **Python 3.9+**: Core runtime
- **FFmpeg**: Video/audio processing (can be auto-installed)
- **pip**: Python package manager

---

## Contributing

We welcome contributions! Here's how you can help:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

See **[CONTRIBUTING.md](CONTRIBUTING.md)** for detailed guidelines.

---

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

For information about third-party licenses used in this project, see [THIRD_PARTY_LICENSES.md](THIRD_PARTY_LICENSES.md).


## Acknowledgments

Built with:
- [yt-dlp](https://github.com/yt-dlp/yt-dlp) - Media extraction engine
- [Rich](https://github.com/Textualize/rich) - Beautiful terminal formatting
- [FFmpeg](https://ffmpeg.org/) - Media processing
- [SpotDL](https://github.com/spotDL/spotify-downloader) - Spotify integration

Special thanks to all contributors and the open-source community!

---

## Support & Contact

- **Bug Reports**: [Open an issue](https://github.com/NK2552003/ULTIMATE-MEDIA-DOWNLOADER/issues)
- **Feature Requests**: [Start a discussion](https://github.com/NK2552003/ULTIMATE-MEDIA-DOWNLOADER/discussions)
- **Contact**: [Create an issue](https://github.com/NK2552003/ULTIMATE-MEDIA-DOWNLOADER/issues)
- ⭐ **Show Support**: [Star the repository](https://github.com/NK2552003/ULTIMATE-MEDIA-DOWNLOADER)


---

<div align="center">

**Made with ❤️ & with love by [NK2552003](https://github.com/NK2552003)**

⭐ Star this repository if you find it useful!

[Report Bug](https://github.com/NK2552003/ULTIMATE-MEDIA-DOWNLOADER/issues) • [Request Feature](https://github.com/NK2552003/ULTIMATE-MEDIA-DOWNLOADER/issues) • [Documentation](documentations/INDEX.md)

</div>
