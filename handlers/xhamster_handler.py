#!/usr/bin/env python3
"""
xHamster Handler Module
Handles downloading videos and photo galleries from xHamster using yt-dlp
with proper configuration and fallback methods.
"""

import os
import re
import ssl
import random
import warnings
from pathlib import Path
from typing import Optional, Dict, Any, List
from urllib.parse import urlparse

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

try:
    from bs4 import BeautifulSoup
    BS4_AVAILABLE = True
except ImportError:
    BS4_AVAILABLE = False

try:
    from rich.console import Console
    from rich.panel import Panel
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

from utils.utils import sanitize_filename
from utils.ui_components import Icons, Messages


# Custom SSL adapter to handle SSL issues
class SSLAdapter(HTTPAdapter):
    """Custom adapter to handle SSL/TLS issues"""
    
    def __init__(self, *args, **kwargs):
        self.ssl_context = kwargs.pop('ssl_context', None)
        super().__init__(*args, **kwargs)
    
    def init_poolmanager(self, *args, **kwargs):
        # Create a custom SSL context with very relaxed settings
        if self.ssl_context:
            kwargs['ssl_context'] = self.ssl_context
        else:
            try:
                # Try multiple SSL context configurations
                ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
                ctx.check_hostname = False
                ctx.verify_mode = ssl.CERT_NONE
                # Set minimum TLS version to TLS 1.0 for maximum compatibility
                ctx.minimum_version = ssl.TLSVersion.TLSv1
                # Use a permissive cipher suite
                ctx.set_ciphers('DEFAULT:@SECLEVEL=0')
                # Disable various checks
                ctx.options |= ssl.OP_NO_SSLv2
                ctx.options |= ssl.OP_NO_SSLv3
                ctx.options |= ssl.OP_LEGACY_SERVER_CONNECT
            except Exception:
                try:
                    ctx = ssl.create_default_context()
                    ctx.check_hostname = False
                    ctx.verify_mode = ssl.CERT_NONE
                    ctx.set_ciphers('DEFAULT@SECLEVEL=1')
                except Exception:
                    ctx = ssl.SSLContext(ssl.PROTOCOL_TLS)
                    ctx.verify_mode = ssl.CERT_NONE
            
            kwargs['ssl_context'] = ctx
        return super().init_poolmanager(*args, **kwargs)


def create_unverified_https_context():
    """Create an unverified HTTPS context for urllib"""
    try:
        ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        ctx.minimum_version = ssl.TLSVersion.TLSv1
        ctx.set_ciphers('DEFAULT:@SECLEVEL=0')
        ctx.options |= ssl.OP_LEGACY_SERVER_CONNECT
        return ctx
    except Exception:
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        return ctx


# Monkey-patch ssl for urllib (fallback)
try:
    ssl._create_default_https_context = ssl._create_unverified_context
except AttributeError:
    pass


