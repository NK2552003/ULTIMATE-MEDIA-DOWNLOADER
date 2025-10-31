"""
Command-line argument parser for Ultimate Media Downloader
This module contains all argument parsing and configuration
"""

import argparse
from ui_components import Icons

__version__ = "2.0.0"


def create_argument_parser():
    """Create and configure the argument parser for the application"""
    parser = argparse.ArgumentParser(
        description=f"{Icons.get('video')} Ultimate Multi-Platform Media Downloader\n\nA powerful, feature-rich downloader supporting many platforms including YouTube, Spotify, Instagram, TikTok, SoundCloud, Apple Music, and more!",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
{'═'*79}
{Icons.get('book')} USAGE EXAMPLES
{'═'*79}

{Icons.get('target')} BASIC USAGE:
  • Interactive Mode (Recommended for Beginners):
    python ultimate_downloader.py

  • Download Single Video/Audio:
    python ultimate_downloader.py "https://www.youtube.com/watch?v=VIDEO_ID"

  • Get Media Information:
    python ultimate_downloader.py "URL" --info --show-formats

{Icons.get('audio')} AUDIO DOWNLOADS:
  • High-Quality MP3 (320kbps):
    python ultimate_downloader.py "URL" --audio-only --format mp3

  • Lossless FLAC Audio:
    python ultimate_downloader.py "URL" --audio-only --format flac

  • Download Spotify Track (via YouTube Search):
    python ultimate_downloader.py "https://open.spotify.com/track/TRACK_ID" \\
        --audio-only --format mp3

{Icons.get('video')} VIDEO DOWNLOADS:
  • Specific Quality:
    python ultimate_downloader.py "URL" --quality 1080p

  • Best Available Quality:
    python ultimate_downloader.py "URL" --quality best --format mp4

  • Custom Format (Advanced):
    python ultimate_downloader.py "URL" \\
        --custom-format "bestvideo[height<=720]+bestaudio[ext=m4a]"

{Icons.get('playlist')} PLAYLIST DOWNLOADS:
  • Download Entire Playlist (Default for playlist URLs):
    python ultimate_downloader.py "PLAYLIST_URL"

  • Download Only Single Video from Playlist:
    python ultimate_downloader.py "PLAYLIST_URL" --no-playlist

  • Interactive Playlist Download:
    python ultimate_downloader.py "PLAYLIST_URL" --playlist

  • Download First 10 Videos (Non-Interactive):
    python ultimate_downloader.py "PLAYLIST_URL" --playlist \\
        --max-downloads 10 --no-interactive

  • Download Specific Range:
    python ultimate_downloader.py "PLAYLIST_URL" --playlist \\
        --start-index 5 --max-downloads 15

{Icons.get('package')} BATCH DOWNLOADS:
  • Download Multiple URLs from File:
    python ultimate_downloader.py --batch-file urls.txt --audio-only

  • Optimized Parallel Batch Download:
    python ultimate_downloader.py --batch-file urls.txt \\
        --optimized-batch --max-concurrent 5

{Icons.get('art')} ADVANCED FEATURES:
  • Embed Metadata & Thumbnails:
    python ultimate_downloader.py "URL" --audio-only --format mp3 \\
        --embed-metadata --embed-thumbnail

  • Download with Custom Output Directory:
    python ultimate_downloader.py "URL" --output /path/to/downloads

{'═'*79}
{Icons.get('world')} SUPPORTED PLATFORMS
{'═'*79}

  {Icons.get('completed')} YouTube (Videos, Playlists, Live Streams)
  {Icons.get('completed')} Spotify (Tracks, Albums, Playlists - via YouTube search)
  {Icons.get('completed')} Apple Music (Tracks, Albums - via YouTube search)
  {Icons.get('completed')} SoundCloud (Tracks, Playlists, User Uploads)
  {Icons.get('completed')} Instagram (Videos, Reels, IGTV)
  {Icons.get('completed')} TikTok (Videos, User Content)
  {Icons.get('completed')} Twitter/X (Videos from Tweets)
  {Icons.get('completed')} Facebook (Videos, Live Streams)
  {Icons.get('completed')} Vimeo (Videos, Private Content)
  {Icons.get('completed')} Twitch (VODs, Clips, Live Streams)
  {Icons.get('completed')} And many more platforms!

  Use --list-platforms to see all supported sites
  Use --check-support <URL> to verify URL compatibility

{'═'*79}
{Icons.get('tip')} TIPS & BEST PRACTICES
{'═'*79}

  • For best audio quality, use: --audio-only --format flac
  • For universal compatibility, use: --format mp4 (video) or --format mp3 (audio)
  • Use interactive mode for guided downloading experience
  • Batch downloads support parallel processing with --optimized-batch
  • Always check available formats with --show-formats before downloading

{'═'*79}
{Icons.get('book')} For more information, visit: https://github.com/yt-dlp/yt-dlp
Report issues: Create an issue on the GitHub repository
{'═'*79}
        """
    )

    # Required positional argument
    parser.add_argument('url', nargs='?', help='Media URL to download (if not provided, starts interactive mode)')

    # Video quality options
    parser.add_argument('-q', '--quality', default='best',
                       choices=['best', 'worst', '4k', '2160p', '1440p', '1080p', '720p', '480p', '360p'],
                       help='Video quality (default: best)')

    # Audio extraction options
    parser.add_argument('-a', '--audio-only', action='store_true',
                       help='Download audio only')

    # Format options
    parser.add_argument('-f', '--format', help='Output format (mp4, mp3, mkv, wav, flac, etc.)')

    # Output directory
    parser.add_argument('-o', '--output', default=None,
                       help='Output directory (default: ~/Downloads/UltimateDownloader)')

    # Playlist options
    parser.add_argument('-p', '--playlist', action='store_true',
                       help='Download playlist (with interactive options by default)')
    parser.add_argument('--no-playlist', action='store_true',
                       help='Download only single video from playlist URL')
    parser.add_argument('-m', '--max-downloads', type=int,
                       help='Maximum number of videos to download from playlist')
    parser.add_argument('-s', '--start-index', type=int, default=1,
                       help='Start index for playlist download (default: 1)')

    # Information options
    parser.add_argument('-i', '--info', action='store_true',
                       help='Show media info without downloading')
    parser.add_argument('--show-formats', action='store_true',
                       help='Show all available formats and qualities')

    # Format customization
    parser.add_argument('--custom-format', help='Custom format selector for advanced users')

    # Timeout and support options
    parser.add_argument('--timeout', type=int, default=60,
                       help='Timeout for operations in seconds (default: 60)')
    parser.add_argument('--check-support', action='store_true',
                       help='Check if URL is supported')
    parser.add_argument('--list-platforms', action='store_true',
                       help='List all supported platforms')

    # Interaction modes
    parser.add_argument('--interactive', action='store_true',
                       help='Force interactive mode even when URL is provided')
    parser.add_argument('--no-interactive', action='store_true',
                       help='Disable interactive prompts (use provided args only)')

    # Enhanced audio quality options
    parser.add_argument('--audio-format',
                       choices=['mp3', 'flac', 'opus', 'm4a', 'aac', 'wav'],
                       help='Audio format (auto-selects best quality for format)')
    parser.add_argument('--audio-quality',
                       choices=['best', 'high', 'medium', 'low'],
                       default='best',
                       help='Audio quality level (default: best)')
    parser.add_argument('--audio-language', '--audio-lang',
                       help='Preferred audio language code (e.g., en, es, fr) for videos with multiple audio tracks')

    # Performance and metadata options
    parser.add_argument('--max-concurrent', type=int, default=3,
                       help='Maximum concurrent downloads for batch operations (default: 3)')
    parser.add_argument('--embed-metadata', action='store_true',
                       help='Embed metadata and cover art in audio files')
    parser.add_argument('--embed-thumbnail', action='store_true',
                       help='Embed thumbnail/cover art in audio files')
    parser.add_argument('--prefer-artist-art', action='store_true',
                       help='Try to get artist cover art instead of video thumbnail')

    # Batch download options
    parser.add_argument('--batch-file',
                       help='File containing URLs to download (one per line)')
    parser.add_argument('--optimized-batch', action='store_true',
                       help='Use optimized parallel batch downloading')

    # Version and debug arguments
    parser.add_argument('-v', '--version', action='version',
                       version=f'Ultimate Media Downloader v{__version__}',
                       help='Show program version and exit')
    parser.add_argument('--verbose', action='store_true',
                       help='Enable verbose output for debugging')

    return parser


def parse_arguments():
    """Parse and return command-line arguments"""
    parser = create_argument_parser()
    return parser.parse_args()
