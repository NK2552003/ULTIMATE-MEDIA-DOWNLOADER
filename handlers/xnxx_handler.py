#!/usr/bin/env python3
"""
XNXX Handler Module
Handles downloading videos from XNXX using yt-dlp with proper configuration
and fallback methods for video extraction.
"""

import os
import re
import warnings
from pathlib import Path
from typing import Optional, Dict, Any, List
from urllib.parse import urlparse

# Suppress warnings
warnings.filterwarnings('ignore')

try:
    import yt_dlp
    YT_DLP_AVAILABLE = True
except ImportError:
    YT_DLP_AVAILABLE = False

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
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

from utils.utils import sanitize_filename
from utils.ui_components import Icons, Messages


class XNXXHandler:
    """Handles XNXX video downloads"""
    
    # Supported domains (including numbered variants like xnxx2.com, xnxx3.com etc.)
    SUPPORTED_DOMAINS = [
        'xnxx.com',
        'xnxx.dev',
        'xnxx.tv',
        'www.xnxx.com',
        'www.xnxx.dev',
        'www.xnxx.tv',
    ]
    
    # Regex pattern for numbered domains (xnxx2.com, xnxx3.com, etc.)
    DOMAIN_PATTERN = re.compile(r'xnxx\d*\.(com|dev|tv|es)', re.I)
    
    def __init__(self, downloader):
        """Initialize XNXX handler with reference to main downloader
        
        Args:
            downloader: Reference to UltimateMediaDownloader instance
        """
        self.downloader = downloader
        self.console = Console() if RICH_AVAILABLE else None
        self.session = None
        
        # Initialize session
        if REQUESTS_AVAILABLE:
            self._init_session()
    
    def _init_session(self):
        """Initialize requests session with required headers"""
        self.session = requests.Session()
        
        # Set user agent
        self.session.headers.update({
            'User-Agent': self.downloader._get_random_user_agent() if hasattr(self.downloader, '_get_random_user_agent') else 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
        })
    
    @classmethod
    def is_xnxx_url(cls, url: str) -> bool:
        """Check if URL is an XNXX URL
        
        Args:
            url: URL to check
            
        Returns:
            True if URL is from XNXX
        """
        url_lower = url.lower()
        
        # Check standard domains
        if any(domain in url_lower for domain in cls.SUPPORTED_DOMAINS):
            return True
        
        # Check numbered domains (xnxx2.com, xnxx3.com, etc.)
        if cls.DOMAIN_PATTERN.search(url_lower):
            return True
        
        return False
    
    @classmethod
    def fix_url(cls, url: str) -> str:
        """Normalize XNXX URL to standard xnxx.com domain
        
        Args:
            url: Original URL
            
        Returns:
            Normalized URL
        """
        # Replace numbered domains with standard xnxx.com
        url = cls.DOMAIN_PATTERN.sub('xnxx.com', url)
        return url
    
    def extract_video_id(self, url: str) -> Optional[str]:
        """Extract video ID from XNXX URL
        
        Args:
            url: XNXX URL
            
        Returns:
            Video ID or None
        """
        # Normalize URL first
        url = self.fix_url(url)
        
        # Extract ID from URL path (e.g., /video-abc123/title)
        if 'xnxx.com/' in url:
            parts = url.split('xnxx.com/')[1].split('/')
            if parts:
                return parts[0]
        
        return None
    
    def _print_rich(self, message: str, style: str = "bold cyan"):
        """Print with Rich formatting if available"""
        if RICH_AVAILABLE and self.console:
            self.console.print(message, style=style)
        else:
            # Strip Rich markup for plain print
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
        """Download video from XNXX
        
        Args:
            url: XNXX video URL
            quality: Video quality (best, 1080p, 720p, 480p, etc.)
            output_format: Output format (mp4, etc.)
            interactive: Whether to prompt for options
            
        Returns:
            Dictionary with download info on success, None on failure
        """
        if not YT_DLP_AVAILABLE:
            self._print_rich("[red]Error: yt-dlp is required for XNXX downloads[/red]")
            return None
        
        # Normalize URL
        url = self.fix_url(url)
        
        # Show download info panel
        download_info = f"""[bold cyan]Platform:[/bold cyan] [yellow]XNXX[/yellow]
[bold cyan]Quality:[/bold cyan] [magenta]{quality}[/magenta]
[bold cyan]Format:[/bold cyan] [blue]{output_format or 'mp4'}[/blue]"""
        
        self._print_panel(download_info, title="▸ XNXX Download", border_style="orange1")
        
        return self._download_video(url, quality, output_format)
    
    def _get_ydl_opts(self, quality: str = "best", output_format: str = None) -> Dict[str, Any]:
        """Get yt-dlp options for XNXX
        
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
            'nocheckcertificate': True,
            'geo_bypass': True,
            'quiet': not getattr(self.downloader, 'verbose', False),
            'no_warnings': True,
            'retries': 10,
            'fragment_retries': 10,
            'skip_unavailable_fragments': True,
            'keepvideo': False,
            'writethumbnail': True,
            'embedthumbnail': True,
            'merge_output_format': output_format or 'mp4',
            'postprocessors': [],
            'http_headers': {
                'User-Agent': self.session.headers.get('User-Agent') if self.session else 'Mozilla/5.0',
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
                
                # Display video info
                duration_str = f"{duration // 60}:{duration % 60:02d}" if duration else "Unknown"
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
            error_msg = str(e)
            if 'private' in error_msg.lower():
                self._print_rich("[red]✗ This video is private or requires login[/red]")
            elif 'removed' in error_msg.lower() or 'deleted' in error_msg.lower():
                self._print_rich("[red]✗ This video has been removed[/red]")
            else:
                self._print_rich(f"[red]✗ Download error: {error_msg}[/red]")
            return None
        except Exception as e:
            self._print_rich(f"[red]✗ Error downloading video: {str(e)}[/red]")
            return None
    
    def _extract_hls_url(self, url: str) -> Optional[str]:
        """Extract HLS stream URL from page (fallback method)
        
        Args:
            url: Page URL
            
        Returns:
            HLS URL or None
        """
        if not REQUESTS_AVAILABLE or not BS4_AVAILABLE:
            return None
        
        try:
            response = self.session.get(url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Look for HLS URL in script tags
            for script in soup.find_all('script'):
                script_text = script.text or script.string or ''
                
                # Try to find setVideoHLS call
                match = re.search(r'''html5player\.setVideoHLS\(['"](.+?)['"]''', script_text)
                if match:
                    return match.group(1)
                
                # Alternative pattern
                match = re.search(r'''setVideoUrlHigh\(['"](.+?)['"]''', script_text)
                if match:
                    return match.group(1)
            
            return None
            
        except Exception as e:
            self._print_rich(f"[yellow]⚠ Could not extract HLS URL: {str(e)}[/yellow]")
            return None
    
    def search_and_download(self, url: str, interactive: bool = True) -> Optional[Dict[str, Any]]:
        """Main entry point for downloading XNXX content
        
        Args:
            url: XNXX URL
            interactive: Whether to prompt for options
            
        Returns:
            Download info on success, None on failure
        """
        # Validate URL
        if not self.is_xnxx_url(url):
            self._print_rich(f"[red]Error: Not a valid XNXX URL[/red]")
            return None
        
        # Download with default settings
        return self.download(url, quality="best", interactive=interactive)
