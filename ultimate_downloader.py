#!/usr/bin/env python3
"""
Ultimate Multi-Platform Media Downloader
Supports YouTube, Spotify, Apple Music, SoundCloud, and many other platforms
"""

__version__ = "2.0.0"

import os
import sys
import argparse
import json
import time
import threading
import re
from pathlib import Path
from datetime import datetime
from urllib.parse import urlparse, parse_qs
import signal
import warnings

# Suppress all warnings globally
warnings.filterwarnings('ignore')
os.environ['PYTHONWARNINGS'] = 'ignore'

# Suppress specific library warnings
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

import yt_dlp
import requests
from concurrent.futures import ThreadPoolExecutor, TimeoutError
import subprocess
import shutil
from PIL import Image
import io

try:
    from spotify_handler import SpotifyHandler
    SPOTIFY_HANDLER_AVAILABLE = True
except ImportError:
    SPOTIFY_HANDLER_AVAILABLE = False

try:
    import mutagen
    from mutagen.flac import FLAC, Picture
    from mutagen.mp3 import MP3
    from mutagen.id3 import ID3, APIC, TIT2, TPE1, TALB, TDRC
    from mutagen.mp4 import MP4, MP4Cover
    from mutagen.wave import WAVE
    MUTAGEN_AVAILABLE = True
except ImportError:
    MUTAGEN_AVAILABLE = False

try:
    from youtubesearchpython import VideosSearch
    YOUTUBE_SEARCH_AVAILABLE = True
except ImportError:
    YOUTUBE_SEARCH_AVAILABLE = False

try:
    import gamdl
    from gamdl.downloader import Downloader as GamdlDownloader
    GAMDL_AVAILABLE = True
except ImportError:
    GAMDL_AVAILABLE = False

try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from webdriver_manager.chrome import ChromeDriverManager
    import undetected_chromedriver as uc
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False

try:
    import cloudscraper
    CLOUDSCRAPER_AVAILABLE = True
except ImportError:
    CLOUDSCRAPER_AVAILABLE = False

try:
    from generic_downloader import GenericSiteDownloader
    GENERIC_DOWNLOADER_AVAILABLE = True
except ImportError:
    GENERIC_DOWNLOADER_AVAILABLE = False

try:
    from rich.console import Console
    from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TimeRemainingColumn, DownloadColumn, TransferSpeedColumn
    from rich.panel import Panel
    from rich.table import Table
    from rich.text import Text
    from rich import box
    from rich.live import Live
    from rich.layout import Layout
    from rich.align import Align
    from rich.style import Style
    from rich.markdown import Markdown
    from rich.prompt import Prompt, Confirm
    from rich.columns import Columns
    from rich.tree import Tree
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

try:
    import emoji
    EMOJI_AVAILABLE = True
except ImportError:
    EMOJI_AVAILABLE = False

try:
    from pyfiglet import Figlet
    PYFIGLET_AVAILABLE = True
except ImportError:
    PYFIGLET_AVAILABLE = False

try:
    from halo import Halo
    HALO_AVAILABLE = True
except ImportError:
    HALO_AVAILABLE = False

try:
    from youtube_scorer import YouTubeScorer, score_youtube_video
    YOUTUBE_SCORER_AVAILABLE = True
except ImportError:
    YOUTUBE_SCORER_AVAILABLE = False

# Import reusable components from separate modules
from logger import QuietLogger
from ui_components import Icons, Messages, ModernUI
from utils import (
    sanitize_filename, format_bytes, format_duration, 
    detect_platform, is_playlist_url, extract_video_id,
    load_config, save_config, ensure_directory,
    validate_url, clean_string, truncate_string
)
from apple_music_handler import AppleMusicHandler

# Import new refactored modules
from progress_display import ProgressDisplay, DurationFormatter
from file_manager import FileManager
from url_validator import URLValidator
from platform_info import PlatformInfo

# Import newly created utility modules
from browser_utils import get_random_user_agent, get_browser_driver, format_duration as format_duration_util
from platform_utils import detect_platform as detect_platform_util, get_supported_sites, get_platform_config
from ui_utils import RichConsoleWrapper

