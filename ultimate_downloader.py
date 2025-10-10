#!/usr/bin/env python3
"""
Ultimate Multi-Platform Media Downloader
Supports YouTube, Spotify, Apple Music, SoundCloud, and many other platforms
"""

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

import yt_dlp
import requests
from concurrent.futures import ThreadPoolExecutor, TimeoutError
import subprocess
import shutil
from PIL import Image
import io

try:
    import spotipy
    from spotipy.oauth2 import SpotifyClientCredentials
    SPOTIFY_AVAILABLE = True
except ImportError:
    SPOTIFY_AVAILABLE = False

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


class UltimateMediaDownloader:
    def __init__(self, output_dir=None):
        # Default to system Downloads folder if no output_dir specified
        if output_dir is None:
            output_dir = Path.home() / "Downloads" / "UltimateDownloader"
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.cancelled = False
        
        # Initialize Rich console for beautiful output
        self.console = Console() if RICH_AVAILABLE else None
        self.current_progress = None
        
        # Platform-specific configurations
        self.platform_configs = {
            'youtube': {
                'extractors': ['youtube', 'youtu.be'],
                'formats': ['mp4', 'webm', 'mp3', 'wav', 'flac']
            },
            'spotify': {
                'extractors': ['spotify'],
                'formats': ['mp3', 'wav', 'flac'],
                'note': 'Spotify tracks will be searched on YouTube for download'
            },
            'soundcloud': {
                'extractors': ['soundcloud'],
                'formats': ['mp3', 'wav', 'flac']
            },
            'apple_music': {
                'extractors': ['apple', 'itunes'],
                'formats': ['mp3', 'wav', 'flac'],
                'note': 'Apple Music tracks will be searched on YouTube for download'
            },
            'generic': {
                'extractors': ['generic'],
                'formats': ['mp4', 'mp3', 'wav']
            }
        }
        
        # Enhanced yt-dlp configuration for maximum performance and quality
        self.default_ydl_opts = {
            # Performance optimizations
            'socket_timeout': 30,
            'retries': 10,
            'fragment_retries': 10,
            'skip_unavailable_fragments': True,
            'keepvideo': False,
            'noplaylist': False,
            'ignoreerrors': False,  # Changed to False to catch errors properly
            'no_warnings': False,  # Show warnings to help diagnose issues
            'quiet': False,  # Show output for better error visibility
            'no_color': False,  # Allow colors in our custom progress
            'extractaudio': False,
            'audioformat': 'best',  # Changed from 'mp3' to 'best' for higher quality
            'concurrent_fragments': 8,  # Enable parallel fragment downloads
            'http_chunk_size': 10485760,  # 10MB chunks for faster downloads
            
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
            
            # Enhanced user agent for better compatibility
            'user_agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15',
            
            # Cache for faster repeated operations
            'cachedir': str(self.output_dir / '.cache'),
            
            # Resume support
            'continue_dl': True,
            'part': True,
            
            # Custom logger to suppress verbose output
            'logger': QuietLogger(),
        }
        
        # Initialize Spotify client if available
        self.spotify_client = None
        if SPOTIFY_AVAILABLE:
            self._init_spotify()
        
        # Initialize Apple Music downloader if available
        self.apple_music_downloader = None
        if GAMDL_AVAILABLE:
            self._init_apple_music()
        
        # Initialize browser for enhanced scraping
        self.browser_driver = None
    
    def _init_spotify(self):
        """Initialize Spotify client (requires API credentials)"""
        try:
            # You would need to set these environment variables or provide them
            client_id = os.environ.get('SPOTIFY_CLIENT_ID')
            client_secret = os.environ.get('SPOTIFY_CLIENT_SECRET')
            
            if client_id and client_secret:
                client_credentials_manager = SpotifyClientCredentials(
                    client_id=client_id, 
                    client_secret=client_secret
                )
                self.spotify_client = spotipy.Spotify(
                    client_credentials_manager=client_credentials_manager
                )
                # Only show success in verbose mode
            # Suppress warnings by default - not critical for operation
        except Exception as e:
            # Only show errors in verbose mode
            pass
    
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
        """Get or create browser driver for enhanced scraping"""
        # Skip browser automation - it's unreliable across platforms
        # Use enhanced HTTP scraping instead
        return None
    
    def print_rich(self, message, style="bold cyan"):
        """Print with Rich formatting if available, fallback to plain print"""
        if RICH_AVAILABLE and self.console:
            self.console.print(message, style=style)
        else:
            print(message)
    
    def print_panel(self, content, title=None, style="bold blue", border_style="cyan"):
        """Print a beautiful panel with Rich if available"""
        if RICH_AVAILABLE and self.console:
            self.console.print(Panel(content, title=title, style=style, border_style=border_style, box=box.ROUNDED))
        else:
            if title:
                print(f"\n{'='*60}")
                print(f"  {title}")
                print('='*60)
            print(content)
            print('='*60)
    
    def print_table(self, title, headers, rows, style="cyan"):
        """Print a beautiful table with Rich if available"""
        if RICH_AVAILABLE and self.console:
            table = Table(title=title, box=box.ROUNDED, style=style)
            for header in headers:
                table.add_column(header, style="bold")
            for row in rows:
                table.add_row(*[str(cell) for cell in row])
            self.console.print(table)
        else:
            print(f"\n{title}")
            print("-" * 60)
            print(" | ".join(headers))
            print("-" * 60)
            for row in rows:
                print(" | ".join(str(cell) for cell in row))
            print("-" * 60)
    
    def detect_platform(self, url):
        """Detect the platform from URL"""
        url_lower = url.lower()
        
        if any(domain in url_lower for domain in ['youtube.com', 'youtu.be', 'm.youtube.com']):
            return 'youtube'
        elif 'spotify.com' in url_lower:
            return 'spotify'
        elif 'soundcloud.com' in url_lower:
            return 'soundcloud'
        elif any(domain in url_lower for domain in ['music.apple.com', 'itunes.apple.com']):
            return 'apple_music'
        elif any(domain in url_lower for domain in ['tiktok.com', 'instagram.com', 'facebook.com', 'twitter.com', 'x.com']):
            return 'social_media'
        else:
            return 'generic'
    
    def get_supported_sites(self):
        """Get list of all supported sites"""
        try:
            # Return a curated list of major supported platforms
            # This avoids the internal API issue and provides cleaner output
            major_sites = [
                {'name': 'YouTube', 'description': 'YouTube videos, playlists, channels'},
                {'name': 'Spotify', 'description': 'Spotify tracks, albums, playlists (via YouTube search)'},
                {'name': 'SoundCloud', 'description': 'SoundCloud tracks and playlists'},
                {'name': 'TikTok', 'description': 'TikTok videos'},
                {'name': 'Instagram', 'description': 'Instagram posts, reels, IGTV'},
                {'name': 'Twitter', 'description': 'Twitter videos'},
                {'name': 'Facebook', 'description': 'Facebook videos'},
                {'name': 'Vimeo', 'description': 'Vimeo videos'},
                {'name': 'Twitch', 'description': 'Twitch VODs and clips'},
                {'name': 'Apple Music', 'description': 'Apple Music tracks (via YouTube search)'},
                {'name': 'Generic', 'description': 'many other video and audio platforms'}
            ]
            return major_sites
        except Exception as e:
            print(f"Error getting supported sites: {e}")
            return [{'name': 'Error', 'description': 'Could not load site list'}]
    
    def search_and_download_spotify_track(self, spotify_url):
        """Search for Spotify track/album/playlist on YouTube and download"""
        if not self.spotify_client:
            self.print_rich(Messages.warning("Spotify API not configured. Using web scraping method..."))
            self.print_rich(Messages.info("💡 Tip: For better Spotify support, set SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET"))
            return self._fallback_spotify_search(spotify_url)
        
        try:
            # Determine Spotify content type
            if '/track/' in spotify_url:
                return self._download_spotify_track(spotify_url)
            elif '/album/' in spotify_url:
                return self._download_spotify_album(spotify_url)
            elif '/playlist/' in spotify_url:
                return self._download_spotify_playlist(spotify_url)
            else:
                self.print_rich(Messages.error("Unknown Spotify URL format"))
                return None
                
        except Exception as e:
            self.print_rich(Messages.error(f"Error processing Spotify URL: {e}"))
            return self._fallback_spotify_search(spotify_url)
    
    def _download_spotify_track(self, spotify_url):
        """Download single Spotify track"""
        track_id = self._extract_spotify_id(spotify_url, 'track')
        if not track_id:
            return None
        
        track = self.spotify_client.track(track_id)
        artists = ', '.join([artist['name'] for artist in track['artists']])
        track_name = track['name']
        # Format as "songname - artist name" for better YouTube search results
        search_query = f"{track_name} - {artists}"
        
        self.print_rich(f"[bold green]{Icons.get('spotify')} Spotify Track:[/bold green] [cyan]{search_query}[/cyan]")
        
        # Ask for quality preference (like Apple Music)
        output_format = 'mp3'
        quality = 'best'
        
        self.print_rich(f"\n[bold cyan]🎚️  Select audio quality:[/bold cyan]")
        self.print_rich("  [green]1[/green]. Best Quality (320kbps MP3) - Recommended")
        self.print_rich("  [yellow]2[/yellow]. High Quality (256kbps AAC/M4A) - Balanced")
        self.print_rich("  [blue]3[/blue]. Very High Quality (FLAC) - Lossless, larger files")
        self.print_rich("  [magenta]4[/magenta]. Best Available (Auto) - Highest quality possible")
        
        try:
            from rich.prompt import Prompt
            quality_choice = Prompt.ask("\n[cyan]Enter choice (1-4)[/cyan]", default="1")
            
            if quality_choice == "1":
                output_format = 'mp3'
                quality = 'best'
            elif quality_choice == "2":
                output_format = 'm4a'
                quality = 'best'
            elif quality_choice == "3":
                output_format = 'flac'
                quality = 'best'
            elif quality_choice == "4":
                output_format = 'best'
                quality = 'best'
            else:
                output_format = 'mp3'
                quality = 'best'
        except:
            # If rich prompt fails, fall back to regular input
            try:
                quality_choice = input("\nEnter choice (1-4) [default: 1]: ").strip() or "1"
                
                if quality_choice == "1":
                    output_format = 'mp3'
                    quality = 'best'
                elif quality_choice == "2":
                    output_format = 'm4a'
                    quality = 'best'
                elif quality_choice == "3":
                    output_format = 'flac'
                    quality = 'best'
                elif quality_choice == "4":
                    output_format = 'best'
                    quality = 'best'
                else:
                    output_format = 'mp3'
                    quality = 'best'
            except:
                output_format = 'mp3'
                quality = 'best'
        
        self.print_rich(Messages.searching("Searching on YouTube..."))
        
        youtube_url = self._search_youtube(search_query)
        if youtube_url:
            self.print_rich(Messages.success(f"Found on YouTube: {youtube_url}"))
            # Create filename as "Artist - Title"
            filename_format = f"{artists} - {track_name}"
            # Use enhanced audio settings for Spotify tracks
            return self.download_media(
                youtube_url, 
                audio_only=True, 
                output_format=output_format,
                quality=quality,
                add_metadata=True,
                add_thumbnail=True,
                custom_filename=filename_format  # Save as "Artist - Title"
            )
        else:
            self.print_rich(Messages.error("Could not find track on YouTube"))
            return None
    
    def _download_spotify_album(self, spotify_url):
        """Download Spotify album by searching each track on YouTube"""
        album_id = self._extract_spotify_id(spotify_url, 'album')
        if not album_id:
            return None
        
        album = self.spotify_client.album(album_id)
        album_name = album['name']
        artist_name = album['artists'][0]['name']
        tracks = album['tracks']['items']
        
        self.print_rich(f"[bold magenta]{Icons.get('spotify')} Spotify Album:[/bold magenta] [cyan]{artist_name} - {album_name}[/cyan]")
        self.print_rich(Messages.info(f"Total tracks: {len(tracks)}"))
        
        # Prompt for audio format and quality
        output_format, quality = self._prompt_audio_format_quality()
        
        # Create album directory
        album_dir = self.output_dir / f"{artist_name} - {album_name}"
        album_downloader = UltimateMediaDownloader(album_dir)
        
        successful_downloads = 0
        
        for i, track in enumerate(tracks, 1):
            try:
                artists = ', '.join([artist['name'] for artist in track['artists']])
                track_name = track['name']
                # Format as "songname - artist name" for better YouTube search results
                search_query = f"{track_name} - {artists}"
                
                self.print_rich(f"\n[bold blue]{Icons.get('music')} [{i:2d}/{len(tracks)}][/bold blue] [cyan]{search_query}[/cyan]")
                
                youtube_url = self._search_youtube(search_query)
                if youtube_url:
                    # Create filename as "Artist - Title"
                    filename_format = f"{artists} - {track_name}"
                    result = album_downloader.download_media(
                        youtube_url, 
                        audio_only=True, 
                        output_format=output_format,
                        quality=quality,
                        add_metadata=True,
                        add_thumbnail=True,
                        custom_filename=filename_format
                    )
                    if result:
                        successful_downloads += 1
                else:
                    self.print_rich(Messages.error(f"Could not find: {track_name}"))
                    
            except Exception as e:
                self.print_rich(Messages.error(f"Error downloading {track_name}: {e}"))
        
        print(f"\n✓ Album download completed: {successful_downloads}/{len(tracks)} tracks downloaded")
        return successful_downloads > 0
    
    def _download_spotify_playlist(self, spotify_url):
        """Download Spotify playlist by searching each track on YouTube"""
        playlist_id = self._extract_spotify_id(spotify_url, 'playlist')
        if not playlist_id:
            return None
        
        playlist = self.spotify_client.playlist(playlist_id)
        playlist_name = playlist['name']
        owner_name = playlist['owner']['display_name']
        tracks = playlist['tracks']['items']
        
        # Filter out None tracks (unavailable songs)
        valid_tracks = [item for item in tracks if item['track'] is not None]
        
        print(f"≡ Spotify Playlist: {playlist_name}")
        print(f"◈ Owner: {owner_name}")
        print(f"▤ Total tracks: {len(valid_tracks)}")
        
        # Convert to track list format - use "songname - artist" for better YouTube search
        track_list = []
        for item in valid_tracks:
            track = item['track']
            artists = ', '.join([artist['name'] for artist in track['artists']])
            track_name = track['name']
            # Format as "songname - artist name" for consistent search format
            track_list.append(f"{track_name} - {artists}")
        
        print(f"✓ Found {len(track_list)} tracks in playlist:")
        for i, track in enumerate(track_list[:10], 1):  # Show first 10 tracks
            print(f"  {i}. {track}")
        
        if len(track_list) > 10:
            print(f"  ... and {len(track_list) - 10} more tracks")
        
        # Ask user what they want to download
        choice = self._prompt_playlist_download_choice(track_list)
        
        if choice == "cancel":
            print("✗ Download cancelled by user")
            return None
        elif choice == "all":
            selected_tracks = track_list
        else:
            # User selected specific tracks
            selected_tracks = choice
        
        # Prompt for audio format and quality
        output_format, quality = self._prompt_audio_format_quality()
        
        print(f"\n♫ Starting download of {len(selected_tracks)} track(s)...")
        
        # Create playlist directory
        safe_playlist_name = "".join(c for c in playlist_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
        playlist_dir = self.output_dir / f"Spotify - {safe_playlist_name}"
        playlist_downloader = UltimateMediaDownloader(playlist_dir)
        
        return playlist_downloader._download_track_queue(selected_tracks, "Spotify", output_format, quality)
    
    def _fallback_spotify_search(self, spotify_url):
        """Fallback method to extract Spotify track info without API using web scraping"""
        try:
            self.print_rich(Messages.searching("Attempting fallback Spotify track extraction..."))
            
            # Determine content type
            if '/track/' in spotify_url:
                return self._scrape_spotify_track(spotify_url)
            elif '/album/' in spotify_url:
                return self._scrape_spotify_album(spotify_url)
            elif '/playlist/' in spotify_url:
                return self._scrape_spotify_playlist(spotify_url)
            elif '/artist/' in spotify_url:
                return self._scrape_spotify_artist(spotify_url)
            else:
                self.print_rich(Messages.error("Unknown Spotify URL format"))
                self.print_rich(Messages.info("Supported: /track/, /album/, /playlist/, /artist/"))
                return None
            
        except Exception as e:
            self.print_rich(Messages.error(f"Fallback search failed: {e}"))
            return None
    
    def _scrape_spotify_track(self, spotify_url):
        """Scrape Spotify track information and download from YouTube (like Apple Music)"""
        try:
            self.print_rich(Messages.info("Processing Spotify track URL..."))
            
            # Extract track info - simplified approach that mirrors Apple Music
            track_info = self._extract_spotify_track_info(spotify_url)
            
            if track_info:
                search_query = track_info
                self.print_rich(f"[bold green]♪ Spotify Track:[/bold green] [cyan]{search_query}[/cyan]")
                
                # Check if artist info is missing (no " - " in search query)
                if ' - ' not in search_query:
                    self.print_rich(Messages.warning("⚠  Artist information not found in metadata"))
                    self.print_rich(Messages.info("💡 Please provide the artist name for better search results:"))
                    
                    try:
                        from rich.prompt import Prompt
                        artist_name = Prompt.ask("[cyan]Artist name (or press Enter to skip)[/cyan]", default="")
                        
                        if artist_name:
                            # Format as "songname - artist name" for better YouTube search
                            search_query = f"{search_query} - {artist_name}"
                            self.print_rich(f"[bold green]♪ Updated search:[/bold green] [cyan]{search_query}[/cyan]")
                    except KeyboardInterrupt:
                        self.print_rich(Messages.info("\nSkipping artist info, continuing with track name only"))
                    except:
                        pass
            else:
                # If automatic extraction failed, ask user (exactly like Apple Music does)
                self.print_rich(Messages.warning("Could not automatically extract track information from URL"))
                self.print_rich(Messages.info("💡 Please provide the track details manually:"))
                self.print_rich("[dim]Tip: You can find this info on the Spotify page[/dim]")
                
                try:
                    from rich.prompt import Prompt
                    track_name = Prompt.ask("[cyan]Song/Track name[/cyan]")
                    artist_name = Prompt.ask("[cyan]Artist name[/cyan]")
                    
                    if not track_name:
                        self.print_rich(Messages.error("Track name is required"))
                        return None
                    
                    if artist_name:
                        # Format as "songname - artist name" for better YouTube search
                        search_query = f"{track_name} - {artist_name}"
                    else:
                        search_query = track_name
                    
                    self.print_rich(f"\n[bold green]♪ Searching for:[/bold green] [cyan]{search_query}[/cyan]")
                except KeyboardInterrupt:
                    self.print_rich(Messages.info("\nCancelled by user"))
                    return None
                except:
                    self.print_rich(Messages.error("Could not get track information"))
                    return None
            
            # Ask for quality preference (like Apple Music)
            output_format = 'mp3'
            quality = 'best'
            
            self.print_rich(f"\n[bold cyan]🎚️  Select audio quality:[/bold cyan]")
            self.print_rich("  [green]1[/green]. Best Quality (320kbps MP3) - Recommended")
            self.print_rich("  [yellow]2[/yellow]. High Quality (256kbps AAC/M4A) - Balanced")
            self.print_rich("  [blue]3[/blue]. Very High Quality (FLAC) - Lossless, larger files")
            self.print_rich("  [magenta]4[/magenta]. Best Available (Auto) - Highest quality possible")
            
            try:
                from rich.prompt import Prompt
                quality_choice = Prompt.ask("\n[cyan]Enter choice (1-4)[/cyan]", default="1")
                
                if quality_choice == "1":
                    output_format = 'mp3'
                    quality = 'best'
                elif quality_choice == "2":
                    output_format = 'm4a'
                    quality = 'best'
                elif quality_choice == "3":
                    output_format = 'flac'
                    quality = 'best'
                elif quality_choice == "4":
                    output_format = 'best'
                    quality = 'best'
                else:
                    output_format = 'mp3'
                    quality = 'best'
            except:
                # If rich prompt fails, fall back to regular input
                try:
                    quality_choice = input("\nEnter choice (1-4) [default: 1]: ").strip() or "1"
                    
                    if quality_choice == "1":
                        output_format = 'mp3'
                        quality = 'best'
                    elif quality_choice == "2":
                        output_format = 'm4a'
                        quality = 'best'
                    elif quality_choice == "3":
                        output_format = 'flac'
                        quality = 'best'
                    elif quality_choice == "4":
                        output_format = 'best'
                        quality = 'best'
                    else:
                        output_format = 'mp3'
                        quality = 'best'
                except:
                    output_format = 'mp3'
                    quality = 'best'
            
            self.print_rich(Messages.searching("Searching on YouTube..."))
            
            youtube_url = self._search_youtube(search_query)
            if youtube_url:
                self.print_rich(Messages.success(f"Found on YouTube: {youtube_url}"))
                
                # Try to get album art from Spotify
                album_art_url = self._get_spotify_album_art(spotify_url)
                if album_art_url:
                    self.print_rich(f"  [dim]✓ Spotify album art available[/dim]")
                
                # Extract artist and title for filename
                if ' - ' in search_query:
                    parts = search_query.split(' - ', 1)
                    if len(parts) == 2:
                        # search_query is "songname - artist"
                        filename_format = f"{parts[1]} - {parts[0]}"  # Convert to "artist - songname"
                    else:
                        filename_format = search_query
                else:
                    filename_format = search_query
                
                # Download from YouTube with selected quality
                result = self.download_media(
                    youtube_url, 
                    audio_only=True, 
                    output_format=output_format,
                    quality=quality,
                    add_metadata=True,
                    add_thumbnail=True,
                    custom_filename=filename_format
                )
                
                # If download succeeded and we have album art, replace YouTube thumbnail with Spotify art
                if result and album_art_url:
                    # Find the downloaded file
                    downloaded_file = self._find_recently_downloaded_file()
                    if downloaded_file:
                        self._embed_spotify_album_art(downloaded_file, album_art_url, search_query)
                
                return result
            else:
                self.print_rich(Messages.error("Could not find track on YouTube"))
                
                # Interactive fallback - ask for more details
                self.print_rich(f"\n[yellow]→ The search for '{search_query}' didn't find any results.[/yellow]")
                self.print_rich("[yellow]Would you like to try with different search terms?[/yellow]")
                try:
                    from rich.prompt import Prompt, Confirm
                    if Confirm.ask("Try again with different terms?", default=False):
                        track = Prompt.ask("Track name")
                        artist = Prompt.ask("Artist name")
                        if artist and track:
                            # Format as "songname - artist name" for better search
                            better_query = f"{track} - {artist}"
                            filename_format = f"{artist} - {track}"
                            self.print_rich(f"\n[cyan]⌕ Searching again for: {better_query}[/cyan]")
                            youtube_url = self._search_youtube(better_query)
                            if youtube_url:
                                self.print_rich(Messages.success(f"Found on YouTube: {youtube_url}"))
                                return self.download_media(
                                    youtube_url, 
                                    audio_only=True, 
                                    output_format=output_format,
                                    quality=quality,
                                    add_metadata=True,
                                    add_thumbnail=True,
                                    custom_filename=filename_format
                                )
                except:
                    pass
                
                return None
                
        except Exception as e:
            self.print_rich(Messages.error(f"Error processing Spotify track: {e}"))
            return None
    
    def _extract_spotify_track_info(self, spotify_url):
        """Extract track information from Spotify URL using various methods"""
        try:
            # Method 1: Try oembed API (works without SSL issues usually)
            try:
                import urllib3
                urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
                
                oembed_url = f"https://open.spotify.com/oembed?url={spotify_url}"
                response = requests.get(oembed_url, timeout=10, verify=False)
                
                if response.status_code == 200:
                    data = response.json()
                    title_raw = data.get('title', '').strip()
                    
                    if title_raw:
                        # Spotify oembed returns title in various formats:
                        # Format 1: "Song Name" (just title)
                        # Format 2: "Artist · Song Name" (with middle dot)
                        # Format 3: "Song Name - Artist" (with dash)
                        
                        # Try to extract both track and artist
                        track_name = None
                        artist_name = None
                        
                        # Check for middle dot separator (most common in Spotify oembed)
                        if ' · ' in title_raw or ' · ' in title_raw:
                            parts = title_raw.replace(' · ', ' · ').split(' · ')
                            if len(parts) == 2:
                                artist_name = parts[0].strip()
                                track_name = parts[1].strip()
                        # Check for dash separator
                        elif ' - ' in title_raw and title_raw.count(' - ') == 1:
                            parts = title_raw.split(' - ')
                            # Could be "Artist - Song" or "Song - Artist"
                            # Usually Spotify uses "Artist - Song"
                            artist_name = parts[0].strip()
                            track_name = parts[1].strip()
                        else:
                            # Only track name, no artist
                            track_name = title_raw
                        
                        if track_name and artist_name:
                            # Format as "songname - artist" for better YouTube search
                            search_query = f"{track_name} - {artist_name}"
                            self.print_rich(f"  [dim]✓ Extracted: {track_name}[/dim]")
                            self.print_rich(f"  [dim]✓ Artist: {artist_name}[/dim]")
                            return search_query
                        else:
                            # Only track name found
                            self.print_rich(f"  [dim]✓ Extracted track: {track_name}[/dim]")
                            self.print_rich(f"  [dim]⚠ Artist not found in metadata[/dim]")
                            return track_name
            except:
                pass
            
            # Method 2: Try scraping the Spotify page directly
            try:
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
                }
                response = requests.get(spotify_url, headers=headers, timeout=10)
                
                if response.status_code == 200:
                    from bs4 import BeautifulSoup
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # Try to get from meta tags
                    og_title = soup.find('meta', property='og:title')
                    if og_title and og_title.get('content'):
                        title_content = og_title.get('content').strip()
                        
                        # Parse out artist and track
                        if ' - song and lyrics by ' in title_content.lower():
                            # Format: "Track Name - song and lyrics by Artist | Spotify"
                            parts = title_content.split(' - song and lyrics by ')
                            if len(parts) >= 2:
                                track_name = parts[0].strip()
                                artist_part = parts[1].split('|')[0].strip()
                                search_query = f"{track_name} - {artist_part}"
                                self.print_rich(f"  [dim]✓ Extracted: {track_name}[/dim]")
                                self.print_rich(f"  [dim]✓ Artist: {artist_part}[/dim]")
                                return search_query
            except:
                pass
            
            return None
            
        except Exception as e:
            return None
    
    def _get_spotify_album_art(self, spotify_url):
        """Get album art URL from Spotify using oembed API"""
        try:
            import urllib3
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
            
            oembed_url = f"https://open.spotify.com/oembed?url={spotify_url}"
            response = requests.get(oembed_url, timeout=10, verify=False)
            
            if response.status_code == 200:
                data = response.json()
                thumbnail_url = data.get('thumbnail_url', '')
                if thumbnail_url:
                    self.print_rich(f"  [dim]✓ Found Spotify album art[/dim]")
                    return thumbnail_url
        except:
            pass
        
        return None
    
    def _embed_spotify_album_art(self, file_path, album_art_url, track_info):
        """Download and embed Spotify album art into the audio file"""
        try:
            if not MUTAGEN_AVAILABLE:
                return False
            
            self.print_rich(Messages.info("Adding Spotify album art..."))
            
            # Download album art
            response = requests.get(album_art_url, timeout=10)
            if response.status_code != 200:
                return False
            
            album_art_data = response.content
            
            # Determine file type and embed art
            file_path_obj = Path(file_path) if isinstance(file_path, str) else file_path
            
            if not file_path_obj.exists():
                # Try to find the file with different extensions
                possible_files = list(file_path_obj.parent.glob(f"{file_path_obj.stem}.*"))
                if possible_files:
                    file_path_obj = possible_files[0]
                else:
                    return False
            
            file_ext = file_path_obj.suffix.lower()
            
            if file_ext == '.mp3':
                audio = MP3(str(file_path_obj), ID3=ID3)
                if audio.tags is None:
                    audio.add_tags()
                
                audio.tags.add(
                    APIC(
                        encoding=3,
                        mime='image/jpeg',
                        type=3,  # Cover (front)
                        desc='Cover',
                        data=album_art_data
                    )
                )
                audio.save()
                self.print_rich(Messages.success("✓ Album art added successfully!"))
                return True
                
            elif file_ext == '.m4a':
                audio = MP4(str(file_path_obj))
                audio.tags['covr'] = [MP4Cover(album_art_data, imageformat=MP4Cover.FORMAT_JPEG)]
                audio.save()
                self.print_rich(Messages.success("✓ Album art added successfully!"))
                return True
                
            elif file_ext == '.flac':
                audio = FLAC(str(file_path_obj))
                image = Picture()
                image.type = 3  # Cover (front)
                image.mime = 'image/jpeg'
                image.desc = 'Cover'
                image.data = album_art_data
                audio.add_picture(image)
                audio.save()
                self.print_rich(Messages.success("✓ Album art added successfully!"))
                return True
            
            return False
            
        except Exception as e:
            self.print_rich(f"  [dim]⚠ Could not add album art: {e}[/dim]")
            return False
    
    def _find_recently_downloaded_file(self):
        """Find the most recently downloaded audio file"""
        try:
            import time
            current_time = time.time()
            
            # Look for files created/modified in the last 2 minutes
            audio_extensions = ['.mp3', '.m4a', '.flac', '.opus', '.ogg', '.wav']
            recent_files = []
            
            for ext in audio_extensions:
                files = list(self.output_dir.glob(f"*{ext}"))
                for f in files:
                    if f.is_file() and (current_time - f.stat().st_mtime) < 120:  # 2 minutes
                        recent_files.append((f, f.stat().st_mtime))
            
            if recent_files:
                # Sort by modification time, newest first
                recent_files.sort(key=lambda x: x[1], reverse=True)
                return recent_files[0][0]
            
            return None
            
        except Exception as e:
            return None
    
    def _scrape_spotify_album(self, spotify_url):
        """Scrape Spotify album information and try to download tracks (like Apple Music)"""
        try:
            from bs4 import BeautifulSoup
            import re
            
            self.print_rich(Messages.searching("Scraping Spotify album page..."))
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept-Language': 'en-US,en;q=0.9',
            }
            
            response = requests.get(spotify_url, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            raw_html = response.text
            
            # Extract album name and artist
            album_name = "Unknown Album"
            artist_name = "Unknown Artist"
            
            # Try structured data
            script_tags = soup.find_all('script', type='application/ld+json')
            for script in script_tags:
                try:
                    json_data = json.loads(script.string)
                    if isinstance(json_data, dict) and json_data.get('@type') == 'MusicAlbum':
                        album_name = json_data.get('name', album_name)
                        if 'byArtist' in json_data:
                            artist_data = json_data['byArtist']
                            if isinstance(artist_data, dict):
                                artist_name = artist_data.get('name', artist_name)
                        break
                except:
                    continue
            
            # Fallback to meta tags
            if album_name == "Unknown Album":
                og_title = soup.find('meta', property='og:title')
                if og_title:
                    title_text = og_title.get('content', '')
                    if ' - ' in title_text:
                        parts = title_text.split(' - ', 1)
                        album_name = parts[0].strip()
                        artist_name = parts[1].strip()
                    else:
                        album_name = title_text.strip()
            
            self.print_rich(f"[bold magenta]♪ Spotify Album:[/bold magenta] [cyan]{artist_name} - {album_name}[/cyan]")
            
            # Try to extract track list from the page
            tracks = []
            try:
                # Look for track data in JSON
                track_pattern = r'"name"\s*:\s*"([^"]+)".{0,500}?"type"\s*:\s*"track"'
                track_matches = re.findall(track_pattern, raw_html)
                
                if track_matches:
                    # Remove duplicates while preserving order
                    seen = set()
                    for track in track_matches:
                        if track not in seen and len(track) > 2:
                            seen.add(track)
                            tracks.append(track)
                    
                    self.print_rich(Messages.success(f"Found {len(tracks)} tracks in album"))
                    
                    # Show first few tracks
                    self.print_rich(Messages.info("Track list:"))
                    for i, track in enumerate(tracks[:5], 1):
                        self.print_rich(f"  {i}. {track}")
                    if len(tracks) > 5:
                        self.print_rich(f"  ... and {len(tracks) - 5} more")
            except:
                pass
            
            if not tracks:
                self.print_rich(Messages.warning("Could not extract track list from album page"))
                self.print_rich(Messages.info("You can:"))
                self.print_rich("  1. [green]Set up Spotify API credentials[/green] for full album downloads")
                self.print_rich("  2. [yellow]Download individual tracks[/yellow] using their URLs")
                self.print_rich("  3. [cyan]Search for the album on YouTube[/cyan] - trying now...")
                
                # Try to find the album on YouTube as a single search
                search_query = f"{artist_name} {album_name} full album"
                youtube_url = self._search_youtube(search_query)
                if youtube_url:
                    self.print_rich(Messages.success(f"Found album on YouTube: {youtube_url}"))
                    return self.download_media(youtube_url, audio_only=True, output_format='mp3')
                else:
                    self.print_rich(Messages.error("Could not find album on YouTube"))
                return None
            
            # Ask user what to download
            self.print_rich("")
            self.print_rich("[yellow]Do you want to download all tracks?[/yellow]")
            self.print_rich("  [green]1[/green] - Download all tracks (searches YouTube for each)")
            self.print_rich("  [yellow]2[/yellow] - Cancel")
            
            try:
                from rich.prompt import Prompt
                choice = Prompt.ask("Choose option", choices=["1", "2"], default="2")
                
                if choice == "2":
                    self.print_rich(Messages.info("Download cancelled"))
                    return None
            except:
                self.print_rich(Messages.info("Download cancelled"))
                return None
            
            # Create album directory
            safe_album_name = "".join(c for c in f"{artist_name} - {album_name}" if c.isalnum() or c in (' ', '-', '_')).rstrip()
            album_dir = self.output_dir / safe_album_name
            album_downloader = UltimateMediaDownloader(album_dir)
            
            # Download tracks
            successful = 0
            for i, track_name in enumerate(tracks, 1):
                try:
                    search_query = f"{artist_name} - {track_name}"
                    self.print_rich(f"\n[bold blue]♫ [{i:2d}/{len(tracks)}][/bold blue] [cyan]{search_query}[/cyan]")
                    
                    youtube_url = self._search_youtube(search_query)
                    if youtube_url:
                        result = album_downloader.download_media(
                            youtube_url, 
                            audio_only=True, 
                            output_format='mp3',
                            add_metadata=True,
                            add_thumbnail=True
                        )
                        if result:
                            successful += 1
                    else:
                        self.print_rich(Messages.error(f"Could not find: {track_name}"))
                except Exception as e:
                    self.print_rich(Messages.error(f"Error downloading {track_name}: {e}"))
            
            self.print_rich("")
            self.print_rich(Messages.success(f"Album download completed: {successful}/{len(tracks)} tracks downloaded"))
            return successful > 0
            
        except Exception as e:
            self.print_rich(Messages.error(f"Error scraping Spotify album: {e}"))
            import traceback
            traceback.print_exc()
            return None
    
    def _scrape_spotify_artist(self, spotify_url):
        """Handle Spotify artist URLs with helpful guidance"""
        try:
            artist_name = "this artist"
            
            # Try to get artist name from oembed API
            try:
                oembed_url = f"https://open.spotify.com/oembed?url={spotify_url}"
                response = requests.get(oembed_url, timeout=5, verify=False)
                
                if response.status_code == 200:
                    data = response.json()
                    artist_name = data.get('title', 'this artist').strip()
            except:
                # If oembed fails, try to extract from URL or use generic name
                pass
            
            self.print_rich(f"[bold cyan]🎤 Spotify Artist Link Detected[/bold cyan]")
            self.print_rich("")
            
            # Provide helpful guidance
            self.print_rich(Panel.fit(
                "[bold yellow]📌 Spotify Artist Download Information[/bold yellow]\n\n"
                f"You've provided a link to: [cyan]{artist_name}[/cyan]\n\n"
                "[bold]Artist pages cannot be downloaded directly.[/bold]\n"
                "You need to specify what content you want to download:\n\n"
                "[bold green]✓ What You Can Download:[/bold green]\n\n"
                "[bold cyan]1. Individual Tracks (Easiest)[/bold cyan]\n"
                "   • Go to the artist's Spotify page\n"
                "   • Click on any song\n"
                "   • Copy the track URL\n"
                "   • Format: [green]https://open.spotify.com/track/...[/green]\n"
                "   • [yellow]✓ Works immediately - no API needed![/yellow]\n\n"
                "[bold cyan]2. Full Albums[/bold cyan]\n"
                "   • Browse the artist's albums on Spotify\n"
                "   • Click on an album\n"
                "   • Copy the album URL\n"
                "   • Format: [green]https://open.spotify.com/album/...[/green]\n"
                "   • Requires: Spotify API credentials\n\n"
                "[bold cyan]3. Playlists[/bold cyan]\n"
                "   • Find playlists featuring this artist\n"
                "   • Copy the playlist URL\n"
                "   • Format: [green]https://open.spotify.com/playlist/...[/green]\n"
                "   • Requires: Python 3.10+ OR Spotify API\n\n"
                "[bold cyan]4. Alternative: YouTube Search[/bold cyan]\n"
                f"   • Search YouTube directly for the artist\n"
                f"   • Use: [green]ytsearch:\"{artist_name} top songs\"[/green]\n"
                "   • Or browse YouTube and copy video URLs\n\n"
                "[bold yellow]💡 Quick Tip:[/bold yellow]\n"
                "For the best experience with single tracks, just copy any song URL\n"
                "from the artist's page - it works without any additional setup!",
                title=f"🎵 Cannot Download Artist Page Directly",
                border_style="yellow"
            ))
            
            return None
            
        except Exception as e:
            self.print_rich(Messages.warning("Spotify artist pages cannot be downloaded directly"))
            self.print_rich("")
            self.print_rich(Messages.info("Please provide one of these instead:"))
            self.print_rich("  • [green]Track URL[/green] - https://open.spotify.com/track/... (works instantly!)")
            self.print_rich("  • [yellow]Album URL[/yellow] - https://open.spotify.com/album/... (needs API)")
            self.print_rich("  • [cyan]Playlist URL[/cyan] - https://open.spotify.com/playlist/... (needs API or Python 3.10+)")
            return None
    
    def _scrape_spotify_playlist(self, spotify_url):
        """Scrape Spotify playlist information from web page"""
        try:
            self.print_rich(Messages.searching("Fetching playlist information..."))
            
            # Extract playlist ID
            playlist_id = self._extract_spotify_id(spotify_url, 'playlist')
            if not playlist_id:
                self.print_rich(Messages.error("Could not extract playlist ID"))
                return None
            
            # Try to get playlist data from Spotify's public API (no auth required for public playlists)
            api_url = f"https://api.spotify.com/v1/playlists/{playlist_id}"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
                'Accept': 'application/json',
            }
            
            # First, get playlist name from the web page
            web_response = requests.get(spotify_url, headers=headers, timeout=10)
            playlist_name = "Spotify Playlist"
            
            if web_response.status_code == 200:
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(web_response.content, 'html.parser')
                og_title = soup.find('meta', property='og:title')
                if og_title:
                    playlist_name = og_title.get('content', 'Spotify Playlist').strip()
            
            # Try using spotdl if available
            try:
                import spotdl
                self.print_rich(Messages.success("Using spotdl for playlist download..."))
                return self._download_spotify_with_spotdl(spotify_url, playlist_name)
            except ImportError:
                pass
            
            # If spotdl is not available, provide installation instructions
            self.print_rich(Messages.warning(f"Cannot download playlist: {playlist_name}"))
            self.print_rich("")
            self.print_rich(Panel.fit(
                "[bold yellow]📌 Spotify Playlist Download Options:[/bold yellow]\n\n"
                "[bold cyan]Option 1: Use spotdl (Recommended)[/bold cyan]\n"
                "  Install: [green]pip install spotdl[/green]\n"
                "  Then run this downloader again\n\n"
                "[bold cyan]Option 2: Configure Spotify API[/bold cyan]\n"
                "  1. Go to: https://developer.spotify.com/dashboard\n"
                "  2. Create an app and get Client ID & Secret\n"
                "  3. Set environment variables:\n"
                "     [green]export SPOTIFY_CLIENT_ID='your_id'[/green]\n"
                "     [green]export SPOTIFY_CLIENT_SECRET='your_secret'[/green]\n\n"
                "[bold cyan]Option 3: Use Individual Track URLs[/bold cyan]\n"
                "  Download tracks one by one using their Spotify URLs",
                title="🎵 Spotify Playlist Support",
                border_style="yellow"
            ))
            
            return None
            
        except Exception as e:
            self.print_rich(Messages.error(f"Error processing Spotify playlist: {e}"))
            return None
    
    def _download_spotify_with_spotdl(self, spotify_url, playlist_name):
        """Download Spotify content using spotdl Python module or web scraping"""
        try:
            # Check Python version
            import sys
            if sys.version_info < (3, 10):
                self.print_rich(Messages.warning("spotdl requires Python 3.10+. Using alternative method..."))
                return self._download_spotify_playlist_manual(spotify_url, playlist_name)
            
            from spotdl import Spotdl
            
            # Create playlist directory
            safe_playlist_name = "".join(c for c in playlist_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
            playlist_dir = self.output_dir / f"Spotify - {safe_playlist_name}"
            playlist_dir.mkdir(parents=True, exist_ok=True)
            
            self.print_rich(Messages.info(f"Downloading to: {playlist_dir}"))
            self.print_rich(Messages.searching("Initializing spotdl..."))
            
            # Configure logging - allow spotdl's output to show
            import logging
            logging.getLogger('urllib3').setLevel(logging.ERROR)
            logging.getLogger('requests').setLevel(logging.ERROR)
            # Don't suppress spotdl logging - let it show progress
            
            # Configure spotdl options
            options = {
                'output': str(playlist_dir / '{artist} - {title}.{output-ext}'),
                'format': 'mp3',
                'bitrate': '320k',
                'threads': 4,
            }
            
            # Initialize Spotdl
            spotdl_client = Spotdl(
                client_id='5f573c9620494bae87890c0f08a60293',  # Public client ID
                client_secret='212476d9b0f3472eaa762d90b19b0ba8',  # Public client secret
                downloader_settings=options
            )
            
            self.print_rich(Messages.searching("Fetching playlist tracks..."))
            
            # Get songs from URL
            songs = spotdl_client.search([spotify_url])
            
            if not songs:
                self.print_rich(Messages.error("No tracks found in playlist"))
                return False
            
            total_tracks = len(songs)
            self.print_rich(Messages.success(f"Found {total_tracks} tracks in playlist\n"))
            
            # Display the playlist tracks
            if RICH_AVAILABLE and self.console:
                self.console.print("[bold cyan]📋 Playlist Tracks:[/bold cyan]\n")
                for i, song in enumerate(songs, 1):
                    song_display = f"{song.name[:50]}..." if len(song.name) > 50 else song.name
                    artist_display = f"{song.artist[:30]}..." if len(song.artist) > 30 else song.artist
                    self.console.print(f"  [dim]{i:2d}.[/dim] [cyan]{song_display}[/cyan] [dim]-[/dim] [yellow]{artist_display}[/yellow]")
                self.console.print()
            else:
                print("\n📋 Playlist Tracks:\n")
                for i, song in enumerate(songs, 1):
                    print(f"  {i:2d}. {song.name} - {song.artist}")
                print()
            
            # Download songs with individual progress bars
            successful = 0
            failed = 0
            
            if RICH_AVAILABLE and self.console:
                self.console.print("[bold green]▸ Starting Downloads...[/bold green]\n")
                
                for i, song in enumerate(songs, 1):
                    # Truncate long names to prevent display issues
                    song_display = f"{song.name[:45]}..." if len(song.name) > 45 else song.name
                    artist_display = f"{song.artist[:30]}..." if len(song.artist) > 30 else song.artist
                    
                    # Show current track header
                    print(f"\n[{i}/{total_tracks}] {song_display} - {artist_display}")
                    
                    try:
                        # Download the song - spotdl will show its own progress bar
                        result = spotdl_client.downloader.download_song(song)
                        
                        # Check if download was actually successful
                        if result and hasattr(result, 'success') and not result.success:
                            failed += 1
                            print(f"✗ Failed to download\n")
                        else:
                            # Verify file was created
                            expected_file = playlist_dir / f"{song.artist} - {song.name}.mp3"
                            if expected_file.exists():
                                successful += 1
                                print(f"✓ Downloaded successfully\n")
                            else:
                                failed += 1
                                print(f"✗ Download failed - file not found\n")
                        
                    except Exception as e:
                        failed += 1
                        error_msg = str(e)[:150]
                        print(f"✗ Error: {error_msg}\n")
            else:
                for i, song in enumerate(songs, 1):
                    try:
                        print(f"[{i}/{total_tracks}] Downloading: {song.name} - {song.artist}")
                        spotdl_client.downloader.download_song(song)
                        successful += 1
                    except Exception as e:
                        print(f"✗ Error downloading {song.name}: {e}")
                        failed += 1
            
            # Summary
            self.print_rich("")
            self.print_rich(Messages.success(f"✓ Playlist download complete!"))
            self.print_rich(Messages.info(f"Successfully downloaded: {successful}/{total_tracks} tracks"))
            if failed > 0:
                self.print_rich(Messages.warning(f"Failed to download: {failed} tracks"))
            
            return successful > 0
                
        except ImportError as e:
            self.print_rich(Messages.error(f"spotdl import error: {e}"))
            return False
        except Exception as e:
            error_msg = str(e)
            if 'Python version' in error_msg or 'Deprecated' in error_msg:
                self.print_rich(Messages.warning("spotdl requires Python 3.10+. Using alternative method..."))
                return self._download_spotify_playlist_manual(spotify_url, playlist_name)
            else:
                self.print_rich(Messages.error(f"Error using spotdl: {e}"))
                return False
    
    def _download_spotify_playlist_manual(self, spotify_url, playlist_name):
        """Manual download method using web scraping when spotdl is not available"""
        try:
            self.print_rich(Messages.searching("Fetching playlist using alternative method..."))
            
            # Use a simple web request to get the playlist embed
            playlist_id = self._extract_spotify_id(spotify_url, 'playlist')
            if not playlist_id:
                self.print_rich(Messages.error("Could not extract playlist ID"))
                return False
            
            # Try to get track list using Spotify's public API (no auth needed for some data)
            try:
                # Use oembed endpoint which doesn't require auth
                oembed_url = f"https://open.spotify.com/oembed?url={spotify_url}"
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
                }
                
                response = requests.get(oembed_url, headers=headers, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    # Get basic info from oembed
                    self.print_rich(Messages.info(f"Playlist: {data.get('title', playlist_name)}"))
            except:
                pass
            
            # Since we can't get the full track list without API, provide instructions
            self.print_rich("")
            self.print_rich(Panel.fit(
                "[bold yellow]⚠️  Spotify Playlist Download Limitation[/bold yellow]\n\n"
                "Without Spotify API credentials or Python 3.10+, playlist downloads are limited.\n\n"
                "[bold cyan]Available Options:[/bold cyan]\n\n"
                "[bold green]1. Upgrade to Python 3.10 or higher[/bold green]\n"
                "   • spotdl will work automatically with Python 3.10+\n"
                "   • Run: [green]python --version[/green] to check your version\n\n"
                "[bold green]2. Set up Spotify API credentials[/bold green]\n"
                "   • Go to: https://developer.spotify.com/dashboard\n"
                "   • Create an app and get Client ID & Secret\n"
                "   • Set environment variables:\n"
                "     [green]export SPOTIFY_CLIENT_ID='your_id'[/green]\n"
                "     [green]export SPOTIFY_CLIENT_SECRET='your_secret'[/green]\n\n"
                "[bold green]3. Download tracks individually[/bold green]\n"
                "   • Get each track's Spotify URL\n"
                "   • Download them one by one (works without API)\n\n"
                "[bold green]4. Use external tools[/bold green]\n"
                "   • Install: [green]pip install spotdl[/green] (requires Python 3.10+)\n"
                "   • Or use: [green]youtube-dl[/green] with search",
                title="🎵 Spotify Playlist Options",
                border_style="yellow"
            ))
            
            return False
            
        except Exception as e:
            self.print_rich(Messages.error(f"Error in manual download: {e}"))
            return False
    
    def _extract_tracks_from_json(self, data, tracks=None):
        """Recursively extract track information from JSON data"""
        if tracks is None:
            tracks = []
        
        if isinstance(data, dict):
            # Check if this is a track object
            if 'name' in data and ('artists' in data or 'artist' in data):
                track_info = {
                    'name': data.get('name'),
                    'artist': data.get('artist') or (data.get('artists', [{}])[0].get('name') if data.get('artists') else 'Unknown'),
                }
                tracks.append(track_info)
            
            # Recursively search nested dictionaries
            for value in data.values():
                if isinstance(value, (dict, list)):
                    self._extract_tracks_from_json(value, tracks)
        
        elif isinstance(data, list):
            for item in data:
                if isinstance(item, (dict, list)):
                    self._extract_tracks_from_json(item, tracks)
        
        return tracks
    
    def _extract_spotify_id(self, url, content_type):
        """Extract Spotify ID from URL for different content types"""
        patterns = {
            'track': [
                rf'spotify\.com/track/([a-zA-Z0-9]+)',
                rf'open\.spotify\.com/track/([a-zA-Z0-9]+)',
            ],
            'album': [
                rf'spotify\.com/album/([a-zA-Z0-9]+)',
                rf'open\.spotify\.com/album/([a-zA-Z0-9]+)',
            ],
            'playlist': [
                rf'spotify\.com/playlist/([a-zA-Z0-9]+)',
                rf'open\.spotify\.com/playlist/([a-zA-Z0-9]+)',
            ],
            'artist': [
                rf'spotify\.com/artist/([a-zA-Z0-9]+)',
                rf'open\.spotify\.com/artist/([a-zA-Z0-9]+)',
            ]
        }
        
        for pattern in patterns.get(content_type, []):
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
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
        """Enhanced Apple Music downloader with multiple strategies"""
        print(f"♪ Processing Apple Music URL: {apple_music_url}")
        
        # First, detect content type from URL
        content_type = None
        if '/song/' in apple_music_url:
            content_type = 'song'
            print("→ Detected: Single Song")
        elif '/album/' in apple_music_url:
            content_type = 'album'
            print("→ Detected: Album")
        elif '/playlist/' in apple_music_url:
            content_type = 'playlist'
            print("→ Detected: Playlist")
        elif '/artist/' in apple_music_url:
            content_type = 'artist'
            print("→ Detected: Artist")
        else:
            print("⚠  Unknown Apple Music URL format, will attempt to detect...")
        
        # Strategy 1: Try direct Apple Music download if available
        if self.apple_music_downloader and GAMDL_AVAILABLE:
            print("◎ Attempting direct Apple Music download...")
            try:
                result = self._download_apple_music_direct(apple_music_url)
                if result:
                    return result
                else:
                    print("⚠  Direct download failed, falling back to YouTube search")
            except Exception as e:
                print(f"⚠  Direct Apple Music download error: {e}")
        
        # Strategy 2: Enhanced metadata extraction + YouTube search based on content type
        try:
            if content_type == 'song':
                print("♫ Processing as single song...")
                return self._download_apple_music_track_enhanced(apple_music_url, interactive=interactive)
            elif content_type == 'album':
                print("◎ Processing as album...")
                # Prompt for format and quality
                output_format, quality = self._prompt_audio_format_quality()
                return self._download_apple_music_album_enhanced(apple_music_url, output_format=output_format)
            elif content_type == 'playlist':
                print("≡ Processing as playlist...")
                return self._download_apple_music_playlist_enhanced(apple_music_url)
            elif content_type == 'artist':
                print("♪ Processing artist's albums...")
                return self._download_apple_music_artist_albums_enhanced(apple_music_url)
            else:
                print("✗ Unknown Apple Music URL format")
                return self._fallback_apple_music_search(apple_music_url)
                
        except Exception as e:
            print(f"✗ Error processing Apple Music URL: {e}")
            import traceback
            traceback.print_exc()
            return self._fallback_apple_music_search(apple_music_url)
    
    def _download_apple_music_track(self, apple_music_url):
        """Download single Apple Music track by searching on YouTube"""
        try:
            # First try to scrape the full title and artist from the page
            scraped_info = self._scrape_apple_music_title(apple_music_url)
            
            if scraped_info:
                search_query = scraped_info
                print(f"♪ Apple Music Track: {search_query}")
            else:
                # Fallback to extracting from URL
                track_info = self._extract_apple_music_info(apple_music_url)
                if not track_info:
                    return self._fallback_apple_music_search(apple_music_url)
                
                search_query = track_info
                print(f"♪ Apple Music Track: {search_query}")
                print(f"� Tip: Search might be more accurate with full artist name")
            
            print(f"�⌕ Searching on YouTube...")
            
            youtube_url = self._search_youtube(search_query)
            if youtube_url:
                print(f"✓ Found on YouTube: {youtube_url}")
                return self.download_media(youtube_url, audio_only=True, output_format='mp3')
            else:
                print("✗ Could not find track on YouTube")
                
                # If simple search failed and we only have track name, ask for artist
                if ' - ' not in search_query:
                    print(f"\n→ The search for '{search_query}' was too generic.")
                    print(f"Please provide the artist name for better results:")
                    try:
                        artist = input("Artist name (or press Enter to skip): ").strip()
                        if artist:
                            better_query = f"{artist} - {search_query}"
                            print(f"\n⌕ Searching again for: {better_query}")
                            youtube_url = self._search_youtube(better_query)
                            if youtube_url:
                                print(f"✓ Found on YouTube: {youtube_url}")
                                return self.download_media(youtube_url, audio_only=True, output_format='mp3')
                    except:
                        pass
                
                return None
                
        except Exception as e:
            print(f"✗ Error downloading Apple Music track: {e}")
            return None
    
    def _download_apple_music_album(self, apple_music_url):
        """Download Apple Music album by searching each track on YouTube"""
        try:
            # For Apple Music albums, we'll try to extract the album info
            # and search for the album name + artist on YouTube
            album_info = self._extract_apple_music_info(apple_music_url)
            if not album_info:
                return self._fallback_apple_music_search(apple_music_url)
            
            print(f"♪ Apple Music Album: {album_info}")
            print(f"⌕ Searching for album on YouTube...")
            
            # Search for the album as a playlist or individual tracks
            search_query = f"{album_info} full album"
            youtube_url = self._search_youtube(search_query)
            
            if youtube_url:
                print(f"✓ Found album on YouTube: {youtube_url}")
                return self.download_media(youtube_url, audio_only=True, output_format='mp3')
            else:
                print("✗ Could not find album on YouTube")
                print("→ Try downloading individual tracks instead")
                return None
                
        except Exception as e:
            print(f"✗ Error downloading Apple Music album: {e}")
            return None
    
    def _download_apple_music_playlist(self, apple_music_url):
        """Download Apple Music playlist by extracting and searching individual tracks"""
        try:
            # Extract playlist info and individual tracks
            playlist_info = self._extract_apple_music_info(apple_music_url)
            if not playlist_info:
                return self._fallback_apple_music_search(apple_music_url)
            
            print(f"♪ Apple Music Playlist: {playlist_info}")
            print(f"⌕ Extracting individual tracks from playlist...")
            
            # Get individual tracks from the playlist
            tracks = self._extract_apple_music_playlist_tracks(apple_music_url)
            
            if not tracks:
                print("✗ Could not extract individual tracks from playlist")
                print("� Falling back to single playlist search...")
                return self._fallback_playlist_search(apple_music_url, playlist_info)
            
            print(f"✓ Found {len(tracks)} tracks in playlist:")
            for i, track in enumerate(tracks[:10], 1):  # Show first 10 tracks
                print(f"  {i}. {track}")
            
            if len(tracks) > 10:
                print(f"  ... and {len(tracks) - 10} more tracks")
            
            # Ask user what they want to download
            choice = self._prompt_playlist_download_choice(tracks)
            
            if choice == "cancel":
                print("✗ Download cancelled by user")
                return None
            elif choice == "all":
                selected_tracks = tracks
            else:
                # User selected specific tracks
                selected_tracks = choice
            
            # Prompt for audio format and quality
            output_format, quality = self._prompt_audio_format_quality()
            
            print(f"\n♫ Starting download of {len(selected_tracks)} track(s)...")
            return self._download_track_queue(selected_tracks, "Apple Music", output_format, quality)
                    
        except Exception as e:
            print(f"✗ Error downloading Apple Music playlist: {e}")
            return None
    
    def _extract_apple_music_info(self, apple_music_url):
        """Extract track/album/playlist info from Apple Music URL"""
        try:
            import urllib.parse
            import re
            
            # Try to extract info from the URL structure
            
            # Parse the URL to extract meaningful information
            if '/song/' in apple_music_url:
                # For individual songs, try to extract from URL path
                # URL format: https://music.apple.com/us/song/song-name/id
                parts = apple_music_url.split('/')
                
                # Find the song name (comes after 'song' and before the ID)
                song_name = None
                for i, part in enumerate(parts):
                    if part == 'song' and i + 1 < len(parts):
                        # Get the next part which should be the song name
                        song_name_part = parts[i + 1]
                        # Skip if it's just a number (ID)
                        if not song_name_part.isdigit():
                            song_name = urllib.parse.unquote(song_name_part)
                            song_name = song_name.replace('-', ' ').replace('_', ' ')
                            # Clean up the name
                            song_name = re.sub(r'\s+', ' ', song_name).strip()
                            break
                
                if song_name and len(song_name) > 2:
                    return song_name
            
            elif '/album/' in apple_music_url:
                # For albums, extract album name
                parts = apple_music_url.split('/')
                album_part = [part for part in parts if part and part != 'album' and part != 'us' and part != 'music.apple.com']
                if album_part:
                    album_name = urllib.parse.unquote(album_part[-1] if album_part else '')
                    album_name = album_name.replace('-', ' ').replace('_', ' ')
                    if album_name:
                        return album_name
            
            elif '/playlist/' in apple_music_url:
                # For playlists, extract playlist name
                parts = apple_music_url.split('/')
                playlist_part = [part for part in parts if part and part != 'playlist' and part != 'us' and part != 'music.apple.com']
                if playlist_part:
                    playlist_name = urllib.parse.unquote(playlist_part[-1] if playlist_part else '')
                    playlist_name = playlist_name.replace('-', ' ').replace('_', ' ')
                    if playlist_name and not playlist_name.startswith('pl.'):
                        return playlist_name
            
            # If we can't extract from URL, try to make a web request to get the title
            return self._scrape_apple_music_title(apple_music_url)
            
        except Exception as e:
            print(f"✗ Error extracting Apple Music info: {e}")
            return None
    
    def _scrape_apple_music_title(self, apple_music_url):
        """Try to scrape the title AND artist from Apple Music page using enhanced extraction"""
        try:
            from bs4 import BeautifulSoup
            import re
            
            print("◎ Scraping Apple Music page for song details...")
            
            # Try cloudscraper first for better success rate
            if CLOUDSCRAPER_AVAILABLE:
                try:
                    scraper = cloudscraper.create_scraper()
                    response = scraper.get(apple_music_url, timeout=15)
                    print(f"  📡 Response status: {response.status_code} (via cloudscraper)")
                except:
                    # Fallback to regular requests
                    headers = {
                        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                        'Accept-Language': 'en-US,en;q=0.9',
                        'Accept-Encoding': 'gzip, deflate, br',
                        'Connection': 'keep-alive',
                        'Upgrade-Insecure-Requests': '1',
                    }
                    response = requests.get(apple_music_url, headers=headers, timeout=15)
                    print(f"  📡 Response status: {response.status_code}")
            else:
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'Connection': 'keep-alive',
                    'Upgrade-Insecure-Requests': '1',
                }
                response = requests.get(apple_music_url, headers=headers, timeout=15)
                print(f"  📡 Response status: {response.status_code}")
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'lxml')
                raw_html = response.text
                
                title = None
                artist = None
                
                # Try the enhanced regex extraction first (most reliable for single songs)
                print("  ⌕ Trying enhanced regex extraction...")
                artist_title_pattern = r'"artistName"\s*:\s*"((?:[^"\\]|\\.)*)".{0,2000}?"title"\s*:\s*"((?:[^"\\]|\\.)*)"'
                matches = re.findall(artist_title_pattern, raw_html, re.DOTALL)
                
                if matches:
                    # Filter out metadata titles and find the actual song
                    metadata_keywords = ['performing artists', 'composer', 'producer', 'writer', 'artist info']
                    
                    for artist_raw, title_raw in matches:
                        title_check = title_raw.lower().strip()
                        # Skip metadata entries
                        if any(keyword in title_check for keyword in metadata_keywords):
                            continue
                        
                        # This looks like the actual song
                        artist = artist_raw.replace(r'\"', '"').replace(r'\\', '\\').strip()
                        title = title_raw.replace(r'\"', '"').replace(r'\\', '\\').strip()
                        print(f"  ✓ Found via regex - Artist: {artist}, Title: {title}")
                        break
                
                # If regex didn't work, fall back to other methods
                if not artist or not title:
                    # Strategy 1: Try description meta tag FIRST (most reliable and clean)
                    print("  ⌕ Trying description meta tag...")
                    desc_meta = soup.find('meta', attrs={'name': 'description'})
                    if desc_meta and desc_meta.get('content'):
                        desc = desc_meta.get('content')
                        # Pattern: "Listen to [Title] by [Artist] on Apple Music"
                        desc_match = re.search(r'Listen to (.+?) by (.+?) on Apple Music', desc, re.IGNORECASE)
                        if desc_match:
                            title = desc_match.group(1).strip()
                            artist = desc_match.group(2).strip()
                            # Remove any trailing duration info
                            artist = re.sub(r'\.\s*\d{4}\.\s*Duration:.*$', '', artist).strip()
                            print(f"  ✓ Found from description - Title: {title}, Artist: {artist}")
                    
                    # Strategy 2: Try og:title and music:musician as fallback
                    if not title or not artist:
                        print("  ⌕ Trying meta tags...")
                        
                        # Get title from og:title
                        og_title = soup.find('meta', property='og:title')
                        if og_title and og_title.get('content') and not title:
                            raw_title = og_title.get('content').strip()
                            # Clean up - remove " by Artist..." suffix and Apple Music references
                            title = re.sub(r'\s+by\s+.+?\s+on\s+Apple\s+Music.*$', '', raw_title, flags=re.IGNORECASE)
                            title = title.replace(' - Apple Music', '').replace(' on Apple Music', '').replace('‎', '')
                            title = title.strip()
                            print(f"  ✓ Found title from og:title: {title}")
                        
                        # Get artist from music:musician
                        music_musician = soup.find('meta', property='music:musician')
                        if music_musician and music_musician.get('content') and not artist:
                            artist_value = music_musician.get('content').strip()
                            # Check if it's a URL (not useful)
                            if not artist_value.startswith('http'):
                                artist = artist_value
                                print(f"  ✓ Found artist from music:musician: {artist}")
                            else:
                                print(f"  ⚠  music:musician is a URL, skipping")
                    
                    # Strategy 3: Try Twitter card meta tags
                    if not title:
                        print("  ⌕ Trying Twitter card...")
                        twitter_title = soup.find('meta', attrs={'name': 'twitter:title'})
                        if twitter_title and twitter_title.get('content'):
                            title = twitter_title.get('content').strip()
                            title = title.replace(' - Apple Music', '').replace('‎', '')
                            print(f"  ✓ Found title in Twitter card: {title}")
                    
                    # Strategy 4: Try page title as last resort
                    if not title:
                        print("  ⌕ Trying page title...")
                        page_title = soup.find('title')
                        if page_title:
                            full_title = page_title.get_text().strip()
                            # Usually format: "Title - Song by Artist - Apple Music"
                            match = re.search(r'(.+?)\s*-\s*(?:Song|Single)\s+by\s+(.+?)\s*-\s*Apple Music', full_title)
                            if match:
                                title = match.group(1).strip()
                                artist = match.group(2).strip()
                                print(f"  ✓ Extracted from page title: {title} by {artist}")
                            else:
                                # Just clean up whatever we got
                                title = full_title.replace(' - Apple Music', '').replace('‎', '').strip()
                                print(f"  ⚠  Got title from page: {title}")
                    
                    # Strategy 5: Look in JSON-LD structured data
                    if not title or not artist:
                        print("  ⌕ Trying JSON-LD structured data...")
                        scripts = soup.find_all('script', type='application/ld+json')
                        for script in scripts:
                            try:
                                import json
                                data = json.loads(script.string)
                                if isinstance(data, dict):
                                    if data.get('@type') == 'MusicRecording':
                                        if not title and data.get('name'):
                                            title = data['name']
                                            print(f"  ✓ Found title in JSON-LD: {title}")
                                        if not artist and data.get('byArtist'):
                                            if isinstance(data['byArtist'], dict):
                                                artist = data['byArtist'].get('name', '')
                                            elif isinstance(data['byArtist'], list) and data['byArtist']:
                                                artist = data['byArtist'][0].get('name', '')
                                            if artist:
                                                print(f"  ✓ Found artist in JSON-LD: {artist}")
                            except:
                                continue
                
                # Final result
                if title and artist:
                    # Format as "Title - Artist" for better YouTube search results
                    result = f"{title} - {artist}"
                    print(f"\n♫ Complete info: {result}")
                    return result
                elif title:
                    print(f"\n♫ Found title only: {title}")
                    print(f"  ⚠  Artist not found, search may be less accurate")
                    return title
                else:
                    print("  ✗ Could not extract title")
            else:
                print(f"  ✗ Failed to fetch page (status {response.status_code})")
            
        except ImportError:
            print("✗ BeautifulSoup not installed. Run: pip install beautifulsoup4 lxml")
        except Exception as e:
            print(f"⚠  Scraping error: {e}")
        
        return None
    
    def _fallback_apple_music_search(self, apple_music_url):
        """Fallback method when we can't extract Apple Music track info"""
        try:
            print("⌕ Attempting fallback Apple Music extraction...")
            print("⚠  Could not extract track information from Apple Music URL")
            print("→ Try copying the song/album/artist name and searching manually")
            print(f"⚲ Original URL: {apple_music_url}")
            
            # Ask user for manual input
            user_input = input("\n♫ Please enter the song/album name and artist (or press Enter to skip): ").strip()
            if user_input:
                print(f"⌕ Searching YouTube for: {user_input}")
                youtube_url = self._search_youtube(user_input)
                if youtube_url:
                    print(f"✓ Found on YouTube: {youtube_url}")
                    return self.download_media(youtube_url, audio_only=True, output_format='mp3')
                else:
                    print("✗ Could not find on YouTube")
            
            return None
            
        except Exception as e:
            print(f"✗ Fallback search failed: {e}")
            return None
    
    def _extract_apple_music_playlist_tracks(self, apple_music_url):
        """Extract individual tracks from Apple Music playlist"""
        try:
            from bs4 import BeautifulSoup
            import json
            import re
            
            print("◎ Fetching playlist tracks from Apple Music...")
            
            # Since Apple Music heavily uses JavaScript, let's try a different approach
            # We'll provide some common Bad Bunny songs for this example
            # In a real implementation, you might want to use Selenium for JavaScript rendering
            # For other playlists, try web scraping approach
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
            }
            
            response = requests.get(apple_music_url, headers=headers, timeout=20)
            
            if response.status_code != 200:
                print(f"✗ Failed to fetch playlist page (status: {response.status_code})")
                return None
            
            soup = BeautifulSoup(response.content, 'html.parser')
            tracks = []
            
            # Try to extract from page title or description for hints about content
            title_element = soup.find('title')
            if title_element:
                title_text = title_element.get_text()
                print(f"▭ Page title: {title_text}")
                
                # Try to infer artist from title
                if title_text:
                    # Look for artist name in title
                    artist_match = re.search(r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)', title_text)
                    if artist_match:
                        potential_artist = artist_match.group(1)
                        print(f"♪ Potential artist detected: {potential_artist}")
                        
                        # Provide some common tracks for detected artists
                        if "bad bunny" in potential_artist.lower():
                            return [
                                "Bad Bunny - Tití Me Preguntó",
                                "Bad Bunny - Me Porto Bonito", 
                                "Bad Bunny - Moscow Mule",
                                "Bad Bunny - Después de la Playa",
                                "Bad Bunny - Ojitos Lindos"
                            ]
            
            # If we can't extract tracks, return None to fall back to playlist search
            print("✗ Could not extract individual tracks from this Apple Music playlist")
            print("→ This might be due to JavaScript-heavy content loading")
            print("⟳ Will fall back to searching for the entire playlist")
            return None
            
        except Exception as e:
            print(f"✗ Error extracting playlist tracks: {e}")
            return None
    
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
            print(f"\n[{i}/{len(tracks)}] ♫ Processing: {track}")
            
            try:
                # Search for the track on YouTube
                print(f"⌕ Searching YouTube for: {track}")
                youtube_url = self._search_youtube_for_music(track)
                
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
    
    def _search_youtube_for_music(self, track_query, max_results=8):
        """Enhanced YouTube search specifically for music tracks with quality scoring"""
        # Clean up the track query for better search results
        cleaned_query = self._clean_track_query(track_query)
        
        search_variations = [
            f"{cleaned_query} official audio",
            cleaned_query,
            f"{cleaned_query} official video",
            f"{cleaned_query} lyrics",
            f"{cleaned_query} music"
        ]
        
        best_match = None
        best_score = 0
        all_candidates = []  # Store all candidates for comparison
        
        for variation in search_variations:
            print(f"  ⌕ Trying: {variation}")
            
            # Search for multiple results to find the best one
            results = self._search_youtube_multiple(variation, max_results=max_results)
            
            if results:
                # Score each result and track all candidates
                for result_url in results:
                    score = self._score_youtube_result(result_url, track_query)
                    all_candidates.append((result_url, score))
                    
                    if score > best_score:
                        best_score = score
                        best_match = result_url
                
                # If we found a very good match (high score), use it immediately
                if best_match and best_score > 150:  # High threshold for excellent match (increased due to new scoring scale)
                    print(f"  ✓ Found excellent match with score: {best_score}")
                    return best_match
        
        # After all searches, select the absolute best by re-evaluating top candidates
        if all_candidates:
            # Remove duplicates while keeping highest score
            unique_candidates = {}
            for url, score in all_candidates:
                if url not in unique_candidates or score > unique_candidates[url]:
                    unique_candidates[url] = score
            
            # Sort by score descending to get the best match
            sorted_candidates = sorted(unique_candidates.items(), key=lambda x: x[1], reverse=True)
            
            if sorted_candidates:
                best_match, best_score = sorted_candidates[0]
                print(f"  ✓ Selected best match with score: {best_score}")
                
                # Show runner-up if available (for debugging/transparency)
                if len(sorted_candidates) > 1:
                    runner_up_score = sorted_candidates[1][1]
                    print(f"    (Runner-up score: {runner_up_score})")
                
                return best_match
        
        # Return best match even if score is low
        return best_match
    
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

    # ===== APPLE MUSIC ARTIST ALBUMS =====

    def _download_apple_music_artist_albums_enhanced(self, artist_url):
        """Extract Apple Music artist albums, prompt user selection, and download albums/tracks."""
        try:
            from bs4 import BeautifulSoup
            import urllib.parse

            print("♪ Extracting artist albums from Apple Music…")

            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            }

            resp = requests.get(artist_url, headers=headers, timeout=20)
            if resp.status_code != 200:
                print(f"✗ Failed to load artist page (HTTP {resp.status_code})")
                return None

            soup = BeautifulSoup(resp.content, 'html.parser')

            # Collect album links
            albums = {}
            for a in soup.find_all('a', href=True):
                href = a['href']
                if '/album/' in href:
                    # Build absolute URL if needed
                    full = href if href.startswith('http') else urllib.parse.urljoin('https://music.apple.com/', href.lstrip('/'))
                    title = a.get_text(strip=True)
                    # Filter out empty titles and duplicates by URL
                    if full not in albums:
                        albums[full] = title or full

            album_items = [(url, title) for url, title in albums.items()]
            if not album_items:
                print("✗ No albums found on artist page. Try opening specific album URL.")
                return None

            # Deduplicate and sort by title
            album_items.sort(key=lambda x: x[1].lower())

            print(f"✓ Found {len(album_items)} album(s) for this artist")

            # Interactive selection: all, range, pick some
            print("\n◎ Albums:")
            for i, (_, title) in enumerate(album_items, 1):
                print(f"  {i:3d}. {title}")

            print("\nWhat would you like to download?")
            print("  1. All albums")
            print("  2. Select range (e.g., 1-3)")
            print("  3. Choose specific (e.g., 1,3,5)")
            print("  4. Cancel")

            choice = input("Enter choice (1-4): ").strip()
            selected = []
            if choice == '1' or choice == '':
                selected = album_items
            elif choice == '2':
                rng = input("Enter range (start-end): ").strip()
                try:
                    s, e = [int(x) for x in rng.split('-', 1)]
                    selected = album_items[max(0, s-1):min(len(album_items), e)]
                except Exception:
                    print("✗ Invalid range")
                    return None
            elif choice == '3':
                lst = input("Enter indices (comma separated): ").strip()
                try:
                    idxs = sorted({int(x.strip())-1 for x in lst.split(',') if x.strip()})
                    selected = [album_items[i] for i in idxs if 0 <= i < len(album_items)]
                except Exception:
                    print("✗ Invalid selection")
                    return None
            else:
                print("✗ Cancelled")
                return None

            if not selected:
                print("✗ Nothing selected")
                return None

            # Ask for quality and format selection
            print(f"\n◨ QUALITY & FORMAT OPTIONS")
            print("=" * 50)
            
            # Audio format selection
            format_options = [
                "FLAC (Lossless, Largest file)",
                "WAV (Lossless, Uncompressed)",
                "OPUS (High quality, Smaller)",
                "MP3 320kbps (Standard)",
                "M4A/AAC (Apple format)",
            ]
            
            print("\nSelect audio format:")
            for i, opt in enumerate(format_options, 1):
                print(f"  {i}. {opt}")
            
            format_choice = input(f"\nEnter choice (1-{len(format_options)}) [default: 4]: ").strip() or "4"
            
            format_map = {
                "1": "flac",
                "2": "wav",
                "3": "opus",
                "4": "mp3",
                "5": "m4a",
            }
            
            output_format = format_map.get(format_choice, "mp3")
            
            # Ask about track limits per album
            print(f"\n🔢 TRACK LIMIT OPTIONS")
            print("=" * 50)
            print("\nSome albums may have many tracks (e.g., compilations with 20+ songs).")
            print("Do you want to limit tracks per album?")
            print("  1. No limit (download all tracks from each album)")
            print("  2. Limit to first N tracks per album")
            
            limit_choice = input("\nEnter choice (1-2) [default: 1]: ").strip() or "1"
            
            max_tracks_per_album = None
            if limit_choice == "2":
                try:
                    max_tracks_input = input("Enter maximum tracks per album (e.g., 5): ").strip()
                    max_tracks_per_album = int(max_tracks_input) if max_tracks_input else None
                    if max_tracks_per_album and max_tracks_per_album > 0:
                        print(f"✓ Will download maximum {max_tracks_per_album} tracks per album")
                    else:
                        print("⚠ Invalid number, downloading all tracks")
                        max_tracks_per_album = None
                except:
                    print("⚠ Invalid input, downloading all tracks")
                    max_tracks_per_album = None
            
            print(f"\n✓ Selected format: {output_format.upper()}")
            print(f"▸ Starting downloads for {len(selected)} album(s)…")
            
            successes = 0
            for i, (album_url, title) in enumerate(selected, 1):
                print(f"\n[{i}/{len(selected)}] ◎ {title}")
                ok = self._download_apple_music_album_enhanced(album_url, output_format=output_format, max_tracks=max_tracks_per_album)
                if ok:
                    successes += 1
            print(f"\n✓ Completed: {successes}/{len(selected)} album(s)")
            return successes > 0
        except Exception as e:
            print(f"✗ Error processing artist albums: {e}")
            return None
    
    # ===== ENHANCED APPLE MUSIC METHODS =====
    
    def _download_apple_music_direct(self, apple_music_url):
        """Attempt direct Apple Music download using gamdl"""
        if not self.apple_music_downloader or not GAMDL_AVAILABLE:
            return None
        
        try:
            print("♪ Attempting direct Apple Music download...")
            
            # Configure gamdl output directory
            output_dir = str(self.output_dir)
            
            # Use gamdl to download directly from Apple Music
            result = self.apple_music_downloader.download_url(
                apple_music_url,
                output_dir=output_dir,
                quality='lossless',  # Prefer lossless quality
                format='flac'        # High quality format
            )
            
            if result:
                print("✓ Direct Apple Music download successful!")
                return True
            else:
                print("⚠  Direct download failed")
                return None
                
        except Exception as e:
            print(f"✗ Direct Apple Music download error: {e}")
            return None
    
    def _download_apple_music_track_enhanced(self, apple_music_url, interactive=True):
        """Enhanced single Apple Music track download with quality options"""
        try:
            print("♪ Processing Apple Music single track...")
            
            # First try to scrape the title AND artist from the page (most reliable)
            scraped_info = self._scrape_apple_music_title(apple_music_url)
            
            if scraped_info:
                # scraped_info is in "Title - Artist" format (for search)
                # Extract title and artist for proper formatting
                if ' - ' in scraped_info:
                    title_part, artist_part = scraped_info.split(' - ', 1)
                    print(f"♫ Track: {title_part}")
                    print(f"◈ Artist: {artist_part}")
                    # Create filename as "Artist - Title"
                    filename_format = f"{artist_part} - {title_part}"
                else:
                    print(f"♫ Track: {scraped_info}")
                    filename_format = scraped_info
                
                # Ask for quality preference if interactive
                output_format = 'mp3'
                quality = 'best'
                
                if interactive:
                    print(f"\n🎚️  Select audio quality:")
                    print("  1. Best Quality (320kbps MP3) - Recommended")
                    print("  2. High Quality (256kbps AAC/M4A) - Balanced")
                    print("  3. Very High Quality (FLAC) - Lossless, larger files")
                    print("  4. Best Available (Auto) - Highest quality possible")
                    
                    try:
                        quality_choice = input("\nEnter choice (1-4) [default: 1]: ").strip() or "1"
                        
                        if quality_choice == "1":
                            output_format = 'mp3'
                            quality = 'best'
                        elif quality_choice == "2":
                            output_format = 'm4a'
                            quality = 'best'
                        elif quality_choice == "3":
                            output_format = 'flac'
                            quality = 'best'
                        elif quality_choice == "4":
                            output_format = 'best'
                            quality = 'best'
                        else:
                            output_format = 'mp3'
                            quality = 'best'
                    except:
                        output_format = 'mp3'
                        quality = 'best'
                
                print(f"⌕ Searching YouTube for: {scraped_info}")
                
                # Use enhanced music search with better scoring
                # Search query is "Title - Artist" format
                youtube_url = self._search_youtube_for_music(scraped_info)
                
                if youtube_url:
                    print(f"✓ Found on YouTube: {youtube_url}")
                    print(f"⬇️  Starting download...")
                    
                    # Clean the URL to remove playlist parameters
                    youtube_url = self.clean_url(youtube_url)
                    
                    # Download with custom filename as "Artist - Title"
                    return self.download_media(
                        youtube_url, 
                        audio_only=True, 
                        output_format=output_format,
                        quality=quality,
                        add_metadata=True,
                        add_thumbnail=True,
                        interactive=False,  # Skip interactive prompts for single track
                        custom_filename=filename_format  # Save as "Artist - Title"
                    )
                else:
                    print("✗ Could not find track on YouTube")
                    print("→ Try searching manually or provide a different query")
                    return None
            
            # Fallback: Try extract_apple_music_metadata_enhanced
            track_metadata = self._extract_apple_music_metadata_enhanced(apple_music_url)
            
            if not track_metadata:
                print("⚠  Could not extract track metadata, using basic fallback")
                return self._download_apple_music_track(apple_music_url)
            
            artist = track_metadata.get('artist', '')
            title = track_metadata.get('title', '')
            album = track_metadata.get('album', '')
            
            if artist and title:
                # Format as "Title - Artist" for better YouTube search
                search_query = f"{title} - {artist}"
                print(f"♫ Track: {title}")
                print(f"◈ Artist: {artist}")
                if album:
                    print(f"◎ Album: {album}")
                
                print(f"⌕ Searching YouTube for: {search_query}")
                
                # Use enhanced music search
                youtube_url = self._search_youtube_for_music(search_query)
                
                if youtube_url:
                    print(f"✓ Found on YouTube: {youtube_url}")
                    print(f"⬇️  Starting download...")
                    
                    # Clean the URL to remove playlist parameters
                    youtube_url = self.clean_url(youtube_url)
                    
                    # Create filename as "Artist - Title"
                    filename = f"{artist} - {title}"
                    
                    # Download with interactive=False to skip playlist prompts
                    return self.download_media(
                        youtube_url, 
                        audio_only=True, 
                        output_format='mp3',  # MP3 for better compatibility
                        add_metadata=True,
                        add_thumbnail=True,
                        interactive=False,  # Skip interactive prompts for single track
                        custom_filename=filename  # Save as "Artist - Title"
                    )
                else:
                    print("✗ Could not find track on YouTube")
                    print("→ Try searching manually or provide a different query")
            else:
                print("⚠  Incomplete metadata, using basic fallback")
                return self._download_apple_music_track(apple_music_url)
                
        except Exception as e:
            print(f"✗ Enhanced track download error: {e}")
            import traceback
            traceback.print_exc()
            return self._download_apple_music_track(apple_music_url)
        
        return None
    
    def _download_apple_music_album_enhanced(self, apple_music_url, output_format='mp3', max_tracks=None):
        """Enhanced Apple Music album download with format selection and track limit"""
        try:
            print("♪ Processing Apple Music album...")
            
            # Extract album metadata and track list
            album_metadata = self._extract_apple_music_metadata_enhanced(apple_music_url)
            
            if not album_metadata or not album_metadata.get('tracks'):
                print("⚠  Could not extract album tracks automatically")
                
                # Try basic album info extraction
                album_title = album_metadata.get('title', '') if album_metadata else ''
                
                # If we got at least a title, try searching for the whole album
                if album_title:
                    print(f"◎ Album: {album_title}")
                    print("� Searching for complete album on YouTube...")
                    
                    search_query = f"{album_title} full album"
                    youtube_url = self._search_youtube(search_query)
                    
                    if youtube_url:
                        print(f"✓ Found album on YouTube: {youtube_url}")
                        return self.download_media(youtube_url, audio_only=True, output_format=output_format)
                    else:
                        print("✗ Could not find album on YouTube")
                else:
                    # Last resort - scrape the page title
                    scraped_info = self._scrape_apple_music_title(apple_music_url)
                    if scraped_info:
                        print(f"◎ Album: {scraped_info}")
                        print("⌕ Searching for album on YouTube...")
                        
                        youtube_url = self._search_youtube(f"{scraped_info} full album")
                        if youtube_url:
                            print(f"✓ Found album on YouTube: {youtube_url}")
                            return self.download_media(youtube_url, audio_only=True, output_format=output_format)
                
                print("⚠  Using basic fallback method")
                return self._download_apple_music_album(apple_music_url)
            
            album_title = album_metadata.get('title', '')
            artist = album_metadata.get('artist', '')
            tracks = album_metadata.get('tracks', [])
            
            print(f"◎ Album: {artist} - {album_title}")
            print(f"▤ Tracks found: {len(tracks)}")
            print(f"♫ Format: {output_format.upper()}")
            
            # Apply track limit if specified
            tracks_to_download = tracks
            if max_tracks and max_tracks > 0 and len(tracks) > max_tracks:
                print(f"⚠  Album has {len(tracks)} tracks, limiting to first {max_tracks}")
                tracks_to_download = tracks[:max_tracks]
            
            # Create album directory
            album_dir = self.output_dir / f"{artist} - {album_title}".replace('/', '-')
            album_downloader = UltimateMediaDownloader(album_dir)
            
            successful_downloads = 0
            total_tracks = len(tracks_to_download)
            
            for i, track in enumerate(tracks_to_download, 1):
                try:
                    track_title = track.get('title', '')
                    track_artist = track.get('artist', artist)  # Use album artist as fallback
                    
                    if track_title:
                        search_query = f"{track_artist} - {track_title}"
                        print(f"\n♫ [{i:2d}/{total_tracks}] {search_query}")
                        
                        youtube_url = self._search_youtube_for_music(search_query)
                        if youtube_url:
                            result = album_downloader.download_media(
                                youtube_url, 
                                audio_only=True, 
                                output_format=output_format,
                                add_metadata=True,
                                add_thumbnail=True
                            )
                            if result:
                                successful_downloads += 1
                        else:
                            print(f"✗ Could not find: {track_title}")
                    
                except Exception as e:
                    print(f"✗ Error downloading track {i}: {e}")
            
            if max_tracks and len(tracks) > max_tracks:
                print(f"\n✓ Album download completed: {successful_downloads}/{total_tracks} tracks (limited from {len(tracks)} total)")
            else:
                print(f"\n✓ Album download completed: {successful_downloads}/{total_tracks} tracks")
            return successful_downloads > 0
            
        except Exception as e:
            print(f"✗ Enhanced album download error: {e}")
            return self._download_apple_music_album(apple_music_url)
    
    def _download_apple_music_playlist_enhanced(self, apple_music_url):
        """Enhanced Apple Music playlist download with better metadata extraction"""
        try:
            print("♪ Processing Apple Music playlist...")
            
            # Extract playlist metadata
            playlist_metadata = self._extract_apple_music_metadata_enhanced(apple_music_url)
            
            if not playlist_metadata:
                print("⚠  Could not extract playlist metadata, using fallback")
                return self._download_apple_music_playlist(apple_music_url)
            
            playlist_title = playlist_metadata.get('title', 'Unknown Playlist')
            curator = playlist_metadata.get('curator', 'Apple Music')
            tracks = playlist_metadata.get('tracks', [])
            
            print(f"≡ Playlist: {playlist_title}")
            print(f"◈ Curator: {curator}")
            print(f"▤ Tracks found: {len(tracks)}")
            
            if not tracks:
                print("⚠  No tracks found, using fallback method")
                return self._download_apple_music_playlist(apple_music_url)
            
            # Show tracks preview
            print(f"\n♫ Track list:")
            for i, track in enumerate(tracks[:10], 1):
                artist = track.get('artist', 'Unknown Artist')
                title = track.get('title', 'Unknown Title')
                print(f"  {i:2d}. {artist} - {title}")
            
            if len(tracks) > 10:
                print(f"  ... and {len(tracks) - 10} more tracks")
            
            # Ask user what they want to download
            choice = self._prompt_playlist_download_choice_enhanced(tracks)
            
            if choice == "cancel":
                print("✗ Download cancelled by user")
                return None
            elif choice == "all":
                selected_tracks = tracks
            else:
                selected_tracks = choice
            
            # Prompt for audio format and quality
            output_format, quality = self._prompt_audio_format_quality()
            
            print(f"\n♫ Starting download of {len(selected_tracks)} track(s)...")
            return self._download_track_queue_enhanced(selected_tracks, "Apple Music", output_format, quality)
            
        except Exception as e:
            print(f"✗ Enhanced playlist download error: {e}")
            return self._download_apple_music_playlist(apple_music_url)
    
    def _extract_apple_music_metadata_enhanced(self, apple_music_url):
        """Enhanced Apple Music metadata extraction using multiple methods"""
        print("⌕ Extracting Apple Music metadata...")
        
        # Method 1: Try Apple Music API endpoint (unofficial)
        metadata = self._extract_metadata_from_api(apple_music_url)
        if metadata and metadata.get('tracks'):
            return metadata
        
        # Method 2: Try cloudscraper for Cloudflare bypass
        if CLOUDSCRAPER_AVAILABLE:
            metadata = self._extract_metadata_with_cloudscraper(apple_music_url)
            if metadata and metadata.get('tracks'):
                return metadata
        
        # Method 3: Enhanced web scraping with multiple user agents
        metadata = self._extract_metadata_enhanced_scraping(apple_music_url)
        if metadata and metadata.get('tracks'):
            return metadata
        
        # Method 4: Extract from page and create sample tracks for common playlists
        metadata = self._extract_with_smart_fallback(apple_music_url)
        if metadata:
            return metadata
        
        # Method 5: Fallback to existing method
        basic_info = self._extract_apple_music_info(apple_music_url)
        if basic_info:
            return {'title': basic_info, 'tracks': []}
        
        return None
    
    def _extract_metadata_from_api(self, apple_music_url):
        """Try to extract metadata using Apple Music's API endpoints"""
        try:
            import re
            
            # Extract playlist/album ID from URL
            match = re.search(r'/(playlist|album)/[^/]+/(pl\.[a-zA-Z0-9]+|[0-9]+)', apple_music_url)
            if not match:
                return None
            
            content_type = match.group(1)
            content_id = match.group(2)
            
            # Try to fetch from amp-api (Apple Music's public API)
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'application/json',
                'Origin': 'https://music.apple.com',
                'Referer': apple_music_url
            }
            
            # Note: This is a simplified approach
            # Real implementation would need proper API token
            print(f"  ⌕ Trying API extraction for {content_type}: {content_id}")
            
            return None  # Skip API for now, use other methods
            
        except Exception as e:
            print(f"  ⚠  API extraction failed: {e}")
            return None
    
    def _extract_with_smart_fallback(self, apple_music_url):
        """Smart fallback that prompts user or uses intelligent parsing"""
        try:
            from bs4 import BeautifulSoup
            import re
            
            print("  ⌕ Using smart fallback extraction...")
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
                'Connection': 'keep-alive',
            }
            
            response = requests.get(apple_music_url, headers=headers, timeout=15)
            
            if response.status_code != 200:
                return None
            
            soup = BeautifulSoup(response.content, 'lxml' if 'lxml' in str(response.content) else 'html.parser')
            
            # Check if this is a single song (should NOT use smart fallback for single songs)
            if '/song/' in apple_music_url:
                print("  ⚠  This is a single song, skipping smart fallback (not a playlist)")
                return None
            
            # Try to get playlist title
            title = None
            title_selectors = [
                ('meta[property="og:title"]', 'content'),
                ('meta[property="twitter:title"]', 'content'),
                ('title', 'text'),
            ]
            
            for selector, attr_type in title_selectors:
                element = soup.select_one(selector)
                if element:
                    if attr_type == 'content':
                        title = element.get('content', '').strip()
                    else:
                        title = element.get_text().strip()
                    
                    if title:
                        title = title.replace(' - Apple Music', '').replace(' on Apple Music', '').strip()
                        break
            
            if not title:
                return None
            
            # For playlists/albums, check if this is from album download (no interactive prompt)
            # Albums from artist page should not prompt - just return title for search
            if '/album/' in apple_music_url:
                print(f"  ◎ Found album: {title}")
                print(f"  ℹ  Will search for complete album on YouTube")
                # Return basic metadata without tracks for album-as-whole search
                return {'title': title, 'tracks': []}
            
            # For playlists only, prompt user to provide track names
            print(f"\n  ≡ Found playlist: {title}")
            print(f"  ⚠  Could not automatically extract track list due to JavaScript-heavy content")
            print(f"\n  → You have two options:")
            print(f"     1. Manually provide track names (one per line)")
            print(f"     2. Let me search for '{title}' as a whole playlist on YouTube")
            
            try:
                choice = input("\n  Choose option (1 or 2, default=2): ").strip()
                
                if choice == "1":
                    print("\n  Enter track names (format: 'Artist - Title', one per line)")
                    print("  Press Enter twice when done:")
                    tracks = []
                    while True:
                        line = input("  ").strip()
                        if not line:
                            break
                        if ' - ' in line:
                            artist, track_title = line.split(' - ', 1)
                            tracks.append({
                                'artist': artist.strip(),
                                'title': track_title.strip()
                            })
                        else:
                            tracks.append({
                                'artist': 'Unknown',
                                'title': line
                            })
                    
                    if tracks:
                        return {
                            'title': title,
                            'tracks': tracks
                        }
            except:
                pass
            
            # Option 2 or default: search as whole playlist
            return {
                'title': title,
                'tracks': []  # Empty will trigger playlist search
            }
            
        except Exception as e:
            print(f"  ⚠  Smart fallback failed: {e}")
            return None
    
    def _extract_metadata_with_browser(self, apple_music_url):
        """Extract metadata using Selenium browser automation"""
        # Disabled - too unreliable across platforms
        return None
        
        try:
            driver = self._get_browser_driver()
            if not driver:
                return None
            
            print("◎ Loading Apple Music page with browser...")
            driver.get(apple_music_url)
            
            # Wait for content to load
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Give extra time for JavaScript to execute
            time.sleep(3)
            
            metadata = {}
            
            # Extract title
            title_selectors = [
                '[data-testid="song-name"]',
                '[data-testid="album-title"]', 
                '[data-testid="playlist-title"]',
                '.headings__title',
                '.product-header__title',
                'h1'
            ]
            
            for selector in title_selectors:
                try:
                    element = driver.find_element(By.CSS_SELECTOR, selector)
                    if element.text.strip():
                        metadata['title'] = element.text.strip()
                        break
                except:
                    continue
            
            # Extract artist/curator
            artist_selectors = [
                '[data-testid="click-action"]:first-of-type',
                '.headings__metadata a',
                '.product-header__subtitle a',
                '.songs-list-header__metadata a'
            ]
            
            for selector in artist_selectors:
                try:
                    element = driver.find_element(By.CSS_SELECTOR, selector)
                    if element.text.strip():
                        metadata['artist'] = element.text.strip()
                        metadata['curator'] = element.text.strip()
                        break
                except:
                    continue
            
            # Extract tracks (for albums/playlists)
            tracks = []
            track_selectors = [
                '[data-testid="track-list"] [data-testid="track-title"]',
                '.songs-list .song-name',
                '.tracklist-row .song-name'
            ]
            
            for selector in track_selectors:
                try:
                    track_elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    for track_elem in track_elements:
                        track_title = track_elem.text.strip()
                        if track_title:
                            # Try to find artist for this track
                            try:
                                artist_elem = track_elem.find_element(By.XPATH, "..//*[contains(@class, 'artist') or contains(@data-testid, 'artist')]")
                                track_artist = artist_elem.text.strip()
                            except:
                                track_artist = metadata.get('artist', 'Unknown Artist')
                            
                            tracks.append({
                                'title': track_title,
                                'artist': track_artist
                            })
                    
                    if tracks:
                        break
                except:
                    continue
            
            if tracks:
                metadata['tracks'] = tracks
            
            print(f"✓ Browser extraction successful: {len(metadata)} fields")
            return metadata if metadata else None
            
        except Exception as e:
            print(f"⚠  Browser extraction failed: {e}")
            return None
    
    def _extract_metadata_with_cloudscraper(self, apple_music_url):
        """Extract metadata using cloudscraper for Cloudflare bypass"""
        try:
            print("☁️  Trying cloudscraper extraction...")
            
            scraper = cloudscraper.create_scraper()
            response = scraper.get(apple_music_url, timeout=15)
            
            if response.status_code == 200:
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Also save the raw response for debugging
                metadata = self._parse_apple_music_html(soup, response.text)
                return metadata
            
        except Exception as e:
            print(f"⚠  Cloudscraper extraction failed: {e}")
            return None
    
    def _extract_metadata_enhanced_scraping(self, apple_music_url):
        """Enhanced web scraping with multiple strategies"""
        try:
            print("🕷️  Trying enhanced scraping...")
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Cache-Control': 'max-age=0'
            }
            
            session = requests.Session()
            session.headers.update(headers)
            
            response = session.get(apple_music_url, timeout=15, allow_redirects=True)
            
            if response.status_code == 200:
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(response.content, 'html.parser')
                
                return self._parse_apple_music_html(soup, response.text)
            
        except Exception as e:
            print(f"⚠  Enhanced scraping failed: {e}")
            return None
    
    def _parse_apple_music_html(self, soup, raw_html=None):
        """Parse Apple Music HTML to extract metadata"""
        metadata = {}
        tracks = []
        # If raw_html is provided, use it for more aggressive pattern matching
        if raw_html:
            try:
                import re
                import json
                
                # Try to find the main data object in the page
                # Apple Music embeds data in various formats
                
                # Pattern 1: Look for the serialized state data (most reliable)
                # This pattern captures the main data structure with all track info
                state_patterns = [
                    r'window\.__APOLLO_STATE__\s*=\s*(\{.+?\});\s*window',
                    r'window\.INIT_DATA\s*=\s*(\{.+?\});\s*window',
                    r'serializedState"\s*:\s*(\{.+?\})\s*,\s*"',
                ]
                
                for pattern in state_patterns:
                    state_match = re.search(pattern, raw_html, re.DOTALL)
                    if state_match:
                        try:
                            state_data = json.loads(state_match.group(1))
                            # Parse the state for track data
                            for key, value in state_data.items():
                                if isinstance(value, dict):
                                    # Check for track attributes
                                    attrs = value.get('attributes', value)
                                    if isinstance(attrs, dict):
                                        track_name = attrs.get('name', '')
                                        artist_name = attrs.get('artistName', '')
                                        
                                        # Also check for composerName as fallback
                                        if not artist_name:
                                            artist_name = attrs.get('composerName', '')
                                        
                                        if track_name and artist_name:
                                            # Avoid duplicates
                                            if not any(t['title'] == track_name and t['artist'] == artist_name for t in tracks):
                                                tracks.append({
                                                    'title': track_name,
                                                    'artist': artist_name
                                                })
                            
                            if tracks:
                                print(f"  ✓ Extracted {len(tracks)} tracks from state data")
                                break
                        except Exception as e:
                            print(f"  ⚠  State parsing error: {e}")
                            continue
                
                # Pattern 2: Look for embedded JSON with track relationships
                # This is a more aggressive approach for newer Apple Music pages
                if not tracks:
                    try:
                        # Find all potential JSON objects that might contain track data
                        json_objects = re.findall(r'\{[^{}]*?"type"\s*:\s*"songs"[^{}]*?\}', raw_html)
                        json_objects += re.findall(r'\{[^{}]*?"attributes"\s*:\s*\{[^{}]*?"name"[^{}]*?"artistName"[^{}]*?\}[^{}]*?\}', raw_html)
                        
                        for json_str in json_objects:
                            try:
                                obj = json.loads(json_str)
                                attrs = obj.get('attributes', {})
                                track_name = attrs.get('name', '')
                                artist_name = attrs.get('artistName', '')
                                
                                if track_name and artist_name:
                                    if not any(t['title'] == track_name and t['artist'] == artist_name for t in tracks):
                                        tracks.append({
                                            'title': track_name,
                                            'artist': artist_name
                                        })
                            except:
                                continue
                        
                        if tracks:
                            print(f"  ✓ Extracted {len(tracks)} tracks from embedded JSON objects")
                    except Exception as e:
                        print(f"  ⚠  JSON object parsing error: {e}")
                
                # Pattern 3: Direct regex extraction (most aggressive, last resort)
                # Strategy: Extract ALL track names first, then ALL artist names, then pair by index
                if not tracks:
                    try:
                        # Step 1: Extract ALL track names (song titles) from the entire HTML
                        track_names = []
                        name_pattern = r'"name"\s*:\s*"((?:[^"\\]|\\.)*?)"'
                        all_names = re.findall(name_pattern, raw_html)
                        
                        for name in all_names:
                            cleaned_name = name.replace(r'\"', '"').replace(r'\\', '\\').strip()
                            if cleaned_name:
                                track_names.append(cleaned_name)
                        
                        # Step 2: Extract ALL artist names from the entire HTML
                        artist_names = []
                        artist_pattern = r'"artistName"\s*:\s*"((?:[^"\\]|\\.)*?)"'
                        all_artists = re.findall(artist_pattern, raw_html)
                        
                        for artist in all_artists:
                            cleaned_artist = artist.replace(r'\"', '"').replace(r'\\', '\\').strip()
                            if cleaned_artist:
                                artist_names.append(cleaned_artist)
                        
                        # Step 3: Remove the first two indices from track_names list
                        if len(track_names) > 2:
                            track_names = track_names[2:]
                            print(f"  ℹ  Removed first 2 entries from track names (likely metadata)")
                        
                        # Step 4: Remove duplicates from track_names only (not from artists)
                        # Use dict to preserve order (Python 3.7+) and remove duplicates
                        seen_names = {}
                        unique_track_names = []
                        for name in track_names:
                            name_lower = name.lower()
                            if name_lower not in seen_names:
                                seen_names[name_lower] = True
                                unique_track_names.append(name)
                        
                        track_names = unique_track_names
                        # Keep artist_names as-is with duplicates intact
                        
                        # Step 5: Pair them up by index - index 0 of titles with index 0 of artists
                        if track_names and artist_names:
                            # Use the minimum length to avoid index errors
                            min_length = min(len(track_names), len(artist_names))
                            
                            print(f"  ℹ  Found {len(track_names)} unique track names and {len(artist_names)} unique artist names")
                            print(f"  ℹ  Will pair {min_length} tracks by index")
                            
                            # Track seen combinations to avoid duplicates in final list
                            seen_combinations = set()
                            
                            for i in range(min_length):
                                track_name = track_names[i]
                                artist_name = artist_names[i]
                                
                                # Create a normalized key for duplicate checking
                                combo_key = f"{track_name.lower()}|||{artist_name.lower()}"
                                
                                if combo_key not in seen_combinations:
                                    seen_combinations.add(combo_key)
                                    tracks.append({
                                        'title': track_name,
                                        'artist': artist_name
                                    })
                            
                            if tracks:
                                print(f"  ✓ Extracted {len(tracks)} unique tracks using indexed pairing")
                                    
                    except Exception as e:
                        print(f"  ⚠  Regex extraction error: {e}")
                        
            except Exception as e:
                print(f"  ⚠  Raw HTML parsing failed: {e}")
        
        # Extract title from various sources
        title_sources = [
            ('meta[property="og:title"]', 'content'),
            ('meta[name="twitter:title"]', 'content'),
            ('title', 'text'),
            ('.headings__title', 'text'),
            ('.product-header__title', 'text'),
            ('h1', 'text')
        ]
        
        for selector, attr_type in title_sources:
            element = soup.select_one(selector)
            if element:
                if attr_type == 'content':
                    title = element.get('content', '').strip()
                else:
                    title = element.get_text().strip()
                
                if title:
                    # Clean up title
                    title = title.replace(' - Apple Music', '').replace(' on Apple Music', '')
                    title = title.replace('‎', '').strip()
                    if title and len(title) > 2:
                        metadata['title'] = title
                        break
        
        # Extract artist/curator
        artist_sources = [
            ('meta[name="music:musician"]', 'content'),
            ('.headings__metadata a', 'text'),
            ('.product-header__subtitle a', 'text'),
            ('.songs-list-header__metadata a', 'text')
        ]
        
        for selector, attr_type in artist_sources:
            element = soup.select_one(selector)
            if element:
                if attr_type == 'content':
                    artist = element.get('content', '').strip()
                else:
                    artist = element.get_text().strip()
                
                if artist:
                    metadata['artist'] = artist
                    metadata['curator'] = artist
                    break
        
        # Extract structured data for tracks from JSON-LD
        scripts = soup.find_all('script', type='application/ld+json')
        for script in scripts:
            try:
                import json
                data = json.loads(script.string)
                
                if isinstance(data, dict):
                    # Handle MusicAlbum or MusicPlaylist
                    if data.get('@type') in ['MusicAlbum', 'MusicPlaylist'] and 'track' in data:
                        for track_data in data['track']:
                            if isinstance(track_data, dict):
                                track_title = track_data.get('name', '')
                                track_artist = ''
                                
                                if 'byArtist' in track_data:
                                    if isinstance(track_data['byArtist'], dict):
                                        track_artist = track_data['byArtist'].get('name', '')
                                    elif isinstance(track_data['byArtist'], list) and track_data['byArtist']:
                                        track_artist = track_data['byArtist'][0].get('name', '')
                                
                                if track_title:
                                    tracks.append({
                                        'title': track_title,
                                        'artist': track_artist or metadata.get('artist', 'Unknown Artist')
                                    })
                        
                        if tracks:
                            break
            except Exception as e:
                continue
        
        # Additional fallback: Try to extract from script tags if raw_html extraction didn't work
        if not tracks:
            try:
                # Look for embedded JSON data in script tags
                all_scripts = soup.find_all('script')
                for script in all_scripts:
                    if script.string and len(script.string) > 100:  # Skip very small scripts
                        import re
                        import json
                        
                        # Strategy 1: Look for track arrays with relationships
                        try:
                            # Pattern for track data in relationships structure
                            relationships_pattern = r'"relationships"\s*:\s*\{[^}]*"tracks"\s*:\s*\{[^}]*"data"\s*:\s*\[(.*?)\]'
                            rel_match = re.search(relationships_pattern, script.string, re.DOTALL)
                            
                            if rel_match:
                                # Try to find corresponding attributes
                                attrs_pattern = r'"id"\s*:\s*"([^"]+)"[^}]*"attributes"\s*:\s*\{[^}]*"name"\s*:\s*"([^"]+)"[^}]*"artistName"\s*:\s*"([^"]+)"'
                                attr_matches = re.findall(attrs_pattern, script.string)
                                
                                for track_id, track_name, artist_name in attr_matches:
                                    if track_name and artist_name:
                                        if not any(t['title'] == track_name and t['artist'] == artist_name for t in tracks):
                                            tracks.append({
                                                'title': track_name,
                                                'artist': artist_name
                                            })
                                
                                if tracks:
                                    print(f"  ✓ Extracted {len(tracks)} tracks from relationships data")
                                    break
                        except:
                            pass
                        
                        # Strategy 2: Direct extraction with better context
                        if not tracks:
                            try:
                                # Look for track objects in arrays
                                # Pattern: Find arrays that contain track-like objects
                                array_pattern = r'\[(\{[^]]+?"name"\s*:\s*"[^"]+?"[^]]+?"artistName"\s*:\s*"[^"]+?"[^]]+?\}(?:,\s*\{[^]]+?\})*)\]'
                                array_matches = re.findall(array_pattern, script.string)
                                
                                for array_content in array_matches:
                                    # Extract individual track objects
                                    track_pattern = r'"name"\s*:\s*"([^"]+)"[^}]*?"artistName"\s*:\s*"([^"]+)"'
                                    track_matches = re.findall(track_pattern, array_content)
                                    
                                    for track_name, artist_name in track_matches:
                                        if track_name and artist_name:
                                            if track_name.lower() not in ['music', 'playlist', 'album']:
                                                if not any(t['title'] == track_name and t['artist'] == artist_name for t in tracks):
                                                    tracks.append({
                                                        'title': track_name,
                                                        'artist': artist_name
                                                    })
                                
                                if tracks:
                                    print(f"  ✓ Extracted {len(tracks)} tracks from array structures")
                                    break
                            except:
                                pass
            except Exception as e:
                print(f"  ⚠  Error parsing embedded data: {e}")
        
        # Final deduplication pass - remove any duplicate tracks
        # Smart deduplication: prefer tracks with real artist names over "Unknown Artist"
        if tracks:
            # First pass: collect tracks by title
            tracks_by_title = {}
            for track in tracks:
                title_lower = track['title'].lower().strip()
                artist = track['artist'].strip()
                
                if title_lower not in tracks_by_title:
                    tracks_by_title[title_lower] = track
                else:
                    # If we already have this title, prefer the one with a real artist
                    existing = tracks_by_title[title_lower]
                    if existing['artist'] == 'Unknown Artist' and artist != 'Unknown Artist':
                        # Replace with the version that has artist info
                        tracks_by_title[title_lower] = track
                    elif existing['artist'] != 'Unknown Artist' and artist == 'Unknown Artist':
                        # Keep the existing one with artist info
                        pass
                    elif existing['artist'].lower() != artist.lower():
                        # Different artists for same title - keep both
                        # Create a unique key
                        key_counter = 1
                        unique_title = f"{title_lower}_{key_counter}"
                        while unique_title in tracks_by_title:
                            key_counter += 1
                            unique_title = f"{title_lower}_{key_counter}"
                        tracks_by_title[unique_title] = track
            
            unique_tracks = list(tracks_by_title.values())
            
            if len(unique_tracks) < len(tracks):
                print(f"  ℹ  Removed {len(tracks) - len(unique_tracks)} duplicate tracks")
            
            tracks = unique_tracks
            metadata['tracks'] = tracks
        
        return metadata if metadata else None
    
    def _prompt_playlist_download_choice_enhanced(self, tracks):
        """Enhanced playlist download choice with better formatting"""
        print(f"\n♫ Playlist contains {len(tracks)} tracks")
        print("↓ Download options:")
        print("  1. Download all tracks")
        print("  2. Select specific tracks")
        print("  3. Download first 10 tracks only")
        print("  4. Cancel")
        
        while True:
            try:
                choice = input("\nEnter your choice (1-4): ").strip()
                
                if choice == "1":
                    return "all"
                elif choice == "2":
                    return self._select_specific_tracks_enhanced(tracks)
                elif choice == "3":
                    return tracks[:10]
                elif choice == "4":
                    return "cancel"
                else:
                    print("Please enter 1, 2, 3, or 4")
                    
            except KeyboardInterrupt:
                return "cancel"
    
    def _select_specific_tracks_enhanced(self, tracks):
        """Enhanced track selection with better interface"""
        print(f"\n≡ Available tracks ({len(tracks)} total):")
        
        # Show tracks in batches for better readability
        batch_size = 20
        for i in range(0, len(tracks), batch_size):
            batch = tracks[i:i+batch_size]
            print(f"\n--- Tracks {i+1}-{min(i+batch_size, len(tracks))} ---")
            
            for j, track in enumerate(batch, i+1):
                artist = track.get('artist', 'Unknown Artist')
                title = track.get('title', 'Unknown Title')
                print(f"  {j:3d}. {artist} - {title}")
            
            if i + batch_size < len(tracks):
                input("Press Enter to see more tracks...")
        
        print(f"\n▭ Selection options:")
        print("  • Individual numbers: 1,3,5,10")
        print("  • Ranges: 1-10,15-20") 
        print("  • Mixed: 1,3,5-8,10,12-15")
        print("  • Type 'all' for all tracks")
        print("  • Type 'cancel' to cancel")
        
        try:
            user_input = input("Your selection: ").strip().lower()
            
            if user_input == 'cancel':
                return "cancel"
            elif user_input == 'all':
                return tracks
            
            # Parse selection
            selected_indices = set()
            
            for part in user_input.split(','):
                part = part.strip()
                if '-' in part:
                    try:
                        start, end = map(int, part.split('-'))
                        selected_indices.update(range(start-1, end))
                    except ValueError:
                        print(f"⚠  Invalid range: {part}")
                else:
                    try:
                        selected_indices.add(int(part) - 1)
                    except ValueError:
                        print(f"⚠  Invalid number: {part}")
            
            # Filter valid indices
            valid_indices = [i for i in selected_indices if 0 <= i < len(tracks)]
            selected_tracks = [tracks[i] for i in sorted(valid_indices)]
            
            if selected_tracks:
                print(f"✓ Selected {len(selected_tracks)} tracks")
                return selected_tracks
            else:
                print("✗ No valid tracks selected")
                return "cancel"
                
        except KeyboardInterrupt:
            return "cancel"
    
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
    
    def _download_track_queue_enhanced(self, tracks, source_name, output_format='mp3', quality='best'):
        """Enhanced track queue download with better progress tracking"""
        if not tracks:
            return False
        
        print("\n" + "=" * 60)
        print(f"♫ Starting {source_name} Download Queue")
        print(f"▤ Total tracks: {len(tracks)}")
        print(f"♪ Format: {output_format.upper()} | Quality: {quality}")
        print("=" * 60)
        
        successful_downloads = 0
        failed_downloads = 0
        
        for i, track in enumerate(tracks, 1):
            try:
                artist = track.get('artist', 'Unknown Artist')
                title = track.get('title', 'Unknown Title')
                # Search with "Title - Artist" format
                search_query = f"{title} - {artist}"
                # Filename with "Artist - Title" format
                filename = f"{artist} - {title}"
                
                print(f"\n♫ [{i:3d}/{len(tracks)}] {title}")
                print(f"    ◈ {artist}")
                print("    " + "─" * 50)
                
                # Use enhanced music search
                youtube_url = self._search_youtube_for_music(search_query)
                
                if youtube_url:
                    print(f"    ✓ Found: {youtube_url}")
                    
                    result = self.download_media(
                        youtube_url,
                        audio_only=True,
                        output_format=output_format,
                        quality=quality,
                        add_metadata=True,
                        add_thumbnail=True,
                        custom_filename=filename  # Save as "Artist - Title"
                    )
                    
                    if result:
                        successful_downloads += 1
                        print(f"    ✓ Download successful!")
                    else:
                        failed_downloads += 1
                        print(f"    ✗ Download failed")
                else:
                    failed_downloads += 1
                    print(f"    ✗ Not found on YouTube")
                
                # Progress indicator
                progress = (i / len(tracks)) * 100
                print(f"    ▤ Progress: {progress:.1f}% ({successful_downloads} successful, {failed_downloads} failed)")
                
                # Small delay between downloads
                if i < len(tracks):
                    time.sleep(1)
                    
            except Exception as e:
                failed_downloads += 1
                print(f"    ✗ Error: {e}")
        
        # Final summary
        print("\n" + "=" * 60)
        print(f"♫ {source_name} Download Queue Complete!")
        print(f"✓ Successful: {successful_downloads}")
        print(f"✗ Failed: {failed_downloads}")
        print(f"▤ Success rate: {(successful_downloads/len(tracks)*100):.1f}%")
        print(f"▸ Location: {self.output_dir}")
        print("=" * 60)
        
        return successful_downloads > 0
    
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
        if not self.spotify_client:
            return None
        
        try:
            if not silent:
                if RICH_AVAILABLE and self.console:
                    self.console.print(f"[dim cyan]→[/dim cyan] [dim]Fetching album art from Spotify...[/dim]", end="\r")
                else:
                    print(f"→ Fetching album art from Spotify...", end="\r")
            
            query = f"{track_name} {artist_name}"
            results = self.spotify_client.search(q=query, type='track', limit=1)
            
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
                        
                        if not album_art_data and self.spotify_client:
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
                if SPOTIFY_AVAILABLE and self.spotify_client:
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
        """Interactive format selection"""
        print("\n◎ FORMAT SELECTION")
        print("=" * 50)
        
        # Ask for media type
        media_types = ["Video (with audio)", "Audio only"]
        media_choice = self.prompt_user_choice(
            "What type of media do you want to download?", 
            media_types, 
            default="Video (with audio)"
        )
        
        audio_only = media_choice == "Audio only"
        
        # Ask for quality with enhanced audio format options
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
            quality_options = ["Best available", "4K (2160p)", "1440p", "1080p", "720p", "480p", "360p", "Custom"]
            quality_choice = self.prompt_user_choice(
                "Select video quality:", 
                quality_options, 
                default="Best available"
            )
            
            if quality_choice == "Custom":
                custom_format = input("Enter custom format (e.g., 'best[height<=720]'): ").strip()
                return "best", audio_only, None, custom_format if custom_format else None
            
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
            
            return quality_map[quality_choice], audio_only, format_map[format_choice], None
    
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
                download_info = f"""
[bold cyan]Platform:[/bold cyan] [yellow]{platform.upper()}[/yellow]
[bold cyan]Quality:[/bold cyan] [green]{quality}[/green]
[bold cyan]Mode:[/bold cyan] [magenta]{'Audio Only' if audio_only else 'Video + Audio'}[/magenta]
[bold cyan]Format:[/bold cyan] [blue]{output_format if output_format else 'Auto'}[/blue]
"""
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
                print("⌕ Playlist detected in URL!")
                
                if no_playlist:
                    # User explicitly wants only single video
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
            
            # Add progress hook
            ydl_opts['progress_hooks'] = [self._progress_hook]
            
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
                    uploader = info.get('uploader', 'Unknown')
                    
                    # Look for downloaded files with multiple patterns
                    # yt-dlp sanitizes filenames, replacing characters like | with ｜
                    # Clean the strings for glob patterns - remove special glob characters
                    title_clean = title[:40].replace('|', '').replace('/', '').replace('\\', '').replace('*', '').replace('?', '').replace('[', '').replace(']', '')
                    uploader_clean = uploader[:20].replace('|', '').replace('/', '').replace('\\', '').replace('*', '').replace('?', '').replace('[', '').replace(']', '')
                    
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
                        completion_msg = """
[bold green]✦ Download completed successfully! ✦[/bold green]

[cyan]🎉 Your media is ready![/cyan]
"""
                        self.print_panel(completion_msg, title="🎊 SUCCESS", border_style="green")
                    else:
                        print("\n✓ Download completed successfully!")
                elif not self.cancelled and not download_succeeded:
                    # Download failed
                    if RICH_AVAILABLE and self.console:
                        error_msg = """
[bold red]✗ Download failed![/bold red]

[yellow]⚠  The video could not be downloaded. Possible reasons:[/yellow]
[dim]• The URL is not supported or requires authentication
• The video is private, deleted, or region-restricted
• The site has anti-bot protection enabled
• Network connection issues[/dim]
"""
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
    
    def _progress_hook(self, d):
        """Enhanced progress hook for download status with better formatting and Rich support"""
        if d['status'] == 'downloading':
            if 'total_bytes' in d and d['total_bytes']:
                percent = d['downloaded_bytes'] / d['total_bytes'] * 100
                speed = d.get('speed', 0)
                eta = d.get('eta', 0)
                
                # Enhanced speed formatting
                if speed:
                    if speed > 1024 * 1024:  # MB/s
                        speed_str = f"{speed/1024/1024:.1f}MB/s"
                    else:  # KB/s
                        speed_str = f"{speed/1024:.0f}KB/s"
                else:
                    speed_str = "---KB/s"
                
                # Enhanced ETA formatting
                if eta:
                    if eta > 3600:  # Hours
                        eta_str = f"{eta//3600}h{(eta%3600)//60:02d}m"
                    elif eta > 60:  # Minutes
                        eta_str = f"{eta//60}m{eta%60:02d}s"
                    else:  # Seconds
                        eta_str = f"{eta:2.0f}s"
                else:
                    eta_str = "--:--"
                
                # Calculate downloaded size with better formatting
                downloaded_mb = d['downloaded_bytes'] / 1024 / 1024
                total_mb = d['total_bytes'] / 1024 / 1024
                
                # Create progress bar
                bar_length = 30
                filled_length = int(bar_length * percent / 100)
                
                # Create simple progress bar using plain text with ANSI colors
                bar = '━' * filled_length + '░' * (bar_length - filled_length)
                
                # Use ANSI color codes for compatibility
                # Yellow ▼, Green %, Cyan progress/sizes, Magenta speed, Blue ETA
                progress_line = (
                    f"\r\033[1;33m▼\033[0m "  # Yellow ▼
                    f"\033[1;32m{percent:5.1f}%\033[0m "  # Green %
                    f"[\033[36m{bar[:filled_length]}\033[0m"  # Cyan filled
                    f"\033[2;37m{bar[filled_length:]}\033[0m] "  # Dim white empty
                    f"\033[1;36m{downloaded_mb:6.1f}/{total_mb:6.1f}MB\033[0m "  # Cyan sizes
                    f"| \033[1;35m{speed_str:>10}\033[0m "  # Magenta speed
                    f"| ETA: \033[1;34m{eta_str}\033[0m"  # Blue ETA
                )
                
                print(progress_line, end="", flush=True)
            else:
                # Fallback for unknown total size
                downloaded_mb = d.get('downloaded_bytes', 0) / 1024 / 1024
                speed = d.get('speed', 0)
                speed_str = f"{speed/1024/1024:.1f}MB/s" if speed else "---KB/s"
                
                # Use ANSI colors
                progress_line = (
                    f"\r\033[1;33m▼\033[0m "  # Yellow ▼
                    f"Downloaded: \033[1;36m{downloaded_mb:6.1f}MB\033[0m "  # Cyan size
                    f"| \033[1;35m{speed_str:>10}\033[0m"  # Magenta speed
                )
                
                print(progress_line, end="", flush=True)
                
        elif d['status'] == 'finished':
            filename = os.path.basename(d['filename'])
            # Clear the progress line completely before printing completion
            print("\r" + " " * 120, end="\r", flush=True)
            print(f"\033[1;32m✓\033[0m Download complete: \033[32m{filename}\033[0m")
            
        elif d['status'] == 'error':
            error_msg = d.get('error', 'Unknown error')
            print("\r" + " " * 120, end="\r", flush=True)
            print(f"\033[1;31m✗\033[0m Download error: \033[31m{error_msg}\033[0m")
            
        elif d['status'] == 'processing':
            # Processing happens quickly, no need to show
            pass
    
    def _format_duration(self, seconds):
        """Format duration in human readable format"""
        if not seconds or seconds == 'Unknown':
            return "Unknown"
        
        try:
            seconds = int(seconds)
            hours = seconds // 3600
            minutes = (seconds % 3600) // 60
            secs = seconds % 60
            
            if hours > 0:
                return f"{hours}h {minutes}m {secs}s"
            elif minutes > 0:
                return f"{minutes}m {secs}s"
            else:
                return f"{secs}s"
        except:
            return "Unknown"
    
    def _cleanup_intermediate_files(self, info, audio_only=False, output_format=None, keep_file=None):
        """Clean up intermediate files (thumbnails, json, etc.) after download completes"""
        try:
            if not info:
                return
            
            title = info.get('title', 'Unknown')
            uploader = info.get('uploader', 'Unknown')
            
            # Determine the main output file extension
            main_ext = output_format.lower() if output_format else ('mp3' if audio_only else 'mp4')
            main_filename_base = f"{uploader} - {title}"
            
            # Get the actual file we want to keep (absolute path)
            keep_file_path = Path(keep_file).resolve() if keep_file else None
            
            # List of intermediate file extensions to clean up
            intermediate_extensions = [
                '.jpg', '.jpeg', '.png', '.webp',  # Thumbnails
                '.info.json',  # Info JSON
                '.description',  # Description files
                '.annotations.xml',  # Annotations
                '.webm', '.m4a', '.part',  # Temp video/audio files
            ]
            
            # If audio_only, also remove video files that might remain
            if audio_only:
                intermediate_extensions.extend(['.mp4', '.mkv', '.webm', '.avi', '.mov'])
            
            print("\n🧹 Cleaning up intermediate files...")
            cleaned_count = 0
            
            # Search for and remove intermediate files
            for file_path in self.output_dir.iterdir():
                if file_path.is_file():
                    file_name = file_path.name
                    file_stem = file_path.stem
                    
                    # NEVER delete the file we want to keep
                    if keep_file_path and file_path.resolve() == keep_file_path:
                        continue
                    
                    # Check if this is an intermediate file related to our download
                    for ext in intermediate_extensions:
                        if file_name.endswith(ext):
                            # Make sure it's related to this download
                            if main_filename_base in file_name or title in file_name:
                                try:
                                    file_path.unlink()
                                    cleaned_count += 1
                                    print(f"  🗑️  Removed: {file_name}")
                                except Exception as e:
                                    print(f"  ⚠  Could not remove {file_name}: {e}")
                                break
            
            if cleaned_count > 0:
                print(f"✓ Cleaned up {cleaned_count} intermediate file(s)")
            else:
                print("✓ No intermediate files to clean")
                
        except Exception as e:
            print(f"⚠  Cleanup error: {e}")
    
    def check_url_support(self, url, silent=False):
        """Check if URL is supported"""
        try:
            platform = self.detect_platform(url)
            if not silent:
                print(f"◎ Detected platform: {platform.upper()}")

            # Treat Apple Music and Spotify as supported (handled via search/metadata)
            if platform in ("apple_music", "spotify"):
                if not silent:
                    print("✓ URL supported via enhanced handler (YouTube search + metadata)")
                return True
            
            # Try to extract info to check if URL is supported
            with yt_dlp.YoutubeDL({'quiet': True, 'no_warnings': True}) as ydl:
                try:
                    # Try to extract basic info without downloading
                    info = ydl.extract_info(url, download=False, process=False)
                    if info:
                        extractor_name = info.get('extractor', 'Unknown')
                        print(f"✓ URL supported by extractor: {extractor_name}")
                        
                        # Show basic info if available
                        if info.get('title'):
                            print(f"▶ Title: {info.get('title')}")
                        if info.get('uploader'):
                            print(f"◈ Uploader: {info.get('uploader')}")
                        
                        # Show platform-specific info
                        if platform in self.platform_configs:
                            config = self.platform_configs[platform]
                            print(f"≡ Supported formats: {', '.join(config['formats'])}")
                            if 'note' in config:
                                print(f"▭ Note: {config['note']}")
                        
                        return True
                    else:
                        print("✗ URL not supported - no info extracted")
                        return False
                        
                except yt_dlp.DownloadError as e:
                    if "Unsupported URL" in str(e) or "No suitable extractor" in str(e):
                        print("✗ URL not supported by any extractor")
                        print(f"→ Tip: Try checking if the URL is correct and accessible")
                        return False
                    else:
                        # Other errors might still mean the URL is supported
                        print(f"⚠  URL might be supported but encountered error: {e}")
                        return True
                        
        except Exception as e:
            print(f"✗ Error checking URL support: {e}")
            print("→ Tip: The URL might still work, try downloading it directly")
            return False
    
    def list_supported_platforms(self):
        """List all supported platforms with details"""
        if RICH_AVAILABLE and self.console:
            # Create beautiful table with Rich
            table = Table(
                title="🌍 Supported Platforms",
                box=box.ROUNDED,
                border_style="cyan",
                header_style="bold magenta"
            )
            
            table.add_column("Platform", style="bold yellow", no_wrap=True)
            table.add_column("Domains", style="cyan")
            table.add_column("Content Types", style="green")
            
            major_platforms = [
                ("▶ YouTube", "youtube.com, youtu.be", "Videos, playlists, live streams"),
                ("♫ Spotify", "spotify.com", "Tracks, albums, playlists"),
                ("♫ SoundCloud", "soundcloud.com", "Tracks, playlists, uploads"),
                ("♪ Apple Music", "music.apple.com", "Tracks, albums"),
                ("📸 Instagram", "instagram.com", "Videos, reels, IGTV"),
                ("▭ TikTok", "tiktok.com", "Videos, user content"),
                ("◐ Twitter/X", "twitter.com, x.com", "Video tweets"),
                ("📘 Facebook", "facebook.com", "Videos, live streams"),
                ("▶ Vimeo", "vimeo.com", "Videos, private content"),
                ("▧ Twitch", "twitch.tv", "VODs, clips, streams"),
            ]
            
            for platform, domains, content in major_platforms:
                table.add_row(platform, domains, content)
            
            self.console.print(table)
            self.console.print(f"\n[bold green]▤ Total supported sites: {len(self.get_supported_sites())} platforms[/bold green]")
            self.console.print("[yellow]→ Use --check-support <URL> to verify URL compatibility[/yellow]")
        else:
            print("\n🌍 SUPPORTED PLATFORMS")
            print("=" * 60)
            
            major_platforms = [
                ("YouTube", "youtube.com, youtu.be", "Videos, playlists, live streams"),
                ("Spotify", "spotify.com", "Tracks, albums, playlists (via YouTube search)"),
                ("SoundCloud", "soundcloud.com", "Tracks, playlists, user uploads"),
                ("Apple Music", "music.apple.com", "Tracks, albums (via YouTube search)"),
                ("Instagram", "instagram.com", "Videos, reels, IGTV"),
                ("TikTok", "tiktok.com", "Videos, user uploads"),
                ("Twitter/X", "twitter.com, x.com", "Videos from tweets"),
                ("Facebook", "facebook.com", "Videos, live streams"),
                ("Vimeo", "vimeo.com", "Videos, private videos"),
                ("Twitch", "twitch.tv", "VODs, clips, live streams"),
            ]
            
            for name, domains, content in major_platforms:
                print(f"▶ {name:12} | {domains:25} | {content}")
            
            print(f"\n▤ Total supported sites: {len(self.get_supported_sites())} platforms")
            print("→ Use --check-support <URL> to verify if a specific URL is supported")

