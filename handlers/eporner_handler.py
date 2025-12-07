#!/usr/bin/env python3
"""
Eporner Handler Module
Handles downloading videos from eporner.com using yt-dlp with proper configuration
and fallback methods for video extraction.
"""

import os
import re
import ssl
import json
import random
import warnings
from pathlib import Path
from typing import Optional, Dict, Any, List
from urllib.parse import urlparse, urljoin

# Suppress warnings
warnings.filterwarnings('ignore')

# Suppress SSL warnings
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

try:
    import yt_dlp
    YT_DLP_AVAILABLE = True
except ImportError:
    YT_DLP_AVAILABLE = False

try:
    import requests
    from requests.adapters import HTTPAdapter
    from urllib3.util.retry import Retry
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

# curl_cffi is better for sites with SSL issues
try:
    from curl_cffi import requests as curl_requests
    CURL_CFFI_AVAILABLE = True
except ImportError:
    CURL_CFFI_AVAILABLE = False

try:
    from bs4 import BeautifulSoup
    BS4_AVAILABLE = True
except ImportError:
    BS4_AVAILABLE = False

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

from utils.utils import sanitize_filename
from utils.ui_components import Icons, Messages


# Custom SSL adapter to handle SSL/TLS issues
class SSLAdapter(HTTPAdapter):
    """Custom adapter to handle SSL/TLS issues"""
    
    def __init__(self, *args, **kwargs):
        self.ssl_context = kwargs.pop('ssl_context', None)
        super().__init__(*args, **kwargs)
    
    def init_poolmanager(self, *args, **kwargs):
        if self.ssl_context:
            kwargs['ssl_context'] = self.ssl_context
        else:
            ctx = self._create_ssl_context()
            kwargs['ssl_context'] = ctx
        return super().init_poolmanager(*args, **kwargs)
    
    @staticmethod
    def _create_ssl_context():
        """Create a permissive SSL context for problematic servers"""
        try:
            # Try TLS 1.2+ with relaxed settings
            ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            ctx.minimum_version = ssl.TLSVersion.TLSv1_2
            # Use permissive cipher suite
            ctx.set_ciphers('DEFAULT:@SECLEVEL=0')
            # Enable legacy server connect for older SSL implementations
            if hasattr(ssl, 'OP_LEGACY_SERVER_CONNECT'):
                ctx.options |= ssl.OP_LEGACY_SERVER_CONNECT
            # Disable certain SSL options that cause issues
            ctx.options |= ssl.OP_NO_SSLv2 | ssl.OP_NO_SSLv3
            return ctx
        except Exception:
            pass
        
        try:
            # Fallback: create default context and disable verification
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            if hasattr(ssl, 'OP_LEGACY_SERVER_CONNECT'):
                ctx.options |= ssl.OP_LEGACY_SERVER_CONNECT
            return ctx
        except Exception:
            pass
        
        # Last resort: basic TLS context
        ctx = ssl.SSLContext(ssl.PROTOCOL_TLS)
        ctx.verify_mode = ssl.CERT_NONE
        return ctx


