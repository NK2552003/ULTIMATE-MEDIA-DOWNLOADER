#!/usr/bin/env python3
"""
TikTok Handler Module
Handles downloading videos from TikTok using yt-dlp with proper configuration
and security bypass methods.
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

warnings.filterwarnings('ignore')

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
    from rich.table import Table
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

from utils.utils import sanitize_filename
from utils.ui_components import Icons, Messages


class SSLAdapter(HTTPAdapter):
    """Custom adapter for SSL/TLS handling"""
    
    def __init__(self, *args, **kwargs):
        self.ssl_context = kwargs.pop('ssl_context', None)
        super().__init__(*args, **kwargs)
    
    def init_poolmanager(self, *args, **kwargs):
        if self.ssl_context:
            kwargs['ssl_context'] = self.ssl_context
        else:
            try:
                ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
                ctx.check_hostname = False
                ctx.verify_mode = ssl.CERT_NONE
                ctx.minimum_version = ssl.TLSVersion.TLSv1_2
                ctx.set_ciphers('DEFAULT:@SECLEVEL=1')
            except Exception:
                ctx = ssl.create_default_context()
                ctx.check_hostname = False
                ctx.verify_mode = ssl.CERT_NONE
            kwargs['ssl_context'] = ctx
        return super().init_poolmanager(*args, **kwargs)


class TikTokHandler:
    """Handles TikTok video downloads"""
    
    SUPPORTED_DOMAINS = [
        'tiktok.com',
        'www.tiktok.com',
        'vm.tiktok.com',
        'm.tiktok.com',
        'vt.tiktok.com',
    ]
    
    USER_AGENTS = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Linux; Android 14; SM-S918B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
    ]
    
    def __init__(self, downloader):
        self.downloader = downloader
        self.console = Console() if RICH_AVAILABLE else None
        self.session = None
        self.current_user_agent = None
        
        if REQUESTS_AVAILABLE:
            self._init_session()
    
    def _get_random_user_agent(self) -> str:
        return random.choice(self.USER_AGENTS)
    
    def _init_session(self):
        self.session = requests.Session()
        
        ssl_adapter = SSLAdapter(
            max_retries=Retry(total=5, backoff_factor=1, status_forcelist=[500, 502, 503, 504])
        )
        self.session.mount('https://', ssl_adapter)
        self.session.mount('http://', HTTPAdapter(max_retries=Retry(total=3)))
        
        self.current_user_agent = self._get_random_user_agent()
        
        self.session.headers.update({
            'User-Agent': self.current_user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
        })
    
    @classmethod
    def is_tiktok_url(cls, url: str) -> bool:
        url_lower = url.lower()
        return any(domain in url_lower for domain in cls.SUPPORTED_DOMAINS)
    
    def extract_video_id(self, url: str) -> Optional[str]:
        # URL format: https://www.tiktok.com/@user/video/1234567890
        match = re.search(r'/video/(\d+)', url, re.I)
        if match:
            return match.group(1)
        return None
    
    def _print_rich(self, message: str, style: str = "bold cyan"):
        if RICH_AVAILABLE and self.console:
            self.console.print(message, style=style)
        else:
            clean_msg = re.sub(r'\[.*?\]', '', message)
            print(clean_msg)
    
    def _print_panel(self, content: str, title: str = "", border_style: str = "cyan"):
        if RICH_AVAILABLE and self.console:
            self.console.print(Panel(content, title=title, border_style=border_style))
        else:
            print(f"\n{'='*50}")
            if title:
                print(f"  {title}")
            print(content)
            print(f"{'='*50}\n")
    
    def _get_available_qualities(self, url: str) -> List[Dict[str, Any]]:
        qualities = []
        
        try:
            if not YT_DLP_AVAILABLE:
                return qualities
            
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'nocheckcertificate': True,
                'geo_bypass': True,
                'extractor_args': {'tiktok': {'api_hostname': 'api16-normal-c-useast1a.tiktokv.com'}},
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
                    
                    qualities.sort(key=lambda x: x['height'], reverse=True)
        
        except Exception as e:
            self._print_rich(f"[yellow]⚠ Could not extract quality info: {str(e)}[/yellow]")
        
        return qualities
    
    def _display_qualities(self, qualities: List[Dict[str, Any]]) -> Optional[str]:
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
    
    def _get_ydl_opts(self, quality: str = "best", output_format: str = None, watermark: bool = False) -> Dict[str, Any]:
        output_dir = self.downloader.output_dir if hasattr(self.downloader, 'output_dir') else Path.home() / "Downloads"
        
        if quality == "best":
            format_str = "bestvideo+bestaudio/best"
        elif quality in ["1080p", "1080"]:
            format_str = "bestvideo[height<=1080]+bestaudio/best[height<=1080]"
        elif quality in ["720p", "720"]:
            format_str = "bestvideo[height<=720]+bestaudio/best[height<=720]"
        elif quality in ["480p", "480"]:
            format_str = "bestvideo[height<=480]+bestaudio/best[height<=480]"
        else:
            format_str = "bestvideo+bestaudio/best"
        
        # TikTok specific: prefer no watermark if available
        if not watermark:
            format_str = f"download_addr-2/download_addr-1/{format_str}"
        
        ydl_opts = {
            'format': format_str,
            'outtmpl': str(output_dir / '%(uploader)s - %(title).80B.%(ext)s'),
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
            'writethumbnail': True,
            'embedthumbnail': True,
            'merge_output_format': output_format or 'mp4',
            'postprocessors': [],
            'http_headers': {
                'User-Agent': self.current_user_agent or self._get_random_user_agent(),
                'Referer': 'https://www.tiktok.com/',
            },
            'extractor_args': {
                'tiktok': {
                    'api_hostname': 'api16-normal-c-useast1a.tiktokv.com',
                }
            },
        }
        
        if output_format in [None, 'mp4']:
            ydl_opts['postprocessors'].extend([
                {'key': 'FFmpegMetadata', 'add_metadata': True},
                {'key': 'EmbedThumbnail', 'already_have_thumbnail': False},
            ])
        
        return ydl_opts
    
    def download(self, url: str, quality: str = "best", output_format: str = None,
                 interactive: bool = True, watermark: bool = False) -> Optional[Dict[str, Any]]:
        if not YT_DLP_AVAILABLE:
            self._print_rich("[red]Error: yt-dlp is required for TikTok downloads[/red]")
            return None
        
        download_info = f"""[bold cyan]Platform:[/bold cyan] [yellow]TikTok[/yellow]