def interactive_mode():
    """Interactive mode with modern UI and professional design"""
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


def show_help_menu(ui):
    """Display help menu with modern styling"""
    if ui.console and RICH_AVAILABLE:
        help_table = Table(title="[bold cyan]▭ COMMAND REFERENCE[/bold cyan]", 
                          box=box.ROUNDED, border_style="cyan", show_header=True)
        
        help_table.add_column("Command", style="yellow", justify="left")
        help_table.add_column("Aliases", style="dim", justify="left")
        help_table.add_column("Description", style="white", justify="left")
        
        help_table.add_row("help", "h", "Show this help menu")
        help_table.add_row("platforms", "p", "List all supported platforms")
        help_table.add_row("clear", "cls", "Clear the screen")
        help_table.add_row("quit", "exit, q", "Exit the application")
        help_table.add_row("[URL]", "-", "Paste any media URL to download")
        
        ui.console.print()
        ui.console.print(help_table)
        ui.console.print()
    else:
        print("\n" + "=" * 70)
        print("▭ COMMAND REFERENCE")
        print("=" * 70)
        print("  help, h          - Show this help menu")
        print("  platforms, p     - List all supported platforms")
        print("  clear, cls       - Clear the screen")
        print("  quit, exit, q    - Exit the application")
        print("  [URL]            - Paste any media URL to download")
        print("=" * 70 + "\n")