class EpornerHandler:
    """Handles Eporner video downloads"""
    
    # Supported domains
    SUPPORTED_DOMAINS = [
        'eporner.com',
        'www.eporner.com',
    ]
    
    # User agents for rotation
    USER_AGENTS = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    ]
    
    def __init__(self, downloader):
        """Initialize Eporner handler with reference to main downloader
        
        Args:
            downloader: Reference to UltimateMediaDownloader instance
        """
        self.downloader = downloader
        self.console = Console() if RICH_AVAILABLE else None
        self.session = None
        self.current_user_agent = None
        
        # Initialize session
        if REQUESTS_AVAILABLE:
            self._init_session()
    
    def _get_random_user_agent(self) -> str:
        """Get a random user agent string"""
        return random.choice(self.USER_AGENTS)
    
    def _init_session(self):
        """Initialize requests session with SSL handling and required headers"""
        self.session = requests.Session()
        
        # Mount SSL adapter for HTTPS
        ssl_adapter = SSLAdapter(
            max_retries=Retry(
                total=5,
                backoff_factor=1,
                status_forcelist=[500, 502, 503, 504]
            )
        )
        self.session.mount('https://', ssl_adapter)
        self.session.mount('http://', HTTPAdapter(max_retries=Retry(total=3)))
        
        self.current_user_agent = self._get_random_user_agent()
        
        # Set headers to mimic browser
        self.session.headers.update({
            'User-Agent': self.current_user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
        })
        
        # Set cookies for age verification
        self.session.cookies.update({
            'age_verified': '1',
            'disclaimer_accepted': '1',
        })
    
    @classmethod
    def is_eporner_url(cls, url: str) -> bool:
        """Check if URL is an Eporner URL
        
        Args:
            url: URL to check
            
        Returns:
            True if URL is from Eporner
        """
        url_lower = url.lower()
        return any(domain in url_lower for domain in cls.SUPPORTED_DOMAINS)
    
    def extract_video_id(self, url: str) -> Optional[str]:
        """Extract video ID from Eporner URL
        
        Args:
            url: Eporner URL
            
        Returns:
            Video ID or None
        """
        # URL format: https://www.eporner.com/video-VIDEOID/title-slug/
        match = re.search(r'/video-([a-zA-Z0-9]+)/', url, re.I)
        if match:
            return match.group(1)
        
        # Alternative format
        match = re.search(r'/hd-porn/([a-zA-Z0-9]+)/', url, re.I)
        if match:
            return match.group(1)
        
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
    
    def _get_available_qualities(self, url: str) -> List[Dict[str, Any]]:
        """Get available video qualities from Eporner
        
        Args:
            url: Video URL
            
        Returns:
            List of quality options with format info
        """
        qualities = []
        
        try:
            if not YT_DLP_AVAILABLE:
                return self._get_default_qualities()
            
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'nocheckcertificate': True,
                'geo_bypass': True,
                'legacy_server_connect': True,
                'prefer_insecure': True,
                'socket_timeout': 30,
                'http_headers': {
                    'User-Agent': self.current_user_agent or self._get_random_user_agent(),
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.9',
                },
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                
                if info and 'formats' in info:
                    seen_heights = set()
                    for fmt in info['formats']:
                        height = fmt.get('height')
                        if height and height not in seen_heights:
                            seen_heights.add(height)
                            qualities.append({
                                'quality': f"{height}p",
                                'height': height,
                                'format_id': fmt.get('format_id'),
                                'ext': fmt.get('ext', 'mp4'),
                                'filesize': fmt.get('filesize'),
                            })
                    
                    # Sort by height descending
                    qualities.sort(key=lambda x: x['height'], reverse=True)
        
        except Exception as e:
            self._print_rich(f"[yellow]⚠ Could not extract quality info: {str(e)}[/yellow]")
            # Return default qualities on error
            return self._get_default_qualities()
        
        # If no qualities found, return defaults
        if not qualities:
            return self._get_default_qualities()
        
        return qualities
    
    def _get_default_qualities(self) -> List[Dict[str, Any]]:
        """Return default quality options when extraction fails"""
        return [
            {'quality': '1080p', 'height': 1080, 'format_id': None, 'ext': 'mp4', 'filesize': None},
            {'quality': '720p', 'height': 720, 'format_id': None, 'ext': 'mp4', 'filesize': None},
            {'quality': '480p', 'height': 480, 'format_id': None, 'ext': 'mp4', 'filesize': None},
            {'quality': '360p', 'height': 360, 'format_id': None, 'ext': 'mp4', 'filesize': None},
            {'quality': '240p', 'height': 240, 'format_id': None, 'ext': 'mp4', 'filesize': None},
        ]
    
    def _display_qualities(self, qualities: List[Dict[str, Any]]) -> Optional[str]:
        """Display available qualities and let user choose
        
        Args:
            qualities: List of quality options
            
        Returns:
            Selected quality string or None
        """
        if not qualities:
            return "best"
        
        if RICH_AVAILABLE and self.console:
            table = Table(title="📊 Available Qualities", border_style="cyan")
            table.add_column("#", style="dim", width=4)
            table.add_column("Quality", style="cyan")
            table.add_column("Size", style="green")
            
            for i, q in enumerate(qualities, 1):
                size_str = f"{q['filesize'] / 1024 / 1024:.1f} MB" if q.get('filesize') else "Unknown"
                table.add_row(str(i), q['quality'], size_str)
            
            table.add_row(str(len(qualities) + 1), "Best Available", "-")
            
            self.console.print(table)
        else:
            print("\n📊 Available Qualities:")
            for i, q in enumerate(qualities, 1):
                size_str = f"{q['filesize'] / 1024 / 1024:.1f} MB" if q.get('filesize') else "Unknown"
                print(f"  {i}. {q['quality']} ({size_str})")
            print(f"  {len(qualities) + 1}. Best Available")
        
        try:
            choice = input(f"\nSelect quality (1-{len(qualities) + 1}) [default: 1]: ").strip()
            if not choice:
                choice = "1"
            
            choice_num = int(choice)
            if choice_num == len(qualities) + 1:
                return "best"
            elif 1 <= choice_num <= len(qualities):
                return qualities[choice_num - 1]['quality']
        except (ValueError, IndexError):
            pass
        
        return "best"
    
    def _get_ydl_opts(self, quality: str = "best", output_format: str = None) -> Dict[str, Any]:
        """Get yt-dlp options for Eporner
        
        Args:
            quality: Video quality
            output_format: Output format
            
        Returns:
            yt-dlp options dictionary
        """
        output_dir = self.downloader.output_dir if hasattr(self.downloader, 'output_dir') else Path.home() / "Downloads"
        
        # Build format string based on quality
        if quality == "best":
            format_str = "bestvideo+bestaudio/best"
        elif quality in ["2160p", "4k", "4K"]:
            format_str = "bestvideo[height<=2160]+bestaudio/best[height<=2160]"
        elif quality in ["1440p", "2k", "2K"]:
            format_str = "bestvideo[height<=1440]+bestaudio/best[height<=1440]"
        elif quality in ["1080p", "1080"]:
            format_str = "bestvideo[height<=1080]+bestaudio/best[height<=1080]"
        elif quality in ["720p", "720"]:
            format_str = "bestvideo[height<=720]+bestaudio/best[height<=720]"
        elif quality in ["480p", "480"]:
            format_str = "bestvideo[height<=480]+bestaudio/best[height<=480]"
        elif quality in ["360p", "360"]:
            format_str = "bestvideo[height<=360]+bestaudio/best[height<=360]"
        elif quality in ["240p", "240"]:
            format_str = "bestvideo[height<=240]+bestaudio/best[height<=240]"
        else:
            format_str = "bestvideo+bestaudio/best"
        
        ydl_opts = {
            'format': format_str,
            'outtmpl': str(output_dir / '%(title).100B.%(ext)s'),
            'restrictfilenames': False,
            'windowsfilenames': True,
            'trim_file_name': 200,
            'nocheckcertificate': True,
            'geo_bypass': True,
            'quiet': False,  # Enable output for progress
            'no_warnings': True,
            'noprogress': False,  # Show progress bar
            'progress_hooks': [self._progress_hook],
            'retries': 10,
            'fragment_retries': 10,
            'skip_unavailable_fragments': True,
            'keepvideo': False,
            'merge_output_format': output_format or 'mp4',
            'postprocessors': [],
            'http_headers': {
                'User-Agent': self.current_user_agent or self._get_random_user_agent(),
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Sec-Fetch-User': '?1',
                'Upgrade-Insecure-Requests': '1',
            },
            # SSL/TLS configuration - important for sites with SSL issues
            'nocheckcertificate': True,
            'prefer_insecure': True,
            'legacy_server_connect': True,
            # Network configuration
            'source_address': '0.0.0.0',
            # Use cookies from session
            'cookiesfrombrowser': None,
            # Extractor arguments
            'extractor_args': {
                'eporner': {
                    'skip_dash': True,
                },
            },
            # Socket timeout - increased for problematic sites
            'socket_timeout': 60,
            # Connection retries
            'retries': 10,
            'file_access_retries': 5,
            # Disable thumbnail to avoid postprocessing errors
            'writethumbnail': False,
            'embedthumbnail': False,
        }
        
        # Add metadata postprocessor only (skip thumbnail embedding which often fails)
        ydl_opts['postprocessors'].append({
            'key': 'FFmpegMetadata',
            'add_metadata': True,
        })
        
        return ydl_opts
    
    def download(self, url: str, quality: str = "best", output_format: str = None,
                 interactive: bool = True) -> Optional[Dict[str, Any]]:
        """Download video from Eporner
        
        Args:
            url: Eporner video URL
            quality: Video quality (best, 1080p, 720p, 480p, etc.)
            output_format: Output format (mp4, etc.)
            interactive: Whether to prompt for options
            
        Returns:
            Dictionary with download info on success, None on failure
        """
        if not YT_DLP_AVAILABLE:
            self._print_rich("[red]Error: yt-dlp is required for Eporner downloads[/red]")
            return None
        
        # Show download info panel
        download_info = f"""[bold cyan]Platform:[/bold cyan] [yellow]Eporner[/yellow]
[bold cyan]URL:[/bold cyan] [blue]{url[:60]}...[/blue]"""
        
        self._print_panel(download_info, title="▸ Eporner Download", border_style="orange1")
        
        # Get available qualities if interactive
        if interactive:
            self._print_rich("[cyan]⌕ Fetching available qualities...[/cyan]")
            qualities = self._get_available_qualities(url)
            if qualities:
                quality = self._display_qualities(qualities)
        
        self._print_rich(f"[cyan]⌕ Selected quality: {quality}[/cyan]")
        
        return self._download_video(url, quality, output_format)
    
    def _download_video(self, url: str, quality: str = "best",
                        output_format: str = None) -> Optional[Dict[str, Any]]:
        """Download a single video
        
        Args:
            url: Video URL
            quality: Video quality
            output_format: Output format
            
        Returns:
            Download info dict or None
        """
        max_retries = 3
        last_error = None
        
        for attempt in range(max_retries):
            try:
                ydl_opts = self._get_ydl_opts(quality, output_format)
                
                # On retry, try different SSL/network settings
                if attempt > 0:
                    self._print_rich(f"[yellow]⟳ Retry attempt {attempt + 1}/{max_retries}...[/yellow]")
                    # Rotate user agent on retry
                    self.current_user_agent = self._get_random_user_agent()
                    ydl_opts['http_headers']['User-Agent'] = self.current_user_agent
                    # Increase timeout on retry
                    ydl_opts['socket_timeout'] = 30 + (attempt * 15)
                    # Try different format selection on retry
                    if attempt >= 2:
                        ydl_opts['format'] = 'best'
                
                self._print_rich("[cyan]⌕ Extracting video information...[/cyan]")
                
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    # Extract info without downloading first
                    info = ydl.extract_info(url, download=False)
                    
                    if not info:
                        self._print_rich("[red]✗ Could not extract video information[/red]")
                        return None
                    
                    title = info.get('title', 'Unknown')
                    duration = info.get('duration', 0)
                    uploader = info.get('uploader', 'Unknown')
                    
                    # Display video info - convert duration to int to avoid format errors
                    if duration:
                        duration_int = int(duration)
                        duration_str = f"{duration_int // 60}:{duration_int % 60:02d}"
                    else:
                        duration_str = "Unknown"
                    video_info = f"""[bold]Title:[/bold] {title}
[bold]Uploader:[/bold] {uploader}
[bold]Duration:[/bold] {duration_str}"""
                    
                    self._print_panel(video_info, title="📹 Video Info", border_style="green")
                    
                    # Now download
                    self._print_rich("[cyan]⬇ Starting download...[/cyan]")
                    ydl.download([url])
                    
                    self._print_rich(f"[green]✓ Successfully downloaded: {title}[/green]")
                    
                    return {
                        'title': title,
                        'uploader': uploader,
                        'duration': duration,
                        'url': url,
                        'success': True
                    }
                    
            except yt_dlp.utils.DownloadError as e:
                last_error = str(e)
                error_lower = last_error.lower()
                
                # Check if it's a postprocessing error (video was downloaded successfully)
                if 'postprocessing' in error_lower or 'postprocessor' in error_lower:
                    self._print_rich(f"[yellow]⚠ Video downloaded but postprocessing failed (non-critical)[/yellow]")
                    self._print_rich(f"[green]✓ Video file should be available in the download folder[/green]")
                    return {
                        'title': 'Unknown',
                        'url': url,
                        'success': True,
                        'note': 'Postprocessing failed but video was downloaded'
                    }
                
                # Check if error is SSL-related and can be retried
                if 'ssl' in error_lower or 'eof' in error_lower or 'connection' in error_lower:
                    if attempt < max_retries - 1:
                        self._print_rich(f"[yellow]⚠ SSL/Connection error, will retry...[/yellow]")
                        import time
                        time.sleep(2 * (attempt + 1))  # Increasing delay between retries
                        continue
                    # Last attempt failed with SSL error - try fallback
                    break
                
                # Non-retryable errors
                if 'private' in error_lower:
                    self._print_rich("[red]✗ This video is private or requires login[/red]")
                    return None
                elif 'removed' in error_lower or 'deleted' in error_lower:
                    self._print_rich("[red]✗ This video has been removed[/red]")
                    return None
                elif 'geo' in error_lower:
                    self._print_rich("[red]✗ This video is not available in your region[/red]")
                    return None
                else:
                    self._print_rich(f"[red]✗ Download error: {last_error}[/red]")
                    # Try fallback for other errors too
                    break
                
            except Exception as e:
                last_error = str(e)
                if attempt < max_retries - 1:
                    self._print_rich(f"[yellow]⚠ Error occurred, will retry: {last_error}[/yellow]")
                    import time
                    time.sleep(2 * (attempt + 1))
                    continue
                self._print_rich(f"[red]✗ Error downloading video: {last_error}[/red]")
                # Don't return yet - try fallback
                break
        
        # All retries exhausted - try direct extraction fallback
        self._print_rich(f"[yellow]⚠ yt-dlp failed, trying direct extraction...[/yellow]")
        video_info = self._extract_video_urls_from_page(url)
        if video_info:
            return self._download_direct(video_info, quality, output_format)
        
        self._print_rich(f"[red]✗ All download methods failed. Last error: {last_error}[/red]")
        return None
    
    def search_and_download(self, url: str, interactive: bool = True) -> Optional[Dict[str, Any]]:
        """Main entry point for downloading Eporner content
        
        Args:
            url: Eporner URL
            interactive: Whether to prompt for options
            
        Returns:
            Download info on success, None on failure
        """
        # Validate URL
        if not self.is_eporner_url(url):
            self._print_rich(f"[red]Error: Not a valid Eporner URL[/red]")
            return None
        
        return self.download(url, quality="best", interactive=interactive)
    
    def _extract_video_urls_from_page(self, url: str) -> Optional[Dict[str, Any]]:
        """Extract video URLs directly from page HTML as fallback
        
        Args:
            url: Video page URL
            
        Returns:
            Dict with video info or None
        """
        try:
            self._print_rich("[cyan]⌕ Trying direct page extraction...[/cyan]")
            
            content = None
            
            # Try curl_cffi first (best for SSL issues)
            if CURL_CFFI_AVAILABLE:
                try:
                    self._print_rich("[dim]Using curl_cffi...[/dim]")
                    resp = curl_requests.get(
                        url,
                        impersonate="chrome",
                        timeout=30,
                        headers={
                            'User-Agent': self._get_random_user_agent(),
                            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                        }
                    )
                    if resp.status_code == 200:
                        content = resp.text
                except Exception as e:
                    self._print_rich(f"[dim]curl_cffi failed: {str(e)[:50]}[/dim]")
            
            # Fallback to requests with session
            if not content and REQUESTS_AVAILABLE:
                try:
                    self._print_rich("[dim]Trying requests...[/dim]")
                    resp = self.session.get(url, verify=False, timeout=30)
                    if resp.status_code == 200:
                        content = resp.text
                except Exception as e:
                    self._print_rich(f"[dim]requests failed: {str(e)[:50]}[/dim]")
            
            if not content:
                self._print_rich("[yellow]⚠ Could not fetch page content[/yellow]")
                return None
            
            # Extract video ID from URL
            video_id_match = re.search(r'/video-([a-zA-Z0-9]+)/', url)
            video_id = video_id_match.group(1) if video_id_match else None
            
            # Extract title
            title_match = re.search(r'<title>([^<]+)</title>', content)
            title = title_match.group(1) if title_match else 'Unknown'
            title = re.sub(r'\s*-\s*EPORNER.*$', '', title, flags=re.I).strip()
            title = re.sub(r'\s*-\s*Free HD Porn Video.*$', '', title, flags=re.I).strip()
            
            video_urls = {}
            base_url = 'https://www.eporner.com'
            
            # Method 1: Look for /dload/ patterns (download API)
            dload_patterns = re.findall(r'/dload/([^/]+)/(\d+)/([^\'"<>\s]+\.mp4)', content)
            for vid, quality_num, filename in dload_patterns:
                # Skip AV1 encoded versions (less compatible)
                if 'av1' in filename.lower():
                    continue
                quality_key = f"{quality_num}p"
                full_url = f"{base_url}/dload/{vid}/{quality_num}/{filename}"
                if quality_key not in video_urls:
                    video_urls[quality_key] = full_url
            
            # Method 2: Look for direct gvideo URLs
            gvideo_matches = re.findall(r'https?://gvideo\.eporner\.com/[^\s\'"<>]+\.mp4[^\s\'"<>]*', content)
            for gvideo_url in gvideo_matches:
                # Clean up any trailing characters
                gvideo_url = re.sub(r'[\'\"<>].*$', '', gvideo_url)
                # This is usually the main/best quality
                if 'best' not in video_urls:
                    video_urls['best'] = gvideo_url
            
            # Method 3: Look for any other MP4 URLs
            mp4_matches = re.findall(r'https?://[^\s\'"<>]+\.mp4(?:\?[^\s\'"<>]*)?', content)
            for mp4_url in mp4_matches:
                if 'eporner' in mp4_url and mp4_url not in video_urls.values():
                    quality_match = re.search(r'(\d{3,4})p', mp4_url)
                    quality = quality_match.group(1) + 'p' if quality_match else 'stream'
                    if quality not in video_urls:
                        video_urls[quality] = mp4_url
            
            if not video_urls:
                self._print_rich("[yellow]⚠ No video URLs found in page[/yellow]")
                return None
            
            self._print_rich(f"[green]✓ Found {len(video_urls)} video source(s): {', '.join(video_urls.keys())}[/green]")
            
            return {
                'title': title,
                'video_urls': video_urls,
                'page_url': url,
                'video_id': video_id,
            }
            
        except Exception as e:
            self._print_rich(f"[yellow]⚠ Direct extraction failed: {str(e)}[/yellow]")
            return None
    
    def _download_direct(self, video_info: Dict[str, Any], quality: str = "best",
                         output_format: str = None) -> Optional[Dict[str, Any]]:
        """Download video using direct URL with progress bar
        
        Args:
            video_info: Video info from _extract_video_urls_from_page
            quality: Preferred quality
            output_format: Output format
            
        Returns:
            Download result or None
        """
        video_urls = video_info.get('video_urls', {})
        title = video_info.get('title', 'Unknown')
        
        if not video_urls:
            return None
        
        # Display available qualities
        self._print_rich(f"[cyan]📊 Available qualities: {', '.join(video_urls.keys())}[/cyan]")
        
        # Select best matching quality
        selected_url = None
        selected_quality = None
        
        # Quality preference order (highest to lowest)
        quality_order = ['1080p', '720p', '480p', '360p', '240p', 'best', 'stream', 'default']
        
        if quality != "best":
            # Try to find exact quality match
            quality_key = quality.replace('p', '') + 'p'
            if quality_key in video_urls:
                selected_url = video_urls[quality_key]
                selected_quality = quality_key
        
        if not selected_url:
            # Select best available
            for q in quality_order:
                if q in video_urls:
                    selected_url = video_urls[q]
                    selected_quality = q
                    break
        
        if not selected_url:
            # Just take any available
            selected_quality = list(video_urls.keys())[0]
            selected_url = video_urls[selected_quality]
        
        self._print_rich(f"[cyan]⬇ Downloading ({selected_quality}): {title}[/cyan]")
        
        output_dir = self.downloader.output_dir if hasattr(self.downloader, 'output_dir') else Path.home() / "Downloads"
        safe_title = sanitize_filename(title)
        output_path = output_dir / f'{safe_title}.mp4'
        
        # Try yt-dlp first (has better handling and progress)
        if YT_DLP_AVAILABLE:
            try:
                ydl_opts = {
                    'outtmpl': str(output_dir / f'{safe_title}.%(ext)s'),
                    'nocheckcertificate': True,
                    'quiet': False,
                    'no_warnings': True,
                    'progress_hooks': [self._progress_hook],
                    'noprogress': False,
                }
                
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([selected_url])
                
                self._print_rich(f"\n[green]✓ Successfully downloaded: {title}[/green]")
                
                return {
                    'title': title,
                    'url': video_info.get('page_url'),
                    'quality': selected_quality,
                    'success': True
                }
            except Exception as e:
                self._print_rich(f"[yellow]⚠ yt-dlp direct download failed: {str(e)}, trying requests...[/yellow]")
        
        # Fallback to requests with progress bar
        return self._download_with_requests(selected_url, output_path, title)
    
    def _progress_hook(self, d):
        """Progress hook for yt-dlp downloads"""
        if d['status'] == 'downloading':
            try:
                percent = d.get('_percent_str', '').strip()
                speed = d.get('_speed_str', '').strip()
                eta = d.get('_eta_str', '').strip()
                downloaded = d.get('_downloaded_bytes_str', '').strip()
                total = d.get('_total_bytes_str', d.get('_total_bytes_estimate_str', '')).strip()
                
                # Build progress string
                progress_parts = []
                if percent:
                    progress_parts.append(percent)
                if downloaded and total:
                    progress_parts.append(f"{downloaded}/{total}")
                elif downloaded:
                    progress_parts.append(downloaded)
                if speed:
                    progress_parts.append(f"@ {speed}")
                if eta:
                    progress_parts.append(f"ETA: {eta}")
                
                progress_str = ' | '.join(progress_parts)
                print(f"\r⬇ {progress_str}    ", end='', flush=True)
            except Exception:
                pass
        elif d['status'] == 'finished':
            print(f"\r✓ Download complete, processing...              ", flush=True)
    
    def _download_with_requests(self, url: str, output_path: Path, title: str) -> Optional[Dict[str, Any]]:
        """Download file using curl_cffi or requests with progress bar
        
        Args:
            url: Direct video URL
            output_path: Output file path
            title: Video title
            
        Returns:
            Download result or None
        """
        response = None
        
        # Try curl_cffi first (handles SSL better)
        if CURL_CFFI_AVAILABLE:
            try:
                self._print_rich("[dim]Using curl_cffi for download...[/dim]")
                response = curl_requests.get(
                    url,
                    impersonate="chrome",
                    stream=True,
                    timeout=120,
                )
            except Exception as e:
                self._print_rich(f"[dim]curl_cffi download failed: {str(e)[:50]}[/dim]")
                response = None
        
        # Fallback to requests
        if response is None and REQUESTS_AVAILABLE:
            try:
                self._print_rich("[dim]Using requests for download...[/dim]")
                response = self.session.get(url, stream=True, verify=False, timeout=120)
            except Exception as e:
                self._print_rich(f"[dim]requests download failed: {str(e)[:50]}[/dim]")
                response = None
        
        if response is None:
            self._print_rich("[red]✗ Could not establish download connection[/red]")
            return None
        
        try:
            response.raise_for_status()
            
            # Get total file size
            total_size = int(response.headers.get('content-length', 0))
            
            # Setup progress display
            downloaded = 0
            chunk_size = 65536  # 64KB chunks for faster download
            
            if RICH_AVAILABLE:
                from rich.progress import Progress, BarColumn, DownloadColumn, TransferSpeedColumn, TimeRemainingColumn
                
                with Progress(
                    "[progress.description]{task.description}",
                    BarColumn(),
                    "[progress.percentage]{task.percentage:>3.0f}%",
                    DownloadColumn(),
                    TransferSpeedColumn(),
                    TimeRemainingColumn(),
                    console=self.console
                ) as progress:
                    task = progress.add_task(f"[cyan]⬇ {title[:50]}...", total=total_size)
                    
                    with open(output_path, 'wb') as f:
                        for chunk in response.iter_content(chunk_size=chunk_size):
                            if chunk:
                                f.write(chunk)
                                downloaded += len(chunk)
                                progress.update(task, completed=downloaded)
            else:
                # Simple progress without rich
                with open(output_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=chunk_size):
                        if chunk:
                            f.write(chunk)
                            downloaded += len(chunk)
                            if total_size > 0:
                                percent = (downloaded / total_size) * 100
                                mb_downloaded = downloaded / (1024 * 1024)
                                mb_total = total_size / (1024 * 1024)
                                print(f"\r⬇ {percent:.1f}% ({mb_downloaded:.1f}/{mb_total:.1f} MB)", end='', flush=True)
                            else:
                                mb_downloaded = downloaded / (1024 * 1024)
                                print(f"\r⬇ {mb_downloaded:.1f} MB downloaded", end='', flush=True)
                print()  # New line after progress
            
            self._print_rich(f"[green]✓ Successfully downloaded: {title}[/green]")
            self._print_rich(f"[green]📁 Saved to: {output_path}[/green]")
            
            return {
                'title': title,
                'output_path': str(output_path),
                'success': True
            }
            
        except Exception as e:
            self._print_rich(f"[red]✗ Download failed: {str(e)}[/red]")
            # Clean up partial download
            if output_path.exists():
                output_path.unlink()
            return None
