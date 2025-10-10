# Installation Guide - Ultimate Media Downloader

> 📖 **New!** For comprehensive installation instructions, see [INSTALLATION_GUIDE.md](INSTALLATION_GUIDE.md)

## Quick Installation (Recommended)

Install from GitHub in just 2 commands:

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

This will:
- ✅ Install the package with all dependencies
- ✅ Create the `umd` command for easy access
- ✅ Set up the downloads directory at `~/Downloads/UltimateDownloader`
- ✅ No virtual environment needed!
- ✅ Works globally from any directory

## Usage After Installation

Once installed, you can use the downloader from anywhere with just one word:

```bash
umd <URL>
```

### Examples:

```bash
# Interactive mode (easiest)
umd

# Download a video
umd "https://www.youtube.com/watch?v=VIDEO_ID"

# Download audio only
umd "https://www.youtube.com/watch?v=VIDEO_ID" --audio-only

# Download with specific quality
umd "https://www.youtube.com/watch?v=VIDEO_ID" --quality 1080p

# Download audio in MP3 format
umd "https://www.youtube.com/watch?v=VIDEO_ID" --audio-only --format mp3

# Download playlist
umd "https://www.youtube.com/playlist?list=PLAYLIST_ID"

# Show all options
umd --help
```

## Download Location

All files will be automatically downloaded to:
```
~/Downloads/UltimateDownloader/
```

You can specify a different location with the `--output` flag:
```bash
umd <URL> --output /path/to/your/folder
```

## Homebrew Installation (Alternative - macOS)

For Homebrew users, you can create a local tap:

```bash
# Create a local Homebrew tap
mkdir -p $(brew --repository)/Library/Taps/homebrew/homebrew-local
cp ultimate-downloader.rb $(brew --repository)/Library/Taps/homebrew/homebrew-local/

# Install via Homebrew
brew install ultimate-downloader
```

Then use it with:
```bash
umd <URL>
```

## Uninstallation

To uninstall the package:

```bash
./uninstall.sh
```

Or manually:
```bash
pip3 uninstall ultimate-downloader
```

Your downloaded files will NOT be deleted.

## Requirements

- Python 3.9 or higher
- FFmpeg (for audio conversion)
  - macOS: `brew install ffmpeg`
  - Linux: `sudo apt install ffmpeg`
  - Windows: Download from https://ffmpeg.org/

## Troubleshooting

### Command not found: umd

If you get "command not found" after installation, add Python's bin directory to your PATH:

**macOS:**
```bash
export PATH="$PATH:$HOME/Library/Python/3.x/bin"
echo 'export PATH="$PATH:$HOME/Library/Python/3.x/bin"' >> ~/.zshrc
source ~/.zshrc
```

**Linux:**
```bash
export PATH="$PATH:$HOME/.local/bin"
echo 'export PATH="$PATH:$HOME/.local/bin"' >> ~/.bashrc
source ~/.bashrc
```

### Permission denied

If you get permission errors:
```bash
chmod +x install.sh
./install.sh
```

### FFmpeg not found

Install FFmpeg:
- macOS: `brew install ffmpeg`
- Ubuntu/Debian: `sudo apt install ffmpeg`
- CentOS/RHEL: `sudo yum install ffmpeg`

## Features

- ✅ **1000+ Platforms**: YouTube, Spotify, Instagram, TikTok, SoundCloud, and more
- ✅ **No Virtual Environment**: Runs directly after installation
- ✅ **Single Command**: Just type `umd` from anywhere
- ✅ **Automatic Downloads Folder**: Saves to `~/Downloads/UltimateDownloader`
- ✅ **High Quality**: Download videos up to 4K, audio up to FLAC
- ✅ **Batch Downloads**: Download multiple URLs at once
- ✅ **Metadata Embedding**: Automatic metadata and thumbnail embedding
- ✅ **Interactive Mode**: Guided experience for beginners

## Support

For issues, feature requests, or questions:
- GitHub: https://github.com/NK2552003/ULTIMATE-MEDIA-DOWNLOADER
- Documentation: See `docs/` folder

## License

MIT License - see LICENSE file for details
