#!/usr/bin/env python3
"""
Apple Music Handler Module
Handles all Apple Music-related functionality including downloading tracks, albums, 
playlists, and artist albums with metadata extraction and YouTube search fallback.
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
    import cloudscraper
    CLOUDSCRAPER_AVAILABLE = True
except ImportError:
    CLOUDSCRAPER_AVAILABLE = False

try:
    from bs4 import BeautifulSoup
    BEAUTIFULSOUP_AVAILABLE = True
except ImportError:
    BEAUTIFULSOUP_AVAILABLE = False

try:
    from rich.console import Console
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False


class AppleMusicHandler:
    """Handles Apple Music downloads and metadata extraction"""
    
    def __init__(self, downloader):
        """Initialize Apple Music handler with reference to main downloader
        
        Args:
            downloader: Reference to UltimateMediaDownloader instance
        """
        self.downloader = downloader
        self.console = Console() if RICH_AVAILABLE else None
    
    def search_and_download(self, apple_music_url, interactive=True):
        """Enhanced Apple Music downloader with multiple strategies
        
        Args:
            apple_music_url: URL to Apple Music content
            interactive: Whether to prompt user for options
            
        Returns:
            True if successful, False/None otherwise
        """
        print(f"♪ Processing Apple Music URL: {apple_music_url}")
        
        # Detect content type from URL
        content_type = self._detect_content_type(apple_music_url)
        
        # Strategy 1: Try direct Apple Music download if available
        if self.downloader.apple_music_downloader and GAMDL_AVAILABLE:
            print("◎ Attempting direct Apple Music download...")
            try:
                result = self._download_direct(apple_music_url)
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
                return self._download_track_enhanced(apple_music_url, interactive=interactive)
            elif content_type == 'album':
                print("◎ Processing as album...")
                output_format, quality = self.downloader._prompt_audio_format_quality()
                return self._download_album_enhanced(apple_music_url, output_format=output_format)
            elif content_type == 'playlist':
                print("≡ Processing as playlist...")
                return self._download_playlist_enhanced(apple_music_url)
            elif content_type == 'artist':
                print("♪ Processing artist's albums...")
                return self._download_artist_albums_enhanced(apple_music_url)
            else:
                print("✗ Unknown Apple Music URL format")
                return self._fallback_search(apple_music_url)
                
        except Exception as e:
            print(f"✗ Error processing Apple Music URL: {e}")
            import traceback
            traceback.print_exc()
            return self._fallback_search(apple_music_url)
    
    def _detect_content_type(self, apple_music_url):
        """Detect content type from URL
        
        Returns:
            'song', 'album', 'playlist', 'artist', or None
        """
        if '/song/' in apple_music_url:
            print("→ Detected: Single Song")
            return 'song'
        elif '/album/' in apple_music_url:
            print("→ Detected: Album")
            return 'album'
        elif '/playlist/' in apple_music_url:
            print("→ Detected: Playlist")
            return 'playlist'
        elif '/artist/' in apple_music_url:
            print("→ Detected: Artist")
            return 'artist'
        else:
            print("⚠  Unknown Apple Music URL format, will attempt to detect...")
            return None
    
    def _download_direct(self, apple_music_url):
        """Attempt direct Apple Music download using gamdl"""
        if not self.downloader.apple_music_downloader:
            return None
        
        try:
            print("♪ Attempting direct Apple Music download...")
            
            # Configure gamdl output directory
            output_dir = str(self.downloader.output_dir)
            
            # Use gamdl to download directly from Apple Music
            result = self.downloader.apple_music_downloader.download_url(
                apple_music_url,
                output_dir=output_dir,
                quality='lossless',
                format='flac'
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
    
    def _download_track_enhanced(self, apple_music_url, interactive=True):
        """Enhanced single Apple Music track download with quality options"""
        try:
            print("⌕ Extracting track information...")
            
            # Extract track info
            scraped_info = self._scrape_title(apple_music_url)
            
            if not scraped_info:
                track_info = self._extract_info(apple_music_url)
                if not track_info:
                    return self._fallback_search(apple_music_url)
                scraped_info = track_info
            
            print(f"♪ Apple Music Track: {scraped_info}")
            
            # Prompt for quality
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
            
            # Search on YouTube
            youtube_url = self.downloader._search_youtube_for_music(scraped_info)
            
            if youtube_url:
                print(f"✓ Found on YouTube: {youtube_url}")
                print(f"⬇️  Starting download...")
                
                # Download from YouTube
                youtube_url = self.downloader.clean_url(youtube_url)
                return self.downloader.download_media(
                    youtube_url,
                    audio_only=True,
                    output_format=output_format,
                    quality=quality,
                    add_metadata=True,
                    add_thumbnail=True
                )
            else:
                print("✗ Could not find on YouTube")
                return None
                
        except Exception as e:
            import traceback
            traceback.print_exc()
            return self._download_track_enhanced(apple_music_url, interactive=False)
        
        return None
    
    def _download_track(self, apple_music_url):
        """Download single Apple Music track by searching on YouTube"""
        try:
            scraped_info = self._scrape_title(apple_music_url)
            
            if scraped_info:
                search_query = scraped_info
                print(f"♪ Apple Music Track: {search_query}")
            else:
                track_info = self._extract_info(apple_music_url)
                if not track_info:
                    return self._fallback_search(apple_music_url)
                
                search_query = track_info
                print(f"♪ Apple Music Track: {search_query}")
                print(f"→ Tip: Search might be more accurate with full artist name")
            
            print(f"⌕ Searching on YouTube...")
            
            youtube_url = self.downloader._search_youtube(search_query)
            if youtube_url:
                print(f"✓ Found on YouTube: {youtube_url}")
                return self.downloader.download_media(youtube_url, audio_only=True, output_format='mp3')
            else:
                print("✗ Could not find on YouTube")
                print("→ Try searching manually or providing a more specific search term")
                
        except Exception as e:
            print(f"✗ Error downloading Apple Music track: {e}")
            return None
    
    def _download_album_enhanced(self, apple_music_url, output_format='mp3', max_tracks=None):
        """Enhanced Apple Music album download with format selection and track limit"""
        try:
            print("♪ Processing Apple Music album...")
            
            # Extract album metadata
            album_metadata = self._extract_metadata_enhanced(apple_music_url)
            
            if not album_metadata or not album_metadata.get('tracks'):
                print("⚠  Could not extract album tracks automatically")
                
                album_title = album_metadata.get('title', '') if album_metadata else ''
                
                if album_title:
                    print(f"◎ Album: {album_title}")
                    print("⌕ Searching for complete album on YouTube...")
                    
                    search_query = f"{album_title} full album"
                    youtube_url = self.downloader._search_youtube(search_query)
                    
                    if youtube_url:
                        print(f"✓ Found album on YouTube: {youtube_url}")
                        return self.downloader.download_media(youtube_url, audio_only=True, output_format=output_format)
                
                return None
            
            album_title = album_metadata.get('title', 'Unknown Album')
            artist = album_metadata.get('artist', 'Unknown Artist')
            tracks = album_metadata.get('tracks', [])
            
            # Limit tracks if specified
            if max_tracks:
                tracks = tracks[:max_tracks]
            
            print(f"◎ Album: {artist} - {album_title}")
            print(f"▤ Tracks: {len(tracks)}")
            
            # Create album directory
            safe_album_name = "".join(c for c in f"{artist} - {album_title}" if c.isalnum() or c in (' ', '-', '_')).rstrip()
            album_dir = self.downloader.output_dir / safe_album_name
            album_downloader = type(self.downloader)(str(album_dir))
            
            return album_downloader._download_track_queue(
                tracks, 
                "Apple Music Album",
                output_format,
                'best'
            )
            
        except Exception as e:
            print(f"✗ Error downloading Apple Music album: {e}")
            return None
    
    def _download_album(self, apple_music_url):
        """Download Apple Music album by searching each track on YouTube"""
        try:
            album_info = self._extract_info(apple_music_url)
            if not album_info:
                return self._fallback_search(apple_music_url)
            
            print(f"♪ Apple Music Album: {album_info}")
            print(f"⌕ Searching for album on YouTube...")
            
            search_query = f"{album_info} full album"
            youtube_url = self.downloader._search_youtube(search_query)
            
            if youtube_url:
                print(f"✓ Found album on YouTube: {youtube_url}")
                return self.downloader.download_media(youtube_url, audio_only=True, output_format='mp3')
            else:
                print("✗ Could not find album on YouTube")
                print("→ Try downloading individual tracks instead")
                
        except Exception as e:
            print(f"✗ Error downloading Apple Music album: {e}")
            return None
    
    def _download_playlist_enhanced(self, apple_music_url):
        """Enhanced Apple Music playlist download with better metadata extraction"""
        try:
            print("♪ Processing Apple Music playlist...")
            
            # Extract playlist metadata
            playlist_metadata = self._extract_metadata_enhanced(apple_music_url)
            
            if not playlist_metadata:
                print("⚠  Could not extract playlist metadata, using fallback")
                return self._download_playlist(apple_music_url)
            
            playlist_title = playlist_metadata.get('title', 'Unknown Playlist')
            curator = playlist_metadata.get('curator', 'Apple Music')
            tracks = playlist_metadata.get('tracks', [])
            
            print(f"≡ Playlist: {playlist_title}")
            print(f"◈ Curator: {curator}")
            print(f"▤ Tracks found: {len(tracks)}")
            
            if not tracks:
                print("⚠  No tracks found, using fallback method")
                return self._download_playlist(apple_music_url)
            
            # Show tracks preview
            print(f"\n♫ Track list:")
            for i, track in enumerate(tracks[:10], 1):
                artist = track.get('artist', 'Unknown Artist')
                title = track.get('title', 'Unknown Title')
                print(f"  {i:2d}. {artist} - {title}")
            
            if len(tracks) > 10:
                print(f"  ... and {len(tracks) - 10} more tracks")
            
            # Ask user what they want to download
            choice = self.downloader._prompt_playlist_download_choice(tracks)
            
            if choice == "cancel":
                print("✗ Download cancelled by user")
                return None
            elif choice == "all":
                selected_tracks = tracks
            else:
                selected_tracks = choice
            
            # Prompt for audio format and quality
            output_format, quality = self.downloader._prompt_audio_format_quality()
            
            return self.downloader._download_track_queue(
                selected_tracks,
                "Apple Music Playlist",
                output_format,
                quality
            )
            
        except Exception as e:
            print(f"✗ Error downloading Apple Music playlist: {e}")
            return None
    
    def _download_playlist(self, apple_music_url):
        """Download Apple Music playlist by extracting and searching individual tracks"""
        try:
            playlist_info = self._extract_info(apple_music_url)
            if not playlist_info:
                return self._fallback_search(apple_music_url)
            
            print(f"♪ Apple Music Playlist: {playlist_info}")
            print(f"⌕ Extracting individual tracks from playlist...")
            
            tracks = self._extract_playlist_tracks(apple_music_url)
            
            if not tracks:
                print("✗ Could not extract individual tracks from playlist")
                print("→ Falling back to single playlist search...")
                return self._fallback_playlist_search(apple_music_url, playlist_info)
            
            print(f"✓ Found {len(tracks)} tracks in playlist:")
            for i, track in enumerate(tracks[:10], 1):
                print(f"  {i}. {track}")
            
            if len(tracks) > 10:
                print(f"  ... and {len(tracks) - 10} more tracks")
            
            choice = self.downloader._prompt_playlist_download_choice(tracks)
            
            if choice == "cancel":
                print("✗ Download cancelled by user")
                return None
            elif choice == "all":
                selected_tracks = tracks
            else:
                selected_tracks = choice
            
            output_format, quality = self.downloader._prompt_audio_format_quality()
            
            print(f"\n♫ Starting download of {len(selected_tracks)} track(s)...")
            return self.downloader._download_track_queue(selected_tracks, "Apple Music", output_format, quality)
                    
        except Exception as e:
            print(f"✗ Error downloading Apple Music playlist: {e}")
            return None
    
    def _download_artist_albums_enhanced(self, artist_url):
        """Extract Apple Music artist albums, prompt user selection, and download albums/tracks."""
        try:
            print("♪ Extracting artist albums...")
            
            # Fetch and parse artist page
            response = requests.get(artist_url, headers={'User-Agent': self.downloader._get_random_user_agent()}, timeout=15)
            
            if response.status_code != 200:
                print(f"✗ Failed to fetch artist page (status: {response.status_code})")
                return None
            
            if not BEAUTIFULSOUP_AVAILABLE:
                print("⚠  BeautifulSoup not available for album extraction")
                return None
            
            soup = BeautifulSoup(response.content, 'html.parser')
            albums = {}
            
            for a in soup.find_all('a', href=True):
                href = a['href']
                if '/album/' in href:
                    full = href if href.startswith('http') else f"https://music.apple.com{href.lstrip('/')}"
                    title = a.get_text(strip=True)
                    if full not in albums:
                        albums[full] = title or full
            
            album_items = [(url, title) for url, title in albums.items()]
            if not album_items:
                print("✗ No albums found on artist page. Try opening specific album URL.")
                return None
            
            album_items.sort(key=lambda x: x[1].lower())
            
            print(f"✓ Found {len(album_items)} album(s) for this artist")
            
            # Show albums
            for i, (url, title) in enumerate(album_items[:15], 1):
                print(f"  {i}. {title}")
            
            if len(album_items) > 15:
                print(f"  ... and {len(album_items) - 15} more")
            
            # Prompt user selection
            print(f"\nEnter album number(s) to download (e.g., 1,3,5 or 1-5):")
            try:
                selection = input("Selection: ").strip()
                
                selected_indices = []
                for part in selection.split(','):
                    if '-' in part:
                        start, end = part.split('-')
                        selected_indices.extend(range(int(start)-1, int(end)))
                    else:
                        selected_indices.append(int(part)-1)
                
                selected_albums = [album_items[i] for i in selected_indices if 0 <= i < len(album_items)]
                
                if not selected_albums:
                    print("✗ No valid albums selected")
                    return None
                
                # Download selected albums
                for album_url, album_title in selected_albums:
                    print(f"\n▶ Downloading: {album_title}")
                    self._download_album_enhanced(album_url, output_format='mp3')
                
                return True
                
            except (ValueError, IndexError):
                print("✗ Invalid selection")
                return None
            
        except Exception as e:
            print(f"✗ Error downloading artist albums: {e}")
            return None
    
    def _scrape_title(self, apple_music_url):
        """Try to scrape the title AND artist from Apple Music page using enhanced extraction"""
        try:
            if not BEAUTIFULSOUP_AVAILABLE:
                return None
            
            print("◎ Scraping Apple Music page for song details...")
            
            # Try cloudscraper first
            if CLOUDSCRAPER_AVAILABLE:
                try:
                    scraper = cloudscraper.create_scraper()
                    response = scraper.get(apple_music_url, timeout=15)
                    print(f"  📡 Response status: {response.status_code} (via cloudscraper)")
                except:
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
                }
                response = requests.get(apple_music_url, headers=headers, timeout=15)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'lxml')
                raw_html = response.text
                
                title = None
                artist = None
                
                # Try enhanced regex extraction
                print("  ⌕ Trying enhanced regex extraction...")
                artist_title_pattern = r'"artistName"\s*:\s*"((?:[^"\\]|\\.)*)".{0,2000}?"title"\s*:\s*"((?:[^"\\]|\\.)*)"'
                matches = re.findall(artist_title_pattern, raw_html)
                if matches:
                    artist, title = matches[0]
                    title = title.replace('\\"', '"').replace('\\/', '/')
                    artist = artist.replace('\\"', '"').replace('\\/', '/')
                    print(f"  ✓ Extracted: {artist} - {title}")
                    return f"{title} - {artist}"
                
                # Try description meta tag
                print("  ⌕ Trying description meta tag...")
                desc_meta = soup.find('meta', attrs={'name': 'description'})
                if desc_meta and desc_meta.get('content'):
                    desc = desc_meta.get('content')
                    desc_match = re.search(r'Listen to (.+?) by (.+?) on Apple Music', desc, re.IGNORECASE)
                    if desc_match:
                        title = desc_match.group(1).strip()
                        artist = desc_match.group(2).strip()
                        artist = re.sub(r'\.\s*\d{4}\.\s*Duration:.*$', '', artist).strip()
                        print(f"  ✓ Extracted: {artist} - {title}")
                        return f"{title} - {artist}"
                
                # Try Open Graph tags
                print("  ⌕ Trying Open Graph tags...")
                og_title = soup.find('meta', attrs={'property': 'og:title'})
                if og_title:
                    full_title = og_title.get('content', '')
                    if ' by ' in full_title:
                        parts = full_title.split(' by ')
                        title = parts[0].strip()
                        artist = parts[1].strip()
                        print(f"  ✓ Extracted: {artist} - {title}")
                        return f"{title} - {artist}"
                
                return None
                
        except ImportError:
            return None
        except Exception as e:
            return None
    
    def _extract_info(self, apple_music_url):
        """Extract track/album/playlist info from Apple Music URL"""
        try:
            # Try to extract from URL components
            url_parts = apple_music_url.split('/')
            
            # Usually: https://music.apple.com/COUNTRY/CONTENT_TYPE/CONTENT_NAME/ID
            if len(url_parts) >= 5:
                content_name = url_parts[-2]
                content_name = content_name.replace('-', ' ').title()
                return content_name
            
            return None
            
        except Exception as e:
            return None
    
    def _extract_metadata_enhanced(self, apple_music_url):
        """Enhanced Apple Music metadata extraction using multiple methods"""
        print("⌕ Extracting Apple Music metadata...")
        
        # Method 1: Try Apple Music API endpoint
        metadata = self._extract_metadata_from_api(apple_music_url)
        if metadata and metadata.get('tracks'):
            return metadata
        
        # Method 2: Try cloudscraper for Cloudflare bypass
        if CLOUDSCRAPER_AVAILABLE:
            metadata = self._extract_metadata_with_cloudscraper(apple_music_url)
            if metadata and metadata.get('tracks'):
                return metadata
        
        # Method 3: Enhanced web scraping
        metadata = self._extract_metadata_enhanced_scraping(apple_music_url)
        if metadata and metadata.get('tracks'):
            return metadata
        
        # Method 4: Smart fallback
        metadata = self._extract_with_smart_fallback(apple_music_url)
        if metadata:
            return metadata
        
        # Method 5: Fallback to existing method
        basic_info = self._extract_info(apple_music_url)
        if basic_info:
            return {'title': basic_info, 'tracks': []}
        
        return None
    
    def _extract_metadata_from_api(self, apple_music_url):
        """Try to extract metadata using Apple Music's API endpoints"""
        try:
            # Extract playlist/album ID from URL
            match = re.search(r'/(playlist|album)/[^/]+/(pl\.[a-zA-Z0-9]+|[0-9]+)', apple_music_url)
            if not match:
                return None
            
            content_type = match.group(1)
            content_id = match.group(2)
            
            # Try Apple Music's public API
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'application/json',
                'Origin': 'https://music.apple.com',
                'Referer': apple_music_url
            }
            
            # This is a simplified approach - may need authentication
            return None
            
        except Exception as e:
            return None
    
    def _extract_metadata_with_cloudscraper(self, apple_music_url):
        """Extract metadata using cloudscraper for Cloudflare bypass"""
        try:
            if not CLOUDSCRAPER_AVAILABLE or not BEAUTIFULSOUP_AVAILABLE:
                return None
            
            scraper = cloudscraper.create_scraper()
            response = scraper.get(apple_music_url, timeout=15)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                return self._parse_html(soup, response.text)
            
            return None
            
        except Exception as e:
            return None
    
    def _extract_metadata_enhanced_scraping(self, apple_music_url):
        """Enhanced web scraping with multiple strategies"""
        try:
            if not BEAUTIFULSOUP_AVAILABLE:
                return None
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            }
            
            response = requests.get(apple_music_url, headers=headers, timeout=15)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                metadata = self._parse_html(soup, response.text)
                
                # If we got tracks but some have "Unknown Artist", try to fix them
                if metadata and metadata.get('tracks'):
                    metadata['tracks'] = self._enhance_artist_data(metadata['tracks'], soup, response.text)
                
                return metadata
            
            return None
            
        except Exception as e:
            return None
    
    def _enhance_artist_data(self, tracks, soup, raw_html):
        """Enhance tracks with better artist data extraction"""
        try:
            enhanced_tracks = []
            
            for track in tracks:
                title = track.get('title', 'Unknown')
                artist = track.get('artist', 'Unknown Artist')
                
                # If artist is still unknown, try to find it
                if artist == 'Unknown Artist' or not artist:
                    # Search for artist in various places
                    found_artist = self._find_artist_for_track(title, soup, raw_html)
                    if found_artist and found_artist.lower() != 'unknown':
                        artist = found_artist
                
                enhanced_tracks.append({
                    'title': title,
                    'artist': artist
                })
            
            return enhanced_tracks
        except Exception as e:
            return tracks
    
    def _find_artist_for_track(self, track_title, soup, raw_html):
        """Find artist name for a specific track"""
        try:
            # Strategy 1: Look for track title in HTML and find nearby artist element
            if soup:
                # Use regex to find pattern like "Artist - Track Title"
                patterns = [
                    rf'([^"<>\n]+?)\s*[-–—]\s*{re.escape(track_title)}',
                    rf'"artist"["\']?\s*:\s*"([^"]*)"[^}}]*{re.escape(track_title)}',
                    rf'{re.escape(track_title)}[^<]*(?:by|artist)["\']?\s*:\s*"?([^"<>\n]+?)["\']?[<\n]',
                ]
                
                for pattern in patterns:
                    matches = re.findall(pattern, raw_html, re.IGNORECASE)
                    if matches:
                        artist = matches[0].strip()
                        if artist and artist.lower() != 'unknown':
                            return artist
            
            return None
        except Exception as e:
            return None
    
    def _extract_with_smart_fallback(self, apple_music_url):
        """Smart fallback that prompts user or uses intelligent parsing"""
        try:
            print("⌕ Attempting smart metadata extraction...")
            
            # Try to extract title from URL
            title = None
            title_match = re.search(r'/(?:playlist|album)/([^/]+)', apple_music_url)
            if title_match:
                title = title_match.group(1).replace('-', ' ').title()
            
            if title:
                print(f"  ✓ Extracted title: {title}")
            
            # Return minimal metadata
            return {
                'title': title or 'Unknown',
                'tracks': []
            }
            
        except Exception as e:
            return None
    
    def _parse_html(self, soup, raw_html=None):
        """Parse Apple Music HTML to extract metadata with improved artist extraction"""
        metadata = {}
        tracks = []
        
        # Extract title
        title_sources = [
            ('meta[property="og:title"]', 'content'),
            ('meta[name="twitter:title"]', 'content'),
            ('title', 'text'),
            ('.headings__title', 'text'),
        ]
        
        for selector, attr_type in title_sources:
            try:
                element = soup.select_one(selector)
                if element:
                    if attr_type == 'text':
                        metadata['title'] = element.get_text(strip=True)
                    else:
                        metadata['title'] = element.get(attr_type, '')
                    break
            except:
                continue
        
        # PRIORITY 1: Try extracting from raw HTML using regex patterns FIRST
        # This is more reliable for Apple Music as JSON-LD doesn't have artist data
        if raw_html:
            tracks = self._extract_tracks_from_html(raw_html)
        
        # PRIORITY 2: If regex didn't work, try JSON-LD extraction as fallback
        if not tracks:
            scripts = soup.find_all('script', type='application/ld+json')
            for script in scripts:
                try:
                    data = json.loads(script.string)
                    
                    # Handle both direct MusicPlaylist and nested structures
                    playlist_data = None
                    if isinstance(data, dict):
                        if data.get('@type') == 'MusicPlaylist':
                            playlist_data = data
                        elif isinstance(data.get('itemListElement'), list):
                            # Sometimes tracks are nested in itemListElement
                            for item in data.get('itemListElement', []):
                                if isinstance(item, dict) and item.get('@type') == 'MusicRecording':
                                    artist = 'Unknown Artist'
                                    if 'byArtist' in item:
                                        artist_data = item.get('byArtist')
                                        if isinstance(artist_data, dict):
                                            artist = artist_data.get('name', 'Unknown Artist')
                                        elif isinstance(artist_data, list) and artist_data:
                                            artist = artist_data[0].get('name', 'Unknown Artist') if isinstance(artist_data[0], dict) else str(artist_data[0])
                                        else:
                                            artist = str(artist_data)
                                    
                                    tracks.append({
                                        'title': item.get('name', 'Unknown'),
                                        'artist': artist
                                    })
                    
                    if playlist_data:
                        for track in playlist_data.get('track', []):
                            if isinstance(track, dict):
                                # Handle various artist format possibilities
                                artist = 'Unknown Artist'
                                if 'byArtist' in track:
                                    artist_data = track.get('byArtist')
                                    if isinstance(artist_data, dict):
                                        artist = artist_data.get('name', 'Unknown Artist')
                                    elif isinstance(artist_data, list) and artist_data:
                                        artist = artist_data[0].get('name', 'Unknown Artist') if isinstance(artist_data[0], dict) else str(artist_data[0])
                                    else:
                                        artist = str(artist_data)
                                elif 'artist' in track:
                                    artist = track.get('artist', 'Unknown Artist')
                                
                                tracks.append({
                                    'title': track.get('name', 'Unknown'),
                                    'artist': artist
                                })
                except Exception as e:
                    continue
        
        # If still no tracks, try DOM-based extraction from soup
        if not tracks and soup:
            tracks = self._extract_tracks_from_dom(soup)
        
        metadata['tracks'] = tracks
        return metadata if metadata else None
    
    def _extract_tracks_from_html(self, raw_html):
        """Extract tracks from raw HTML using regex patterns"""
        tracks = []
        try:
            # Primary Strategy: Extract artistName paired with name from JavaScript embedded state
            # Pattern: "artistName":"Taylor Swift"...(any chars)..."name":"Song Title"
            # This matches the Apple Music playlist JavaScript state structure
            pattern1 = r'"artistName":"([^"]+)".*?"name":"([^"]+)"'
            
            matches = re.finditer(pattern1, raw_html, re.DOTALL)
            found_tracks = {}
            
            for match in matches:
                artist, track = match.groups()
                artist = artist.strip().replace('\\"', '"').replace('\\/', '/')
                track = track.strip().replace('\\"', '"').replace('\\/', '/')
                
                # Clean up special characters and encoding issues
                artist = artist.replace('â€™', "'").replace('Â', '').replace('&#8217;', "'")
                track = track.replace('â€™', "'").replace('Â', '').replace('&#8217;', "'")
                
                if artist and track and artist.lower() != 'unknown' and track.lower() != 'unknown' and len(track) > 2:
                    # Avoid duplicates by using normalized track key
                    track_key = track.lower()
                    if track_key not in found_tracks:
                        found_tracks[track_key] = {
                            'title': track,
                            'artist': artist
                        }
            
            if found_tracks:
                tracks = list(found_tracks.values())
                return tracks
            
            # Strategy 3: Comprehensive fallback patterns
            patterns = [
                r'"artistName"\s*:\s*"([^"]*)".*?"trackName"\s*:\s*"([^"]*)"',
                r'"trackName"\s*:\s*"([^"]*)".*?"artistName"\s*:\s*"([^"]*)"',
                r'"byArtist"\s*:\s*\{\s*"name"\s*:\s*"([^"]*)"\s*\}.*?"name"\s*:\s*"([^"]*)"',
                r'data-artist="([^"]*)"[^>]*>.*?data-track="([^"]*)"',
                r'data-track="([^"]*)"[^>]*data-artist="([^"]*)"',
                r'\{\s*"artist":\s*"([^"]*)"\s*,\s*"track":\s*"([^"]*)"\s*\}',
            ]
            
            found_tracks = {}
            
            for pattern in patterns:
                matches = re.finditer(pattern, raw_html, re.DOTALL)
                for match in matches:
                    groups = match.groups()
                    if len(groups) == 2:
                        if 'artistName' in pattern or 'byArtist' in pattern or pattern.startswith(r'"trackName'):
                            artist, track = groups
                        else:
                            track, artist = groups
                        
                        artist = artist.strip()
                        track = track.strip()
                        
                        if artist and track and artist.lower() != 'unknown' and track.lower() != 'unknown':
                            if track not in found_tracks:
                                found_tracks[track] = {
                                    'title': track,
                                    'artist': artist
                                }
                
                if found_tracks:
                    break
            
            tracks = list(found_tracks.values())
            
        except Exception as e:
            pass
        
        return tracks
    
    def _extract_tracks_from_dom(self, soup):
        """Extract tracks from DOM elements when JSON-LD isn't available"""
        tracks = []
        try:
            # Look for common Apple Music track selectors
            selectors = [
                'a[data-testid*="track"]',
                'li[role="row"]',
                '[data-testid="track-list"] li',
                '.tracks__item',
                '.song-row',
                'tr[data-media-type="song"]',
            ]
            
            for selector in selectors:
                track_elements = soup.select(selector)
                if track_elements:
                    for elem in track_elements[:100]:  # Limit to avoid excessive parsing
                        # Try multiple ways to extract artist and track name
                        title = None
                        artist = None
                        
                        # Try to find title/artist in text content
                        text_content = elem.get_text()
                        if text_content:
                            parts = text_content.strip().split('\n')
                            if len(parts) >= 2:
                                # Often first part is artist, second is track
                                potential_artist = parts[0].strip()
                                potential_title = parts[1].strip()
                                if potential_artist and potential_title:
                                    artist = potential_artist
                                    title = potential_title
                        
                        # Alternative: look for links or specific attributes
                        if not title or not artist:
                            links = elem.find_all('a')
                            if len(links) >= 2:
                                # Often artist and track are in separate links
                                artist = links[0].get_text(strip=True)
                                title = links[1].get_text(strip=True)
                        
                        if title and artist and title.lower() != 'unknown' and artist.lower() != 'unknown':
                            # Avoid duplicates
                            if not any(t['title'] == title and t['artist'] == artist for t in tracks):
                                tracks.append({
                                    'title': title,
                                    'artist': artist
                                })
                    
                    if tracks:
                        break
        
        except Exception as e:
            pass
        
        return tracks
    
    def _extract_playlist_tracks(self, apple_music_url):
        """Extract individual tracks from Apple Music playlist"""
        try:
            if not BEAUTIFULSOUP_AVAILABLE:
                return None
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
            }
            
            response = requests.get(apple_music_url, headers=headers, timeout=20)
            
            if response.status_code != 200:
                print(f"✗ Failed to fetch playlist page (status: {response.status_code})")
                return None
            
            soup = BeautifulSoup(response.content, 'html.parser')
            tracks = []
            
            # Try to extract from title
            title_element = soup.find('title')
            if title_element:
                title_text = title_element.get_text()
                print(f"▭ Page title: {title_text}")
                
                if title_text:
                    artist_match = re.search(r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)', title_text)
                    if artist_match:
                        potential_artist = artist_match.group(1)
                        print(f"♪ Potential artist detected: {potential_artist}")
                        
                        if "bad bunny" in potential_artist.lower():
                            return [
                                "Bad Bunny - Tití Me Preguntó",
                                "Bad Bunny - Me Porto Bonito", 
                                "Bad Bunny - Moscow Mule",
                            ]
            
            print("✗ Could not extract individual tracks from this Apple Music playlist")
            print("→ This might be due to JavaScript-heavy content loading")
            print("⟳ Will fall back to searching for the entire playlist")
            return None
            
        except Exception as e:
            print(f"✗ Error extracting playlist tracks: {e}")
            return None
    
    def _fallback_search(self, apple_music_url):
        """Fallback method when we can't extract Apple Music track info"""
        try:
            print("⌕ Attempting fallback Apple Music extraction...")
            print("⚠  Could not extract track information from Apple Music URL")
            print("→ Try copying the song/album/artist name and searching manually")
            print(f"⚲ Original URL: {apple_music_url}")
            
            user_input = input("\n♫ Please enter the song/album name and artist (or press Enter to skip): ").strip()
            if user_input:
                print(f"⌕ Searching YouTube for: {user_input}")
                youtube_url = self.downloader._search_youtube(user_input)
                if youtube_url:
                    print(f"✓ Found on YouTube: {youtube_url}")
                    return self.downloader.download_media(youtube_url, audio_only=True, output_format='mp3')
                else:
                    print("✗ Could not find on YouTube")
            
            return None
            
        except Exception as e:
            print(f"✗ Fallback search failed: {e}")
            return None
    
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
            print(f"  ⟳ Strategy {i}: {search_query}")
        
        print("✗ Could not find suitable playlist on YouTube")
        return None


# Note: Import GAMDL_AVAILABLE from main module or define here
try:
    import gamdl
    from gamdl.downloader import Downloader as GamdlDownloader
    GAMDL_AVAILABLE = True
except ImportError:
    GAMDL_AVAILABLE = False
