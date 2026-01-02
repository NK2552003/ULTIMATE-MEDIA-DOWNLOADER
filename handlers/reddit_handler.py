#!/usr/bin/env python3
"""
Reddit Handler Module
Handles downloading videos, images, and GIFs from Reddit posts and user profiles.
Supports username-based bulk downloads with ZIP creation.
Uses PRAW (Python Reddit API Wrapper) and web scraping.
"""

import os
import re
import json
import time
import random
import zipfile
import warnings
from pathlib import Path
from typing import Optional, Dict, Any, List
from urllib.parse import urlparse, urljoin
from datetime import datetime

warnings.filterwarnings('ignore')

try:
    import requests
    from requests.adapters import HTTPAdapter
    from urllib3.util.retry import Retry
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

try:
    from bs4 import BeautifulSoup
    BS4_AVAILABLE = True
except ImportError:
    BS4_AVAILABLE = False

try:
    import praw
    PRAW_AVAILABLE = True
except ImportError:
    PRAW_AVAILABLE = False

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TimeRemainingColumn, TimeElapsedColumn
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

try:
    import cloudscraper
    CLOUDSCRAPER_AVAILABLE = True
except ImportError:
    CLOUDSCRAPER_AVAILABLE = False

try:
    import yt_dlp
    YT_DLP_AVAILABLE = True
except ImportError:
    YT_DLP_AVAILABLE = False

from utils.utils import sanitize_filename
from utils.ui_components import Icons, Messages