class XHamsterHandler:
    """Handles xHamster video and gallery downloads"""
    
    # Supported domain patterns (including mirror sites)
    # xhamster, xhwebsite, xhofficial, xhlocal, xhopen, xhtotal, megaxh, xhwide, xhtab, xhtime
    DOMAIN_PATTERN = re.compile(
        r'(xhamster|xhwebsite|xhofficial|xhlocal|xhopen|xhtotal|megaxh|xhwide|xhtab|xhtime)\d*\.',
        re.I
    )
    
    SUPPORTED_DOMAINS = [
        'xhamster.com',
        'xhamster.desi',
        'xhamster2.com',
        'xhamster3.com',
        'xhwebsite.com',
        'xhofficial.com',
        'xhlocal.com',
        'xhopen.com',
        'xhtotal.com',
        'megaxh.com',
        'xhwide.com',
        'xhtab.com',
        'xhtime.com',
    ]
    
    # User agents for rotation
    USER_AGENTS = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:121.0) Gecko/20100101 Firefox/121.0',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:121.0) Gecko/20100101 Firefox/121.0',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 OPR/106.0.0.0',
    ]
    
    # Free proxy list (these are examples - in production you'd want to use a proxy service)
    # Format: (ip, port, protocol)
    FREE_PROXIES = [
        # These will be populated dynamically or can be configured
    ]
    
    # Mirror domains to try if main domain fails
    MIRROR_DOMAINS = [
        'xhamster.com',
        'xhamster.desi',
        'xhamster2.com',
        'xhamster3.com',
        'xhopen.com',
        'xhtab.com',
        'xhwide.com',
    ]
    
    def __init__(self, downloader):
        """Initialize xHamster handler with reference to main downloader
        
        Args:
            downloader: Reference to UltimateMediaDownloader instance
        """
        self.downloader = downloader
        self.console = Console() if RICH_AVAILABLE else None
        self.session = None
        self.current_user_agent = None
        self.current_proxy = None
        
        # Initialize session
        if REQUESTS_AVAILABLE:
            self._init_session()
    
    def _get_random_user_agent(self) -> str:
        """Get a random user agent string"""
        return random.choice(self.USER_AGENTS)
    
    def _get_random_proxy(self) -> Optional[Dict[str, str]]:
        """Get a random proxy from the list (if available)"""
        if not self.FREE_PROXIES:
            return None
        proxy_info = random.choice(self.FREE_PROXIES)
        if len(proxy_info) >= 3:
            ip, port, protocol = proxy_info[:3]
            return {
                'http': f'{protocol}://{ip}:{port}',
                'https': f'{protocol}://{ip}:{port}',
            }
        return None
    
    def _rotate_identity(self):
        """Rotate user agent and optionally proxy for a new identity"""
        self.current_user_agent = self._get_random_user_agent()
        self.current_proxy = self._get_random_proxy()
        
        if self.session:
            self.session.headers['User-Agent'] = self.current_user_agent
            if self.current_proxy:
                self.session.proxies.update(self.current_proxy)
    
    def _get_mirror_url(self, url: str, mirror_domain: str) -> str:
        """Convert URL to use a different mirror domain
        
        Args:
            url: Original URL
            mirror_domain: Target mirror domain
            
        Returns:
            URL with the new domain
        """
        parsed = urlparse(url)
        # Replace the domain in the URL
        new_url = url.replace(parsed.netloc, mirror_domain)
        return new_url
    
    def _try_fetch_with_mirrors(self, url: str, timeout: int = 30) -> Optional[requests.Response]:
        """Try to fetch a URL, falling back to mirror domains if needed
        
        Args:
            url: Original URL
            timeout: Request timeout
            
        Returns:
            Response object or None
        """
        parsed = urlparse(url)
        original_domain = parsed.netloc
        
        # Try original URL first
        domains_to_try = [original_domain]
        
        # Add mirror domains (excluding the original)
        for mirror in self.MIRROR_DOMAINS:
            if mirror != original_domain and mirror not in domains_to_try:
                domains_to_try.append(mirror)
        
        for domain in domains_to_try:
            try:
                test_url = self._get_mirror_url(url, domain) if domain != original_domain else url
                self._print_rich(f"[dim]  Trying domain: {domain}...[/dim]")
                
                response = self.session.get(test_url, timeout=timeout)
                if response.status_code == 200:
                    self._print_rich(f"[green]  ✓ Connected via {domain}[/green]")
                    return response
                    
            except Exception as e:
                error_str = str(e).lower()
                if 'ssl' in error_str or 'eof' in error_str:
                    self._print_rich(f"[yellow]  ✗ SSL error on {domain}[/yellow]")
                else:
                    self._print_rich(f"[yellow]  ✗ Failed on {domain}: {str(e)[:50]}[/yellow]")
                continue
        
        return None
    
    def _init_session(self):
        """Initialize requests session with required headers and SSL workarounds"""
        self.session = requests.Session()
        
        # Create custom SSL context
        ssl_context = create_unverified_https_context()
        
        # Mount SSL adapter for HTTPS requests to handle SSL issues
        ssl_adapter = SSLAdapter(ssl_context=ssl_context)
        retry_strategy = Retry(
            total=5,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS"],
        )
        ssl_adapter.max_retries = retry_strategy
        
        self.session.mount('https://', ssl_adapter)
        self.session.mount('http://', HTTPAdapter(max_retries=retry_strategy))
        
        # Disable SSL verification
        self.session.verify = False
        
        # Get random user agent
        self.current_user_agent = self._get_random_user_agent()
        
        # Set headers (randomized user agent)
        self.session.headers.update({
            'User-Agent': self.current_user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate',  # Remove 'br' (brotli) as it can cause issues
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0',
        })
        
        # Set proxy if available
        self.current_proxy = self._get_random_proxy()
        if self.current_proxy:
            self.session.proxies.update(self.current_proxy)
    
    @classmethod
    def is_xhamster_url(cls, url: str) -> bool:
        """Check if URL is an xHamster URL
        
        Args:
            url: URL to check
            
        Returns:
            True if URL is from xHamster (or mirror sites)
        """
        url_lower = url.lower()
        
        # Check standard domains
        if any(domain in url_lower for domain in cls.SUPPORTED_DOMAINS):
            return True
        
        # Check pattern for numbered/mirror domains
        if cls.DOMAIN_PATTERN.search(url_lower):
            return True
        
        return False
    
    @classmethod
    def fix_url(cls, url: str) -> str:
        """Normalize xHamster URL
        
        Args:
            url: Original URL
            
        Returns:
            Normalized URL
        """
        # Fix pagination in user video URLs
        url = re.sub(r'(/users/[^/]+/videos)/\d+', r'\1', url)
        return url
    
    def get_content_type(self, url: str) -> str:
        """Determine the type of xHamster content from URL
        
        Args:
            url: xHamster URL
            
        Returns:
            Content type: 'video', 'gallery', 'channel', 'creator'
        """
        url_lower = url.lower()
        
        if '/photos/gallery/' in url_lower:
            return 'gallery'
        elif '/users/' in url_lower:
            return 'channel'
        elif '/creators/' in url_lower:
            return 'creator'
        elif '/videos/' in url_lower:
            return 'video'
        else:
            return 'video'  # Default to video
    
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
    
    def download(self, url: str, quality: str = "best", output_format: str = None,
                 interactive: bool = True) -> Optional[Dict[str, Any]]:
        """Download content from xHamster
        
        Args:
            url: xHamster URL
            quality: Video quality (best, 1080p, 720p, 480p, etc.)
            output_format: Output format (mp4, etc.)
            interactive: Whether to prompt for options
            
        Returns:
            Dictionary with download info on success, None on failure
        """
        if not YT_DLP_AVAILABLE:
            self._print_rich("[red]Error: yt-dlp is required for xHamster downloads[/red]")
            return None
        
        # Normalize URL
        url = self.fix_url(url)
        
        # Determine content type
        content_type = self.get_content_type(url)
        
        # Show download info panel
        download_info = f"""[bold cyan]Platform:[/bold cyan] [yellow]XHAMSTER[/yellow]
[bold cyan]Content Type:[/bold cyan] [green]{content_type.upper()}[/green]
[bold cyan]Quality:[/bold cyan] [magenta]{quality}[/magenta]"""
        
        self._print_panel(download_info, title="▸ xHamster Download", border_style="orange1")
        
        # Handle different content types
        if content_type == 'video':
            return self._download_video(url, quality, output_format)
        elif content_type == 'gallery':
            return self._download_gallery(url)
        elif content_type in ['channel', 'creator']:
            return self._download_channel(url, content_type, quality, output_format, interactive)
        else:
            return self._download_video(url, quality, output_format)
    
    def _get_ydl_opts(self, quality: str = "best", output_format: str = None) -> Dict[str, Any]:
        """Get yt-dlp options for xHamster
        
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
        elif quality in ["1080p", "1080"]:
            format_str = "bestvideo[height<=1080]+bestaudio/best[height<=1080]"
        elif quality in ["720p", "720"]:
            format_str = "bestvideo[height<=720]+bestaudio/best[height<=720]"
        elif quality in ["480p", "480"]:
            format_str = "bestvideo[height<=480]+bestaudio/best[height<=480]"
        elif quality in ["360p", "360"]:
            format_str = "bestvideo[height<=360]+bestaudio/best[height<=360]"
        else:
            format_str = "bestvideo+bestaudio/best"
        
        ydl_opts = {
            'format': format_str,
            'outtmpl': str(output_dir / '%(uploader)s - %(title).100B.%(ext)s'),
            'restrictfilenames': False,
            'windowsfilenames': True,
            'trim_file_name': 200,
            # SSL/TLS workarounds
            'nocheckcertificate': True,
            'no_check_certificate': True,
            'legacy_server_connect': True,  # Use legacy SSL connection
            # Network settings
            'geo_bypass': True,
            'socket_timeout': 30,
            'retries': 10,
            'fragment_retries': 10,
            'skip_unavailable_fragments': True,
            'extractor_retries': 5,
            # Output settings
            'quiet': not getattr(self.downloader, 'verbose', False),
            'no_warnings': True,
            'keepvideo': False,
            'writethumbnail': True,
            'embedthumbnail': True,
            'merge_output_format': output_format or 'mp4',
            'postprocessors': [],
            # HTTP settings
            'http_headers': {
                'User-Agent': self.session.headers.get('User-Agent') if self.session else 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
            },
            # Extractor arguments for xHamster
            'extractor_args': {
                'xhamster': {
                    'prefer_https': ['false'],
                }
            },
        }
        
        # Add thumbnail embedding for mp4
        if output_format in [None, 'mp4']:
            ydl_opts['postprocessors'].append({
                'key': 'FFmpegMetadata',
                'add_metadata': True,
            })
            ydl_opts['postprocessors'].append({
                'key': 'EmbedThumbnail',
                'already_have_thumbnail': False,
            })
        
        return ydl_opts
    
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
        try:
            ydl_opts = self._get_ydl_opts(quality, output_format)
            
            # Extract video info first
            self._print_rich("[cyan]⌕ Extracting video information...[/cyan]")
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # Extract info without downloading first
                info = ydl.extract_info(url, download=False)
                
                if not info:
                    self._print_rich("[red]✗ Could not extract video information[/red]")
                    return None
                
                title = info.get('title', 'Unknown')
                uploader = info.get('uploader', 'Unknown')
                duration = info.get('duration', 0)
                
                # Get available formats
                formats = info.get('formats', [])
                https_formats = [f for f in formats if f.get('protocol') == 'https' and f.get('height')]
                if https_formats:
                    qualities = sorted(set(f['height'] for f in https_formats))
                    quality_str = ', '.join(f"{q}p" for q in qualities)
                else:
                    quality_str = "Unknown"
                
                # Display video info
                duration_str = f"{duration // 60}:{duration % 60:02d}" if duration else "Unknown"
                video_info = f"""[bold]Title:[/bold] {title}