class UltimateMediaDownloader:
    def __init__(self, output_dir=None, verbose=False):
        # Default to system Downloads folder if no output_dir specified
        if output_dir is None:
            output_dir = Path.home() / "Downloads" / "UltimateDownloader"
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.cancelled = False
        self.verbose = verbose
        
        # Initialize Rich console for beautiful output
        self.console = Console() if RICH_AVAILABLE else None
        self.current_progress = None
        
        # Initialize custom logger for counting warnings
        self.quiet_logger = QuietLogger()
        
        # Platform-specific configurations (import from platform_utils module)
        from platform_utils import PLATFORM_CONFIGS
        self.platform_configs = PLATFORM_CONFIGS.copy()
        
        # Enhanced yt-dlp configuration for maximum performance and quality
        self.default_ydl_opts = {
            # Performance optimizations
            'socket_timeout': 30,
            'retries': 15,  # Increased retries for better reliability
            'fragment_retries': 15,
            'skip_unavailable_fragments': True,
            'keepvideo': False,
            'noplaylist': False,
            'ignoreerrors': False,  # Changed to False to catch errors properly
            'no_warnings': True,  # Always suppress warnings - we count them now
            'quiet': not self.verbose,  # Show full output in verbose mode
            'no_color': False,  # Allow colors in our custom progress
            'verbose': self.verbose,  # Enable verbose output if requested
            'extractaudio': False,
            'audioformat': 'best',  # Changed from 'mp3' to 'best' for higher quality
            'concurrent_fragments': 8,  # Enable parallel fragment downloads
            'http_chunk_size': 10485760,  # 10MB chunks for faster downloads
            
            # Anti-restriction measures
            'geo_bypass': True,  # Bypass geographic restrictions
            'geo_bypass_country': 'US',
            'nocheckcertificate': True,  # Ignore SSL certificate errors
            'sleep_interval': 1,  # Sleep between downloads to avoid rate limiting
            'max_sleep_interval': 3,
            'sleep_interval_requests': 1,  # Sleep between requests
            
            # Quality settings for high-quality audio
            'prefer_free_formats': False,  # Prefer higher quality formats even if not free
            'format_sort': ['quality', 'res', 'fps', 'hdr:12', 'codec:vp9.2', 'size', 'br', 'asr', 'proto'],
            
            # File naming and organization - use simpler template to avoid long filenames
            'outtmpl': str(self.output_dir / '%(uploader)s - %(title).100B.%(ext)s'),
            'restrictfilenames': False,  # Allow unicode characters but sanitize problematic ones
            'windowsfilenames': True,  # Sanitize filenames for Windows compatibility (removes :, ?, etc.)
            'trim_file_name': 200,  # Limit filename length to 200 characters
            
            # Metadata and cover art - write intermediate files but clean them later
            'writeinfojson': False,  # Don't keep JSON files
            'writethumbnail': True,  # Write thumbnail for embedding
            'writesubtitles': False,
            'writeautomaticsub': False,
            'subtitleslangs': ['en'],
            
            # Enhanced user agent rotation for better compatibility and anti-detection
            'user_agent': self._get_random_user_agent(),
            
            # Cache for faster repeated operations
            'cachedir': str(self.output_dir / '.cache'),
            
            # Resume support
            'continue_dl': True,
            'part': True,
            
            # Custom logger to suppress verbose output (unless verbose mode is enabled)
            'logger': None if self.verbose else self.quiet_logger,
        }
        
        # Initialize Spotify handler if available
        self.spotify_handler = None
        if SPOTIFY_HANDLER_AVAILABLE:
            self.spotify_handler = SpotifyHandler(self)
        
        # Initialize Apple Music downloader if available
        self.apple_music_downloader = None
        if GAMDL_AVAILABLE:
            self._init_apple_music()
        
        # Initialize browser for enhanced scraping
        self.browser_driver = None
        
        # Initialize Apple Music handler
        self.apple_music_handler = AppleMusicHandler(self)
    
    def _init_apple_music(self):
        """Initialize Apple Music downloader"""
        try:
            # Check if Apple Music credentials are available
            apple_music_token = os.environ.get('APPLE_MUSIC_TOKEN')
            apple_music_storefront = os.environ.get('APPLE_MUSIC_STOREFRONT', 'us')
            
            if apple_music_token:
                # Initialize gamdl with token
                self.apple_music_downloader = GamdlDownloader(
                    token=apple_music_token,
                    storefront=apple_music_storefront
                )
                # Only show success in verbose mode
            # Suppress warnings - fallback to YouTube search works well
        except Exception as e:
            # Only show errors in verbose mode
            pass
    
    def _get_browser_driver(self):
        """Get or create browser driver for enhanced scraping
        
        Delegates to browser_utils module for implementation
        """
        return get_browser_driver()
    
    def _get_random_user_agent(self):
        """Get a random user agent to avoid detection
        
        Delegates to browser_utils module for implementation
        """
        return get_random_user_agent()
    
    def _format_duration(self, seconds):
        """Format duration in seconds to human-readable format
        
        Delegates to browser_utils module for implementation.
        
        Args:
            seconds (int/float): Duration in seconds
            
        Returns:
            str: Formatted duration (e.g., "1:23:45" or "1:23")
        """
        return format_duration_util(seconds)
    
    def print_rich(self, message, style="bold cyan"):
        """Print with Rich formatting if available, fallback to plain print
        
        Delegates to ui_utils module for implementation
        """
        wrapper = RichConsoleWrapper()
        wrapper.print_rich(message, style)
    
    def print_panel(self, content, title=None, style="bold blue", border_style="cyan"):
        """Print a beautiful panel with Rich if available
        
        Delegates to ui_utils module for implementation
        """
        wrapper = RichConsoleWrapper()
        wrapper.print_panel(content, title, style, border_style)
    
    def print_table(self, title, headers, rows, style="cyan"):
        """Print a beautiful table with Rich if available
        
        Delegates to ui_utils module for implementation
        """
        wrapper = RichConsoleWrapper()
        wrapper.print_table(title, headers, rows, style)
    
    def detect_platform(self, url):
        """Detect the platform from URL
        
        Delegates to platform_utils module for implementation
        """
        return detect_platform_util(url)
    
    def get_supported_sites(self):
        """Get list of all supported sites
        
        Delegates to platform_utils module for implementation
        """
        try:
            return get_supported_sites()
        except Exception as e:
            print(f"Error getting supported sites: {e}")
            return [{'name': 'Error', 'description': 'Could not load site list'}]
    
    def search_and_download_spotify_track(self, spotify_url):
        """Search for Spotify track/album/playlist on YouTube and download
        
        Delegates to SpotifyHandler
        """
        if self.spotify_handler:
            return self.spotify_handler.search_and_download(spotify_url, interactive=True)
        else:
            self.print_rich(Messages.error("Spotify handler not available"))
            return None
    
    def _search_youtube(self, query, max_results=1):
        """Search for a track on YouTube with animated spinner"""
        
        if RICH_AVAILABLE and self.console:
            with self.console.status(f"[bold cyan]⌕ Searching YouTube for: {query}...", spinner="dots"):
                return self._do_youtube_search(query, max_results)
        else:
            print(f"  ⌕ Searching YouTube: {query}")
            return self._do_youtube_search(query, max_results)
    
    def _do_youtube_search(self, query, max_results=1):
        """Actual YouTube search implementation"""
        # Use yt-dlp's search functionality as primary method (more reliable)
        try:
            search_url = f"ytsearch{max_results}:{query}"
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': True,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                search_results = ydl.extract_info(search_url, download=False)
                
                if search_results and 'entries' in search_results and search_results['entries']:
                    first_result = search_results['entries'][0]
                    video_id = first_result.get('id')
                    if video_id:
                        return f"https://www.youtube.com/watch?v={video_id}"
        
        except Exception as e:
            if RICH_AVAILABLE and self.console:
                self.console.print(f"[red]✗ YouTube search error: {e}[/red]")
            else:
                print(f"✗ YouTube search error: {e}")
        
        # Fallback: Try youtube-search-python library
        if YOUTUBE_SEARCH_AVAILABLE:
            try:
                print("⟳ Trying alternative search library...")
                videos_search = VideosSearch(query, limit=max_results)
                results = videos_search.result()
                
                if results and 'result' in results and results['result']:
                    video = results['result'][0]
                    return video.get('link')
                
            except Exception as e:
                print(f"⚠  Alternative search library error: {e}")
        
        return None
    
    def search_and_download_apple_music_track(self, apple_music_url, interactive=True):
        """Enhanced Apple Music downloader with multiple strategies
        
        Delegates to AppleMusicHandler
        """
        return self.apple_music_handler.search_and_download(apple_music_url, interactive=interactive)
    
    def _prompt_playlist_download_choice(self, tracks):
        """Prompt user to choose which tracks to download"""
        print(f"\n♫ Playlist contains {len(tracks)} tracks")
        print("What would you like to download?")
        print("1. Download all tracks")
        print("2. Select specific tracks")
        print("3. Cancel")
        
        while True:
            try:
                choice = input("\nEnter your choice (1-3): ").strip()
                
                if choice == "1":
                    return "all"
                elif choice == "2":
                    return self._select_specific_tracks(tracks)
                elif choice == "3":
                    return "cancel"
                else:
                    print("Please enter 1, 2, or 3")
                    
            except KeyboardInterrupt:
                return "cancel"
    
    def _select_specific_tracks(self, tracks):
        """Let user select specific tracks to download"""
        print(f"\n≡ Available tracks:")
        for i, track in enumerate(tracks, 1):
            print(f"  {i:2d}. {track}")
        
        print(f"\nEnter track numbers to download (e.g., 1,3,5-8,10):")
        print("Or type 'all' for all tracks, 'cancel' to cancel:")
        
        try:
            user_input = input("Selection: ").strip().lower()
            
            if user_input == 'cancel':
                return "cancel"
            elif user_input == 'all':
                return tracks
            
            # Parse selection (e.g., "1,3,5-8,10")
            selected_indices = set()
            
            for part in user_input.split(','):
                part = part.strip()
                if '-' in part:
                    # Range like "5-8"
                    start, end = part.split('-', 1)
                    start_idx = int(start.strip()) - 1
                    end_idx = int(end.strip()) - 1
                    for idx in range(start_idx, end_idx + 1):
                        if 0 <= idx < len(tracks):
                            selected_indices.add(idx)
                else:
                    # Single number
                    idx = int(part) - 1
                    if 0 <= idx < len(tracks):
                        selected_indices.add(idx)
            
            selected_tracks = [tracks[i] for i in sorted(selected_indices)]
            
            if selected_tracks:
                print(f"✓ Selected {len(selected_tracks)} tracks for download")
                return selected_tracks
            else:
                print("✗ No valid tracks selected")
                return "cancel"
                
        except (ValueError, KeyboardInterrupt):
            print("✗ Invalid selection")
            return "cancel"
    
    def _download_track_queue(self, tracks, source_platform="Unknown", output_format='mp3', quality='best'):
        """Download a queue of tracks one by one"""
        successful_downloads = 0
        failed_downloads = 0
        
        print(f"\n♫ Starting download queue: {len(tracks)} tracks from {source_platform}")
        print(f"♪ Format: {output_format.upper()} | Quality: {quality}")
        print("=" * 60)
        
        for i, track in enumerate(tracks, 1):
            # Convert dictionary track to string format
            if isinstance(track, dict):
                artist = track.get('artist', 'Unknown Artist')
                title = track.get('title', 'Unknown Title')
                track_str = f"{artist} - {title}"
            else:
                track_str = str(track)
            
            print(f"\n[{i}/{len(tracks)}] ♫ Processing: {track_str}")
            
            try:
                # Search for the track on YouTube
                print(f"⌕ Searching YouTube for: {track_str}")
                youtube_url = self._search_youtube_for_music(track_str)
                
                if youtube_url:
                    print(f"✓ Found: {youtube_url}")
                    
                    # Download with enhanced options including thumbnail
                    result = self.download_media(
                        youtube_url, 
                        audio_only=True, 
                        output_format=output_format,
                        quality=quality,
                        add_metadata=True,
                        add_thumbnail=True
                    )
                    
                    if result:
                        successful_downloads += 1
                        print(f"✓ [{i}/{len(tracks)}] Downloaded successfully!")
                    else:
                        failed_downloads += 1
                        print(f"✗ [{i}/{len(tracks)}] Download failed")
                else:
                    failed_downloads += 1
                    print(f"✗ [{i}/{len(tracks)}] Could not find on YouTube")
                
                # Small delay between downloads to be respectful
                if i < len(tracks):
                    time.sleep(2)
                    
            except Exception as e:
                failed_downloads += 1
                print(f"✗ [{i}/{len(tracks)}] Error: {e}")
        
        print("\n" + "=" * 60)
        print(f"♫ Download Queue Complete!")
        print(f"✓ Successful: {successful_downloads}")
        print(f"✗ Failed: {failed_downloads}")
        print(f"▸ Location: {self.output_dir}")
        
        return successful_downloads > 0
    
    def _search_youtube_multiple(self, query, max_results=5):
        """Search YouTube and return multiple results"""
        try:
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': True,
                'playlistend': max_results
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                search_results = ydl.extract_info(f"ytsearch{max_results}:{query}", download=False)
                
                if search_results and 'entries' in search_results:
                    urls = []
                    for entry in search_results['entries']:
                        if entry and entry.get('id'):
                            urls.append(f"https://www.youtube.com/watch?v={entry['id']}")
                    return urls
        except Exception as e:
            print(f"  ⚠  Multiple search error: {e}")
        
        return []
    
    def _score_youtube_result(self, youtube_url, original_query):
        """Score YouTube result using advanced scoring system"""
        try:
            ydl_opts = {'quiet': True, 'no_warnings': True}
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(youtube_url, download=False)
                
                # Use advanced scorer if available
                if YOUTUBE_SCORER_AVAILABLE:
                    score, breakdown = score_youtube_video(info, original_query, verbose=False)
                    
                    # Display score with metrics
                    title = info.get('title', '')
                    view_count = info.get('view_count') or 0
                    like_count = info.get('like_count') or 0
                    like_ratio_pct = (like_count / view_count * 100) if view_count > 0 else 0
                    
                    view_str = f"{view_count:,}" if isinstance(view_count, (int, float)) else "N/A"
                    like_str = f"{like_count:,}" if isinstance(like_count, (int, float)) else "N/A"
                    
                    print(f"    ▤ Score: {score:.0f} | Views: {view_str} | Likes: {like_str} ({like_ratio_pct:.2f}%) | {title[:50]}...")
                    
                    return score
                else:
                    # Fallback: Return basic score if advanced scorer not available
                    print(f"  ⚠  Advanced scorer not available, using basic scoring")
                    return self._basic_score(info, original_query)
                
        except Exception as e:
            print(f"  ⚠  Scoring error: {e}")
            return 0
    
    def _basic_score(self, info, original_query):
        """Basic fallback scoring when advanced scorer is unavailable"""
        score = 0
        title = info.get('title', '').lower()
        view_count = info.get('view_count') or 0
        like_count = info.get('like_count') or 0
        
        # Simple title matching
        query_lower = original_query.lower()
        if query_lower in title:
            score += 100
        
        # Basic popularity scoring
        if view_count > 1_000_000:
            score += 50
        elif view_count > 100_000:
            score += 30
        elif view_count > 10_000:
            score += 10
        
        if like_count > 10_000:
            score += 30
        elif like_count > 1_000:
            score += 15
        
        # Display score
        like_ratio_pct = (like_count / view_count * 100) if view_count > 0 else 0
        view_str = f"{view_count:,}"
        like_str = f"{like_count:,}"
        print(f"    ▤ Score: {score} | Views: {view_str} | Likes: {like_str} ({like_ratio_pct:.2f}%) | {title[:50]}...")
        
        return max(0, score)
    
    def _clean_track_query(self, track_query):
        """Clean track query for better YouTube search results"""
        # Remove common suffixes that might interfere with search
        cleaned = track_query
        
        # Remove featuring information that might be in different formats
        cleaned = re.sub(r'\s*\(feat\..*?\)', '', cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r'\s*\(featuring.*?\)', '', cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r'\s*feat\..*?(?=\s|$)', '', cleaned, flags=re.IGNORECASE)
        
        # Remove explicit/clean markers
        cleaned = re.sub(r'\s*\[(Explicit|Clean|Radio Edit)\]', '', cleaned, flags=re.IGNORECASE)
        
        # Remove extra whitespace
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        
        return cleaned
    
    def _verify_music_content(self, youtube_url, original_query):
        """Verify that YouTube content is actually the music track we want"""
        try:
            ydl_opts = {'quiet': True, 'no_warnings': True}
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(youtube_url, download=False)
                
                title = info.get('title', '').lower()
                duration = info.get('duration', 0)
                
                # Extract artist and song from original query
                if ' - ' in original_query:
                    artist, song = original_query.split(' - ', 1)
                    artist = artist.lower().strip()
                    song = song.lower().strip()
                    
                    # Check if both artist and song appear in the title
                    has_artist = any(word in title for word in artist.split() if len(word) > 2)
                    has_song = any(word in title for word in song.split() if len(word) > 2)
                    
                    # Check duration (music tracks are usually 1-10 minutes)
                    reasonable_duration = 30 < duration < 600  # 30 seconds to 10 minutes
                    
                    # Avoid obvious non-music content
                    non_music_keywords = ['interview', 'documentary', 'behind the scenes', 'making of', 'reaction']
                    is_non_music = any(keyword in title for keyword in non_music_keywords)
                    
                    if (has_artist or has_song) and reasonable_duration and not is_non_music:
                        return True
                
                return False
                
        except Exception:
            # If we can't verify, assume it's okay
            return True
    
    def _fallback_playlist_search(self, apple_music_url, playlist_info):
        """Fallback to searching for entire playlist when individual tracks can't be extracted"""
        print("⟳ Falling back to playlist search...")
        
        search_strategies = [
            f"{playlist_info} playlist music",
            f"{playlist_info} mix songs",
            f"{playlist_info} full playlist",
            f"{playlist_info} album mix",
            playlist_info
        ]
        
        for i, search_query in enumerate(search_strategies, 1):
            print(f"⌕ Trying search strategy {i}/{len(search_strategies)}: {search_query}")
            youtube_url = self._search_youtube(search_query)
            
            if youtube_url:
                print(f"✓ Found match on YouTube: {youtube_url}")
                return self.download_media(youtube_url, audio_only=True, output_format='mp3', add_thumbnail=True)
        
        print("✗ Could not find suitable playlist on YouTube")
        return None
    def _prompt_audio_format_quality(self):
        """Prompt user for audio format and quality preferences"""
        print(f"\n🎚️  Select audio quality:")
        print("  1. Best Quality (320kbps MP3) - Recommended")
        print("  2. High Quality (256kbps AAC/M4A) - Balanced")
        print("  3. Very High Quality (FLAC) - Lossless, larger files")
        print("  4. Best Available (Auto) - Highest quality possible")
        
        while True:
            try:
                quality_choice = input("\nEnter choice (1-4) [default: 1]: ").strip() or "1"
                
                if quality_choice == "1":
                    return 'mp3', 'best'
                elif quality_choice == "2":
                    return 'm4a', 'best'
                elif quality_choice == "3":
                    return 'flac', 'best'
                elif quality_choice == "4":
                    return 'best', 'best'
                else:
                    print("Please enter 1, 2, 3, or 4")
                    
            except KeyboardInterrupt:
                print("\n✗ Using default: MP3 320kbps")
                return 'mp3', 'best'
    def cleanup(self):
        """Cleanup resources"""
        if self.browser_driver:
            try:
                self.browser_driver.quit()
                print("🧹 Browser driver cleaned up")
            except:
                pass
            self.browser_driver = None
    
    def __del__(self):
        """Destructor to ensure cleanup"""
        self.cleanup()
    
    def signal_handler(self, signum, frame):
        """Handle interruption signals"""
        print("\n\nDownload interrupted by user. Cleaning up...")
        self.cancelled = True
        sys.exit(0)
    
    def setup_signal_handlers(self):
        """Setup signal handlers for graceful interruption"""
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
    
    def clean_url(self, url, keep_playlist=False):
        """Clean and normalize URLs
        
        Args:
            url: The URL to clean
            keep_playlist: If True, keeps playlist parameters (for playlist downloads)
        """
        # Remove playlist parameters that might cause issues for single video downloads
        if not keep_playlist:
            if "youtube.com" in url or "youtu.be" in url:
                if "&list=" in url and "watch?v=" in url:
                    # For YouTube, if it's a single video in a playlist, extract just the video
                    parsed = urlparse(url)
                    params = parse_qs(parsed.query)
                    if 'v' in params:
                        video_id = params['v'][0]
                        return f"https://www.youtube.com/watch?v={video_id}"
        return url
    
    def _fetch_spotify_album_art(self, track_name, artist_name, silent=False):
        """Fetch high-quality album art from Spotify"""
        if not self.spotify_handler or not self.spotify_handler.spotify_client:
            return None
        
        try:
            if not silent:
                if RICH_AVAILABLE and self.console:
                    self.console.print(f"[dim cyan]→[/dim cyan] [dim]Fetching album art from Spotify...[/dim]", end="\r")
                else:
                    print(f"→ Fetching album art from Spotify...", end="\r")
            
            query = f"{track_name} {artist_name}"
            results = self.spotify_handler.spotify_client.search(q=query, type='track', limit=1)
            
            if results and results['tracks']['items']:
                track = results['tracks']['items'][0]
                album = track['album']
                
                # Get the highest quality image (first one is usually largest)
                if album['images']:
                    image_url = album['images'][0]['url']
                    
                    # Download the image
                    response = requests.get(image_url, timeout=10)
                    if response.status_code == 200:
                        return response.content
            
            return None
            
        except Exception as e:
            return None
    
    def _fetch_apple_music_album_art(self, track_name, artist_name, silent=False):
        """Fetch high-quality album art from Apple Music API"""
        try:
            if not silent:
                if RICH_AVAILABLE and self.console:
                    self.console.print(f"[dim cyan]→[/dim cyan] [dim]Fetching album art from Apple Music...[/dim]", end="\r")
                else:
                    print(f"→ Fetching album art from Apple Music...", end="\r")
            
            # Use Apple Music Search API (doesn't require authentication)
            base_url = "https://itunes.apple.com/search"
            params = {
                'term': f"{artist_name} {track_name}",
                'media': 'music',
                'entity': 'song',
                'limit': 1
            }
            
            response = requests.get(base_url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                
                if data.get('results'):
                    result = data['results'][0]
                    # Apple Music provides artwork URLs, usually at 100x100, but we can request higher res
                    artwork_url = result.get('artworkUrl100', '').replace('100x100', '600x600')
                    
                    if artwork_url:
                        art_response = requests.get(artwork_url, timeout=10)
                        if art_response.status_code == 200:
                            return art_response.content
            
            return None
            
        except Exception as e:
            return None
    
    def _embed_album_art(self, audio_file_path, album_art_data, track_info=None, silent=False):
        """Embed album art into audio file with proper metadata"""
        if not MUTAGEN_AVAILABLE:
            if not silent:
                if RICH_AVAILABLE and self.console:
                    self.console.print("[yellow]⚠[/yellow] Mutagen not available, skipping album art embedding")
                else:
                    print("⚠ Mutagen not available, skipping album art embedding")
            return False
        
        try:
            file_path = Path(audio_file_path)
            file_ext = file_path.suffix.lower()
            
            if file_ext == '.mp3':
                audio = MP3(str(file_path), ID3=ID3)
                
                # Add ID3 tag if doesn't exist
                try:
                    audio.add_tags()
                except:
                    pass
                
                # Add cover art
                audio.tags.add(
                    APIC(
                        encoding=3,
                        mime='image/jpeg',
                        type=3,  # Cover (front)
                        desc='Cover',
                        data=album_art_data
                    )
                )
                
                # Add track info if provided
                if track_info:
                    if track_info.get('title'):
                        audio.tags.add(TIT2(encoding=3, text=track_info['title']))
                    if track_info.get('artist'):
                        audio.tags.add(TPE1(encoding=3, text=track_info['artist']))
                    if track_info.get('album'):
                        audio.tags.add(TALB(encoding=3, text=track_info['album']))
                    if track_info.get('year'):
                        audio.tags.add(TDRC(encoding=3, text=str(track_info['year'])))
                
                audio.save()
                return True
                
            elif file_ext == '.flac':
                audio = FLAC(str(file_path))
                
                # Create Picture object for FLAC
                picture = Picture()
                picture.type = 3  # Cover (front)
                picture.mime = 'image/jpeg'
                picture.desc = 'Cover'
                picture.data = album_art_data
                
                # Remove existing pictures
                audio.clear_pictures()
                audio.add_picture(picture)
                
                # Add track info if provided
                if track_info:
                    if track_info.get('title'):
                        audio['title'] = track_info['title']
                    if track_info.get('artist'):
                        audio['artist'] = track_info['artist']
                    if track_info.get('album'):
                        audio['album'] = track_info['album']
                    if track_info.get('year'):
                        audio['date'] = str(track_info['year'])
                
                audio.save()
                return True
                
            elif file_ext in ['.m4a', '.mp4']:
                audio = MP4(str(file_path))
                
                # Add cover art
                audio['covr'] = [MP4Cover(album_art_data, imageformat=MP4Cover.FORMAT_JPEG)]
                
                # Add track info if provided
                if track_info:
                    if track_info.get('title'):
                        audio['\xa9nam'] = track_info['title']
                    if track_info.get('artist'):
                        audio['\xa9ART'] = track_info['artist']
                    if track_info.get('album'):
                        audio['\xa9alb'] = track_info['album']
                    if track_info.get('year'):
                        audio['\xa9day'] = str(track_info['year'])
                
                audio.save()
                return True
            
            else:
                if not silent:
                    if RICH_AVAILABLE and self.console:
                        self.console.print(f"[yellow]⚠[/yellow] Album art embedding not supported for {file_ext} format")
                    else:
                        print(f"⚠ Album art embedding not supported for {file_ext} format")
                return False
                
        except Exception as e:
            if not silent:
                if RICH_AVAILABLE and self.console:
                    self.console.print(f"[red]✗[/red] Error embedding album art: {e}")
                else:
                    print(f"✗ Error embedding album art: {e}")
            return False
    
    def _convert_to_true_lossless(self, audio_file_path, target_format='flac'):
        """Convert audio to true lossless format using FFmpeg with proper settings"""
        try:
            file_path = Path(audio_file_path)
            
            # Check if source is already lossless
            source_ext = file_path.suffix.lower()
            if source_ext in ['.flac', '.wav', '.alac']:
                print(f"✓ Source is already in lossless format: {source_ext}")
                return str(file_path)
            
            # For lossy sources, we can't create "true" lossless, but we can ensure best quality conversion
            if source_ext in ['.mp3', '.m4a', '.aac', '.opus', '.ogg']:
                print(f"⚠  Source is lossy ({source_ext}). Converting to {target_format} for archival...")
                print(f"→ Note: This won't improve quality, but provides better format for storage")
            
            output_file = file_path.with_suffix(f'.{target_format}')
            
            print(f"⟳ Converting {file_path.name} to {target_format.upper()}...")
            
            if target_format == 'flac':
                # FLAC with maximum compression (level 8) for best size/quality ratio
                cmd = [
                    'ffmpeg', '-i', str(file_path),
                    '-c:a', 'flac',
                    '-compression_level', '8',
                    '-sample_fmt', 's32',  # 32-bit depth
                    '-ar', '48000',  # 48kHz sample rate
                    str(output_file),
                    '-y'  # Overwrite output file
                ]
            elif target_format == 'wav':
                # WAV with high bit depth
                cmd = [
                    'ffmpeg', '-i', str(file_path),
                    '-c:a', 'pcm_s24le',  # 24-bit PCM
                    '-ar', '48000',  # 48kHz sample rate
                    str(output_file),
                    '-y'
                ]
            else:
                print(f"✗ Unsupported target format: {target_format}")
                return str(file_path)
            
            # Run FFmpeg conversion
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            if result.returncode == 0 and output_file.exists():
                print(f"✓ Converted to {target_format.upper()}: {output_file.name}")
                
                # Remove original file if conversion successful
                try:
                    file_path.unlink()
                    print(f"🗑️  Removed original file: {file_path.name}")
                except:
                    pass
                
                return str(output_file)
            else:
                print(f"✗ Conversion failed: {result.stderr}")
                return str(file_path)
                
        except subprocess.TimeoutExpired:
            print(f"✗ Conversion timeout exceeded")
            return str(file_path)
        except Exception as e:
            print(f"✗ Error during conversion: {e}")
            return str(file_path)
    
    def _convert_video_format(self, video_file_path, target_format='mp4'):
        """Convert video to target format using FFmpeg"""
        try:
            file_path = Path(video_file_path)
            output_file = file_path.with_suffix(f'.{target_format}')
            
            # If output already exists, return it
            if output_file.exists():
                return str(output_file)
            
            print(f"⟳ Converting {file_path.name} to {target_format.upper()}...")
            
            # Use FFmpeg to convert with good quality settings
            cmd = [
                'ffmpeg', '-i', str(file_path),
                '-c:v', 'libx264',  # H.264 codec for MP4
                '-preset', 'medium',  # Encoding speed/quality tradeoff
                '-crf', '23',  # Quality (lower = better, 23 is good default)
                '-c:a', 'aac',  # AAC audio codec
                '-b:a', '192k',  # Audio bitrate
                str(output_file),
                '-y'  # Overwrite output file
            ]
            
            # For formats other than MP4, adjust codec
            if target_format == 'mkv':
                cmd = [
                    'ffmpeg', '-i', str(file_path),
                    '-c:v', 'copy',  # Copy video stream (no re-encode)
                    '-c:a', 'copy',  # Copy audio stream (no re-encode)
                    str(output_file),
                    '-y'
                ]
            elif target_format == 'avi':
                cmd = [
                    'ffmpeg', '-i', str(file_path),
                    '-c:v', 'libx264',
                    '-c:a', 'mp3',
                    str(output_file),
                    '-y'
                ]
            
            # Run FFmpeg conversion
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=600  # 10 minute timeout for video
            )
            
            if result.returncode == 0 and output_file.exists():
                print(f"✓ Converted to {target_format.upper()}: {output_file.name}")
                return str(output_file)
            else:
                error_msg = result.stderr if result.stderr else "Unknown error"
                print(f"✗ Conversion failed: {error_msg[:200]}")
                return None
                
        except subprocess.TimeoutExpired:
            print(f"✗ Conversion timeout exceeded")
            return None
        except Exception as e:
            print(f"✗ Error during video conversion: {e}")
            return None
                
    def _add_album_art_to_playlist(self, playlist_dir):
        """Add album art to all audio files in a playlist directory"""
        try:
            playlist_path = Path(playlist_dir)
            if not playlist_path.exists():
                return
            
            # Find all audio files
            audio_files = []
            for ext in ['.flac', '.mp3', '.m4a', '.aac']:
                audio_files.extend(playlist_path.glob(f'*{ext}'))
            
            if not audio_files:
                return
            
            if RICH_AVAILABLE and self.console:
                self.console.print(f"\n[bold cyan]♪[/bold cyan] Processing album artwork for {len(audio_files)} files...")
            else:
                print(f"\n♪ Processing album artwork for {len(audio_files)} files...")
            
            # Process each file
            for idx, audio_file in enumerate(audio_files, 1):
                try:
                    # Extract track info from filename (format: "001 - Artist - Title.ext")
                    filename = audio_file.stem
                    
                    # Try to parse title and artist from filename
                    # Common patterns: "001 - Title", "001 - Artist - Title"
                    parts = filename.split(' - ', 1)
                    if len(parts) > 1:
                        track_name = parts[1].strip()
                        
                        # Try to split artist and title
                        if ' - ' in track_name:
                            artist_parts = track_name.split(' - ', 1)
                            artist_name = artist_parts[0].strip()
                            track_title = artist_parts[1].strip()
                        else:
                            artist_name = ""
                            track_title = track_name
                    else:
                        track_title = filename
                        artist_name = ""
                    
                    if RICH_AVAILABLE and self.console:
                        self.console.print(f"[dim][{idx}/{len(audio_files)}][/dim] [cyan]{track_title}[/cyan]", end="")
                    else:
                        print(f"[{idx}/{len(audio_files)}] {track_title}", end="")
                    
                    # Try to fetch album art from Apple Music first, then Spotify
                    album_art_data = None
                    if track_title:
                        album_art_data = self._fetch_apple_music_album_art(track_title, artist_name, silent=True)
                        
                        if not album_art_data and self.spotify_handler and self.spotify_handler.spotify_client:
                            album_art_data = self._fetch_spotify_album_art(track_title, artist_name, silent=True)
                    
                    # Embed album art if found
                    if album_art_data:
                        track_info = {
                            'title': track_title,
                            'artist': artist_name if artist_name else 'Unknown',
                        }
                        self._embed_album_art(str(audio_file), album_art_data, track_info, silent=True)
                        if RICH_AVAILABLE and self.console:
                            self.console.print(f" [green]✓[/green]")
                        else:
                            print(f" ✓")
                    else:
                        if RICH_AVAILABLE and self.console:
                            self.console.print(f" [yellow]⊘[/yellow]")
                        else:
                            print(f" ⊘")
                    
                except Exception as e:
                    if RICH_AVAILABLE and self.console:
                        self.console.print(f" [red]✗[/red] ({str(e)})")
                    else:
                        print(f" ✗ ({str(e)})")
                    continue
            
            if RICH_AVAILABLE and self.console:
                self.console.print(f"[bold green]✓[/bold green] Album artwork processing completed")
            else:
                print(f"✓ Album artwork processing completed")
                
        except Exception as e:
            if RICH_AVAILABLE and self.console:
                self.console.print(f"[yellow]⚠[/yellow] Error processing album art: {str(e)}")
            else:
                print(f"⚠ Error processing album art: {str(e)}")
    
    def _enhance_audio_with_metadata(self, audio_file_path, track_name, artist_name, fetch_from_streaming=True):
        """Enhance audio file with proper metadata and album art from streaming services"""
        try:
            print(f"\n♫ Enhancing audio metadata for: {track_name}")
            
            # Try to fetch album art from streaming services
            album_art_data = None
            
            if fetch_from_streaming:
                # Try Spotify first (usually better quality)
                if self.spotify_handler:
                    album_art_data = self._fetch_spotify_album_art(track_name, artist_name)
                
                # If Spotify fails, try Apple Music
                if not album_art_data:
                    album_art_data = self._fetch_apple_music_album_art(track_name, artist_name)
            
            # If we got album art, embed it
            if album_art_data:
                track_info = {
                    'title': track_name,
                    'artist': artist_name,
                }
                self._embed_album_art(audio_file_path, album_art_data, track_info)
            else:
                print("⚠  Using YouTube thumbnail as fallback")
            
            return True
            
        except Exception as e:
            print(f"✗ Error enhancing audio metadata: {e}")
            return False

    def is_playlist_url(self, url):
        """Detect if URL is a playlist"""
        playlist_indicators = [
            'list=',  # YouTube playlists
            'playlist',  # Generic playlist
            'album',  # Spotify albums
            'sets/',  # SoundCloud sets
            '/playlists/',  # Various platforms
        ]
        
        url_lower = url.lower()
        return any(indicator in url_lower for indicator in playlist_indicators)
    
    def prompt_user_choice(self, prompt, choices, default=None):
        """Prompt user for a choice from a list"""
        print(f"\n{prompt}")
        for i, choice in enumerate(choices, 1):
            marker = " (default)" if default and choice == default else ""
            print(f"  {i}. {choice}{marker}")
        
        while True:
            try:
                choice = input(f"\nEnter your choice (1-{len(choices)}): ").strip()
                if not choice and default:
                    return default
                
                choice_idx = int(choice) - 1
                if 0 <= choice_idx < len(choices):
                    return choices[choice_idx]
                else:
                    print(f"Please enter a number between 1 and {len(choices)}")
            except (ValueError, KeyboardInterrupt):
                if default:
                    return default
                print(f"Please enter a number between 1 and {len(choices)}")
    
    def prompt_format_selection(self, url):
        """Interactive format selection with auto-detected qualities"""
        print("\n◎ FORMAT SELECTION")
        print("=" * 50)
        
        # First, try to detect available qualities
        print("🔍 Detecting available video qualities...")
        info = self.get_supported_formats(url, timeout=20)
        
        # Ask for media type
        media_types = ["Video (with audio)", "Audio only"]
        media_choice = self.prompt_user_choice(
            "What type of media do you want to download?", 
            media_types, 
            default="Video (with audio)"
        )
        
        audio_only = media_choice == "Audio only"
        
        # Ask for quality with enhanced audio format options or detected video qualities
        if audio_only:
            quality_options = [
                "Best lossless (FLAC)",
                "High quality (Opus 256kbps)", 
                "High quality (M4A 256kbps)",
                "Standard (MP3 320kbps)", 
                "Compact (MP3 192kbps)",
                "Custom"
            ]
            quality_choice = self.prompt_user_choice(
                "Select audio quality and format:", 
                quality_options, 
                default="Best lossless (FLAC)"
            )
            
            if quality_choice == "Custom":
                print("\nCustom format examples:")
                print("  FLAC lossless: bestaudio[acodec=flac]/bestaudio")
                print("  Opus high quality: bestaudio[acodec=opus]/bestaudio")
                print("  M4A/AAC: bestaudio[acodec=m4a]/bestaudio[acodec=aac]")
                custom_format = input("Enter custom format: ").strip()
                return "best", audio_only, None, custom_format if custom_format else None
            
            quality_map = {
                "Best lossless (FLAC)": "best",
                "High quality (Opus 256kbps)": "best", 
                "High quality (M4A 256kbps)": "best",
                "Standard (MP3 320kbps)": "best",
                "Compact (MP3 192kbps)": "best"
            }
            
            format_map = {
                "Best lossless (FLAC)": "flac",
                "High quality (Opus 256kbps)": "opus", 
                "High quality (M4A 256kbps)": "m4a",
                "Standard (MP3 320kbps)": "mp3",
                "Compact (MP3 192kbps)": "mp3"
            }
            
            return quality_map[quality_choice], audio_only, format_map[quality_choice], None
        else:
            # Build quality options from detected formats
            quality_options = ["Best available"]
            detected_qualities = set()
            
            if info and 'formats' in info:
                # Extract unique video heights from formats
                for fmt in info['formats']:
                    if fmt.get('vcodec') != 'none' and fmt.get('height'):
                        height = fmt.get('height')
                        if height >= 2160:
                            detected_qualities.add("4K (2160p)")
                        elif height >= 1440:
                            detected_qualities.add("1440p")
                        elif height >= 1080:
                            detected_qualities.add("1080p")
                        elif height >= 720:
                            detected_qualities.add("720p")
                        elif height >= 480:
                            detected_qualities.add("480p")
                        elif height >= 360:
                            detected_qualities.add("360p")
                
                # Sort detected qualities by resolution (descending)
                quality_order = ["4K (2160p)", "1440p", "1080p", "720p", "480p", "360p"]
                for q in quality_order:
                    if q in detected_qualities:
                        quality_options.append(f"{q} ✓ (available)")
            
            # Add standard options that weren't detected
            standard_qualities = ["4K (2160p)", "1440p", "1080p", "720p", "480p", "360p"]
            for q in standard_qualities:
                if f"{q} ✓ (available)" not in quality_options:
                    quality_options.append(q)
            
            quality_options.append("Custom")
            
            # Show detected qualities if any
            if detected_qualities:
                print(f"\n✓ Detected available qualities: {', '.join(sorted(detected_qualities, reverse=True))}")
            
            quality_choice = self.prompt_user_choice(
                "Select video quality:", 
                quality_options, 
                default="Best available"
            )
            
            if quality_choice == "Custom":
                custom_format = input("Enter custom format (e.g., 'best[height<=720]'): ").strip()
                return "best", audio_only, None, custom_format if custom_format else None
            
            # Map the choice back to simple quality name
            quality_choice_clean = quality_choice.replace(" ✓ (available)", "")
            
            quality_map = {
                "Best available": "best",
                "4K (2160p)": "2160p",
                "1440p": "1440p", 
                "1080p": "1080p",
                "720p": "720p",
                "480p": "480p",
                "360p": "360p"
            }
            
            # Ask for output format
            format_options = ["MP4 (recommended)", "MKV", "WebM", "AVI", "MOV", "Keep original"]
            format_choice = self.prompt_user_choice(
                "Select output format:", 
                format_options, 
                default="MP4 (recommended)"
            )
            
            format_map = {
                "MP4 (recommended)": "mp4",
                "MKV": "mkv",
                "WebM": "webm", 
                "AVI": "avi",
                "MOV": "mov",
                "Keep original": None
            }
            
            return quality_map[quality_choice_clean], audio_only, format_map[format_choice], None
    
    def get_supported_formats(self, url, timeout=30):
        """Get all available formats for a URL with timeout"""
        def extract_formats():
            ydl_opts = self.default_ydl_opts.copy()
            ydl_opts.update({
                'quiet': True,
                'listformats': True,
                'extract_flat': False,
            })
            
            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=False)
                    return info
            except Exception as e:
                print(f"Error extracting formats: {e}")
                return None
        
        # Use threading with timeout
        with ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(extract_formats)
            try:
                result = future.result(timeout=timeout)
                return result
            except TimeoutError:
                print(f"Format extraction timed out after {timeout} seconds")
                return None
            except Exception as e:
                print(f"Error in format extraction: {e}")
                return None
    
    def display_available_qualities(self, info):
        """Display available video and audio qualities"""
        if not info or 'formats' not in info:
            print("No format information available")
            return
        
        formats = info['formats']
        
        # Separate video and audio formats
        video_formats = []
        audio_formats = []
        
        for fmt in formats:
            if fmt.get('vcodec') != 'none' and fmt.get('height'):
                video_formats.append(fmt)
            elif fmt.get('acodec') != 'none' and fmt.get('vcodec') == 'none':
                audio_formats.append(fmt)
        
        print("\n" + "="*70)
        print(f"▶ AVAILABLE VIDEO QUALITIES ({len(video_formats)} formats)")
        print("="*70)
        
        # Sort video formats by quality (height)
        video_formats.sort(key=lambda x: x.get('height', 0), reverse=True)
        
        for i, fmt in enumerate(video_formats[:15]):  # Show top 15
            height = fmt.get('height', 'Unknown')
            fps = fmt.get('fps', 'Unknown')
            vcodec = fmt.get('vcodec', 'Unknown')[:20]  # Truncate long codec names
            filesize = fmt.get('filesize')
            ext = fmt.get('ext', 'Unknown')
            format_id = fmt.get('format_id', 'Unknown')
            
            size_str = f"{filesize / 1024 / 1024:.1f}MB" if filesize else "Unknown size"
            
            print(f"{i+1:2d}. {height:4}p @{fps:4}fps | {vcodec:20} | {ext:4} | {size_str:12} | ID: {format_id}")
        
        print("\n" + "="*70)
        print(f"♫ AVAILABLE AUDIO QUALITIES ({len(audio_formats)} formats)")
        print("="*70)
        
        # Sort audio formats by quality (abr - audio bitrate)
        audio_formats.sort(key=lambda x: x.get('abr', 0), reverse=True)
        
        for i, fmt in enumerate(audio_formats[:15]):  # Show top 15
            abr = fmt.get('abr', 'Unknown')
            acodec = fmt.get('acodec', 'Unknown')[:20]
            ext = fmt.get('ext', 'Unknown')
            filesize = fmt.get('filesize')
            format_id = fmt.get('format_id', 'Unknown')
            
            size_str = f"{filesize / 1024 / 1024:.1f}MB" if filesize else "Unknown size"
            bitrate_str = f"{abr:6.1f}kbps" if abr != 'Unknown' else "Unknown   "
            
            print(f"{i+1:2d}. {bitrate_str} | {acodec:20} | {ext:4} | {size_str:12} | ID: {format_id}")
        
        # Show recommended formats
        print("\n" + "="*70)
        print("★ RECOMMENDED FORMATS")
        print("="*70)
        print("▶ Best video quality:     bestvideo+bestaudio/best")
        print("♫ Best audio quality:     bestaudio/best")
        print("▶ 1080p video:           best[height<=1080]")
        print("▶ 720p video:            best[height<=720]")
        print("♫ MP3 audio (320kbps):   bestaudio[abr>=320]/bestaudio")
        print("♫ High quality audio:    bestaudio[ext=m4a]/bestaudio")
        print("\n→ Pro tip: Use --custom-format to specify exact format IDs")
    
    def get_video_info(self, url, timeout=45):
        """Get comprehensive video information with timeout"""
        # Handle special platforms
        platform = self.detect_platform(url)
        
        if platform == 'spotify':
            return self.search_and_download_spotify_track(url)
        
        def extract_info():
            # Clean the URL first
            clean_url = self.clean_url(url)
            
            ydl_opts = self.default_ydl_opts.copy()
            ydl_opts.update({
                'quiet': True,
                'extract_flat': False,
            })
            
            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    print("⌕ Extracting media information...")
                    info = ydl.extract_info(clean_url, download=False)
                    return info
            except Exception as e:
                print(f"Error extracting info: {e}")
                return None
        
        # Progress indicator
        def show_progress():
            chars = "|/-\\"
            i = 0
            start_time = time.time()
            while not hasattr(extract_info, 'done'):
                elapsed = int(time.time() - start_time)
                print(f"\r⏳ Loading {chars[i % len(chars)]} ({elapsed}s)", end="", flush=True)
                i += 1
                time.sleep(0.5)
        
        # Use threading with timeout
        with ThreadPoolExecutor(max_workers=2) as executor:
            future = executor.submit(extract_info)
            progress_future = executor.submit(show_progress)
            
            try:
                result = future.result(timeout=timeout)
                extract_info.done = True  # Stop progress indicator
                print("\r✓ Information extracted successfully!          ")
                return result
            except TimeoutError:
                extract_info.done = True
                print(f"\r✗ Information extraction timed out after {timeout} seconds")
                return None
            except Exception as e:
                extract_info.done = True
                print(f"\r✗ Error in information extraction: {e}")
                return None
    
    def detect_audio_languages(self, url):
        """Detect available audio language tracks in a video
        
        Returns:
            List of dictionaries containing language info, or None if only one language
        """
        try:
            ydl_opts = self.default_ydl_opts.copy()
            ydl_opts.update({
                'quiet': True,
                'extract_flat': False,
            })
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                
                if not info or 'formats' not in info:
                    return None
                
                # Extract unique audio languages from formats
                audio_languages = {}
                
                for fmt in info.get('formats', []):
                    # Check if this is an audio format
                    if fmt.get('acodec') != 'none':
                        lang = fmt.get('language') or fmt.get('audio_lang') or 'und'
                        
                        # Normalize language code for display deduplication (e.g., en-US, en-GB -> en)
                        normalized_lang = self._normalize_language_code(lang)
                        
                        # Skip if we already have this language with better quality
                        if normalized_lang in audio_languages:
                            # Compare quality (prefer higher bitrate)
                            existing_abr = audio_languages[normalized_lang].get('abr', 0) or 0
                            current_abr = fmt.get('abr', 0) or 0
                            if current_abr <= existing_abr:
                                continue
                        
                        # Get language name (try to convert code to full name)
                        lang_name = self._get_language_name(normalized_lang)
                        
                        # Store with both original and normalized codes
                        # Use original code for actual download, normalized for display
                        audio_languages[normalized_lang] = {
                            'code': lang,  # Keep original code (en-US, en-GB, etc.) for download
                            'normalized_code': normalized_lang,  # Normalized code (en, es, etc.) for display
                            'name': lang_name,
                            'format_id': fmt.get('format_id'),
                            'abr': fmt.get('abr'),
                            'acodec': fmt.get('acodec'),
                            'ext': fmt.get('ext')
                        }
                
                # If only one language or no language info, return None
                if len(audio_languages) <= 1:
                    return None
                
                # Return sorted list (by language name)
                languages_list = list(audio_languages.values())
                languages_list.sort(key=lambda x: x['name'])
                
                return languages_list
                
        except Exception as e:
            if RICH_AVAILABLE and self.console:
                self.console.print(f"[yellow]⚠ Could not detect audio languages: {e}[/yellow]")
            else:
                print(f"⚠ Could not detect audio languages: {e}")
            return None
    
    def _normalize_language_code(self, lang_code):
        """Normalize language codes to avoid duplicates
        
        Converts variants like en-US, en-GB to just 'en'
        es-ES, es-MX to just 'es', etc.
        
        Args:
            lang_code: Language code (e.g., 'en-US', 'en', 'es-MX')
            
        Returns:
            Normalized language code (e.g., 'en', 'es')
        """
        if not lang_code:
            return 'und'
        
        # Convert to lowercase for consistency
        lang_code = lang_code.lower()
        
        # Split on hyphen or underscore (e.g., en-US, en_US)
        if '-' in lang_code:
            base_lang = lang_code.split('-')[0]
        elif '_' in lang_code:
            base_lang = lang_code.split('_')[0]
        else:
            base_lang = lang_code
        
        return base_lang
    
    def _get_language_name(self, lang_code):
        """Convert language code to full name"""
        # Common language codes mapping
        language_map = {
            'en': 'English',
            'es': 'Spanish',
            'fr': 'French',
            'de': 'German',
            'it': 'Italian',
            'pt': 'Portuguese',
            'ru': 'Russian',
            'ja': 'Japanese',
            'ko': 'Korean',
            'zh': 'Chinese',
            'ar': 'Arabic',
            'hi': 'Hindi',
            'nl': 'Dutch',
            'pl': 'Polish',
            'tr': 'Turkish',
            'sv': 'Swedish',
            'da': 'Danish',
            'no': 'Norwegian',
            'fi': 'Finnish',
            'el': 'Greek',
            'he': 'Hebrew',
            'th': 'Thai',
            'vi': 'Vietnamese',
            'id': 'Indonesian',
            'ms': 'Malay',
            'cs': 'Czech',
            'hu': 'Hungarian',
            'ro': 'Romanian',
            'uk': 'Ukrainian',
            'und': 'Unknown/Default'
        }
        
        return language_map.get(lang_code.lower(), lang_code.upper())
    
    def prompt_audio_language_selection(self, languages):
        """Prompt user to select audio language
        
        Args:
            languages: List of language dictionaries
            
        Returns:
            Selected language dictionary
        """
        if not languages or len(languages) <= 1:
            return None
        
        # Display available languages
        if RICH_AVAILABLE and self.console:
            self.console.print("\n[bold cyan]🌐 Multiple Audio Languages Detected[/bold cyan]")
            self.console.print("[dim]─" * 50 + "[/dim]")
            
            # Create table for better display
            from rich.table import Table
            table = Table(show_header=True, header_style="bold magenta")
            table.add_column("#", style="cyan", width=4)
            table.add_column("Language", style="green")
            table.add_column("Quality", style="yellow")
            table.add_column("Codec", style="blue")
            
            for i, lang in enumerate(languages, 1):
                quality = f"{lang.get('abr', 'N/A')} kbps" if lang.get('abr') else "N/A"
                codec = lang.get('acodec', 'N/A')
                table.add_row(str(i), lang['name'], quality, codec)
            
            self.console.print(table)
        else:
            print("\n🌐 Multiple Audio Languages Detected")
            print("─" * 50)
            for i, lang in enumerate(languages, 1):
                quality = f"{lang.get('abr', 'N/A')} kbps" if lang.get('abr') else "N/A"
                codec = lang.get('acodec', 'N/A')
                print(f"{i}. {lang['name']} - {quality} ({codec})")
        
        # Prompt for selection
        language_choices = [lang['name'] for lang in languages]
        selected_name = self.prompt_user_choice(
            "Select audio language:",
            language_choices,
            default=language_choices[0]
        )
        
        # Find and return the selected language
        for lang in languages:
            if lang['name'] == selected_name:
                return lang
        
        return languages[0]  # Fallback to first language
    
    def download_media(self, url, quality="best", audio_only=False, output_format=None, custom_format=None, interactive=False, add_metadata=False, add_thumbnail=False, custom_filename=None, no_playlist=False, audio_language=None):
        """Download media with enhanced options and smart URL handling
        
        Args:
            url: Media URL to download
            quality: Video quality
            audio_only: Download audio only
            output_format: Output format
            custom_format: Custom yt-dlp format
            interactive: Interactive mode
            add_metadata: Add metadata to file
            add_thumbnail: Add thumbnail to file
            custom_filename: Custom filename
            no_playlist: Download only single video from playlist URL
        """
        try:
            # Setup signal handlers
            self.setup_signal_handlers()
            
            # Handle special platforms
            platform = self.detect_platform(url)
            
            # Show beautiful download start panel
            if RICH_AVAILABLE and self.console:
                download_info = f"""[bold cyan]Platform:[/bold cyan] [yellow]{platform.upper()}[/yellow]
[bold cyan]Quality:[/bold cyan] [green]{quality}[/green]
[bold cyan]Mode:[/bold cyan] [magenta]{'Audio Only' if audio_only else 'Video + Audio'}[/magenta]
[bold cyan]Format:[/bold cyan] [blue]{output_format if output_format else 'Auto'}[/blue]"""
                self.print_panel(download_info, title="▸ Starting Download", border_style="green")
            else:
                print(f"◎ Detected platform: {platform.upper()}")
            
            # For Spotify/Apple Music, use enhanced handlers first
            if platform == 'spotify':
                return self.search_and_download_spotify_track(url)
            elif platform == 'apple_music':
                return self.search_and_download_apple_music_track(url, interactive=interactive)
            
            # Check if URL might be a playlist
            if self.is_playlist_url(url):
                # First check if this is a YouTube Mix/Radio playlist (unviewable)
                is_youtube_mix = False
                if "youtube.com" in url or "youtu.be" in url:
                    if "list=" in url:
                        parsed = urlparse(url)
                        params = parse_qs(parsed.query)
                        if 'list' in params:
                            list_id = params['list'][0]
                            # Mix/Radio playlists start with RD
                            if list_id.startswith('RD'):
                                is_youtube_mix = True
                                print("⌕ YouTube Mix/Radio playlist detected!")
                                print("ℹ  Mix playlists are dynamically generated and unviewable")
                                print("→ Extracting single video from URL...")
                                url = self.clean_url(url, keep_playlist=False)
                                print(f"◎ Extracted video URL: {url}")
                                # Continue to single video download (skip playlist logic)
                
                if not is_youtube_mix:
                    print("⌕ Playlist detected in URL!")
                
                if no_playlist or is_youtube_mix:
                    # User explicitly wants only single video, or it's a Mix playlist
                    if not is_youtube_mix:
                        url = self.clean_url(url, keep_playlist=False)
                        print(f"ℹ  --no-playlist flag detected: downloading single item only")
                        print(f"◎ Downloading: {url}")
                elif interactive:
                    choice_options = [
                        "Download as playlist (all videos/songs)",
                        "Download single video (select from list)",
                        "Show playlist contents first"
                    ]
                    
                    choice = self.prompt_user_choice(
                        "This appears to be a playlist URL. What would you like to do?",
                        choice_options,
                        default="Show playlist contents first"
                    )
                    
                    if choice == "Download as playlist (all videos/songs)":
                        result = self.download_playlist(url, quality, audio_only, output_format, custom_format, interactive=interactive)
                        if result is None and "RD" in url and "list=" in url:
                            # YouTube Mix/Radio playlist - extract single video
                            print("→ Extracting single video from Mix/Radio URL...")
                            url = self.clean_url(url, keep_playlist=False)
                            print(f"◎ Extracted video URL: {url}")
                            # Continue to single video download below
                        else:
                            return result
                    elif choice == "Download single video (select from list)":
                        # Let user select which video from the playlist
                        selected_url = self.select_video_from_playlist(url)
                        if selected_url:
                            url = selected_url
                            print(f"◎ Downloading selected video: {url}")
                        else:
                            # Check if this is a Mix/Radio playlist (unviewable)
                            if "RD" in url and "list=" in url:
                                print("→ Extracting single video from Mix/Radio URL...")
                                url = self.clean_url(url, keep_playlist=False)
                                print(f"◎ Extracted video URL: {url}")
                                # Continue to single video download below
                            else:
                                print("✗ No video selected, cancelling download")
                                return None
                    elif choice == "Show playlist contents first":
                        playlist_info = self.show_playlist_contents(url)
                        if playlist_info is None and "RD" in url and "list=" in url:
                            # YouTube Mix/Radio playlist - extract single video
                            print("→ Extracting single video from Mix/Radio URL...")
                            url = self.clean_url(url, keep_playlist=False)
                            print(f"◎ Extracted video URL: {url}")
                            # Continue to single video download
                        elif playlist_info:
                            # Ask again after showing contents
                            download_choice = self.prompt_user_choice(
                                "Now what would you like to do?",
                                ["Download entire playlist", "Download single video (select from list)", "Cancel"],
                                default="Download entire playlist"
                            )
                            
                            if download_choice == "Download entire playlist":
                                try:
                                    result = self.download_playlist(url, quality, audio_only, output_format, custom_format, interactive=interactive)
                                    if result is None and "RD" in url and "list=" in url:
                                        # YouTube Mix/Radio playlist - extract single video
                                        print("→ Extracting single video from Mix/Radio URL...")
                                        url = self.clean_url(url, keep_playlist=False)
                                        print(f"◎ Extracted video URL: {url}")
                                        # Continue to single video download below
                                    else:
                                        return result
                                except Exception as e:
                                    if "unviewable" in str(e).lower() or ("mix" in url.lower() and "list=" in url):
                                        print("→ YouTube Mix/Radio playlist detected (unviewable), extracting single video...")
                                        url = self.clean_url(url, keep_playlist=False)
                                        print(f"◎ Extracted video URL: {url}")
                                        # Continue to single video download below
                                    else:
                                        raise
                            elif download_choice == "Download single video (select from list)":
                                # Let user select which video from the playlist
                                selected_url = self.select_video_from_playlist(url)
                                if selected_url:
                                    url = selected_url
                                    print(f"◎ Downloading selected video: {url}")
                                else:
                                    # Check if this is a Mix/Radio playlist (unviewable)
                                    if "RD" in url and "list=" in url:
                                        print("→ Extracting single video from Mix/Radio URL...")
                                        url = self.clean_url(url, keep_playlist=False)
                                        print(f"◎ Extracted video URL: {url}")
                                        # Continue to single video download below
                                    else:
                                        print("✗ No video selected, cancelling download")
                                        return None
                            elif download_choice == "Cancel":
                                print("✗ Download cancelled by user")
                                return None
                else:
                    # Non-interactive mode: download entire playlist automatically
                    print("ℹ  Playlist URL detected: downloading entire playlist automatically")
                    print("◎ Tip: Use --no-playlist flag to download single item only")
                    
                    # Try to download playlist, but fallback to single video if it fails
                    try:
                        result = self.download_playlist(url, quality, audio_only, output_format, custom_format, interactive=False)
                        if result is None and "RD" in url and "list=" in url:
                            # Playlist extraction failed (likely YouTube Mix), extract single video
                            print("→ Playlist extraction failed, attempting to download single video instead...")
                            url = self.clean_url(url, keep_playlist=False)
                            print(f"◎ Extracted video URL: {url}")
                            # Continue to single video download below
                        else:
                            return result
                    except Exception as e:
                        if "unviewable" in str(e).lower():
                            print("→ YouTube Mix/Radio playlist detected, extracting single video...")
                            url = self.clean_url(url, keep_playlist=False)
                            print(f"◎ Extracted video URL: {url}")
                            # Continue to single video download below
                        else:
                            raise
            
            # Platform-specific handling already done above for spotify/apple_music
            
            # For YouTube single videos, ask if user wants audio or video (if not already specified)
            if platform == 'youtube' and not self.is_playlist_url(url):
                if not audio_only and not custom_format and output_format is None:
                    # Ask user if they want audio or video
                    media_type_options = ["🎵 Audio Only (MP3/FLAC)", "🎬 Video + Audio (MP4)", "⚙️  Advanced (Custom Settings)"]
                    
                    if RICH_AVAILABLE and self.console:
                        self.console.print("\n[bold cyan]❓ What would you like to download?[/bold cyan]")
                    else:
                        print("\n❓ What would you like to download?")
                    
                    media_choice = self.prompt_user_choice(
                        "Select download type:",
                        media_type_options,
                        default=media_type_options[0]
                    )
                    
                    if media_choice == "🎵 Audio Only (MP3/FLAC)":
                        audio_only = True
                        # Ask for audio format
                        audio_format_options = ["MP3 (Universal)", "FLAC (Lossless)", "M4A (Apple)", "OPUS (High Efficiency)"]
                        format_choice = self.prompt_user_choice(
                            "Select audio format:",
                            audio_format_options,
                            default=audio_format_options[0]
                        )
                        
                        if format_choice == "MP3 (Universal)":
                            output_format = "mp3"
                        elif format_choice == "FLAC (Lossless)":
                            output_format = "flac"
                        elif format_choice == "M4A (Apple)":
                            output_format = "m4a"
                        elif format_choice == "OPUS (High Efficiency)":
                            output_format = "opus"
                        
                        if RICH_AVAILABLE and self.console:
                            self.console.print(f"[green]✓ Selected:[/green] Audio only ({output_format.upper()})")
                        else:
                            print(f"✓ Selected: Audio only ({output_format.upper()})")
                    
                    elif media_choice == "🎬 Video + Audio (MP4)":
                        audio_only = False
                        output_format = "mp4"
                        
                        # Ask for quality
                        quality_options = ["Best Available", "1080p (Full HD)", "720p (HD)", "480p (SD)"]
                        quality_choice = self.prompt_user_choice(
                            "Select video quality:",
                            quality_options,
                            default=quality_options[0]
                        )
                        
                        if quality_choice == "Best Available":
                            quality = "best"
                        elif quality_choice == "1080p (Full HD)":
                            quality = "1080p"
                        elif quality_choice == "720p (HD)":
                            quality = "720p"
                        elif quality_choice == "480p (SD)":
                            quality = "480p"
                        
                        if RICH_AVAILABLE and self.console:
                            self.console.print(f"[green]✓ Selected:[/green] Video ({quality})")
                        else:
                            print(f"✓ Selected: Video ({quality})")
                    
                    elif media_choice == "⚙️  Advanced (Custom Settings)":
                        # Fall through to interactive format selection below
                        pass
            
            # Interactive format selection
            if interactive and not custom_format and media_choice == "⚙️  Advanced (Custom Settings)" if 'media_choice' in locals() else (interactive and not custom_format):
                quality, audio_only, output_format, custom_format = self.prompt_format_selection(url)
            
            # Detect and prompt for audio language selection (YouTube videos)
            selected_language = None
            if platform == 'youtube' and not audio_language:
                # Detect available audio languages
                if RICH_AVAILABLE and self.console:
                    with self.console.status("[bold cyan]🔍 Detecting available audio languages...[/bold cyan]"):
                        languages = self.detect_audio_languages(url)
                else:
                    print("🔍 Detecting available audio languages...")
                    languages = self.detect_audio_languages(url)
                
                # If multiple languages found, prompt user (in interactive mode or always for multi-language)
                if languages and len(languages) > 1:
                    if interactive:
                        selected_language = self.prompt_audio_language_selection(languages)
                    else:
                        # Even in non-interactive mode, show languages and prompt
                        selected_language = self.prompt_audio_language_selection(languages)
                    
                    if selected_language:
                        if RICH_AVAILABLE and self.console:
                            self.console.print(f"[green]✓ Selected audio language: {selected_language['name']}[/green]")
                        else:
                            print(f"✓ Selected audio language: {selected_language['name']}")
                elif languages and len(languages) == 1:
                    # Only one language, download silently
                    if RICH_AVAILABLE and self.console:
                        self.console.print(f"[dim]ℹ Audio language: {languages[0]['name']}[/dim]")
                    else:
                        pass  # Don't display message for single language
            elif audio_language:
                # Audio language was specified via parameter
                if RICH_AVAILABLE and self.console:
                    self.console.print(f"[green]✓ Using specified audio language: {audio_language}[/green]")
                else:
                    print(f"✓ Using specified audio language: {audio_language}")
            
            # Configure yt-dlp options
            ydl_opts = self.default_ydl_opts.copy()
            
            # Set custom filename if provided
            if custom_filename:
                # Clean filename to remove invalid characters
                safe_filename = custom_filename.replace('/', '-').replace('\\', '-').replace(':', '-')
                ydl_opts['outtmpl'] = str(self.output_dir / f'{safe_filename}.%(ext)s')
            
            # Set format selector
            if custom_format:
                ydl_opts['format'] = custom_format
            else:
                base_format = self._get_format_selector(quality, audio_only)
                
                # Apply audio language filter if selected
                if selected_language and selected_language.get('code'):
                    lang_code = selected_language['code']  # Original code like en-US, es-MX, etc.
                    # Modify format selector to prefer the selected language
                    if audio_only:
                        # For audio-only downloads, filter by language
                        # Try exact match first, then fallback to base language, then any
                        ydl_opts['format'] = f"bestaudio[language={lang_code}]/bestaudio"
                    else:
                        # For video downloads, prefer audio track in selected language
                        # Split the format selector and add language preference
                        if '+' in base_format:
                            # Format like "bestvideo+bestaudio"
                            video_part, audio_part = base_format.split('+', 1)
                            ydl_opts['format'] = f"{video_part}+bestaudio[language={lang_code}]/{base_format}"
                        else:
                            # Fallback for other formats
                            ydl_opts['format'] = base_format
                elif audio_language:
                    # Use specified audio language parameter
                    # This could be either normalized (en) or specific (en-US)
                    # We need to handle both cases
                    if audio_only:
                        # Try the specified language and common variants
                        ydl_opts['format'] = f"bestaudio[language^={audio_language}]/bestaudio[language={audio_language}]/bestaudio"
                    else:
                        base_video = base_format.split('+')[0] if '+' in base_format else 'bestvideo'
                        ydl_opts['format'] = f"{base_video}+bestaudio[language^={audio_language}]/{base_video}+bestaudio[language={audio_language}]/{base_format}"
                else:
                    ydl_opts['format'] = base_format
            
            # Set output format and post-processors with enhanced quality settings
            if output_format:
                if audio_only and output_format.lower() in ['mp3', 'wav', 'flac', 'aac', 'm4a', 'opus']:
                    # Enhanced quality settings for different formats
                    quality_settings = {
                        'mp3': '320',      # 320kbps for MP3
                        'aac': '256',      # 256kbps for AAC
                        'm4a': '256',      # 256kbps for M4A
                        'opus': '256',     # 256kbps for Opus
                        'flac': '0',       # Lossless for FLAC
                        'wav': '0',        # Lossless for WAV
                    }
                    
                    ydl_opts['postprocessors'] = [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': output_format.lower(),
                        'preferredquality': quality_settings.get(output_format.lower(), '320'),
                        'nopostoverwrites': False,
                    }]
                elif not audio_only and output_format.lower() in ['mp4', 'mkv', 'avi', 'webm', 'mov']:
                    ydl_opts['merge_output_format'] = output_format.lower()
            
            # Enhanced thumbnail and metadata support with artist cover art preference
            if add_thumbnail:
                ydl_opts['writethumbnail'] = True
                
                # Add thumbnail embedding for audio files with enhanced options
                if audio_only:
                    if 'postprocessors' not in ydl_opts:
                        ydl_opts['postprocessors'] = []
                    
                    # Enhanced thumbnail embedding with better quality settings
                    ydl_opts['postprocessors'].append({
                        'key': 'EmbedThumbnail',
                        'already_have_thumbnail': False,
                    })
                    
                    # Add comprehensive metadata processor
                    ydl_opts['postprocessors'].append({
                        'key': 'FFmpegMetadata',
                        'add_metadata': True,
                        'add_chapters': True,
                        'add_infojson': False,  # Don't embed the entire JSON
                    })
            
            # Enhanced metadata support even without thumbnail
            elif add_metadata and audio_only:
                if 'postprocessors' not in ydl_opts:
                    ydl_opts['postprocessors'] = []
                ydl_opts['postprocessors'].append({
                    'key': 'FFmpegMetadata',
                    'add_metadata': True,
                    'add_chapters': True,
                })
            
            # Always enable basic metadata and thumbnails for audio files if not specified
            elif audio_only:
                ydl_opts['writethumbnail'] = True
                if 'postprocessors' not in ydl_opts:
                    ydl_opts['postprocessors'] = []
                ydl_opts['postprocessors'].extend([{
                    'key': 'EmbedThumbnail',
                    'already_have_thumbnail': False,
                }, {
                    'key': 'FFmpegMetadata',
                    'add_metadata': True,
                    'add_chapters': True,
                }])
            
            # Add progress hook using new ProgressDisplay module
            ydl_opts['progress_hooks'] = [ProgressDisplay.progress_hook]
            
            # Download
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                print(f"▶ Starting download: {url}")
                
                # Get info first
                info = ydl.extract_info(url, download=False)
                if info:
                    print(f"\n▶ MEDIA INFO:")
                    print(f"▶ Title: {info.get('title', 'Unknown')}")
                    print(f"◷️  Duration: {self._format_duration(info.get('duration', 0))}")
                    print(f"◈ Uploader: {info.get('uploader', 'Unknown')}")
                    
                    # Show additional info if available
                    if info.get('view_count'):
                        print(f"👀 Views: {info.get('view_count'):,}")
                    if info.get('upload_date'):
                        print(f"📅 Upload Date: {info.get('upload_date')}")
                    if info.get('like_count'):
                        print(f"👍 Likes: {info.get('like_count'):,}")
                    
                    # Show download settings
                    print(f"\n⚙  DOWNLOAD SETTINGS:")
                    print(f"◎ Quality: {quality}")
                    print(f"♫ Audio only: {'Yes' if audio_only else 'No'}")
                    if output_format:
                        print(f"▭ Output format: {output_format.upper()}")
                    if custom_format:
                        print(f"🔧 Custom format: {custom_format}")
                    # Show selected audio language if available
                    if selected_language:
                        print(f"🌐 Audio language: {selected_language['name']}")
                    elif audio_language:
                        print(f"🌐 Audio language: {audio_language}")
                
                # Start download
                if RICH_AVAILABLE and self.console:
                    download_msg = "\n[bold green]▸ Starting download...[/bold green]"
                    if selected_language and len(selected_language) > 1:
                        download_msg += f"\n[cyan]🌐 Downloading in {selected_language['name']}[/cyan]"
                    self.console.print(download_msg)
                else:
                    print("\n▸ Starting download...")
                
                # Track download success
                download_result = ydl.download([url])
                
                # Check if download actually succeeded
                # yt-dlp returns 0 on success, non-zero on failure
                download_succeeded = (download_result == 0)
                
                # Enhanced check: Also verify if any file was actually downloaded
                if download_succeeded and info:
                    title = info.get('title', 'Unknown')
                    uploader = info.get('uploader') or 'Unknown'
                    
                    # Look for downloaded files with multiple patterns
                    # yt-dlp sanitizes filenames, replacing characters like | with ｜
                    # Clean the strings for glob patterns - remove special glob characters
                    title_clean = (title or 'Unknown')[:40].replace('|', '').replace('/', '').replace('\\', '').replace('*', '').replace('?', '').replace('[', '').replace(']', '')
                    uploader_clean = (uploader or 'Unknown')[:20].replace('|', '').replace('/', '').replace('\\', '').replace('*', '').replace('?', '').replace('[', '').replace(']', '')
                    
                    # Search for files with any of these extensions
                    extensions = ['.mp3', '.m4a', '.webm', '.mp4', '.mkv', '.flac', '.opus']
                    downloaded_files = []
                    
                    for ext in extensions:
                        # Try multiple search patterns
                        # Clean patterns to avoid glob syntax errors
                        if title_clean:
                            title_pattern = ''.join(c for c in title_clean[:20] if c.isalnum() or c in ' -_')
                            if title_pattern.strip():
                                try:
                                    files = list(self.output_dir.glob(f"*{title_pattern[:15]}*{ext}"))
                                    if files:
                                        downloaded_files.extend(files)
                                        break
                                except:
                                    pass
                        
                        if uploader_clean and not downloaded_files:
                            uploader_pattern = ''.join(c for c in uploader_clean if c.isalnum() or c in ' -_')
                            if uploader_pattern.strip():
                                try:
                                    files = list(self.output_dir.glob(f"*{uploader_pattern[:15]}*{ext}"))
                                    if files:
                                        downloaded_files.extend(files)
                                        break
                                except:
                                    pass
                        
                        if downloaded_files:
                            break
                    
                    if not downloaded_files:
                        # Last resort: check for any recently created files
                        import time
                        current_time = time.time()
                        recent_files = [f for f in self.output_dir.iterdir() 
                                      if f.is_file() and (current_time - f.stat().st_mtime) < 60]
                        
                        if recent_files:
                            download_succeeded = True
                            self.print_rich(f"  [dim]✓ Found downloaded file: {recent_files[0].name}[/dim]")
                        else:
                            # No files found, download likely failed
                            download_succeeded = False
                
                if not self.cancelled and download_succeeded:
                    # Show beautiful completion message
                    if RICH_AVAILABLE and self.console:
                        completion_msg = """[bold green]✦ Download completed successfully! ✦[/bold green]
[cyan]🎉 Your media is ready![/cyan]"""
                        self.print_panel(completion_msg, title="🎊 SUCCESS", border_style="green")
                    else:
                        print("\n✓ Download completed successfully!")
                elif not self.cancelled and not download_succeeded:
                    # Download failed
                    if RICH_AVAILABLE and self.console:
                        error_msg = """[bold red]✗ Download failed![/bold red]
[yellow]⚠  The video could not be downloaded. Possible reasons:[/yellow]
[dim]• The URL is not supported or requires authentication
• The video is private, deleted, or region-restricted
• The site has anti-bot protection enabled
• Network connection issues[/dim]"""
                        self.print_panel(error_msg, title="❌ DOWNLOAD FAILED", border_style="red")
                    else:
                        print("\n✗ Download failed!")
                        print("⚠  The video could not be downloaded")
                    return None
                
                if download_succeeded:
                    # Show downloaded file info
                    if info:
                        title = info.get('title', 'Unknown')
                        artist = info.get('artist') or info.get('uploader', 'Unknown')
                        ext = 'mp3' if audio_only else 'mp4'
                        if output_format:
                            ext = output_format.lower()
                        
                        # Determine expected filename - use custom filename if provided
                        if custom_filename:
                            # Custom filename was provided
                            safe_custom = custom_filename.replace('/', '-').replace('\\', '-').replace(':', '-')
                            expected_filename = f"{safe_custom}.{ext}"
                        else:
                            # Default filename format
                            expected_filename = f"{artist} - {title}.{ext}"
                        
                        downloaded_file_path = self.output_dir / expected_filename
                        
                        # Verify the expected file actually exists
                        actual_file = None
                        if downloaded_file_path.exists():
                            actual_file = downloaded_file_path
                        else:
                            # yt-dlp sanitizes filenames, so we need to search for the actual file
                            # Check for recently modified files first (most reliable)
                            import time
                            current_time = time.time()
                            recent_files = [f for f in self.output_dir.iterdir() 
                                          if f.is_file() and (current_time - f.stat().st_mtime) < 60]
                            
                            if recent_files:
                                # Find files with the correct extension
                                possible_extensions = [f'.{ext}', '.mp4', '.webm', '.mkv', '.avi', '.mov', '.mp3', '.m4a', '.flac', '.wav', '.opus']
                                for check_ext in possible_extensions:
                                    ext_matches = [f for f in recent_files if f.suffix.lower() == check_ext]
                                    if ext_matches:
                                        # Take the most recently modified file
                                        actual_file = max(ext_matches, key=lambda p: p.stat().st_mtime)
                                        
                                        if check_ext.lower() != f".{ext}":
                                            print(f"  ℹ  File downloaded as {check_ext} format instead of requested .{ext}")
                                        
                                        # Try to convert to requested format if different (for video files)
                                        if not audio_only and output_format and check_ext.lower() != f".{ext}":
                                            print(f"  ⟳ Converting {check_ext} to .{ext}...")
                                            try:
                                                converted_path = self._convert_video_format(str(actual_file), ext)
                                                if converted_path and Path(converted_path).exists():
                                                    old_file = actual_file
                                                    actual_file = Path(converted_path)
                                                    downloaded_file_path = actual_file
                                                    # Remove the original file after successful conversion
                                                    try:
                                                        old_file.unlink()
                                                    except:
                                                        pass
                                                    print(f"  ✓ Converted to: {actual_file.name}")
                                                else:
                                                    print(f"  ⚠  Conversion failed, keeping original format")
                                            except Exception as e:
                                                print(f"  ⚠  Conversion error: {e}, keeping original format")
                                        break
                            
                            # If still not found, try pattern matching as fallback
                            if not actual_file:
                                title_pattern = title[:40].replace('|', '*').replace('/', '*').replace('\\', '*')
                                possible_extensions = ['.mp4', '.webm', '.mkv', '.avi', '.mov', '.mp3', '.m4a', '.flac', '.wav', '.opus']
                                
                                for alt_ext in possible_extensions:
                                    try:
                                        matching_files = list(self.output_dir.glob(f"*{title_pattern}*{alt_ext}"))
                                        if matching_files:
                                            actual_file = max(matching_files, key=lambda p: p.stat().st_mtime)
                                            break
                                    except:
                                        pass
                        
                        # Only show success if file actually exists
                        if actual_file and actual_file.exists():
                            print(f"📁 File saved as: {actual_file.name}")
                            print(f"▸ Location: {self.output_dir}")
                            downloaded_file_path = actual_file
                            
                            # Enhanced post-processing for audio files
                            if audio_only and downloaded_file_path.exists():
                                print("\n◨ Applying enhanced post-processing...")
                                
                                # Fetch and embed album art from Spotify/Apple Music
                                if platform not in ['spotify', 'apple_music']:  # Only if not from streaming service
                                    self._enhance_audio_with_metadata(
                                        str(downloaded_file_path),
                                        title,
                                        artist,
                                        fetch_from_streaming=True
                                    )
                                
                                # Convert to true lossless if FLAC or WAV requested
                                if output_format and output_format.lower() in ['flac', 'wav']:
                                    print(f"\n⟳ Converting to true {output_format.upper()} format...")
                                    converted_path = self._convert_to_true_lossless(
                                        str(downloaded_file_path),
                                        target_format=output_format.lower()
                                    )
                                    if converted_path != str(downloaded_file_path):
                                        downloaded_file_path = Path(converted_path)
                                        print(f"✓ Converted to: {downloaded_file_path.name}")
                            
                            # Cleanup intermediate files (thumbnails, json, etc.)
                            self._cleanup_intermediate_files(info, audio_only, output_format, str(actual_file))
                        else:
                            # File not found - this shouldn't happen but handle gracefully
                            # Check one more time for ANY recent file
                            import time
                            current_time = time.time()
                            any_recent_files = [f for f in self.output_dir.iterdir() 
                                              if f.is_file() and (current_time - f.stat().st_mtime) < 120]
                            
                            if any_recent_files:
                                # File was downloaded but we can't find it with expected name
                                latest_file = max(any_recent_files, key=lambda p: p.stat().st_mtime)
                                print(f"✓ File downloaded successfully!")
                                print(f"📁 File saved as: {latest_file.name}")
                                print(f"▸ Location: {self.output_dir}")
                                # Don't mark as failed since file exists
                            else:
                                print(f"⚠  Warning: Expected file not found: {expected_filename}")
                                print(f"⚠  Download may have failed or file was saved with a different name")
                                download_succeeded = False
                
                # Only return info if download succeeded
                return info if download_succeeded else None
                
        except KeyboardInterrupt:
            print("\n✗ Download cancelled by user")
            return None
        except Exception as e:
            error_msg = str(e)
            print(f"\n✗ Error downloading media: {error_msg}")
            
            # Print full traceback for debugging
            import traceback
            print(f"\n⌕ Full error details:")
            traceback.print_exc()
            
            # Try to provide helpful error messages
            if "video unavailable" in error_msg.lower():
                print("→ Tip: The video might be private, deleted, or region-restricted")
            elif "format not available" in error_msg.lower():
                print("→ Tip: Try a different quality setting or use --show-formats to see available options")
            elif "ffmpeg" in error_msg.lower() or "avconv" in error_msg.lower():
                print("→ Tip: FFmpeg might not be installed or not in PATH. Install it with:")
                print("   macOS: brew install ffmpeg")
                print("   Ubuntu/Debian: sudo apt-get install ffmpeg")
                print("   Windows: Download from https://ffmpeg.org/download.html")
            elif not error_msg or error_msg.strip() == "":
                print("→ Tip: An unknown error occurred. The video might be unavailable or have restricted access")
            
            # Try generic downloader as last resort
            if platform == 'generic' and GENERIC_DOWNLOADER_AVAILABLE:
                print(f"\n{'='*80}")
                print("🔥 ATTEMPTING ADVANCED GENERIC DOWNLOADER")
                print(f"{'='*80}")
                print("ℹ  yt-dlp failed, trying alternative methods with SSL/TLS bypass...")
                
                try:
                    generic_dl = GenericSiteDownloader(self.output_dir, verbose=True)
                    result_file = generic_dl.download(url)
                    
                    if result_file:
                        print(f"\n✅ SUCCESS with advanced downloader!")
                        print(f"📥 Downloaded: {result_file}")
                        
                        # Return a mock info dict for compatibility
                        return {
                            'title': Path(result_file).stem,
                            'filepath': result_file,
                            'ext': Path(result_file).suffix[1:],
                        }
                    else:
                        print("\n❌ Advanced downloader also failed")
                except Exception as generic_error:
                    print(f"❌ Advanced downloader error: {generic_error}")
            
            # Don't fail completely, return None to continue with other tracks
            return None
    
    def download_batch_optimized(self, urls, quality="best", audio_only=False, output_format=None, max_concurrent=3):
        """
        Optimized batch download with parallel processing and smart queue management
        
        Args:
            urls: List of URLs to download
            quality: Quality setting for all downloads
            audio_only: Download audio only
            output_format: Output format (mp3, flac, opus, m4a, etc.)
            max_concurrent: Maximum concurrent downloads (default: 3)
        """
        if not urls:
            print("✗ No URLs provided for batch download")
            return []
        
        print(f"▸ Starting optimized batch download of {len(urls)} items")
        print(f"⚙  Settings: Quality={quality}, Audio Only={audio_only}, Format={output_format or 'default'}")
        print(f"⟳ Max concurrent downloads: {max_concurrent}")
        
        successful_downloads = []
        failed_downloads = []
        
        def download_single_threaded(url_info):
            """Download a single URL in a thread"""
            url, index = url_info
            try:
                print(f"\n↓ [{index+1}/{len(urls)}] Starting: {url}")
                
                # Create thread-specific downloader to avoid conflicts
                thread_downloader = UltimateMediaDownloader(self.output_dir)
                
                # Use enhanced settings for better performance
                result = thread_downloader.download_media(
                    url=url,
                    quality=quality,
                    audio_only=audio_only,
                    output_format=output_format,
                    add_metadata=True,
                    add_thumbnail=True
                )
                
                if result:
                    successful_downloads.append((url, result))
                    print(f"✓ [{index+1}/{len(urls)}] Completed: {result.get('title', 'Unknown')}")
                else:
                    failed_downloads.append(url)
                    print(f"✗ [{index+1}/{len(urls)}] Failed: {url}")
                    
            except Exception as e:
                failed_downloads.append(url)
                print(f"✗ [{index+1}/{len(urls)}] Error: {e}")
        
        # Use ThreadPoolExecutor for controlled parallel downloads
        try:
            with ThreadPoolExecutor(max_workers=max_concurrent) as executor:
                # Submit all download tasks
                url_with_index = [(url, i) for i, url in enumerate(urls)]
                futures = [executor.submit(download_single_threaded, url_info) for url_info in url_with_index]
                
                # Wait for all downloads to complete
                for future in futures:
                    try:
                        future.result(timeout=3600)  # 1 hour timeout per download
                    except TimeoutError:
                        print("⚠  Download timed out after 1 hour")
                    except Exception as e:
                        print(f"⚠  Thread execution error: {e}")
        
        except KeyboardInterrupt:
            print("\n✗ Batch download cancelled by user")
        
        # Print summary
        print(f"\n▤ BATCH DOWNLOAD SUMMARY:")
        print(f"✓ Successful: {len(successful_downloads)}")
        print(f"✗ Failed: {len(failed_downloads)}")
        print(f"▤ Success rate: {len(successful_downloads)/len(urls)*100:.1f}%")
        
        if failed_downloads:
            print(f"\n✗ Failed URLs:")
            for i, url in enumerate(failed_downloads, 1):
                print(f"  {i}. {url}")
        
        return successful_downloads
    
    def show_playlist_contents(self, url, max_display=20):
        """Display playlist contents for user review"""
        try:
            print("⌕ Extracting playlist information...")
            
            # For YouTube URLs with both video and playlist, convert to playlist URL
            if "youtube.com" in url and "watch?v=" in url and "list=" in url:
                parsed = urlparse(url)
                params = parse_qs(parsed.query)
                if 'list' in params:
                    # Convert to playlist URL to force playlist extraction
                    list_id = params['list'][0]
                    url = f"https://www.youtube.com/playlist?list={list_id}"
            
            ydl_opts = self.default_ydl_opts.copy()
            ydl_opts.update({
                'quiet': True,
                'extract_flat': 'in_playlist',  # Fast extraction for listing
                'noplaylist': False,
                'yes_playlist': True,  # Force playlist extraction
            })
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                
                if not info or not info.get('entries'):
                    print("✗ No playlist found or playlist is empty")
                    return None
                
                entries = [entry for entry in info['entries'] if entry]  # Filter out None entries
                total_videos = len(entries)
                
                print("\n" + "="*80)
                print(f"≡ PLAYLIST: {info.get('title', 'Unknown Playlist')}")
                print("="*80)
                print(f"◈ Creator: {info.get('uploader', 'Unknown')}")
                print(f"▤ Total videos: {total_videos}")
                print(f"📅 Playlist URL: {info.get('webpage_url', url)}")
                
                if info.get('description'):
                    desc = info['description'][:150] + '...' if len(info['description']) > 150 else info['description']
                    print(f"▭ Description: {desc}")
                
                print("\n♫ PLAYLIST CONTENTS:")
                print("-" * 80)
                
                # Display videos
                display_count = min(max_display, total_videos)
                for i, entry in enumerate(entries[:display_count], 1):
                    if entry:
                        title = entry.get('title', 'Unknown Title')
                        duration = self._format_duration(entry.get('duration', 0))
                        uploader = entry.get('uploader', 'Unknown')
                        
                        # Truncate long titles
                        if len(title) > 50:
                            title = title[:47] + "..."
                        
                        print(f"{i:3d}. {title:<50} | {duration:>8} | {uploader}")
                
                if total_videos > max_display:
                    print(f"     ... and {total_videos - max_display} more videos")
                
                print("-" * 80)
                return info
                
        except Exception as e:
            error_msg = str(e)
            print(f"✗ Error extracting playlist: {e}")
            
            # Check if this is a YouTube Mix/Radio playlist error
            if "unviewable" in error_msg.lower() or "mix" in url.lower() or "RD" in url:
                print("ℹ  This appears to be a YouTube Mix/Radio playlist (unviewable)")
                print("→ Attempting to extract single video from the URL...")
                return None  # Signal that we should try single video extraction
            
            return None
    
    def select_video_from_playlist(self, url):
        """Allow user to select a specific video from playlist
        
        Args:
            url: Playlist URL
            
        Returns:
            Selected video URL or None if cancelled
        """
        try:
            print("⌕ Loading playlist videos...")
            
            # For YouTube URLs with both video and playlist, convert to playlist URL
            if "youtube.com" in url and "watch?v=" in url and "list=" in url:
                parsed = urlparse(url)
                params = parse_qs(parsed.query)
                if 'list' in params:
                    list_id = params['list'][0]
                    url = f"https://www.youtube.com/playlist?list={list_id}"
            
            ydl_opts = self.default_ydl_opts.copy()
            ydl_opts.update({
                'quiet': True,
                'extract_flat': 'in_playlist',
                'noplaylist': False,
                'yes_playlist': True,
            })
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                
                if not info or not info.get('entries'):
                    print("✗ No playlist found or playlist is empty")
                    return None
                
                entries = [entry for entry in info['entries'] if entry]
                total_videos = len(entries)
                
                # Show playlist info
                if RICH_AVAILABLE and self.console:
                    self.console.print(f"\n[bold cyan]≡ PLAYLIST:[/bold cyan] [yellow]{info.get('title', 'Unknown')}[/yellow]")
                    self.console.print(f"[cyan]▤ Total videos:[/cyan] [green]{total_videos}[/green]\n")
                else:
                    print(f"\n≡ PLAYLIST: {info.get('title', 'Unknown')}")
                    print(f"▤ Total videos: {total_videos}\n")
                
                # Display all videos with numbers
                print("♫ PLAYLIST VIDEOS:")
                print("-" * 80)
                
                for i, entry in enumerate(entries, 1):
                    if entry:
                        title = entry.get('title', 'Unknown Title')
                        duration = self._format_duration(entry.get('duration', 0))
                        
                        # Truncate long titles
                        if len(title) > 60:
                            title = title[:57] + "..."
                        
                        print(f"{i:3d}. {title:<60} | {duration:>8}")
                
                print("-" * 80)
                
                # Prompt user to select a video
                while True:
                    if RICH_AVAILABLE and self.console:
                        from rich.prompt import Prompt
                        selection = Prompt.ask(
                            f"\n[bold cyan]Select video number[/bold cyan] [dim](1-{total_videos}, or 'c' to cancel)[/dim]",
                            default="1"
                        )
                    else:
                        selection = input(f"\nSelect video number (1-{total_videos}, or 'c' to cancel) [1]: ").strip() or "1"
                    
                    if selection.lower() == 'c':
                        print("✗ Selection cancelled")
                        return None
                    
                    try:
                        video_num = int(selection)
                        if 1 <= video_num <= total_videos:
                            selected_entry = entries[video_num - 1]
                            video_url = selected_entry.get('url') or selected_entry.get('webpage_url')
                            
                            # For YouTube, construct the URL from video ID
                            if not video_url and selected_entry.get('id'):
                                video_url = f"https://www.youtube.com/watch?v={selected_entry['id']}"
                            
                            if video_url:
                                selected_title = selected_entry.get('title', 'Unknown')
                                if RICH_AVAILABLE and self.console:
                                    self.console.print(f"\n[green]✓ Selected:[/green] [bold]{selected_title}[/bold]")
                                else:
                                    print(f"\n✓ Selected: {selected_title}")
                                return video_url
                            else:
                                print("✗ Could not get video URL")
                                return None
                        else:
                            print(f"⚠ Please enter a number between 1 and {total_videos}")
                    except ValueError:
                        print("⚠ Please enter a valid number or 'c' to cancel")
                        
        except Exception as e:
            error_msg = str(e)
            print(f"✗ Error selecting video from playlist: {e}")
            
            # Check if this is a YouTube Mix/Radio playlist error
            if "unviewable" in error_msg.lower() or "mix" in url.lower() or "RD" in url:
                print("ℹ  This appears to be a YouTube Mix/Radio playlist (unviewable)")
                print("→ Cannot select from unviewable playlist. Will extract single video from URL.")
                return None  # Signal that we should try single video extraction
            
            return None
    
    def download_playlist(self, url, quality="best", audio_only=False, output_format=None, custom_format=None, max_downloads=None, start_index=1, interactive=True):
        """Download playlist with enhanced options and user interaction"""
        try:
            # For YouTube URLs with both video and playlist, convert to playlist URL
            if "youtube.com" in url and "watch?v=" in url and "list=" in url:
                parsed = urlparse(url)
                params = parse_qs(parsed.query)
                if 'list' in params:
                    # Convert to playlist URL to force playlist extraction
                    list_id = params['list'][0]
                    url = f"https://www.youtube.com/playlist?list={list_id}"
            
            platform = self.detect_platform(url)
            if RICH_AVAILABLE and self.console:
                self.console.print(f"[bold cyan]→[/bold cyan] Detected platform: [cyan]{platform.upper()}[/cyan]")
            else:
                print(f"→ Detected platform: {platform.upper()}")
            
            # Show playlist contents first
            playlist_info = self.show_playlist_contents(url)
            if not playlist_info:
                # Return None to signal failure (caller can try single video download)
                return None
            
            total_videos = len([e for e in playlist_info.get('entries', []) if e])
            
            if interactive:
                if RICH_AVAILABLE and self.console:
                    self.console.print(f"\n[bold white]DOWNLOAD OPTIONS[/bold white]")
                else:
                    print(f"\nDOWNLOAD OPTIONS")
                print("=" * 50)
                
                # Ask how many to download
                download_options = [
                    f"Download all {total_videos} videos",
                    "Download specific range",
                    "Download first N videos",
                    "Cancel download"
                ]
                
                download_choice = self.prompt_user_choice(
                    "What would you like to download?",
                    download_options,
                    default=download_options[0]
                )
                
                if download_choice == "Cancel download":
                    print("✗ Download cancelled by user")
                    return
                
                elif download_choice == "Download specific range":
                    while True:
                        try:
                            start_input = input(f"Start from video number (1-{total_videos}): ").strip()
                            start_index = int(start_input) if start_input else 1
                            
                            end_input = input(f"End at video number ({start_index}-{total_videos}): ").strip()
                            end_index = int(end_input) if end_input else total_videos
                            
                            if 1 <= start_index <= end_index <= total_videos:
                                max_downloads = end_index - start_index + 1
                                break
                            else:
                                print("Invalid range. Please try again.")
                        except ValueError:
                            print("Please enter valid numbers.")
                
                elif download_choice == "Download first N videos":
                    while True:
                        try:
                            max_input = input(f"How many videos to download (1-{total_videos}): ").strip()
                            max_downloads = int(max_input) if max_input else total_videos
                            if 1 <= max_downloads <= total_videos:
                                start_index = 1  # Reset to 1 for "first N"
                                break
                            else:
                                print(f"Please enter a number between 1 and {total_videos}")
                        except ValueError:
                            print("Please enter a valid number.")
                
                # Ask for quality and format selection
                if RICH_AVAILABLE and self.console:
                    self.console.print(f"\n[bold white]QUALITY & FORMAT OPTIONS[/bold white]")
                    self.console.print("=" * 50)
                else:
                    print(f"\nQUALITY & FORMAT OPTIONS")
                    print("=" * 50)
                
                # Ask if audio only or video
                media_type_options = ["Audio Only (Music)", "Video + Audio", "Video Only"]
                media_type_choice = self.prompt_user_choice(
                    "What type of media?",
                    media_type_options,
                    default="Audio Only (Music)"
                )
                
                audio_only = (media_type_choice == "Audio Only (Music)")
                
                if audio_only:
                    # Audio quality and format selection
                    format_options = [
                        "FLAC (Lossless, Largest file)",
                        "WAV (Lossless, Uncompressed)",
                        "OPUS (High quality, Smaller)",
                        "MP3 320kbps (Standard)",
                        "M4A/AAC (Apple format)",
                    ]
                    format_choice = self.prompt_user_choice(
                        "Select audio format:",
                        format_options,
                        default="FLAC (Lossless, Largest file)"
                    )
                    
                    format_map = {
                        "FLAC (Lossless, Largest file)": "flac",
                        "WAV (Lossless, Uncompressed)": "wav",
                        "OPUS (High quality, Smaller)": "opus",
                        "MP3 320kbps (Standard)": "mp3",
                        "M4A/AAC (Apple format)": "m4a",
                    }
                    output_format = format_map[format_choice]
                    quality = "best"  # Always use best quality for audio
                    
                else:
                    # Video quality selection
                    quality_options = [
                        "Best (4K/2160p if available)",
                        "1440p (2K)",
                        "1080p (Full HD)",
                        "720p (HD)",
                        "480p (SD)",
                        "360p (Low quality)"
                    ]
                    quality_choice = self.prompt_user_choice(
                        "Select video quality:",
                        quality_options,
                        default="1080p (Full HD)"
                    )
                    
                    quality_map = {
                        "Best (4K/2160p if available)": "best",
                        "1440p (2K)": "1440p",
                        "1080p (Full HD)": "1080p",
                        "720p (HD)": "720p",
                        "480p (SD)": "480p",
                        "360p (Low quality)": "360p"
                    }
                    quality = quality_map[quality_choice]
                    
                    # Ask for video format
                    video_format_options = ["MP4 (Compatible)", "MKV (High quality)", "WEBM (Smaller size)"]
                    video_format_choice = self.prompt_user_choice(
                        "Select video format:",
                        video_format_options,
                        default="MP4 (Compatible)"
                    )
                    
                    video_format_map = {
                        "MP4 (Compatible)": "mp4",
                        "MKV (High quality)": "mkv",
                        "WEBM (Smaller size)": "webm"
                    }
                    output_format = video_format_map[video_format_choice]
                
                # Confirm download
                actual_downloads = max_downloads if max_downloads else total_videos
                if RICH_AVAILABLE and self.console:
                    self.console.print(f"\n[bold green]→[/bold green] Ready to download [cyan]{actual_downloads}[/cyan] items starting from [cyan]#{start_index}[/cyan]")
                    self.console.print(f"[bold white]Format:[/bold white] [cyan]{output_format.upper()}[/cyan]")
                    self.console.print(f"[bold white]Quality:[/bold white] [cyan]{'Audio Only - ' + output_format.upper() if audio_only else quality}[/cyan]")
                else:
                    print(f"\n→ Ready to download {actual_downloads} items starting from #{start_index}")
                    print(f"Format: {output_format.upper()}")
                    print(f"Quality: {'Audio Only - ' + output_format.upper() if audio_only else quality}")
                
                confirm = input("Continue? (y/n): ").strip().lower()
                if confirm not in ['y', 'yes', '']:
                    if RICH_AVAILABLE and self.console:
                        self.console.print("[bold red]✗[/bold red] Download cancelled by user")
                    else:
                        print("✗ Download cancelled by user")
                    return
            
            # Configure download options
            ydl_opts = self.default_ydl_opts.copy()
            ydl_opts.update({
                'outtmpl': str(self.output_dir / '%(playlist)s/%(playlist_index)03d - %(title)s.%(ext)s'),
                'noplaylist': False,
                'playliststart': start_index,
                'extract_flat': False,  # Get full info for each video
            })
            
            # Set format
            if custom_format:
                ydl_opts['format'] = custom_format
            else:
                ydl_opts['format'] = self._get_format_selector(quality, audio_only)
            
            if max_downloads:
                ydl_opts['playlistend'] = start_index + max_downloads - 1
            
            # Set output format and post-processors
            if output_format:
                if audio_only and output_format.lower() in ['mp3', 'wav', 'flac', 'aac', 'm4a', 'opus']:
                    ydl_opts['postprocessors'] = [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': output_format.lower(),
                        'preferredquality': '320' if output_format.lower() == 'mp3' else '0',
                    }]
                elif not audio_only and output_format.lower() in ['mp4', 'mkv', 'avi', 'webm', 'mov']:
                    ydl_opts['merge_output_format'] = output_format.lower()
            
            ydl_opts['progress_hooks'] = [self._progress_hook]
            
            # Track current file for metadata enhancement
            self._current_playlist_dir = str(self.output_dir / playlist_info.get('title', 'Unknown'))
            self._playlist_audio_only = audio_only
            self._playlist_format = output_format
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                if RICH_AVAILABLE and self.console:
                    self.console.print(f"\n[bold cyan]▶[/bold cyan] Starting playlist download...", style="bold")
                else:
                    print(f"\n▶ Starting playlist download...")
                
                actual_downloads = max_downloads if max_downloads else total_videos
                
                if RICH_AVAILABLE and self.console:
                    self.console.print(f"[bold white]Downloading {actual_downloads} items from:[/bold white] [cyan]{playlist_info.get('title', 'Unknown')}[/cyan]")
                else:
                    print(f"Downloading {actual_downloads} items from: {playlist_info.get('title', 'Unknown')}")
                
                ydl.download([url])
                
                # Post-process: Add album art to audio files
                if audio_only and output_format in ['flac', 'mp3', 'm4a']:
                    self._add_album_art_to_playlist(self._current_playlist_dir)
                
                if RICH_AVAILABLE and self.console:
                    self.console.print(f"\n[bold green]✓[/bold green] Playlist download completed!", style="bold green")
                else:
                    print("\n✓ Playlist download completed!")
                
        except KeyboardInterrupt:
            if RICH_AVAILABLE and self.console:
                self.console.print("\n[bold red]✗[/bold red] Download cancelled by user")
            else:
                print("\n✗ Download cancelled by user")
        except Exception as e:
            if RICH_AVAILABLE and self.console:
                self.console.print(f"[bold red]✗[/bold red] Error downloading playlist: [red]{str(e)}[/red]")
            else:
                print(f"✗ Error downloading playlist: {str(e)}")
    
    def _get_format_selector(self, quality, audio_only):
        """Get format selector string for yt-dlp with enhanced audio quality support"""
        if audio_only:
            # Prioritize high-quality audio formats: FLAC > Opus > M4A > AAC > MP3
            return ('bestaudio[acodec=flac]/bestaudio[acodec=opus]/bestaudio[acodec=m4a]/'
                   'bestaudio[acodec=aac]/bestaudio[abr>=320]/bestaudio[abr>=256]/'
                   'bestaudio[abr>=192]/bestaudio/best')
        
        quality_map = {
            'best': 'bestvideo[height<=2160]+bestaudio[acodec=flac]/bestvideo[height<=2160]+bestaudio[acodec=opus]/bestvideo+bestaudio/best',
            'worst': 'worst',
            '1080p': 'bestvideo[height<=1080]+bestaudio[acodec=flac]/bestvideo[height<=1080]+bestaudio[acodec=opus]/bestvideo[height<=1080]+bestaudio/best[height<=1080]',
            '720p': 'bestvideo[height<=720]+bestaudio[acodec=flac]/bestvideo[height<=720]+bestaudio[acodec=opus]/bestvideo[height<=720]+bestaudio/best[height<=720]',
            '480p': 'bestvideo[height<=480]+bestaudio[acodec=flac]/bestvideo[height<=480]+bestaudio[acodec=opus]/bestvideo[height<=480]+bestaudio/best[height<=480]',
            '360p': 'bestvideo[height<=360]+bestaudio[acodec=flac]/bestvideo[height<=360]+bestaudio[acodec=opus]/bestvideo[height<=360]+bestaudio/best[height<=360]',
            '1440p': 'bestvideo[height<=1440]+bestaudio[acodec=flac]/bestvideo[height<=1440]+bestaudio[acodec=opus]/bestvideo[height<=1440]+bestaudio/best[height<=1440]',
            '2160p': 'bestvideo[height<=2160]+bestaudio[acodec=flac]/bestvideo[height<=2160]+bestaudio[acodec=opus]/bestvideo[height<=2160]+bestaudio/best[height<=2160]',  # 4K
            '4k': 'bestvideo[height<=2160]+bestaudio[acodec=flac]/bestvideo[height<=2160]+bestaudio[acodec=opus]/bestvideo[height<=2160]+bestaudio/best[height<=2160]',
        }
        
        return quality_map.get(quality, 'bestvideo+bestaudio[acodec=flac]/bestvideo+bestaudio[acodec=opus]/bestvideo+bestaudio/best')
    
    def _enhance_audio_metadata(self, info_dict, output_format):
        """Enhance metadata extraction for better audio tagging"""
        enhanced_opts = {
            'writeinfojson': True,
            'writethumbnail': True,
            'writesubtitles': False,
            
            # Try to extract artist-specific thumbnails and info
            'extract_flat': False,
            'force_json': True,
            
            # Enhanced thumbnail options
            'thumbnail_format': 'jpg/png/webp',
        }
        
        # Format-specific optimizations
        if output_format and output_format.lower() in ['flac', 'wav']:
            # For lossless formats, get the highest quality thumbnail
            enhanced_opts['thumbnail_max_size'] = '1920x1920'
        elif output_format and output_format.lower() in ['mp3', 'm4a', 'aac']:
            # For compressed formats, optimize thumbnail size
            enhanced_opts['thumbnail_max_size'] = '1200x1200'
        
        return enhanced_opts
    
    def _get_artist_cover_art(self, url, info_dict=None):
        """Attempt to get proper artist cover art instead of video thumbnail"""
        try:
            # For music videos, try to extract artist/album information
            if info_dict:
                title = info_dict.get('title', '').lower()
                uploader = info_dict.get('uploader', '').lower()
                
                # Check if this looks like a music video
                music_indicators = ['official', 'music video', 'mv', 'official video', 
                                  'lyric video', 'lyrics', 'audio', 'song']
                
                if any(indicator in title for indicator in music_indicators):
                    print("♫ Music content detected, optimizing for artist cover art...")
                    
                    # Try to extract artist and song name
                    # Common patterns: "Artist - Song", "Song by Artist", etc.
                    import re
                    
                    # Pattern 1: "Artist - Song Title"
                    match = re.search(r'^(.+?)\s*[-–]\s*(.+?)(?:\s*\([^)]*\))?(?:\s*\[.*\])?$', title)
                    if match:
                        artist, song = match.groups()
                        print(f"♫ Detected: Artist: {artist.strip()}, Song: {song.strip()}")
                        return {'artist': artist.strip(), 'song': song.strip()}
                    
                    # Pattern 2: Try uploader as artist
                    if 'vevo' in uploader or 'records' in uploader or 'music' in uploader:
                        # Extract artist name from uploader (remove common suffixes)
                        clean_uploader = re.sub(r'\s*(vevo|records|music|official).*$', '', uploader, flags=re.I)
                        if clean_uploader:
                            print(f"♫ Using uploader as artist: {clean_uploader}")
                            return {'artist': clean_uploader.strip(), 'song': title}
            
            return None
            
        except Exception as e:
            print(f"⚠  Error extracting artist info: {e}")
            return None
    
    def _cleanup_intermediate_files(self, info, audio_only=False, output_format=None, keep_file=None):
        """Clean up intermediate files - uses FileManager module"""
        FileManager.cleanup_intermediate_files(
            self.output_dir, info, audio_only, output_format, keep_file
        )
    
    def check_url_support(self, url, silent=False):
        """Check if URL is supported - delegates to URLValidator module"""
        url_validator = URLValidator(self.platform_configs)
        return url_validator.check_url_support(url, self.detect_platform, silent)
    
    def list_supported_platforms(self):
        """List all supported platforms - delegates to PlatformInfo module"""
        platform_info = PlatformInfo(self.console if RICH_AVAILABLE else None)
        total_sites = len(self.get_supported_sites())
        platform_info.display_platforms_rich(total_sites) if RICH_AVAILABLE else platform_info.display_platforms_plain(total_sites)

