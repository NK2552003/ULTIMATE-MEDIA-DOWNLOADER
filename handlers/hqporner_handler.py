#!/usr/bin/env python3
"""
HQPorner Handler Module
Handles downloading videos from hqporner.com using yt-dlp with proper configuration
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
    """Custom adapter to handle SSL/TLS issues"""
    
    def __init__(self, *args, **kwargs):
        self.ssl_context = kwargs.pop('ssl_context', None)
        super().__init__(*args, **kwargs)
    
    def init_poolmanager(self, *args, **kwargs):
        if self.ssl_context:
            kwargs['ssl_context'] = self.ssl_context
        else:
            try:
                # For Python 3.14+, check_hostname must be set before verify_mode
                ctx = ssl.create_default_context()
                ctx.check_hostname = False
                ctx.verify_mode = ssl.CERT_NONE
            except Exception:
                ctx = ssl.create_default_context()
                ctx.check_hostname = False
                ctx.verify_mode = ssl.CERT_NONE
            
            kwargs['ssl_context'] = ctx
        return super().init_poolmanager(*args, **kwargs)


class HQPornerHandler:
    """Handles HQPorner video downloads"""
    
    SUPPORTED_DOMAINS = [
        'hqporner.com',
        'www.hqporner.com',
    ]
    
    USER_AGENTS = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
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
            'Upgrade-Insecure-Requests': '1',
        })
        
        self.session.cookies.update({
            'age_verified': '1',
        })
    
    @classmethod
    def is_hqporner_url(cls, url: str) -> bool:
        url_lower = url.lower()
        return any(domain in url_lower for domain in cls.SUPPORTED_DOMAINS)
    
    def extract_video_id(self, url: str) -> Optional[str]:
        # URL format: https://hqporner.com/hdporn/12345-video-title.html
        match = re.search(r'/hdporn/(\d+-[^/]+)\.html', url, re.I)
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
        """Get available video qualities"""
        qualities = []
        
        try:
            if not YT_DLP_AVAILABLE:
                return qualities
            
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'nocheckcertificate': True,
                'geo_bypass': True,
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
        """Display available qualities and let user choose"""
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
        output_dir = self.downloader.output_dir if hasattr(self.downloader, 'output_dir') else Path.home() / "Downloads"
        
        if quality == "best":
            format_str = "bestvideo+bestaudio/best"
        elif quality in ["2160p", "4k", "4K"]:
            format_str = "bestvideo[height<=2160]+bestaudio/best[height<=2160]"
        elif quality in ["1080p", "1080"]:
            format_str = "bestvideo[height<=1080]+bestaudio/best[height<=1080]"
        elif quality in ["720p", "720"]:
            format_str = "bestvideo[height<=720]+bestaudio/best[height<=720]"
        elif quality in ["480p", "480"]:
            format_str = "bestvideo[height<=480]+bestaudio/best[height<=480]"
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
                'Cookie': 'age_verified=1',
            },
        }
        
        if output_format in [None, 'mp4']:
            ydl_opts['postprocessors'].extend([
                {'key': 'FFmpegMetadata', 'add_metadata': True},
                {'key': 'EmbedThumbnail', 'already_have_thumbnail': False},
            ])
        
        return ydl_opts
    
    def _extract_video_from_page(self, url: str) -> Optional[Dict[str, Any]]:
        """Extract video URL and info from HQPorner page (two-step: page -> iframe -> video)"""
        if not REQUESTS_AVAILABLE or not BS4_AVAILABLE:
            self._print_rich("[yellow]⚠ requests and beautifulsoup4 are required[/yellow]")
            return None
        
        try:
            self._print_rich("[cyan]⌕ Fetching page content...[/cyan]")
            response = self.session.get(url, timeout=30, verify=False)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract title from HQPorner page
            title = None
            title_tag = soup.find('h1', class_='main-h1') or soup.find('h1') or soup.find('title')
            if title_tag:
                title = title_tag.get_text(strip=True)
                # Clean up title
                title = re.sub(r'\s*-\s*HQporner.*$', '', title, flags=re.I)
                title = re.sub(r'\s*\|\s*HQporner.*$', '', title, flags=re.I)
            
            # Step 1: Find iframe URL (usually mydaddy.cc or similar)
            iframe = soup.find('iframe')
            if not iframe:
                self._print_rich("[yellow]⚠ No video iframe found on page[/yellow]")
                return None
            
            iframe_src = iframe.get('src', '') or iframe.get('data-src', '')
            if not iframe_src:
                self._print_rich("[yellow]⚠ Iframe has no source URL[/yellow]")
                return None
            
            # Clean up iframe URL
            if iframe_src.startswith('//'):
                iframe_src = 'https:' + iframe_src
            elif not iframe_src.startswith('http'):
                iframe_src = urljoin(url, iframe_src)
            
            self._print_rich(f"[cyan]⌕ Found video player: {iframe_src[:50]}...[/cyan]")
            
            # Step 2: Fetch the iframe page to get actual video sources
            iframe_headers = {
                'User-Agent': self.current_user_agent or self._get_random_user_agent(),
                'Referer': url,
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            }
            
            iframe_response = self.session.get(iframe_src, headers=iframe_headers, timeout=30, verify=False)
            iframe_response.raise_for_status()
            
            iframe_content = iframe_response.text
            
            # Extract video sources using regex (handles both escaped and unescaped quotes)
            video_sources = []
            
            # Pattern that handles both regular quotes and escaped quotes (from JS strings)
            # Matches: src="//url.mp4" title="720p" OR src=\"//url.mp4\" title=\"720p\"
            source_pattern = r'src=\\?["\']?(//[^\s"\'\\>]+\.mp4)\\?["\']?[^>]*?title=\\?["\']?([^"\'\\>]*)\\?["\']?'
            source_matches = re.findall(source_pattern, iframe_content)
            
            for src, quality_title in source_matches:
                if src:
                    if src.startswith('//'):
                        src = 'https:' + src
                    
                    # Extract quality number from title (e.g., "1080p Full HD" -> 1080)
                    quality_match = re.search(r'(\d+)p?', quality_title)
                    quality = int(quality_match.group(1)) if quality_match else 0
                    
                    video_sources.append({
                        'url': src,
                        'quality': quality,
                        'quality_label': quality_title.strip() or f'{quality}p',
                    })
            
            # Method 2: If no matches, try just finding all MP4 URLs
            if not video_sources:
                mp4_pattern = r'(//[^\s"\'\\<>]+\.mp4)'
                mp4_matches = re.findall(mp4_pattern, iframe_content)
                
                for src in mp4_matches:
                    if src.startswith('//'):
                        src = 'https:' + src
                    
                    quality_match = re.search(r'/(\d+)\.mp4', src)
                    quality = int(quality_match.group(1)) if quality_match else 0
                    
                    video_sources.append({
                        'url': src,
                        'quality': quality,
                        'quality_label': f'{quality}p',
                    })
            
            if not video_sources:
                self._print_rich("[yellow]⚠ No video sources found in player[/yellow]")
                return None
            
            # Sort by quality (highest first)
            video_sources.sort(key=lambda x: x['quality'], reverse=True)
            
            # Remove duplicates
            seen_urls = set()
            unique_sources = []
            for src in video_sources:
                if src['url'] not in seen_urls:
                    seen_urls.add(src['url'])
                    unique_sources.append(src)
            
            self._print_rich(f"[green]✓ Found {len(unique_sources)} quality options[/green]")
            
            return {
                'title': title or 'HQPorner Video',
                'video_sources': unique_sources,
                'best_url': unique_sources[0]['url'] if unique_sources else None,
                'iframe_url': iframe_src,
            }
            
        except Exception as e:
            self._print_rich(f"[yellow]⚠ Could not extract from page: {str(e)}[/yellow]")
            import traceback
            traceback.print_exc()
            return None
    
    def download(self, url: str, quality: str = "best", output_format: str = None,
                 interactive: bool = True) -> Optional[Dict[str, Any]]:
        if not YT_DLP_AVAILABLE:
            self._print_rich("[red]Error: yt-dlp is required for HQPorner downloads[/red]")
            return None
        
        download_info = f"""[bold cyan]Platform:[/bold cyan] [yellow]HQPorner[/yellow]