[bold]Uploader:[/bold] {uploader}
[bold]Duration:[/bold] {duration_str}
[bold]Available:[/bold] {quality_str}"""
                
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
            error_msg = str(e)
            if 'private' in error_msg.lower():
                self._print_rich("[red]✗ This video is private or requires login[/red]")
            elif 'removed' in error_msg.lower() or 'deleted' in error_msg.lower():
                self._print_rich("[red]✗ This video has been removed[/red]")
            elif 'geo' in error_msg.lower():
                self._print_rich("[red]✗ This video is not available in your region[/red]")
            elif 'ssl' in error_msg.lower() or 'eof' in error_msg.lower() or 'certificate' in error_msg.lower():
                self._print_rich("[yellow]⚠ SSL error detected, trying fallback method...[/yellow]")
                return self._download_video_fallback(url, quality, output_format)
            elif 'no video formats' in error_msg.lower() or 'unsupported url' in error_msg.lower():
                self._print_rich("[yellow]⚠ yt-dlp couldn't extract formats, trying fallback method...[/yellow]")
                return self._download_video_fallback(url, quality, output_format)
            else:
                self._print_rich(f"[red]✗ Download error: {error_msg}[/red]")
                # Try fallback for any download error
                self._print_rich("[yellow]⚠ Trying fallback method...[/yellow]")
                return self._download_video_fallback(url, quality, output_format)
            return None
        except ssl.SSLError as e:
            self._print_rich("[yellow]⚠ SSL error detected, trying fallback method...[/yellow]")
            return self._download_video_fallback(url, quality, output_format)
        except Exception as e:
            error_msg = str(e).lower()
            if 'ssl' in error_msg or 'eof' in error_msg or 'certificate' in error_msg:
                self._print_rich("[yellow]⚠ SSL error detected, trying fallback method...[/yellow]")
                return self._download_video_fallback(url, quality, output_format)
            self._print_rich(f"[red]✗ Error downloading video: {str(e)}[/red]")
            return None
    
    def _download_video_fallback(self, url: str, quality: str = "best",
                                  output_format: str = None, max_retries: int = 3) -> Optional[Dict[str, Any]]:
        """Fallback download method using direct extraction when yt-dlp SSL fails
        
        Args:
            url: Video URL
            quality: Video quality
            output_format: Output format
            max_retries: Maximum number of retries with different identities
            
        Returns:
            Download info dict or None
        """
        last_error = None
        
        for attempt in range(max_retries):
            try:
                if attempt > 0:
                    self._print_rich(f"[yellow]⚠ Retry {attempt + 1}/{max_retries} with new identity...[/yellow]")
                    # Rotate to a new identity (user agent)
                    self._rotate_identity()
                    import time
                    time.sleep(random.uniform(1, 3))  # Random delay between retries
                
                self._print_rich("[cyan]⌕ Attempting fallback extraction...[/cyan]")
                self._print_rich(f"[dim]  User-Agent: {self.current_user_agent[:50]}...[/dim]")
                
                # Re-initialize session with new identity
                self._init_session()
                
                # Try to get the page using mirror domains if needed
                response = self._try_fetch_with_mirrors(url, timeout=30)
                
                if not response:
                    self._print_rich(f"[red]✗ Failed to fetch page from all mirrors[/red]")
                    last_error = "All mirrors failed"
                    continue
                
                html_content = response.text
                
                # Extract video data from page
                soup = BeautifulSoup(html_content, 'html.parser')
                
                # Try multiple methods to get the title
                title = None
                # Method 1: h1 tag
                h1_tag = soup.find('h1')
                if h1_tag:
                    title = h1_tag.get_text(strip=True)
                # Method 2: og:title meta
                if not title:
                    og_title = soup.find('meta', property='og:title')
                    if og_title:
                        title = og_title.get('content', '')
                # Method 3: title tag
                if not title:
                    title_tag = soup.find('title')
                    if title_tag:
                        title = title_tag.get_text(strip=True).split(' - ')[0]
                
                title = title or "xhamster_video"
                
                # Look for video sources using multiple methods
                import json as json_mod
                video_url = None
                video_sources = []
                
                # Method 1: Look for window.initials JSON data (most common)
                initials_patterns = [
                    r'window\.initials\s*=\s*(\{.*?\});?\s*(?:</script>|window\.)',
                    r'window\.initials\s*=\s*(\{.*?\})\s*;',
                    r'"videoModel"\s*:\s*(\{.*?"sources"\s*:\s*\{[^}]+\}.*?\})',
                ]
                
                for pattern in initials_patterns:
                    initials_match = re.search(pattern, html_content, re.DOTALL)
                    if initials_match:
                        try:
                            json_str = initials_match.group(1)
                            # Try to extract sources with multiple patterns
                            sources_patterns = [
                                r'"sources"\s*:\s*\{([^}]+)\}',
                                r'"mp4"\s*:\s*\{([^}]+)\}',
                                r'"download"\s*:\s*\{([^}]+)\}',
                            ]
                            for sp in sources_patterns:
                                sources_match = re.search(sp, json_str)
                                if sources_match:
                                    sources_str = sources_match.group(1)
                                    # Extract URLs from sources - handle various formats
                                    url_patterns = [
                                        r'"(\d+p?)"\s*:\s*"(https?://[^"]+)"',
                                        r'"(https?://[^"]+\.mp4[^"]*)"',
                                        r'(https?://[^"\']+\.mp4[^"\']*)',
                                    ]
                                    for up in url_patterns:
                                        url_matches = re.findall(up, sources_str)
                                        for match in url_matches:
                                            if isinstance(match, tuple):
                                                qual, vid_url = match[0], match[1] if len(match) > 1 else match[0]
                                            else:
                                                qual, vid_url = 'unknown', match
                                            clean_url = vid_url.replace('\\/', '/').replace('\\u0026', '&')
                                            if clean_url.startswith('http'):
                                                video_sources.append({'quality': qual, 'url': clean_url})
                                    if video_sources:
                                        break
                            if video_sources:
                                break
                        except Exception:
                            pass
                
                # Method 2: Look for xplayer config
                if not video_sources:
                    xplayer_patterns = [
                        r'xplayer\.init\s*\(\s*(\{.*?\})\s*\)',
                        r'playerSettings\s*=\s*(\{.*?\});',
                        r'XPlayer\s*\(\s*(\{.*?\})\s*\)',
                    ]
                    for pattern in xplayer_patterns:
                        xplayer_match = re.search(pattern, html_content, re.DOTALL)
                        if xplayer_match:
                            try:
                                config_str = xplayer_match.group(1)
                                url_matches = re.findall(r'"(https?://[^"]+\.mp4[^"]*)"', config_str)
                                for vid_url in url_matches:
                                    clean_url = vid_url.replace('\\/', '/').replace('\\u0026', '&')
                                    video_sources.append({'quality': 'unknown', 'url': clean_url})
                            except Exception:
                                pass
                
                # Method 3: Look for any MP4/M3U8 URLs in script tags
                if not video_sources:
                    for script in soup.find_all('script'):
                        script_text = script.string or ''
                        if script_text and ('mp4' in script_text.lower() or 'm3u8' in script_text.lower()):
                            # Look for video URLs
                            url_patterns = [
                                r'https?://[^"\'<>\s\\]+\.mp4[^"\'<>\s\\]*',
                                r'https?://[^"\'<>\s\\]+/video[^"\'<>\s\\]*\.mp4',
                            ]
                            for pattern in url_patterns:
                                mp4_matches = re.findall(pattern, script_text)
                                for vid_url in mp4_matches:
                                    clean_url = vid_url.replace('\\/', '/').replace('\\u0026', '&')
                                    # Filter for xHamster CDN URLs
                                    if any(domain in clean_url for domain in ['xhcdn', 'xhamster', 'xhvid', 'xhpak']):
                                        video_sources.append({'quality': 'unknown', 'url': clean_url})
                
                # Method 4: Look for video/source tags with src attributes
                if not video_sources:
                    for tag in soup.find_all(['video', 'source']):
                        src = tag.get('src') or tag.get('data-src') or tag.get('data-url')
                        if src and ('.mp4' in src or '.m3u8' in src):
                            video_sources.append({'quality': 'unknown', 'url': src})
                
                # Method 5: Search for CDN URLs in the entire page
                if not video_sources:
                    cdn_patterns = [
                        r'https?://[a-zA-Z0-9.-]*xhcdn[a-zA-Z0-9.-]*/[^\s"\'<>\\]+\.mp4[^\s"\'<>\\]*',
                        r'https?://[a-zA-Z0-9.-]*xhvid[a-zA-Z0-9.-]*/[^\s"\'<>\\]+\.mp4[^\s"\'<>\\]*',
                        r'https?://[a-zA-Z0-9.-]*xhamster[a-zA-Z0-9.-]*/[^\s"\'<>\\]+\.mp4[^\s"\'<>\\]*',
                    ]
                    for pattern in cdn_patterns:
                        cdn_matches = re.findall(pattern, html_content)
                        for vid_url in cdn_matches:
                            clean_url = vid_url.replace('\\/', '/').replace('\\u0026', '&')
                            video_sources.append({'quality': 'unknown', 'url': clean_url})
                
                # Method 6: Look for JSON-LD data
                if not video_sources:
                    for script in soup.find_all('script', type='application/ld+json'):
                        try:
                            json_data = json_mod.loads(script.string)
                            if isinstance(json_data, dict):
                                content_url = json_data.get('contentUrl') or json_data.get('embedUrl')
                                if content_url and '.mp4' in content_url:
                                    video_sources.append({'quality': 'unknown', 'url': content_url})
                        except Exception:
                            pass
                
                # Remove duplicates while preserving order
                seen_urls = set()
                unique_sources = []
                for source in video_sources:
                    if source['url'] not in seen_urls:
                        seen_urls.add(source['url'])
                        unique_sources.append(source)
                video_sources = unique_sources
                
                if not video_sources:
                    self._print_rich("[red]✗ Could not extract video URL from page[/red]")
                    last_error = "No video sources found"
                    continue
                
                self._print_rich(f"[green]✓ Found {len(video_sources)} video source(s)[/green]")
                
                # Select best quality
                quality_order = ['1080p', '720p', '480p', '360p', '240p', 'unknown']
                video_url = None
                selected_quality = 'unknown'
                
                for q in quality_order:
                    for source in video_sources:
                        if source['quality'] == q:
                            video_url = source['url']
                            selected_quality = q
                            break
                    if video_url:
                        break
                
                # If no match by quality, just take the first one
                if not video_url and video_sources:
                    video_url = video_sources[0]['url']
                    selected_quality = video_sources[0]['quality']
                
                if not video_url:
                    self._print_rich("[red]✗ Could not find a valid video URL[/red]")
                    last_error = "No valid video URL"
                    continue
                
                self._print_rich(f"[dim]  Selected quality: {selected_quality}[/dim]")
                self._print_rich(f"[cyan]⬇ Downloading: {title[:50]}...[/cyan]")
                
                # Download the video directly
                output_dir = self.downloader.output_dir if hasattr(self.downloader, 'output_dir') else Path.home() / "Downloads"
                safe_title = re.sub(r'[<>:"/\\|?*]', '_', title)[:100]
                output_path = output_dir / f"{safe_title}.{output_format or 'mp4'}"
                
                # Stream download with headers
                download_headers = {
                    'Referer': url,
                    'Origin': urlparse(url).scheme + '://' + urlparse(url).netloc,
                    'Accept': '*/*',
                    'Accept-Encoding': 'identity;q=1, *;q=0',
                    'Range': 'bytes=0-',
                }
                video_response = self.session.get(video_url, stream=True, timeout=120, headers=download_headers)
                
                if video_response.status_code not in [200, 206]:
                    self._print_rich(f"[red]✗ Failed to download video (status: {video_response.status_code})[/red]")
                    # Try next source if available
                    for source in video_sources[1:]:
                        self._print_rich("[yellow]⚠ Trying alternate source...[/yellow]")
                        video_response = self.session.get(source['url'], stream=True, timeout=120, headers=download_headers)
                        if video_response.status_code in [200, 206]:
                            break
                    else:
                        last_error = f"Download failed with status {video_response.status_code}"
                        continue
                
                total_size = int(video_response.headers.get('content-length', 0))
                
                with open(output_path, 'wb') as f:
                    downloaded = 0
                    for chunk in video_response.iter_content(chunk_size=65536):
                        if chunk:
                            f.write(chunk)
                            downloaded += len(chunk)
                            if total_size:
                                progress = (downloaded / total_size) * 100
                                size_mb = downloaded / (1024 * 1024)
                                total_mb = total_size / (1024 * 1024)
                                print(f"\r  Progress: {progress:.1f}% ({size_mb:.1f}/{total_mb:.1f} MB)", end='', flush=True)
                
                print()  # New line after progress
                self._print_rich(f"[green]✓ Downloaded: {output_path.name}[/green]")
                self._print_rich(f"[dim]  Saved to: {output_path}[/dim]")
                
                return {
                    'title': title,
                    'uploader': 'Unknown',
                    'duration': 0,
                    'url': url,
                    'output_path': str(output_path),
                    'success': True
                }
                
            except Exception as e:
                last_error = str(e)
                self._print_rich(f"[red]✗ Attempt {attempt + 1} failed: {last_error}[/red]")
                if attempt < max_retries - 1:
                    continue
        
        # All retries exhausted
        self._print_rich(f"[red]✗ Fallback download failed after {max_retries} attempts[/red]")
        self._print_rich(f"[yellow]ℹ The video may require login or is region-restricted[/yellow]")
        return None
    
    def _download_channel(self, url: str, channel_type: str, quality: str = "best",
                          output_format: str = None, interactive: bool = True) -> Optional[Dict[str, Any]]:
        """Download videos from a channel/user/creator
        
        Args:
            url: Channel URL
            channel_type: 'channel' or 'creator'
            quality: Video quality
            output_format: Output format
            interactive: Whether to prompt for options
            
        Returns:
            Download info dict or None
        """
        try:
            # Extract username from URL
            if channel_type == 'creator':
                match = re.search(r'/creators/([^/]+)', url)
            else:
                match = re.search(r'/users/([^/]+)', url)
            
            username = match.group(1) if match else 'Unknown'
            
            self._print_rich(f"[cyan]⌕ Fetching {channel_type} videos for: {username}...[/cyan]")
            
            ydl_opts = self._get_ydl_opts(quality, output_format)
            ydl_opts['noplaylist'] = False
            
            # Limit downloads
            max_downloads = 20
            if interactive:
                try:
                    user_input = input(f"Maximum videos to download (default: {max_downloads}): ").strip()
                    if user_input:
                        max_downloads = int(user_input)
                except (ValueError, KeyboardInterrupt):
                    pass
            
            ydl_opts['playlistend'] = max_downloads
            
            with yt_dlp.YoutubeDL({**ydl_opts, 'extract_flat': True}) as ydl:
                info = ydl.extract_info(url, download=False)
                
                if not info:
                    self._print_rich(f"[red]✗ Could not extract {channel_type} information[/red]")
                    return None
                
                entries = info.get('entries', [])
                total_videos = len(entries) if entries else 0
                channel_title = info.get('title', username)
                
                if total_videos == 0:
                    self._print_rich(f"[yellow]⚠ No videos found for this {channel_type}[/yellow]")
                    return None
                
                # Display channel info
                channel_info = f"""[bold]Channel:[/bold] {channel_title}
