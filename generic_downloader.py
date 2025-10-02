#!/usr/bin/env python3
"""
Advanced Generic Site Downloader - 2025 Edition
Handles sites with SSL/TLS issues, anti-bot protection, Cloudflare bypass, and complex video extraction
Uses multiple methods, proxies, and fallbacks for maximum compatibility
"""

import os
import sys
import re
import json
import time
import urllib.parse
import random
from pathlib import Path
from typing import Optional, Dict, List, Any
import warnings

# Suppress SSL warnings
warnings.filterwarnings('ignore', category=Warning)
import urllib3
urllib3.disable_warnings()

# Core libraries
import requests
from bs4 import BeautifulSoup

# Advanced request libraries
try:
    import httpx
    HTTPX_AVAILABLE = True
except ImportError:
    HTTPX_AVAILABLE = False

try:
    import cloudscraper
    CLOUDSCRAPER_AVAILABLE = True
except ImportError:
    CLOUDSCRAPER_AVAILABLE = False

try:
    from curl_cffi import requests as curl_requests
    CURL_CFFI_AVAILABLE = True
except ImportError:
    CURL_CFFI_AVAILABLE = False

try:
    from fake_useragent import UserAgent
    FAKE_UA_AVAILABLE = True
except ImportError:
    FAKE_UA_AVAILABLE = False

try:
    from requests_html import HTMLSession
    REQUESTS_HTML_AVAILABLE = True
except ImportError:
    REQUESTS_HTML_AVAILABLE = False

try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options as ChromeOptions
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    import undetected_chromedriver as uc
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False

try:
    from playwright.sync_api import sync_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False

try:
    import streamlink
    STREAMLINK_AVAILABLE = True
except ImportError:
    STREAMLINK_AVAILABLE = False

try:
    import yt_dlp
    YT_DLP_AVAILABLE = True
except ImportError:
    YT_DLP_AVAILABLE = False


