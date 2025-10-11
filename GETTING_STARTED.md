# Getting Started - Navigation Guide

## Quick Links

| What do you want to do? | Go here |
|-------------------------|---------|
| **Install the app** | [Installation Guide](INSTALL.md) or run `./scripts/install.sh` |
| **Quick start** | [Quick Start Guide](QUICKSTART.md) |
| **See what's new** | [What's New](WHATS_NEW.md) |
| **Read full documentation** | [User Guide](docs/USER_GUIDE.md) |
| **Understand the code** | [Architecture](docs/ARCHITECTURE.md) |
| **Report a bug** | [GitHub Issues](https://github.com/NK2552003/ULTIMATE-MEDIA-DOWNLOADER/issues) |
| **Contribute** | [Contributing Guide](CONTRIBUTING.md) |

---

## For First-Time Users

### Step 1: Install
```bash
git clone https://github.com/NK2552003/ULTIMATE-MEDIA-DOWNLOADER.git
cd ULTIMATE-MEDIA-DOWNLOADER
./scripts/install.sh
```

### Step 2: Try it out
```bash
umd   # Interactive mode - easiest!
```

### Step 3: Learn more
Read the [Quick Start Guide](QUICKSTART.md) for common examples.

---

## Documentation Structure

```
📚 Documentation
│
├── 📄 README.md                 ← Start here! Main overview
├── 📄 QUICKSTART.md            ← Quick reference for commands
├── 📄 INSTALL.md               ← Installation instructions
├── 📄 WHATS_NEW.md             ← Latest changes & features
│
└── 📁 docs/
    ├── 📄 INDEX.md             ← Documentation hub
    ├── 📄 USER_GUIDE.md        ← Complete user manual
    ├── 📄 API_REFERENCE.md     ← API documentation
    ├── 📄 ARCHITECTURE.md      ← Technical deep dive
    ├── 📄 PROJECT_STRUCTURE.md ← File organization
    │
    └── 📁 guides/
        └── YOUTUBE_MIX_FIX.md  ← Troubleshooting guides
```

---

## Common Tasks

### I want to...

#### Download a YouTube video
```bash
umd "https://youtube.com/watch?v=VIDEO_ID"
```
 More: [QUICKSTART.md](QUICKSTART.md#basic-commands)

#### Download audio only
```bash
umd "URL" --audio-only --format mp3
```
 More: [QUICKSTART.md](QUICKSTART.md#download-audio)

#### Download a playlist
```bash
umd "PLAYLIST_URL"
```
 More: [docs/USER_GUIDE.md](docs/USER_GUIDE.md#playlist-downloads)

#### Batch download multiple URLs
```bash
umd --batch-file urls.txt
```
 More: [docs/USER_GUIDE.md](docs/USER_GUIDE.md#batch-downloads)

#### Troubleshoot an issue
 See: [docs/guides/](docs/guides/) or [GitHub Issues](https://github.com/NK2552003/ULTIMATE-MEDIA-DOWNLOADER/issues)

---

## For Developers

### Understanding the Code

1. **[Architecture](docs/ARCHITECTURE.md)** - System design & components
2. **[API Reference](docs/API_REFERENCE.md)** - Function documentation
3. **[Project Structure](docs/PROJECT_STRUCTURE.md)** - File organization
4. **[Flowcharts](docs/FLOWCHARTS.md)** - Process diagrams

### Contributing

1. Read [CONTRIBUTING.md](CONTRIBUTING.md)
2. Check [open issues](https://github.com/NK2552003/ULTIMATE-MEDIA-DOWNLOADER/issues)
3. Fork, code, and submit a PR!

### Key Files

| File | Purpose |
|------|---------|
| `ultimate_downloader.py` | Main application (6800+ lines) |
| `utils.py` | Utility functions |
| `ui_components.py` | UI components & Rich formatting |
| `logger.py` | Logging utilities |
| `setup.py` | Package configuration |

---

## Learning Path

### Beginner
1. [README.md](README.md) - Overview
2. [INSTALL.md](INSTALL.md) - Installation
3. [QUICKSTART.md](QUICKSTART.md) - Basic usage

### Intermediate
4. [docs/USER_GUIDE.md](docs/USER_GUIDE.md) - Comprehensive guide
5. [WHATS_NEW.md](WHATS_NEW.md) - New features

### Advanced
6. [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) - Technical details
7. [docs/API_REFERENCE.md](docs/API_REFERENCE.md) - API docs
8. [CONTRIBUTING.md](CONTRIBUTING.md) - Contribute code

---

## Getting Help

### Something not working?

1. **Check the docs**: [docs/USER_GUIDE.md](docs/USER_GUIDE.md)
2. **Search issues**: [GitHub Issues](https://github.com/NK2552003/ULTIMATE-MEDIA-DOWNLOADER/issues)
3. **Ask for help**: [Create a new issue](https://github.com/NK2552003/ULTIMATE-MEDIA-DOWNLOADER/issues/new)

### Common Issues

- **Command not found**: See [INSTALL.md#troubleshooting](INSTALL.md#troubleshooting)
- **FFmpeg error**: See [INSTALL.md#requirements](INSTALL.md#requirements)
- **Download fails**: See [docs/guides/](docs/guides/)

---

## Quick Commands Reference

```bash
# Interactive mode (easiest)
umd

# Download video
umd "URL"

# Download audio
umd "URL" -a

# Download playlist
umd "PLAYLIST_URL"

# Show help
umd --help

# Show supported platforms
umd --list-platforms

# Get media info
umd "URL" --info

# Batch download
umd --batch-file urls.txt
```

---

## Project Organization

```
ULTIMATE-MEDIA-DOWNLOADER/
├── 📄 Core Application Files (*.py)
├── 📄 Documentation (*.md)
├── 📁 scripts/          → Installation scripts
├── 📁 docs/             → Full documentation
├── 📁 homebrew/         → Homebrew formula
└── 📁 demo_video/       → Demo videos
```

**Clean & organized** 

---

## Ready to Start?

### Option 1: Quick Install
```bash
./scripts/install.sh
```

### Option 2: Interactive Mode
```bash
umd
```

### Option 3: Read First
[ README.md](README.md)

---

<div align="center">

**Questions?** Check the [docs/](docs/) folder or [open an issue](https://github.com/NK2552003/ULTIMATE-MEDIA-DOWNLOADER/issues)

**Happy Downloading!** 

[⬆ Back to Top](#-getting-started---navigation-guide)

</div>