[bold]Videos Found:[/bold] {total_videos}
[bold]Downloading:[/bold] up to {max_downloads}"""
                
                self._print_panel(channel_info, title=f"📁 {channel_type.title()} Info", border_style="blue")
            
            # Download videos
            self._print_rich(f"[cyan]⬇ Downloading videos from {channel_title}...[/cyan]")
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            
            self._print_rich(f"[green]✓ Successfully downloaded from: {channel_title}[/green]")
            
            return {
                'channel': channel_title,
                'type': channel_type,
                'total_videos': total_videos,
                'max_downloads': max_downloads,
                'url': url,
                'success': True
            }
            
        except Exception as e:
            self._print_rich(f"[red]✗ Error downloading {channel_type}: {str(e)}[/red]")
            return None
    
    def _download_gallery(self, url: str) -> Optional[Dict[str, Any]]:
        """Download photos from a gallery
        
        Args:
            url: Gallery URL
            
        Returns:
            Download info dict or None
        """
        if not REQUESTS_AVAILABLE or not BS4_AVAILABLE:
            self._print_rich("[red]Error: requests and BeautifulSoup are required for gallery downloads[/red]")
            return None
        
        try:
            self._print_rich("[cyan]⌕ Extracting gallery information...[/cyan]")
            
            response = self.session.get(url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Get gallery title
            h1 = soup.find('h1')
            if h1 and h1.find('a'):
                # Follow redirect if needed
                redirect_url = h1.find('a')['href']
                return self._download_gallery(redirect_url)
            
            title = h1.text.strip() if h1 else 'Unknown Gallery'
            
            # Create output directory
            output_dir = self.downloader.output_dir if hasattr(self.downloader, 'output_dir') else Path.home() / "Downloads"
            gallery_dir = output_dir / sanitize_filename(title)
            gallery_dir.mkdir(parents=True, exist_ok=True)
            
            # Collect all photos across pages
            all_photos = []
            seen_ids = set()
            page = 1
            base_url = url.rstrip('/')
            
            # Remove page number from URL if present
            if '/photos/gallery/' in base_url:
                parts = base_url.split('/photos/gallery/')[1].split('/')
                if len(parts) > 1 and parts[-1].isdigit():
                    base_url = '/'.join(base_url.split('/')[:-1])
            
            while page <= 100:  # Max 100 pages
                if page == 1:
                    page_url = base_url
                else:
                    page_url = f"{base_url}/{page}"
                
                self._print_rich(f"[dim]  Scanning page {page}...[/dim]")
                
                response = self.session.get(page_url)
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Find photo slider
                photo_slider = soup.find('div', id='photo-slider')
                if not photo_slider:
                    break
                
                # Find all photo links
                photos = photo_slider.find_all('a', id=lambda x: x and x.startswith('photo-'))
                
                if not photos:
                    break
                
                new_photos = 0
                for photo in photos:
                    photo_id = photo['id'].replace('photo-', '')
                    if photo_id in seen_ids:
                        continue
                    
                    seen_ids.add(photo_id)
                    img_url = photo.get('href')
                    if img_url:
                        all_photos.append({
                            'id': photo_id,
                            'url': img_url,
                            'referer': page_url
                        })
                        new_photos += 1
                
                if new_photos == 0:
                    break
                
                page += 1
            
            if not all_photos:
                self._print_rich("[yellow]⚠ No photos found in this gallery[/yellow]")
                return None
            
            # Display gallery info
            gallery_info = f"""[bold]Title:[/bold] {title}
