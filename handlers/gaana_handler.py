#!/usr/bin/env python3
"""
Gaana Handler Module
Handles all Gaana-related functionality including downloading tracks, albums, 
playlists, and artists with metadata extraction and YouTube search fallback.
Uses Gaana web scraping for fetching song metadata.
"""

import os
import re
import sys
import json
import requests
import warnings
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from html import unescape

# Suppress warnings
warnings.filterwarnings('ignore')

try:
    from bs4 import BeautifulSoup
    BEAUTIFULSOUP_AVAILABLE = True
except ImportError:
    BEAUTIFULSOUP_AVAILABLE = False

try:
    import cloudscraper
    CLOUDSCRAPER_AVAILABLE = True
except ImportError:
    CLOUDSCRAPER_AVAILABLE = False

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

from utils.utils import sanitize_filename
from utils.ui_components import Icons, Messages


class GaanaHandler:
    """Handles Gaana downloads and metadata extraction"""
    
    def __init__(self, downloader):
        """Initialize Gaana handler with reference to main downloader
        
        Args:
            downloader: Reference to UltimateMediaDownloader instance
        """
        self.downloader = downloader
        self.console = Console() if RICH_AVAILABLE else None
        
        # Gaana base URL
        self.base_url = "https://gaana.com"
        self.api_base_url = "https://api.gaana.com"
        
        # User-Agent for requests
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Referer': 'https://gaana.com/'
        }
    
    def _decode_html_entities(self, text):
        """Decode HTML entities in text (e.g., &quot; to ", &amp; to &)
        
        Args:
            text: Text that may contain HTML entities
            
        Returns:
            Decoded text with HTML entities converted to proper characters
        """
        if not text or not isinstance(text, str):
            return text
        return unescape(text)
        
    def search_and_download(self, gaana_url, interactive=True):
        """Enhanced Gaana downloader with multiple strategies
        
        Args:
            gaana_url: URL to Gaana content
            interactive: Whether to prompt user for options
            
        Returns:
            True if successful, False/None otherwise
        """
        print(f"♪ Processing Gaana URL: {gaana_url}")
        
        try:
            # Determine Gaana content type
            if '/song/' in gaana_url:
                return self._download_track(gaana_url, interactive=interactive)
            elif '/album/' in gaana_url:
                return self._download_album(gaana_url, interactive=interactive)
            elif '/playlist/' in gaana_url:
                return self._download_playlist(gaana_url, interactive=interactive)
            elif '/artist/' in gaana_url:
                return self._download_artist(gaana_url, interactive=interactive)
            else:
                self._print(Messages.error("Unknown Gaana URL format"))
                return None
                
        except Exception as e:
            self._print(Messages.error(f"Error processing Gaana URL: {e}"))
            return None
    
    def _fetch_song_data(self, song_url):
        """Fetch song data from Gaana page
        
        Args:
            song_url: Gaana song URL
            
        Returns:
            Dictionary containing song metadata or None
        """
        try:
            if not BEAUTIFULSOUP_AVAILABLE:
                self._print(Messages.error("BeautifulSoup is required for Gaana support"))
                return None
            
            self._print(f"[dim]Fetching: {song_url}[/dim]")
            
            response = requests.get(song_url, headers=self.headers, timeout=15)
            
            if response.status_code != 200:
                self._print(Messages.error(f"Failed to fetch page: HTTP {response.status_code}"))
                return None
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            song_data = {}
            
            # Try to extract from meta tags first
            title_tag = soup.find('meta', {'property': 'og:title'})
            if title_tag:
                song_data['name'] = self._decode_html_entities(title_tag.get('content', ''))
            
            # Image
            image_tag = soup.find('meta', {'property': 'og:image'})
            if image_tag:
                song_data['image'] = image_tag.get('content', '')
            
            # Description might contain artist info
            desc_tag = soup.find('meta', {'property': 'og:description'}) or soup.find('meta', {'name': 'description'})
            if desc_tag:
                desc = desc_tag.get('content', '')
                song_data['description'] = desc
            
            # Try to find structured JSON-LD data
            script_tags = soup.find_all('script', type='application/ld+json')
            for script in script_tags:
                try:
                    json_data = json.loads(script.string)
                    if isinstance(json_data, dict):
                        if json_data.get('@type') == 'MusicRecording':
                            song_data['name'] = json_data.get('name', song_data.get('name', ''))
                            
                            # Extract artist info
                            if 'byArtist' in json_data:
                                artist_data = json_data['byArtist']
                                if isinstance(artist_data, dict):
                                    song_data['primary_artists'] = artist_data.get('name', '')
                                elif isinstance(artist_data, list):
                                    artists = [a.get('name', '') for a in artist_data if isinstance(a, dict) and a.get('name')]
                                    song_data['primary_artists'] = ', '.join(artists)
                            
                            # Extract album info
                            if 'inAlbum' in json_data and isinstance(json_data['inAlbum'], dict):
                                song_data['album'] = json_data['inAlbum'].get('name', '')
                            
                            # Extract duration
                            if 'duration' in json_data:
                                song_data['duration'] = json_data['duration']
                            
                            # Extract release date
                            if 'datePublished' in json_data:
                                song_data['year'] = json_data['datePublished'][:4]
                            
                            break
                except Exception as e:
                    if self.downloader.verbose:
                        self._print(f"[dim]Error parsing JSON-LD: {e}[/dim]")
                    continue
            
            # Fallback: Try to extract from page elements
            if not song_data.get('name'):
                # Try h1 or title elements
                h1_tag = soup.find('h1')
                if h1_tag:
                    song_data['name'] = self._decode_html_entities(h1_tag.get_text(strip=True))
                elif soup.title:
                    title_text = soup.title.get_text()
                    # Remove "- Gaana.com" or similar suffixes
                    song_data['name'] = re.sub(r'\s*[-|]\s*Gaana.*$', '', title_text, flags=re.IGNORECASE).strip()
            
            # Try to find artist from page elements if not found in JSON-LD
            if not song_data.get('primary_artists'):
                artist_links = soup.find_all('a', href=re.compile(r'/artist/'))
                if artist_links:
                    artists = [self._decode_html_entities(a.get_text(strip=True)) for a in artist_links[:3]]
                    song_data['primary_artists'] = ', '.join(filter(None, artists))
            
            if song_data.get('name'):
                return song_data
            
            self._print(Messages.error("Could not extract song data from page"))
            return None
            
        except Exception as e:
            self._print(Messages.error(f"Error fetching song data: {e}"))
            if self.downloader.verbose:
                import traceback
                self._print(f"[dim]{traceback.format_exc()}[/dim]")
            return None
    
    def _fetch_album_data(self, album_url):
        """Fetch album data from Gaana page
        
        Args:
            album_url: Gaana album URL
            
        Returns:
            Dictionary containing album metadata and songs or None
        """
        try:
            if not BEAUTIFULSOUP_AVAILABLE:
                self._print(Messages.error("BeautifulSoup is required for Gaana support"))
                return None
            
            self._print(f"[dim]Fetching album: {album_url}[/dim]")
            
            response = requests.get(album_url, headers=self.headers, timeout=15)
            
            if response.status_code != 200:
                self._print(Messages.error(f"Failed to fetch album: HTTP {response.status_code}"))
                return None
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            album_data = {'songs': []}
            
            # Extract album title
            title_tag = soup.find('meta', {'property': 'og:title'})
            if title_tag:
                album_data['name'] = self._decode_html_entities(title_tag.get('content', ''))
            
            # Extract album image
            image_tag = soup.find('meta', {'property': 'og:image'})
            if image_tag:
                album_data['image'] = image_tag.get('content', '')
            
            # Try to find structured JSON-LD data
            script_tags = soup.find_all('script', type='application/ld+json')
            for script in script_tags:
                try:
                    json_data = json.loads(script.string)
                    if isinstance(json_data, dict):
                        if json_data.get('@type') == 'MusicAlbum':
                            album_data['name'] = json_data.get('name', album_data.get('name', ''))
                            
                            # Extract artist
                            if 'byArtist' in json_data:
                                artist_data = json_data['byArtist']
                                if isinstance(artist_data, dict):
                                    album_data['primary_artists'] = artist_data.get('name', '')
                                elif isinstance(artist_data, list) and len(artist_data) > 0:
                                    album_data['primary_artists'] = artist_data[0].get('name', '') if isinstance(artist_data[0], dict) else ''
                            
                            # Extract tracks
                            if 'track' in json_data and isinstance(json_data['track'], list):
                                for track in json_data['track']:
                                    if isinstance(track, dict):
                                        song = {
                                            'name': track.get('name', ''),
                                            'url': track.get('url', '')
                                        }
                                        if 'byArtist' in track:
                                            artist_info = track['byArtist']
                                            if isinstance(artist_info, dict):
                                                song['primary_artists'] = artist_info.get('name', '')
                                            elif isinstance(artist_info, list):
                                                song['primary_artists'] = ', '.join([a.get('name', '') for a in artist_info if isinstance(a, dict)])
                                        album_data['songs'].append(song)
                            
                            break
                except Exception as e:
                    if self.downloader.verbose:
                        self._print(f"[dim]Error parsing JSON-LD: {e}[/dim]")
                    continue
            
            # Fallback: Try to extract songs from page links
            if not album_data['songs']:
                song_links = soup.find_all('a', href=re.compile(r'/song/[^/]+'))
                seen_urls = set()
                for link in song_links:
                    song_url = link.get('href', '')
                    if song_url and song_url not in seen_urls:
                        if not song_url.startswith('http'):
                            song_url = f"{self.base_url}{song_url}"
                        song_title = self._decode_html_entities(link.get_text(strip=True))
                        if song_title and song_url:
                            album_data['songs'].append({
                                'name': song_title,
                                'url': song_url
                            })
                            seen_urls.add(song_url)
            
            if album_data.get('name') or album_data['songs']:
                return album_data
            
            self._print(Messages.error("Could not extract album data"))
            return None
            
        except Exception as e:
            self._print(Messages.error(f"Error fetching album data: {e}"))
            if self.downloader.verbose:
                import traceback
                self._print(f"[dim]{traceback.format_exc()}[/dim]")
            return None
    
    def _fetch_playlist_data(self, playlist_url):
        """Fetch playlist data from Gaana page
        
        Args:
            playlist_url: Gaana playlist URL
            
        Returns:
            Dictionary containing playlist metadata and songs or None
        """
        try:
            if not BEAUTIFULSOUP_AVAILABLE:
                self._print(Messages.error("BeautifulSoup is required for Gaana support"))
                return None
            
            self._print(f"[dim]Fetching playlist: {playlist_url}[/dim]")
            
            response = requests.get(playlist_url, headers=self.headers, timeout=15)
            
            if response.status_code != 200:
                self._print(Messages.error(f"Failed to fetch playlist: HTTP {response.status_code}"))
                return None
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            playlist_data = {'songs': []}
            
            # Extract playlist title
            title_tag = soup.find('meta', {'property': 'og:title'})
            if title_tag:
                playlist_data['name'] = self._decode_html_entities(title_tag.get('content', ''))
            
            # Extract playlist image
            image_tag = soup.find('meta', {'property': 'og:image'})
            if image_tag:
                playlist_data['image'] = image_tag.get('content', '')
            
            # Try to find structured JSON-LD data
            script_tags = soup.find_all('script', type='application/ld+json')
            for script in script_tags:
                try:
                    json_data = json.loads(script.string)
                    if isinstance(json_data, dict):
                        if json_data.get('@type') == 'MusicPlaylist':
                            playlist_data['name'] = json_data.get('name', playlist_data.get('name', ''))
                            
                            # Extract tracks
                            if 'track' in json_data and isinstance(json_data['track'], list):
                                for track in json_data['track']:
                                    if isinstance(track, dict):
                                        song = {
                                            'name': track.get('name', ''),
                                            'url': track.get('url', '')
                                        }
                                        if 'byArtist' in track:
                                            artist_info = track['byArtist']
                                            if isinstance(artist_info, dict):
                                                song['primary_artists'] = artist_info.get('name', '')
                                            elif isinstance(artist_info, list):
                                                song['primary_artists'] = ', '.join([a.get('name', '') for a in artist_info if isinstance(a, dict)])
                                        playlist_data['songs'].append(song)
                            
                            break
                except Exception as e:
                    if self.downloader.verbose:
                        self._print(f"[dim]Error parsing JSON-LD: {e}[/dim]")
                    continue
            
            # Fallback: Try to extract songs from page links
            if not playlist_data['songs']:
                song_links = soup.find_all('a', href=re.compile(r'/song/[^/]+'))
                seen_urls = set()
                for link in song_links:
                    song_url = link.get('href', '')
                    if song_url and song_url not in seen_urls:
                        if not song_url.startswith('http'):
                            song_url = f"{self.base_url}{song_url}"
                        song_title = self._decode_html_entities(link.get_text(strip=True))
                        if song_title and song_url:
                            playlist_data['songs'].append({
                                'name': song_title,
                                'url': song_url
                            })
                            seen_urls.add(song_url)
            
            if playlist_data.get('name') or playlist_data['songs']:
                return playlist_data
            
            self._print(Messages.error("Could not extract playlist data"))
            return None
            
        except Exception as e:
            self._print(Messages.error(f"Error fetching playlist data: {e}"))
            if self.downloader.verbose:
                import traceback
                self._print(f"[dim]{traceback.format_exc()}[/dim]")
            return None
    
    def _download_track(self, song_url, interactive=True, output_format=None, quality=None):
        """Download single Gaana track by searching on YouTube
        
        Args:
            song_url: Gaana song URL
            interactive: Whether to prompt user for options
            output_format: Output format (mp3, flac, m4a, etc.) - if None, will prompt
            quality: Quality setting - if None, will prompt
            
        Returns:
            True if successful, False/None otherwise
        """
        try:
            self._print(Messages.searching("Fetching song metadata from Gaana..."))
            
            song_data = self._fetch_song_data(song_url)
            
            if not song_data:
                self._print(Messages.error("Could not fetch song data from Gaana"))
                return None
            
            # Extract song information
            title = self._decode_html_entities(song_data.get('name', 'Unknown'))
            artists = self._decode_html_entities(song_data.get('primary_artists', 'Unknown Artist'))
            album = self._decode_html_entities(song_data.get('album', ''))
            year = song_data.get('year', '')
            image_url = song_data.get('image', '')
            
            search_query = f"{title} - {artists}"
            
            self._print(f"[bold green]{Icons.get('music')} Gaana Track:[/bold green] [cyan]{search_query}[/cyan]")
            if album:
                self._print(f"[dim]Album: {album}[/dim]")
            if year:
                self._print(f"[dim]Year: {year}[/dim]")
            
            # Ask for quality preference
            if output_format is None or quality is None:
                if interactive:
                    output_format, quality = self.downloader._prompt_audio_format_quality()
                else:
                    output_format = 'mp3'
                    quality = 'best'
            
            self._print(Messages.searching("Searching on YouTube..."))
            
            # Use YouTube search with scoring for better results
            youtube_url = self._search_youtube_with_scoring(search_query, title, artists)
            if youtube_url:
                self._print(Messages.success(f"Found on YouTube: {youtube_url}"))
                filename_format = f"{artists} - {title}"
                
                result = self.downloader.download_media(
                    youtube_url, 
                    audio_only=True, 
                    output_format=output_format,
                    quality=quality,
                    add_metadata=True,
                    add_thumbnail=True,
                    custom_filename=filename_format
                )
                
                # Embed album art from Gaana if available
                if result and image_url and MUTAGEN_AVAILABLE:
                    downloaded_file = self._find_recently_downloaded_file()
                    if downloaded_file:
                        self._embed_album_art(downloaded_file, image_url, title, artists, album, year)
                
                return result
            else:
                self._print(Messages.error("Could not find track on YouTube"))
                return None
                
        except Exception as e:
            self._print(Messages.error(f"Error downloading Gaana track: {e}"))
            return None
    
    def _search_youtube_with_scoring(self, search_query, title, artists):
        """Search YouTube and pick the best match based on view count and likes
        
        Args:
            search_query: Full search query (format: "Title - Artist")
            title: Song title
            artists: Artist names
            
        Returns:
            Best matching YouTube URL or None
        """
        # Clean the title by removing extra info
        clean_title = re.sub(r'\(From ["\'].*?["\']\)', '', title).strip()
        clean_title = re.sub(r'\s*-\s*(Hindi|English|Tamil|Telugu|Malayalam|Kannada|Bengali|Punjabi|Marathi)\s*$', '', clean_title, flags=re.IGNORECASE).strip()
        
        # Try multiple search query variations
        search_queries = [
            f"{clean_title} {artists} official audio",
            f"{clean_title} {artists} lyric video",
            f"{clean_title} {artists} audio",
            f"{clean_title} {artists}",
            search_query,
            f"{title} {artists} official",
        ]
        
        for attempt, query in enumerate(search_queries, 1):
            try:
                if attempt > 1:
                    self._print(f"[dim]⟳ Retry {attempt}/{len(search_queries)}: Trying '{query}'...[/dim]")
                
                # Search for multiple results
                if hasattr(self.downloader, '_search_youtube_multiple'):
                    results = self.downloader._search_youtube_multiple(query, max_results=5)
                    
                    if results and len(results) > 0:
                        if attempt == 1:
                            print(f"Found {len(results)} results, analyzing...")
                        
                        best_url = self._pick_best_youtube_result(results, clean_title, artists, attempt == 1)
                        
                        if best_url:
                            return best_url
                        
                        if attempt < len(search_queries):
                            continue
                
                # Fallback to simple search only on last attempt
                if attempt == len(search_queries):
                    result = self.downloader._search_youtube(query)
                    if result:
                        return result
                    
            except Exception as e:
                if attempt == len(search_queries):
                    self._print(Messages.warning(f"YouTube search error: {e}"))
                continue
        
        return None
    
    def _pick_best_youtube_result(self, youtube_urls, title, artists, show_details=True):
        """Pick the best YouTube result based on title similarity, view count and likes
        
        Args:
            youtube_urls: List of YouTube URLs to analyze
            title: Song title to match against
            artists: Artist names to match against
            show_details: Whether to print detailed analysis
            
        Returns:
            Best matching YouTube URL or None
        """
        try:
            import yt_dlp
            
            best_url = None
            best_score = -1
            
            # Normalize search terms for comparison
            title_lower = title.lower()
            artists_lower = artists.lower() if artists else ""
            
            # Keywords to avoid
            avoid_keywords = ['remix', 'cover', 'karaoke', 'instrumental', 'live', 'unplugged']
            
            for url in youtube_urls[:5]:  # Analyze top 5 results
                try:
                    ydl_opts = {
                        'quiet': True,
                        'no_warnings': True,
                        'extract_flat': False,
                    }
                    
                    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                        info = ydl.extract_info(url, download=False)
                        
                        if not info:
                            continue
                        
                        video_title = info.get('title', '').lower()
                        view_count = info.get('view_count', 0) or 0
                        like_count = info.get('like_count', 0) or 0
                        
                        # Calculate score
                        score = 0
                        
                        # Title match (most important)
                        if title_lower in video_title:
                            score += 100
                        
                        # Artist match
                        if artists_lower and artists_lower in video_title:
                            score += 50
                        
                        # Prefer official content
                        if 'official' in video_title:
                            score += 30
                        if 'audio' in video_title or 'lyric' in video_title:
                            score += 20
                        
                        # Penalize unwanted content
                        for keyword in avoid_keywords:
                            if keyword in video_title:
                                score -= 50
                        
                        # View count bonus (normalized)
                        if view_count > 1000000:
                            score += 10
                        if view_count > 10000000:
                            score += 20
                        
                        # Like ratio bonus
                        if view_count > 0 and like_count > 0:
                            like_ratio = like_count / view_count
                            if like_ratio > 0.03:  # 3% or more
                                score += 15
                        
                        if show_details:
                            self._print(f"[dim]  • {info.get('title', 'Unknown')} (Score: {score}, Views: {view_count:,})[/dim]")
                        
                        if score > best_score:
                            best_score = score
                            best_url = url
                            
                except Exception as e:
                    if self.downloader.verbose:
                        self._print(f"[dim]Error analyzing {url}: {e}[/dim]")
                    continue
            
            return best_url
            
        except ImportError:
            self._print(Messages.warning("yt-dlp not available for scoring"))
            return youtube_urls[0] if youtube_urls else None
        except Exception as e:
            self._print(Messages.warning(f"Error picking best result: {e}"))
            return youtube_urls[0] if youtube_urls else None
    
    def _download_album(self, album_url, interactive=True):
        """Download Gaana album by downloading all tracks
        
        Args:
            album_url: Gaana album URL
            interactive: Whether to prompt user for options
            
        Returns:
            True if successful, False/None otherwise
        """
        try:
            self._print(Messages.searching("Fetching album metadata from Gaana..."))
            
            album_data = self._fetch_album_data(album_url)
            
            if not album_data or not album_data.get('songs'):
                self._print(Messages.error("Could not fetch album data or no songs found"))
                return None
            
            album_name = album_data.get('name', 'Unknown Album')
            songs = album_data['songs']
            
            self._print(f"\n[bold green]{Icons.get('music')} Gaana Album:[/bold green] [cyan]{album_name}[/cyan]")
            self._print(f"[bold]Total tracks:[/bold] {len(songs)}\n")
            
            # Display song list
            if interactive:
                self._print("[bold cyan]═══ Song List ═══[/bold cyan]")
                for i, song in enumerate(songs, 1):
                    song_name = song.get('name', 'Unknown')
                    artist = song.get('primary_artists', '')
                    if artist:
                        self._print(f"[yellow]{i:2d}.[/yellow] {song_name} [dim]- {artist}[/dim]")
                    else:
                        self._print(f"[yellow]{i:2d}.[/yellow] {song_name}")
                
                self._print("\n[bold cyan]Download Options:[/bold cyan]")
                self._print("  • Press [green]Enter[/green] or type [green]'all'[/green] to download all tracks")
                self._print("  • Type specific numbers (e.g., [yellow]1,3,5[/yellow] or [yellow]1-5[/yellow])")
                self._print("  • Type [red]'cancel'[/red] to abort\n")
                
                choice = input("Your choice: ").strip().lower()
                
                if choice in ['cancel', 'c', 'n', 'no']:
                    self._print("Download cancelled")
                    return None
                elif choice in ['', 'all', 'y', 'yes']:
                    # Download all
                    selected_songs = songs
                else:
                    # Parse selection
                    selected_songs = self._parse_song_selection(choice, songs)
                    if not selected_songs:
                        self._print(Messages.error("Invalid selection"))
                        return None
            else:
                selected_songs = songs
            
            # Ask for quality preference once for all tracks
            if interactive:
                output_format, quality = self.downloader._prompt_audio_format_quality()
            else:
                output_format = 'mp3'
                quality = 'best'
            
            # Download each track
            success_count = 0
            total_selected = len(selected_songs)
            
            for i, song in enumerate(selected_songs, 1):
                try:
                    self._print(f"\n[bold cyan]Track {i}/{total_selected}:[/bold cyan]")
                    
                    song_url = song.get('url', '')
                    if not song_url:
                        self._print(Messages.warning(f"Skipping {song.get('name', 'Unknown')}: No URL"))
                        continue
                    
                    # Ensure full URL
                    if not song_url.startswith('http'):
                        song_url = f"{self.base_url}{song_url}"
                    
                    result = self._download_track(song_url, interactive=False, output_format=output_format, quality=quality)
                    if result:
                        success_count += 1
                    
                except Exception as e:
                    self._print(Messages.error(f"Error downloading track {i}: {e}"))
                    continue
            
            self._print(f"\n[bold green]✓ Album download complete![/bold green]")
            self._print(f"Successfully downloaded {success_count}/{total_selected} tracks")
            
            return True
            
        except Exception as e:
            self._print(Messages.error(f"Error downloading album: {e}"))
            return None
    
    def _download_playlist(self, playlist_url, interactive=True):
        """Download Gaana playlist by downloading all tracks
        
        Args:
            playlist_url: Gaana playlist URL
            interactive: Whether to prompt user for options
            
        Returns:
            True if successful, False/None otherwise
        """
        try:
            self._print(Messages.searching("Fetching playlist metadata from Gaana..."))
            
            playlist_data = self._fetch_playlist_data(playlist_url)
            
            if not playlist_data or not playlist_data.get('songs'):
                self._print(Messages.error("Could not fetch playlist data or no songs found"))
                return None
            
            playlist_name = playlist_data.get('name', 'Unknown Playlist')
            songs = playlist_data['songs']
            
            self._print(f"\n[bold green]{Icons.get('music')} Gaana Playlist:[/bold green] [cyan]{playlist_name}[/cyan]")
            self._print(f"[bold]Total tracks:[/bold] {len(songs)}\n")
            
            # Display song list
            if interactive:
                self._print("[bold cyan]═══ Song List ═══[/bold cyan]")
                for i, song in enumerate(songs, 1):
                    song_name = song.get('name', 'Unknown')
                    artist = song.get('primary_artists', '')
                    if artist:
                        self._print(f"[yellow]{i:2d}.[/yellow] {song_name} [dim]- {artist}[/dim]")
                    else:
                        self._print(f"[yellow]{i:2d}.[/yellow] {song_name}")
                
                self._print("\n[bold cyan]Download Options:[/bold cyan]")
                self._print("  • Press [green]Enter[/green] or type [green]'all'[/green] to download all tracks")
                self._print("  • Type specific numbers (e.g., [yellow]1,3,5[/yellow] or [yellow]1-5[/yellow])")
                self._print("  • Type [red]'cancel'[/red] to abort\n")
                
                choice = input("Your choice: ").strip().lower()
                
                if choice in ['cancel', 'c', 'n', 'no']:
                    self._print("Download cancelled")
                    return None
                elif choice in ['', 'all', 'y', 'yes']:
                    # Download all
                    selected_songs = songs
                else:
                    # Parse selection
                    selected_songs = self._parse_song_selection(choice, songs)
                    if not selected_songs:
                        self._print(Messages.error("Invalid selection"))
                        return None
            else:
                selected_songs = songs
            
            # Ask for quality preference once for all tracks
            if interactive:
                output_format, quality = self.downloader._prompt_audio_format_quality()
            else:
                output_format = 'mp3'
                quality = 'best'
            
            # Download each track
            success_count = 0
            total_selected = len(selected_songs)
            
            for i, song in enumerate(selected_songs, 1):
                try:
                    self._print(f"\n[bold cyan]Track {i}/{total_selected}:[/bold cyan]")
                    
                    song_url = song.get('url', '')
                    if not song_url:
                        self._print(Messages.warning(f"Skipping {song.get('name', 'Unknown')}: No URL"))
                        continue
                    
                    # Ensure full URL
                    if not song_url.startswith('http'):
                        song_url = f"{self.base_url}{song_url}"
                    
                    result = self._download_track(song_url, interactive=False, output_format=output_format, quality=quality)
                    if result:
                        success_count += 1
                    
                except Exception as e:
                    self._print(Messages.error(f"Error downloading track {i}: {e}"))
                    continue
            
            self._print(f"\n[bold green]✓ Playlist download complete![/bold green]")
            self._print(f"Successfully downloaded {success_count}/{total_selected} tracks")
            
            return True
            
        except Exception as e:
            self._print(Messages.error(f"Error downloading playlist: {e}"))
            return None
    
    def _download_artist(self, artist_url, interactive=True):
        """Download songs from Gaana artist page
        
        Args:
            artist_url: Gaana artist URL
            interactive: Whether to prompt user for options
            
        Returns:
            True if successful, False/None otherwise
        """
        try:
            self._print(Messages.info("Fetching artist information from Gaana..."))
            
            if not BEAUTIFULSOUP_AVAILABLE:
                self._print(Messages.error("BeautifulSoup is required for Gaana artist support"))
                return None
            
            response = requests.get(artist_url, headers=self.headers, timeout=15)
            
            if response.status_code != 200:
                self._print(Messages.error(f"Failed to fetch artist page: HTTP {response.status_code}"))
                return None
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract artist name
            artist_name = "Unknown Artist"
            title_tag = soup.find('meta', {'property': 'og:title'})
            if title_tag:
                artist_name = self._decode_html_entities(title_tag.get('content', artist_name))
            
            # Find all song links on artist page
            song_links = soup.find_all('a', href=re.compile(r'/song/[^/]+'))
            songs = []
            seen_urls = set()
            
            for link in song_links:
                song_url = link.get('href', '')
                if song_url and song_url not in seen_urls:
                    if not song_url.startswith('http'):
                        song_url = f"{self.base_url}{song_url}"
                    song_title = self._decode_html_entities(link.get_text(strip=True))
                    if song_title and song_url:
                        songs.append({
                            'name': song_title,
                            'url': song_url
                        })
                        seen_urls.add(song_url)
            
            if not songs:
                self._print(Messages.error("No songs found on artist page"))
                self._print(Messages.info("Try using an album or playlist URL instead"))
                return None
            
            self._print(f"\n[bold green]{Icons.get('music')} Gaana Artist:[/bold green] [cyan]{artist_name}[/cyan]")
            self._print(f"[bold]Total songs found:[/bold] {len(songs)}\n")
            
            # Display song list
            if interactive:
                self._print("[bold cyan]═══ Song List ═══[/bold cyan]")
                for i, song in enumerate(songs, 1):
                    song_name = song.get('name', 'Unknown')
                    self._print(f"[yellow]{i:2d}.[/yellow] {song_name}")
                
                self._print("\n[bold cyan]Download Options:[/bold cyan]")
                self._print("  • Press [green]Enter[/green] or type [green]'all'[/green] to download all tracks")
                self._print("  • Type specific numbers (e.g., [yellow]1,3,5[/yellow] or [yellow]1-5[/yellow])")
                self._print("  • Type [red]'cancel'[/red] to abort\n")
                
                choice = input("Your choice: ").strip().lower()
                
                if choice in ['cancel', 'c', 'n', 'no']:
                    self._print("Download cancelled")
                    return None
                elif choice in ['', 'all', 'y', 'yes']:
                    # Download all
                    selected_songs = songs
                else:
                    # Parse selection
                    selected_songs = self._parse_song_selection(choice, songs)
                    if not selected_songs:
                        self._print(Messages.error("Invalid selection"))
                        return None
            else:
                selected_songs = songs
            
            # Ask for quality preference once for all tracks
            if interactive:
                output_format, quality = self.downloader._prompt_audio_format_quality()
            else:
                output_format = 'mp3'
                quality = 'best'
            
            # Download each song
            success_count = 0
            total_selected = len(selected_songs)
            
            for i, song in enumerate(selected_songs, 1):
                try:
                    self._print(f"\n[bold cyan]Song {i}/{total_selected}:[/bold cyan]")
                    
                    result = self._download_track(song['url'], interactive=False, output_format=output_format, quality=quality)
                    if result:
                        success_count += 1
                    
                except Exception as e:
                    self._print(Messages.error(f"Error downloading song {i}: {e}"))
                    continue
            
            self._print(f"\n[bold green]✓ Artist songs download complete![/bold green]")
            self._print(f"Successfully downloaded {success_count}/{total_selected} songs")
            
            return True
            
        except Exception as e:
            self._print(Messages.error(f"Error downloading artist songs: {e}"))
            return None
    
    def _embed_album_art(self, audio_file, image_url, title, artist, album='', year=''):
        """Embed album art and metadata into audio file
        
        Args:
            audio_file: Path to audio file
            image_url: URL to album art image
            title: Song title
            artist: Artist name
            album: Album name (optional)
            year: Release year (optional)
        """
        try:
            if not MUTAGEN_AVAILABLE:
                return
            
            # Download album art
            response = requests.get(image_url, timeout=10)
            if response.status_code != 200:
                self._print(Messages.warning("Could not download album art"))
                return
            
            album_art_data = response.content
            
            # Get file extension
            file_ext = Path(audio_file).suffix.lower()
            
            # Embed based on file type
            if file_ext == '.mp3':
                audio = MP3(audio_file, ID3=ID3)
                
                # Add ID3 tag if it doesn't exist
                if audio.tags is None:
                    audio.add_tags()
                
                # Add metadata
                audio.tags.add(TIT2(encoding=3, text=title))
                audio.tags.add(TPE1(encoding=3, text=artist))
                if album:
                    audio.tags.add(TALB(encoding=3, text=album))
                if year:
                    audio.tags.add(TDRC(encoding=3, text=str(year)))
                
                # Add album art
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
                
            elif file_ext == '.m4a':
                audio = MP4(audio_file)
                audio['\xa9nam'] = title
                audio['\xa9ART'] = artist
                if album:
                    audio['\xa9alb'] = album
                if year:
                    audio['\xa9day'] = str(year)
                
                audio['covr'] = [MP4Cover(album_art_data, imageformat=MP4Cover.FORMAT_JPEG)]
                audio.save()
                
            elif file_ext == '.flac':
                audio = FLAC(audio_file)
                audio['title'] = title
                audio['artist'] = artist
                if album:
                    audio['album'] = album
                if year:
                    audio['date'] = str(year)
                
                picture = Picture()
                picture.type = 3
                picture.mime = 'image/jpeg'
                picture.desc = 'Cover'
                picture.data = album_art_data
                audio.add_picture(picture)
                audio.save()
            
            self._print(Messages.success("Album art and metadata embedded"))
            
        except Exception as e:
            self._print(Messages.warning(f"Could not embed album art: {e}"))
    
    def _parse_song_selection(self, choice, songs):
        """Parse user's song selection input
        
        Args:
            choice: User input string (e.g., "1,3,5" or "1-5" or "2,4-6,8")
            songs: List of all songs
            
        Returns:
            List of selected songs or None if invalid
        """
        try:
            selected_indices = set()
            
            # Split by comma
            parts = choice.split(',')
            
            for part in parts:
                part = part.strip()
                
                # Check if it's a range (e.g., "1-5")
                if '-' in part:
                    start, end = part.split('-', 1)
                    start = int(start.strip())
                    end = int(end.strip())
                    
                    if start < 1 or end > len(songs) or start > end:
                        self._print(Messages.error(f"Invalid range: {part}"))
                        return None
                    
                    selected_indices.update(range(start - 1, end))
                else:
                    # Single number
                    num = int(part)
                    if num < 1 or num > len(songs):
                        self._print(Messages.error(f"Invalid song number: {num}"))
                        return None
                    selected_indices.add(num - 1)
            
            # Get selected songs
            selected_songs = [songs[i] for i in sorted(selected_indices)]
            
            self._print(f"\n[green]✓ Selected {len(selected_songs)} song(s)[/green]\n")
            return selected_songs
            
        except ValueError:
            self._print(Messages.error("Invalid input format. Use numbers like: 1,3,5 or 1-5"))
            return None
        except Exception as e:
            self._print(Messages.error(f"Error parsing selection: {e}"))
            return None
    
    def _find_recently_downloaded_file(self):
        """Find the most recently downloaded audio file in output directory
        
        Returns:
            Path to most recent audio file or None
        """
        try:
            audio_extensions = ['.mp3', '.m4a', '.flac', '.opus', '.ogg', '.wav', '.webm']
            
            # Get the current output directory from downloader
            if hasattr(self.downloader, 'output_dir'):
                output_dir = Path(self.downloader.output_dir)
            else:
                output_dir = Path.home() / 'Downloads' / 'UltimateDownloader'
            
            if not output_dir.exists():
                return None
            
            audio_files = []
            # Search recursively in output directory and subdirectories
            for ext in audio_extensions:
                audio_files.extend(output_dir.rglob(f'*{ext}'))
            
            if not audio_files:
                return None
            
            # Return the most recently modified file
            most_recent = max(audio_files, key=lambda p: p.stat().st_mtime)
            return str(most_recent)
            
        except Exception:
            return None
    
    def _print(self, message):
        """Print message using rich console if available, otherwise regular print
        
        Args:
            message: Message to print
        """
        if RICH_AVAILABLE and self.console:
            self.console.print(message)
        else:
            # Strip rich markup for plain printing
            import re
            plain_message = re.sub(r'\[.*?\]', '', str(message))
            print(plain_message)
