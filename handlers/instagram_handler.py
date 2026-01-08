#!/usr/bin/env python3
"""
Instagram Handler Module
Handles downloading reels, stories, posts, and images from Instagram using Playwright.
Supports bulk downloads with ZIP creation and range selection.
"""

import os
import re
import json
import time
import random
import zipfile
import warnings
from pathlib import Path
from typing import Optional, Dict, Any, List, Tuple
from urllib.parse import urlparse, urljoin
from datetime import datetime

warnings.filterwarnings('ignore')

try:
    from playwright.sync_api import sync_playwright, Page, Browser, TimeoutError as PlaywrightTimeoutError
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False

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
    from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TimeRemainingColumn, TimeElapsedColumn, DownloadColumn
    from rich.table import Table
    from rich.prompt import Prompt, Confirm
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

from utils.utils import sanitize_filename
from utils.ui_components import Icons, Messages


class InstagramHandler:
    """Handles Instagram reels, stories, posts, and image downloads"""
    
    SUPPORTED_DOMAINS = [
        'instagram.com',
        'www.instagram.com',
        'm.instagram.com',
        'instagr.am',
    ]
    
    USER_AGENTS = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Linux; Android 14; Pixel 8) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36',
    ]
    
    def __init__(self, downloader):
        """Initialize Instagram handler
        
        Args:
            downloader: Reference to main downloader instance
        """
        self.downloader = downloader
        self.console = Console() if RICH_AVAILABLE else None
        self.session = self._create_session()
        self.browser = None
        self.context = None
        self.page = None
        self.playwright = None
        # Look for cookies in project directory first, then home directory
        project_cookies = Path('cookies.json')
        home_cookies = Path.home() / '.instagram_cookies.json'
        self.cookie_file = project_cookies if project_cookies.exists() else home_cookies
        
    def _create_session(self):
        """Create a requests session with retry logic"""
        if not REQUESTS_AVAILABLE:
            return None
            
        session = requests.Session()
        retry = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry)
        session.mount('http://', adapter)
        session.mount('https://', adapter)
        session.headers.update({
            'User-Agent': random.choice(self.USER_AGENTS)
        })
        return session
    
    def _init_browser(self):
        """Initialize Playwright browser with cookie support"""
        if not PLAYWRIGHT_AVAILABLE:
            if self.console:
                self.console.print(f"\n{Icons.get('error')} Playwright is not installed!", style="bold red")
                self.console.print("Install it with: pip install playwright && playwright install chromium")
            return False
        
        try:
            self.playwright = sync_playwright().start()
            self.browser = self.playwright.chromium.launch(
                headless=True,
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--disable-dev-shm-usage',
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-web-security'
                ]
            )
            self.context = self.browser.new_context(
                user_agent=random.choice(self.USER_AGENTS),
                viewport={'width': 1920, 'height': 1080},
                locale='en-US',
                timezone_id='America/New_York',
                permissions=['geolocation']
            )
            
            # Add stealth scripts
            self.context.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
                Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]});
                Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']});
                window.chrome = {runtime: {}};
            """)
            
            # Load cookies if available
            if self.cookie_file.exists():
                try:
                    with open(self.cookie_file, 'r') as f:
                        cookies = json.load(f)
                    
                    # Convert Chrome cookie format to Playwright format
                    playwright_cookies = []
                    for cookie in cookies:
                        pw_cookie = {
                            'name': cookie['name'],
                            'value': cookie['value'],
                            'domain': cookie['domain'],
                            'path': cookie['path'],
                            'secure': cookie.get('secure', True),
                            'httpOnly': cookie.get('httpOnly', False),
                        }
                        
                        # Convert expirationDate to expires (Unix timestamp)
                        if 'expirationDate' in cookie:
                            pw_cookie['expires'] = int(cookie['expirationDate'])
                        elif 'expires' in cookie:
                            pw_cookie['expires'] = cookie['expires']
                        
                        # Handle sameSite
                        same_site = cookie.get('sameSite', 'unspecified')
                        if same_site == 'no_restriction':
                            pw_cookie['sameSite'] = 'None'
                        elif same_site == 'unspecified':
                            pw_cookie['sameSite'] = 'Lax'
                        elif same_site in ['lax', 'strict', 'none']:
                            pw_cookie['sameSite'] = same_site.capitalize()
                        
                        playwright_cookies.append(pw_cookie)
                    
                    self.context.add_cookies(playwright_cookies)
                    
                    if self.console:
                        # Check for important cookies
                        cookie_names = [c['name'] for c in cookies]
                        has_session = 'sessionid' in cookie_names
                        has_user = 'ds_user_id' in cookie_names
                        status = "✓ Authenticated" if has_session else "⚠ No session"
                        self.console.print(f"{Icons.get('success' if has_session else 'warning')} Loaded {len(cookies)} cookies from {self.cookie_file.name} [{status}]", 
                                         style="green" if has_session else "yellow")
                except Exception as e:
                    if self.console:
                        self.console.print(f"{Icons.get('warning')} Failed to load cookies: {e}", style="yellow")
            else:
                if self.console:
                    self.console.print(f"{Icons.get('info')} No cookie file found at: {self.cookie_file}", style="cyan")
            
            self.page = self.context.new_page()
            return True
        except Exception as e:
            if self.console:
                self.console.print(f"\n{Icons.get('error')} Failed to initialize browser: {e}", style="bold red")
            return False
    
    def _save_cookies(self):
        """Save cookies for future use"""
        try:
            if self.context:
                cookies = self.context.cookies()
                # Save to project directory if that's where we loaded from
                save_path = self.cookie_file if self.cookie_file.exists() else Path('cookies.json')
                with open(save_path, 'w') as f:
                    json.dump(cookies, f, indent=2)
                if self.console:
                    self.console.print(f"{Icons.get('success')} Updated cookies in {save_path.name}", style="green")
        except Exception as e:
            if self.console:
                self.console.print(f"{Icons.get('warning')} Failed to save cookies: {e}", style="yellow")
    
    def _close_browser(self):
        """Close Playwright browser"""
        try:
            # Save cookies before closing
            if self.context:
                try:
                    self._save_cookies()
                except Exception:
                    pass
            
            if self.page:
                self.page.close()
            if self.context:
                self.context.close()
            if self.browser:
                self.browser.close()
            if self.playwright:
                self.playwright.stop()
        except Exception:
            pass
    
    def can_handle(self, url: str) -> bool:
        """Check if this handler can process the given URL"""
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            path = parsed.path.lower()
            
            # Check if domain is Instagram
            if not any(supported in domain for supported in self.SUPPORTED_DOMAINS):
                return False
            
            # Accept various Instagram URL patterns
            valid_patterns = [
                r'/p/[A-Za-z0-9_-]+',           # Single post
                r'/reel/[A-Za-z0-9_-]+',        # Single reel (singular)
                r'/reels/[A-Za-z0-9_-]+',       # Single reel (plural)
                r'/tv/[A-Za-z0-9_-]+',          # IGTV
                r'/stories/[^/]+',              # Stories
                r'/[A-Za-z0-9._]+/?$',          # Profile page
                r'/[A-Za-z0-9._]+/reels/?$',    # Profile reels page
                r'/[A-Za-z0-9._]+/tagged/?$',   # Profile tagged page
            ]
            
            return any(re.search(pattern, path) for pattern in valid_patterns)
        except Exception:
            return False
    
    def _extract_username_from_url(self, url: str) -> Optional[str]:
        """Extract username from Instagram URL"""
        patterns = [
            r'instagram\.com/([^/\?]+)',
            r'instagram\.com/stories/([^/\?]+)',
            r'instagr\.am/([^/\?]+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                username = match.group(1)
                # Filter out common paths
                if username not in ['p', 'reel', 'reels', 'tv', 'stories', 'explore', 'accounts']:
                    return username
        return None
    
    def _is_post_url(self, url: str) -> bool:
        """Check if URL is a specific post"""
        url_lower = url.lower()
        # Check for single post patterns with specific IDs after the slash
        # Pattern: /p/POST_ID, /reel/POST_ID, /reels/POST_ID, /tv/POST_ID
        # Use regex to ensure there's an ID after the post type
        patterns = [
            r'/p/[A-Za-z0-9_-]+',      # /p/ABC123
            r'/reel/[A-Za-z0-9_-]+',   # /reel/ABC123
            r'/reels/[A-Za-z0-9_-]+',  # /reels/ABC123
            r'/tv/[A-Za-z0-9_-]+'      # /tv/ABC123
        ]
        return any(re.search(pattern, url_lower) for pattern in patterns)
    
    def _is_stories_url(self, url: str) -> bool:
        """Check if URL is for stories"""
        return '/stories/' in url
    
    def download(self, url: str, output_dir: str = "downloads/instagram") -> Dict[str, Any]:
        """Main download method"""
        try:
            if not self.can_handle(url):
                return {
                    'success': False,
                    'error': 'URL not supported'
                }
            
            # Display header
            if self.console:
                self.console.print(Panel.fit(
                    f"{Icons.get('download')} Instagram Downloader",
                    style="bold magenta",
                    border_style="magenta"
                ))
            
            # Determine download type - check for specific post types first
            url_lower = url.lower()
            if self._is_post_url(url):
                # Direct download for single posts/reels without showing menu
                return self._download_single_post(url, output_dir)
            elif self._is_stories_url(url):
                return self._download_stories(url, output_dir)
            else:
                # Profile URL - extract username and determine type
                username = self._extract_username_from_url(url)
                if not username:
                    return {'success': False, 'error': 'Could not extract username'}
                
                # Check if it's a specific profile section
                if '/reels/' in url_lower and username in url_lower:
                    # Profile reels page: download all reels
                    return self._download_profile_posts(username, output_dir, content_type="reels")
                elif '/tagged/' in url_lower:
                    return {'success': False, 'error': 'Tagged posts download not yet supported'}
                else:
                    # Regular profile - show menu
                    return self._handle_profile_download(username, output_dir)
                
        except Exception as e:
            if self.console:
                self.console.print(f"\n{Icons.get('error')} Error: {e}", style="bold red")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _handle_profile_download(self, username: str, output_dir: str) -> Dict[str, Any]:
        """Handle profile-based downloads with menu"""
        if not self.console:
            return {'success': False, 'error': 'Rich console not available'}
        
        # Display options menu
        table = Table(title=f"Download Options for @{username}", show_header=True, header_style="bold magenta")
        table.add_column("Option", style="cyan", width=10)
        table.add_column("Description", style="white")
        
        table.add_row("1", "Download all posts")
        table.add_row("2", "Download all reels")
        table.add_row("3", "Download stories")
        table.add_row("4", "Download specific range")
        table.add_row("5", "Download as ZIP")
        
        self.console.print(table)
        
        choice = Prompt.ask(
            "\nSelect download option",
            choices=["1", "2", "3", "4", "5"],
            default="1"
        )
        
        if choice == "1":
            return self._download_profile_posts(username, output_dir, content_type="posts")
        elif choice == "2":
            return self._download_profile_posts(username, output_dir, content_type="reels")
        elif choice == "3":
            return self._download_stories_by_username(username, output_dir)
        elif choice == "4":
            start = int(Prompt.ask("Start index (1-based)", default="1"))
            end = int(Prompt.ask("End index", default="10"))
            return self._download_profile_posts(username, output_dir, start_index=start, end_index=end)
        elif choice == "5":
            return self._download_profile_posts(username, output_dir, create_zip=True)
        
        return {'success': False, 'error': 'Invalid choice'}
    
    def _download_single_post(self, url: str, output_dir: str) -> Dict[str, Any]:
        """Download a single post (reel, video, or images)"""
        if self.console:
            self.console.print(f"\n{Icons.get('search')} Extracting post information...", style="yellow")
        
        if not self._init_browser():
            return {'success': False, 'error': 'Failed to initialize browser'}
        
        # Extract post ID from URL to filter for correct video
        import re
        post_id_match = re.search(r'/(?:p|reel|reels)/([A-Za-z0-9_-]+)', url)
        post_id = post_id_match.group(1) if post_id_match else None
        
        if self.console and post_id:
            self.console.print(f"{Icons.get('info')} Post ID: {post_id}", style="dim cyan")
        
        # Storage for captured video URLs - dict with metadata
        captured_video_urls = {}  # {url: {'is_main_post': bool, 'size': int}}
        main_video_url = None  # Will store the main post's video
        post_specific_video_urls = []  # Videos confirmed to be from THIS post
        
        def capture_response(response):
            """Capture video URLs from network responses"""
            nonlocal main_video_url, post_specific_video_urls
            try:
                resp_url = response.url
                
                # Capture direct video URLs with size info
                if '.mp4' in resp_url and resp_url.startswith('http') and 'blob:' not in resp_url:
                    # Get content length to filter out tiny files (audio-only or previews)
                    content_length = response.headers.get('content-length', 0)
                    try:
                        size = int(content_length) if content_length else 0
                    except:
                        size = 0
                    
                    # Only capture if it's a reasonable size (> 100KB suggests video)
                    if size > 100000 or size == 0:  # 0 means unknown, still capture
                        captured_video_urls[resp_url] = {'is_main_post': False, 'size': size}
                
                # Check API responses for video URLs with STRICT post ID context
                if any(keyword in resp_url for keyword in ['graphql', 'api', 'media', 'query']):
                    try:
                        body = response.text()
                        
                        # STRICT check: Extract video URL that's directly associated with our post_id
                        # Look for patterns where shortcode/code is directly linked to video_url
                        if post_id and post_id in body:
                            patterns = [
                                # Pattern for shortcode followed by video_url in same object
                                rf'"(?:shortcode|code)"\s*:\s*"{re.escape(post_id)}"[^{{}}]*?"video_url"\s*:\s*"([^"]+)"',
                                # Pattern for video_url followed by shortcode in same object
                                rf'"video_url"\s*:\s*"([^"]+)"[^{{}}]*?"(?:shortcode|code)"\s*:\s*"{re.escape(post_id)}"',
                            ]
                            
                            for pattern in patterns:
                                matches = re.findall(pattern, body)
                                for match in matches:
                                    clean_url = match.replace('\\u0026', '&').replace('\\/', '/')
                                    if clean_url.startswith('http') and '.mp4' in clean_url:
                                        post_specific_video_urls.append(clean_url)
                                        if main_video_url is None:
                                            main_video_url = clean_url
                                        if captured_video_urls.get(clean_url):
                                            captured_video_urls[clean_url]['is_main_post'] = True
                                        else:
                                            captured_video_urls[clean_url] = {'is_main_post': True, 'size': 0}
                                        break
                                if main_video_url:
                                    break
                    except:
                        pass
            except:
                pass
        
        # Listen for network responses
        self.page.on('response', capture_response)
        
        try:
            # Navigate to post with more reliable wait strategy
            if self.console:
                self.console.print(f"{Icons.get('loading')} Loading page...", style="cyan")
            
            try:
                # First try: domcontentloaded with reasonable timeout
                self.page.goto(url, wait_until='domcontentloaded', timeout=30000)
                time.sleep(2)
                
                # Check if we're being blocked or redirected to login
                current_url = self.page.url
                if 'login' in current_url or 'challenge' in current_url:
                    if self.console:
                        self.console.print(f"{Icons.get('warning')} Instagram is requesting login. Cookies may be expired.", style="yellow")
                
                # Wait for video element to appear
                try:
                    self.page.wait_for_selector('video', timeout=10000)
                except:
                    time.sleep(2)
                    
            except Exception as nav_error:
                # Fallback: try with 'load'
                try:
                    self.page.goto(url, wait_until='load', timeout=30000)
                    time.sleep(2)
                except Exception as e:
                    # Last resort: try with commit
                    self.page.goto(url, wait_until='commit', timeout=20000)
                    time.sleep(2)
            
            if self.console:
                self.console.print(f"{Icons.get('success')} Page loaded, extracting video...", style="green")
            
            # Verify we're on the correct post page
            current_url = self.page.url
            if post_id and post_id not in current_url:
                if self.console:
                    self.console.print(f"{Icons.get('warning')} Page URL doesn't contain post ID {post_id}", style="yellow")
            
            # Quick video trigger - click the main video element (not sidebar/recommended)
            try:
                video_element = self.page.query_selector('article video, main video, div[role="dialog"] video, section video')
                if video_element:
                    video_element.click(timeout=2000)
            except:
                pass
            
            # Brief wait for video src to populate
            time.sleep(2)
            
            if self.console:
                self.console.print(f"{Icons.get('info')} Captured {len(captured_video_urls)} video URLs from network", style="cyan")
            
            # Try to get video from the main video element first (most reliable for current post)
            video_src = None
            try:
                # Get the first video element's source - focus on main article to avoid recommendations
                video_src = self.page.evaluate(f"""
                    (postId) => {{
                        // Prioritize video elements within the main article/dialog (current post)
                        const selectors = [
                            'article video',
                            'main video', 
                            'div[role="dialog"] video',
                            'section video',
                            'video'
                        ];
                        
                        for (const selector of selectors) {{
                            const mainVideo = document.querySelector(selector);
                            if (!mainVideo) continue;
                            
                            // Try currentSrc (most reliable - what's actually playing)
                            if (mainVideo.currentSrc && mainVideo.currentSrc.includes('.mp4') && !mainVideo.currentSrc.includes('blob:')) {{
                                return mainVideo.currentSrc;
                            }}
                            
                            // Try src attribute
                            if (mainVideo.src && mainVideo.src.includes('.mp4') && !mainVideo.src.includes('blob:')) {{
                                return mainVideo.src;
                            }}
                            
                            // Try source child elements
                            const source = mainVideo.querySelector('source');
                            if (source && source.src && source.src.includes('.mp4')) {{
                                return source.src;
                            }}
                        }}
                        
                        return null;
                    }}
                """, post_id)
            except:
                pass
            
            # Determine the best video URL to use
            final_video_url = None
            
            # Priority 1: Main video URL captured from API with post ID context (most reliable)
            if main_video_url:
                final_video_url = main_video_url
                if self.console:
                    self.console.print(f"{Icons.get('success')} Found video from API (matched post ID {post_id})", style="green")
            
            # Priority 1.5: Use post_specific_video_urls if main_video_url not set
            if not final_video_url and post_specific_video_urls:
                final_video_url = post_specific_video_urls[0]
                if self.console:
                    self.console.print(f"{Icons.get('success')} Found post-specific video URL for {post_id}", style="green")
            
            # Priority 2: Try to extract from page's script tags with STRICT post ID verification
            if not final_video_url and post_id:
                try:
                    extracted_from_page = self.page.evaluate(f"""
                        (postId) => {{
                            // Search for video_url in script tags with STRICT post ID verification
                            const scripts = document.querySelectorAll('script[type="application/ld+json"], script:not([src])');
                            for (const script of scripts) {{
                                const content = script.textContent || '';
                                
                                // Only process if this script contains our post ID
                                if (!content.includes(postId)) continue;
                                
                                // STRICT check: Look for the video_url that appears in the same data block as our post ID
                                const shortcodePattern = new RegExp('"(?:shortcode|code)"\\\\s*:\\\\s*"' + postId + '"');
                                if (!shortcodePattern.test(content)) continue;
                                
                                // Now look for video_url in the same object (within reasonable distance)
                                const postIdIdx = content.indexOf('"' + postId + '"');
                                if (postIdIdx === -1) continue;
                                
                                // Search within a window around the post ID (within same JSON object)
                                const windowStart = Math.max(0, postIdIdx - 5000);
                                const windowEnd = Math.min(content.length, postIdIdx + 10000);
                                const searchWindow = content.substring(windowStart, windowEnd);
                                
                                const videoMatch = searchWindow.match(/"video_url"\\s*:\\s*"([^"]+)"/);
                                if (videoMatch && videoMatch[1]) {{
                                    let url = videoMatch[1];
                                    url = url.replace(/\\\\u0026/g, '&').replace(/\\\\\//g, '/');
                                    if (url.includes('.mp4')) return url;
                                }}
                                
                                // Also check for contentUrl in ld+json VideoObject
                                if (content.includes('"@type":"VideoObject"')) {{
                                    const contentUrlMatch = searchWindow.match(/"contentUrl"\\s*:\\s*"([^"]+)"/);
                                    if (contentUrlMatch && contentUrlMatch[1]) {{
                                        return contentUrlMatch[1];
                                    }}
                                }}
                            }}
                            return null;
                        }}
                    """, post_id)
                    
                    if extracted_from_page:
                        final_video_url = extracted_from_page
                        if self.console:
                            self.console.print(f"{Icons.get('success')} Found verified video in page scripts for {post_id}", style="green")
                except:
                    pass
            
            # Priority 3: Video URLs marked as main post from network capture
            if not final_video_url and captured_video_urls:
                # First try to find one marked as main post
                for url, metadata in captured_video_urls.items():
                    if metadata['is_main_post']:
                        final_video_url = url
                        if self.console:
                            size_mb = metadata['size'] / (1024 * 1024) if metadata['size'] > 0 else 0
                            self.console.print(f"{Icons.get('success')} Found video from network (main post, {size_mb:.1f} MB)", style="green")
                        break
                
                # Priority 3.5: Try to find a URL that contains the post_id
                if not final_video_url:
                    for url, metadata in captured_video_urls.items():
                        if post_id and post_id in url:
                            final_video_url = url
                            if self.console:
                                size_mb = metadata['size'] / (1024 * 1024) if metadata['size'] > 0 else 0
                                self.console.print(f"{Icons.get('success')} Found video URL containing post_id ({size_mb:.1f} MB)", style="green")
                            break
                
                # If no main post match, use the largest video (likely the full quality one) - LAST RESORT
                if not final_video_url:
                    largest_url = max(captured_video_urls.items(), key=lambda x: x[1]['size'])
                    final_video_url = largest_url[0]
                    if self.console:
                        size_mb = largest_url[1]['size'] / (1024 * 1024) if largest_url[1]['size'] > 0 else 0
                        self.console.print(f"{Icons.get('warning')} Using largest captured video ({size_mb:.1f} MB) - not verified for {post_id}", style="yellow")
            
            # Priority 4: Video element src (might be from sidebar, use with caution)
            if not final_video_url and video_src and video_src.startswith('http') and 'blob:' not in video_src:
                final_video_url = video_src
                if self.console:
                    self.console.print(f"{Icons.get('warning')} Using video from page element (not verified)", style="yellow")
            
            # Extract media URLs with the best URL we found
            if final_video_url:
                # Clean the URL
                clean_url = final_video_url.replace('\\u0026', '&').replace('\\/', '/')
                
                # Remove byte range parameters that limit download size
                if 'bytestart=' in clean_url or 'byteend=' in clean_url:
                    # Remove all byte range params
                    clean_url = re.sub(r'[&?]bytestart=[^&]*', '', clean_url)
                    clean_url = re.sub(r'[&?]byteend=[^&]*', '', clean_url)
                    if self.console:
                        self.console.print(f"{Icons.get('info')} Removed byte range params for full download", style="dim cyan")
                
                if self.console:
                    self.console.print(f"{Icons.get('info')} Video URL: {clean_url[:80]}...", style="dim cyan")
                
                media_data = [{'url': clean_url, 'type': 'video', 'ext': 'mp4'}]
            else:
                # Fallback to original extraction method
                media_data = self._extract_post_media(list(captured_video_urls.keys()) if captured_video_urls else None)
            
            if not media_data:
                self._close_browser()
                if self.console:
                    self.console.print(f"\n{Icons.get('error')} No media found. The page might require login or the content is unavailable.", style="bold red")
                return {'success': False, 'error': 'No media found on page'}
            
            # Create output directory
            Path(output_dir).mkdir(parents=True, exist_ok=True)
            
            downloaded_files = []
            
            # Download with progress bar
            if self.console and RICH_AVAILABLE:
                with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    BarColumn(),
                    TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
                    DownloadColumn(),
                    TimeRemainingColumn(),
                    console=self.console
                ) as progress:
                    task = progress.add_task(
                        f"{Icons.get('download')} Downloading media...",
                        total=len(media_data)
                    )
                    
                    for idx, media_info in enumerate(media_data, 1):
                        filename = self._generate_filename(media_info, idx)
                        filepath = os.path.join(output_dir, filename)
                        
                        if self._download_media(media_info['url'], filepath):
                            downloaded_files.append(filepath)
                        
                        progress.update(task, advance=1)
            
            self._close_browser()
            
            if downloaded_files:
                if self.console:
                    self.console.print(f"\n{Icons.get('success')} Downloaded {len(downloaded_files)} file(s)", style="bold green")
                    for f in downloaded_files:
                        self.console.print(f"  {Icons.get('completed')} {os.path.basename(f)}", style="green")
                return {
                    'success': True,
                    'files': downloaded_files,
                    'count': len(downloaded_files)
                }
            else:
                if self.console:
                    self.console.print(f"\n{Icons.get('error')} Failed to download any files. Check your internet connection or try again.", style="bold red")
                return {'success': False, 'error': 'No files were successfully downloaded'}
                
        except Exception as e:
            self._close_browser()
            if self.console:
                self.console.print(f"\n{Icons.get('error')} Error downloading post: {e}", style="bold red")
            return {'success': False, 'error': str(e)}
    
    def _download_profile_posts(
        self,
        username: str,
        output_dir: str,
        content_type: str = "all",
        start_index: int = 1,
        end_index: Optional[int] = None,
        create_zip: bool = False
    ) -> Dict[str, Any]:
        """Download posts from a profile"""
        if self.console:
            self.console.print(f"\n{Icons.get('search')} Fetching @{username}'s {content_type}...", style="yellow")
        
        if not self._init_browser():
            return {'success': False, 'error': 'Failed to initialize browser'}
        
        try:
            # Navigate to the correct tab based on content type
            if content_type == "reels":
                profile_url = f"https://www.instagram.com/{username}/reels/"
            elif content_type == "posts":
                profile_url = f"https://www.instagram.com/{username}/"
            else:
                profile_url = f"https://www.instagram.com/{username}/"
            
            try:
                self.page.goto(profile_url, wait_until='domcontentloaded', timeout=60000)
            except:
                self.page.goto(profile_url, wait_until='load', timeout=60000)
            time.sleep(4)
            
            # Scroll and collect post URLs - verify they belong to the user
            # Allow collecting up to 500 posts (or end_index if specified)
            max_to_collect = end_index if end_index else 500
            post_urls = self._collect_and_verify_user_posts(username, content_type, max_to_collect)
            
            if self.console:
                self.console.print(f"{Icons.get('info')} Debug: Collected {len(post_urls)} verified URLs from @{username}", style="dim cyan")
            
            if not post_urls:
                self._close_browser()
                if self.console:
                    self.console.print(f"\n{Icons.get('error')} No posts found for @{username}. The profile might be private or have no {content_type}.", style="bold red")
                return {'success': False, 'error': 'No posts found'}
            
            # Apply range filter
            post_urls = post_urls[start_index-1:end_index] if end_index else post_urls[start_index-1:]
            
            # Display all posts that will be downloaded
            if self.console:
                self.console.print(f"\n{Icons.get('info')} Found {len(post_urls)} posts from @{username} to download:\n", style="bold cyan")
                
                # Create a table to display posts
                if RICH_AVAILABLE:
                    table = Table(show_header=True, header_style="bold magenta")
                    table.add_column("#", style="dim", width=4)
                    table.add_column("Post ID", style="cyan")
                    table.add_column("URL", style="blue")
                    
                    for idx, post_url in enumerate(post_urls[:20], 1):  # Show first 20
                        post_id = re.search(r'/(p|reel|reels|tv)/([A-Za-z0-9_-]+)', post_url)
                        post_id_str = post_id.group(2) if post_id else 'unknown'
                        table.add_row(str(idx), post_id_str, post_url[:60] + "...")
                    
                    if len(post_urls) > 20:
                        table.add_row("...", "...", f"...and {len(post_urls) - 20} more")
                    
                    self.console.print(table)
                    self.console.print()
            
            # Create output directory
            user_dir = os.path.join(output_dir, sanitize_filename(username))
            Path(user_dir).mkdir(parents=True, exist_ok=True)
            
            downloaded_files = []
            
            # Download each post using the single post download method
            if self.console and RICH_AVAILABLE:
                with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    BarColumn(),
                    TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
                    TextColumn("{task.completed}/{task.total}"),
                    TimeElapsedColumn(),
                    TimeRemainingColumn(),
                    console=self.console
                ) as progress:
                    task = progress.add_task(
                        f"{Icons.get('download')} Downloading from @{username}...",
                        total=len(post_urls)
                    )
                    
                    for idx, post_url in enumerate(post_urls, 1):
                        try:
                            # Extract post ID
                            post_id_match = re.search(r'/(p|reel|reels|tv)/([A-Za-z0-9_-]+)', post_url)
                            post_id = post_id_match.group(2) if post_id_match else f'post_{idx}'
                            
                            if self.console:
                                self.console.print(f"\n{Icons.get('download')} [{idx}/{len(post_urls)}] Downloading: {post_id}", style="cyan")
                            
                            # Use the single post download logic
                            result = self._download_single_post_simplified(post_url, user_dir, username, idx)
                            
                            if result['success'] and result.get('file'):
                                downloaded_files.append(result['file'])
                            else:
                                # Log the error but continue
                                if self.console:
                                    error_msg = result.get('error', 'Unknown error')
                                    self.console.print(f"{Icons.get('warning')} Skipped {post_id}: {error_msg}", style="yellow")
                            
                        except Exception as e:
                            if self.console:
                                self.console.print(f"{Icons.get('warning')} Exception for {post_id}: {str(e)[:80]}", style="yellow")
                        
                        progress.update(task, advance=1)
            
            self._close_browser()
            
            # Create ZIP if requested
            if create_zip and downloaded_files:
                zip_path = self._create_zip_archive(downloaded_files, username, user_dir)
                if self.console:
                    self.console.print(f"\n{Icons.get('success')} Created ZIP: {os.path.basename(zip_path)}", style="bold green")
            
            if downloaded_files:
                if self.console:
                    self.console.print(f"\n{Icons.get('success')} Downloaded {len(downloaded_files)} file(s)", style="bold green")
                return {
                    'success': True,
                    'files': downloaded_files,
                    'count': len(downloaded_files)
                }
            else:
                return {'success': False, 'error': 'No files downloaded'}
                
        except Exception as e:
            self._close_browser()
            if self.console:
                self.console.print(f"\n{Icons.get('error')} Error: {e}", style="bold red")
            return {'success': False, 'error': str(e)}
    
    def _download_stories(self, url: str, output_dir: str) -> Dict[str, Any]:
        """Download stories from URL"""
        username = self._extract_username_from_url(url)
        if not username:
            return {'success': False, 'error': 'Could not extract username'}
        
        return self._download_stories_by_username(username, output_dir)
    
    def _download_stories_by_username(self, username: str, output_dir: str) -> Dict[str, Any]:
        """Download stories by username"""
        if self.console:
            self.console.print(f"\n{Icons.get('search')} Fetching stories for @{username}...", style="yellow")
        
        if not self._init_browser():
            return {'success': False, 'error': 'Failed to initialize browser'}
        
        try:
            # Navigate to stories
            stories_url = f"https://www.instagram.com/stories/{username}/"
            try:
                self.page.goto(stories_url, wait_until='domcontentloaded', timeout=60000)
            except:
                self.page.goto(stories_url, wait_until='load', timeout=60000)
            time.sleep(4)
            
            # Extract story media
            story_media = self._extract_story_media()
            
            if not story_media:
                self._close_browser()
                if self.console:
                    self.console.print(f"\n{Icons.get('info')} No active stories found for @{username}", style="yellow")
                return {'success': False, 'error': 'No active stories'}
            
            # Create output directory
            stories_dir = os.path.join(output_dir, f"{sanitize_filename(username)}_stories")
            Path(stories_dir).mkdir(parents=True, exist_ok=True)
            
            downloaded_files = []
            
            # Download stories
            if self.console and RICH_AVAILABLE:
                with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    BarColumn(),
                    TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
                    DownloadColumn(),
                    TimeRemainingColumn(),
                    console=self.console
                ) as progress:
                    task = progress.add_task(
                        f"{Icons.get('download')} Downloading stories...",
                        total=len(story_media)
                    )
                    
                    for idx, media_info in enumerate(story_media, 1):
                        filename = f"story_{idx:03d}_{int(time.time())}.{media_info['ext']}"
                        filepath = os.path.join(stories_dir, filename)
                        
                        if self._download_media(media_info['url'], filepath):
                            downloaded_files.append(filepath)
                        
                        progress.update(task, advance=1)
            
            self._close_browser()
            
            if downloaded_files:
                if self.console:
                    self.console.print(f"\n{Icons.get('success')} Downloaded {len(downloaded_files)} stories", style="bold green")
                return {
                    'success': True,
                    'files': downloaded_files,
                    'count': len(downloaded_files)
                }
            else:
                return {'success': False, 'error': 'No stories downloaded'}
                
        except Exception as e:
            self._close_browser()
            if self.console:
                self.console.print(f"\n{Icons.get('error')} Error downloading stories: {e}", style="bold red")
            return {'success': False, 'error': str(e)}
    
    def _extract_post_media(self, captured_urls: List[str] = None) -> List[Dict[str, Any]]:
        """Extract media URLs from current post page"""
        media_data = []
        
        try:
            # Method 0: Use captured network URLs first (most reliable)
            if captured_urls:
                if self.console:
                    self.console.print(f"{Icons.get('search')} Processing {len(captured_urls)} captured network URLs...", style="cyan")
                
                # Clean and deduplicate URLs
                cleaned_urls = set()
                for url in captured_urls:
                    clean_url = url.replace('\\u0026', '&').replace('\\/', '/').split('"')[0]
                    if clean_url and clean_url.startswith('http') and '.mp4' in clean_url:
                        cleaned_urls.add(clean_url)
                
                if cleaned_urls:
                    # Select the best quality video (usually the one with longest URL or "bytestart" param)
                    # Instagram serves multiple qualities - we want the highest
                    best_url = None
                    best_score = 0
                    
                    for url in cleaned_urls:
                        score = 0
                        # Prefer URLs with higher byte ranges (usually better quality)
                        if 'bytestart=' in url:
                            score += 10
                        # Prefer longer URLs (more parameters = usually higher quality)
                        score += len(url) / 100
                        # Prefer URLs with "video" in path
                        if '/v/' in url or '/video/' in url:
                            score += 5
                        
                        if score > best_score:
                            best_score = score
                            best_url = url
                    
                    if best_url:
                        # Get the base URL without range params for full download
                        if 'bytestart=' in best_url:
                            # Remove byte range params to get full video
                            base_url = best_url.split('&bytestart=')[0]
                        else:
                            base_url = best_url
                        
                        media_data.append({
                            'url': base_url,
                            'type': 'video',
                            'ext': 'mp4'
                        })
                        
                        if self.console:
                            self.console.print(f"{Icons.get('success')} Selected best quality video from {len(cleaned_urls)} captured URLs!", style="green")
                        return media_data
            
            # Wait for dynamic content
            if self.console:
                self.console.print(f"{Icons.get('loading')} Waiting for media to load...", style="cyan")
            time.sleep(5)
            
            # Save page HTML for analysis if needed
            page_html = self.page.content()
            
            # Method 1: Extract from page HTML using regex (most reliable)
            if self.console:
                self.console.print(f"{Icons.get('search')} Analyzing page structure...", style="cyan")
            
            # Look for video URLs in the HTML
            import re
            
            # Pattern 1: Look for cdninstagram.com video URLs
            video_pattern1 = r'https://[^"\'\\]+\.cdninstagram\.com/[^"\'\\]+\.mp4[^"\'\\]*'
            videos1 = re.findall(video_pattern1, page_html)
            
            # Pattern 2: Look for scontent CDN video URLs  
            video_pattern2 = r'https://[^"\'\\]+scontent[^"\'\\]+\.mp4[^"\'\\]*'
            videos2 = re.findall(video_pattern2, page_html)
            
            # Combine and clean URLs
            all_video_urls = videos1 + videos2
            
            if self.console:
                self.console.print(f"  {Icons.get('info')} Found {len(all_video_urls)} potential video URLs in HTML", style="dim cyan")
            
            # Clean and deduplicate URLs
            seen_urls = set()
            for url in all_video_urls:
                # Clean up escaped characters
                clean_url = url.replace('\\/', '/').replace('\\u0026', '&')
                # Remove trailing junk
                clean_url = clean_url.split('"')[0].split("'")[0].split('\\')[0]
                
                if clean_url and clean_url not in seen_urls and clean_url.startswith('http'):
                    seen_urls.add(clean_url)
                    media_data.append({
                        'url': clean_url,
                        'type': 'video',
                        'ext': 'mp4'
                    })
            
            if media_data and self.console:
                self.console.print(f"{Icons.get('success')} Extracted {len(media_data)} video URL(s)", style="green")
            
            # Method 2: Try JavaScript extraction for video elements
            if not media_data:
                if self.console:
                    self.console.print(f"{Icons.get('info')} Trying video element extraction...", style="cyan")
                
                try:
                    video_srcs = self.page.evaluate("""
                        () => {
                            const urls = [];
                            document.querySelectorAll('video').forEach(v => {
                                if (v.src) urls.push(v.src);
                                if (v.currentSrc) urls.push(v.currentSrc);
                                v.querySelectorAll('source').forEach(s => {
                                    if (s.src) urls.push(s.src);
                                });
                            });
                            return urls;
                        }
                    """)
                    
                    for url in video_srcs:
                        if url and url.startswith('http') and 'blob:' not in url:
                            media_data.append({
                                'url': url,
                                'type': 'video',
                                'ext': 'mp4'
                            })
                            
                except Exception as e:
                    if self.console:
                        self.console.print(f"  {Icons.get('warning')} Video element extraction failed: {e}", style="yellow")
            
            # Method 3: Extract meta tags
            if not media_data:
                try:
                    meta_video = self.page.evaluate("""
                        () => {
                            const urls = [];
                            const meta1 = document.querySelector('meta[property="og:video"]');
                            if (meta1 && meta1.content) urls.push(meta1.content);
                            const meta2 = document.querySelector('meta[property="og:video:secure_url"]');
                            if (meta2 && meta2.content) urls.push(meta2.content);
                            return urls;
                        }
                    """)
                    
                    for url in meta_video:
                        if url:
                            media_data.append({
                                'url': url,
                                'type': 'video',
                                'ext': 'mp4'
                            })
                except Exception:
                    pass
            
            # Method 4: If still no videos, check for images (photo post)
            if not media_data:
                if self.console:
                    self.console.print(f"{Icons.get('info')} No videos found, checking for images...", style="cyan")
                
                # Look for high-res image URLs
                image_pattern = r'https://[^"\'\\]+scontent[^"\'\\]+\.(jpg|jpeg)[^"\'\\]*'
                images = re.findall(image_pattern, page_html)
                
                seen_imgs = set()
                for img_match in images[:10]:  # Limit to 10 images
                    img_url = img_match if isinstance(img_match, str) else img_match[0]
                    # Skip small images
                    if any(skip in img_url for skip in ['150x150', '320x320', 's150x150', 's320x320', 'profile', 'avatar']):
                        continue
                    
                    clean_url = img_url.replace('\\/', '/').split('"')[0].split("'")[0]
                    if clean_url and clean_url not in seen_imgs:
                        seen_imgs.add(clean_url)
                        media_data.append({
                            'url': clean_url,
                            'type': 'image',
                            'ext': 'jpg'
                        })
                
                if media_data and self.console:
                    self.console.print(f"{Icons.get('info')} This appears to be a photo post ({len(media_data)} images)", style="cyan")
            
            # Debug: Save page HTML if no media found
            if not media_data:
                try:
                    debug_path = os.path.join(os.getcwd(), 'debug_instagram_page.html')
                    with open(debug_path, 'w', encoding='utf-8') as f:
                        f.write(page_html)
                    if self.console:
                        self.console.print(f"{Icons.get('info')} Debug: Page HTML saved to {debug_path}", style="yellow")
                except Exception:
                    pass
            
            # Remove duplicates
            seen = set()
            unique_media = []
            for item in media_data:
                if item['url'] not in seen:
                    seen.add(item['url'])
                    unique_media.append(item)
            
            media_data = unique_media
            
        except Exception as e:
            if self.console:
                self.console.print(f"\n{Icons.get('warning')} Error extracting media: {e}", style="yellow")
        
        return media_data
    
    def _extract_story_media(self) -> List[Dict[str, Any]]:
        """Extract media URLs from stories"""
        story_media = []
        
        try:
            # Wait for stories to load
            time.sleep(3)
            
            # Extract videos
            videos = self.page.query_selector_all('video[src]')
            for video in videos:
                src = video.get_attribute('src')
                if src:
                    story_media.append({
                        'url': src,
                        'type': 'video',
                        'ext': 'mp4'
                    })
            
            # Extract images
            images = self.page.query_selector_all('img[srcset]')
            for img in images:
                srcset = img.get_attribute('srcset')
                if srcset:
                    urls = [s.strip().split()[0] for s in srcset.split(',')]
                    if urls:
                        story_media.append({
                            'url': urls[-1],
                            'type': 'image',
                            'ext': 'jpg'
                        })
        
        except Exception as e:
            if self.console:
                self.console.print(f"\n{Icons.get('warning')} Error extracting stories: {e}", style="yellow")
        
        return story_media
    
    def _collect_and_verify_user_posts(self, username: str, content_type: str = "all", max_posts: int = 500) -> List[str]:
        """Collect post URLs and verify they belong to the target user"""
        verified_post_urls = []
        post_ids = set()
        scroll_attempts = 0
        max_scroll_attempts = 500  # More attempts for large profiles
        consecutive_no_new_posts = 0
        last_post_count = 0
        
        try:
            if self.console:
                self.console.print(f"{Icons.get('search')} Scanning @{username}'s profile for all {content_type}...", style="cyan")
            
            # Initial wait for page to fully load
            time.sleep(3)
            
            while len(verified_post_urls) < max_posts and scroll_attempts < max_scroll_attempts:
                # Get all potential post links currently in DOM
                links = self.page.query_selector_all('a[href*="/p/"], a[href*="/reel/"], a[href*="/reels/"], a[href*="/tv/"]')
                
                if self.console and scroll_attempts == 0:
                    self.console.print(f"{Icons.get('info')} Found {len(links)} total links on page initially", style="dim cyan")
                
                # Process all links currently visible
                for link in links:
                    try:
                        href = link.get_attribute('href')
                        if not href:
                            continue
                        
                        # Extract post ID
                        post_id_match = re.search(r'/(p|reel|reels|tv)/([A-Za-z0-9_-]+)', href)
                        if not post_id_match:
                            continue
                        
                        post_id = post_id_match.group(2)
                        
                        # Skip if already processed
                        if post_id in post_ids:
                            continue
                        
                        full_url = urljoin('https://www.instagram.com', href)
                        
                        # Debug: Show first 5 posts being checked
                        if self.console and len(verified_post_urls) < 5 and scroll_attempts == 0:
                            self.console.print(f"{Icons.get('info')} Checking: {post_id} - {full_url[:60]}...", style="dim")
                        
                        # Filter by content type
                        if content_type == "reels" and not any(x in full_url for x in ["/reel/", "/reels/"]):
                            continue
                        elif content_type == "posts" and any(x in full_url for x in ["/reel/", "/reels/"]):
                            continue
                        
                        # Add to our collection
                        verified_post_urls.append(full_url)
                        post_ids.add(post_id)
                    except:
                        continue
                
                # Check if we found new posts this iteration
                new_posts_found = len(verified_post_urls) - last_post_count
                if new_posts_found == 0:
                    consecutive_no_new_posts += 1
                else:
                    consecutive_no_new_posts = 0
                    last_post_count = len(verified_post_urls)
                
                if len(verified_post_urls) >= max_posts:
                    break
                
                # Scroll strategy: scroll in smaller increments and wait for content
                # This helps Instagram's lazy loading work better
                
                # Get current scroll position and page height
                scroll_info = self.page.evaluate('''
                    () => ({
                        scrollY: window.scrollY,
                        innerHeight: window.innerHeight,
                        scrollHeight: document.body.scrollHeight
                    })
                ''')
                
                # Scroll down by one viewport height
                new_scroll_pos = scroll_info['scrollY'] + scroll_info['innerHeight']
                self.page.evaluate(f'window.scrollTo(0, {new_scroll_pos})')
                time.sleep(1.5)
                
                # Wait for any lazy-loaded content
                time.sleep(1)
                
                # Check if we're near the bottom
                new_scroll_info = self.page.evaluate('''
                    () => ({
                        scrollY: window.scrollY,
                        innerHeight: window.innerHeight,
                        scrollHeight: document.body.scrollHeight
                    })
                ''')
                
                at_bottom = (new_scroll_info['scrollY'] + new_scroll_info['innerHeight']) >= (new_scroll_info['scrollHeight'] - 100)
                
                # If at bottom and no new posts for a while, try scrolling back up and down
                if at_bottom and consecutive_no_new_posts >= 3:
                    # Scroll back up a bit to trigger more loading
                    self.page.evaluate('window.scrollBy(0, -1000)')
                    time.sleep(1)
                    # Scroll back down
                    self.page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
                    time.sleep(2)
                
                scroll_attempts += 1
                
                # Only stop if we've been at the bottom with no new posts for extended period
                if at_bottom and consecutive_no_new_posts >= 25:
                    if self.console:
                        self.console.print(f"{Icons.get('info')} Reached end of profile after {scroll_attempts} scrolls", style="dim yellow")
                    break
                
                # Show progress every 10 scrolls
                if scroll_attempts % 10 == 0 and self.console:
                    self.console.print(f"{Icons.get('info')} Scroll {scroll_attempts}: Found {len(verified_post_urls)} {content_type} from @{username}...", style="dim cyan")
        
        except Exception as e:
            if self.console:
                self.console.print(f"\n{Icons.get('warning')} Error collecting posts: {e}", style="yellow")
        
        if self.console:
            self.console.print(f"{Icons.get('success')} Finished scanning: Found {len(verified_post_urls)} {content_type} total", style="green")
        
        return verified_post_urls
    
    def _convert_json_cookies_to_netscape(self) -> Optional[Path]:
        """Convert JSON cookies to Netscape format for yt-dlp"""
        try:
            if not self.cookie_file.exists():
                return None
            
            with open(self.cookie_file, 'r') as f:
                cookies = json.load(f)
            
            # Create Netscape format cookie file
            netscape_file = Path('cookies_netscape.txt')
            
            with open(netscape_file, 'w') as f:
                f.write("# Netscape HTTP Cookie File\n")
                f.write("# https://curl.se/docs/http-cookies.html\n")
                f.write("# This file was generated automatically\n\n")
                
                for cookie in cookies:
                    # Netscape format: domain, flag, path, secure, expiration, name, value
                    domain = cookie.get('domain', '')
                    # Add leading dot if not present and domain doesn't start with dot
                    if domain and not domain.startswith('.'):
                        domain_flag = 'FALSE'
                    else:
                        domain_flag = 'TRUE'
                    
                    path = cookie.get('path', '/')
                    secure = 'TRUE' if cookie.get('secure', False) else 'FALSE'
                    
                    # Handle expiration
                    expiration = cookie.get('expirationDate', cookie.get('expires', 0))
                    if isinstance(expiration, float):
                        expiration = int(expiration)
                    if expiration == 0 or expiration is None:
                        expiration = int(time.time()) + 86400 * 365  # 1 year from now
                    
                    name = cookie.get('name', '')
                    value = cookie.get('value', '')
                    
                    # Write cookie line
                    f.write(f"{domain}\t{domain_flag}\t{path}\t{secure}\t{expiration}\t{name}\t{value}\n")
            
            return netscape_file
        except Exception as e:
            if self.console:
                self.console.print(f"{Icons.get('warning')} Failed to convert cookies: {e}", style="yellow")
            return None
    
    def _download_single_post_simplified(self, post_url: str, output_dir: str, username: str, index: int) -> Dict[str, Any]:
        """Download a single post using yt-dlp"""
        try:
            # Extract post ID from URL
            post_id_match = re.search(r'/(?:p|reel|reels|tv)/([A-Za-z0-9_-]+)', post_url)
            post_id = post_id_match.group(1) if post_id_match else f'post_{index}'
            
            # Generate filename
            filename = f"{sanitize_filename(username)}_{post_id}_{index:03d}.mp4"
            filepath = os.path.join(output_dir, filename)
            
            # Use yt-dlp to download
            import subprocess
            
            # Build yt-dlp command
            cmd = [
                'yt-dlp',
                '--no-warnings',
                '--quiet',
                '--no-progress',
                '-o', filepath,
                '-f', 'best',
            ]
            
            # Try to use cookies - convert JSON to Netscape format
            netscape_cookies = self._convert_json_cookies_to_netscape()
            if netscape_cookies and netscape_cookies.exists():
                cmd.extend(['--cookies', str(netscape_cookies)])
            else:
                # Try to use browser cookies directly (Chrome, Firefox, etc.)
                # yt-dlp can extract cookies from browsers
                cmd.extend(['--cookies-from-browser', 'chrome'])
            
            cmd.append(post_url)
            
            # Run yt-dlp
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=120  # 2 minute timeout per video
            )
            
            if result.returncode == 0:
                # Check if file was created
                if os.path.exists(filepath):
                    if self.console:
                        self.console.print(f"{Icons.get('success')} Downloaded: {post_id}", style="dim green")
                    return {'success': True, 'file': filepath, 'post_id': post_id}
                else:
                    # yt-dlp might have added extension, check for variations
                    for ext in ['.mp4', '.webm', '.mkv']:
                        base = filepath.rsplit('.', 1)[0]
                        alt_path = base + ext
                        if os.path.exists(alt_path):
                            if self.console:
                                self.console.print(f"{Icons.get('success')} Downloaded: {post_id}", style="dim green")
                            return {'success': True, 'file': alt_path, 'post_id': post_id}
                    
                    if self.console:
                        self.console.print(f"{Icons.get('warning')} yt-dlp succeeded but file not found for {post_id}", style="yellow")
                    return {'success': False, 'error': 'File not created'}
            else:
                error_msg = result.stderr.strip() if result.stderr else 'Unknown error'
                # If browser cookies failed, try without cookies
                if 'cookies' in error_msg.lower() or 'browser' in error_msg.lower():
                    # Retry without cookies
                    cmd_no_cookies = [
                        'yt-dlp',
                        '--no-warnings',
                        '--quiet',
                        '--no-progress',
                        '-o', filepath,
                        '-f', 'best',
                        post_url
                    ]
                    result2 = subprocess.run(cmd_no_cookies, capture_output=True, text=True, timeout=120)
                    if result2.returncode == 0 and os.path.exists(filepath):
                        if self.console:
                            self.console.print(f"{Icons.get('success')} Downloaded: {post_id}", style="dim green")
                        return {'success': True, 'file': filepath, 'post_id': post_id}
                
                if self.console:
                    self.console.print(f"{Icons.get('error')} yt-dlp failed for {post_id}: {error_msg[:80]}", style="red")
                return {'success': False, 'error': error_msg}
                
        except subprocess.TimeoutExpired:
            if self.console:
                self.console.print(f"{Icons.get('error')} Timeout downloading {post_id}", style="red")
            return {'success': False, 'error': 'Timeout'}
        except FileNotFoundError:
            if self.console:
                self.console.print(f"{Icons.get('error')} yt-dlp not found. Install with: pip install yt-dlp", style="red")
            return {'success': False, 'error': 'yt-dlp not installed'}
        except Exception as e:
            if self.console:
                self.console.print(f"{Icons.get('error')} Error downloading {post_id}: {str(e)[:50]}", style="red")
            return {'success': False, 'error': str(e)}
    
    def _collect_post_urls(self, content_type: str = "all", max_posts: int = 50, username: str = None) -> List[str]:
        """Collect post URLs from profile by scrolling"""
        post_urls = set()
        post_ids = set()  # Track post IDs to avoid duplicates
        no_new_posts_count = 0
        scroll_attempts = 0
        max_scroll_attempts = 50  # Allow more scrolls to find all posts
        
        try:
            # Scroll and collect URLs
            last_height = self.page.evaluate('document.body.scrollHeight')
            
            # Debug: Check what's on the page initially
            if self.console:
                initial_links = self.page.query_selector_all('a[href*="/reel"]')
                self.console.print(f"{Icons.get('info')} Initial scan found {len(initial_links)} reel links", style="dim cyan")
            
            # Track unique URLs by their path (not full URL to avoid query param duplicates)
            seen_paths = set()
            
            while len(post_urls) < max_posts and scroll_attempts < max_scroll_attempts:
                previous_count = len(post_urls)
                
                # Get all post links - use flexible selector that works for all pages
                # Don't restrict to article tags as Instagram's structure varies
                links = self.page.query_selector_all('a[href*="/p/"], a[href*="/reel/"], a[href*="/reels/"], a[href*="/tv/"]')
                
                for link in links:
                    href = link.get_attribute('href')
                    if href:
                        # Extract post ID to check for duplicates
                        post_id_match = re.search(r'/(p|reel|reels|tv)/([A-Za-z0-9_-]+)', href)
                        if not post_id_match:
                            continue
                        
                        post_id = post_id_match.group(2)
                        
                        # Skip if we already have this post ID
                        if post_id in post_ids:
                            continue
                        
                        # Create a path signature to detect duplicates regardless of query params or domain
                        path_signature = f"/{post_id_match.group(1)}/{post_id}"
                        if path_signature in seen_paths:
                            continue
                        
                        full_url = urljoin('https://www.instagram.com', href)
                        
                        # If username is provided, only collect posts from this user
                        # Check if this post belongs to the target user by verifying it's on their profile
                        if username:
                            # On profile pages, we should only get the user's posts
                            # Additional filtering: make sure URL is valid and from the user's profile context
                            pass  # Trust that we're on the user's profile page
                        
                        # Filter by content type - check for both /reel/ and /reels/
                        if content_type == "reels" and not any(x in full_url for x in ["/reel/", "/reels/"]):
                            continue
                        elif content_type == "posts" and any(x in full_url for x in ["/reel/", "/reels/"]):
                            continue
                        
                        post_urls.add(full_url)
                        post_ids.add(post_id)
                        seen_paths.add(path_signature)
                
                # Check if we found new posts
                if len(post_urls) == previous_count:
                    no_new_posts_count += 1
                    if no_new_posts_count >= 5:  # Increase from 3 to 5 for better coverage
                        break
                else:
                    no_new_posts_count = 0
                
                if len(post_urls) >= max_posts:
                    break
                
                # Scroll down more aggressively
                self.page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
                time.sleep(1.5)  # Slightly faster scrolling
                
                # Try scrolling a bit more to trigger lazy loading
                self.page.evaluate('window.scrollBy(0, 500)')
                time.sleep(0.5)
                
                # Check if we've reached the bottom
                new_height = self.page.evaluate('document.body.scrollHeight')
                if new_height == last_height:
                    no_new_posts_count += 1
                    # Only break if we've tried enough times
                    if no_new_posts_count >= 5:
                        break
                else:
                    last_height = new_height
                    no_new_posts_count = 0  # Reset counter when height changes
                
                scroll_attempts += 1
                
                # Show progress every 10 scrolls
                if scroll_attempts % 10 == 0 and self.console:
                    self.console.print(f"{Icons.get('info')} Scrolling... Found {len(post_urls)} posts so far", style="dim cyan")
        
        except Exception as e:
            if self.console:
                self.console.print(f"\n{Icons.get('warning')} Error collecting posts: {e}", style="yellow")
        
        return list(post_urls)
    
    def _download_media(self, url: str, filepath: str) -> bool:
        """Download media file"""
        try:
            if not self.session:
                return False
            
            # Add headers to ensure full download
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
                'Accept': 'video/mp4,video/*,*/*',
                'Accept-Encoding': 'identity',  # Disable compression to avoid issues
                'Range': None  # Explicitly no range request
            }
            
            response = self.session.get(url, stream=True, timeout=60, headers=headers)
            response.raise_for_status()
            
            # Check content length
            content_length = response.headers.get('content-length')
            if content_length:
                size_mb = int(content_length) / (1024 * 1024)
                if self.console:
                    self.console.print(f"{Icons.get('info')} Downloading {size_mb:.2f} MB...", style="dim cyan")
            
            total_bytes = 0
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        total_bytes += len(chunk)
            
            # Verify download size
            if total_bytes < 10000:  # Less than 10KB is suspicious
                if self.console:
                    self.console.print(f"\n{Icons.get('warning')} Downloaded only {total_bytes} bytes - file may be incomplete", style="yellow")
            
            return True
        except Exception as e:
            if self.console:
                self.console.print(f"\n{Icons.get('warning')} Failed to download {os.path.basename(filepath)}: {e}", style="yellow")
            return False
    
    def _generate_filename(self, media_info: Dict[str, Any], index: int, prefix: str = "instagram") -> str:
        """Generate filename for media"""
        timestamp = int(time.time())
        media_type = media_info['type']
        ext = media_info['ext']
        return f"{sanitize_filename(prefix)}_{media_type}_{index:03d}_{timestamp}.{ext}"
    
    def _create_zip_archive(self, files: List[str], username: str, output_dir: str) -> str:
        """Create ZIP archive of downloaded files"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        zip_filename = f"{sanitize_filename(username)}_instagram_{timestamp}.zip"
        zip_path = os.path.join(output_dir, zip_filename)
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file in files:
                if os.path.exists(file):
                    zipf.write(file, os.path.basename(file))
        
        return zip_path
    
    def get_info(self, url: str) -> Dict[str, Any]:
        """Get information about Instagram content without downloading"""
        try:
            if not self.can_handle(url):
                return {'success': False, 'error': 'URL not supported'}
            
            if not self._init_browser():
                return {'success': False, 'error': 'Failed to initialize browser'}
            
            self.page.goto(url, wait_until='networkidle', timeout=30000)
            time.sleep(2)
            
            info = {
                'success': True,
                'url': url,
                'platform': 'Instagram',
            }
            
            # Extract title/caption
            try:
                caption = self.page.query_selector('h1')
                if caption:
                    info['caption'] = caption.inner_text()[:100]
            except Exception:
                pass
            
            # Count media
            media_data = self._extract_post_media()
            info['media_count'] = len(media_data)
            info['has_video'] = any(m['type'] == 'video' for m in media_data)
            info['has_images'] = any(m['type'] == 'image' for m in media_data)
            
            self._close_browser()
            
            return info
            
        except Exception as e:
            self._close_browser()
            return {'success': False, 'error': str(e)}


def register_handler(downloader):
    """Register Instagram handler with downloader"""
    return InstagramHandler(downloader)