class GenericSiteDownloader:
    """Advanced downloader for generic sites with multiple fallback methods"""
    
    def __init__(self, output_dir: Path, verbose: bool = False, proxies: Optional[List[str]] = None):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.verbose = verbose
        
        # Initialize user agent
        if FAKE_UA_AVAILABLE:
            self.ua = UserAgent()
        else:
            self.ua = None
        
        # Proxy support
        self.proxies = proxies or []
        self.current_proxy_index = 0
        
        # Common video file extensions and patterns
        self.video_extensions = ['.mp4', '.webm', '.m3u8', '.mpd', '.mkv', '.avi', '.mov', '.flv', '.m4v', '.ts']
        self.video_patterns = [
            r'https?://[^\s"\'<>]+\.mp4[^\s"\'<>]*',
            r'https?://[^\s"\'<>]+\.m3u8[^\s"\'<>]*',
            r'https?://[^\s"\'<>]+\.mpd[^\s"\'<>]*',
            r'https?://[^\s"\'<>]+/video[^\s"\'<>]*',
            r'https?://[^\s"\'<>]+/stream[^\s"\'<>]*',
        ]
        
        # SSL context that bypasses verification
        self.ssl_context = self._create_permissive_ssl_context()
    
    def _create_permissive_ssl_context(self):
        """Create SSL context that bypasses certificate verification"""
        import ssl
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        
        # Try to set legacy SSL options (may not work on all systems)
        try:
            context.minimum_version = ssl.TLSVersion.TLSv1
        except:
            pass
        
        # Try to enable more ciphers (LibreSSL may not support @SECLEVEL)
        try:
            context.set_ciphers('DEFAULT:!DH')
        except:
            try:
                context.set_ciphers('DEFAULT')
            except:
                pass
        
        return context
    
    def _create_ssl_adapter(self):
        """Create a custom SSL adapter for requests with legacy SSL support"""
        import ssl
        from requests.adapters import HTTPAdapter
        from urllib3.util.ssl_ import create_urllib3_context
        
        class SSLAdapter(HTTPAdapter):
            def init_poolmanager(self, *args, **kwargs):
                try:
                    context = create_urllib3_context()
                    context.check_hostname = False
                    context.verify_mode = ssl.CERT_NONE
                    
                    # Try legacy SSL settings
                    try:
                        context.minimum_version = ssl.TLSVersion.TLSv1
                    except:
                        pass
                    
                    # Try more permissive ciphers
                    try:
                        context.set_ciphers('DEFAULT:!DH')
                    except:
                        try:
                            context.set_ciphers('DEFAULT')
                        except:
                            pass
                    
                    kwargs['ssl_context'] = context
                except Exception as e:
                    # If custom context fails, just disable verification
                    kwargs['ssl_context'] = None
                    
                return super().init_poolmanager(*args, **kwargs)
        
        return SSLAdapter()
    
    def _get_random_headers(self) -> Dict[str, str]:
        """Get random headers to avoid detection"""
        if self.ua and FAKE_UA_AVAILABLE:
            user_agent = self.ua.random
        else:
            # Latest Chrome 2025 user agents
            user_agents = [
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
                'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
            ]
            user_agent = random.choice(user_agents)
        
        return {
            'User-Agent': user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br, zstd',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0',
            'sec-ch-ua': '"Chromium";v="131", "Not_A Brand";v="24"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"',
        }
    
    def _get_proxy(self) -> Optional[Dict[str, str]]:
        """Get next proxy from the list in rotation"""
        if not self.proxies:
            return None
        
        proxy = self.proxies[self.current_proxy_index]
        self.current_proxy_index = (self.current_proxy_index + 1) % len(self.proxies)
        
        return {
            'http': proxy,
            'https': proxy
        }
    
    def download(self, url: str, output_filename: Optional[str] = None) -> Optional[str]:
        """
        Download video from generic site using multiple methods
        Returns path to downloaded file or None if failed
        """
        print(f"\n{'='*80}")
        print(f"🔥 ADVANCED GENERIC SITE DOWNLOADER - 2025 EDITION")
        print(f"{'='*80}")
        print(f"🌐 URL: {url}")
        print(f"📁 Output: {self.output_dir}")
        if self.proxies:
            print(f"🔒 Proxies: {len(self.proxies)} configured")
        print(f"{'='*80}\n")
        
        methods = [
            ("Method 1: yt-dlp (Universal extractor)", self._download_with_ytdlp),
            ("Method 2: curl_cffi (TLS fingerprint bypass)", self._download_with_curl_cffi),
            ("Method 3: Cloudscraper v2 (Advanced Cloudflare bypass)", self._download_with_cloudscraper),
            ("Method 4: Playwright (Chromium automation + interception)", self._download_with_playwright),
            ("Method 5: Selenium Undetected (Anti-bot bypass)", self._download_with_selenium),
            ("Method 6: System curl (Best SSL compatibility)", self._download_with_system_curl),
            ("Method 7: httpx (Modern async HTTP)", self._download_with_httpx),
            ("Method 8: Streamlink (Stream extraction)", self._download_with_streamlink),
            ("Method 9: requests-html (JS rendering)", self._download_with_requests_html),
            ("Method 10: Advanced web scraping", self._download_with_advanced_scraping),
            ("Method 11: Direct video URL extraction", self._download_direct_video),
        ]
        
        for method_name, method_func in methods:
            try:
                print(f"\n🔧 Trying {method_name}...")
                result = method_func(url, output_filename)
                if result:
                    print(f"✅ SUCCESS with {method_name}!")
                    print(f"📥 Downloaded: {result}")
                    return result
                else:
                    print(f"⚠️  {method_name} failed, trying next method...")
            except Exception as e:
                if self.verbose:
                    import traceback
                    print(f"❌ {method_name} error: {str(e)}")
                    traceback.print_exc()
                else:
                    print(f"⚠️  {method_name} failed")
                continue
        
        print(f"\n❌ All methods failed for: {url}")
        return None
    
    def _download_with_ytdlp(self, url: str, output_filename: Optional[str]) -> Optional[str]:
        """Download using yt-dlp (most powerful universal extractor)"""
        if not YT_DLP_AVAILABLE:
            return None
        
        try:
            if not output_filename:
                output_filename = "%(title)s.%(ext)s"
            
            output_template = str(self.output_dir / output_filename)
            
            ydl_opts = {
                'outtmpl': output_template,
                'format': 'best',
                'quiet': not self.verbose,
                'no_warnings': not self.verbose,
                'nocheckcertificate': True,
                'geo_bypass': True,
                'user_agent': self._get_random_headers()['User-Agent'],
                'http_headers': self._get_random_headers(),
                'extractor_retries': 3,
                'fragment_retries': 10,
                'retry_sleep_functions': {'http': lambda n: 3},
            }
            
            # Add proxy if available
            if self.proxies:
                proxy = self.proxies[self.current_proxy_index]
                ydl_opts['proxy'] = proxy
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                if info:
                    # Get the actual downloaded filename
                    if 'requested_downloads' in info:
                        return info['requested_downloads'][0].get('filepath')
                    else:
                        # Try to find the file
                        title = info.get('title', 'video')
                        for ext in ['.mp4', '.webm', '.mkv', '.m4v']:
                            possible_file = self.output_dir / f"{title}{ext}"
                            if possible_file.exists():
                                return str(possible_file)
            
            return None
        except Exception as e:
            if self.verbose:
                print(f"yt-dlp error: {e}")
            return None

    def _download_with_system_curl(self, url: str, output_filename: Optional[str]) -> Optional[str]:
        """Download using system curl command (best SSL compatibility)"""
        try:
            import subprocess
            import tempfile
            
            # Create temp file for HTML content
            with tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix='.html') as tmp:
                tmp_path = tmp.name
            
            # Use curl with all SSL bypasses
            curl_cmd = [
                'curl',
                '-k',  # Insecure - ignore SSL cert verification
                '-L',  # Follow redirects
                '--insecure',  # Additional insecure flag
                '--tlsv1',  # Try TLS 1.0+
                '-A', self._get_random_headers()['User-Agent'],  # User agent
                '-o', tmp_path,  # Output to temp file
                '--connect-timeout', '30',
                '--max-time', '60',
            ]
            
            # Add proxy if available
            if self.proxies:
                proxy = self.proxies[self.current_proxy_index]
                curl_cmd.extend(['-x', proxy])
            
            curl_cmd.append(url)
            
            # Run curl
            result = subprocess.run(curl_cmd, capture_output=True, text=True, timeout=65)
            
            if result.returncode == 0:
                # Read the downloaded HTML
                with open(tmp_path, 'r', encoding='utf-8', errors='ignore') as f:
                    html_content = f.read()
                
                # Clean up temp file
                try:
                    os.unlink(tmp_path)
                except:
                    pass
                
                # Extract video URL from HTML
                video_url = self._extract_video_url_from_html(html_content, url)
                if video_url:
                    # Download the video file using curl
                    if not output_filename:
                        output_filename = f"video_{int(time.time())}.mp4"
                    
                    output_path = self.output_dir / output_filename
                    
                    download_cmd = [
                        'curl',
                        '-k',
                        '-L',
                        '--insecure',
                        '--tlsv1',
                        '-o', str(output_path),
                        '--connect-timeout', '30',
                        '--max-time', '600',
                        video_url
                    ]
                    
                    result = subprocess.run(download_cmd, capture_output=True, timeout=605)
                    
                    if result.returncode == 0 and output_path.exists():
                        return str(output_path)
            
            # Clean up temp file if still exists
            try:
                os.unlink(tmp_path)
            except:
                pass
            
            return None
            
        except Exception as e:
            if self.verbose:
                print(f"System curl error: {e}")
            return None
    
    def _download_with_advanced_scraping(self, url: str, output_filename: Optional[str]) -> Optional[str]:
        """Advanced web scraping with multiple extraction techniques"""
        try:
            import ssl
            session = requests.Session()
            
            # Mount the custom SSL adapter
            adapter = self._create_ssl_adapter()
            session.mount('https://', adapter)
            session.mount('http://', adapter)
            
            # Disable SSL warnings
            session.verify = False
            
            # Add proxy if available
            proxy_dict = self._get_proxy()
            
            response = session.get(
                url,
                headers=self._get_random_headers(),
                timeout=30,
                allow_redirects=True,
                proxies=proxy_dict
            )
            
            if response.status_code == 200:
                # Try multiple extraction methods
                video_urls = self._extract_all_video_urls(response.text, url)
                
                for video_url in video_urls:
                    if self.verbose:
                        print(f"Trying video URL: {video_url}")
                    result = self._download_file(video_url, output_filename, scraper=session)
                    if result:
                        return result
            
            return None
        except Exception as e:
            if self.verbose:
                print(f"Advanced scraping error: {e}")
            return None
    
    def _download_with_curl_cffi(self, url: str, output_filename: Optional[str]) -> Optional[str]:
        """Download using curl_cffi (best for TLS fingerprint bypass)"""
        if not CURL_CFFI_AVAILABLE:
            return None
        
        try:
            # curl_cffi mimics real browser TLS fingerprints - use latest Chrome
            proxies_dict = None
            if self.proxies:
                proxy = self.proxies[self.current_proxy_index]
                proxies_dict = {'http': proxy, 'https': proxy}
            
            response = curl_requests.get(
                url,
                impersonate="chrome131",  # Mimic Chrome 131 (latest 2025)
                verify=False,
                timeout=30,
                proxies=proxies_dict
            )
            
            if response.status_code == 200:
                # Try to find all video URLs in the page
                video_urls = self._extract_all_video_urls(response.text, url)
                
                for video_url in video_urls:
                    if self.verbose:
                        print(f"Found video URL: {video_url}")
                    
                    # Download with curl_cffi to maintain fingerprint
                    result = self._download_file_curl_cffi(video_url, output_filename, proxies_dict)
                    if result:
                        return result
            
            return None
        except Exception as e:
            if self.verbose:
                print(f"curl_cffi error: {e}")
            return None
    
    def _download_with_cloudscraper(self, url: str, output_filename: Optional[str]) -> Optional[str]:
        """Download using cloudscraper (Advanced Cloudflare bypass)"""
        if not CLOUDSCRAPER_AVAILABLE:
            return None
        
        try:
            scraper = cloudscraper.create_scraper(
                browser={
                    'browser': 'chrome',
                    'platform': 'darwin',
                    'desktop': True
                },
                delay=10,  # Add delay to solve challenges
                interpreter='native'  # Use native JS interpreter
            )
            
            # Mount custom SSL adapter to handle SSL issues
            adapter = self._create_ssl_adapter()
            scraper.mount('https://', adapter)
            scraper.mount('http://', adapter)
            
            # Add proxy if available
            proxy_dict = self._get_proxy()
            
            response = scraper.get(
                url, 
                timeout=45, 
                verify=False,
                proxies=proxy_dict,
                headers=self._get_random_headers()
            )
            
            if response.status_code == 200:
                video_urls = self._extract_all_video_urls(response.text, url)
                
                for video_url in video_urls:
                    if self.verbose:
                        print(f"Found video URL: {video_url}")
                    result = self._download_file(video_url, output_filename, scraper=scraper)
                    if result:
                        return result
            
            return None
        except Exception as e:
            if self.verbose:
                print(f"Cloudscraper error: {e}")
            return None
    
    def _download_with_streamlink(self, url: str, output_filename: Optional[str]) -> Optional[str]:
        """Download using streamlink (specialized stream extractor)"""
        if not STREAMLINK_AVAILABLE:
            return None
        
        try:
            streams = streamlink.streams(url)
            if not streams:
                return None
            
            # Get best quality stream
            best_stream = streams.get('best') or streams.get('worst')
            if not best_stream:
                return None
            
            # Generate output filename
            if not output_filename:
                output_filename = f"video_{int(time.time())}.mp4"
            
            output_path = self.output_dir / output_filename
            
            # Download stream
            with best_stream.open() as stream:
                with open(output_path, 'wb') as f:
                    while True:
                        data = stream.read(1024 * 1024)  # 1MB chunks
                        if not data:
                            break
                        f.write(data)
            
            return str(output_path)
        
        except Exception as e:
            if self.verbose:
                print(f"Streamlink error: {e}")
            return None
    
    def _download_with_httpx(self, url: str, output_filename: Optional[str]) -> Optional[str]:
        """Download using httpx (modern async HTTP client with HTTP/2)"""
        if not HTTPX_AVAILABLE:
            return None
        
        try:
            # Proxy setup
            proxies_dict = None
            if self.proxies:
                proxy = self.proxies[self.current_proxy_index]
                proxies_dict = {
                    'http://': proxy,
                    'https://': proxy
                }
            
            client = httpx.Client(
                verify=False,
                follow_redirects=True,
                timeout=30.0,
                headers=self._get_random_headers(),
                http2=True,  # Enable HTTP/2
                proxies=proxies_dict
            )
            
            response = client.get(url)
            
            if response.status_code == 200:
                video_urls = self._extract_all_video_urls(response.text, url)
                
                for video_url in video_urls:
                    result = self._download_file_httpx(video_url, output_filename, client)
                    if result:
                        client.close()
                        return result
            
            client.close()
            return None
        except Exception as e:
            if self.verbose:
                print(f"httpx error: {e}")
            return None
    
    def _download_with_selenium(self, url: str, output_filename: Optional[str]) -> Optional[str]:
        """Download using Selenium with undetected chromedriver (Anti-bot bypass)"""
        if not SELENIUM_AVAILABLE:
            return None
        
        try:
            # Use undetected chromedriver to avoid detection
            options = uc.ChromeOptions()
            options.add_argument('--headless=new')  # New headless mode
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_argument('--disable-gpu')
            options.add_argument('--window-size=1920,1080')
            
            # Add proxy if available
            if self.proxies:
                proxy = self.proxies[self.current_proxy_index]
                options.add_argument(f'--proxy-server={proxy}')
            
            # Enable network logging
            options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})
            
            driver = uc.Chrome(options=options, version_main=None)
            driver.get(url)
            
            # Wait for page to load
            time.sleep(8)
            
            # Collect video URLs from multiple sources
            video_urls = []
            
            # 1. Try to find video element
            try:
                video_elements = driver.find_elements(By.TAG_NAME, 'video')
                for video_element in video_elements:
                    src = video_element.get_attribute('src')
                    if src:
                        video_urls.append(src)
                    
                    # Check source tags
                    sources = video_element.find_elements(By.TAG_NAME, 'source')
                    for source in sources:
                        src = source.get_attribute('src')
                        if src:
                            video_urls.append(src)
            except:
                pass
            
            # 2. Extract from network logs
            try:
                logs = driver.get_log('performance')
                for log in logs:
                    message = json.loads(log['message'])
                    if message.get('message', {}).get('method') == 'Network.responseReceived':
                        response = message.get('message', {}).get('params', {}).get('response', {})
                        resp_url = response.get('url', '')
                        mime_type = response.get('mimeType', '')
                        
                        if any(ext in resp_url.lower() for ext in self.video_extensions) or 'video' in mime_type:
                            video_urls.append(resp_url)
            except:
                pass
            
            # 3. Extract from page source
            page_source = driver.page_source
            extracted_urls = self._extract_all_video_urls(page_source, url)
            video_urls.extend(extracted_urls)
            
            driver.quit()
            
            # Remove duplicates
            video_urls = list(set(video_urls))
            
            # Try to download each video URL
            for video_url in video_urls:
                if self.verbose:
                    print(f"Trying video URL: {video_url}")
                result = self._download_file(video_url, output_filename)
                if result:
                    return result
        
        except Exception as e:
            if self.verbose:
                import traceback
                print(f"Selenium error: {e}")
                traceback.print_exc()
        
        return None
    
    def _download_with_playwright(self, url: str, output_filename: Optional[str]) -> Optional[str]:
        """Download using Playwright (most reliable browser automation with network interception)"""
        if not PLAYWRIGHT_AVAILABLE:
            return None
        
        try:
            with sync_playwright() as p:
                # Launch options for stealth
                launch_options = {
                    'headless': True,
                    'args': [
                        '--disable-blink-features=AutomationControlled',
                        '--no-sandbox',
                        '--disable-dev-shm-usage',
                    ]
                }
                
                # Add proxy if available
                if self.proxies:
                    proxy = self.proxies[self.current_proxy_index]
                    # Parse proxy URL
                    if '://' in proxy:
                        proxy_parts = proxy.split('://', 1)
                        proxy_protocol = proxy_parts[0]
                        proxy_url = proxy_parts[1]
                    else:
                        proxy_url = proxy
                        proxy_protocol = 'http'
                    
                    if '@' in proxy_url:
                        # Has authentication
                        auth, server = proxy_url.rsplit('@', 1)
                        username, password = auth.split(':', 1)
                        launch_options['proxy'] = {
                            'server': f"{proxy_protocol}://{server}",
                            'username': username,
                            'password': password
                        }
                    else:
                        launch_options['proxy'] = {
                            'server': f"{proxy_protocol}://{proxy_url}"
                        }
                
                browser = p.chromium.launch(**launch_options)
                context = browser.new_context(
                    user_agent=self._get_random_headers()['User-Agent'],
                    ignore_https_errors=True,
                    viewport={'width': 1920, 'height': 1080}
                )
                page = context.new_page()
                
                # Intercept all network requests for video files
                video_urls = []
                video_data = []
                
                def handle_response(response):
                    url_lower = response.url.lower()
                    # Check for video file extensions or content type
                    if any(ext in url_lower for ext in self.video_extensions):
                        video_urls.append(response.url)
                        if self.verbose:
                            print(f"Intercepted video URL: {response.url}")
                    
                    # Check content-type header
                    try:
                        content_type = response.headers.get('content-type', '').lower()
                        if 'video' in content_type or 'stream' in content_type:
                            video_urls.append(response.url)
                            if self.verbose:
                                print(f"Intercepted video by content-type: {response.url}")
                    except:
                        pass
                
                page.on('response', handle_response)
                
                # Navigate to page
                page.goto(url, wait_until='networkidle', timeout=60000)
                time.sleep(5)  # Wait for any delayed video loads
                
                # Extract video URLs from page
                try:
                    video_sources = page.evaluate('''() => {
                        const videos = [];
                        
                        // Check video elements
                        document.querySelectorAll('video').forEach(v => {
                            if (v.src) videos.push(v.src);
                            v.querySelectorAll('source').forEach(s => {
                                if (s.src) videos.push(s.src);
                            });
                        });
                        
                        // Check for common video player variables
                        if (window.playerConfig && window.playerConfig.src) {
                            videos.push(window.playerConfig.src);
                        }
                        
                        return videos;
                    }''')
                    video_urls.extend(video_sources)
                except:
                    pass
                
                # Also extract from page HTML
                page_content = page.content()
                extracted_urls = self._extract_all_video_urls(page_content, url)
                video_urls.extend(extracted_urls)
                
                browser.close()
                
                # Remove duplicates
                video_urls = list(set(video_urls))
                
                # Try to download each video URL
                for video_url in video_urls:
                    if self.verbose:
                        print(f"Attempting to download: {video_url}")
                    result = self._download_file(video_url, output_filename)
                    if result:
                        return result
        
        except Exception as e:
            if self.verbose:
                import traceback
                print(f"Playwright error: {e}")
                traceback.print_exc()
        
        return None
    
    def _download_with_requests_html(self, url: str, output_filename: Optional[str]) -> Optional[str]:
        """Download using requests-html (renders JavaScript)"""
        if not REQUESTS_HTML_AVAILABLE:
            return None
        
        try:
            session = HTMLSession()
            response = session.get(url, verify=False, timeout=30)
            
            # Render JavaScript
            response.html.render(timeout=20, wait=2)
            
            # Extract video URL
            video_url = self._extract_video_url_from_html(response.html.html, url)
            
            if video_url:
                return self._download_file(video_url, output_filename)
        
        except Exception as e:
            if self.verbose:
                print(f"requests-html error: {e}")
        
        return None
    
    def _download_direct_video(self, url: str, output_filename: Optional[str]) -> Optional[str]:
        """Try to download if URL is already a direct video link"""
        if any(ext in url.lower() for ext in self.video_extensions):
            return self._download_file(url, output_filename)
        
        return None
    
    def _extract_video_url_from_html(self, html: str, base_url: str) -> Optional[str]:
        """Extract first video URL from HTML content"""
        urls = self._extract_all_video_urls(html, base_url)
        return urls[0] if urls else None
    
    def _extract_all_video_urls(self, html: str, base_url: str) -> List[str]:
        """Extract all possible video URLs from HTML content using advanced techniques"""
        video_urls = []
        soup = BeautifulSoup(html, 'html.parser')
        
        # Method 1: Look for video tags
        video_tags = soup.find_all('video')
        for video in video_tags:
            src = video.get('src')
            if src:
                video_urls.append(urllib.parse.urljoin(base_url, src))
            
            # Check source tags within video
            sources = video.find_all('source')
            for source in sources:
                src = source.get('src')
                if src:
                    video_urls.append(urllib.parse.urljoin(base_url, src))
                    
                # Check data attributes
                for attr in source.attrs:
                    if 'src' in attr.lower() or 'url' in attr.lower():
                        video_urls.append(urllib.parse.urljoin(base_url, source[attr]))
        
        # Method 2: Look for common video URL patterns with regex
        patterns = [
            r'"(https?://[^"]+\.mp4[^"]*)"',
            r"'(https?://[^']+\.mp4[^']*)'",
            r'"(https?://[^"]+\.m3u8[^"]*)"',
            r"'(https?://[^']+\.m3u8[^']*)'",
            r'"(https?://[^"]+\.mpd[^"]*)"',
            r"'(https?://[^']+\.mpd[^']*)'",
            r'"(https?://[^"]+\.webm[^"]*)"',
            r"'(https?://[^']+\.webm[^']*)'",
            r'video_url["\s:=]+["\']([^"\']+)["\']',
            r'videoUrl["\s:=]+["\']([^"\']+)["\']',
            r'file["\s:=]+["\']([^"\']+\.(mp4|m3u8|mpd|webm)[^"\']*)["\']',
            r'src["\s:=]+["\']([^"\']+\.(mp4|m3u8|mpd|webm)[^"\']*)["\']',
            r'source["\s:=]+["\']([^"\']+\.(mp4|m3u8|mpd|webm)[^"\']*)["\']',
            r'url["\s:=]+["\']([^"\']+\.(mp4|m3u8|mpd|webm)[^"\']*)["\']',
            r'"content_url":\s*"([^"]+)"',
            r'"contentUrl":\s*"([^"]+)"',
            r'"video":\s*"([^"]+)"',
            r'hlsUrl["\s:=]+["\']([^"\']+)["\']',
            r'dashUrl["\s:=]+["\']([^"\']+)["\']',
            r'stream_url["\s:=]+["\']([^"\']+)["\']',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, html, re.IGNORECASE)
            for match in matches:
                # Handle tuple matches from groups
                if isinstance(match, tuple):
                    match = match[0]
                video_urls.append(urllib.parse.urljoin(base_url, match))
        
        # Method 3: Look for JSON-LD structured data
        try:
            json_ld_scripts = soup.find_all('script', type='application/ld+json')
            for script in json_ld_scripts:
                try:
                    data = json.loads(script.string)
                    # Handle different JSON-LD structures
                    if isinstance(data, dict):
                        if 'contentUrl' in data:
                            video_urls.append(urllib.parse.urljoin(base_url, data['contentUrl']))
                        if 'embedUrl' in data:
                            video_urls.append(urllib.parse.urljoin(base_url, data['embedUrl']))
                        if 'video' in data and isinstance(data['video'], dict):
                            if 'contentUrl' in data['video']:
                                video_urls.append(urllib.parse.urljoin(base_url, data['video']['contentUrl']))
                except:
                    pass
        except:
            pass
        
        # Method 4: Look for Open Graph video meta tags
        og_video_tags = soup.find_all('meta', property=re.compile(r'og:video'))
        for tag in og_video_tags:
            content = tag.get('content')
            if content:
                video_urls.append(urllib.parse.urljoin(base_url, content))
        
        # Method 5: Look for Twitter card video meta tags
        twitter_video_tags = soup.find_all('meta', attrs={'name': re.compile(r'twitter:player')})
        for tag in twitter_video_tags:
            content = tag.get('content')
            if content:
                video_urls.append(urllib.parse.urljoin(base_url, content))
        
        # Method 6: Look for data attributes with video URLs
        elements_with_data = soup.find_all(attrs={'data-src': True})
        elements_with_data.extend(soup.find_all(attrs={'data-video': True}))
        elements_with_data.extend(soup.find_all(attrs={'data-url': True}))
        
        for elem in elements_with_data:
            for attr in elem.attrs:
                if 'video' in attr.lower() or 'src' in attr.lower() or 'url' in attr.lower():
                    value = elem[attr]
                    if any(ext in str(value).lower() for ext in self.video_extensions):
                        video_urls.append(urllib.parse.urljoin(base_url, value))
        
        # Method 7: Search for base64 encoded video URLs
        try:
            import base64
            b64_pattern = r'data:video/[^;]+;base64,([A-Za-z0-9+/=]+)'
            b64_matches = re.findall(b64_pattern, html)
            # Note: Base64 videos are embedded, we'll skip these for now as they're handled differently
        except:
            pass
        
        # Remove duplicates and filter valid URLs
        unique_urls = []
        seen = set()
        for url in video_urls:
            # Clean up the URL
            url = url.strip()
            # Remove escape characters
            url = url.replace('\\/', '/')
            url = url.replace('\\', '')
            
            if url and url not in seen:
                # Basic validation
                if url.startswith('http') or url.startswith('//'):
                    if url.startswith('//'):
                        url = 'https:' + url
                    seen.add(url)
                    unique_urls.append(url)
        
        return unique_urls
    
    def _download_file(self, url: str, output_filename: Optional[str] = None, scraper=None) -> Optional[str]:
        """Download file from direct URL using requests"""
        try:
            # Generate filename if not provided
            if not output_filename:
                # Try to get filename from URL
                parsed = urllib.parse.urlparse(url)
                filename = os.path.basename(parsed.path)
                if not filename or len(filename) < 3:
                    filename = f"video_{int(time.time())}.mp4"
                output_filename = filename
            
            output_path = self.output_dir / output_filename
            
            # Get proxy if available
            proxy_dict = self._get_proxy()
            
            # Use provided scraper or create new session
            if scraper:
                response = scraper.get(url, stream=True, timeout=120, verify=False)
            else:
                session = requests.Session()
                session.verify = False
                adapter = self._create_ssl_adapter()
                session.mount('https://', adapter)
                session.mount('http://', adapter)
                
                response = session.get(
                    url,
                    headers=self._get_random_headers(),
                    stream=True,
                    timeout=120,
                    proxies=proxy_dict
                )
            
            if response.status_code == 200:
                total_size = int(response.headers.get('content-length', 0))
                
                with open(output_path, 'wb') as f:
                    if total_size:
                        downloaded = 0
                        chunk_size = 1024 * 1024  # 1MB chunks
                        for chunk in response.iter_content(chunk_size=chunk_size):
                            if chunk:
                                f.write(chunk)
                                downloaded += len(chunk)
                                if self.verbose:
                                    progress = (downloaded / total_size) * 100
                                    print(f"\rDownloading: {progress:.1f}% ({downloaded}/{total_size} bytes)", end='')
                    else:
                        for chunk in response.iter_content(chunk_size=1024*1024):
                            if chunk:
                                f.write(chunk)
                
                if self.verbose:
                    print()  # New line after progress
                
                # Verify file was downloaded
                if output_path.exists() and output_path.stat().st_size > 0:
                    return str(output_path)
        
        except Exception as e:
            if self.verbose:
                print(f"Download error: {e}")
        
        return None
    
    def _download_file_curl_cffi(self, url: str, output_filename: Optional[str] = None, proxies_dict=None) -> Optional[str]:
        """Download file using curl_cffi to maintain TLS fingerprint"""
        if not CURL_CFFI_AVAILABLE:
            return self._download_file(url, output_filename)
        
        try:
            if not output_filename:
                parsed = urllib.parse.urlparse(url)
                filename = os.path.basename(parsed.path)
                if not filename or len(filename) < 3:
                    filename = f"video_{int(time.time())}.mp4"
                output_filename = filename
            
            output_path = self.output_dir / output_filename
            
            response = curl_requests.get(
                url,
                impersonate="chrome131",
                verify=False,
                timeout=120,
                stream=True,
                proxies=proxies_dict
            )
            
            if response.status_code == 200:
                with open(output_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=1024*1024):
                        if chunk:
                            f.write(chunk)
                
                if output_path.exists() and output_path.stat().st_size > 0:
                    return str(output_path)
        
        except Exception as e:
            if self.verbose:
                print(f"curl_cffi download error: {e}")
        
        return None
    
    def _download_file_httpx(self, url: str, output_filename: Optional[str] = None, client=None) -> Optional[str]:
        """Download file using httpx with HTTP/2 support"""
        if not HTTPX_AVAILABLE:
            return self._download_file(url, output_filename)
        
        try:
            if not output_filename:
                parsed = urllib.parse.urlparse(url)
                filename = os.path.basename(parsed.path)
                if not filename or len(filename) < 3:
                    filename = f"video_{int(time.time())}.mp4"
                output_filename = filename
            
            output_path = self.output_dir / output_filename
            
            if not client:
                proxies_dict = None
                if self.proxies:
                    proxy = self.proxies[self.current_proxy_index]
                    proxies_dict = {
                        'http://': proxy,
                        'https://': proxy
                    }
                
                client = httpx.Client(
                    verify=False,
                    follow_redirects=True,
                    timeout=120.0,
                    headers=self._get_random_headers(),
                    http2=True,
                    proxies=proxies_dict
                )
                should_close = True
            else:
                should_close = False
            
            with client.stream('GET', url) as response:
                if response.status_code == 200:
                    with open(output_path, 'wb') as f:
                        for chunk in response.iter_bytes(chunk_size=1024*1024):
                            if chunk:
                                f.write(chunk)
                    
                    if should_close:
                        client.close()
                    
                    if output_path.exists() and output_path.stat().st_size > 0:
                        return str(output_path)
            
            if should_close:
                client.close()
        
        except Exception as e:
            if self.verbose:
                print(f"httpx download error: {e}")
        
        return None