class RedditHandler:
    """Handles Reddit video, image, and GIF downloads"""
    
    SUPPORTED_DOMAINS = [
        'reddit.com',
        'www.reddit.com',
        'old.reddit.com',
        'new.reddit.com',
        'redd.it',
        'v.redd.it',
        'i.redd.it',
    ]
    
    # Rotating IP addresses using proxies
    PROXY_LIST = [
        # Add your proxy servers here
        # Format: 'http://ip:port' or 'http://user:pass@ip:port'
    ]
    
    USER_AGENTS = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    ]
    
    def __init__(self, downloader):
        """Initialize Reddit handler
        
        Args:
            downloader: Reference to main downloader instance
        """
        self.downloader = downloader
        self.console = Console() if RICH_AVAILABLE else None
        self.session = self._create_session()
        self.reddit = None
        
        # Try to initialize PRAW if credentials are available
        self._init_praw()
        
    def _create_session(self):
        """Create a requests session with retry strategy"""
        if not REQUESTS_AVAILABLE:
            return None
            
        session = cloudscraper.create_scraper() if CLOUDSCRAPER_AVAILABLE else requests.Session()
        
        # Configure retry strategy
        retry_strategy = Retry(
            total=5,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        return session
    
    def _init_praw(self):
        """Initialize PRAW (Python Reddit API Wrapper)"""
        if not PRAW_AVAILABLE:
            return
        
        try:
            client_id = os.environ.get('REDDIT_CLIENT_ID')
            client_secret = os.environ.get('REDDIT_CLIENT_SECRET')
            user_agent = os.environ.get('REDDIT_USER_AGENT', 'python:ultimate-downloader:v1.0')
            
            if client_id and client_secret:
                self.reddit = praw.Reddit(
                    client_id=client_id,
                    client_secret=client_secret,
                    user_agent=user_agent
                )
        except Exception as e:
            if self.console:
                self.console.print(f"[yellow]Warning: Could not initialize Reddit API: {e}[/yellow]")
            self.reddit = None
    
    def _get_random_proxy(self):
        """Get a random proxy from the list"""
        if self.PROXY_LIST:
            return random.choice(self.PROXY_LIST)
        return None
    
    def _get_headers(self, for_media=False):
        """Get randomized headers
        
        Args:
            for_media: If True, returns headers optimized for media downloads
        """
        base_headers = {
            'User-Agent': random.choice(self.USER_AGENTS),
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
        }
        
        if for_media:
            # Headers optimized for media downloads from Reddit
            base_headers.update({
                'Accept': 'image/webp,image/apng,image/*,*/*;q=0.8',
                'Referer': 'https://www.reddit.com/',
                'Origin': 'https://www.reddit.com',
                'Sec-Fetch-Dest': 'image',
                'Sec-Fetch-Mode': 'no-cors',
                'Sec-Fetch-Site': 'same-site',
            })
        else:
            base_headers['Accept'] = 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
        
        return base_headers
    
    def is_supported_url(self, url: str) -> bool:
        """Check if URL is from Reddit
        
        Args:
            url: URL to check
            
        Returns:
            True if supported, False otherwise
        """
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            return any(supported in domain for supported in self.SUPPORTED_DOMAINS)
        except:
            return False
    
    def extract_username(self, url: str) -> Optional[str]:
        """Extract Reddit username from URL
        
        Args:
            url: Reddit profile or user URL
            
        Returns:
            Username if found, None otherwise
        """
        patterns = [
            r'reddit\.com/user/([^/\?]+)',
            r'reddit\.com/u/([^/\?]+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None
    
    def extract_subreddit(self, url: str) -> Optional[str]:
        """Extract subreddit name from URL
        
        Args:
            url: Reddit subreddit URL
            
        Returns:
            Subreddit name if found, None otherwise
        """
        patterns = [
            r'reddit\.com/r/([^/\?]+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None
    
    def get_user_posts_api(self, username: str, limit: int = 100) -> List[Dict]:
        """Get user posts using PRAW API
        
        Args:
            username: Reddit username
            limit: Maximum number of posts
            
        Returns:
            List of post dictionaries
        """
        if not self.reddit:
            return []
        
        try:
            user = self.reddit.redditor(username)
            posts = []
            
            for submission in user.submissions.new(limit=limit):
                post_data = {
                    'id': submission.id,
                    'title': submission.title,
                    'url': submission.url,
                    'permalink': f"https://reddit.com{submission.permalink}",
                    'subreddit': submission.subreddit.display_name,
                    'created_utc': submission.created_utc,
                    'is_video': submission.is_video,
                }
                posts.append(post_data)
            
            return posts
            
        except Exception as e:
            if self.console:
                self.console.print(f"[yellow]Warning: API error: {e}[/yellow]")
            return []
    
    def get_subreddit_posts_scraping(self, subreddit: str, limit: int = 100) -> List[Dict]:
        """Get posts from a subreddit using web scraping
        
        Args:
            subreddit: Subreddit name (without r/)
            limit: Maximum number of posts
            
        Returns:
            List of post dictionaries
        """
        posts = []
        
        try:
            # Try multiple approaches
            # Approach 1: Try old.reddit.com JSON API
            url = f"https://old.reddit.com/r/{subreddit}/.json?limit={limit}"
            
            proxy = self._get_random_proxy()
            proxies = {'http': proxy, 'https': proxy} if proxy else None
            
            # Use better headers that mimic a real browser
            headers = self._get_headers()
            headers['User-Agent'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            headers['Accept'] = 'application/json, text/javascript, */*; q=0.01'
            headers['X-Requested-With'] = 'XMLHttpRequest'
            headers['Referer'] = f'https://old.reddit.com/r/{subreddit}/'
            
            try:
                response = self.session.get(
                    url,
                    headers=headers,
                    proxies=proxies,
                    timeout=15,
                    allow_redirects=True
                )
                response.raise_for_status()
                
                data = response.json()
                
                if 'data' in data and 'children' in data['data']:
                    for child in data['data']['children']:
                        post = child['data']
                        post_data = {
                            'id': post.get('id'),
                            'title': post.get('title'),
                            'url': post.get('url'),
                            'permalink': f"https://reddit.com{post.get('permalink')}",
                            'subreddit': post.get('subreddit'),
                            'created_utc': post.get('created_utc'),
                            'is_video': post.get('is_video', False),
                        }
                        posts.append(post_data)
                
                if posts:
                    return posts
                    
            except Exception as e:
                if self.console:
                    self.console.print(f"[yellow]JSON API failed: {e}[/yellow]")
            
            # Approach 2: Parse HTML directly with BeautifulSoup
            if not posts and BS4_AVAILABLE:
                if self.console:
                    self.console.print(f"[cyan]Trying HTML parsing...[/cyan]")
                
                html_url = f"https://old.reddit.com/r/{subreddit}/"
                
                response = self.session.get(
                    html_url,
                    headers={
                        'User-Agent': random.choice(self.USER_AGENTS),
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                        'Accept-Language': 'en-US,en;q=0.9',
                        'Referer': 'https://old.reddit.com/',
                    },
                    proxies=proxies,
                    timeout=15
                )
                response.raise_for_status()
                
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Find all post links
                post_divs = soup.find_all('div', class_='thing')
                
                for div in post_divs[:limit]:
                    try:
                        post_id = div.get('data-id', '')
                        permalink = div.get('data-permalink', '')
                        url = div.get('data-url', '')
                        
                        # Get title
                        title_element = div.find('a', class_='title')
                        title = title_element.text.strip() if title_element else 'Untitled'
                        
                        # Get subreddit
                        subreddit_element = div.find('a', class_='subreddit')
                        subreddit_name = subreddit_element.text.replace('r/', '') if subreddit_element else subreddit
                        
                        if post_id and permalink:
                            post_data = {
                                'id': post_id,
                                'title': title,
                                'url': url,
                                'permalink': f"https://reddit.com{permalink}",
                                'subreddit': subreddit_name,
                                'created_utc': time.time(),
                                'is_video': 'v.redd.it' in url,
                            }
                            posts.append(post_data)
                    except Exception as e:
                        if self.console:
                            self.console.print(f"[yellow]Error parsing post: {e}[/yellow]")
                        continue
            
            return posts
            
        except Exception as e:
            if self.console:
                self.console.print(f"[yellow]Warning: Scraping error: {e}[/yellow]")
            return []
    
    def get_user_posts_scraping(self, username: str, limit: int = 100) -> List[Dict]:
        """Get user posts using web scraping (fallback method)
        
        Args:
            username: Reddit username
            limit: Maximum number of posts
            
        Returns:
            List of post dictionaries
        """
        posts = []
        
        try:
            # Try multiple approaches
            # Approach 1: Try old.reddit.com JSON API with better headers
            url = f"https://old.reddit.com/user/{username}/submitted/.json?limit={limit}"
            
            proxy = self._get_random_proxy()
            proxies = {'http': proxy, 'https': proxy} if proxy else None
            
            # Use better headers that mimic a real browser
            headers = self._get_headers()
            headers['User-Agent'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            headers['Accept'] = 'application/json, text/javascript, */*; q=0.01'
            headers['X-Requested-With'] = 'XMLHttpRequest'
            headers['Referer'] = f'https://old.reddit.com/user/{username}/'
            
            try:
                response = self.session.get(
                    url,
                    headers=headers,
                    proxies=proxies,
                    timeout=15,
                    allow_redirects=True
                )
                response.raise_for_status()
                
                data = response.json()
                
                if 'data' in data and 'children' in data['data']:
                    for child in data['data']['children']:
                        post = child['data']
                        post_data = {
                            'id': post.get('id'),
                            'title': post.get('title'),
                            'url': post.get('url'),
                            'permalink': f"https://reddit.com{post.get('permalink')}",
                            'subreddit': post.get('subreddit'),
                            'created_utc': post.get('created_utc'),
                            'is_video': post.get('is_video', False),
                        }
                        posts.append(post_data)
                
                if posts:
                    return posts
                    
            except Exception as e:
                if self.console:
                    self.console.print(f"[yellow]JSON API failed: {e}[/yellow]")
            
            # Approach 2: Parse HTML directly with BeautifulSoup
            if not posts and BS4_AVAILABLE:
                if self.console:
                    self.console.print(f"[cyan]Trying HTML parsing...[/cyan]")
                
                html_url = f"https://old.reddit.com/user/{username}/submitted/"
                
                response = self.session.get(
                    html_url,
                    headers={
                        'User-Agent': random.choice(self.USER_AGENTS),
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                        'Accept-Language': 'en-US,en;q=0.9',
                        'Referer': 'https://old.reddit.com/',
                    },
                    proxies=proxies,
                    timeout=15
                )
                response.raise_for_status()
                
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Find all post links
                post_divs = soup.find_all('div', class_='thing')
                
                for div in post_divs[:limit]:
                    try:
                        post_id = div.get('data-id', '')
                        permalink = div.get('data-permalink', '')
                        url = div.get('data-url', '')
                        
                        # Get title
                        title_element = div.find('a', class_='title')
                        title = title_element.text.strip() if title_element else 'Untitled'
                        
                        # Get subreddit
                        subreddit_element = div.find('a', class_='subreddit')
                        subreddit = subreddit_element.text.replace('r/', '') if subreddit_element else ''
                        
                        if post_id and permalink:
                            post_data = {
                                'id': post_id,
                                'title': title,
                                'url': url,
                                'permalink': f"https://reddit.com{permalink}",
                                'subreddit': subreddit,
                                'created_utc': time.time(),
                                'is_video': 'v.redd.it' in url,
                            }
                            posts.append(post_data)
                    except Exception as e:
                        if self.console:
                            self.console.print(f"[yellow]Error parsing post: {e}[/yellow]")
                        continue
            
            return posts
            
        except Exception as e:
            if self.console:
                self.console.print(f"[yellow]Warning: Scraping error: {e}[/yellow]")
            return []
    
    def extract_media_urls(self, post_url: str) -> Dict[str, List[str]]:
        """Extract media URLs from a Reddit post
        
        Args:
            post_url: URL of the Reddit post
            
        Returns:
            Dictionary with 'videos', 'images', and 'gifs' lists
        """
        media = {'videos': [], 'images': [], 'gifs': []}
        
        try:
            # Get JSON data from Reddit
            json_url = post_url.rstrip('/') + '.json'
            
            proxy = self._get_random_proxy()
            proxies = {'http': proxy, 'https': proxy} if proxy else None
            
            # Try JSON API first
            try:
                response = self.session.get(
                    json_url,
                    headers={
                        'User-Agent': random.choice(self.USER_AGENTS),
                        'Accept': 'application/json, text/javascript, */*; q=0.01',
                        'Accept-Language': 'en-US,en;q=0.9',
                        'X-Requested-With': 'XMLHttpRequest',
                        'Referer': post_url,
                    },
                    proxies=proxies,
                    timeout=15
                )
                response.raise_for_status()
                
                data = response.json()
                
                # Navigate through Reddit's JSON structure
                if isinstance(data, list) and len(data) > 0:
                    post_data = data[0]['data']['children'][0]['data']
                    
                    # Check for video
                    if post_data.get('is_video'):
                        if 'media' in post_data and post_data['media']:
                            video_url = post_data['media'].get('reddit_video', {}).get('fallback_url')
                            if video_url:
                                media['videos'].append(video_url)
                    
                    # Check for images
                    url = post_data.get('url', '')
                    
                    # Direct image links
                    if any(url.endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp']):
                        if url.endswith('.gif') or 'gif' in url:
                            media['gifs'].append(url)
                        else:
                            media['images'].append(url)
                    
                    # i.redd.it images
                    elif 'i.redd.it' in url:
                        media['images'].append(url)
                    
                    # imgur links
                    elif 'imgur.com' in url:
                        if '/a/' not in url and '/gallery/' not in url:
                            # Single image
                            if not url.endswith(('.jpg', '.png', '.gif')):
                                url = url + '.jpg'
                            media['images'].append(url)
                    
                    # Check for gallery (priority: use original i.redd.it URLs)
                    if 'gallery_data' in post_data:
                        gallery_items = post_data.get('gallery_data', {}).get('items', [])
                        media_metadata = post_data.get('media_metadata', {})
                        
                        for item in gallery_items:
                            media_id = item.get('media_id')
                            if media_id in media_metadata:
                                metadata = media_metadata[media_id]
                                # Try to get the original source URL first (i.redd.it)
                                if 'p' in metadata and metadata['p']:
                                    # Get the highest resolution preview
                                    largest = max(metadata['p'], key=lambda x: x.get('x', 0) * x.get('y', 0))
                                    img_url = largest.get('u', '').replace('&amp;', '&')
                                    if img_url:
                                        # Convert preview URL to original i.redd.it URL
                                        img_url = img_url.replace('preview.redd.it', 'i.redd.it')
                                        # Remove size parameters
                                        if '?' in img_url:
                                            base_url = img_url.split('?')[0]
                                            media['images'].append(base_url)
                                        else:
                                            media['images'].append(img_url)
                                elif 's' in metadata and 'u' in metadata['s']:
                                    img_url = metadata['s']['u'].replace('&amp;', '&')
                                    # Try to convert to i.redd.it
                                    img_url = img_url.replace('preview.redd.it', 'i.redd.it')
                                    if '?' in img_url:
                                        base_url = img_url.split('?')[0]
                                        media['images'].append(base_url)
                                    else:
                                        media['images'].append(img_url)
                    
                    # Check for preview images (only if no gallery found)
                    if 'preview' in post_data and not media['images']:
                        images = post_data['preview'].get('images', [])
                        for img_data in images:
                            if 'source' in img_data:
                                img_url = img_data['source'].get('url', '').replace('&amp;', '&')
                                # Convert preview to i.redd.it
                                img_url = img_url.replace('preview.redd.it', 'i.redd.it')
                                # Remove query parameters for cleaner URLs
                                if '?' in img_url:
                                    img_url = img_url.split('?')[0]
                                if img_url and img_url not in media['images']:
                                    media['images'].append(img_url)
                
                # If we got media, return it
                if media['videos'] or media['images'] or media['gifs']:
                    return media
                    
            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 403:
                    if self.console:
                        self.console.print(f"[yellow]JSON API blocked (403), trying HTML parsing...[/yellow]")
                else:
                    raise
            
            # Fallback: Parse HTML if JSON fails
            if BS4_AVAILABLE and not (media['videos'] or media['images'] or media['gifs']):
                # Convert to old.reddit.com for easier parsing
                if 'old.reddit.com' not in post_url:
                    old_reddit_url = post_url.replace('www.reddit.com', 'old.reddit.com').replace('reddit.com', 'old.reddit.com')
                else:
                    old_reddit_url = post_url
                
                response = self.session.get(
                    old_reddit_url,
                    headers={
                        'User-Agent': random.choice(self.USER_AGENTS),
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                        'Accept-Language': 'en-US,en;q=0.9',
                        'Referer': 'https://old.reddit.com/',
                    },
                    proxies=proxies,
                    timeout=15
                )
                response.raise_for_status()
                
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Look for i.redd.it images in the HTML
                for link in soup.find_all('a'):
                    href = link.get('href', '')
                    if 'i.redd.it' in href:
                        # Clean up URL
                        if '?' in href:
                            href = href.split('?')[0]
                        if href not in media['images']:
                            media['images'].append(href)
                
                # Look for v.redd.it videos
                for link in soup.find_all('a'):
                    href = link.get('href', '')
                    if 'v.redd.it' in href:
                        if href not in media['videos']:
                            media['videos'].append(href)
                
                # Look for img tags with i.redd.it sources
                for img in soup.find_all('img'):
                    src = img.get('src', '')
                    if 'i.redd.it' in src or 'preview.redd.it' in src:
                        # Convert preview to i.redd.it
                        src = src.replace('preview.redd.it', 'i.redd.it')
                        if '?' in src:
                            src = src.split('?')[0]
                        if src not in media['images']:
                            media['images'].append(src)
            
            return media
            
        except Exception as e:
            if self.console:
                self.console.print(f"[yellow]Warning: Error extracting media: {e}[/yellow]")
            return media
    
    def download_video_ytdlp(self, url: str, output_path: Path, silent: bool = False) -> bool:
        """Download Reddit video using yt-dlp
        
        Args:
            url: URL of the video
            output_path: Path to save the file
            silent: If True, suppress all error messages
            
        Returns:
            True if successful, False otherwise
        """
        if not YT_DLP_AVAILABLE:
            return False
        
        try:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            ydl_opts = {
                # Use bestvideo+bestaudio for Reddit (they have separate streams)
                # Fallback to best if combined stream is available
                'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
                'outtmpl': str(output_path),
                'quiet': silent,
                'no_warnings': silent,
                'no_color': True,
                'noprogress': True,
                'merge_output_format': 'mp4',
            }
            
            proxy = self._get_random_proxy()
            if proxy:
                ydl_opts['proxy'] = proxy
            
            # Only suppress stderr if silent mode is requested
            if silent:
                import sys
                from io import StringIO
                
                old_stderr = sys.stderr
                sys.stderr = StringIO()
                
                try:
                    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                        ydl.download([url])
                finally:
                    sys.stderr = old_stderr
            else:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([url])
            
            # Check if file was created
            return output_path.exists() and output_path.stat().st_size > 0
            
        except Exception as e:
            # Restore stderr if it was redirected
            import sys
            if 'old_stderr' in locals():
                sys.stderr = old_stderr
            
            # Only print errors if not silent and file doesn't exist
            if not silent and not output_path.exists():
                if self.console:
                    self.console.print(f"[yellow]yt-dlp download failed: {e}[/yellow]")
            # If file exists despite error, consider it successful
            return output_path.exists() and output_path.stat().st_size > 0
    
    def download_media(self, url: str, output_path: Path, media_type: str = 'image', silent: bool = False) -> bool:
        """Download a single media file
        
        Args:
            url: URL of the media
            output_path: Path to save the file
            media_type: 'video', 'image', or 'gif'
            silent: If True, suppress success/error messages
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Skip external-i.redd.it (these are just preview thumbnails)
            if 'external-i.redd.it' in url:
                return False
            
            # For Reddit videos, try yt-dlp first
            if media_type == 'video' and 'v.redd.it' in url:
                # Extract post URL from video URL
                post_url = url.split('/DASH_')[0]
                success = self.download_video_ytdlp(post_url, output_path, silent=True)
                if success and not silent:
                    if self.console:
                        self.console.print(f"[green]Downloaded: {output_path.name}[/green]")
                return success
            
            # Standard download for images and gifs
            proxy = self._get_random_proxy()
            proxies = {'http': proxy, 'https': proxy} if proxy else None
            
            # Use media-optimized headers
            headers = self._get_headers(for_media=True)
            
            response = self.session.get(
                url,
                headers=headers,
                proxies=proxies,
                stream=True,
                timeout=30,
                allow_redirects=True
            )
            response.raise_for_status()
            
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            
            if not silent and self.console:
                self.console.print(f"[green]Downloaded: {output_path.name}[/green]")
            
            return True
            
        except Exception as e:
            # Only show error if not silent and not a known ignorable error
            if not silent and 'external-i.redd.it' not in url:
                if self.console:
                    self.console.print(f"[red]✗ Failed to download {output_path.name}[/red]")
            return False
    
    def download_post(self, post_url: str, output_dir: Path, download_videos: bool = True, 
                     download_images: bool = True, progress_task=None, progress=None) -> Dict[str, Any]:
        """Download all media from a Reddit post
        
        Args:
            post_url: URL of the post
            output_dir: Directory to save media
            download_videos: Whether to download videos
            download_images: Whether to download images/gifs
            progress_task: Rich progress task ID
            progress: Rich progress instance
            
        Returns:
            Dictionary with download statistics
        """
        stats = {'videos': 0, 'images': 0, 'gifs': 0, 'failed': 0, 'total_size': 0}
        
        try:
            # Extract media
            media = self.extract_media_urls(post_url)
            
            # Generate folder name from post ID
            post_id = post_url.split('/')[-3] if '/comments/' in post_url else post_url.split('/')[-1]
            post_dir = output_dir / f"post_{post_id}"
            post_dir.mkdir(parents=True, exist_ok=True)
            
            # Download videos - for Reddit videos, use yt-dlp with post URL
            if download_videos and media['videos']:
                for idx, video_url in enumerate(media['videos'], 1):
                    filename = f"video_{idx}.mp4"
                    output_path = post_dir / filename
                    
                    # For v.redd.it videos, use yt-dlp with the post URL
                    if 'v.redd.it' in video_url:
                        success = self.download_video_ytdlp(post_url, output_path, silent=True)
                        if success:
                            stats['videos'] += 1
                            if output_path.exists():
                                stats['total_size'] += output_path.stat().st_size
                            if progress and progress_task is not None:
                                progress.update(progress_task, advance=1)
                        else:
                            stats['failed'] += 1
                    else:
                        # Other video hosts
                        if self.download_media(video_url, output_path, 'video', silent=True):
                            stats['videos'] += 1
                            if output_path.exists():
                                stats['total_size'] += output_path.stat().st_size
                            if progress and progress_task is not None:
                                progress.update(progress_task, advance=1)
                        else:
                            stats['failed'] += 1
                    
                    time.sleep(random.uniform(0.3, 0.8))
            
            # Download images
            if download_images:
                for idx, img_url in enumerate(media['images'], 1):
                    ext = 'jpg'
                    if img_url:
                        ext = img_url.split('.')[-1].split('?')[0][:4]
                        if ext not in ['jpg', 'jpeg', 'png', 'webp']:
                            ext = 'jpg'
                    
                    filename = f"image_{idx}.{ext}"
                    output_path = post_dir / filename
                    
                    if self.download_media(img_url, output_path, 'image', silent=True):
                        stats['images'] += 1
                        if output_path.exists():
                            stats['total_size'] += output_path.stat().st_size
                        if progress and progress_task is not None:
                            progress.update(progress_task, advance=1)
                    else:
                        stats['failed'] += 1
                    
                    time.sleep(random.uniform(0.3, 0.8))
                
                # Download GIFs
                for idx, gif_url in enumerate(media['gifs'], 1):
                    filename = f"gif_{idx}.gif"
                    output_path = post_dir / filename
                    
                    if self.download_media(gif_url, output_path, 'gif', silent=True):
                        stats['gifs'] += 1
                        if output_path.exists():
                            stats['total_size'] += output_path.stat().st_size
                        if progress and progress_task is not None:
                            progress.update(progress_task, advance=1)
                    else:
                        stats['failed'] += 1
                    
                    time.sleep(random.uniform(0.3, 0.8))
            
            return stats
            
        except Exception as e:
            if self.console:
                self.console.print(f"[red]Error downloading post: {e}[/red]")
            return stats
            
            # Download GIFs
            for idx, gif_url in enumerate(media['gifs'], 1):
                filename = f"gif_{idx}.gif"
                output_path = post_dir / filename
                
                if self.download_media(gif_url, output_path, 'gif'):
                    stats['gifs'] += 1
                else:
                    stats['failed'] += 1
                
                time.sleep(random.uniform(0.5, 1.5))
            
            return stats
            
        except Exception as e:
            if self.console:
                self.console.print(f"[red]Error downloading post: {e}[/red]")
            return stats
    
    def download_by_username(self, username: str, output_dir: Path, max_posts: int = 100, create_zip: bool = False) -> bool:
        """Download all media from a Reddit user's posts
        
        Args:
            username: Reddit username (without u/)
            output_dir: Directory to save downloads
            max_posts: Maximum number of posts to download
            create_zip: Whether to create a ZIP archive (default: False)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Interactive prompts for user preferences
            if self.console:
                self.console.print(f"\n[bold cyan]Reddit User Download: u/{username}[/bold cyan]\n")
                
                # Ask what to download
                self.console.print("[yellow]What would you like to download?[/yellow]")
                self.console.print("  [cyan]1.[/cyan] Videos only")
                self.console.print("  [cyan]2.[/cyan] Images only")
                self.console.print("  [cyan]3.[/cyan] Both (videos + images)")
                
                choice = input("\n[?] Enter your choice (1-3) [default: 3]: ").strip() or "3"
                
                download_videos = choice in ["1", "3"]
                download_images = choice in ["2", "3"]
                
                # Ask how many
                self.console.print(f"\n[yellow]How many posts would you like to download?[/yellow]")
                self.console.print(f"  [cyan]•[/cyan] Enter a number (e.g., 10, 25, 50)")
                self.console.print(f"  [cyan]•[/cyan] Press Enter for ALL posts")
                
                limit_input = input(f"\n[?] Enter number [default: ALL]: ").strip()
                
                if limit_input and limit_input.isdigit():
                    max_posts = int(limit_input)
                    self.console.print(f"\n[green]Will download first {max_posts} posts[/green]")
                else:
                    self.console.print(f"\n[green]Will download ALL available posts[/green]")
                
                self.console.print(f"\n[dim]───────────────────────────────────────────[/dim]\n")
            else:
                download_videos = True
                download_images = True
            
            # Create output directory
            user_dir = output_dir / f"reddit_{username}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            user_dir.mkdir(parents=True, exist_ok=True)
            
            # Try API first, fallback to scraping
            if self.console:
                self.console.print("[cyan]Fetching user posts...[/cyan]")
            
            posts = self.get_user_posts_api(username, max_posts)
            
            if not posts:
                if self.console:
                    self.console.print("[yellow]API unavailable, using web scraping...[/yellow]")
                posts = self.get_user_posts_scraping(username, max_posts)
            
            if not posts:
                if self.console:
                    self.console.print("[red]No posts found or unable to access user[/red]")
                return False
            
            if self.console:
                self.console.print(f"[green]✓ Found {len(posts)} posts[/green]\n")
            
            # Download media from each post with progress bar
            total_stats = {'videos': 0, 'images': 0, 'gifs': 0, 'failed': 0}
            
            if RICH_AVAILABLE and self.console:
                from rich.progress import Progress, BarColumn, TextColumn, TimeRemainingColumn, TimeElapsedColumn
                
                with Progress(
                    TextColumn("[progress.description]{task.description}"),
                    BarColumn(complete_style="green", finished_style="bold green"),
                    TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
                    TextColumn("•"),
                    TextColumn("[cyan]{task.completed}/{task.total}[/cyan] posts"),
                    TextColumn("•"),
                    TimeElapsedColumn(),
                    TextColumn("•"),
                    TimeRemainingColumn(),
                    console=self.console
                ) as progress:
                    task = progress.add_task(
                        f"[cyan]Downloading from u/{username}[/cyan]",
                        total=len(posts)
                    )
                    
                    for idx, post in enumerate(posts, 1):
                        stats = self.download_post(
                            post['permalink'], 
                            user_dir,
                            download_videos=download_videos,
                            download_images=download_images,
                            progress_task=None,  # Don't update per-file progress
                            progress=None
                        )
                        total_stats['videos'] += stats['videos']
                        total_stats['images'] += stats['images']
                        total_stats['gifs'] += stats['gifs']
                        total_stats['failed'] += stats['failed']
                        
                        progress.update(task, advance=1)
                        
                        # Random delay between posts
                        if idx < len(posts):
                            time.sleep(random.uniform(0.5, 1.5))
            else:
                # Fallback without progress bar
                for idx, post in enumerate(posts, 1):
                    if self.console:
                        self.console.print(f"[cyan]Post {idx}/{len(posts)}[/cyan]")
                    
                    stats = self.download_post(
                        post['permalink'], 
                        user_dir,
                        download_videos=download_videos,
                        download_images=download_images
                    )
                    total_stats['videos'] += stats['videos']
                    total_stats['images'] += stats['images']
                    total_stats['gifs'] += stats['gifs']
                    total_stats['failed'] += stats['failed']
                    total_stats['total_size'] += stats.get('total_size', 0)
                    
                    if idx < len(posts):
                        time.sleep(random.uniform(0.5, 1.5))
            
            # Display summary
            if self.console:
                # Format file size
                size_mb = total_stats['total_size'] / (1024 * 1024)
                if size_mb >= 1024:
                    size_str = f"{size_mb / 1024:.2f} GB"
                else:
                    size_str = f"{size_mb:.2f} MB"
                
                summary_text = f"[bold green]Download Complete![/bold green]\n\n"
                summary_text += f"[cyan]Statistics:[/cyan]\n"
                summary_text += f"  Videos: [bold]{total_stats['videos']}[/bold]\n"
                summary_text += f"  Images: [bold]{total_stats['images']}[/bold]\n"
                summary_text += f"  GIFs: [bold]{total_stats['gifs']}[/bold]\n"
                summary_text += f"  Total Size: [bold]{size_str}[/bold]\n"
                summary_text += f"\n[cyan]Location:[/cyan]\n"
                summary_text += f"  {user_dir}"
                
                self.console.print(Panel.fit(
                    summary_text,
                    border_style="green",
                    padding=(1, 2)
                ))
            
            return True
            
        except KeyboardInterrupt:
            if self.console:
                self.console.print("\n[yellow]Download interrupted by user[/yellow]")
            return False
        except Exception as e:
            if self.console:
                self.console.print(f"[red]Error in username download: {e}[/red]")
            return False
    
    def download_by_subreddit(self, subreddit: str, output_dir: Path, max_posts: int = 100, create_zip: bool = False) -> bool:
        """Download all media from a subreddit's posts
        
        Args:
            subreddit: Subreddit name (without r/)
            output_dir: Directory to save downloads
            max_posts: Maximum number of posts to download
            create_zip: Whether to create a ZIP archive (default: False)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Interactive prompts for user preferences
            if self.console:
                self.console.print(f"\n[bold cyan]Reddit Subreddit Download: r/{subreddit}[/bold cyan]\n")
                
                # Ask what to download
                self.console.print("[yellow]What would you like to download?[/yellow]")
                self.console.print("  [cyan]1.[/cyan] Videos only")
                self.console.print("  [cyan]2.[/cyan] Images only")
                self.console.print("  [cyan]3.[/cyan] Both (videos + images)")
                
                choice = input("\n[?] Enter your choice (1-3) [default: 3]: ").strip() or "3"
                
                download_videos = choice in ["1", "3"]
                download_images = choice in ["2", "3"]
                
                # Ask how many
                self.console.print(f"\n[yellow]How many posts would you like to download?[/yellow]")
                self.console.print(f"  [cyan]•[/cyan] Enter a number (e.g., 10, 25, 50)")
                self.console.print(f"  [cyan]•[/cyan] Press Enter for ALL posts (up to 100)")
                
                limit_input = input(f"\n[?] Enter number [default: 25]: ").strip()
                
                if limit_input and limit_input.isdigit():
                    max_posts = int(limit_input)
                    self.console.print(f"\n[green]Will download first {max_posts} posts[/green]")
                else:
                    max_posts = 25  # Default for subreddits
                    self.console.print(f"\n[green]Will download first 25 posts[/green]")
                
                self.console.print(f"\n[dim]───────────────────────────────────────────[/dim]\n")
            else:
                download_videos = True
                download_images = True
            
            # Create output directory
            sub_dir = output_dir / f"reddit_r_{subreddit}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            sub_dir.mkdir(parents=True, exist_ok=True)
            
            # Get subreddit posts
            if self.console:
                self.console.print("[cyan]Fetching subreddit posts...[/cyan]")
            
            posts = self.get_subreddit_posts_scraping(subreddit, max_posts)
            
            if not posts:
                if self.console:
                    self.console.print("[red]❌ No posts found or unable to access subreddit[/red]")
                return False
            
            if self.console:
                self.console.print(f"[green]✓ Found {len(posts)} posts[/green]\n")
            
            # Download media from each post with progress bar
            total_stats = {'videos': 0, 'images': 0, 'gifs': 0, 'failed': 0, 'total_size': 0}
            
            if RICH_AVAILABLE and self.console:
                from rich.progress import Progress, BarColumn, TextColumn, TimeRemainingColumn, TimeElapsedColumn
                
                with Progress(
                    TextColumn("[progress.description]{task.description}"),
                    BarColumn(complete_style="green", finished_style="bold green"),
                    TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
                    TextColumn("•"),
                    TextColumn("[cyan]{task.completed}/{task.total}[/cyan] posts"),
                    TextColumn("•"),
                    TimeElapsedColumn(),
                    TextColumn("•"),
                    TimeRemainingColumn(),
                    console=self.console
                ) as progress:
                    task = progress.add_task(
                        f"[cyan]Downloading from r/{subreddit}[/cyan]",
                        total=len(posts)
                    )
                    
                    for idx, post in enumerate(posts, 1):
                        stats = self.download_post(
                            post['permalink'], 
                            sub_dir,
                            download_videos=download_videos,
                            download_images=download_images,
                            progress_task=None,
                            progress=None
                        )
                        total_stats['videos'] += stats['videos']
                        total_stats['images'] += stats['images']
                        total_stats['gifs'] += stats['gifs']
                        total_stats['failed'] += stats['failed']
                        total_stats['total_size'] += stats.get('total_size', 0)
                        
                        progress.update(task, advance=1)
                        
                        # Random delay between posts
                        if idx < len(posts):
                            time.sleep(random.uniform(0.5, 1.5))
            else:
                # Fallback without progress bar
                for idx, post in enumerate(posts, 1):
                    if self.console:
                        self.console.print(f"[cyan]Post {idx}/{len(posts)}[/cyan]")
                    
                    stats = self.download_post(
                        post['permalink'], 
                        sub_dir,
                        download_videos=download_videos,
                        download_images=download_images
                    )
                    total_stats['videos'] += stats['videos']
                    total_stats['images'] += stats['images']
                    total_stats['gifs'] += stats['gifs']
                    total_stats['failed'] += stats['failed']
                    total_stats['total_size'] += stats.get('total_size', 0)
                    
                    if idx < len(posts):
                        time.sleep(random.uniform(0.5, 1.5))
            
            # Display summary
            if self.console:
                # Format file size
                size_mb = total_stats['total_size'] / (1024 * 1024)
                if size_mb >= 1024:
                    size_str = f"{size_mb / 1024:.2f} GB"
                else:
                    size_str = f"{size_mb:.2f} MB"
                
                summary_text = f"[bold green]Download Complete![/bold green]\n\n"
                summary_text += f"[cyan]Statistics:[/cyan]\n"
                summary_text += f"  Videos: [bold]{total_stats['videos']}[/bold]\n"
                summary_text += f"  Images: [bold]{total_stats['images']}[/bold]\n"
                summary_text += f"  GIFs: [bold]{total_stats['gifs']}[/bold]\n"
                summary_text += f"  Total Size: [bold]{size_str}[/bold]\n"
                summary_text += f"\n[cyan]Location:[/cyan]\n"
                summary_text += f"  {sub_dir}"
                
                self.console.print(Panel.fit(
                    summary_text,
                    border_style="green",
                    padding=(1, 2)
                ))
            
            return True
            
        except KeyboardInterrupt:
            if self.console:
                self.console.print("\n[yellow]Download interrupted by user[/yellow]")
            return False
        except Exception as e:
            if self.console:
                self.console.print(f"[red]Error in subreddit download: {e}[/red]")
            return False
    
    def download(self, url: str, output_dir: Path = None) -> bool:
        """Main download method
        
        Args:
            url: Reddit URL (post, user, or subreddit)
            output_dir: Directory to save downloads
            
        Returns:
            True if successful, False otherwise
        """
        if not output_dir:
            output_dir = Path.cwd() / 'downloads' / 'reddit'
        
        try:
            # Check if it's a username/profile URL
            username = self.extract_username(url)
            
            if username and '/comments/' not in url:
                # It's a user profile, download all posts
                if self.console:
                    self.console.print(f"[cyan]Detected user profile: u/{username}[/cyan]")
                result = self.download_by_username(username, output_dir)
                # Return the result as-is (boolean or dict)
                return result if result else False
            elif '/comments/' in url:
                # It's a single post
                if self.console:
                    self.console.print(f"[cyan]Detected single post[/cyan]")
                stats = self.download_post(url, output_dir)
                # Return True if any media was downloaded
                return (stats['videos'] + stats['images'] + stats['gifs']) > 0
            else:
                # Check if it's a subreddit
                subreddit = self.extract_subreddit(url)
                if subreddit:
                    if self.console:
                        self.console.print(f"[cyan]Detected subreddit: r/{subreddit}[/cyan]")
                    return self.download_by_subreddit(subreddit, output_dir)
                
                if self.console:
                    self.console.print(f"[yellow]Could not determine Reddit content type[/yellow]")
                # Try as a post anyway
                stats = self.download_post(url, output_dir)
                return (stats['videos'] + stats['images'] + stats['gifs']) > 0
            
        except Exception as e:
            if self.console:
                self.console.print(f"[red]Error: {e}[/red]")
                import traceback
                self.console.print(f"[red]{traceback.format_exc()}[/red]")
            return False