[bold cyan]URL:[/bold cyan] [blue]{url[:60]}...[/blue]"""
        
        self._print_panel(download_info, title="▸ HQPorner Download", border_style="orange1")
        
        # First, extract video info from the page
        video_info = self._extract_video_from_page(url)
        
        if not video_info or not video_info.get('video_sources'):
            self._print_rich("[red]✗ Could not find video on the page[/red]")
            return None
        
        self._print_rich(f"[green]✓ Found video: {video_info['title']}[/green]")
        
        # Always show quality selection when multiple qualities are available
        video_sources = video_info['video_sources']
        selected_url = video_info['best_url']
        
        if len(video_sources) > 0:
            # Show quality table and let user select (or auto-select best if non-interactive)
            selected_url = self._select_quality(video_sources, interactive=interactive)
        
        return self._download_video(url, video_info['title'], selected_url, video_info.get('iframe_url'), output_format)
    
    def _select_quality(self, video_sources: List[Dict[str, Any]], interactive: bool = True) -> str:
        """Display quality options and let user select (or auto-select if non-interactive)"""
        # Always display the quality table
        if RICH_AVAILABLE and self.console:
            table = Table(title="📊 Available Qualities", border_style="cyan", 
                         show_header=True, header_style="bold cyan")
            table.add_column("#", style="dim", width=4, justify="center")
            table.add_column("Quality", style="cyan", width=20)
            table.add_column("Resolution", style="green", width=15)
            
            for i, src in enumerate(video_sources, 1):
                quality_label = src['quality_label']
                resolution = f"{src['quality']}p" if src['quality'] else "Unknown"
                table.add_row(str(i), quality_label, resolution)
            
            self.console.print()
            self.console.print(table)
            self.console.print()
        else:
            print("\n📊 Available Qualities:")
            print("-" * 40)
            for i, src in enumerate(video_sources, 1):
                print(f"  {i}. {src['quality_label']}")
            print("-" * 40)
        
        # If not interactive, auto-select best quality
        if not interactive:
            self._print_rich(f"[cyan]⌕ Auto-selected best quality: {video_sources[0]['quality_label']}[/cyan]")
            return video_sources[0]['url']
        
        # Interactive: prompt for selection
        try:
            if RICH_AVAILABLE and self.console:
                from rich.prompt import Prompt
                choice = Prompt.ask(
                    f"[bold yellow]⌕[/bold yellow] Select quality",
                    choices=[str(i) for i in range(1, len(video_sources) + 1)],
                    default="1"
                )
            else:
                choice = input(f"⌕ Select quality (1-{len(video_sources)}) [default: 1]: ").strip()
                if not choice:
                    choice = "1"
            
            choice_num = int(choice)
            if 1 <= choice_num <= len(video_sources):
                selected = video_sources[choice_num - 1]
                self._print_rich(f"[cyan]⌕ Selected: {selected['quality_label']}[/cyan]")
                return selected['url']
        except (ValueError, IndexError, KeyboardInterrupt):
            pass
        
        self._print_rich(f"[cyan]⌕ Using best quality: {video_sources[0]['quality_label']}[/cyan]")
        return video_sources[0]['url']
    
    def _download_video(self, original_url: str, title: str, video_url: str,
                        referer_url: str = None, output_format: str = None) -> Optional[Dict[str, Any]]:
        try:
            output_dir = self.downloader.output_dir if hasattr(self.downloader, 'output_dir') else Path.home() / "Downloads"
            
            self._print_rich(f"[cyan]⬇ Downloading: {title}[/cyan]")
            
            # Try direct download first since the URLs are direct MP4 links
            result = self._direct_download(video_url, title, output_dir, referer_url or original_url)
            
            if result:
                return result
            
            # Fallback to yt-dlp if direct download fails
            self._print_rich("[yellow]⚠ Direct download failed, trying yt-dlp...[/yellow]")
            
            ydl_opts = {
                'format': 'best',
                'outtmpl': str(output_dir / f'{sanitize_filename(title)}.%(ext)s'),
                'restrictfilenames': False,
                'windowsfilenames': True,
                'trim_file_name': 200,
                'nocheckcertificate': True,
                'geo_bypass': True,
                'quiet': not getattr(self.downloader, 'verbose', False),
                'no_warnings': True,
                'retries': 10,
                'merge_output_format': output_format or 'mp4',
                'http_headers': {
                    'User-Agent': self.current_user_agent or self._get_random_user_agent(),
                    'Referer': referer_url or original_url,
                },
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([video_url])
                self._print_rich(f"[green]✓ Successfully downloaded: {title}[/green]")
                
                return {
                    'title': title,
                    'url': original_url,
                    'video_url': video_url,
                    'success': True
                }
                
        except Exception as e:
            self._print_rich(f"[red]✗ Error downloading video: {str(e)}[/red]")
            return None
    
    def _direct_download(self, video_url: str, title: str, output_dir: Path, 
                         referer: str) -> Optional[Dict[str, Any]]:
        """Download video directly using requests with proper progress display"""
        if not REQUESTS_AVAILABLE:
            self._print_rich("[red]✗ requests library not available for direct download[/red]")
            return None
        
        try:
            self._print_rich("[cyan]⬇ Attempting direct download...[/cyan]")
            
            headers = {
                'User-Agent': self.current_user_agent or self._get_random_user_agent(),
                'Referer': referer,
                'Accept': '*/*',
                'Accept-Language': 'en-US,en;q=0.9',
            }
            
            response = self.session.get(video_url, headers=headers, stream=True, 
                                        timeout=60, verify=False)
            response.raise_for_status()
            
            # Get file extension from content type or URL
            content_type = response.headers.get('content-type', '')
            if 'video/mp4' in content_type:
                ext = 'mp4'
            elif 'video/webm' in content_type:
                ext = 'webm'
            else:
                ext = 'mp4'  # Default to mp4
            
            filename = sanitize_filename(title) + f'.{ext}'
            filepath = output_dir / filename
            
            # Get total size for progress
            total_size = int(response.headers.get('content-length', 0))
            
            if total_size:
                total_mb = total_size / 1024 / 1024
                self._print_rich(f"[cyan]📦 File size: {total_mb:.1f} MB[/cyan]")
            
            downloaded = 0
            start_time = __import__('time').time()
            last_update_time = start_time
            last_downloaded = 0
            
            # Use Rich Progress if available
            if RICH_AVAILABLE and self.console:
                from rich.progress import Progress, BarColumn, DownloadColumn, TransferSpeedColumn, TimeRemainingColumn, TextColumn
                
                with Progress(
                    TextColumn("[bold yellow]▼[/bold yellow]"),
                    TextColumn("[bold green]{task.percentage:>5.1f}%[/bold green]"),
                    BarColumn(bar_width=30, complete_style="cyan", finished_style="green"),
                    DownloadColumn(),
                    TextColumn("│"),
                    TransferSpeedColumn(),
                    TextColumn("│ ETA:"),
                    TimeRemainingColumn(),
                    console=self.console,
                    transient=True,
                ) as progress:
                    task = progress.add_task("Downloading", total=total_size or 100)
                    
                    with open(filepath, 'wb') as f:
                        for chunk in response.iter_content(chunk_size=65536):  # 64KB chunks
                            if chunk:
                                f.write(chunk)
                                downloaded += len(chunk)
                                progress.update(task, completed=downloaded)
            else:
                # Fallback to ANSI progress display
                with open(filepath, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=65536):  # 64KB chunks
                        if chunk:
                            f.write(chunk)
                            downloaded += len(chunk)
                            
                            current_time = __import__('time').time()
                            
                            # Update every 0.1 seconds
                            if current_time - last_update_time >= 0.1:
                                # Calculate speed
                                time_diff = current_time - last_update_time
                                bytes_diff = downloaded - last_downloaded
                                speed = bytes_diff / time_diff if time_diff > 0 else 0
                                
                                # Calculate ETA
                                if speed > 0 and total_size:
                                    remaining = total_size - downloaded
                                    eta = remaining / speed
                                else:
                                    eta = 0
                                
                                # Format values
                                if total_size:
                                    percent = (downloaded / total_size) * 100
                                    downloaded_mb = downloaded / 1024 / 1024
                                    total_mb = total_size / 1024 / 1024
                                    
                                    # Create progress bar
                                    bar_length = 30
                                    filled = int(bar_length * percent / 100)
                                    bar = '━' * filled + '░' * (bar_length - filled)
                                    
                                    # Format speed
                                    if speed > 1024 * 1024:
                                        speed_str = f"{speed/1024/1024:.1f}MB/s"
                                    else:
                                        speed_str = f"{speed/1024:.0f}KB/s"
                                    
                                    # Format ETA
                                    if eta > 3600:
                                        eta_str = f"{int(eta//3600)}h{int((eta%3600)//60):02d}m"
                                    elif eta > 60:
                                        eta_str = f"{int(eta//60)}m{int(eta%60):02d}s"
                                    else:
                                        eta_str = f"{int(eta):2d}s"
                                    
                                    # Print progress line with ANSI colors
                                    progress_line = (
                                        f"\r\033[1;33m▼\033[0m "
                                        f"\033[1;32m{percent:5.1f}%\033[0m "
                                        f"[\033[36m{bar[:filled]}\033[0m"
                                        f"\033[2;37m{bar[filled:]}\033[0m] "
                                        f"\033[1;36m{downloaded_mb:6.1f}/{total_mb:6.1f}MB\033[0m "
                                        f"| \033[1;35m{speed_str:>10}\033[0m "
                                        f"| ETA: \033[1;34m{eta_str:>8}\033[0m"
                                    )
                                    print(progress_line, end="", flush=True)
                                
                                last_update_time = current_time
                                last_downloaded = downloaded
                
                # Clear progress line
                print("\r" + " " * 100, end="\r", flush=True)
            
            self._print_rich(f"[green]✓ Successfully downloaded: {title}[/green]")
            self._print_rich(f"[green]📁 Saved to: {filepath}[/green]")
            
            return {
                'title': title,
                'filepath': str(filepath),
                'success': True
            }
            
        except Exception as e:
            self._print_rich(f"[red]✗ Direct download failed: {str(e)}[/red]")
            return None
    
    def search_and_download(self, url: str, interactive: bool = True) -> Optional[Dict[str, Any]]:
        if not self.is_hqporner_url(url):
            self._print_rich(f"[red]Error: Not a valid HQPorner URL[/red]")
            return None
        
        return self.download(url, quality="best", interactive=interactive)