# Standalone usage
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Advanced Generic Site Downloader - 2025 Edition",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s "https://example.com/video"
  %(prog)s "https://example.com/video" -o downloads -v
  %(prog)s "https://example.com/video" --proxy socks5://127.0.0.1:9050
  %(prog)s "https://example.com/video" --proxy-file proxies.txt
        """
    )
    parser.add_argument("url", help="URL to download from")
    parser.add_argument("-o", "--output", help="Output directory", default="downloads")
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
    parser.add_argument("-p", "--proxy", help="Proxy to use (e.g., http://proxy:port, socks5://proxy:port)")
    parser.add_argument("--proxy-file", help="File containing list of proxies (one per line)")
    parser.add_argument("-f", "--filename", help="Output filename (optional)")
    
    args = parser.parse_args()
    
    # Load proxies
    proxies = []
    if args.proxy:
        proxies.append(args.proxy)
    if args.proxy_file:
        try:
            with open(args.proxy_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        proxies.append(line)
            print(f"Loaded {len(proxies)} proxies from {args.proxy_file}")
        except Exception as e:
            print(f"Warning: Could not load proxy file: {e}")
    
    downloader = GenericSiteDownloader(
        Path(args.output), 
        verbose=args.verbose,
        proxies=proxies if proxies else None
    )
    result = downloader.download(args.url, output_filename=args.filename)
    
    if result:
        print(f"\n✅ Download successful: {result}")
        sys.exit(0)
    else:
        print(f"\n❌ Download failed")
        sys.exit(1)