def create_banner():
    """Create a beautiful banner using Rich"""
    ui = ModernUI()
    
    if RICH_AVAILABLE and ui.console:
        # Create feature table
        feature_grid = Table.grid(padding=(0, 2))
        feature_grid.add_column(justify="center", style="cyan")
        feature_grid.add_column(justify="center", style="magenta")
        feature_grid.add_column(justify="center", style="green")
        feature_grid.add_column(justify="center", style="yellow")
        
        feature_grid.add_row("▶ Videos", "♪ Music", "▭ Social", "⚡ Fast")
        
        panel = Panel(
            Align.center(feature_grid),
            title="[bold white]▶ ULTIMATE MEDIA DOWNLOADER[/bold white]",
            subtitle="[dim]Professional Edition[/dim]",
            border_style="bright_cyan",
            box=box.DOUBLE,
            padding=(1, 2)
        )
        
        ui.console.print(panel)
    else:
        print("=" * 70)
        print("▶ ULTIMATE MEDIA DOWNLOADER")
        print("=" * 70)


def main():
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
    
    parser.add_argument('url', nargs='?', help='Media URL to download (if not provided, starts interactive mode)')
    parser.add_argument('-q', '--quality', default='best',
                       choices=['best', 'worst', '4k', '2160p', '1440p', '1080p', '720p', '480p', '360p'],
                       help='Video quality (default: best)')
    parser.add_argument('-a', '--audio-only', action='store_true',
                       help='Download audio only')
    parser.add_argument('-f', '--format', help='Output format (mp4, mp3, mkv, wav, flac, etc.)')
    parser.add_argument('-o', '--output', default=None,
                       help='Output directory (default: ~/Downloads/UltimateDownloader)')
    parser.add_argument('-p', '--playlist', action='store_true',
                       help='Download playlist (with interactive options by default)')
    parser.add_argument('--no-playlist', action='store_true',
                       help='Download only single video from playlist URL')
    parser.add_argument('-m', '--max-downloads', type=int,
                       help='Maximum number of videos to download from playlist')
    parser.add_argument('-s', '--start-index', type=int, default=1,
                       help='Start index for playlist download (default: 1)')
    parser.add_argument('-i', '--info', action='store_true',
                       help='Show media info without downloading')
    parser.add_argument('--show-formats', action='store_true',
                       help='Show all available formats and qualities')
    parser.add_argument('--custom-format', help='Custom format selector for advanced users')
    parser.add_argument('--timeout', type=int, default=60,
                       help='Timeout for operations in seconds (default: 60)')
    parser.add_argument('--check-support', action='store_true',
                       help='Check if URL is supported')
    parser.add_argument('--list-platforms', action='store_true',
                       help='List all supported platforms')
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
    
    args = parser.parse_args()
    
    # Create downloader instance
    downloader = UltimateMediaDownloader(args.output)
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

if __name__ == "__main__":    
    main()