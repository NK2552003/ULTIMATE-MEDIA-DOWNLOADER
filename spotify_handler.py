#!/usr/bin/env python3
"""
Spotify Handler Module
Handles all Spotify-related functionality including downloading tracks, albums, 
playlists, and artists with metadata extraction and YouTube search fallback.
"""

import os
import re
import sys
import json
import requests
import warnings
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

# Suppress warnings
warnings.filterwarnings('ignore')

try:
    import spotipy
    from spotipy.oauth2 import SpotifyClientCredentials
    SPOTIPY_AVAILABLE = True
except ImportError:
    SPOTIPY_AVAILABLE = False

try:
    from bs4 import BeautifulSoup
    BEAUTIFULSOUP_AVAILABLE = True
except ImportError:
    BEAUTIFULSOUP_AVAILABLE = False

try:
    from mutagen.flac import FLAC, Picture
    from mutagen.mp3 import MP3
    from mutagen.id3 import ID3, APIC, TIT2, TPE1, TALB, TDRC
    from mutagen.mp4 import MP4, MP4Cover
    MUTAGEN_AVAILABLE = True
except ImportError:
    MUTAGEN_AVAILABLE = False

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.align import Align
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

from utils import sanitize_filename
from ui_components import Icons, Messages


class SpotifyHandler:
    """Handles Spotify downloads and metadata extraction"""
    
    def __init__(self, downloader):
        """Initialize Spotify handler with reference to main downloader
        
        Args:
            downloader: Reference to UltimateMediaDownloader instance
        """
        self.downloader = downloader
        self.console = Console() if RICH_AVAILABLE else None
        self.spotify_client = None
        
        # Initialize Spotify client if API credentials available
        if SPOTIPY_AVAILABLE:
            self._init_spotify()
    
    def _init_spotify(self):
        """Initialize Spotify client (requires API credentials)"""
        try:
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
        except Exception as e:
            self.spotify_client = None
    
    def search_and_download(self, spotify_url, interactive=True):
        """Enhanced Spotify downloader with multiple strategies
        
        Args:
            spotify_url: URL to Spotify content
            interactive: Whether to prompt user for options
            
        Returns:
            True if successful, False/None otherwise
        """
        print(f"♪ Processing Spotify URL: {spotify_url}")
        
        try:
            # Determine Spotify content type
            if '/track/' in spotify_url:
                return self._download_track(spotify_url, interactive=interactive)
            elif '/album/' in spotify_url:
                return self._download_album(spotify_url, interactive=interactive)
            elif '/playlist/' in spotify_url:
                return self._download_playlist(spotify_url, interactive=interactive)
            elif '/artist/' in spotify_url:
                return self._download_artist(spotify_url)
            else:
                self._print(Messages.error("Unknown Spotify URL format"))
                return None
                
        except Exception as e:
            self._print(Messages.error(f"Error processing Spotify URL: {e}"))
            return self._fallback_search(spotify_url)
    
    def _download_track(self, spotify_url, interactive=True):
        """Download single Spotify track"""
        if self.spotify_client:
            return self._download_track_api(spotify_url, interactive)
        else:
            return self._scrape_spotify_track(spotify_url)
    
    def _download_track_api(self, spotify_url, interactive=True):
        """Download single Spotify track using API"""
        try:
            track_id = self._extract_spotify_id(spotify_url, 'track')
            if not track_id:
                return None
            
            track = self.spotify_client.track(track_id)
            artists = ', '.join([artist['name'] for artist in track['artists']])
            track_name = track['name']
            search_query = f"{track_name} - {artists}"
            
            self._print(f"[bold green]{Icons.get('spotify')} Spotify Track:[/bold green] [cyan]{search_query}[/cyan]")
            
            # Ask for quality preference
            if interactive:
                output_format, quality = self.downloader._prompt_audio_format_quality()
            else:
                output_format = 'mp3'
                quality = 'best'
            
            self._print(Messages.searching("Searching on YouTube..."))
            
            youtube_url = self.downloader._search_youtube(search_query)
            if youtube_url:
                self._print(Messages.success(f"Found on YouTube: {youtube_url}"))
                filename_format = f"{artists} - {track_name}"
                
                return self.downloader.download_media(
                    youtube_url, 
                    audio_only=True, 
                    output_format=output_format,
                    quality=quality,
                    add_metadata=True,
                    add_thumbnail=True,
                    custom_filename=filename_format
                )
            else:
                self._print(Messages.error("Could not find track on YouTube"))
                return None
                
        except Exception as e:
            self._print(Messages.error(f"Error downloading Spotify track: {e}"))
            return None
    
    def _download_album(self, spotify_url, interactive=True):
        """Download Spotify album by searching each track on YouTube"""
        if self.spotify_client:
            return self._download_album_api(spotify_url, interactive)
        else:
            return self._scrape_spotify_album(spotify_url)
    
    def _download_album_api(self, spotify_url, interactive=True):
        """Download Spotify album using API"""
        try:
            album_id = self._extract_spotify_id(spotify_url, 'album')
            if not album_id:
                return None
            
            album = self.spotify_client.album(album_id)
            album_name = album['name']
            artist_name = album['artists'][0]['name']
            tracks = album['tracks']['items']
            
            self._print(f"[bold magenta]{Icons.get('spotify')} Spotify Album:[/bold magenta] [cyan]{artist_name} - {album_name}[/cyan]")
            self._print(Messages.info(f"Total tracks: {len(tracks)}"))
            
            # Prompt for audio format and quality
            if interactive:
                output_format, quality = self.downloader._prompt_audio_format_quality()
            else:
                output_format = 'mp3'
                quality = 'best'
            
            # Create album directory
            album_dir = self.downloader.output_dir / f"{artist_name} - {album_name}"
            album_downloader = self.downloader.__class__(album_dir)
            
            successful_downloads = 0
            
            for i, track in enumerate(tracks, 1):
                try:
                    artists = ', '.join([artist['name'] for artist in track['artists']])
                    track_name = track['name']
                    search_query = f"{track_name} - {artists}"
                    
                    self._print(f"\n[bold blue]{Icons.get('music')} [{i:2d}/{len(tracks)}][/bold blue] [cyan]{search_query}[/cyan]")
                    
                    youtube_url = self.downloader._search_youtube(search_query)
                    if youtube_url:
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
                        self._print(Messages.error(f"Could not find: {track_name}"))
                        
                except Exception as e:
                    self._print(Messages.error(f"Error downloading {track_name}: {e}"))
            
            print(f"\n✓ Album download completed: {successful_downloads}/{len(tracks)} tracks downloaded")
            return successful_downloads > 0
            
        except Exception as e:
            self._print(Messages.error(f"Error downloading Spotify album: {e}"))
            return None
    
    def _download_playlist(self, spotify_url, interactive=True):
        """Download Spotify playlist by searching each track on YouTube"""
        if self.spotify_client:
            return self._download_playlist_api(spotify_url, interactive)
        else:
            return self._scrape_spotify_playlist(spotify_url)
    
    def _download_playlist_api(self, spotify_url, interactive=True):
        """Download Spotify playlist using API"""
        try:
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
            
            # Convert to track list format
            track_list = []
            for item in valid_tracks:
                track = item['track']
                artists = ', '.join([artist['name'] for artist in track['artists']])
                track_name = track['name']
                track_list.append(f"{track_name} - {artists}")
            
            print(f"✓ Found {len(track_list)} tracks in playlist:")
            for i, track in enumerate(track_list[:10], 1):
                print(f"  {i}. {track}")
            
            if len(track_list) > 10:
                print(f"  ... and {len(track_list) - 10} more tracks")
            
            # Ask user what they want to download
            if interactive:
                choice = self.downloader._prompt_playlist_download_choice(track_list)
                
                if choice == "cancel":
                    print("✗ Download cancelled by user")
                    return None
                elif choice == "all":
                    selected_tracks = track_list
                else:
                    selected_tracks = choice
                
                # Prompt for audio format and quality
                output_format, quality = self.downloader._prompt_audio_format_quality()
            else:
                selected_tracks = track_list
                output_format = 'mp3'
                quality = 'best'
            
            print(f"\n♫ Starting download of {len(selected_tracks)} track(s)...")
            
            # Create playlist directory
            safe_playlist_name = "".join(c for c in playlist_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
            playlist_dir = self.downloader.output_dir / f"Spotify - {safe_playlist_name}"
            playlist_downloader = self.downloader.__class__(playlist_dir)
            
            return playlist_downloader._download_track_queue(selected_tracks, "Spotify", output_format, quality)
            
        except Exception as e:
            self._print(Messages.error(f"Error downloading Spotify playlist: {e}"))
            return None
    
    def _download_artist(self, spotify_url):
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
                pass
            
            self._print(f"[bold cyan]🎤 Spotify Artist Link Detected[/bold cyan]")
            self._print("")
            
            # Provide helpful guidance
            if RICH_AVAILABLE and self.console:
                self.console.print(Panel.fit(
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
            else:
                print("Artist pages cannot be downloaded directly.")
                print(f"Please provide one of these instead:")
                print(f"  • Track URL - https://open.spotify.com/track/...")
                print(f"  • Album URL - https://open.spotify.com/album/...")
                print(f"  • Playlist URL - https://open.spotify.com/playlist/...")
            
            return None
            
        except Exception as e:
            self._print(Messages.warning("Spotify artist pages cannot be downloaded directly"))
            return None
    
    def _fallback_search(self, spotify_url):
        """Fallback method to extract Spotify track info without API using web scraping"""
        try:
            self._print(Messages.searching("Attempting fallback Spotify track extraction..."))
            
            # Determine content type
            if '/track/' in spotify_url:
                return self._scrape_spotify_track(spotify_url)
            elif '/album/' in spotify_url:
                return self._scrape_spotify_album(spotify_url)
            elif '/playlist/' in spotify_url:
                return self._scrape_spotify_playlist(spotify_url)
            elif '/artist/' in spotify_url:
                return self._download_artist(spotify_url)
            else:
                self._print(Messages.error("Unknown Spotify URL format"))
                return None
            
        except Exception as e:
            self._print(Messages.error(f"Fallback search failed: {e}"))
            return None
    
    def _scrape_spotify_track(self, spotify_url):
        """Scrape Spotify track information and download from YouTube"""
        try:
            self._print(Messages.info("Processing Spotify track URL..."))
            
            # Extract track info
            track_info = self._extract_spotify_track_info(spotify_url)
            
            if track_info:
                search_query = track_info
                self._print(f"[bold green]♪ Spotify Track:[/bold green] [cyan]{search_query}[/cyan]")
            else:
                # Ask user for track details
                self._print(Messages.warning("Could not automatically extract track information from URL"))
                self._print(Messages.info("💡 Please provide the track details manually:"))
                
                try:
                    from rich.prompt import Prompt
                    track_name = Prompt.ask("[cyan]Song/Track name[/cyan]")
                    artist_name = Prompt.ask("[cyan]Artist name (optional)[/cyan]", default="")
                    
                    if not track_name:
                        self._print(Messages.error("Track name is required"))
                        return None
                    
                    search_query = f"{track_name} - {artist_name}" if artist_name else track_name
                    self._print(f"\n[bold green]♪ Searching for:[/bold green] [cyan]{search_query}[/cyan]")
                except KeyboardInterrupt:
                    self._print(Messages.info("\nCancelled by user"))
                    return None
                except:
                    search_query = input("\nEnter track name and artist (e.g., 'Song - Artist'): ").strip()
                    if not search_query:
                        return None
            
            # Ask for quality preference
            output_format = 'mp3'
            quality = 'best'
            
            self._print(f"\n[bold cyan]🎚️  Select audio quality:[/bold cyan]")
            self._print("  [green]1[/green]. Best Quality (320kbps MP3) - Recommended")
            self._print("  [yellow]2[/yellow]. High Quality (256kbps AAC/M4A) - Balanced")
            self._print("  [blue]3[/blue]. Very High Quality (FLAC) - Lossless, larger files")
            self._print("  [magenta]4[/magenta]. Best Available (Auto) - Highest quality possible")
            
            try:
                from rich.prompt import Prompt
                quality_choice = Prompt.ask("\n[cyan]Enter choice (1-4)[/cyan]", default="1")
                
                if quality_choice == "1":
                    output_format = 'mp3'
                elif quality_choice == "2":
                    output_format = 'm4a'
                elif quality_choice == "3":
                    output_format = 'flac'
                elif quality_choice == "4":
                    output_format = 'best'
            except:
                try:
                    quality_choice = input("\nEnter choice (1-4) [default: 1]: ").strip() or "1"
                    if quality_choice == "2":
                        output_format = 'm4a'
                    elif quality_choice == "3":
                        output_format = 'flac'
                    elif quality_choice == "4":
                        output_format = 'best'
                except:
                    pass
            
            self._print(Messages.searching("Searching on YouTube..."))
            
            youtube_url = self.downloader._search_youtube(search_query)
            if youtube_url:
                self._print(Messages.success(f"Found on YouTube: {youtube_url}"))
                
                # Extract artist and title for filename
                if ' - ' in search_query:
                    parts = search_query.split(' - ', 1)
                    filename_format = f"{parts[1]} - {parts[0]}" if len(parts) == 2 else search_query
                else:
                    filename_format = search_query
                
                result = self.downloader.download_media(
                    youtube_url, 
                    audio_only=True, 
                    output_format=output_format,
                    quality=quality,
                    add_metadata=True,
                    add_thumbnail=True,
                    custom_filename=filename_format
                )
                
                # Get album art if available
                album_art_url = self._get_spotify_album_art(spotify_url)
                if result and album_art_url:
                    downloaded_file = self._find_recently_downloaded_file()
                    if downloaded_file:
                        self._embed_spotify_album_art(downloaded_file, album_art_url)
                
                return result
            else:
                self._print(Messages.error("Could not find track on YouTube"))
                return None
                
        except Exception as e:
            self._print(Messages.error(f"Error processing Spotify track: {e}"))
            return None
    
    def _scrape_spotify_album(self, spotify_url):
        """Scrape Spotify album information and download tracks"""
        try:
            if not BEAUTIFULSOUP_AVAILABLE:
                self._print(Messages.error("BeautifulSoup required for album scraping"))
                return None
            
            self._print(Messages.searching("Scraping Spotify album page..."))
            
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
            
            self._print(f"[bold magenta]♪ Spotify Album:[/bold magenta] [cyan]{artist_name} - {album_name}[/cyan]")
            
            # Try to extract track list
            tracks = []
            try:
                track_pattern = r'"name"\s*:\s*"([^"]+)".{0,500}?"type"\s*:\s*"track"'
                track_matches = re.findall(track_pattern, raw_html)
                
                if track_matches:
                    seen = set()
                    for track in track_matches:
                        if track not in seen and len(track) > 2:
                            seen.add(track)
                            tracks.append(track)
                    
                    self._print(Messages.success(f"Found {len(tracks)} tracks in album"))
                    self._print(Messages.info("Track list:"))
                    for i, track in enumerate(tracks[:5], 1):
                        self._print(f"  {i}. {track}")
                    if len(tracks) > 5:
                        self._print(f"  ... and {len(tracks) - 5} more")
            except:
                pass
            
            if not tracks:
                self._print(Messages.warning("Could not extract track list from album page"))
                # Fallback to searching for album on YouTube
                search_query = f"{artist_name} {album_name} full album"
                youtube_url = self.downloader._search_youtube(search_query)
                if youtube_url:
                    self._print(Messages.success(f"Found album on YouTube: {youtube_url}"))
                    return self.downloader.download_media(youtube_url, audio_only=True, output_format='mp3')
                return None
            
            # Download tracks
            safe_album_name = sanitize_filename(f"{artist_name} - {album_name}")
            album_dir = self.downloader.output_dir / safe_album_name
            album_downloader = self.downloader.__class__(album_dir)
            
            successful = 0
            for i, track_name in enumerate(tracks, 1):
                try:
                    search_query = f"{artist_name} - {track_name}"
                    self._print(f"\n[bold blue]♫ [{i:2d}/{len(tracks)}][/bold blue] [cyan]{search_query}[/cyan]")
                    
                    youtube_url = self.downloader._search_youtube(search_query)
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
                        self._print(Messages.error(f"Could not find: {track_name}"))
                except Exception as e:
                    self._print(Messages.error(f"Error downloading {track_name}: {e}"))
            
            self._print("")
            self._print(Messages.success(f"Album download completed: {successful}/{len(tracks)} tracks downloaded"))
            return successful > 0
            
        except Exception as e:
            self._print(Messages.error(f"Error scraping Spotify album: {e}"))
            return None
    
    def _scrape_spotify_playlist(self, spotify_url):
        """Scrape Spotify playlist information from web page with user preferences"""
        try:
            self._print(Messages.searching("Fetching playlist information..."))
            
            # Extract playlist ID
            playlist_id = self._extract_spotify_id(spotify_url, 'playlist')
            if not playlist_id:
                self._print(Messages.error("Could not extract playlist ID"))
                return None
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
                'Accept': 'application/json',
            }
            
            # Get playlist name from the web page
            web_response = requests.get(spotify_url, headers=headers, timeout=10)
            playlist_name = "Spotify Playlist"
            
            if web_response.status_code == 200 and BEAUTIFULSOUP_AVAILABLE:
                soup = BeautifulSoup(web_response.content, 'html.parser')
                og_title = soup.find('meta', property='og:title')
                if og_title:
                    playlist_name = og_title.get('content', 'Spotify Playlist').strip()
            
            # Try using spotdl if available
            try:
                import spotdl
                self._print(Messages.success("Using spotdl for playlist download..."))
                result = self._download_spotify_with_spotdl(spotify_url, playlist_name)
                if result:  # If spotdl succeeded, return
                    return True
                # If spotdl failed, fall through to next methods
            except ImportError:
                # spotdl not available, continue to next method
                pass
            
            # Try using Spotify API if available
            if self.spotify_client:
                self._print(Messages.info("Using Spotify API for playlist download..."))
                return self._download_playlist_api(spotify_url, interactive=True)
            
            # Fallback: Try to scrape tracks from the page and download individually
            self._print(Messages.info(f"Attempting web scraping for playlist: {playlist_name}"))
            try:
                tracks = self._scrape_playlist_tracks(web_response.text if web_response.status_code == 200 else "")
                
                if tracks and len(tracks) > 0:
                    self._print(Messages.success(f"Found {len(tracks)} tracks in playlist"))
                    
                    # Show track list
                    self._print("")
                    self._print(f"[bold cyan]♫ Playlist: {playlist_name}[/bold cyan]")
                    self._print(f"[bold]Total tracks available: {len(tracks)}[/bold]")
                    self._print("")
                    self._print("First 15 tracks:")
                    for i, track in enumerate(tracks[:15], 1):
                        self._print(f"  {i:2d}. {track}")
                    if len(tracks) > 15:
                        self._print(f"  ... and {len(tracks) - 15} more tracks")
                    
                    # Ask user what to download
                    selected_tracks = self._prompt_playlist_scraping_preferences(tracks, playlist_name)
                    
                    if not selected_tracks or len(selected_tracks) == 0:
                        self._print(Messages.warning("No tracks selected for download"))
                        return None
                    
                    # Ask for audio format and quality
                    self._print("")
                    output_format, quality = self.downloader._prompt_audio_format_quality()
                    
                    # Create playlist directory
                    safe_playlist_name = sanitize_filename(playlist_name)
                    playlist_dir = self.downloader.output_dir / f"Spotify - {safe_playlist_name}"
                    playlist_dir.mkdir(parents=True, exist_ok=True)
                    
                    # Download selected tracks
                    self._print(f"\n[bold cyan]▶ Starting download of {len(selected_tracks)} track(s)...[/bold cyan]\n")
                    
                    successful = 0
                    failed = 0
                    
                    for i, track in enumerate(selected_tracks, 1):
                        try:
                            self._print(f"[bold blue]♫ [{i:2d}/{len(selected_tracks)}][/bold blue] [cyan]{track}[/cyan]")
                            
                            youtube_url = self.downloader._search_youtube(track)
                            if youtube_url:
                                playlist_downloader = self.downloader.__class__(playlist_dir)
                                result = playlist_downloader.download_media(
                                    youtube_url,
                                    audio_only=True,
                                    output_format=output_format,
                                    quality=quality,
                                    add_metadata=True,
                                    add_thumbnail=True
                                )
                                if result:
                                    successful += 1
                                else:
                                    failed += 1
                            else:
                                self._print(Messages.error(f"Could not find on YouTube: {track}"))
                                failed += 1
                        except Exception as e:
                            self._print(Messages.error(f"Error downloading: {e}"))
                            failed += 1
                    
                    self._print("")
                    self._print(f"[bold green]✓ Playlist download completed![/bold green]")
                    self._print(f"  {successful} tracks downloaded successfully")
                    if failed > 0:
                        self._print(f"  {failed} tracks failed")
                    
                    return successful > 0
            except Exception as e:
                self._print(Messages.warning(f"Web scraping failed: {e}"))
            
            # Provide help information
            self._print(Messages.warning(f"Cannot fully download playlist: {playlist_name}"))
            self._print("")
            
            if RICH_AVAILABLE and self.console:
                self.console.print(Panel.fit(
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
            else:
                print("Spotify Playlist Download Options:")
                print("1. Install spotdl: pip install spotdl")
                print("2. Set Spotify API credentials")
                print("3. Download individual tracks using their URLs")
            
            return None
            
        except Exception as e:
            self._print(Messages.error(f"Error processing Spotify playlist: {e}"))
            return None
    
    def _prompt_playlist_scraping_preferences(self, tracks, playlist_name):
        """Prompt user for playlist download preferences (range and options)"""
        try:
            self._print("")
            self._print("[bold yellow]━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━[/bold yellow]")
            self._print("[bold cyan]📋 Download Preferences[/bold cyan]")
            self._print("[bold yellow]━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━[/bold yellow]")
            self._print("")
            
            # Option 1: Download all tracks
            self._print("[bold]1.[/bold] Download all tracks")
            self._print("[bold]2.[/bold] Download first N tracks (specify range)")
            self._print("[bold]3.[/bold] Select custom range (e.g., 1-20)")
            self._print("[bold]4.[/bold] Cancel")
            self._print("")
            
            while True:
                try:
                    choice = input("Enter your choice (1-4): ").strip()
                    
                    if choice == "1":
                        # Download all
                        self._print(f"[bold green]✓[/bold green] Will download all {len(tracks)} tracks")
                        return tracks
                    
                    elif choice == "2":
                        # Download first N tracks
                        while True:
                            try:
                                num_tracks_str = input(f"How many tracks to download? (1-{len(tracks)}): ").strip()
                                num_tracks = int(num_tracks_str)
                                
                                if 1 <= num_tracks <= len(tracks):
                                    self._print(f"[bold green]✓[/bold green] Will download first {num_tracks} tracks")
                                    return tracks[:num_tracks]
                                else:
                                    print(f"Please enter a number between 1 and {len(tracks)}")
                            except ValueError:
                                print("Please enter a valid number")
                    
                    elif choice == "3":
                        # Custom range
                        while True:
                            try:
                                range_str = input(f"Enter range (e.g., 1-20, or 5-15): ").strip()
                                
                                if '-' in range_str:
                                    parts = range_str.split('-')
                                    start = int(parts[0].strip())
                                    end = int(parts[1].strip())
                                    
                                    if 1 <= start <= end <= len(tracks):
                                        selected = tracks[start-1:end]
                                        self._print(f"[bold green]✓[/bold green] Will download {len(selected)} tracks (#{start}-#{end})")
                                        return selected
                                    else:
                                        print(f"Please enter valid range within 1-{len(tracks)}")
                                else:
                                    print("Use format: start-end (e.g., 1-20)")
                            except ValueError:
                                print("Please enter valid numbers in format: start-end")
                    
                    elif choice == "4":
                        print("Download cancelled")
                        return []
                    
                    else:
                        print("Please enter 1, 2, 3, or 4")
                        
                except KeyboardInterrupt:
                    print("\nDownload cancelled")
                    return []
        
        except Exception as e:
            self._print(Messages.error(f"Error in preferences: {e}"))
            return tracks
    
    def _scrape_playlist_tracks(self, html_content):
        """Scrape track names from Spotify playlist HTML"""
        try:
            if not html_content:
                return []
            
            import re
            
            # Primary method: Extract track URLs and get track names from BeautifulSoup
            try:
                from bs4 import BeautifulSoup
                
                soup = BeautifulSoup(html_content, 'html.parser')
                
                # Find all track links in the HTML
                track_links = soup.find_all('a', href=True)
                tracks = []
                
                for link in track_links:
                    href = link.get('href', '')
                    if '/track/' in href:
                        # Get the visible text of the link
                        track_name = link.get_text(strip=True)
                        if track_name and len(track_name) > 2:
                            # Filter out common non-track strings
                            if not any(x in track_name.lower() for x in ['playlist', 'button', 'icon', 'close']):
                                if track_name not in tracks:
                                    tracks.append(track_name)
                
                if tracks:
                    return tracks[:50]  # Return up to 50 tracks
            except ImportError:
                pass  # Fall back to regex if BeautifulSoup not available
            except Exception:
                pass  # Fall back to regex on any parsing error
            
            # Fallback: Regex-based extraction if BeautifulSoup fails
            tracks = []
            
            # Pattern 1: Direct extraction from href="/track/..." links
            link_pattern = r'<a[^>]*href="/track/[^"]*"[^>]*>([^<]+)<'
            matches = re.findall(link_pattern, html_content)
            if matches:
                for match in matches:
                    track_name = match.strip()
                    if len(track_name) > 2 and track_name not in tracks:
                        if not any(x in track_name.lower() for x in ['playlist', 'button', 'icon', 'close']):
                            tracks.append(track_name)
            
            # Pattern 2: JSON-LD structured data extraction
            if not tracks:
                json_patterns = [
                    r'"name"\s*:\s*"([^"]+)"\s*,\s*"type"\s*:\s*"track"',
                    r'"trackName"\s*:\s*"([^"]+)"',
                    r'"@type"\s*:\s*"MusicRecording"\s*,\s*"name"\s*:\s*"([^"]+)"',
                ]
                
                for pattern in json_patterns:
                    matches = re.findall(pattern, html_content, re.DOTALL)
                    if matches:
                        for match in matches:
                            track_name = match.strip()
                            if len(track_name) > 2 and track_name not in tracks:
                                if not any(x in track_name.lower() for x in ['playlist', 'button', 'icon', 'close']):
                                    tracks.append(track_name)
                        if tracks:
                            break
            
            # Remove duplicates while preserving order
            seen = set()
            unique_tracks = []
            for track in tracks:
                if track not in seen:
                    seen.add(track)
                    unique_tracks.append(track)
            
            return unique_tracks[:50]  # Return up to 50 tracks
            
        except Exception as e:
            return []
    
    def _download_spotify_with_spotdl(self, spotify_url, playlist_name):
        """Download Spotify content using spotdl"""
        try:
            # Check Python version
            if sys.version_info < (3, 10):
                self._print(Messages.warning("spotdl requires Python 3.10+. Trying alternative method..."))
                return None
            
            try:
                from spotdl import Spotdl
            except ImportError as ie:
                self._print(Messages.warning(f"spotdl not available: {ie}"))
                self._print(Messages.info("Falling back to web scraping method..."))
                return None
            except Exception as import_error:
                self._print(Messages.warning(f"Error importing spotdl: {import_error}"))
                self._print(Messages.info("Falling back to web scraping method..."))
                return None
            
            # Create playlist directory
            safe_playlist_name = sanitize_filename(playlist_name)
            playlist_dir = self.downloader.output_dir / f"Spotify - {safe_playlist_name}"
            playlist_dir.mkdir(parents=True, exist_ok=True)
            
            self._print(Messages.info(f"Downloading to: {playlist_dir}"))
            self._print(Messages.searching("Initializing spotdl..."))
            
            try:
                # Configure spotdl options
                spotdl_client = Spotdl(
                    client_id="",
                    client_secret="",
                    user_auth=False,
                    cache_path=str(playlist_dir / '.spotdl'),
                    output=str(playlist_dir / '{artist} - {title}.{output-ext}')
                )
                
                self._print(Messages.info("Starting download with spotdl..."))
                results = spotdl_client.download([spotify_url])
                
                self._print(Messages.success(f"Download completed: {len(results)} items"))
                return len(results) > 0
            except TypeError as te:
                # spotdl API might have changed, try without auth parameters
                self._print(Messages.warning("Retrying with simplified spotdl configuration..."))
                try:
                    spotdl_client = Spotdl(
                        cache_path=str(playlist_dir / '.spotdl'),
                        output=str(playlist_dir / '{artist} - {title}.{output-ext}')
                    )
                    results = spotdl_client.download([spotify_url])
                    self._print(Messages.success(f"Download completed: {len(results)} items"))
                    return len(results) > 0
                except Exception as retry_error:
                    self._print(Messages.warning(f"spotdl retry failed: {retry_error}"))
                    self._print(Messages.info("Falling back to web scraping method..."))
                    return None
            
        except Exception as e:
            self._print(Messages.warning(f"spotdl error: {e}"))
            self._print(Messages.info("Falling back to web scraping method..."))
            return None
    
    def _extract_spotify_track_info(self, spotify_url):
        """Extract track information from Spotify URL"""
        try:
            # Method 1: Try oembed API
            try:
                import urllib3
                urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
                
                oembed_url = f"https://open.spotify.com/oembed?url={spotify_url}"
                response = requests.get(oembed_url, timeout=10, verify=False)
                
                if response.status_code == 200:
                    data = response.json()
                    title_raw = data.get('title', '').strip()
                    
                    if title_raw:
                        # Parse title - try middle dot first, then dash
                        if ' · ' in title_raw:
                            parts = title_raw.split(' · ')
                            if len(parts) == 2:
                                artist_name = parts[0].strip()
                                track_name = parts[1].strip()
                                return f"{track_name} - {artist_name}"
                        elif ' - ' in title_raw and title_raw.count(' - ') == 1:
                            parts = title_raw.split(' - ')
                            return f"{parts[1]} - {parts[0]}"
                        else:
                            return title_raw
            except:
                pass
            
            # Method 2: Try scraping the page
            try:
                if not BEAUTIFULSOUP_AVAILABLE:
                    return None
                
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
                }
                response = requests.get(spotify_url, headers=headers, timeout=10)
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    og_title = soup.find('meta', property='og:title')
                    if og_title and og_title.get('content'):
                        title_content = og_title.get('content').strip()
                        
                        if ' - song and lyrics by ' in title_content.lower():
                            parts = title_content.split(' - song and lyrics by ')
                            if len(parts) >= 2:
                                track_name = parts[0].strip()
                                artist_part = parts[1].split('|')[0].strip()
                                return f"{track_name} - {artist_part}"
            except:
                pass
            
            return None
            
        except Exception:
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
                    return thumbnail_url
        except:
            pass
        
        return None
    
    def _embed_spotify_album_art(self, file_path, album_art_url):
        """Download and embed Spotify album art into the audio file"""
        try:
            if not MUTAGEN_AVAILABLE:
                return False
            
            self._print(Messages.info("Adding Spotify album art..."))
            
            # Download album art
            response = requests.get(album_art_url, timeout=10)
            if response.status_code != 200:
                return False
            
            album_art_data = response.content
            
            # Determine file type and embed art
            file_path_obj = Path(file_path) if isinstance(file_path, str) else file_path
            
            if not file_path_obj.exists():
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
                        type=3,
                        desc='Cover',
                        data=album_art_data
                    )
                )
                audio.save()
                self._print(Messages.success("✓ Album art added successfully!"))
                return True
                
            elif file_ext == '.m4a':
                audio = MP4(str(file_path_obj))
                audio.tags['covr'] = [MP4Cover(album_art_data, imageformat=MP4Cover.FORMAT_JPEG)]
                audio.save()
                self._print(Messages.success("✓ Album art added successfully!"))
                return True
                
            elif file_ext == '.flac':
                audio = FLAC(str(file_path_obj))
                image = Picture()
                image.type = 3
                image.mime = 'image/jpeg'
                image.desc = 'Cover'
                image.data = album_art_data
                audio.add_picture(image)
                audio.save()
                self._print(Messages.success("✓ Album art added successfully!"))
                return True
            
            return False
            
        except Exception as e:
            self._print(f"  [dim]⚠ Could not add album art: {e}[/dim]")
            return False
    
    def _find_recently_downloaded_file(self):
        """Find the most recently downloaded audio file"""
        try:
            import time
            current_time = time.time()
            
            audio_extensions = ['.mp3', '.m4a', '.flac', '.opus', '.ogg', '.wav']
            recent_files = []
            
            for ext in audio_extensions:
                files = list(self.downloader.output_dir.glob(f"*{ext}"))
                for f in files:
                    if f.is_file() and (current_time - f.stat().st_mtime) < 120:
                        recent_files.append((f, f.stat().st_mtime))
            
            if recent_files:
                recent_files.sort(key=lambda x: x[1], reverse=True)
                return recent_files[0][0]
            
            return None
            
        except Exception:
            return None
    
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
    
    def _print(self, message):
        """Print message with Rich support"""
        if RICH_AVAILABLE and self.console:
            self.console.print(message)
        else:
            print(message)
