#!/usr/bin/env python3
"""
LinkedIn Handler Module - Direct Post URLs Only
Handles downloading videos and images from LinkedIn direct post URLs.
Profile scraping is not supported.
"""

import os
import re
import json
import time
import random
import warnings
from pathlib import Path
from typing import Optional, Dict, Any, List
from urllib.parse import urlparse
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
    import yt_dlp
    YTDLP_AVAILABLE = True
except ImportError:
    YTDLP_AVAILABLE = False

try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    import undetected_chromedriver as uc
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.progress import (
        Progress, 
        SpinnerColumn, 
        BarColumn, 
        TextColumn,
        DownloadColumn,
        TransferSpeedColumn,
        TimeRemainingColumn
    )
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

try:
    import cloudscraper
    CLOUDSCRAPER_AVAILABLE = True
except ImportError:
    CLOUDSCRAPER_AVAILABLE = False

from utils.utils import sanitize_filename
from utils.ui_components import Icons, Messages


class LinkedInHandler:
    """Handles LinkedIn video and image downloads from direct post URLs only"""
    
    SUPPORTED_DOMAINS = [
        'linkedin.com',
        'www.linkedin.com',
    ]
    
    USER_AGENTS = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
    ]
    
    def __init__(self, downloader):
        """Initialize LinkedIn handler
        
        Args:
            downloader: Reference to main downloader instance
        """
        self.downloader = downloader
        self.console = Console() if RICH_AVAILABLE else None
        self.session = self._create_session()
        self.driver = None
        self.use_selenium = False  # Only use selenium as last resort
        
    def _create_session(self):
        """Create a requests session with retry strategy"""
        if not REQUESTS_AVAILABLE:
            return None
            
        session = cloudscraper.create_scraper() if CLOUDSCRAPER_AVAILABLE else requests.Session()
        
        # Configure retry strategy
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        return session
    
    def _get_headers(self):
        """Get randomized headers for requests"""
        return {
            'User-Agent': random.choice(self.USER_AGENTS),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0',
        }
    
    def is_supported(self, url: str) -> bool:
        """Check if URL is supported by this handler
        
        Args:
            url: URL to check
            
        Returns:
            True if supported, False otherwise
        """
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            
            # Remove www. prefix for comparison
            domain = domain.replace('www.', '')
            
            # Check if it's a LinkedIn domain and a direct post URL
            return any(d.replace('www.', '') in domain for d in self.SUPPORTED_DOMAINS) and self.is_direct_post_url(url)
        except:
            return False
    
    def is_direct_post_url(self, url: str) -> bool:
        """Check if URL is a direct LinkedIn post URL
        
        Args:
            url: LinkedIn URL
            
        Returns:
            True if direct post URL, False otherwise
        """
        post_patterns = [
            r'/posts/',
            r'/feed/update/',
            r'linkedin\.com/.*activity-\d+',
        ]
        
        for pattern in post_patterns:
            if re.search(pattern, url):
                return True
        
        return False
    
    def _try_ytdlp_download(self, url: str, output_dir: Path) -> Dict[str, Any]:
        """Try to download using yt-dlp with Rich progress bar
        
        Args:
            url: LinkedIn post URL
            output_dir: Output directory
            
        Returns:
            Dictionary with success status and info
        """
        if not YTDLP_AVAILABLE:
            return {'success': False, 'error': 'yt-dlp not available'}
        
        try:
            if self.console:
                self.console.print("[cyan]Trying yt-dlp method...[/cyan]")
            
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Progress tracking variables
            progress_bar = None
            task_id = None
            
            def progress_hook(d):
                nonlocal progress_bar, task_id
                
                if d['status'] == 'downloading':
                    if self.console and RICH_AVAILABLE:
                        # Initialize progress bar on first call
                        if progress_bar is None:
                            # Get filename and display it first
                            filename = d.get('filename', 'video').split('/')[-1]
                            if len(filename) > 60:
                                filename = filename[:57] + '...'
                            
                            self.console.print(f"[cyan]📥 {filename}[/cyan]")
                            
                            progress_bar = Progress(
                                SpinnerColumn(),
                                BarColumn(bar_width=40),
                                DownloadColumn(),
                                TransferSpeedColumn(),
                                TimeRemainingColumn(),
                                console=self.console
                            )
                            progress_bar.start()
                            
                            total = d.get('total_bytes') or d.get('total_bytes_estimate', 0)
                            
                            task_id = progress_bar.add_task(
                                "",
                                total=total
                            )
                        
                        # Update progress
                        downloaded = d.get('downloaded_bytes', 0)
                        if task_id is not None:
                            progress_bar.update(task_id, completed=downloaded)
                
                elif d['status'] == 'finished':
                    if progress_bar is not None:
                        progress_bar.stop()
                        if self.console:
                            filename = d.get('filename', 'video').split('/')[-1]
                            self.console.print(f"[green]✓ Download completed: {filename}[/green]")
            
            ydl_opts = {
                'format': 'best',
                'outtmpl': str(output_dir / '%(title)s.%(ext)s'),
                'quiet': True,
                'no_warnings': True,
                'ignoreerrors': False,
                'progress_hooks': [progress_hook],
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                
                # Ensure progress bar is stopped
                if progress_bar is not None:
                    progress_bar.stop()
                
                if info:
                    return {
                        'success': True,
                        'title': info.get('title', 'Unknown'),
                        'filename': ydl.prepare_filename(info)
                    }
        
        except Exception as e:
            if self.console:
                self.console.print(f"[yellow]yt-dlp method failed: {e}[/yellow]")
            return {'success': False, 'error': str(e)}
        
        return {'success': False}
    
    def _try_api_method(self, url: str) -> Dict[str, List[str]]:
        """Try to extract media using API/requests method
        
        Args:
            url: LinkedIn post URL
            
        Returns:
            Dictionary with 'videos' and 'images' lists
        """
        media = {'videos': [], 'images': []}
        
        try:
            if self.console:
                self.console.print("[cyan]Extracting media from post URL...[/cyan]")
            
            # Standard requests method for direct post URLs
            headers = self._get_headers()
            headers.update({
                'Referer': 'https://www.linkedin.com/',
                'Origin': 'https://www.linkedin.com',
            })
            
            response = self.session.get(
                url,
                headers=headers,
                timeout=15,
                allow_redirects=True
            )
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Extract videos
                video_tags = soup.find_all('video')
                for video in video_tags:
                    src = video.get('src')
                    if src and src not in media['videos']:
                        media['videos'].append(src)
                    
                    # Check for source tags
                    sources = video.find_all('source')
                    for source in sources:
                        src = source.get('src')
                        if src and src not in media['videos']:
                            media['videos'].append(src)
                
                # Look for video URLs in JavaScript/scripts
                scripts = soup.find_all('script')
                for script in scripts:
                    if script.string:
                        # Find .mp4 URLs
                        video_urls = re.findall(r'https?://[^\s\"\'<>]+\.mp4[^\s\"\'<>]*', script.string)
                        for vid_url in video_urls:
                            if vid_url not in media['videos']:
                                media['videos'].append(vid_url)
                        
                        # Find .m3u8 streams
                        m3u8_urls = re.findall(r'https?://[^\s\"\'<>]+\.m3u8[^\s\"\'<>]*', script.string)
                        for m3u8_url in m3u8_urls:
                            if m3u8_url not in media['videos']:
                                media['videos'].append(m3u8_url)
                
                # Extract images
                img_tags = soup.find_all('img', class_=re.compile(r'media|post|content'))
                for img in img_tags:
                    src = img.get('src')
                    # Filter out small icons and profile pictures
                    if src and 'media' in src and not any(x in src for x in ['icon', 'logo', 'emoji', 'avatar']):
                        if src not in media['images']:
                            media['images'].append(src)
                
                # Look for JSON-LD structured data
                scripts = soup.find_all('script', type='application/ld+json')
                for script in scripts:
                    try:
                        if script.string:
                            data = json.loads(script.string)
                            if isinstance(data, dict):
                                # Check for video content
                                if 'video' in data:
                                    video_data = data['video']
                                    if isinstance(video_data, dict) and 'contentUrl' in video_data:
                                        url = video_data['contentUrl']
                                        if url not in media['videos']:
                                            media['videos'].append(url)
                                
                                # Check for image content
                                if 'image' in data:
                                    img_data = data['image']
                                    if isinstance(img_data, str) and img_data not in media['images']:
                                        media['images'].append(img_data)
                                    elif isinstance(img_data, list):
                                        for img_url in img_data:
                                            if isinstance(img_url, str) and img_url not in media['images']:
                                                media['images'].append(img_url)
                    except Exception as parse_error:
                        continue
                
                # Look for Open Graph meta tags
                og_video = soup.find('meta', property='og:video')
                if og_video and og_video.get('content'):
                    video_url = og_video.get('content')
                    if video_url not in media['videos']:
                        media['videos'].append(video_url)
                
                og_image = soup.find('meta', property='og:image')
                if og_image and og_image.get('content'):
                    img_url = og_image.get('content')
                    if img_url not in media['images']:
                        media['images'].append(img_url)
                
                if media['videos'] or media['images']:
                    if self.console:
                        self.console.print(f"[green]✓ Found {len(media['videos'])} videos and {len(media['images'])} images[/green]")
                elif self.console:
                    self.console.print(f"[yellow]No videos found - LinkedIn may require authentication (status: {response.status_code})[/yellow]")
        
        except Exception as e:
            if self.console:
                self.console.print(f"[yellow]Extraction failed: {e}[/yellow]")
        
        return media
    
    def download_media(self, url: str, output_path: Path, media_type: str = 'video') -> bool:
        """Download a media file
        
        Args:
            url: Media URL
            output_path: Path to save the file
            media_type: Type of media ('video' or 'image')
            
        Returns:
            True if successful, False otherwise
        """
        try:
            headers = self._get_headers()
            headers['Referer'] = 'https://www.linkedin.com/'
            
            response = self.session.get(url, headers=headers, stream=True, timeout=30)
            
            if response.status_code == 200:
                output_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Get total size for progress bar
                total_size = int(response.headers.get('content-length', 0))
                
                with open(output_path, 'wb') as f:
                    if self.console and RICH_AVAILABLE:
                        with Progress(
                            SpinnerColumn(),
                            TextColumn("[bold blue]{task.description}"),
                            BarColumn(bar_width=40),
                            DownloadColumn(),
                            TransferSpeedColumn(),
                            TimeRemainingColumn(),
                            console=self.console
                        ) as progress:
                            task = progress.add_task(
                                f"[cyan]Downloading {media_type}: {output_path.name}",
                                total=total_size if total_size > 0 else None
                            )
                            
                            downloaded = 0
                            for chunk in response.iter_content(chunk_size=8192):
                                if chunk:
                                    f.write(chunk)
                                    downloaded += len(chunk)
                                    progress.update(task, advance=len(chunk))
                                    downloaded += len(chunk)
                                    progress.update(task, advance=len(chunk))
                    else:
                        # Fallback without progress bar
                        if self.console:
                            self.console.print(f"[cyan]Downloading {media_type}: {output_path.name}...[/cyan]")
                        for chunk in response.iter_content(chunk_size=8192):
                            if chunk:
                                f.write(chunk)
                
                if self.console:
                    size_mb = output_path.stat().st_size / (1024 * 1024)
                    self.console.print(f"[green]✓ Saved {media_type}: {output_path.name} ({size_mb:.2f} MB)[/green]")
                
                return True
            else:
                if self.console:
                    self.console.print(f"[red]Failed to download {media_type}: HTTP {response.status_code}[/red]")
                return False
        
        except Exception as e:
            if self.console:
                self.console.print(f"[red]Error downloading {media_type}: {e}[/red]")
            return False
    
    def download(self, url: str, output_dir: Path = None) -> bool:
        """Main download method for direct LinkedIn post URLs
        
        Args:
            url: LinkedIn post URL (direct post link only)
            output_dir: Directory to save downloads
            
        Returns:
            True if successful, False otherwise
        """
        if not output_dir:
            output_dir = Path.cwd() / 'downloads' / 'linkedin'
        
        try:
            # Validate that it's a direct post URL
            if not self.is_direct_post_url(url):
                if self.console:
                    self.console.print("[red]Error: Only direct LinkedIn post URLs are supported[/red]")
                    self.console.print("[yellow]Please provide a direct post URL like:[/yellow]")
                    self.console.print("[yellow]  https://www.linkedin.com/posts/username_activity-123456...[/yellow]")
                    self.console.print("[yellow]  https://www.linkedin.com/feed/update/urn:li:activity:123456...[/yellow]")
                    self.console.print("[dim]Profile URLs and username-based downloads are not supported[/dim]")
                return False
            
            if self.console:
                self.console.print("[cyan]Downloading from LinkedIn post...[/cyan]")
            
            # Method 1: Try yt-dlp first (best for single posts)
            if YTDLP_AVAILABLE:
                result = self._try_ytdlp_download(url, output_dir)
                if result['success']:
                    if self.console:
                        self.console.print("[green]✓ Successfully downloaded using yt-dlp[/green]")
                    return True
            
            # Method 2: Try API/requests method
            media = self._try_api_method(url)
            
            if media['videos'] or media['images']:
                # Download the extracted media
                post_id = url.split('/')[-1].split('-')[-1] if '/' in url else 'post'
                post_dir = output_dir / f"post_{post_id}"
                post_dir.mkdir(parents=True, exist_ok=True)
                
                stats = {'videos': 0, 'images': 0, 'failed': 0}
                
                # Download videos
                for idx, video_url in enumerate(media['videos'], 1):
                    filename = f"video_{idx}.mp4"
                    output_path = post_dir / filename
                    if self.download_media(video_url, output_path, 'video'):
                        stats['videos'] += 1
                    else:
                        stats['failed'] += 1
                    time.sleep(random.uniform(0.5, 1.5))
                
                # Download images
                for idx, img_url in enumerate(media['images'], 1):
                    ext = 'jpg'
                    if img_url:
                        url_ext = img_url.split('.')[-1].split('?')[0][:4].lower()
                        if url_ext in ['jpg', 'jpeg', 'png', 'gif', 'webp']:
                            ext = url_ext
                    
                    filename = f"image_{idx}.{ext}"
                    output_path = post_dir / filename
                    if self.download_media(img_url, output_path, 'image'):
                        stats['images'] += 1
                    else:
                        stats['failed'] += 1
                    time.sleep(random.uniform(0.5, 1.5))
                
                # Display summary
                if self.console:
                    self.console.print(Panel.fit(
                        f"[bold green]Download Complete![/bold green]\n"
                        f"Videos: {stats['videos']}\n"
                        f"Images: {stats['images']}\n"
                        f"Failed: {stats['failed']}\n"
                        f"Location: {post_dir}",
                        border_style="green"
                    ))
                
                return stats['videos'] > 0 or stats['images'] > 0
            else:
                if self.console:
                    self.console.print("[yellow]No media found in post[/yellow]")
                    self.console.print("[yellow]Tips:[/yellow]")
                    self.console.print("[yellow]  • LinkedIn may require authentication for some posts[/yellow]")
                    self.console.print("[yellow]  • Try using yt-dlp directly with --cookies-from-browser chrome[/yellow]")
                    self.console.print("[yellow]  • The post may not contain any video or image content[/yellow]")
                return False
        
        except Exception as e:
            if self.console:
                self.console.print(f"[red]Error downloading: {e}[/red]")
            return False
    
    def _close_driver(self):
        """Close Selenium driver if active"""
        if self.driver:
            try:
                self.driver.quit()
                self.driver = None
            except:
                pass
    
    def __del__(self):
        """Cleanup when handler is destroyed"""
        self._close_driver()
