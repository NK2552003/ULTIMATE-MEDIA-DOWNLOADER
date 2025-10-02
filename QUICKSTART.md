# Quick Start Guide

Welcome to **Ultimate Media Downloader**! This guide will get you up and running in minutes.

## 🚀 Installation (60 seconds)

### One-Command Setup

```bash
# Clone and setup in one go
git clone https://github.com/yourusername/ultimate-downloader.git && \
cd ultimate-downloader && \
./setup.sh
```

### Manual Setup

```bash
# 1. Clone the repository
git clone https://github.com/yourusername/ultimate-downloader.git
cd ultimate-downloader

# 2. Run setup script
chmod +x setup.sh
./setup.sh

# 3. Activate environment
source activate_env.sh
```

## 💡 First Use (Interactive Mode)

The easiest way to start:

```bash
python ultimate_downloader.py
```

Then simply paste any URL when prompted!

## 📝 Common Commands

### Download a Video
```bash
python ultimate_downloader.py "https://www.youtube.com/watch?v=VIDEO_ID"
```

### Download Audio (MP3)
```bash
python ultimate_downloader.py "URL" --audio-only --format mp3
```

### Download Lossless Audio (FLAC)
```bash
python ultimate_downloader.py "URL" --audio-only --format flac
```

### Download a Playlist
```bash
python ultimate_downloader.py "PLAYLIST_URL" --playlist
```

### Download Spotify Track
```bash
python ultimate_downloader.py "https://open.spotify.com/track/TRACK_ID" --audio-only
```

### Download with Specific Quality
```bash
python ultimate_downloader.py "URL" --quality 1080p
```

## 🎯 Quick Examples

### Example 1: Music Video to MP3
```bash
python ultimate_downloader.py \
  "https://www.youtube.com/watch?v=dQw4w9WgXcQ" \
  --audio-only \
  --format mp3 \
  --embed-metadata \
  --embed-thumbnail
```

### Example 2: Playlist to Audio
```bash
python ultimate_downloader.py \
  "https://www.youtube.com/playlist?list=PLAYLIST_ID" \
  --playlist \
  --audio-only \
  --format mp3 \
  --max-downloads 10
```

### Example 3: Multiple URLs
```bash
# Create a file with URLs
cat > urls.txt <<EOF
https://www.youtube.com/watch?v=VIDEO1
https://www.youtube.com/watch?v=VIDEO2
https://soundcloud.com/artist/track
EOF

# Download all
python ultimate_downloader.py \
  --batch-file urls.txt \
  --audio-only \
  --optimized-batch
```

## 🔧 Troubleshooting

### FFmpeg Not Found
```bash
# macOS
brew install ffmpeg

# Ubuntu
sudo apt-get install ffmpeg

# Windows
choco install ffmpeg
```

### Module Not Found
```bash
# Activate environment first
source activate_env.sh

# Then reinstall
pip install -r requirements.txt
```

### Slow Downloads
```bash
# Use optimized batch mode
python ultimate_downloader.py \
  --batch-file urls.txt \
  --optimized-batch \
  --max-concurrent 5
```

## 📚 Learn More

- Full documentation: [DOCUMENTATION.md](DOCUMENTATION.md)
- All features: [README.md](README.md)
- Contribute: [CONTRIBUTING.md](CONTRIBUTING.md)

## ❓ Get Help

```bash
# Show all options
python ultimate_downloader.py --help

# List supported platforms
python ultimate_downloader.py --list-platforms

# Check if URL is supported
python ultimate_downloader.py "URL" --check-support
```

## 🎉 You're Ready!

Start downloading with:
```bash
python ultimate_downloader.py
```

Enjoy! 🚀
