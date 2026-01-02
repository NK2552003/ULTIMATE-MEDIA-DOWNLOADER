#!/usr/bin/env python3
"""
Pinterest Handler Module
Handles downloading images and videos from Pinterest pins, boards, and user profiles.
Supports username-based bulk downloads with ZIP creation.
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
from urllib.parse import urlparse, urljoin, quote
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
    from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

try:
    import cloudscraper
    CLOUDSCRAPER_AVAILABLE = True
except ImportError:
    CLOUDSCRAPER_AVAILABLE = False

try:
    from pinterest_dl import Pinterest
    PINTEREST_DL_AVAILABLE = True
except ImportError:
    PINTEREST_DL_AVAILABLE = False

try:
    import gallery_dl
    GALLERY_DL_AVAILABLE = True
except ImportError:
    GALLERY_DL_AVAILABLE = False

from utils.utils import sanitize_filename
from utils.ui_components import Icons, Messages


class PinterestHandler:
    """Handles Pinterest image and video downloads"""
    
    SUPPORTED_DOMAINS = [
        'pinterest.com',
        'www.pinterest.com',
        'pin.it',
        'pinterest.co.uk',
        'pinterest.ca',
        'pinterest.de',
        'pinterest.fr',
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
        'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1',
    ]
    
    def __init__(self, downloader):
        """Initialize Pinterest handler
        
        Args:
            downloader: Reference to main downloader instance
        """
        self.downloader = downloader
        self.console = Console() if RICH_AVAILABLE else None
        self.session = self._create_session()
        self.driver = None
        
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
    
    def _get_random_proxy(self):
        """Get a random proxy from the list"""
        if self.PROXY_LIST:
            return random.choice(self.PROXY_LIST)
        return None
    
    def _get_headers(self):
        """Get randomized headers"""
        return {
            'User-Agent': random.choice(self.USER_AGENTS),
            'Accept': 'application/json, text/javascript, */*, q=0.01',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'X-Requested-With': 'XMLHttpRequest',
            'X-APP-VERSION': 'cb1841c',
            'X-Pinterest-AppState': 'active',
        }
    
    def _init_driver(self):
        """Initialize undetected Chrome driver"""
        if not SELENIUM_AVAILABLE:
            return None
            
        try:
            options = uc.ChromeOptions()
            options.add_argument('--headless')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_argument(f'user-agent={random.choice(self.USER_AGENTS)}')
            
            # Add proxy if available
            proxy = self._get_random_proxy()
            if proxy:
                options.add_argument(f'--proxy-server={proxy}')
            
            self.driver = uc.Chrome(options=options)
            return self.driver
        except OSError as e:
            if 'Bad CPU type' in str(e):
                if self.console:
                    self.console.print(f"[yellow]Browser automation not available on this system (CPU architecture incompatibility)[/yellow]")
                    self.console.print(f"[yellow]Tip: Use yt-dlp for Pinterest downloads: pip install yt-dlp[/yellow]")
            else:
                if self.console:
                    self.console.print(f"[yellow]Warning: Could not initialize browser: {e}[/yellow]")
            return None
        except Exception as e:
            if self.console:
                self.console.print(f"[yellow]Warning: Could not initialize browser: {e}[/yellow]")
            return None
    
    def _close_driver(self):
        """Close the browser driver"""
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass
    
    def _try_gallery_dl(self, url: str, output_dir: Path) -> bool:
        """Try to download using gallery-dl external library
        
        Args:
            url: Pinterest profile or board URL
            output_dir: Output directory
            
        Returns:
            True if successful, False otherwise
        """
        if not GALLERY_DL_AVAILABLE:
            return False
        
        try:
            if self.console:
                self.console.print("[cyan]Downloading with gallery-dl...[/cyan]")
            
            import subprocess
            
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Use gallery-dl command line tool with high quality settings and verbose output
            cmd = [
                'gallery-dl',
                '--dest', str(output_dir),
                '--no-part',
                '--no-skip',
                '--verbose',
                '--option', 'image-range=1',
                '--option', 'image-filter=width >= 1000',  # High quality images only
                url
            ]
            
            # Don't write metadata to avoid .json files
            # High quality is default for gallery-dl
            
            # Run with real-time output
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            downloaded_count = 0
            error_count = 0
            
            if self.console and RICH_AVAILABLE:
                from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
                
                with Progress(
                    SpinnerColumn(),
                    TextColumn("[bold blue]{task.description}"),
                    BarColumn(bar_width=40),
                    console=self.console,
                    transient=False
                ) as progress:
                    task = progress.add_task("[cyan]Downloading pins...", total=None)
                    
                    # Stream output line by line
                    if process.stdout:
                        for line in process.stdout:
                            line = line.strip()
                            if line:
                                # Parse gallery-dl output to show file names
                                # gallery-dl outputs file paths when downloading
                                if any(ext in line.lower() for ext in ['.jpg', '.png', '.gif', '.mp4', '.webm', '.jpeg']):
                                    # Extract filename from path
                                    file_name = line.split('/')[-1] if '/' in line else line.split('\\')[-1] if '\\' in line else line
                                    # Clean up the filename
                                    if file_name and any(ext in file_name.lower() for ext in ['.jpg', '.png', '.gif', '.mp4', '.webm', '.jpeg']):
                                        downloaded_count += 1
                                        progress.update(task, description=f"[cyan]Downloaded {downloaded_count} files")
                                        self.console.print(f"[green]📥 [{downloaded_count}] {file_name[:80]}[/green]")
                                elif 'error' in line.lower() or 'failed' in line.lower():
                                    error_count += 1
                                    # Don't show SSL errors as they're too verbose
                                    if 'ssl' not in line.lower():
                                        self.console.print(f"[yellow]⚠  {line[:150]}[/yellow]")
            else:
                # Fallback without rich progress
                if process.stdout:
                    for line in process.stdout:
                        line = line.strip()
                        if line and any(ext in line.lower() for ext in ['.jpg', '.png', '.gif', '.mp4', '.webm', '.jpeg']):
                            file_name = line.split('/')[-1] if '/' in line else line.split('\\')[-1] if '\\' in line else line
                            if file_name:
                                downloaded_count += 1
                                if self.console:
                                    self.console.print(f"[green]📥 [{downloaded_count}] {file_name[:80]}[/green]")
            
            # Wait for process to complete
            return_code = process.wait(timeout=300)
            
            if downloaded_count > 0:
                if self.console:
                    self.console.print(f"[green]✓ Downloaded {downloaded_count} files using gallery-dl[/green]")
                return True
            elif return_code == 0:
                if self.console:
                    self.console.print("[green]✓ gallery-dl completed[/green]")
                return True
            
        except FileNotFoundError:
            if self.console:
                self.console.print("[dim]gallery-dl command not found. Install: pip install gallery-dl[/dim]")
        except subprocess.TimeoutExpired:
            if self.console:
                self.console.print("[yellow]gallery-dl timeout[/yellow]")
        except Exception as e:
            if self.console:
                self.console.print(f"[dim]gallery-dl failed: {str(e)[:100]}[/dim]")
        
        return False
    
    def _try_pinterest_dl(self, url: str, output_dir: Path) -> bool:
        """Try to download using pinterest-dl external library
        
        Args:
            url: Pinterest URL
            output_dir: Output directory
            
        Returns:
            True if successful, False otherwise
        """
        if not PINTEREST_DL_AVAILABLE:
            return False
        
        try:
            if self.console:
                self.console.print("[cyan]Trying pinterest-dl library...[/cyan]")
            
            import subprocess
            
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Use pinterest-dl command
            cmd = [
                'pinterest-dl',
                '-d', str(output_dir),
                url
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if result.returncode == 0:
                if self.console:
                    self.console.print("[green]✓ Successfully downloaded using pinterest-dl[/green]")
                return True
            
        except FileNotFoundError:
            if self.console:
                self.console.print("[dim]pinterest-dl command not found. Install: pip install pinterest-dl[/dim]")
        except subprocess.TimeoutExpired:
            if self.console:
                self.console.print("[yellow]pinterest-dl timeout[/yellow]")
        except Exception as e:
            if self.console:
                self.console.print(f"[dim]pinterest-dl failed: {str(e)[:100]}[/dim]")
        
        return False
    
    def _try_ytdlp_profile_download(self, url: str, output_dir: Path, max_downloads: int = 100) -> bool:
        """Try to download Pinterest profile/board using yt-dlp
        
        Args:
            url: Pinterest profile or board URL
            output_dir: Output directory
            max_downloads: Maximum number of items to download
            
        Returns:
            True if successful, False otherwise
        """
        try:
            import yt_dlp
            
            if self.console:
                self.console.print("[cyan]Trying yt-dlp for profile download...[/cyan]")
            
            output_dir.mkdir(parents=True, exist_ok=True)
            
            ydl_opts = {
                'format': 'best',
                'outtmpl': str(output_dir / '%(title)s.%(ext)s'),
                'quiet': True,
                'no_warnings': True,
                'ignoreerrors': True,
                'playlistend': max_downloads,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                return info is not None
                
        except ImportError:
            if self.console:
                self.console.print("[yellow]yt-dlp not available. Install with: pip install yt-dlp[/yellow]")
            return False
        except Exception as e:
            if self.console:
                self.console.print(f"[yellow]yt-dlp method failed: {e}[/yellow]")
            return False
            self.driver = None
    
    def is_supported_url(self, url: str) -> bool:
        """Check if URL is from Pinterest
        
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
        """Extract Pinterest username from URL
        
        Args:
            url: Pinterest profile or board URL
            
        Returns:
            Username if found, None otherwise
        """
        patterns = [
            r'pinterest\.[^/]+/([^/\?]+)/?$',
            r'pinterest\.[^/]+/([^/\?]+)/(?:_created|_saved|boards)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                username = match.group(1)
                # Filter out non-username paths
                if username not in ['pin', 'search', 'explore', 'today', 'ideas', 'shopping']:
                    return username
        return None
    
    def extract_board_name(self, url: str) -> Optional[str]:
        """Extract board name from URL
        
        Args:
            url: Pinterest board URL
            
        Returns:
            Board name if found, None otherwise
        """
        match = re.search(r'pinterest\.[^/]+/[^/]+/([^/\?]+)', url)
        if match:
            board_name = match.group(1)
            if board_name not in ['_created', '_saved', 'pins']:
                return board_name
        return None
    
    def get_pin_data(self, pin_url: str) -> Optional[Dict]:
        """Get pin data including media URLs
        
        Args:
            pin_url: URL of the pin
            
        Returns:
            Dictionary with pin data or None
        """
        try:
            # Extract pin ID from URL
            pin_id = re.search(r'/pin/(\d+)', pin_url)
            if not pin_id:
                return None
            pin_id = pin_id.group(1)
            
            # Use Pinterest API endpoint
            api_url = f"https://www.pinterest.com/resource/PinResource/get/?source_url=/pin/{pin_id}/&data=%7B%22options%22%3A%7B%22field_set_key%22%3A%22detailed%22%2C%22id%22%3A%22{pin_id}%22%7D%7D"
            
            proxy = self._get_random_proxy()
            proxies = {'http': proxy, 'https': proxy} if proxy else None
            
            response = self.session.get(
                api_url,
                headers=self._get_headers(),
                proxies=proxies,
                timeout=15
            )
            response.raise_for_status()
            
            data = response.json()
            
            if 'resource_response' in data and 'data' in data['resource_response']:
                pin_data = data['resource_response']['data']
                
                result = {
                    'id': pin_id,
                    'title': pin_data.get('title', ''),
                    'description': pin_data.get('description', ''),
                    'images': [],
                    'videos': [],
                }
                
                # Get image URLs
                if 'images' in pin_data:
                    # Try to get the highest quality image
                    if 'orig' in pin_data['images']:
                        result['images'].append(pin_data['images']['orig']['url'])
                    elif '736x' in pin_data['images']:
                        result['images'].append(pin_data['images']['736x']['url'])
                    elif 'originals' in pin_data['images']:
                        result['images'].append(pin_data['images']['originals']['url'])
                
                # Get video URLs
                if 'videos' in pin_data and 'video_list' in pin_data['videos']:
                    video_list = pin_data['videos']['video_list']
                    # Get the highest quality video
                    if 'V_HLSV4' in video_list:
                        result['videos'].append(video_list['V_HLSV4']['url'])
                    elif 'V_720P' in video_list:
                        result['videos'].append(video_list['V_720P']['url'])
                    elif video_list:
                        # Get first available video
                        result['videos'].append(list(video_list.values())[0]['url'])
                
                return result
            
            return None
            
        except Exception as e:
            if self.console:
                self.console.print(f"[yellow]Warning: Error getting pin data: {e}[/yellow]")
            return None
    
    def scrape_user_pins_webscraping(self, username: str, max_pins: int = 100) -> List[str]:
        """Scrape pin URLs from a user's profile using web scraping
        
        Args:
            username: Pinterest username
            max_pins: Maximum number of pins to scrape
            
        Returns:
            List of pin URLs
        """
        if not REQUESTS_AVAILABLE or not BS4_AVAILABLE:
            if self.console:
                self.console.print("[red]Required libraries not available. Install: pip install requests beautifulsoup4[/red]")
            return []
        
        pin_urls = []
        profile_url = f"https://www.pinterest.com/{username}/_created/"
        
        try:
            if self.console:
                self.console.print(f"[cyan]🔍 Advanced scraping of Pinterest profile: {username}[/cyan]")
            
            # Try multiple aggressive approaches to extract ALL pins
            
            # Method 1: Get initial page with aggressive anti-detection
            headers = self._get_headers()
            headers.update({
                'Referer': 'https://www.pinterest.com/',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
                'Cache-Control': 'no-cache',
                'Pragma': 'no-cache',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Upgrade-Insecure-Requests': '1',
            })
            
            if self.console:
                self.console.print("[dim]  → Fetching profile page with anti-bot bypass...[/dim]")
            
            # Try with cloudscraper if available for better anti-bot
            response = None
            for attempt in range(3):
                try:
                    response = self.session.get(profile_url, headers=headers, timeout=20)
                    if response.status_code == 200:
                        break
                    time.sleep(2)
                except Exception as e:
                    if attempt == 2:
                        raise e
                    time.sleep(2)
            
            if response and response.status_code == 200:
                html_content = response.text
                soup = BeautifulSoup(html_content, 'html.parser')
                
                # Check if we got actual content or just a redirect/login page
                if 'window.location' in html_content.lower() or 'redirect' in html_content.lower():
                    if self.console:
                        self.console.print("[yellow]  ⚠ Detected redirect - trying alternative method...[/yellow]")
                
                if self.console:
                    self.console.print("[dim]  → Extracting pins from HTML...[/dim]")
                
                # 1. Extract from all <a> tags with pin links
                links = soup.find_all('a', href=re.compile(r'/pin/\d+'))
                for link in links:
                    href = link.get('href')
                    if href:
                        pin_id = re.search(r'/pin/(\d+)', href)
                        if pin_id:
                            full_url = f"https://www.pinterest.com/pin/{pin_id.group(1)}/"
                            if full_url not in pin_urls:
                                pin_urls.append(full_url)
                
                # 2. Extract ALL pin IDs from raw HTML using multiple aggressive regex patterns
                patterns = [
                    r'"id"\s*:\s*"(\d{15,20})"',  # JSON id fields
                    r'href="[^"]*?/pin/(\d+)/',    # href attributes
                    r'/pin/(\d{15,20})/',           # Any pin URL patterns
                    r'"pin_id"\s*:\s*"(\d{15,20})"',  # pin_id fields
                    r'"pinId"\s*:\s*"(\d{15,20})"',   # pinId fields
                    r'"closeupId"\s*:\s*"(\d{15,20})"', # closeupId fields
                    r'data-pin-id="(\d{15,20})"',   # data attributes
                    r'pin-id-(\d{15,20})',          # class/id patterns
                    r'pin_id=(\d{15,20})',          # URL parameters
                    r'pin/(\d{15,20})[\?/"\']',     # Pin URLs in various contexts
                ]
                
                for pattern in patterns:
                    matches = re.findall(pattern, html_content)
                    for pin_id in matches:
                        full_url = f"https://www.pinterest.com/pin/{pin_id}/"
                        if full_url not in pin_urls:
                            pin_urls.append(full_url)
                
                # 3. Extract from ALL script tags
                if self.console:
                    self.console.print("[dim]  → Parsing JavaScript data...[/dim]")
                
                all_scripts = soup.find_all('script')
                for script in all_scripts:
                    try:
                        if script.string:
                            script_content = script.string
                            
                            # Try to parse as JSON
                            try:
                                json_data = json.loads(script_content)
                                if isinstance(json_data, dict):
                                    pin_ids = self._extract_pin_ids_from_json(json_data)
                                    for pin_id in pin_ids:
                                        full_url = f"https://www.pinterest.com/pin/{pin_id}/"
                                        if full_url not in pin_urls:
                                            pin_urls.append(full_url)
                            except json.JSONDecodeError:
                                # Search for pin IDs in the script content with all patterns
                                for pattern in patterns:
                                    pin_ids_in_script = re.findall(pattern, script_content)
                                    for pin_id in pin_ids_in_script:
                                        full_url = f"https://www.pinterest.com/pin/{pin_id}/"
                                        if full_url not in pin_urls:
                                            pin_urls.append(full_url)
                    except Exception as e:
                        continue
                
                # 4. Extract from meta tags and data attributes
                meta_tags = soup.find_all('meta')
                for meta in meta_tags:
                    content = meta.get('content', '')
                    if content:
                        pin_ids_meta = re.findall(r'/pin/(\d{15,20})', content)
                        for pin_id in pin_ids_meta:
                            full_url = f"https://www.pinterest.com/pin/{pin_id}/"
                            if full_url not in pin_urls:
                                pin_urls.append(full_url)
                
                # 5. Try Pinterest API endpoints
                if self.console:
                    self.console.print(f"[dim]  → Found {len(pin_urls)} pins so far, trying API...[/dim]")
                
                api_pins = self._scrape_pins_via_api(username, max_pins)
                pin_urls.extend([p for p in api_pins if p not in pin_urls])
                
                # 6. Try Pinterest RSS/JSON feeds
                if len(pin_urls) < 10:  # Only try if we haven't found many pins yet
                    feed_pins = self._scrape_pins_via_feeds(username, max_pins)
                    pin_urls.extend([p for p in feed_pins if p not in pin_urls])
                
                # 7. Try alternative profile URLs
                if len(pin_urls) < 5:
                    if self.console:
                        self.console.print("[dim]  → Trying alternative URLs...[/dim]")
                    
                    alt_urls = [
                        f"https://www.pinterest.com/{username}/pins/",
                        f"https://www.pinterest.com/{username}/_saved/",
                    ]
                    
                    for alt_url in alt_urls:
                        try:
                            alt_response = self.session.get(alt_url, headers=headers, timeout=15)
                            if alt_response.status_code == 200:
                                for pattern in patterns:
                                    matches = re.findall(pattern, alt_response.text)
                                    for pin_id in matches:
                                        full_url = f"https://www.pinterest.com/pin/{pin_id}/"
                                        if full_url not in pin_urls:
                                            pin_urls.append(full_url)
                        except:
                            continue
            
            if self.console:
                if pin_urls:
                    self.console.print(f"[green]✓ Successfully extracted {len(pin_urls)} pins![/green]")
                else:
                    self.console.print("[red]✗ No pins found - Pinterest requires authentication[/red]")
                    self.console.print("[yellow]Pinterest blocks automated scraping of profiles without login[/yellow]")
                    self.console.print("[cyan]💡 Recommended solution:[/cyan]")
                    self.console.print("[cyan]   Use browser cookies to authenticate:[/cyan]")
                    self.console.print("[dim]   yt-dlp --cookies-from-browser chrome https://www.pinterest.com/{username}/[/dim]")
            
            return pin_urls[:max_pins]
            
        except Exception as e:
            if self.console:
                self.console.print(f"[red]Error scraping profile: {e}[/red]")
            return []
    
    def _extract_pin_ids_from_json(self, data: Any, pin_ids: set = None) -> List[str]:
        """Recursively extract pin IDs from JSON data
        
        Args:
            data: JSON data structure
            pin_ids: Set to collect unique pin IDs
            
        Returns:
            List of pin IDs
        """
        if pin_ids is None:
            pin_ids = set()
        
        if isinstance(data, dict):
            # Check if this is a pin object
            if 'id' in data and isinstance(data.get('id'), str) and data['id'].isdigit():
                if len(data['id']) > 10:  # Pinterest pin IDs are long numbers
                    pin_ids.add(data['id'])
            
            # Recurse into nested structures
            for value in data.values():
                self._extract_pin_ids_from_json(value, pin_ids)
        
        elif isinstance(data, list):
            for item in data:
                self._extract_pin_ids_from_json(item, pin_ids)
        
        return list(pin_ids)
    
    def _scrape_pins_via_api(self, username: str, max_pins: int) -> List[str]:
        """Try to scrape pins using Pinterest's internal API endpoints
        
        Args:
            username: Pinterest username
            max_pins: Maximum pins to retrieve
            
        Returns:
            List of pin URLs
        """
        pin_urls = []
        
        try:
            # Pinterest API endpoint (may require authentication)
            api_url = f"https://www.pinterest.com/resource/UserPinsResource/get/"
            
            params = {
                'source_url': f'/{username}/_created/',
                'data': json.dumps({
                    'options': {
                        'username': username,
                        'field_set_key': 'grid_item',
                        'is_own_profile_pins': False
                    }
                }),
            }
            
            headers = self._get_headers()
            headers['X-Requested-With'] = 'XMLHttpRequest'
            
            response = self.session.get(api_url, params=params, headers=headers, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                
                if 'resource_response' in data and 'data' in data['resource_response']:
                    pins = data['resource_response']['data']
                    if isinstance(pins, list):
                        for pin in pins:
                            if isinstance(pin, dict) and 'id' in pin:
                                pin_url = f"https://www.pinterest.com/pin/{pin['id']}/"
                                pin_urls.append(pin_url)
                                if len(pin_urls) >= max_pins:
                                    break
        
        except Exception as e:
            # Silently fail as this is a fallback method
            pass
        
        return pin_urls
    
    def _scrape_pins_via_feeds(self, username: str, max_pins: int) -> List[str]:
        """Try to scrape pins using Pinterest RSS/JSON feeds
        
        Args:
            username: Pinterest username
            max_pins: Maximum pins to retrieve
            
        Returns:
            List of pin URLs
        """
        pin_urls = []
        
        try:
            # Try RSS feed format
            rss_url = f"https://www.pinterest.com/{username}/feed.rss"
            
            headers = self._get_headers()
            headers['Accept'] = 'application/rss+xml, application/xml, text/xml'
            
            response = self.session.get(rss_url, headers=headers, timeout=15)
            
            if response.status_code == 200:
                # Parse RSS/XML content
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Look for pin links in RSS items
                items = soup.find_all('item')
                for item in items:
                    link = item.find('link')
                    if link and link.string:
                        pin_match = re.search(r'/pin/(\d{15,20})', link.string)
                        if pin_match:
                            pin_url = f"https://www.pinterest.com/pin/{pin_match.group(1)}/"
                            if pin_url not in pin_urls:
                                pin_urls.append(pin_url)
                                if len(pin_urls) >= max_pins:
                                    break
                
                # Also check for pins in GUID/description
                for item in items:
                    guid = item.find('guid')
                    if guid and guid.string:
                        pin_match = re.search(r'/pin/(\d{15,20})', guid.string)
                        if pin_match:
                            pin_url = f"https://www.pinterest.com/pin/{pin_match.group(1)}/"
                            if pin_url not in pin_urls:
                                pin_urls.append(pin_url)
        
        except Exception as e:
            # Silently fail as this is a fallback method
            pass
        
        return pin_urls
    
    def scrape_board_pins(self, username: str, board_name: str, max_pins: int = 100) -> List[str]:
        """Scrape pin URLs from a specific board
        
        Args:
            username: Pinterest username
            board_name: Name of the board
            max_pins: Maximum number of pins to scrape
            
        Returns:
            List of pin URLs
        """
        if not SELENIUM_AVAILABLE:
            return []
        
        pin_urls = []
        board_url = f"https://www.pinterest.com/{username}/{board_name}/"
        
        try:
            if not self.driver:
                self._init_driver()
            
            if not self.driver:
                return []
            
            if self.console:
                self.console.print(f"[cyan]Scraping pins from board: {board_name}[/cyan]")
            
            self.driver.get(board_url)
            time.sleep(5)
            
            # Similar scrolling logic as user pins
            last_height = self.driver.execute_script("return document.body.scrollHeight")
            scroll_attempts = 0
            max_scrolls = max_pins // 25
            
            while scroll_attempts < max_scrolls and len(pin_urls) < max_pins:
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)
                
                soup = BeautifulSoup(self.driver.page_source, 'html.parser')
                links = soup.find_all('a', href=re.compile(r'/pin/\d+'))
                
                for link in links:
                    href = link.get('href')
                    if href:
                        full_url = urljoin('https://www.pinterest.com', href.split('?')[0])
                        if full_url not in pin_urls:
                            pin_urls.append(full_url)
                            if len(pin_urls) >= max_pins:
                                break
                
                new_height = self.driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    break
                    
                last_height = new_height
                scroll_attempts += 1
            
            if self.console:
                self.console.print(f"[green]Found {len(pin_urls)} pins in board[/green]")
            
            return pin_urls[:max_pins]
            
        except Exception as e:
            if self.console:
                self.console.print(f"[red]Error scraping board: {e}[/red]")
            return []
    
    def _extract_pin_ids_from_json(self, data: Any, pin_ids: set = None) -> List[str]:
        """Recursively extract pin IDs from JSON data
        
        Args:
            data: JSON data structure
            pin_ids: Set to collect unique pin IDs
            
        Returns:
            List of pin IDs
        """
        if pin_ids is None:
            pin_ids = set()
        
        if isinstance(data, dict):
            # Check if this is a pin object
            if 'id' in data and isinstance(data.get('id'), str) and data['id'].isdigit():
                if len(data['id']) > 10:  # Pinterest pin IDs are long numbers
                    pin_ids.add(data['id'])
            
            # Recurse into nested structures
            for value in data.values():
                self._extract_pin_ids_from_json(value, pin_ids)
        
        elif isinstance(data, list):
            for item in data:
                self._extract_pin_ids_from_json(item, pin_ids)
        
        return list(pin_ids)
    
    def _scrape_pins_via_api(self, username: str, max_pins: int) -> List[str]:
        """Try to scrape pins using Pinterest's internal API endpoints
        
        Args:
            username: Pinterest username
            max_pins: Maximum pins to retrieve
            
        Returns:
            List of pin URLs
        """
        pin_urls = []
        
        try:
            # Pinterest API endpoint (may require authentication)
            api_url = f"https://www.pinterest.com/resource/UserPinsResource/get/"
            
            params = {
                'source_url': f'/{username}/_created/',
                'data': json.dumps({
                    'options': {
                        'username': username,
                        'field_set_key': 'grid_item',
                        'is_own_profile_pins': False
                    }
                }),
            }
            
            headers = self._get_headers()
            headers['X-Requested-With'] = 'XMLHttpRequest'
            
            response = self.session.get(api_url, params=params, headers=headers, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                
                if 'resource_response' in data and 'data' in data['resource_response']:
                    pins = data['resource_response']['data']
                    if isinstance(pins, list):
                        for pin in pins:
                            if isinstance(pin, dict) and 'id' in pin:
                                pin_url = f"https://www.pinterest.com/pin/{pin['id']}/"
                                pin_urls.append(pin_url)
                                if len(pin_urls) >= max_pins:
                                    break
        
        except Exception as e:
            # Silently fail as this is a fallback method
            pass
        
        return pin_urls
    
    def download_media(self, url: str, output_path: Path, media_type: str = 'image') -> bool:
        """Download a single media file with progress bar
        
        Args:
            url: URL of the media
            output_path: Path to save the file
            media_type: 'video' or 'image'
            
        Returns:
            True if successful, False otherwise
        """
        try:
            proxy = self._get_random_proxy()
            proxies = {'http': proxy, 'https': proxy} if proxy else None
            
            # Add quality parameters for videos
            headers = self._get_headers()
            if media_type == 'video':
                headers['Accept'] = 'video/mp4,video/*;q=0.9,*/*;q=0.8'
            
            response = self.session.get(
                url,
                headers=headers,
                proxies=proxies,
                stream=True,
                timeout=30
            )
            response.raise_for_status()
            
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Get total size for progress bar
            total_size = int(response.headers.get('content-length', 0))
            
            # Display file name and progress
            if self.console and RICH_AVAILABLE:
                from rich.progress import (
                    Progress,
                    SpinnerColumn,
                    BarColumn,
                    DownloadColumn,
                    TransferSpeedColumn,
                    TimeRemainingColumn,
                    TextColumn
                )
                
                with Progress(
                    SpinnerColumn(),
                    TextColumn("[bold blue]{task.description}"),
                    BarColumn(bar_width=30),
                    DownloadColumn(),
                    TransferSpeedColumn(),
                    TimeRemainingColumn(),
                    console=self.console
                ) as progress:
                    task = progress.add_task(
                        f"📥 {output_path.name}",
                        total=total_size if total_size > 0 else None
                    )
                    
                    with open(output_path, 'wb') as f:
                        downloaded = 0
                        for chunk in response.iter_content(chunk_size=8192):
                            if chunk:
                                f.write(chunk)
                                downloaded += len(chunk)
                                progress.update(task, advance=len(chunk))
                
                # Show completion message
                size_mb = output_path.stat().st_size / (1024 * 1024)
                self.console.print(f"[green]✓ {output_path.name} ({size_mb:.2f} MB)[/green]")
            else:
                # Fallback without progress bar
                with open(output_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                
                if self.console:
                    self.console.print(f"[green]✓ Downloaded: {output_path.name}[/green]")
            
            return True
            
        except Exception as e:
            if self.console:
                self.console.print(f"[red]✗ Failed to download {url}: {e}[/red]")
            return False
    
    def download_pin(self, pin_url: str, output_dir: Path) -> Dict[str, Any]:
        """Download media from a single pin
        
        Args:
            pin_url: URL of the pin
            output_dir: Directory to save media
            
        Returns:
            Dictionary with download statistics
        """
        stats = {'images': 0, 'videos': 0, 'failed': 0}
        
        try:
            # Get pin data
            pin_data = self.get_pin_data(pin_url)
            
            if not pin_data:
                if self.console:
                    self.console.print(f"[yellow]Could not extract pin data[/yellow]")
                stats['failed'] += 1
                return stats
            
            pin_id = pin_data['id']
            pin_dir = output_dir / f"pin_{pin_id}"
            pin_dir.mkdir(parents=True, exist_ok=True)
            
            # Download images
            for idx, img_url in enumerate(pin_data['images'], 1):
                ext = img_url.split('.')[-1].split('?')[0][:4]
                if ext not in ['jpg', 'jpeg', 'png', 'webp']:
                    ext = 'jpg'
                
                filename = f"image_{idx}.{ext}"
                output_path = pin_dir / filename
                
                if self.download_media(img_url, output_path, 'image'):
                    stats['images'] += 1
                else:
                    stats['failed'] += 1
                
                time.sleep(random.uniform(0.5, 1.5))
            
            # Download videos
            for idx, video_url in enumerate(pin_data['videos'], 1):
                filename = f"video_{idx}.mp4"
                output_path = pin_dir / filename
                
                if self.download_media(video_url, output_path, 'video'):
                    stats['videos'] += 1
                else:
                    stats['failed'] += 1
                
                time.sleep(random.uniform(0.5, 1.5))
            
            return stats
            
        except Exception as e:
            if self.console:
                self.console.print(f"[red]Error downloading pin: {e}[/red]")
            stats['failed'] += 1
            return stats
    
    def download_by_username(self, username: str, output_dir: Path, max_pins: int = 100, create_zip: bool = True) -> bool:
        """Download all media from a Pinterest user's pins
        
        Args:
            username: Pinterest username
            output_dir: Directory to save downloads
            max_pins: Maximum number of pins to download
            create_zip: Whether to create a ZIP archive
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Ask user how many pins they want to download
            if self.console:
                self.console.print("\n[cyan]📌 How many pins do you want to download?[/cyan]")
                self.console.print(f"[dim]   Press Enter for default ({max_pins}) or type a number:[/dim]")
                
                try:
                    user_input = input("   → ").strip()
                    if user_input:
                        requested_pins = int(user_input)
                        if requested_pins > 0:
                            max_pins = requested_pins
                        else:
                            self.console.print("[yellow]Invalid number, using default[/yellow]")
                except (ValueError, KeyboardInterrupt):
                    self.console.print("[yellow]Using default value[/yellow]")
            
            if self.console:
                self.console.print(Panel.fit(
                    f"[bold cyan]Downloading Pinterest Content[/bold cyan]\n"
                    f"Username: {username}\n"
                    f"Max Pins: {max_pins}",
                    border_style="cyan"
                ))
            
            # Create output directory
            user_dir = output_dir / f"pinterest_{username}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            user_dir.mkdir(parents=True, exist_ok=True)
            
            profile_url = f"https://www.pinterest.com/{username}/"
            
            # Method 1: Try gallery-dl (most reliable external library)
            if GALLERY_DL_AVAILABLE:
                gallery_success = self._try_gallery_dl(profile_url, user_dir)
                if gallery_success:
                    return True
            
            # Method 2: Try pinterest-dl
            if PINTEREST_DL_AVAILABLE:
                pinterest_dl_success = self._try_pinterest_dl(profile_url, user_dir)
                if pinterest_dl_success:
                    return True
            
            # Method 3: Try yt-dlp
            ytdlp_success = self._try_ytdlp_profile_download(profile_url, user_dir, max_pins)
            if ytdlp_success:
                if self.console:
                    self.console.print("[green]✓ Successfully downloaded using yt-dlp[/green]")
                return True
            
            # Method 4: Fallback to advanced web scraping
            pin_urls = self.scrape_user_pins_webscraping(username, max_pins)
            
            if not pin_urls:
                if self.console:
                    self.console.print("\n[red]━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━[/red]")
                    self.console.print("[red]✗ Unable to extract pins from profile[/red]")
                    self.console.print("[red]━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━[/red]\n")
                    
                    self.console.print("[yellow] Pinterest requires login to view profiles[/yellow]\n")
                    
                    self.console.print("[cyan] Recommended Solutions:[/cyan]\n")
                    
                    self.console.print("[green]  1. Install External Libraries (Most Reliable)[/green]")
                    self.console.print("[dim]     • gallery-dl: pip install gallery-dl[/dim]")
                    self.console.print("[dim]     • pinterest-dl: pip install pinterest-dl[/dim]")
                    self.console.print("[dim]     Then re-run the download[/dim]\n")
                    
                    self.console.print("[green]  2. Use yt-dlp with Browser Cookies[/green]")
                    self.console.print("[dim]     • Login to Pinterest in your browser first[/dim]")
                    self.console.print("[dim]     • Run: yt-dlp --cookies-from-browser chrome {profile_url}[/dim]\n")
                    
                    self.console.print("[green]  3. Direct Pin URLs[/green]")
                    self.console.print("[dim]     • Copy individual pin links: https://pinterest.com/pin/123456789/[/dim]\n")
                    
                    self.console.print("[green]  4. Browser Extension[/green]")
                    self.console.print("[dim]     • Search for Pinterest downloader in Chrome/Firefox stores[/dim]\n")
                return False
            
            # Download media from each pin
            total_stats = {'images': 0, 'videos': 0, 'failed': 0}
            
            for idx, pin_url in enumerate(pin_urls, 1):
                if self.console:
                    self.console.print(f"\n[bold]Pin {idx}/{len(pin_urls)}[/bold]")
                
                stats = self.download_pin(pin_url, user_dir)
                total_stats['images'] += stats['images']
                total_stats['videos'] += stats['videos']
                total_stats['failed'] += stats['failed']
                
                # Random delay between pins
                if idx < len(pin_urls):
                    time.sleep(random.uniform(2, 4))
            
            # Create ZIP archive if requested
            if create_zip and (total_stats['images'] > 0 or total_stats['videos'] > 0):
                zip_path = output_dir / f"pinterest_{username}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
                
                if self.console:
                    self.console.print(f"\n[cyan]Creating ZIP archive...[/cyan]")
                
                with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                    for root, dirs, files in os.walk(user_dir):
                        for file in files:
                            file_path = Path(root) / file
                            arcname = file_path.relative_to(user_dir)
                            zipf.write(file_path, arcname)
                
                if self.console:
                    self.console.print(f"[green]✓ ZIP created: {zip_path}[/green]")
            
            # Display summary
            if self.console:
                self.console.print(Panel.fit(
                    f"[bold green]Download Complete![/bold green]\n"
                    f"Images: {total_stats['images']}\n"
                    f"Videos: {total_stats['videos']}\n"
                    f"Failed: {total_stats['failed']}\n"
                    f"Location: {user_dir}",
                    border_style="green"
                ))
            
            return True
            
        except Exception as e:
            if self.console:
                self.console.print(f"[red]Error in username download: {e}[/red]")
            return False
        finally:
            self._close_driver()
    
    def download_board(self, username: str, board_name: str, output_dir: Path, max_pins: int = 100, create_zip: bool = True) -> bool:
        """Download all media from a specific Pinterest board
        
        Args:
            username: Pinterest username
            board_name: Name of the board
            output_dir: Directory to save downloads
            max_pins: Maximum number of pins to download
            create_zip: Whether to create a ZIP archive
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if self.console:
                self.console.print(Panel.fit(
                    f"[bold cyan]Downloading Pinterest Board[/bold cyan]\n"
                    f"Username: {username}\n"
                    f"Board: {board_name}\n"
                    f"Max Pins: {max_pins}",
                    border_style="cyan"
                ))
            
            # Create output directory
            board_dir = output_dir / f"pinterest_{username}_{board_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            board_dir.mkdir(parents=True, exist_ok=True)
            
            # Scrape pin URLs from board
            pin_urls = self.scrape_board_pins(username, board_name, max_pins)
            
            if not pin_urls:
                if self.console:
                    self.console.print("[yellow]No pins found in board[/yellow]")
                return False
            
            # Download media from each pin
            total_stats = {'images': 0, 'videos': 0, 'failed': 0}
            
            for idx, pin_url in enumerate(pin_urls, 1):
                if self.console:
                    self.console.print(f"\n[bold]Pin {idx}/{len(pin_urls)}[/bold]")
                
                stats = self.download_pin(pin_url, board_dir)
                total_stats['images'] += stats['images']
                total_stats['videos'] += stats['videos']
                total_stats['failed'] += stats['failed']
                
                if idx < len(pin_urls):
                    time.sleep(random.uniform(2, 4))
            
            # Create ZIP archive if requested
            if create_zip and (total_stats['images'] > 0 or total_stats['videos'] > 0):
                zip_path = output_dir / f"pinterest_{username}_{board_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
                
                if self.console:
                    self.console.print(f"\n[cyan]Creating ZIP archive...[/cyan]")
                
                with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                    for root, dirs, files in os.walk(board_dir):
                        for file in files:
                            file_path = Path(root) / file
                            arcname = file_path.relative_to(board_dir)
                            zipf.write(file_path, arcname)
                
                if self.console:
                    self.console.print(f"[green]✓ ZIP created: {zip_path}[/green]")
            
            # Display summary
            if self.console:
                self.console.print(Panel.fit(
                    f"[bold green]Download Complete![/bold green]\n"
                    f"Images: {total_stats['images']}\n"
                    f"Videos: {total_stats['videos']}\n"
                    f"Failed: {total_stats['failed']}\n"
                    f"Location: {board_dir}",
                    border_style="green"
                ))
            
            return True
            
        except Exception as e:
            if self.console:
                self.console.print(f"[red]Error in board download: {e}[/red]")
            return False
        finally:
            self._close_driver()
    
    def download(self, url: str, output_dir: Path = None) -> bool:
        """Main download method
        
        Args:
            url: Pinterest URL (pin, board, or profile)
            output_dir: Directory to save downloads
            
        Returns:
            True if successful, False otherwise
        """
        if not output_dir:
            output_dir = Path.cwd() / 'downloads' / 'pinterest'
        
        try:
            # Check if it's a single pin
            if '/pin/' in url:
                return self.download_pin(url, output_dir)
            
            # Extract username
            username = self.extract_username(url)
            if not username:
                if self.console:
                    self.console.print("[red]Could not extract username from URL[/red]")
                return False
            
            # Check if it's a board
            board_name = self.extract_board_name(url)
            if board_name:
                return self.download_board(username, board_name, output_dir)
            
            # Otherwise, it's a user profile
            return self.download_by_username(username, output_dir)
            
        except Exception as e:
            if self.console:
                self.console.print(f"[red]Error: {e}[/red]")
            return False
        finally:
            self._close_driver()