[bold cyan]URL:[/bold cyan] [blue]{url[:60]}...[/blue]
[bold cyan]Watermark:[/bold cyan] [magenta]{'Yes' if watermark else 'No'}[/magenta]"""
        
        self._print_panel(download_info, title="▸ TikTok Download", border_style="magenta")
        
        if interactive:
            self._print_rich("[cyan]⌕ Fetching available qualities...[/cyan]")
            qualities = self._get_available_qualities(url)
            if qualities:
                quality = self._display_qualities(qualities)
            
            # Ask about watermark
            watermark_choice = input("\nRemove watermark? (Y/n) [default: Y]: ").strip().lower()
            watermark = watermark_choice == 'n'
        
        self._print_rich(f"[cyan]⌕ Selected quality: {quality}[/cyan]")
        
        return self._download_video(url, quality, output_format, watermark)
    
    def _download_video(self, url: str, quality: str = "best",
                        output_format: str = None, watermark: bool = False) -> Optional[Dict[str, Any]]:
        try:
            ydl_opts = self._get_ydl_opts(quality, output_format, watermark)
            
            self._print_rich("[cyan]⌕ Extracting video information...[/cyan]")
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                
                if not info:
                    self._print_rich("[red]✗ Could not extract video information[/red]")
                    return None
                
                title = info.get('title', 'Unknown')
                uploader = info.get('uploader', 'Unknown')
                duration = info.get('duration', 0)
                like_count = info.get('like_count', 0)
                comment_count = info.get('comment_count', 0)
                
                duration_str = f"{duration}s" if duration else "Unknown"
                video_info = f"""[bold]Title:[/bold] {title}
[bold]Creator:[/bold] @{uploader}
[bold]Duration:[/bold] {duration_str}
[bold]Likes:[/bold] {like_count:,}
[bold]Comments:[/bold] {comment_count:,}"""
                
                self._print_panel(video_info, title="📱 TikTok Video Info", border_style="green")
                
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
                
        except Exception as e:
            self._print_rich(f"[red]✗ Error downloading video: {str(e)}[/red]")
            return None
    
    def search_and_download(self, url: str, interactive: bool = True) -> Optional[Dict[str, Any]]:
        if not self.is_tiktok_url(url):
            self._print_rich(f"[red]Error: Not a valid TikTok URL[/red]")
            return None
        
        return self.download(url, quality="best", interactive=interactive)
