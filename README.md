<div align="center">

# Ultimate Media Downloader

[](https://www.python.org/downloads/)
[](LICENSE)
[](https://github.com/NK2552003/ULTIMATE-MEDIA-DOWNLOADER)
[](https://github.com/NK2552003/ULTIMATE-MEDIA-DOWNLOADER/commits/main)
[](https://github.com/NK2552003/ULTIMATE-MEDIA-DOWNLOADER)

**Download media from 1000+ platforms with just one command: `umd`**

[Features](#features) • [Installation](#installation) • [Quick Start](#quick-start) • [Documentation](#documentation) • [Contributing](CONTRIBUTING.md) • [Code of Conduct](CODE_OF_CONDUCT.md)

</div>

---

## Overview

**Ultimate Media Downloader** is a professional-grade, open-source media downloading tool that supports over 1000+ platforms including YouTube, Spotify, SoundCloud, Instagram, TikTok, and many more. Built with Python and featuring a beautiful Rich CLI interface, it provides enterprise-level features with consumer-friendly simplicity.

### Why Choose Ultimate Media Downloader?

- **One Command**: Install once, use `umd` from anywhere
- **1000+ Platforms**: YouTube, Spotify, Instagram, TikTok, SoundCloud, and more
- **No Virtual Environment**: Clean installation with `pipx`
- **Auto Organization**: Downloads saved to `~/Downloads/UltimateDownloader`
- **Beautiful UI**: Modern CLI with progress bars and rich formatting
- **Fast Downloads**: Concurrent downloads with resume support
- **High Quality**: 4K/8K video, 320kbps audio, metadata embedding
- ️ **Active Development**: Regular updates and improvements

---

## Demo

<div align="center">

https://github.com/NK2552003/ULTIMATE-MEDIA-DOWNLOADER/blob/main/demo_video/demo.mp4

*Watch the Ultimate Media Downloader in action*

</div>

---

## Features

### Core Capabilities

 **Video Downloads**
- YouTube (4K/8K), Vimeo, Dailymotion
- Live streams and premieres
- Age-restricted content support
- Custom quality selection

 **Audio Downloads**
- Spotify (via YouTube search)
- SoundCloud, Apple Music
- MP3, FLAC, M4A, OPUS formats
- Automatic metadata & cover art embedding

 **Social Media**
- Instagram (Posts, Reels, IGTV, Stories)
- TikTok (Videos, User content)
- Twitter/X (Video tweets)
- Facebook (Videos, Live streams)

 **Streaming Platforms**
- Twitch (VODs, Clips, Live)
- YouTube Live
- Facebook Live
- And 1000+ more sites!

### Advanced Features

 **Smart URL Handling**
- YouTube Mix/Radio playlists (auto-extract single video)
- Playlist support with selection options
- Batch downloads from file
- Parallel processing

 **Quality & Format**
- Choose quality: Best, 4K, 1080p, 720p, 480p, 360p
- Multiple formats: MP4, MKV, MP3, FLAC, M4A, OPUS
- Custom format strings for advanced users
- Audio language selection

 **User Experience**
- Interactive mode for beginners
- Non-interactive mode for automation
- Real-time progress tracking
- Beautiful terminal UI with Rich
- Comprehensive error messages

 **Metadata & Thumbnails**
- Auto-embed album art
- ID3 tags (artist, title, album, year)
- Thumbnail embedding
- Spotify/Apple Music cover art fetching

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
./scripts/install.sh
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
scripts\install.bat
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

**[📖 Complete Installation Guide](docs/INSTALLATION_GUIDE.md)**

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

For more examples and detailed usage, see **[Quick Start Guide](docs/QUICKSTART.md)**

---

## Supported Platforms

<details>
<summary><b>Click to see full list of 1000+ supported platforms</b></summary>

### Video Platforms
- YouTube (Videos, Playlists, Live Streams, Shorts)
- Vimeo (Videos, Private content)
- Dailymotion
- Twitch (VODs, Clips, Streams)
- Facebook (Videos, Live)
- And many more...

### Social Media
- Instagram (Posts, Reels, IGTV, Stories)
- TikTok (Videos, User content)
- Twitter/X (Video tweets)
- Reddit (Videos)
- Snapchat

### Music Platforms
- Spotify (Tracks, Albums, Playlists - via YouTube search)
- SoundCloud (Tracks, Playlists, Sets)
- Apple Music (Tracks, Albums - via YouTube search)
- Bandcamp
- Mixcloud

### Streaming Services
- Twitch
- YouTube Live
- Facebook Live
- And more...

**Total: 1000+ supported sites via yt-dlp**

Use `umd --list-platforms` to see detailed platform support.

</details>

---

## Documentation

### User Documentation

- **[Installation Guide](docs/INSTALLATION_GUIDE.md)** - Comprehensive installation instructions
- **[Quick Start Guide](docs/QUICKSTART.md)** - Get started in 5 minutes
- **[Getting Started](docs/GETTING_STARTED.md)** - Step-by-step beginner guide
- **[Project Summary](docs/PROJECT_SUMMARY.md)** - Overview of the project
- **[Documentation Summary](docs/DOCUMENTATION_SUMMARY.md)** - All documentation in one place

### Technical Documentation

- **[File Structure](docs/FILE_STRUCTURE.md)** - Project file organization
- **[Contributing Guide](CONTRIBUTING.md)** - How to contribute
- **[Changelog](docs/CHANGELOG.md)** - Version history and updates

### Installation & Setup Guides

- **[Install Guide](docs/INSTALL.md)** - Installation instructions
- **[Uninstall Guide](docs/UNINSTALL.md)** - How to remove the application
- **[Windows Batch Files](docs/WINDOWS_BATCH_FILES.md)** - Windows installation help

---

## 🔧 How It Works

Ultimate Media Downloader uses a sophisticated multi-layered architecture to provide seamless media downloading from thousands of platforms.

### System Architecture

```mermaid
flowchart TB
    Start([User Initiates Download]) --> CLI[CLI Interface<br/>ultimate_downloader.py]
    CLI --> URLValidation{Valid URL?}
    
    URLValidation -->|No| Error1[Show Error Message]
    Error1 --> End1([End])
    
    URLValidation -->|Yes| PlatformDetect[Platform Detection<br/>yt-dlp]
    
    PlatformDetect --> PlatformType{Platform Type}
    
    PlatformType -->|YouTube/Video| VideoFlow[Video Download Flow]
    PlatformType -->|Spotify/Music| SpotifyFlow[Spotify Flow<br/>spotdl/YouTube Search]
    PlatformType -->|Social Media| SocialFlow[Social Media Flow<br/>Instagram/TikTok/Twitter]
    PlatformType -->|Generic| GenericFlow[Generic Downloader<br/>generic_downloader.py]
    
    VideoFlow --> QualitySelect[Quality Selection<br/>4K/1080p/720p/etc.]
    SpotifyFlow --> MusicSearch[YouTube Music Search<br/>Match by Metadata]
    SocialFlow --> ContentExtract[Content Extraction<br/>Posts/Reels/Stories]
    GenericFlow --> AutoDetect[Auto-detect Format]
    
    QualitySelect --> Download
    MusicSearch --> Download
    ContentExtract --> Download
    AutoDetect --> Download
    
    Download[Download Manager<br/>Concurrent Downloads] --> Processing{Processing Needed?}
    
    Processing -->|Video| FFmpegVideo[FFmpeg Processing<br/>Format Conversion<br/>Merge Audio+Video]
    Processing -->|Audio| FFmpegAudio[FFmpeg Audio<br/>Extract/Convert Audio<br/>Apply Quality Settings]
    Processing -->|None| DirectSave
    
    FFmpegVideo --> Metadata
    FFmpegAudio --> Metadata
    DirectSave[Direct Save] --> Metadata
    
    Metadata[Metadata Embedding<br/>- Title, Artist, Album<br/>- Thumbnail/Cover Art<br/>- ID3 Tags] --> Organization
    
    Organization[File Organization<br/>~/Downloads/UltimateDownloader/] --> Logger[Logging System<br/>logger.py]
    
    Logger --> Success{Success?}
    
    Success -->|Yes| Display1[Display Success<br/>Rich UI with Stats]
    Success -->|No| Display2[Display Error<br/>Detailed Error Message]
    
    Display1 --> End2([Download Complete])
    Display2 --> End2
    
    style Start fill:#4CAF50,stroke:#2E7D32,stroke-width:3px,color:#fff
    style CLI fill:#2196F3,stroke:#1565C0,stroke-width:2px,color:#fff
    style Download fill:#FF9800,stroke:#E65100,stroke-width:2px,color:#fff
    style FFmpegVideo fill:#9C27B0,stroke:#6A1B9A,stroke-width:2px,color:#fff
    style FFmpegAudio fill:#9C27B0,stroke:#6A1B9A,stroke-width:2px,color:#fff
    style Metadata fill:#00BCD4,stroke:#006064,stroke-width:2px,color:#fff
    style End2 fill:#4CAF50,stroke:#2E7D32,stroke-width:3px,color:#fff
```

### Component Breakdown

```mermaid
graph LR
    A[ultimate_downloader.py<br/>Main CLI Application] --> B[ui_components.py<br/>Rich UI Interface]
    A --> C[generic_downloader.py<br/>Generic Download Handler]
    A --> D[youtube_scorer.py<br/>YouTube Match Scoring]
    A --> E[utils.py<br/>Utility Functions]
    A --> F[logger.py<br/>Logging System]
    A --> G[config.json<br/>Configuration]
    
    B --> H[Rich Library<br/>Progress Bars<br/>Panels & Tables]
    C --> I[yt-dlp<br/>1000+ Platform Support]
    D --> J[spotdl<br/>Spotify Integration]
    E --> K[FFmpeg<br/>Media Processing]
    F --> L[Log Files<br/>~/Downloads/logs/]
    
    style A fill:#2196F3,stroke:#1565C0,stroke-width:3px,color:#fff
    style B fill:#4CAF50,stroke:#2E7D32,stroke-width:2px,color:#fff
    style C fill:#FF9800,stroke:#E65100,stroke-width:2px,color:#fff
    style I fill:#9C27B0,stroke:#6A1B9A,stroke-width:2px,color:#fff
    style K fill:#E91E63,stroke:#880E4F,stroke-width:2px,color:#fff
```

### Download Process Flow

```mermaid
sequenceDiagram
    participant User
    participant CLI
    participant URLParser
    participant PlatformHandler
    participant yt-dlp
    participant FFmpeg
    participant FileSystem
    
    User->>CLI: Execute: umd <URL>
    CLI->>URLParser: Validate & Parse URL
    URLParser-->>CLI: URL Info & Platform
    
    CLI->>PlatformHandler: Route to Handler
    PlatformHandler->>yt-dlp: Extract Media Info
    yt-dlp-->>PlatformHandler: Available Formats
    
    PlatformHandler->>User: Display Quality Options
    User->>PlatformHandler: Select Quality/Format
    
    PlatformHandler->>yt-dlp: Download Media
    yt-dlp->>FileSystem: Save Raw Media
    
    alt Processing Required
        PlatformHandler->>FFmpeg: Convert/Process
        FFmpeg->>FileSystem: Save Processed
    end
    
    PlatformHandler->>FileSystem: Embed Metadata
    FileSystem-->>PlatformHandler: Complete
    
    PlatformHandler-->>CLI: Download Status
    CLI-->>User: Display Success ✓
```

---

## 🚀 How I Created It

This project was built through careful planning, iterative development, and community feedback. Here's the journey:

### Development Timeline

```mermaid
graph LR
    A[Phase 1: Planning<br/>2024-Q1] --> B[Phase 2: Core Development<br/>2024-Q2]
    B --> C[Phase 3: Feature Expansion<br/>2024-Q3]
    C --> D[Phase 4: Optimization<br/>2024-Q4]
    D --> E[Phase 5: Polish & Release<br/>2025-Q1]
    
    style A fill:#E3F2FD,stroke:#1976D2,stroke-width:2px
    style B fill:#F3E5F5,stroke:#7B1FA2,stroke-width:2px
    style C fill:#E8F5E9,stroke:#388E3C,stroke-width:2px
    style D fill:#FFF3E0,stroke:#F57C00,stroke-width:2px
    style E fill:#FCE4EC,stroke:#C2185B,stroke-width:2px
```

#### 📅 Development Phases

| Phase | Period | Key Achievements |
|-------|--------|------------------|
| **🎯 Phase 1: Planning** | 2024-Q1 | • Research & Ideation<br/>• Studied yt-dlp capabilities<br/>• Analyzed user needs<br/>• Designed architecture |
| **🔨 Phase 2: Core Development** | 2024-Q2 | • Built CLI Interface<br/>• Integrated yt-dlp<br/>• Added FFmpeg support<br/>• Created download manager |
| **🚀 Phase 3: Feature Expansion** | 2024-Q3 | • Added Spotify support<br/>• Implemented metadata embedding<br/>• Built Rich UI interface<br/>• Added batch downloads |
| **⚡ Phase 4: Optimization** | 2024-Q4 | • Parallel downloads<br/>• Error handling<br/>• Installation scripts<br/>• Cross-platform support |
| **✨ Phase 5: Polish & Release** | 2025-Q1 | • Documentation<br/>• Testing & bug fixes<br/>• Public release<br/>• Community feedback |

### Technology Stack Decision Process

```mermaid
mindmap
  root((Ultimate Media<br/>Downloader))
    Core Technologies
      Python 3.9+
        Easy to maintain
        Rich ecosystem
        Cross-platform
      yt-dlp
        1000+ platforms
        Active development
        Robust extraction
      FFmpeg
        Industry standard
        Format conversion
        Metadata support
    
    User Interface
      Rich Library
        Beautiful CLI
        Progress tracking
        Color formatting
      Interactive Mode
        Beginner friendly
        Step-by-step
      Non-Interactive
        Automation ready
        Batch processing
    
    Architecture Choices
      Modular Design
        Easy to extend
        Maintainable code
        Clear separation
      Error Handling
        Comprehensive logging
        User-friendly messages
        Graceful failures
      Performance
        Concurrent downloads
        Optimized batching
        Resume support
    
    Distribution
      pipx Installation
        No venv needed
        Global command
        Clean install
      Cross-platform
        macOS support
        Linux support
        Windows support
      Package Management
        setup.py
        requirements.txt
        Automated scripts
```

### Key Development Decisions

```mermaid
flowchart LR
    A[Design Goals] --> B{Priority Decision}
    
    B -->|Ease of Use| C[Single Command<br/>Installation]
    B -->|Flexibility| D[Multiple Platform<br/>Support]
    B -->|Performance| E[Concurrent<br/>Downloads]
    B -->|Quality| F[High Quality<br/>Media]
    
    C --> G[Implementation:<br/>pipx + scripts]
    D --> H[Implementation:<br/>yt-dlp integration]
    E --> I[Implementation:<br/>asyncio/threading]
    F --> J[Implementation:<br/>FFmpeg processing]
    
    G --> K[Result:<br/>umd command globally]
    H --> L[Result:<br/>1000+ platforms]
    I --> M[Result:<br/>5x faster batches]
    J --> N[Result:<br/>4K/8K + metadata]
    
    style A fill:#2196F3,stroke:#1565C0,stroke-width:3px,color:#fff
    style C fill:#4CAF50,stroke:#2E7D32,stroke-width:2px,color:#fff
    style D fill:#4CAF50,stroke:#2E7D32,stroke-width:2px,color:#fff
    style E fill:#4CAF50,stroke:#2E7D32,stroke-width:2px,color:#fff
    style F fill:#4CAF50,stroke:#2E7D32,stroke-width:2px,color:#fff
    style K fill:#FF9800,stroke:#E65100,stroke-width:2px,color:#fff
    style L fill:#FF9800,stroke:#E65100,stroke-width:2px,color:#fff
    style M fill:#FF9800,stroke:#E65100,stroke-width:2px,color:#fff
    style N fill:#FF9800,stroke:#E65100,stroke-width:2px,color:#fff
```

### Project Structure Evolution

```mermaid
graph TB
    subgraph "Initial Structure"
        A1[Simple Script<br/>single_file.py]
    end
    
    subgraph "Modular Refactor"
        B1[ultimate_downloader.py]
        B2[utils.py]
        B3[logger.py]
    end
    
    subgraph "Feature Expansion"
        C1[ultimate_downloader.py<br/>Main CLI]
        C2[generic_downloader.py<br/>Platform Handler]
        C3[youtube_scorer.py<br/>Spotify Matching]
        C4[ui_components.py<br/>Rich UI]
        C5[utils.py<br/>Helpers]
        C6[logger.py<br/>Logging]
        C7[config.json<br/>Settings]
    end
    
    subgraph "Distribution Ready"
        D1[Core Modules]
        D2[Setup & Install<br/>setup.py<br/>scripts/]
        D3[Documentation<br/>*.md files]
        D4[Tests & CI/CD]
    end
    
    A1 --> B1
    B1 --> C1
    B2 --> C5
    B3 --> C6
    C1 --> D1
    C2 --> D1
    C3 --> D1
    C4 --> D1
    C5 --> D1
    C6 --> D1
    C7 --> D1
    D1 --> D2
    D1 --> D3
    D1 --> D4
    
    style A1 fill:#f9f9f9,stroke:#999
    style C1 fill:#2196F3,stroke:#1565C0,stroke-width:2px,color:#fff
    style C2 fill:#4CAF50,stroke:#2E7D32,stroke-width:2px,color:#fff
    style C3 fill:#FF9800,stroke:#E65100,stroke-width:2px,color:#fff
    style C4 fill:#9C27B0,stroke:#6A1B9A,stroke-width:2px,color:#fff
    style D1 fill:#00BCD4,stroke:#006064,stroke-width:3px,color:#fff
```

### Lessons Learned & Best Practices

1. **User-Centric Design**: Always prioritize ease of use over technical complexity
2. **Modular Architecture**: Separation of concerns makes maintenance easier
3. **Error Handling**: Comprehensive error messages save hours of support time
4. **Documentation**: Good docs are as important as good code
5. **Community Feedback**: Early user feedback shaped many key features
6. **Testing**: Platform diversity requires extensive real-world testing
7. **Performance**: Concurrent downloads were a game-changer for batch operations

---

## Use Cases

### For Music Lovers
```bash
# Download Spotify playlist as MP3 with metadata
umd "SPOTIFY_PLAYLIST_URL" --audio-only --format mp3 --embed-metadata

# Download album in FLAC quality
umd "ALBUM_URL" --audio-only --format flac
```

### For Content Creators
```bash
# Download 4K video for editing
umd "URL" --quality 4k --format mp4

# Download entire channel
umd "CHANNEL_URL" --playlist
```

### For Researchers
```bash
# Batch download educational content
umd --batch-file lectures.txt --quality 1080p

# Download with subtitles
umd "URL" --write-subs --sub-lang en
```

### For Automation
```bash
# Automated batch download (non-interactive)
umd --batch-file daily_downloads.txt --no-interactive --optimized-batch
```

---

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

### Development Setup

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/ULTIMATE-MEDIA-DOWNLOADER.git
cd ULTIMATE-MEDIA-DOWNLOADER

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
pytest
```

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## ️ Disclaimer

This tool is for personal use only. Users are responsible for complying with copyright laws and terms of service of the platforms they download from. The developers assume no liability for misuse of this software.

**Please respect:**
- Copyright laws and fair use policies
- Platform terms of service
- Content creator rights
- Regional restrictions and DRM

---

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

## Roadmap

- [ ] GUI interface
- [ ] Browser extension
- [ ] Docker support
- [ ] Multi-language support
- [ ] Advanced scheduling
- [ ] Cloud storage integration
- [ ] Mobile app

---

## Statistics

- **Lines of Code**: 5000+
- **Supported Platforms**: 1000+
- **Active Users**: Growing
- **Last Updated**: October 2025

---

<div align="center">

**Made with ️ by [NK2552003](https://github.com/NK2552003)**

⭐ Star this repository if you find it useful!

[Report Bug](https://github.com/NK2552003/ULTIMATE-MEDIA-DOWNLOADER/issues) • [Request Feature](https://github.com/NK2552003/ULTIMATE-MEDIA-DOWNLOADER/issues) • [Documentation](docs/DOCUMENTATION_SUMMARY.md)

</div>
