#!/usr/bin/env python3
"""
Tumblr Handler Module
Handles downloading images and videos from Tumblr blogs using the Tumblr API
and fallback methods for media extraction.
"""

import os
import re
import warnings
from pathlib import Path
from typing import Optional, Dict, Any, List, Generator
from urllib.parse import urlparse, parse_qs, urljoin, urlencode
import time

# Suppress warnings
warnings.filterwarnings('ignore')

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

try:
    from bs4 import BeautifulSoup
    BS4_AVAILABLE = True
except ImportError:
    BS4_AVAILABLE = False

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

try:
    import yt_dlp
    YT_DLP_AVAILABLE = True
except ImportError:
    YT_DLP_AVAILABLE = False

from utils.utils import sanitize_filename
from utils.ui_components import Icons, Messages


class TumblrAPI:
    """Tumblr API wrapper for fetching blog posts and media"""
    
    BASE_URL = 'https://www.tumblr.com/api'
    
    # Default authorization token (public API token)
    DEFAULT_AUTH = 'Bearer aIcXSOoTtqrzR8L8YEIOmBeW94c3FmbSNSWAUbxsny9KKx5VFh'
    
    DEFAULT_PARAMS = {
        'fields[blogs]': 'name,avatar,title,url,is_adult,description_npf,uuid,can_be_followed,theme',
        'npf': 'true',
        'reblog_info': 'false',
        'include_pinned_posts': 'false',
    }
    
    def __init__(self, session: requests.Session):
        self.session = session
        self.headers = {
            'referer': 'https://www.tumblr.com',
            'authorization': self.DEFAULT_AUTH,
        }
    
    def _call(self, path: str, params: Dict = None, use_default_params: bool = True) -> Dict:
        """Make API call
        
        Args:
            path: API path
            params: Query parameters
            use_default_params: Whether to include default params
            
        Returns:
            API response data
        """
        if params is None:
            params = {}
        
        if use_default_params:
            full_params = self.DEFAULT_PARAMS.copy()
            full_params.update(params)
        else:
            full_params = params
        
        url = f"{self.BASE_URL}{path}"
        if full_params:
            url = f"{url}?{urlencode(full_params)}"
        
        response = self.session.get(url, headers=self.headers)
        data = response.json()
        
        # Check for errors
        errors = data.get('errors', [])
        if errors:
            error = errors[0]
            code = int(error.get('code', 0))
            detail = error.get('detail', 'Unknown error')
            
            if code == 0:
                raise Exception('Blog not found')
            elif code == 4012:
                raise Exception(f'Login required: {detail}')
            else:
                raise Exception(f'API error {code}: {detail}')
        
        response.raise_for_status()
        return data.get('response', {})
    
    def get_blog_info(self, username: str) -> Dict:
        """Get blog information
        
        Args:
            username: Blog username
            
        Returns:
            Blog info dict
        """
        path = f'/v2/blog/{username}/posts'
        data = self._call(path, {})
        return data.get('blog', {})
    
    def get_blog_name(self, username: str) -> str:
        """Get blog display name
        
        Args:
            username: Blog username
            
        Returns:
            Blog title or name
        """
        blog = self.get_blog_info(username)
        return blog.get('title') or blog.get('name') or username
    
    def get_posts(self, username: str, max_posts: int = 100) -> Generator[Dict, None, None]:
        """Get posts from a blog
        
        Args:
            username: Blog username
            max_posts: Maximum number of posts to fetch
            
        Yields:
            Post data dictionaries
        """
        path = f'/v2/blog/{username}/posts'
        params = {}
        seen_ids = set()
        use_default_params = True
        post_count = 0
        
        while post_count < max_posts:
            data = self._call(path, params, use_default_params=use_default_params)
            posts = data.get('posts', [])
            
            if not posts:
                break
            
            for post in posts:
                # Skip ads
                if post.get('object_type') == 'backfill_ad':
                    continue
                
                post_id = post.get('id')
                if post_id in seen_ids:
                    continue
                
                seen_ids.add(post_id)
                post_count += 1
                
                if post_count > max_posts:
                    break
                
                yield post
            
            # Get next page
            links = data.get('links') or data.get('_links', {})
            next_link = links.get('next', {}).get('href')
            
            if next_link:
                path = next_link
                use_default_params = False
                params = {}
            else:
                break
            
            # Rate limiting
            time.sleep(0.5)