def interactive_mode():
    """Interactive mode with modern UI and professional design"""
    from ui_display import show_help_menu
    
    downloader = UltimateMediaDownloader()
    ui = ModernUI()
    
    # Show welcome screen
    ui.show_welcome_banner()
    time.sleep(1)  # Brief pause for impact
    
    # Show interactive mode banner
    ui.show_interactive_banner()
    
    while True:
        try:
            # Get user input with styled prompt
            url = ui.prompt_input("Enter media URL or command", default=None)
            
            if not url:
                continue
            
            url = url.strip()
            
            # Handle commands
            if url.lower() in ['quit', 'exit', 'q']:
                if ui.console:
                    ui.console.print("\n[bold cyan]👋 Thank you for using Ultimate Downloader![/bold cyan]\n")
                else:
                    print("\n👋 Thank you for using Ultimate Downloader!\n")
                break
                
            elif url.lower() in ['help', 'h']:
                show_help_menu(ui)
                continue
                
            elif url.lower() in ['platforms', 'p']:
                downloader.list_supported_platforms()
                continue
                
            elif url.lower() in ['clear', 'cls']:
                ui.show_welcome_banner()
                ui.show_interactive_banner()
                continue
            
            # Validate URL
            if not url.startswith(('http://', 'https://')):
                ui.error_message("Invalid URL. Please enter a valid URL starting with 'http://' or 'https://'")
                continue
            
            # Check URL support with spinner
            spinner = ui.show_spinner("Analyzing URL...")
            if spinner:
                spinner.start()
            
            supported = downloader.check_url_support(url, silent=True)
            
            if spinner:
                spinner.stop()
            
            if not supported:
                ui.error_message("URL is not supported or invalid")
                continue
            
            # Start download with progress indication
            ui.info_message(f"Starting download from: {url[:60]}...")
            result = downloader.download_media(url, interactive=True)
            
            if result:
                ui.success_message("Download completed successfully!")
            else:
                ui.warning_message("Download was cancelled or failed")
            
            # Ask to continue
            if ui.console and RICH_AVAILABLE:
                another = Prompt.ask("\n[bold yellow]↓[/bold yellow] Download another file?", 
                                   choices=["y", "n"], default="y")
            else:
                another = input("\n↓ Download another file? (y/n): ").strip().lower()
            
            if another in ['n', 'no']:
                if ui.console:
                    ui.console.print("\n[bold cyan]👋 Thanks for using Ultimate Downloader![/bold cyan]\n")
                else:
                    print("\n👋 Thanks for using Ultimate Downloader!\n")
                break
            
            # Clear for next iteration
            ui.show_welcome_banner()
            ui.show_interactive_banner()
                
        except KeyboardInterrupt:
            if ui.console:
                ui.console.print("\n\n[bold yellow]⚠[/bold yellow] Interrupted by user\n")
                ui.console.print("[bold cyan]👋 Goodbye![/bold cyan]\n")
            else:
                print("\n\n⚠ Interrupted by user")
                print("👋 Goodbye!\n")
            break
        except Exception as e:
            ui.error_message(f"An error occurred: {str(e)}")
            ui.warning_message("Please try again with a different URL")