[bold]Photos:[/bold] {len(all_photos)}"""
            
            self._print_panel(gallery_info, title="📷 Gallery Info", border_style="magenta")
            
            # Download photos
            self._print_rich(f"[cyan]⬇ Downloading {len(all_photos)} photos...[/cyan]")
            
            downloaded = 0
            failed = 0
            
            for i, photo in enumerate(all_photos, 1):
                try:
                    # Get file extension
                    ext = '.jpg'
                    if '.' in photo['url'].split('/')[-1]:
                        ext = '.' + photo['url'].split('.')[-1].split('?')[0].lower()
                    
                    filename = f"{photo['id']}{ext}"
                    filepath = gallery_dir / filename
                    
                    # Download with referer
                    headers = {'Referer': photo['referer']}
                    response = self.session.get(photo['url'], headers=headers)
                    response.raise_for_status()
                    
                    with open(filepath, 'wb') as f:
                        f.write(response.content)
                    
                    downloaded += 1
                    
                    if i % 10 == 0 or i == len(all_photos):
                        self._print_rich(f"[dim]  [{i}/{len(all_photos)}] Downloaded[/dim]")
                    
                except Exception as e:
                    failed += 1
                    self._print_rich(f"[yellow]  [{i}/{len(all_photos)}] Failed: {str(e)}[/yellow]")
            
            self._print_rich(f"[green]✓ Download complete: {downloaded} succeeded, {failed} failed[/green]")
            self._print_rich(f"[dim]  Saved to: {gallery_dir}[/dim]")
            
            return {
                'title': title,
                'type': 'gallery',
                'total_photos': len(all_photos),
                'downloaded': downloaded,
                'failed': failed,
                'output_dir': str(gallery_dir),
                'success': True
            }
            
        except Exception as e:
            self._print_rich(f"[red]✗ Error downloading gallery: {str(e)}[/red]")
            return None
    
    def search_and_download(self, url: str, interactive: bool = True) -> Optional[Dict[str, Any]]:
        """Main entry point for downloading xHamster content
        
        Args:
            url: xHamster URL
            interactive: Whether to prompt for options
            
        Returns:
            Download info on success, None on failure
        """
        # Validate URL
        if not self.is_xhamster_url(url):
            self._print_rich(f"[red]Error: Not a valid xHamster URL[/red]")
            return None
        
        # Check for xHamsterLive (not supported)
        if 'xhamsterlive' in url.lower():
            self._print_rich("[red]Error: xHamsterLive streams are not supported[/red]")
            return None
        
        # Download with default settings
        return self.download(url, quality="best", interactive=interactive)