class TumblrMedia:
    """Represents a media item from Tumblr"""
    
    def __init__(self, url: str, post_id: str, index: int, media_type: str = 'image'):
        self.url = url
        self.post_id = post_id
        self.index = index
        self.media_type = media_type
        self.filename = self._generate_filename()
    
    def _generate_filename(self) -> str:
        """Generate filename for the media"""
        # Get extension from URL
        ext = '.jpg'  # default
        if '.' in self.url.split('/')[-1]:
            ext = '.' + self.url.split('.')[-1].split('?')[0].lower()
        
        # Normalize extension
        if ext not in ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.mp4', '.webm']:
            if self.media_type == 'video':
                ext = '.mp4'
            else:
                ext = '.jpg'
        
        return f"{self.post_id}_p{self.index}{ext}"


class TumblrHandler:
    """Handles Tumblr blog and media downloads"""
    
    SUPPORTED_DOMAINS = [
        'tumblr.com',
        'www.tumblr.com',
    ]
    
    def __init__(self, downloader):
        """Initialize Tumblr handler with reference to main downloader
        
        Args:
            downloader: Reference to UltimateMediaDownloader instance
        """
        self.downloader = downloader
        self.console = Console() if RICH_AVAILABLE else None
        self.session = None
        self.api = None
        
        # Initialize session
        if REQUESTS_AVAILABLE:
            self._init_session()
    
    def _init_session(self):
        """Initialize requests session"""
        self.session = requests.Session()
        
        # Set user agent
        self.session.headers.update({
            'User-Agent': self.downloader._get_random_user_agent() if hasattr(self.downloader, '_get_random_user_agent') else 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.5',
        })
        
        # Initialize API
        self.api = TumblrAPI(self.session)
    
    @classmethod
    def is_tumblr_url(cls, url: str) -> bool:
        """Check if URL is a Tumblr URL
        
        Args:
            url: URL to check
            
        Returns:
            True if URL is from Tumblr
        """
        url_lower = url.lower()
        return 'tumblr.com' in url_lower
    
    @classmethod
    def fix_url(cls, url: str) -> str:
        """Normalize Tumblr URL
        
        Args:
            url: Original URL
            
        Returns:
            Normalized URL
        """
        # Handle redirect URLs
        parsed = urlparse(url)
        params = parse_qs(parsed.query)
        
        if 'redirect_to' in params:
            redirect_path = params['redirect_to'][0]
            url = urljoin('https://tumblr.com', redirect_path)
        
        # Extract username and create canonical URL
        username = cls.extract_username(url)
        if username:
            return f'https://{username}.tumblr.com'
        
        return url
    
    @classmethod
    def extract_username(cls, url: str) -> Optional[str]:
        """Extract username from Tumblr URL
        
        Args:
            url: Tumblr URL
            
        Returns:
            Username or None
        """
        url_lower = url.lower()
        
        # Handle /dashboard/blog/username
        match = re.search(r'/dashboard/blog/([0-9a-zA-Z_-]+)', url)
        if match:
            return match.group(1)
        
        # Handle /login_required/username
        if '/login_required/' in url:
            parts = url.split('/login_required/')[1].split('?')[0].split('/')
            if parts:
                return parts[0]
        
        # Handle tumblr.com/blog/view/username
        if 'tumblr.com/blog/view/' in url_lower:
            parts = url.split('tumblr.com/blog/view/')[1].split('/')
            if parts:
                return parts[0].split('?')[0]
        
        # Handle username.tumblr.com
        if 'tumblr.com' in url_lower:
            parsed = urlparse(url)
            
            # Check for ?url= parameter
            params = parse_qs(parsed.query)
            if 'url' in params:
                return cls.extract_username(params['url'][0])
            
            # Extract from subdomain
            host = parsed.netloc
            if '.tumblr.com' in host:
                subdomain = host.split('.tumblr.com')[0]
                if subdomain and subdomain != 'www':
                    return subdomain
            
            # Extract from path (tumblr.com/username)
            path_parts = parsed.path.strip('/').split('/')
            if path_parts and path_parts[0] not in ['post', 'blog', 'dashboard', 'login', 'search', 'tagged']:
                return path_parts[0]
        
        return None
    
    def _print_rich(self, message: str, style: str = "bold cyan"):
        """Print with Rich formatting if available"""
        if RICH_AVAILABLE and self.console:
            self.console.print(message, style=style)
        else:
            clean_msg = re.sub(r'\[.*?\]', '', message)
            print(clean_msg)
    
    def _print_panel(self, content: str, title: str = "", border_style: str = "cyan"):
        """Print a Rich panel if available"""
        if RICH_AVAILABLE and self.console:
            self.console.print(Panel(content, title=title, border_style=border_style))
        else:
            print(f"\n{'='*50}")
            if title:
                print(f"  {title}")
                print(f"{'='*50}")
            print(content)
            print(f"{'='*50}\n")
    
    def _extract_media_from_post(self, post: Dict, username: str) -> List[TumblrMedia]:
        """Extract media items from a post
        
        Args:
            post: Post data dictionary
            username: Blog username
            
        Returns:
            List of TumblrMedia objects
        """
        media_items = []
        post_id = str(post.get('id', ''))
        
        # Get content from post and trails
        contents = post.get('content', [])
        for trail in post.get('trail', []):
            contents.extend(trail.get('content', []))
        
        for content in contents:
            content_type = content.get('type', '')
            
            if content_type == 'image':
                media = content.get('media')
                if media:
                    if isinstance(media, list):
                        media = media[0]
                    url = media.get('url')
                    if url:
                        media_items.append(TumblrMedia(
                            url=url,
                            post_id=post_id,
                            index=len(media_items),
                            media_type='image'
                        ))
            
            elif content_type == 'video':
                media = content.get('media')
                if media:
                    if isinstance(media, list):
                        media = media[0]
                    url = media.get('url')
                    if url:
                        media_items.append(TumblrMedia(
                            url=url,
                            post_id=post_id,
                            index=len(media_items),
                            media_type='video'
                        ))
        
        return media_items
    
    def download(self, url: str, max_items: int = 100, 
                 interactive: bool = True) -> Optional[Dict[str, Any]]:
        """Download media from a Tumblr blog
        
        Args:
            url: Tumblr blog URL
            max_items: Maximum number of media items to download
            interactive: Whether to prompt for options
            
        Returns:
            Dictionary with download info on success, None on failure
        """
        if not REQUESTS_AVAILABLE:
            self._print_rich("[red]Error: requests library is required for Tumblr downloads[/red]")
            return None
        
        # Normalize URL and extract username
        url = self.fix_url(url)
        username = self.extract_username(url)
        
        if not username:
            self._print_rich("[red]Error: Could not extract username from URL[/red]")
            return None
        
        # Show download info panel
        download_info = f"""[bold cyan]Platform:[/bold cyan] [yellow]TUMBLR[/yellow]
[bold cyan]Blog:[/bold cyan] [green]{username}[/green]
[bold cyan]Max Items:[/bold cyan] [magenta]{max_items}[/magenta]"""
        
        self._print_panel(download_info, title="▸ Tumblr Download", border_style="blue")
        
        try:
            # Get blog info
            self._print_rich("[cyan]⌕ Fetching blog information...[/cyan]")
            blog_name = self.api.get_blog_name(username)
            
            self._print_rich(f"[green]✓ Found blog: {blog_name}[/green]")
            
            # Create output directory
            output_dir = self.downloader.output_dir if hasattr(self.downloader, 'output_dir') else Path.home() / "Downloads"
            blog_dir = output_dir / sanitize_filename(f"{blog_name} (tumblr_{username})")
            blog_dir.mkdir(parents=True, exist_ok=True)
            
            # Collect media items
            self._print_rich("[cyan]⌕ Scanning posts for media...[/cyan]")
            
            all_media = []
            post_count = 0
            
            for post in self.api.get_posts(username, max_posts=max_items * 2):  # Fetch extra posts to ensure enough media
                post_count += 1
                media_items = self._extract_media_from_post(post, username)
                all_media.extend(media_items)
                
                if len(all_media) >= max_items:
                    break
                
                # Progress update
                if post_count % 10 == 0:
                    self._print_rich(f"[dim]  Scanned {post_count} posts, found {len(all_media)} media items...[/dim]")
            
            all_media = all_media[:max_items]
            
            if not all_media:
                self._print_rich("[yellow]⚠ No media found in this blog[/yellow]")
                return None
            
            # Display summary
            images = sum(1 for m in all_media if m.media_type == 'image')
            videos = sum(1 for m in all_media if m.media_type == 'video')
            
            summary = f"""[bold]Blog:[/bold] {blog_name}
[bold]Username:[/bold] {username}
[bold]Media Found:[/bold] {len(all_media)} ({images} images, {videos} videos)"""
            
            self._print_panel(summary, title="📁 Blog Info", border_style="green")
            
            # Download media
            self._print_rich(f"[cyan]⬇ Downloading {len(all_media)} items...[/cyan]")
            
            downloaded = 0
            failed = 0
            
            for i, media in enumerate(all_media, 1):
                try:
                    filepath = blog_dir / media.filename
                    
                    # Download the file
                    response = self.session.get(media.url, stream=True)
                    response.raise_for_status()
                    
                    with open(filepath, 'wb') as f:
                        for chunk in response.iter_content(chunk_size=8192):
                            f.write(chunk)
                    
                    downloaded += 1
                    
                    # Progress update
                    if i % 5 == 0 or i == len(all_media):
                        self._print_rich(f"[dim]  [{i}/{len(all_media)}] Downloaded: {media.filename}[/dim]")
                    
                except Exception as e:
                    failed += 1
                    self._print_rich(f"[yellow]  [{i}/{len(all_media)}] Failed: {media.filename} - {str(e)}[/yellow]")
                
                # Rate limiting
                time.sleep(0.25)
            
            # Final summary
            self._print_rich(f"[green]✓ Download complete: {downloaded} succeeded, {failed} failed[/green]")
            self._print_rich(f"[dim]  Saved to: {blog_dir}[/dim]")
            
            return {
                'blog_name': blog_name,
                'username': username,
                'total_media': len(all_media),
                'downloaded': downloaded,
                'failed': failed,
                'output_dir': str(blog_dir),
                'success': True
            }
            
        except Exception as e:
            self._print_rich(f"[red]✗ Error downloading from Tumblr: {str(e)}[/red]")
            return None
    
    def download_post(self, url: str) -> Optional[Dict[str, Any]]:
        """Download media from a single Tumblr post
        
        Args:
            url: Tumblr post URL
            
        Returns:
            Dictionary with download info on success, None on failure
        """
        # For single posts, try yt-dlp first as it handles video posts well
        if YT_DLP_AVAILABLE:
            try:
                output_dir = self.downloader.output_dir if hasattr(self.downloader, 'output_dir') else Path.home() / "Downloads"
                
                ydl_opts = {
                    'format': 'best',
                    'outtmpl': str(output_dir / '%(title).100B.%(ext)s'),
                    'quiet': not getattr(self.downloader, 'verbose', False),
                    'no_warnings': True,
                }
                
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=True)
                    
                    if info:
                        self._print_rich(f"[green]✓ Downloaded: {info.get('title', 'Unknown')}[/green]")
                        return {
                            'title': info.get('title'),
                            'url': url,
                            'success': True
                        }
            except Exception as e:
                self._print_rich(f"[yellow]⚠ yt-dlp failed, this might be an image post: {str(e)}[/yellow]")
        
        self._print_rich("[yellow]⚠ Single post downloads work best for video posts. For blogs, use the blog URL.[/yellow]")
        return None
    
    def search_and_download(self, url: str, interactive: bool = True) -> Optional[Dict[str, Any]]:
        """Main entry point for downloading Tumblr content
        
        Args:
            url: Tumblr URL
            interactive: Whether to prompt for options
            
        Returns:
            Download info on success, None on failure
        """
        # Validate URL
        if not self.is_tumblr_url(url):
            self._print_rich(f"[red]Error: Not a valid Tumblr URL[/red]")
            return None
        
        # Check if this is a single post URL
        if '/post/' in url:
            self._print_rich("[cyan]ℹ Single post detected[/cyan]")
            return self.download_post(url)
        
        # Download blog
        max_items = 100
        if interactive:
            try:
                user_input = input("Maximum number of media items to download (default: 100): ").strip()
                if user_input:
                    max_items = int(user_input)
            except (ValueError, KeyboardInterrupt):
                pass
        
        return self.download(url, max_items=max_items, interactive=interactive)