def main():
    from cli_args import parse_arguments
    from ui_display import show_help_menu
    
    args = parse_arguments()
    
    # Create downloader instance
    downloader = UltimateMediaDownloader(args.output, verbose=args.verbose)
    ui = ModernUI()
    
    # Show beautiful welcome banner only in interactive mode
    # For command-line mode, keep it minimal
    
    # List platforms
    if args.list_platforms:
        downloader.list_supported_platforms()
        return
    
    # Start interactive mode if no URL provided or explicitly requested
    if not args.url or args.interactive:
        if not args.url:
            interactive_mode()
            return
        # If URL provided with --interactive, we'll use interactive mode for the URL
    
    downloader.print_rich(f"{Icons.get('folder')} Output directory: [bold cyan]{downloader.output_dir}[/bold cyan]")
    downloader.print_rich(f"{Icons.get('link')} URL: [bold blue]{args.url}[/bold blue]")
    downloader.console.print("") if downloader.console else print("")
    
    # Check URL support
    if args.check_support:
        downloader.check_url_support(args.url)
        return
    
    # Get media information
    if args.info or args.show_formats:
        downloader.print_rich(Messages.searching("Gathering media information..."))
        info = downloader.get_video_info(args.url, timeout=args.timeout)
        
        if info:
            if downloader.console:
                downloader.console.print("")
            else:
                print("")
            downloader.print_panel(
                f"[bold]{Icons.get('video')} MEDIA INFORMATION[/bold]",
                border_style="cyan"
            )
            
            details = {
                'Title': info.get('title', 'Unknown'),
                'Duration': downloader._format_duration(info.get('duration', 0)),
                'Uploader': info.get('uploader', 'Unknown'),
                'Platform': downloader.detect_platform(args.url).upper(),
                'Views': f"{info.get('view_count', 0):,}" if info.get('view_count') else 'Unknown',
                'Upload Date': info.get('upload_date', 'Unknown'),
                'Likes': f"{info.get('like_count', 0):,}" if info.get('like_count') else 'Unknown',
                'Description': (info.get('description', '')[:100] + '...') if info.get('description') else 'No description',
                'URL': info.get('webpage_url', args.url),
            }
            
            for key, value in details.items():
                print(f"{key:15}: {value}")
            
            # Show available formats if requested
            if args.show_formats:
                downloader.display_available_qualities(info)
        
        if args.info:  # If only info was requested, don't download
            return
    
    # Determine if we should use interactive mode
    use_interactive = args.interactive and not args.no_interactive
    
    # Download playlist
    if args.playlist:
        downloader.download_playlist(
            args.url, 
            args.quality, 
            args.audio_only, 
            args.format,
            args.custom_format,
            args.max_downloads,
            args.start_index,
            interactive=use_interactive
        )
        return
    
    # Handle batch file download
    if args.batch_file:
        try:
            with open(args.batch_file, 'r') as f:
                urls = [line.strip() for line in f if line.strip() and not line.startswith('#')]
            
            if not urls:
                downloader.print_rich(Messages.error("No valid URLs found in batch file"))
                return
            
            downloader.print_rich(Messages.info(f"Found {len(urls)} URLs in batch file"))
            
            # Determine output format from args
            output_format = args.format or args.audio_format
            
            if args.optimized_batch:
                downloader.download_batch_optimized(
                    urls=urls,
                    quality=args.quality,
                    audio_only=args.audio_only,
                    output_format=output_format,
                    max_concurrent=args.max_concurrent
                )
            else:
                # Standard sequential batch download
                successful = 0
                for i, url in enumerate(urls, 1):
                    downloader.print_rich(f"\n{Icons.get('download')} [{i}/{len(urls)}] Processing: [bold blue]{url}[/bold blue]")
                    result = downloader.download_media(
                        url=url,
                        quality=args.quality,
                        audio_only=args.audio_only,
                        output_format=output_format,
                        custom_format=args.custom_format,
                        interactive=False,
                        add_metadata=args.embed_metadata or args.audio_only,
                        add_thumbnail=args.embed_thumbnail or args.audio_only,
                        no_playlist=args.no_playlist,
                        audio_language=args.audio_language
                    )
                    if result:
                        successful += 1
                
                downloader.print_rich(f"\n{Icons.get('stats')} Batch complete: [bold green]{successful}[/bold green]/[bold]{len(urls)}[/bold] successful")
            
            return
            
        except FileNotFoundError:
            downloader.print_rich(Messages.error(f"Batch file not found: {args.batch_file}"))
            return
        except Exception as e:
            downloader.print_rich(Messages.error(f"Error reading batch file: {e}"))
            return
    
    # Determine output format with priority: --format > --audio-format
    output_format = args.format or args.audio_format
    
    # Auto-enable metadata and thumbnails for audio files
    add_metadata = args.embed_metadata or args.audio_only
    add_thumbnail = args.embed_thumbnail or args.audio_only
    
    # Download single media with enhanced options
    downloader.download_media(
        url=args.url,
        quality=args.quality,
        audio_only=args.audio_only,
        output_format=output_format,
        custom_format=args.custom_format,
        interactive=use_interactive,
        add_metadata=add_metadata,
        add_thumbnail=add_thumbnail,
        no_playlist=args.no_playlist,
        audio_language=args.audio_language
    )
    
    # Print warning summary at the end
    if not args.verbose and hasattr(downloader, 'quiet_logger'):
        downloader.quiet_logger.print_summary()

if __name__ == "__main__":    
    main()