#!/usr/bin/env python3
"""
JioSaavn Handler Module
Handles all JioSaavn-related functionality including downloading tracks, albums, 
playlists, and artists with metadata extraction and YouTube search fallback.
Uses JioSaavn unofficial API for fetching song metadata.
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


class JioSaavnHandler:
    """Handles JioSaavn downloads and metadata extraction"""
    
    def __init__(self, downloader):
        """Initialize JioSaavn handler with reference to main downloader
        
        Args:
            downloader: Reference to UltimateMediaDownloader instance
        """
        self.downloader = downloader
        self.console = Console() if RICH_AVAILABLE else None
        
        # JioSaavn official API endpoints
        self.search_base_url = "https://www.jiosaavn.com/api.php?__call=autocomplete.get&_format=json&_marker=0&cc=in&includeMetaTags=1&query="
        self.song_details_base_url = "https://www.jiosaavn.com/api.php?__call=song.getDetails&cc=in&_marker=0%3F_marker%3D0&_format=json&pids="
        self.album_details_base_url = "https://www.jiosaavn.com/api.php?__call=content.getAlbumDetails&_format=json&cc=in&_marker=0%3F_marker%3D0&albumid="
        self.playlist_details_base_url = "https://www.jiosaavn.com/api.php?__call=playlist.getDetails&_format=json&cc=in&_marker=0%3F_marker%3D0&listid="
        self.lyrics_base_url = "https://www.jiosaavn.com/api.php?__call=lyrics.getLyrics&ctx=web6dot0&api_version=4&_format=json&_marker=0%3F_marker%3D0&lyrics_id="
        
        # Fallback API
        self.fallback_api = "https://jiosaavn-api-privatecvc.vercel.app"
    
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
        
    def search_and_download(self, jiosaavn_url, interactive=True):
        """Enhanced JioSaavn downloader with multiple strategies
        
        Args:
            jiosaavn_url: URL to JioSaavn content
            interactive: Whether to prompt user for options
            
        Returns:
            True if successful, False/None otherwise
        """
        print(f"♪ Processing JioSaavn URL: {jiosaavn_url}")
        
        try:
            # Determine JioSaavn content type
            if '/song/' in jiosaavn_url:
                return self._download_track(jiosaavn_url, interactive=interactive)
            elif '/album/' in jiosaavn_url:
                return self._download_album(jiosaavn_url, interactive=interactive)
            elif '/playlist/' in jiosaavn_url or '/featured/' in jiosaavn_url:
                return self._download_playlist(jiosaavn_url, interactive=interactive)
            elif '/artist/' in jiosaavn_url:
                return self._download_artist(jiosaavn_url, interactive=interactive)
            else:
                self._print(Messages.error("Unknown JioSaavn URL format"))
                return None
                
        except Exception as e:
            self._print(Messages.error(f"Error processing JioSaavn URL: {e}"))
            return None
    
    def _fetch_song_data(self, song_url):
        """Fetch song data from JioSaavn API
        
        Args:
            song_url: JioSaavn song URL or song ID
            
        Returns:
            Dictionary containing song metadata or None
        """
        try:
            # Extract song slug/ID from URL
            song_slug = self._extract_id_from_url(song_url)
            if not song_slug:
                self._print(Messages.error("Could not extract song identifier from URL"))
                return None
            
            self._print(f"[dim]Extracted identifier: {song_slug}[/dim]")
            
            # JioSaavn URLs contain a slug (like ICERW0MFfQs) which is NOT the actual song ID
            # The actual song ID (like PIzj75J8) is different and needs to be looked up
            
            # Method 1: Try to extract song name from URL and search
            if song_url.startswith('http') and '/song/' in song_url:
                # Extract song name from URL path
                parts = song_url.split('/song/')[1].split('/')
                if len(parts) >= 1:
                    song_name = parts[0].replace('-', ' ').strip()
                    self._print(f"[dim]Searching for: {song_name}[/dim]")
                    
                    # Search for the song
                    search_results = self._search_jiosaavn(song_name)
                    if search_results and len(search_results) > 0:
                        # Find the song that matches the URL slug
                        for song in search_results:
                            if song.get('url') and song_slug in song['url']:
                                # Found the matching song, now get full details
                                real_song_id = song.get('id')
                                self._print(f"[dim]Found song ID: {real_song_id}[/dim]")
                                return self._fetch_song_by_id(real_song_id)
                        
                        # If no exact match, return the first result
                        self._print(Messages.info("Using best match from search"))
                        first_song = search_results[0]
                        real_song_id = first_song.get('id')
                        return self._fetch_song_by_id(real_song_id)
            
            # Method 2: Try direct ID fetch (in case it's actually an ID)
            song_data = self._fetch_song_by_id(song_slug)
            if song_data:
                return song_data
            
            # Method 3: Try web scraping as fallback
            self._print(Messages.info("Trying web scraping method..."))
            return self._scrape_song_data(song_url, song_slug)
            
        except Exception as e:
            self._print(Messages.warning(f"API fetch error: {e}"))
            import traceback
            if self.downloader.verbose:
                self._print(f"[dim]{traceback.format_exc()}[/dim]")
            return None
    
    def _fetch_song_by_id(self, song_id):
        """Fetch song details using the actual JioSaavn song ID
        
        Args:
            song_id: The actual JioSaavn song ID (like PIzj75J8)
            
        Returns:
            Dictionary containing song metadata or None
        """
        try:
            api_url = f"{self.song_details_base_url}{song_id}"
            
            response = requests.get(
                api_url,
                timeout=10,
                headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                    'Accept': 'application/json',
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Referer': 'https://www.jiosaavn.com/'
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # JioSaavn API returns songs as a dict with song_id as key
                if isinstance(data, dict) and song_id in data:
                    return data[song_id]
                
                # Try to find any song data in the response
                for key, value in data.items():
                    if isinstance(value, dict) and value.get('id'):
                        return value
            
            return None
            
        except Exception as e:
            self._print(Messages.warning(f"Error fetching song by ID: {e}"))
            return None
    
    def _scrape_song_data(self, song_url, song_id=None):
        """Scrape song data from JioSaavn page when API fails
        
        Args:
            song_url: JioSaavn song URL
            song_id: Optional pre-extracted song ID
            
        Returns:
            Dictionary with basic song info or None
        """
        try:
            if not BEAUTIFULSOUP_AVAILABLE:
                self._print(Messages.warning("BeautifulSoup not available for scraping"))
                return None
            
            # Ensure we have a full URL
            if not song_url.startswith('http'):
                song_url = f"https://www.jiosaavn.com/song/{song_id}/{song_id}"
            
            response = requests.get(
                song_url,
                timeout=10,
                headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'Accept': 'text/html,application/xhtml+xml',
                    'Accept-Language': 'en-US,en;q=0.9'
                }
            )
            
            if response.status_code != 200:
                return None
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Try to extract from meta tags
            song_data = {}
            
            # Title
            title_tag = soup.find('meta', {'property': 'og:title'}) or soup.find('title')
            if title_tag:
                song_data['name'] = title_tag.get('content', title_tag.text).split('|')[0].strip()
            
            # Image
            image_tag = soup.find('meta', {'property': 'og:image'})
            if image_tag:
                song_data['image'] = image_tag.get('content', '')
            
            # Description (might contain artist info)
            desc_tag = soup.find('meta', {'property': 'og:description'})
            if desc_tag:
                desc = desc_tag.get('content', '')
                # Try to extract artist from description
                if ' - ' in desc:
                    parts = desc.split(' - ')
                    if len(parts) >= 2:
                        song_data['primary_artists'] = parts[0].strip()
                        song_data['name'] = parts[1].split('.')[0].strip()
            
            # Try to find structured data
            script_tags = soup.find_all('script', type='application/ld+json')
            for script in script_tags:
                try:
                    json_data = json.loads(script.string)
                    if isinstance(json_data, dict):
                        if json_data.get('@type') == 'MusicRecording':
                            song_data['name'] = json_data.get('name', song_data.get('name', ''))
                            if 'byArtist' in json_data:
                                artist_data = json_data['byArtist']
                                if isinstance(artist_data, dict):
                                    song_data['primary_artists'] = artist_data.get('name', '')
                                elif isinstance(artist_data, list) and len(artist_data) > 0:
                                    song_data['primary_artists'] = ', '.join([a.get('name', '') for a in artist_data if isinstance(a, dict)])
                            break
                except:
                    continue
            
            if song_data.get('name'):
                return song_data
            
            return None
            
        except Exception as e:
            self._print(Messages.warning(f"Scraping error: {e}"))
            return None
    
    def _fetch_album_data(self, album_url):
        """Fetch album data from JioSaavn API
        
        Args:
            album_url: JioSaavn album URL or album ID
            
        Returns:
            Dictionary containing album metadata and songs or None
        """
        try:
            # Extract album slug/ID from URL
            album_slug = self._extract_id_from_url(album_url)
            if not album_slug:
                return None
            
            self._print(f"[dim]Extracted identifier: {album_slug}[/dim]")
            
            # Try to get album name from URL and search for it
            if album_url.startswith('http') and '/album/' in album_url:
                # Extract album name from URL path
                parts = album_url.split('/album/')[1].split('/')
                if len(parts) >= 1:
                    album_name = parts[0].replace('-', ' ').strip()
                    self._print(f"[dim]Searching for: {album_name}[/dim]")
                    
                    # Search for albums
                    search_url = "https://www.jiosaavn.com/api.php?__call=autocomplete.get&_format=json&_marker=0&cc=in&includeMetaTags=1&query="
                    response = requests.get(
                        f"{search_url}{requests.utils.quote(album_name)}",
                        timeout=10,
                        headers={
                            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                            'Accept': 'application/json'
                        }
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        # Check for albums in search results
                        if 'albums' in data and 'data' in data['albums']:
                            albums = data['albums']['data']
                            if albums:
                                # Find matching album
                                for album in albums:
                                    if album.get('url') and album_slug in album['url']:
                                        real_album_id = album.get('id')
                                        self._print(f"[dim]Found album ID: {real_album_id}[/dim]")
                                        return self._fetch_album_by_id(real_album_id)
                                
                                # Use first result if no exact match
                                first_album = albums[0]
                                real_album_id = first_album.get('id')
                                self._print(f"[dim]Using album ID: {real_album_id}[/dim]")
                                return self._fetch_album_by_id(real_album_id)
            
            # Try direct ID fetch
            album_data = self._fetch_album_by_id(album_slug)
            if album_data:
                return album_data
            
            return None
            
        except Exception as e:
            self._print(Messages.warning(f"API fetch error: {e}"))
            if self.downloader.verbose:
                import traceback
                self._print(f"[dim]{traceback.format_exc()}[/dim]")
            return None
    
    def _fetch_album_by_id(self, album_id):
        """Fetch album details using the actual JioSaavn album ID
        
        Args:
            album_id: The actual JioSaavn album ID
            
        Returns:
            Dictionary containing album metadata and songs or None
        """
        try:
            response = requests.get(
                f"{self.album_details_base_url}{album_id}",
                timeout=15,
                headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                    'Accept': 'application/json',
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Referer': 'https://www.jiosaavn.com/'
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                # JioSaavn returns album data directly
                if isinstance(data, dict) and (data.get('id') or data.get('songs')):
                    return data
            
            return None
            
        except Exception as e:
            self._print(Messages.warning(f"Error fetching album by ID: {e}"))
            return None
    
    def _fetch_playlist_data(self, playlist_url):
        """Fetch playlist data from JioSaavn API
        
        Args:
            playlist_url: JioSaavn playlist URL or playlist ID
            
        Returns:
            Dictionary containing playlist metadata and songs or None
        """
        try:
            # Extract playlist slug/ID from URL
            playlist_slug = self._extract_id_from_url(playlist_url)
            if not playlist_slug:
                return None
            
            self._print(f"[dim]Extracted identifier: {playlist_slug}[/dim]")
            
            # Try to get playlist name from URL and search for it
            if playlist_url.startswith('http') and ('/playlist/' in playlist_url or '/featured/' in playlist_url):
                # Extract playlist name from URL path
                url_part = playlist_url.split('/playlist/')[-1] if '/playlist/' in playlist_url else playlist_url.split('/featured/')[-1]
                parts = url_part.split('/')
                if len(parts) >= 1:
                    playlist_name = parts[0].replace('-', ' ').strip()
                    self._print(f"[dim]Searching for: {playlist_name}[/dim]")
                    
                    # Try searching for playlists
                    search_url = "https://www.jiosaavn.com/api.php?__call=autocomplete.get&_format=json&_marker=0&cc=in&includeMetaTags=1&query="
                    response = requests.get(
                        f"{search_url}{requests.utils.quote(playlist_name)}",
                        timeout=10,
                        headers={
                            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                            'Accept': 'application/json'
                        }
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        # Check for playlists in search results
                        if 'playlists' in data and 'data' in data['playlists']:
                            playlists = data['playlists']['data']
                            if playlists:
                                # Find matching playlist
                                for playlist in playlists:
                                    if playlist.get('url') and playlist_slug in playlist['url']:
                                        real_playlist_id = playlist.get('id')
                                        self._print(f"[dim]Found playlist ID: {real_playlist_id}[/dim]")
                                        return self._fetch_playlist_by_id(real_playlist_id)
                                
                                # Use first result if no exact match
                                first_playlist = playlists[0]
                                real_playlist_id = first_playlist.get('id')
                                self._print(f"[dim]Using playlist ID: {real_playlist_id}[/dim]")
                                return self._fetch_playlist_by_id(real_playlist_id)
            
            # Try direct ID fetch
            playlist_data = self._fetch_playlist_by_id(playlist_slug)
            if playlist_data:
                return playlist_data
            
            # Try web scraping
            self._print(Messages.info("Trying web scraping method..."))
            return self._scrape_playlist_data(playlist_url)
            
        except Exception as e:
            self._print(Messages.warning(f"API fetch error: {e}"))
            if self.downloader.verbose:
                import traceback
                self._print(f"[dim]{traceback.format_exc()}[/dim]")
            return None
    
    def _fetch_playlist_by_id(self, playlist_id):
        """Fetch playlist details using the actual JioSaavn playlist ID
        
        Args:
            playlist_id: The actual JioSaavn playlist ID
            
        Returns:
            Dictionary containing playlist metadata and songs or None
        """
        try:
            response = requests.get(
                f"{self.playlist_details_base_url}{playlist_id}",
                timeout=15,
                headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                    'Accept': 'application/json',
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Referer': 'https://www.jiosaavn.com/'
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                # JioSaavn returns playlist data directly
                if isinstance(data, dict) and (data.get('id') or data.get('songs') or data.get('list')):
                    return data
            
            return None
            
        except Exception as e:
            self._print(Messages.warning(f"Error fetching playlist by ID: {e}"))
            return None
    
    def _scrape_playlist_data(self, playlist_url):
        """Scrape playlist data from JioSaavn page when API fails
        
        Args:
            playlist_url: JioSaavn playlist URL
            
        Returns:
            Dictionary with basic playlist info or None
        """
        try:
            if not BEAUTIFULSOUP_AVAILABLE:
                return None
            
            response = requests.get(
                playlist_url,
                timeout=10,
                headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                    'Accept': 'text/html'
                }
            )
            
            if response.status_code != 200:
                return None
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Try to extract playlist name
            title_tag = soup.find('meta', {'property': 'og:title'})
            if title_tag:
                playlist_name = title_tag.get('content', 'Unknown Playlist').split('|')[0].strip()
                # Return minimal data, will need to search for songs
                return {'name': playlist_name, 'songs': []}
            
            return None
            
        except Exception:
            return None
    
    def _search_jiosaavn(self, query):
        """Search JioSaavn for songs
        
        Args:
            query: Search query string
            
        Returns:
            List of search results or None
        """
        try:
            # Use official JioSaavn search API
            response = requests.get(
                f"{self.search_base_url}{requests.utils.quote(query)}",
                timeout=10,
                headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                    'Accept': 'application/json'
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                # JioSaavn search returns songs in 'songs' or 'data' field
                if isinstance(data, dict):
                    songs = data.get('songs', {}).get('data', [])
                    if songs:
                        return songs
                    # Alternative response format
                    if data.get('data'):
                        return data['data']
            
            return None
            
        except Exception as e:
            self._print(Messages.warning(f"Search error: {e}"))
            return None
    
    def _extract_id_from_url(self, url):
        """Extract ID from JioSaavn URL
        
        Args:
            url: JioSaavn URL or ID
            
        Returns:
            Extracted ID or original string if already an ID
        """
        try:
            # If it's already just an ID, return it
            if not url.startswith('http'):
                return url
            
            # Extract ID from URL
            # JioSaavn URLs format: https://www.jiosaavn.com/song/name/ID
            # or https://www.jiosaavn.com/album/name/ID
            # ID is the last part after the last /
            
            # Remove query parameters first
            url = url.split('?')[0]
            
            # Get the last part of the URL
            parts = url.rstrip('/').split('/')
            if len(parts) > 0:
                potential_id = parts[-1]
                if potential_id:
                    return potential_id
            
            return None
            
        except Exception as e:
            self._print(Messages.warning(f"Error extracting ID: {e}"))
            return None
    
    def _download_track(self, song_url, interactive=True):
        """Download single JioSaavn track by searching on YouTube
        
        Args:
            song_url: JioSaavn song URL
            interactive: Whether to prompt user for options
            
        Returns:
            True if successful, False/None otherwise
        """
        try:
            self._print(Messages.searching("Fetching song metadata from JioSaavn..."))
            
            song_data = self._fetch_song_data(song_url)
            
            if not song_data:
                self._print(Messages.error("Could not fetch song data from JioSaavn"))
                return None
            
            # Extract song information
            title = self._decode_html_entities(song_data.get('name') or song_data.get('title') or song_data.get('song', 'Unknown'))
            artists = self._decode_html_entities(song_data.get('artists') or song_data.get('singers') or song_data.get('primary_artists', 'Unknown Artist'))
            
            # Handle artist list format
            if isinstance(artists, list):
                artists = ', '.join([self._decode_html_entities(a.get('name', str(a))) if isinstance(a, dict) else self._decode_html_entities(str(a)) for a in artists])
            elif isinstance(artists, dict):
                artists = self._decode_html_entities(artists.get('primary', 'Unknown Artist'))
            
            album = self._decode_html_entities(song_data.get('album') or song_data.get('album_name', ''))
            if isinstance(album, dict):
                album = album.get('name', '')
            
            year = song_data.get('year') or song_data.get('release_date', '')
            image_url = song_data.get('image') or song_data.get('image_url', '')
            
            # Get highest quality image if available
            if isinstance(image_url, list) and len(image_url) > 0:
                image_url = image_url[-1].get('link', '') if isinstance(image_url[-1], dict) else str(image_url[-1])
            
            search_query = f"{title} - {artists}"
            
            self._print(f"[bold green]{Icons.get('music')} JioSaavn Track:[/bold green] [cyan]{search_query}[/cyan]")
            if album:
                self._print(f"[dim]Album: {album}[/dim]")
            if year:
                self._print(f"[dim]Year: {year}[/dim]")
            
            # Ask for quality preference
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
                
                # Embed album art from JioSaavn if available
                if result and image_url and MUTAGEN_AVAILABLE:
                    downloaded_file = self._find_recently_downloaded_file()
                    if downloaded_file:
                        self._embed_album_art(downloaded_file, image_url, title, artists, album, year)
                
                return result
            else:
                self._print(Messages.error("Could not find track on YouTube"))
                return None
                
        except Exception as e:
            self._print(Messages.error(f"Error downloading JioSaavn track: {e}"))
            return None
    
    def _search_youtube_with_scoring(self, search_query, title, artists):
        """Search YouTube and pick the best match based on view count and likes
        
        Searches for top 5 results and selects the most relevant video based on:
        - View count
        - Like count
        - Engagement ratio (likes/views)
        - Title similarity
        
        Args:
            search_query: Full search query (format: "Title - Artist")
            title: Song title
            artists: Artist names
            
        Returns:
            Best matching YouTube URL or None
        """
        # Clean the title by removing (From "...") parts and extra info
        clean_title = re.sub(r'\(From ["\'].*?["\']\)', '', title).strip()
        clean_title = re.sub(r'\s*-\s*(Hindi|English|Tamil|Telugu|Malayalam|Kannada|Bengali|Punjabi|Marathi)\s*$', '', clean_title, flags=re.IGNORECASE).strip()
        
        # Try multiple search query variations with cleaned title
        search_queries = [
            f"{clean_title} {artists} official audio",  # Most specific first
            f"{clean_title} {artists} lyric video",
            f"{clean_title} {artists} audio",
            f"{clean_title} {artists}",  # Without any suffix
            search_query,  # Original: "Title - Artist"
            f"{title} {artists} official",  # Original title with official tag
        ]
        
        for attempt, query in enumerate(search_queries, 1):
            try:
                if attempt > 1:
                    self._print(f"[dim]⟳ Retry {attempt}/{len(search_queries)}: Trying '{query}'...[/dim]")
                
                # Search for multiple results
                if hasattr(self.downloader, '_search_youtube_multiple'):
                    results = self.downloader._search_youtube_multiple(query, max_results=5)
                    
                    if results and len(results) > 0:
                        if attempt == 1:  # Only show detailed info for first attempt
                            print(f"Found {len(results)} results, analyzing...")
                        
                        best_url = self._pick_best_youtube_result(results, clean_title, artists, attempt == 1)
                        
                        if best_url:
                            return best_url
                        
                        # Don't fallback to first result - try next query instead
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
            
            # Keywords that indicate bad matches
            bad_keywords = ['shorts', 'short video', 'ytshorts', 'tiktok', 'dance', 'status', 
                           'whatsapp status', 'viral', 'remix', 'cover', 'reaction', 'review',
                           'instrumental', 'karaoke', 'ringtone', 'bgm', 'mashup']
            
            for url in youtube_urls:
                try:
                    ydl_opts = {
                        'quiet': True,
                        'no_warnings': True,
                        'extract_flat': False,
                        'skip_download': True,
                    }
                    
                    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                        info = ydl.extract_info(url, download=False)
                        
                        if not info:
                            continue
                        
                        video_title = info.get('title', '').lower()
                        duration = info.get('duration') or 0
                        view_count = info.get('view_count') or 0
                        like_count = info.get('like_count') or 0
                        channel = info.get('uploader', '').lower()
                        
                        # Filter out shorts and very short videos (less than 60 seconds)
                        if duration < 60:
                            if show_details:
                                print(f"    ✗ Skipped (too short): {info.get('title', '')[:50]}...")
                            continue
                        
                        # Filter out bad keywords
                        if any(keyword in video_title for keyword in bad_keywords):
                            if show_details:
                                print(f"    ✗ Skipped (unwanted content): {info.get('title', '')[:50]}...")
                            continue
                        
                        # Calculate title similarity score (0-100)
                        title_words = set(title_lower.split())
                        video_words = set(video_title.split())
                        
                        # Check if key words from title are in video title
                        matching_words = title_words & video_words
                        title_match_score = (len(matching_words) / len(title_words) * 100) if title_words else 0
                        
                        # Check if artist name is in video title
                        artist_match = 50 if artists_lower and artists_lower in video_title else 0
                        
                        # Bonus for official channels
                        official_channels = [
                        "t-series","t-series bollywood","sony music india","zee music company",
                        "saregama music","tips official","venus music","eros now music",
                        "yrf music","dharma productions music","jio studios music",
                        "times music","panorama music","lahari music","aditya music",
                        "aditya music tamil","aditya music telugu","think music india",
                        "white hill music","desi music factory","hombale music",
                        "aanand audio","junglee music","saregama south","sony music south",
                        "zee music south","t-series south","sun tv music",
                        "speed records","white hill music","t-series apna punjab",
                        "lokdhun punjabi","amar audio","finetone music",
                        "mad4music","humble music","desi crew official",
                        "brown town music","vehli janta records","rebel records",
                        "single track studio","jass records","tips punjabi",
                        "zee music punjabi","sony music punjabi",
                        "sony music","vevo","universal music group","warner music group",
                        "atlantic records","interscope records","republic records",
                        "def jam recordings","capitol records","island records",
                        "columbia records","motown records","epic records",
                        "rca records","virgin music","polydor records",
                        "arijit singh","atif aslam","armaan malik","shreya ghoshal",
                        "neha kakkar","jubin nautiyal","b praak","guru randhawa",
                        "badshah","yo yo honey singh","sidhu moose wala",
                        "diljit dosanjh","karan aujla","ap dhillon","shubh",
                        "billie eilish","taylor swift","ed sheeran","drake",
                        "the weeknd","dua lipa","ariana grande","eminem","coldplay"
                        ]

                        channel_bonus = 30 if any(ch in channel for ch in official_channels) else 0
                        
                        # Calculate engagement score
                        engagement_ratio = (like_count / view_count * 100) if view_count > 0 else 0
                        
                        # Composite scoring:
                        # 1. Title match (0-100 points)
                        # 2. Artist match (0-50 points)
                        # 3. Channel bonus (0-30 points)
                        # 4. View count (normalized, max 100 points)
                        # 5. Engagement bonus (0-50 points)
                        
                        view_score = min(view_count / 100000, 100)  # Normalize views
                        engagement_score = min(engagement_ratio * 10, 50)  # Cap at 50 points
                        
                        score = (title_match_score * 2) + artist_match + channel_bonus + view_score + engagement_score
                        
                        # Require minimum title match of 30% to be considered
                        if title_match_score < 30:
                            if show_details:
                                print(f"    ✗ Low relevance ({title_match_score:.0f}%): {info.get('title', '')[:50]}...")
                            continue
                        
                        if show_details:
                            view_str = f"{view_count:,}" if isinstance(view_count, (int, float)) else "N/A"
                            like_str = f"{like_count:,}" if isinstance(like_count, (int, float)) else "N/A"
                            print(f"    ▤ Views: {view_str} | Likes: {like_str} ({engagement_ratio:.2f}%) | {info.get('title', '')[:50]}...")
                        
                        if score > best_score:
                            best_score = score
                            best_url = url
                        
                except Exception as e:
                    if show_details:
                        print(f"    ⚠  Error analyzing result: {e}")
                    continue
            
            if best_url and show_details:
                print(f"Selected best match based on engagement metrics")
            
            return best_url
            
        except Exception as e:
            self._print(Messages.warning(f"Error picking best result: {e}"))
            return None
    
    def _download_album(self, album_url, interactive=True):
        """Download JioSaavn album by searching each track on YouTube
        
        Args:
            album_url: JioSaavn album URL
            interactive: Whether to prompt user for options
            
        Returns:
            True if successful, False/None otherwise
        """
        try:
            self._print(Messages.searching("Fetching album data from JioSaavn..."))
            
            album_data = self._fetch_album_data(album_url)
            
            if not album_data:
                self._print(Messages.error("Could not fetch album data from JioSaavn"))
                return None
            
            # Extract album information
            album_name = album_data.get('name') or album_data.get('title') or album_data.get('album', 'Unknown Album')
            artist_name = album_data.get('artists') or album_data.get('primary_artists', 'Unknown Artist')
            
            # Handle artist format
            if isinstance(artist_name, list):
                artist_name = ', '.join([a.get('name', str(a)) if isinstance(a, dict) else str(a) for a in artist_name])
            elif isinstance(artist_name, dict):
                artist_name = artist_name.get('primary', 'Unknown Artist')
            
            songs = album_data.get('songs') or album_data.get('list') or []
            
            self._print(f"[bold magenta]{Icons.get('music')} JioSaavn Album:[/bold magenta] [cyan]{artist_name} - {album_name}[/cyan]")
            self._print(Messages.info(f"Total tracks: {len(songs)}"))
            
            if not songs:
                self._print(Messages.error("No songs found in album"))
                return None
            
            # Prompt for audio format and quality
            if interactive:
                output_format, quality = self.downloader._prompt_audio_format_quality()
            else:
                output_format = 'mp3'
                quality = 'best'
            
            # Create album directory
            safe_album_name = sanitize_filename(f"{artist_name} - {album_name}")
            album_dir = self.downloader.output_dir / safe_album_name
            album_downloader = self.downloader.__class__(album_dir)
            
            successful_downloads = 0
            
            for i, song in enumerate(songs, 1):
                try:
                    title = self._decode_html_entities(song.get('name') or song.get('title') or song.get('song', 'Unknown'))
                    artists = song.get('artists') or song.get('singers') or song.get('primary_artists', artist_name)
                    
                    # Handle artist format
                    if isinstance(artists, list):
                        artists = ', '.join([self._decode_html_entities(a.get('name', str(a))) if isinstance(a, dict) else self._decode_html_entities(str(a)) for a in artists])
                    elif isinstance(artists, dict):
                        artists = self._decode_html_entities(artists.get('primary', artist_name))
                    else:
                        artists = self._decode_html_entities(str(artists))
                    
                    search_query = f"{title} - {artists}"
                    
                    self._print(f"\n[bold blue]{Icons.get('music')} [{i:2d}/{len(songs)}][/bold blue] [cyan]{search_query}[/cyan]")
                    
                    youtube_url = self._search_youtube_with_scoring(search_query, title, artists)
                    if youtube_url:
                        filename_format = f"{artists} - {title}"
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
                            
                            # Embed album art
                            image_url = song.get('image') or song.get('image_url', '')
                            if isinstance(image_url, list) and len(image_url) > 0:
                                image_url = image_url[-1].get('link', '') if isinstance(image_url[-1], dict) else str(image_url[-1])
                            
                            if image_url and MUTAGEN_AVAILABLE:
                                downloaded_file = self._find_recently_downloaded_file()
                                if downloaded_file:
                                    year = song.get('year', '')
                                    self._embed_album_art(downloaded_file, image_url, title, artists, album_name, year)
                    else:
                        self._print(Messages.error(f"Could not find: {title}"))
                        
                except Exception as e:
                    self._print(Messages.error(f"Error downloading {title}: {e}"))
            
            print(f"\n✓ Album download completed: {successful_downloads}/{len(songs)} tracks downloaded")
            return successful_downloads > 0
            
        except Exception as e:
            self._print(Messages.error(f"Error downloading JioSaavn album: {e}"))
            return None
    
    def _download_playlist(self, playlist_url, interactive=True):
        """Download JioSaavn playlist by searching each track on YouTube
        
        Args:
            playlist_url: JioSaavn playlist URL
            interactive: Whether to prompt user for options
            
        Returns:
            True if successful, False/None otherwise
        """
        try:
            self._print(Messages.searching("Fetching playlist data from JioSaavn..."))
            
            playlist_data = self._fetch_playlist_data(playlist_url)
            
            if not playlist_data:
                self._print(Messages.error("Could not fetch playlist data from JioSaavn"))
                return None
            
            # Extract playlist information
            playlist_name = playlist_data.get('name') or playlist_data.get('title') or playlist_data.get('listname', 'Unknown Playlist')
            songs = playlist_data.get('songs') or playlist_data.get('list') or []
            
            print(f"≡ JioSaavn Playlist: {playlist_name}")
            print(f"▤ Total tracks: {len(songs)}")
            
            if not songs:
                self._print(Messages.error("No songs found in playlist"))
                return None
            
            # Convert to track list format
            track_list = []
            for song in songs:
                title = self._decode_html_entities(song.get('name') or song.get('title') or song.get('song', 'Unknown'))
                artists = song.get('artists') or song.get('singers') or song.get('primary_artists', 'Unknown Artist')
                
                # Handle artist format
                if isinstance(artists, list):
                    artists = ', '.join([self._decode_html_entities(a.get('name', str(a))) if isinstance(a, dict) else self._decode_html_entities(str(a)) for a in artists])
                elif isinstance(artists, dict):
                    artists = self._decode_html_entities(artists.get('primary', 'Unknown Artist'))
                else:
                    artists = self._decode_html_entities(str(artists))
                
                track_list.append(f"{title} - {artists}")
            
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
                    selected_songs = songs
                else:
                    # Filter selected songs based on indices
                    indices = [track_list.index(track) for track in choice if track in track_list]
                    selected_tracks = choice
                    selected_songs = [songs[i] for i in indices]
                
                # Prompt for audio format and quality
                output_format, quality = self.downloader._prompt_audio_format_quality()
            else:
                selected_tracks = track_list
                selected_songs = songs
                output_format = 'mp3'
                quality = 'best'
            
            print(f"\n♫ Starting download of {len(selected_tracks)} track(s)...")
            
            # Create playlist directory
            safe_playlist_name = sanitize_filename(f"JioSaavn - {playlist_name}")
            playlist_dir = self.downloader.output_dir / safe_playlist_name
            playlist_downloader = self.downloader.__class__(playlist_dir)
            
            successful_downloads = 0
            
            for i, (track_name, song) in enumerate(zip(selected_tracks, selected_songs), 1):
                try:
                    self._print(f"\n[bold blue]{Icons.get('music')} [{i:2d}/{len(selected_tracks)}][/bold blue] [cyan]{track_name}[/cyan]")
                    
                    # Extract title and artists for scoring
                    title = self._decode_html_entities(song.get('name') or song.get('title') or song.get('song', 'Unknown'))
                    artists_data = song.get('artists') or song.get('singers') or song.get('primary_artists', 'Unknown Artist')
                    
                    if isinstance(artists_data, list):
                        artists_str = ', '.join([self._decode_html_entities(a.get('name', str(a))) if isinstance(a, dict) else self._decode_html_entities(str(a)) for a in artists_data])
                    elif isinstance(artists_data, dict):
                        artists_str = self._decode_html_entities(artists_data.get('primary', 'Unknown Artist'))
                    else:
                        artists_str = self._decode_html_entities(str(artists_data))
                    
                    youtube_url = self._search_youtube_with_scoring(track_name, title, artists_str)
                    if youtube_url:
                        # Extract title and artists for filename
                        title = self._decode_html_entities(song.get('name') or song.get('title') or song.get('song', 'Unknown'))
                        artists = song.get('artists') or song.get('singers') or song.get('primary_artists', 'Unknown Artist')
                        
                        if isinstance(artists, list):
                            artists = ', '.join([self._decode_html_entities(a.get('name', str(a))) if isinstance(a, dict) else self._decode_html_entities(str(a)) for a in artists])
                        elif isinstance(artists, dict):
                            artists = self._decode_html_entities(artists.get('primary', 'Unknown Artist'))
                        else:
                            artists = self._decode_html_entities(str(artists))
                        
                        filename_format = f"{artists} - {title}"
                        
                        result = playlist_downloader.download_media(
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
                            
                            # Embed album art
                            image_url = song.get('image') or song.get('image_url', '')
                            if isinstance(image_url, list) and len(image_url) > 0:
                                image_url = image_url[-1].get('link', '') if isinstance(image_url[-1], dict) else str(image_url[-1])
                            
                            if image_url and MUTAGEN_AVAILABLE:
                                downloaded_file = self._find_recently_downloaded_file()
                                if downloaded_file:
                                    album = song.get('album', '')
                                    if isinstance(album, dict):
                                        album = album.get('name', '')
                                    year = song.get('year', '')
                                    self._embed_album_art(downloaded_file, image_url, title, artists, album, year)
                    else:
                        self._print(Messages.error(f"Could not find on YouTube"))
                        
                except Exception as e:
                    self._print(Messages.error(f"Error downloading track: {e}"))
            
            print(f"\n✓ Playlist download completed: {successful_downloads}/{len(selected_tracks)} tracks downloaded")
            return successful_downloads > 0
            
        except Exception as e:
            self._print(Messages.error(f"Error downloading JioSaavn playlist: {e}"))
            return None
    
    def _download_artist(self, artist_url, interactive=True):
        """Handle JioSaavn artist URLs by scraping and downloading all songs
        
        Args:
            artist_url: JioSaavn artist URL
            interactive: Whether to prompt user for options
            
        Returns:
            True if songs were found and downloaded, None otherwise
        """
        try:
            self._print(f"[bold cyan]🎤 JioSaavn Artist Link Detected[/bold cyan]")
            self._print("")
            
            # Try to extract artist name from URL
            artist_name = "this artist"
            if '/artist/' in artist_url:
                # Extract from URL pattern
                parts = artist_url.split('/artist/')
                if len(parts) > 1:
                    artist_name = parts[1].split('/')[0].replace('-', ' ').title()
            
            # Try to scrape artist page for songs
            self._print(f"[bold yellow]🔍 Fetching songs from artist page...[/bold yellow]")
            songs = self._scrape_artist_songs(artist_url, artist_name)
            
            if songs and len(songs) > 0:
                # Display all found songs
                print(f"≡ JioSaavn Artist: {artist_name}")
                print(f"▤ Total tracks: {len(songs)}")
                
                # Convert to track list format
                track_list = []
                for song in songs:
                    title = song.get('title', 'Unknown')
                    artists = song.get('artists', artist_name)
                    track_list.append(f"{title} - {artists}")
                
                print(f"✓ Found {len(track_list)} tracks:")
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
                        selected_songs = songs
                    else:
                        # Filter selected songs based on indices
                        indices = [track_list.index(track) for track in choice if track in track_list]
                        selected_tracks = choice
                        selected_songs = [songs[i] for i in indices]
                    
                    # Prompt for audio format and quality
                    output_format, quality = self.downloader._prompt_audio_format_quality()
                else:
                    selected_tracks = track_list
                    selected_songs = songs
                    output_format = 'mp3'
                    quality = 'best'
                
                print(f"\n♫ Starting download of {len(selected_tracks)} track(s)...")
                
                # Create artist directory
                safe_artist_name = sanitize_filename(f"JioSaavn - {artist_name}")
                artist_dir = self.downloader.output_dir / safe_artist_name
                artist_downloader = self.downloader.__class__(artist_dir)
                
                successful_downloads = 0
                
                for i, (track_name, song) in enumerate(zip(selected_tracks, selected_songs), 1):
                    try:
                        self._print(f"\n[bold blue]{Icons.get('music')} [{i:2d}/{len(selected_tracks)}][/bold blue] [cyan]{track_name}[/cyan]")
                        
                        # Extract title and artists for scoring
                        title = song.get('title', 'Unknown')
                        artists_str = song.get('artists', artist_name)
                        
                        youtube_url = self._search_youtube_with_scoring(track_name, title, artists_str)
                        if youtube_url:
                            filename_format = f"{artists_str} - {title}"
                            
                            result = artist_downloader.download_media(
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
                            self._print(Messages.error(f"Could not find on YouTube"))
                            
                    except Exception as e:
                        self._print(Messages.error(f"Error downloading track: {e}"))
                
                print(f"\n✓ Artist download completed: {successful_downloads}/{len(selected_tracks)} tracks downloaded")
                return True if successful_downloads > 0 else None
            else:
                # Show guidance if scraping failed
                self._show_artist_guidance(artist_name)
                return None
            
        except Exception as e:
            self._print(Messages.warning(f"Error processing artist page: {e}"))
            if self.downloader.verbose:
                import traceback
                self._print(f"[dim]{traceback.format_exc()}[/dim]")
            self._show_artist_guidance(artist_name)
            return None
    
    def _show_artist_guidance(self, artist_name):
        """Show guidance for downloading from artist pages
        
        Args:
            artist_name: Name of the artist
        """
        if RICH_AVAILABLE and self.console:
            self.console.print(Panel.fit(
                "[bold yellow]📌 JioSaavn Artist Download Information[/bold yellow]\n\n"
                f"You've provided a link to: [cyan]{artist_name}[/cyan]\n\n"
                "[bold]Artist pages cannot be downloaded directly.[/bold]\n"
                "You need to specify what content you want to download:\n\n"
                "[bold green]✓ What You Can Download:[/bold green]\n\n"
                "[bold cyan]1. Individual Songs[/bold cyan]\n"
                "   • Go to the artist's JioSaavn page\n"
                "   • Click on any song\n"
                "   • Copy the song URL\n"
                "   • Format: [green]https://www.jiosaavn.com/song/...[/green]\n\n"
                "[bold cyan]2. Full Albums[/bold cyan]\n"
                "   • Browse the artist's albums on JioSaavn\n"
                "   • Click on an album\n"
                "   • Copy the album URL\n"
                "   • Format: [green]https://www.jiosaavn.com/album/...[/green]\n\n"
                "[bold cyan]3. Playlists[/bold cyan]\n"
                "   • Find playlists featuring this artist\n"
                "   • Copy the playlist URL\n"
                "   • Format: [green]https://www.jiosaavn.com/playlist/...[/green]\n"
                "   • Or: [green]https://www.jiosaavn.com/featured/...[/green]\n\n"
                "[bold cyan]4. Alternative: YouTube Search[/bold cyan]\n"
                f"   • Search YouTube directly for the artist\n"
                f"   • Use: [green]ytsearch:\"{artist_name} top songs\"[/green]\n"
                "   • Or browse YouTube and copy video URLs\n\n"
                "[bold yellow]💡 Quick Tip:[/bold yellow]\n"
                "For the best experience, copy the URL of specific songs or albums\n"
                "from the artist's JioSaavn page!",
                title=f"🎵 Cannot Download Artist Page Directly",
                border_style="yellow"
            ))
        else:
            print("Artist pages cannot be downloaded directly.")
            print(f"Please provide one of these instead:")
            print(f"  • Song URL - https://www.jiosaavn.com/song/...")
            print(f"  • Album URL - https://www.jiosaavn.com/album/...")
            print(f"  • Playlist URL - https://www.jiosaavn.com/playlist/...")
    
    def _scrape_artist_songs(self, artist_url, artist_name):
        """Scrape artist page to get all songs
        
        Args:
            artist_url: JioSaavn artist URL
            artist_name: Name of the artist
            
        Returns:
            List of dictionaries containing song info or empty list
        """
        try:
            if not BEAUTIFULSOUP_AVAILABLE:
                self._print(Messages.warning("BeautifulSoup not available for scraping"))
                return []
            
            self._print("[dim]Fetching artist page...[/dim]")
            
            # Use cloudscraper if available for better bot detection bypass
            if CLOUDSCRAPER_AVAILABLE:
                scraper = cloudscraper.create_scraper(
                    browser={
                        'browser': 'chrome',
                        'platform': 'windows',
                        'mobile': False
                    }
                )
                response = scraper.get(artist_url, timeout=30)
            else:
                # Fallback to regular requests with retries
                session = requests.Session()
                retries = requests.adapters.Retry(
                    total=3,
                    backoff_factor=1,
                    status_forcelist=[429, 500, 502, 503, 504]
                )
                session.mount('https://', requests.adapters.HTTPAdapter(max_retries=retries))
                
                response = session.get(
                    artist_url,
                    timeout=30,
                    headers={
                        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
                        'Accept-Language': 'en-US,en;q=0.9',
                        'Accept-Encoding': 'gzip, deflate, br',
                        'Connection': 'keep-alive',
                        'Upgrade-Insecure-Requests': '1',
                        'Sec-Fetch-Dest': 'document',
                        'Sec-Fetch-Mode': 'navigate',
                        'Sec-Fetch-Site': 'none',
                        'Sec-Fetch-User': '?1',
                        'Cache-Control': 'max-age=0',
                        'Referer': 'https://www.jiosaavn.com/'
                    }
                )
            
            if response.status_code != 200:
                self._print(f"[dim red]Failed to fetch page (Status: {response.status_code})[/dim red]")
                return []
            
            self._print("[dim]Parsing page content...[/dim]")
            soup = BeautifulSoup(response.text, 'html.parser')
            
            songs = []
            
            # Method 1: Look for script tags with JSON data
            script_tags = soup.find_all('script')
            for script in script_tags:
                if script.string and ('window.__INITIAL_DATA__' in script.string or 'topSongs' in script.string):
                    try:
                        # Extract JSON data from script
                        script_content = script.string
                        
                        # Try to find JSON data
                        if 'window.__INITIAL_DATA__' in script_content:
                            # Extract the JSON part
                            json_start = script_content.find('{')
                            json_end = script_content.rfind('}') + 1
                            if json_start != -1 and json_end > json_start:
                                json_str = script_content[json_start:json_end]
                                data = json.loads(json_str)
                                
                                # Navigate through the JSON to find songs
                                songs_data = self._extract_songs_from_json(data)
                                if songs_data:
                                    songs.extend(songs_data)
                                    break
                    except Exception as e:
                        if self.downloader.verbose:
                            self._print(f"[dim]JSON parsing error: {e}[/dim]")
                        continue
            
            # Method 2: Look for structured data (ld+json)
            if not songs:
                self._print("[dim]Trying structured data extraction...[/dim]")
                script_tags = soup.find_all('script', type='application/ld+json')
                for script in script_tags:
                    try:
                        json_data = json.loads(script.string)
                        if isinstance(json_data, dict):
                            # Look for MusicGroup or artist info
                            if json_data.get('@type') == 'MusicGroup':
                                # Extract tracks if available
                                tracks = json_data.get('track', [])
                                if isinstance(tracks, list):
                                    for track in tracks:
                                        if isinstance(track, dict):
                                            songs.append({
                                                'title': self._decode_html_entities(track.get('name', 'Unknown')),
                                                'artists': self._decode_html_entities(artist_name)
                                            })
                    except:
                        continue
            
            # Method 3: Parse HTML for song elements
            if not songs:
                self._print("[dim]Trying HTML parsing...[/dim]")
                
                # Look for more specific song containers with href attributes
                song_links = soup.find_all('a', href=re.compile(r'/song/'))
                
                for link in song_links:
                    try:
                        # Get the song title from the link text or nested elements
                        title = None
                        
                        # Try to find title in nested elements
                        title_elem = link.find(['p', 'span', 'div'], class_=re.compile(r'(title|name|song)', re.IGNORECASE))
                        if title_elem:
                            title = title_elem.get_text(strip=True)
                        elif link.get('title'):
                            title = link.get('title')
                        elif link.get_text(strip=True):
                            title = link.get_text(strip=True)
                        
                        if title:
                            title = self._decode_html_entities(title)
                            
                            # Filter out non-song titles (menu items, durations, etc.)
                            if (len(title) > 3 and 
                                not title.replace(':', '').replace('.', '').isdigit() and  # Not a duration
                                title not in ['New Releases', 'Top Playlists', 'Top Artists', 'Popular', 'Date', 'Name', 'Save', 'Clear'] and
                                not any(s.get('title') == title for s in songs)):
                                
                                # Try to find artist info near the link
                                artist = None
                                
                                # Look in parent container
                                parent = link.find_parent(['div', 'li', 'article'])
                                if parent:
                                    # Try multiple strategies to find artist
                                    artist_elem = (parent.find(['p', 'span', 'div', 'a'], class_=re.compile(r'(artist|singer|subtitle)', re.IGNORECASE)) or
                                                 parent.find('a', href=re.compile(r'/artist/')))
                                    
                                    if artist_elem:
                                        artist_text = artist_elem.get_text(strip=True)
                                        if artist_text and len(artist_text) > 2 and artist_text != title:
                                            artist = self._decode_html_entities(artist_text)
                                
                                # If no artist found, use the artist name from URL
                                if not artist:
                                    artist = artist_name.replace(' Songs', '').replace(' songs', '')
                                
                                songs.append({
                                    'title': title,
                                    'artists': artist
                                })
                    except:
                        continue
            
            # Remove duplicates and clean up
            seen_titles = set()
            unique_songs = []
            for song in songs:
                title = song.get('title', '').strip()
                if title and title not in seen_titles and len(title) > 2:
                    seen_titles.add(title)
                    unique_songs.append(song)
            
            self._print(f"[dim]Found {len(unique_songs)} unique songs[/dim]")
            return unique_songs
            
        except requests.exceptions.Timeout:
            self._print(Messages.warning("Request timed out. JioSaavn may be blocking requests or is slow to respond."))
            return []
        except Exception as e:
            self._print(Messages.warning(f"Scraping error: {e}"))
            if self.downloader.verbose:
                import traceback
                self._print(f"[dim]{traceback.format_exc()}[/dim]")
            return []
    
    def _extract_songs_from_json(self, data):
        """Recursively extract song information from JSON data
        
        Args:
            data: JSON data structure
            
        Returns:
            List of song dictionaries
        """
        songs = []
        
        try:
            if isinstance(data, dict):
                # Look for common keys that contain songs
                for key in ['topSongs', 'songs', 'tracks', 'items', 'results']:
                    if key in data:
                        items = data[key]
                        if isinstance(items, list):
                            for item in items:
                                if isinstance(item, dict):
                                    title = item.get('title') or item.get('name') or item.get('song')
                                    artist = item.get('artist') or item.get('artists') or item.get('singer')
                                    
                                    # Handle artist as dict or list
                                    if isinstance(artist, dict):
                                        artist = artist.get('name', '')
                                    elif isinstance(artist, list):
                                        artist = ', '.join([a.get('name', '') if isinstance(a, dict) else str(a) for a in artist])
                                    
                                    if title:
                                        songs.append({
                                            'title': self._decode_html_entities(str(title)),
                                            'artists': self._decode_html_entities(str(artist)) if artist else 'Unknown'
                                        })
                        elif isinstance(items, dict):
                            # Recursively search
                            songs.extend(self._extract_songs_from_json(items))
                
                # Recursively search other dict values
                if not songs:
                    for value in data.values():
                        if isinstance(value, (dict, list)):
                            found_songs = self._extract_songs_from_json(value)
                            if found_songs:
                                songs.extend(found_songs)
                                break
            
            elif isinstance(data, list):
                for item in data:
                    if isinstance(item, (dict, list)):
                        songs.extend(self._extract_songs_from_json(item))
        
        except Exception as e:
            pass
        
        return songs
    
    def _embed_album_art(self, audio_file, image_url, title, artist, album, year):
        """Embed album art and metadata into audio file
        
        Args:
            audio_file: Path to audio file
            image_url: URL of album art image
            title: Song title
            artist: Artist name
            album: Album name
            year: Release year
        """
        try:
            if not MUTAGEN_AVAILABLE:
                return
            
            # Download album art
            response = requests.get(image_url, timeout=10)
            if response.status_code != 200:
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
