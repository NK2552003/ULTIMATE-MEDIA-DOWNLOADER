# Troubleshooting Guide

This guide helps you solve common problems you might encounter when using the Ultimate Media Downloader.

## Table of Contents

1. [Installation Issues](#installation-issues)
2. [Download Issues](#download-issues)
3. [Platform-Specific Issues](#platform-specific-issues)
   - [YouTube Age-Restricted Videos](#youtube-age-restricted-videos)
   - [Spotify Downloads Not Working](#spotify-downloads-not-working)
   - [Instagram Downloads Failing](#instagram-downloads-failing)
   - [TikTok Videos Not Downloading](#tiktok-videos-not-downloading)
   - [Adult Site Downloads Failing](#adult-site-downloads-failing-eporner-hqporner-beeg)
   - [Twitter/X Videos Failing](#twitterx-videos-failing)
   - [4K Wallpapers Issues](#4k-wallpapers-issues)
4. [Audio and Video Issues](#audio-and-video-issues)
5. [Performance Issues](#performance-issues)
6. [Error Messages](#error-messages)
7. [Getting Help](#getting-help)

---

## Installation Issues

### Python Not Found

**Symptom**: Running `python3 --version` shows "command not found"

**Solution**:

On macOS:

```bash
brew install python@3.11
```

On Ubuntu/Debian:

```bash
sudo apt install python3
```

On Windows: Download and install from [python.org](https://www.python.org/downloads/)

---

### Command "umd" Not Found After Installation

**Symptom**: After running the install script, `umd` command is not recognized

**Solution**:

The Python scripts directory is not in your PATH.

On macOS (zsh):

```bash
echo 'export PATH="$PATH:$HOME/Library/Python/3.11/bin"' >> ~/.zshrc
source ~/.zshrc
```

On Linux (bash):

```bash
echo 'export PATH="$PATH:$HOME/.local/bin"' >> ~/.bashrc
source ~/.bashrc
```

On Windows: Restart your terminal or computer after installation.

---

### Permission Denied on Linux/macOS

**Symptom**: Running `./scripts/install.sh` shows "Permission denied"

**Solution**:

```bash
chmod +x scripts/install.sh
./scripts/install.sh
```

---

### pip Install Fails with SSL Error

**Symptom**: pip shows SSL certificate verification errors

**Solution**:

```bash
pip3 install --upgrade certifi
pip3 install --trusted-host pypi.org --trusted-host files.pythonhosted.org -r requirements.txt
```

---

### Missing Dependencies

**Symptom**: Import errors when running the application

**Solution**:

```bash
pip3 install -r requirements.txt
```

If specific packages fail, install them individually:

```bash
pip3 install yt-dlp rich mutagen
```

---

## Download Issues

### Video Not Downloading

**Symptom**: Download starts but produces no file

**Possible Causes and Solutions**:

1. **URL is incorrect**: Double-check the URL
2. **Content is private**: Use cookies for authenticated access
3. **Geographic restriction**: Try using a proxy or VPN
4. **Site changed**: Update yt-dlp with `pip3 install -U yt-dlp`

---

### Download Stuck at 0%

**Symptom**: Progress bar shows 0% and does not move

**Solutions**:

1. Check your internet connection
2. Try a different quality: `umd "URL" --quality 720p`
3. Use verbose mode to see details: `umd --verbose "URL"`
4. The server might be slow, wait a bit longer

---

### "Unable to Extract" Error

**Symptom**: Error message about unable to extract video

**Solutions**:

1. Update yt-dlp:

   ```bash
   pip3 install -U yt-dlp
   ```

2. Try the generic downloader:

   ```bash
   umd "URL" --verbose
   ```

3. Check if the URL is still valid (video might be deleted)

---

### Download Speed is Very Slow

**Solutions**:

1. Try a different quality (lower quality downloads faster)
2. Check if your ISP is throttling
3. Try at a different time (less server load)
4. Use a VPN or proxy

---

### Resume Not Working

**Symptom**: Downloads start from beginning after interruption

**Solution**:

Make sure you are downloading to the same directory. The application looks for partial files in the output directory.

---

## Platform-Specific Issues

### YouTube Age-Restricted Videos

**Symptom**: Cannot download age-restricted content

**Solution**: Use cookies from a logged-in browser session

1. Install a browser extension to export cookies
2. Export cookies from YouTube
3. Use the cookies file:

   Edit `config.json`:

   ```json
   {
       "authentication": {
           "youtube": {
               "cookies_file": "/path/to/cookies.txt"
           }
       }
   }
   ```

---

### Spotify Downloads Not Working

**Symptom**: Spotify URLs fail or download wrong song

**Solutions**:

1. The application searches YouTube for the song. If it finds the wrong one, try with more specific search:

   ```bash
   umd "https://open.spotify.com/track/xxx" --verbose
   ```

2. Set up Spotify API credentials for better metadata:

   ```bash
   export SPOTIFY_CLIENT_ID="your_id"
   export SPOTIFY_CLIENT_SECRET="your_secret"
   ```

---

### Instagram Downloads Failing

**Symptom**: Instagram posts return errors

**Solutions**:

1. Instagram requires login for some content. Use cookies.
2. Private accounts need authentication.
3. Try updating yt-dlp:

   ```bash
   pip3 install -U yt-dlp
   ```

---

### TikTok Videos Not Downloading

**Symptom**: TikTok URLs fail

**Solutions**:

1. Make sure the URL is the full URL (not shortened)
2. Try using the mobile URL format: `https://m.tiktok.com/...`
3. Update yt-dlp:

   ```bash
   pip3 install -U yt-dlp
   ```

4. TikTok frequently changes their site, updates help
5. If SSL errors occur, the handler will automatically try fallback methods

---

### Adult Site Downloads Failing (Eporner, HQPorner, Beeg)

**Symptom**: Adult site URLs return SSL or connection errors

**Solutions**:

1. These handlers have built-in SSL bypass mechanisms
2. Try with verbose mode to see which fallback method works:

   ```bash
   umd "URL" --verbose
   ```

3. If issues persist, ensure you have the latest dependencies:

   ```bash
   pip3 install -U requests urllib3
   ```

4. Some sites may require curl_cffi for better compatibility:

   ```bash
   pip3 install curl_cffi
   ```

---

### Twitter/X Videos Failing

**Symptom**: Twitter video URLs return errors

**Solutions**:

1. Use the full tweet URL, not embedded video URL
2. Some videos require authentication
3. Update yt-dlp

---

### 4K Wallpapers Issues

#### No Wallpapers Found (0 results)

**Symptom**: The handler shows "0 wallpapers found" for a category or search

**Solutions**:

1. The category slug in the URL may have changed. Try browsing via the interactive menu (`umd --wallpaper`) instead of pasting a URL directly.
2. For search, ensure you are using simple keywords (e.g. `anime` not `anime+girl`).
3. The site may be temporarily unavailable. Try again in a few minutes.

#### Cloudflare Challenge / Access Denied

**Symptom**: Wallpaper pages return very short responses or HTML challenge pages

**Root Cause & Fix**: This was a known bug (now fixed in v2.2.1) caused by passing browser emulation arguments to `cloudscraper`. If you still see this, ensure you are on the latest version:

```bash
git pull
pip install -r requirements.txt
```

#### Search Returns Only 24 Results

**Symptom**: Search only ever shows 24 wallpapers regardless of how many you request

**Explanation**: This is a site limitation. 4kwallpapers.com search pages are single-page only — no pagination is available for search results. Use a category or tag browse instead to get more wallpapers.

#### Downloads Fail or Return 404

**Symptom**: Individual wallpaper downloads fail with 404

**Solutions**:

1. The wallpaper may have been removed from the site.
2. Try downloading a different resolution from the same wallpaper.
3. Re-fetch the listing (run the browse flow again) to get fresh links.

#### `wallpaper` / `wp` Command Not Recognized in Interactive Mode

**Symptom**: Typing `wallpaper` in interactive mode shows "URL not recognized"

**Solutions**:

1. Make sure you are on v3.0.0 or later.
2. Verify `four_k_wallpapers_handler.py` exists in the `handlers/` directory.
3. Check for import errors by running `umd --wallpaper` to see if there is a Python error.

---

## Audio and Video Issues

### No Audio in Downloaded Video

**Symptom**: Video plays but has no sound

**Solutions**:

1. The video might have been uploaded without audio
2. Try a different format:

   ```bash
   umd "URL" --format mp4
   ```

3. Make sure FFmpeg is installed:

   ```bash
   ffmpeg -version
   ```

---

### FFmpeg Not Found

**Symptom**: Error about FFmpeg not being installed

**Solution**:

On macOS:

```bash
brew install ffmpeg
```

On Ubuntu/Debian:

```bash
sudo apt install ffmpeg
```

On Windows:

```batch
choco install ffmpeg
```

---

### Audio Quality is Poor

**Solutions**:

1. Use higher quality settings:

   ```bash
   umd "URL" --audio-only --format flac --audio-quality best
   ```

2. The source might not have better quality available
3. Check available formats:

   ```bash
   umd "URL" --show-formats
   ```

---

### Metadata Not Embedded

**Symptom**: Audio files missing artist, title, etc.

**Solution**:

```bash
umd "URL" --audio-only --embed-metadata --embed-thumbnail
```

---

### Cover Art Not Showing

**Symptom**: Audio files have no album art

**Solutions**:

1. Use the embed thumbnail option:

   ```bash
   umd "URL" --audio-only --embed-thumbnail
   ```

2. Make sure Pillow and Mutagen are installed:

   ```bash
   pip3 install Pillow mutagen
   ```

---

## Performance Issues

### High Memory Usage

**Solutions**:

1. Download fewer concurrent items:

   ```bash
   umd --batch-file urls.txt --max-concurrent 2
   ```

2. Download lower quality content

---

### Slow Batch Downloads

**Solutions**:

1. Increase concurrency (if you have bandwidth):

   ```bash
   umd --batch-file urls.txt --optimized-batch --max-concurrent 5
   ```

2. Make sure your internet connection is stable

---

## Error Messages

### "No Video Formats Found"

**Meaning**: The extractor could not find any downloadable video

**Solutions**:

1. The video might be removed or private
2. Geographic restriction
3. Update yt-dlp
4. Try verbose mode for more info

---

### "HTTP Error 403: Forbidden"

**Meaning**: The server rejected the request

**Solutions**:

1. Use cookies for authentication
2. Wait and try later (rate limiting)
3. Use a different IP (proxy/VPN)

---

### "HTTP Error 429: Too Many Requests"

**Meaning**: You have been rate limited

**Solutions**:

1. Wait before trying again
2. Reduce concurrent downloads
3. Use slower download settings

---

### "SSL Certificate Error"

**Meaning**: SSL/TLS verification failed

**Solutions**:

1. The application usually handles this automatically
2. Try:

   ```bash
   pip3 install --upgrade certifi
   ```

---

### "Unsupported URL"

**Meaning**: The URL is not recognized

**Solutions**:

1. Check if the URL is correct
2. Check if the platform is supported:

   ```bash
   umd --list-platforms
   ```

3. Try the generic downloader by just running the command

---

## Getting Help

### Enable Verbose Mode

For detailed output, add `--verbose`:

```bash
umd --verbose "URL"
```

This shows:

- Exact HTTP requests
- Response details
- Error stack traces
- Processing steps

### Check Application Version

```bash
umd --version
```

### Check yt-dlp Version

```bash
pip3 show yt-dlp
```

### Report a Bug

If you cannot solve the issue:

1. Note your operating system and Python version
2. Copy the full error message
3. Note the URL you were trying to download (if not private)
4. Create an issue at: [Issues](https://codeberg.org/nk2552003/umd/issues)

### Update All Dependencies

Sometimes updating fixes issues:

```bash
pip3 install -U yt-dlp
pip3 install -r requirements.txt --upgrade
```

---

## Summary

Most issues can be solved by:

1. Updating yt-dlp and other dependencies
2. Using verbose mode to understand what is happening
3. Checking URL validity and permissions
4. Installing required external tools like FFmpeg

If problems persist, check the issues or create a new one with detailed information about your problem.
