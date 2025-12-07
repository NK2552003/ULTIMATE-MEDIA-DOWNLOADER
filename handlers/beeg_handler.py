#!/usr/bin/env python3
"""
Beeg Handler Module
Handles downloading videos from beeg.com using yt-dlp with proper configuration.
Includes fallback methods for SSL/TLS issues using subprocess curl.
"""

import os
import re
import ssl
import json
import random
import warnings
import subprocess
import shutil
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
    from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, DownloadColumn, TransferSpeedColumn
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

from utils.utils import sanitize_filename
from utils.ui_components import Icons, Messages

# Check if curl is available
CURL_AVAILABLE = shutil.which('curl') is not None


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


class BeegHandler:
    """Handles Beeg video downloads"""
    
    SUPPORTED_DOMAINS = [
        'beeg.com',
        'www.beeg.com',
    ]
    
    # API endpoints
    API_BASE = 'https://store.externulls.com'
    VIDEO_CDN_BASE = 'https://video.beeg.com'
    
    USER_AGENTS = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    ]
    
    def __init__(self, downloader):
        self.downloader = downloader
        self.console = Console() if RICH_AVAILABLE else None
        self.session = None
        self.current_user_agent = None
        self.use_fallback = False  # Flag to use curl-based fallback
        
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
        })
    
    @classmethod
    def is_beeg_url(cls, url: str) -> bool:
        url_lower = url.lower()
        return any(domain in url_lower for domain in cls.SUPPORTED_DOMAINS)
    
    def extract_video_id(self, url: str) -> Optional[str]:
        """Extract video ID from URL, handling negative IDs and leading zeros"""
        # URL format: https://beeg.com/-0454199801215758 or https://beeg.com/1234567890
        match = re.search(r'beeg\.com/-?(\d+)', url, re.I)
        if match:
            # Return as string but strip leading zeros for API calls
            return match.group(1).lstrip('0') or '0'
        return None
    
    def _extract_video_id_raw(self, url: str) -> Optional[str]:
        """Extract raw video ID from URL (with leading zeros)"""
        match = re.search(r'beeg\.com/-?(\d+)', url, re.I)
        if match:
            return match.group(1)
        return None
    
    def _curl_fetch(self, url: str, headers: Dict[str, str] = None) -> Optional[str]:
        """Fetch URL using subprocess curl with TLS 1.2 to bypass SSL issues"""
        if not CURL_AVAILABLE:
            return None
        
        cmd = [
            'curl', '-s', '-k',
            '--max-time', '30',
            '--tlsv1.2',
        ]
        
        # Add headers
        default_headers = {
            'User-Agent': self.current_user_agent or self._get_random_user_agent(),
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Origin': 'https://beeg.com',
            'Referer': 'https://beeg.com/',
        }
        
        if headers:
            default_headers.update(headers)
        
        for key, value in default_headers.items():
            cmd.extend(['-H', f'{key}: {value}'])
        
        cmd.append(url)
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=35)
            if result.returncode == 0:
                return result.stdout
        except subprocess.TimeoutExpired:
            self._print_rich("[yellow]⚠ Request timed out[/yellow]")
        except Exception as e:
            self._print_rich(f"[yellow]⚠ Curl error: {str(e)}[/yellow]")
        
        return None
    
    def _fetch_video_info_api(self, video_id: str) -> Optional[Dict[str, Any]]:
        """Fetch video information from Beeg API using curl fallback"""
        api_url = f'{self.API_BASE}/facts/file/{video_id}'
        
        self._print_rich("[cyan]⌕ Fetching video info from API...[/cyan]")
        
        response = self._curl_fetch(api_url)
        if not response:
            return None
        
        try:
            data = json.loads(response)
            
            # Check for API errors
            if 'error' in data or 'code' in data:
                error_msg = data.get('message', data.get('error', 'Unknown error'))
                self._print_rich(f"[yellow]⚠ API error: {error_msg}[/yellow]")
                return None
            
            return data
        except json.JSONDecodeError as e:
            self._print_rich(f"[yellow]⚠ Failed to parse API response: {str(e)}[/yellow]")
            return None
    
    def _extract_qualities_from_api(self, api_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract available qualities from API data"""
        qualities = []
        
        file_data = api_data.get('file', {})
        qualities_data = file_data.get('qualities', {})
        
        # Prefer h264 for compatibility, then h265, then av1
        codec_preference = ['h264', 'h265', 'av1']
        
        for codec in codec_preference:
            codec_qualities = qualities_data.get(codec, [])
            if codec_qualities:
                for q in codec_qualities:
                    quality = q.get('quality')
                    if quality:
                        qualities.append({
                            'quality': f"{quality}p",
                            'height': quality,
                            'codec': codec,
                            'url': q.get('url'),
                            'filesize': q.get('size'),
                            'video_codec': q.get('video_codec'),
                            'audio_codec': q.get('audio_codec'),
                        })
                break  # Use first available codec
        
        # Sort by quality (highest first)
        qualities.sort(key=lambda x: x['height'], reverse=True)
        return qualities
    
    def _get_video_url_from_api(self, api_data: Dict[str, Any], quality: str = "best") -> Optional[Dict[str, Any]]:
        """Get video download URL from API data - prioritizes HLS streams"""
        file_data = api_data.get('file', {})
        hls_resources = file_data.get('hls_resources', {})
        
        # Get title
        title = "Beeg Video"
        data_list = file_data.get('data', [])
        for item in data_list:
            if item.get('cd_column') == 'sf_name':
                title = item.get('cd_value', title)
                break
        
        # Get duration
        duration = file_data.get('fl_duration', 0)
        
        # Parse quality preference
        target_height = None
        if quality != "best":
            match = re.search(r'(\d+)', quality)
            if match:
                target_height = int(match.group(1))
        
        # Use HLS resources (they work reliably)
        video_url = None
        selected_quality = None
        
        if hls_resources:
            # Quality preference order
            quality_keys = ['fl_cdn_1080', 'fl_cdn_720', 'fl_cdn_480', 'fl_cdn_360', 'fl_cdn_240']
            
            if target_height:
                # Find matching quality
                key = f'fl_cdn_{target_height}'
                if key in hls_resources:
                    video_url = hls_resources[key]
                    selected_quality = f"{target_height}p"
            
            if not video_url:
                # Use best available (or first match for target)
                if target_height:
                    # Find closest quality >= target
                    for key in quality_keys:
                        height = int(key.split('_')[-1])
                        if height >= target_height and key in hls_resources:
                            video_url = hls_resources[key]
                            selected_quality = f"{height}p"
                            break
                
                # If still no match, use best available
                if not video_url:
                    for key in quality_keys:
                        if key in hls_resources:
                            video_url = hls_resources[key]
                            height = key.split('_')[-1]
                            selected_quality = f"{height}p"
                            break
        
        if not video_url:
            return None
        
        # Build full video URL
        full_url = f"{self.VIDEO_CDN_BASE}/{video_url}"
        
        return {
            'title': title,
            'duration': duration,
            'video_url': full_url,
            'quality': selected_quality,
            'is_hls': True,  # HLS streams are always used now
        }
    
    def _download_with_curl(self, video_url: str, output_path: Path, title: str) -> bool:
        """Download video using curl with progress display"""
        if not CURL_AVAILABLE:
            return False
        
        self._print_rich(f"[cyan]⬇ Downloading: {title}[/cyan]")
        
        cmd = [
            'curl', '-L', '-k',
            '--max-time', '3600',
            '--tlsv1.2',
            '-H', f'User-Agent: {self.current_user_agent or self._get_random_user_agent()}',
            '-H', 'Referer: https://beeg.com/',
            '-o', str(output_path),
            '--progress-bar',
            video_url
        ]
        
        try:
            result = subprocess.run(cmd, timeout=3600)
            if result.returncode == 0 and output_path.exists() and output_path.stat().st_size > 0:
                return True
        except subprocess.TimeoutExpired:
            self._print_rich("[red]✗ Download timed out[/red]")
        except Exception as e:
            self._print_rich(f"[red]✗ Download error: {str(e)}[/red]")
        
        return False
    
    def _download_with_ffmpeg(self, video_url: str, output_path: Path, title: str) -> bool:
        """Download HLS stream using ffmpeg"""
        ffmpeg_path = shutil.which('ffmpeg')
        if not ffmpeg_path:
            self._print_rich("[yellow]⚠ ffmpeg not found[/yellow]")
            return False
        
        self._print_rich(f"[cyan]⬇ Downloading HLS stream: {title}[/cyan]")
        
        # Build headers string for ffmpeg
        headers = (
            f"User-Agent: {self.current_user_agent or self._get_random_user_agent()}\r\n"
            f"Referer: https://beeg.com/\r\n"
            f"Origin: https://beeg.com\r\n"
        )
        
        cmd = [
            ffmpeg_path,
            '-y',  # Overwrite output
            '-protocol_whitelist', 'file,http,https,tcp,tls,crypto',
            '-headers', headers,
            '-tls_verify', '0',  # Disable TLS verification
            '-i', video_url,
            '-c', 'copy',  # Copy streams without re-encoding
            '-bsf:a', 'aac_adtstoasc',
            '-movflags', '+faststart',
            str(output_path)
        ]
        
        try:
            # Set environment to use TLS 1.2
            env = os.environ.copy()
            env['OPENSSL_CONF'] = ''  # Clear any OpenSSL config that might interfere
            
            # Run ffmpeg with progress output
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True,
                env=env
            )
            
            # Monitor progress
            stderr_output = []
            while True:
                line = process.stderr.readline()
                if not line and process.poll() is not None:
                    break
                if line:
                    stderr_output.append(line)
                    # Show progress updates
                    if 'time=' in line:
                        # Extract time progress
                        match = re.search(r'time=(\d+:\d+:\d+)', line)
                        if match:
                            print(f"\r  Progress: {match.group(1)}", end='', flush=True)
            
            print()  # New line after progress
            
            if process.returncode == 0 and output_path.exists() and output_path.stat().st_size > 0:
                return True
            else:
                if stderr_output:
                    error_lines = [l for l in stderr_output[-5:] if l.strip()]
                    self._print_rich(f"[yellow]ffmpeg output: {''.join(error_lines)[-200:]}[/yellow]")
                return False
                
        except subprocess.TimeoutExpired:
            self._print_rich("[red]✗ Download timed out[/red]")
            process.kill()
        except Exception as e:
            self._print_rich(f"[red]✗ ffmpeg error: {str(e)}[/red]")
        
        return False
    
    def _download_hls_with_ytdlp(self, video_url: str, output_path: Path, title: str) -> bool:
        """Download HLS stream using yt-dlp (which handles TLS better)"""
        if not YT_DLP_AVAILABLE:
            return False
        
        self._print_rich(f"[cyan]⬇ Downloading with yt-dlp: {title}[/cyan]")
        
        ydl_opts = {
            'format': 'best',
            'outtmpl': str(output_path),
            'nocheckcertificate': True,
            'geo_bypass': True,
            'quiet': True,
            'no_warnings': True,
            'retries': 5,
            'fragment_retries': 5,
            'http_headers': {
                'User-Agent': self.current_user_agent or self._get_random_user_agent(),
                'Referer': 'https://beeg.com/',
                'Origin': 'https://beeg.com',
            },
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([video_url])
            
            if output_path.exists() and output_path.stat().st_size > 0:
                return True
        except Exception as e:
            self._print_rich(f"[yellow]⚠ yt-dlp error: {str(e)[:100]}[/yellow]")
        
        return False
    
    def _download_hls_segments(self, video_url: str, output_path: Path, title: str) -> bool:
        """Download HLS stream by fetching segments with curl and merging with ffmpeg"""
        import tempfile
        
        self._print_rich(f"[cyan]⬇ Downloading HLS segments: {title}[/cyan]")
        
        # Fetch the m3u8 playlist
        playlist_content = self._curl_fetch(video_url, {
            'Accept': 'application/vnd.apple.mpegurl, */*',
        })
        
        if not playlist_content:
            self._print_rich("[yellow]⚠ Failed to fetch HLS playlist[/yellow]")
            return False
        
        # Parse the playlist and extract segment URLs
        lines = playlist_content.strip().split('\n')
        segments = []
        base_url = video_url.rsplit('/', 1)[0] + '/'
        
        for line in lines:
            line = line.strip()
            if line and not line.startswith('#'):
                if line.startswith('http'):
                    segments.append(line)
                elif line.startswith('/'):
                    # Relative URL starting with /
                    segments.append(f"https://video.beeg.com{line}")
                else:
                    # Relative URL
                    segments.append(f"{base_url}{line}")
        
        if not segments:
            self._print_rich("[yellow]⚠ No segments found in playlist[/yellow]")
            return False
        
        self._print_rich(f"[cyan]  Found {len(segments)} segments to download[/cyan]")
        
        # Create temp directory for segments
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            segment_files = []
            
            # Download each segment
            for i, segment_url in enumerate(segments):
                segment_file = temp_path / f"segment_{i:04d}.ts"
                
                # Show progress
                progress = (i + 1) / len(segments) * 100
                print(f"\r  Downloading segment {i+1}/{len(segments)} ({progress:.1f}%)", end='', flush=True)
                
                # Download segment with curl
                cmd = [
                    'curl', '-s', '-L', '-k',
                    '--max-time', '60',
                    '--tlsv1.2',
                    '-H', f'User-Agent: {self.current_user_agent or self._get_random_user_agent()}',
                    '-H', 'Referer: https://beeg.com/',
                    '-H', 'Origin: https://beeg.com',
                    '-o', str(segment_file),
                    segment_url
                ]
                
                try:
                    result = subprocess.run(cmd, capture_output=True, timeout=120)
                    if result.returncode == 0 and segment_file.exists() and segment_file.stat().st_size > 0:
                        segment_files.append(segment_file)
                    else:
                        # Try to continue even if some segments fail
                        self._print_rich(f"\n[yellow]⚠ Failed to download segment {i+1}[/yellow]")
                except Exception as e:
                    self._print_rich(f"\n[yellow]⚠ Error downloading segment {i+1}: {str(e)[:50]}[/yellow]")
            
            print()  # New line after progress
            
            if len(segment_files) < len(segments) * 0.9:  # Less than 90% success
                self._print_rich(f"[yellow]⚠ Too many failed segments ({len(segments) - len(segment_files)}/{len(segments)})[/yellow]")
                return False
            
            # Create concat file for ffmpeg
            concat_file = temp_path / "concat.txt"
            with open(concat_file, 'w') as f:
                for seg_file in segment_files:
                    f.write(f"file '{seg_file}'\n")
            
            # Merge segments with ffmpeg
            ffmpeg_path = shutil.which('ffmpeg')
            if not ffmpeg_path:
                self._print_rich("[yellow]⚠ ffmpeg not found for merging[/yellow]")
                return False
            
            self._print_rich("[cyan]  Merging segments...[/cyan]")
            
            cmd = [
                ffmpeg_path,
                '-y',
                '-f', 'concat',
                '-safe', '0',
                '-i', str(concat_file),
                '-c', 'copy',
                '-movflags', '+faststart',
                str(output_path)
            ]
            
            try:
                result = subprocess.run(cmd, capture_output=True, timeout=300)
                if result.returncode == 0 and output_path.exists() and output_path.stat().st_size > 0:
                    return True
                else:
                    self._print_rich(f"[yellow]ffmpeg merge error: {result.stderr.decode()[-200:]}[/yellow]")
            except Exception as e:
                self._print_rich(f"[red]✗ Merge error: {str(e)}[/red]")
        
        return False
    
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
        
        # First try yt-dlp
        try:
            if YT_DLP_AVAILABLE:
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
                        return qualities
        
        except Exception as e:
            error_str = str(e).lower()
            if 'ssl' in error_str or 'eof' in error_str or 'connection' in error_str:
                self._print_rich("[yellow]⚠ SSL/Connection issue detected, using fallback method...[/yellow]")
                self.use_fallback = True
            else:
                self._print_rich(f"[yellow]⚠ Could not extract quality info: {str(e)}[/yellow]")
        
        # Fallback: Use API via curl
        if CURL_AVAILABLE:
            video_id = self.extract_video_id(url)
            if video_id:
                api_data = self._fetch_video_info_api(video_id)
                if api_data:
                    self.use_fallback = True
                    qualities = self._extract_qualities_from_api(api_data)
        
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
    
    def _get_ydl_opts(self, quality: str = "best", output_format: str = None) -> Dict[str, Any]:
        output_dir = self.downloader.output_dir if hasattr(self.downloader, 'output_dir') else Path.home() / "Downloads"
        
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
            },
        }
        
        if output_format in [None, 'mp4']:
            ydl_opts['postprocessors'].extend([
                {'key': 'FFmpegMetadata', 'add_metadata': True},
                {'key': 'EmbedThumbnail', 'already_have_thumbnail': False},
            ])
        
        return ydl_opts
    
    def download(self, url: str, quality: str = "best", output_format: str = None,
                 interactive: bool = True) -> Optional[Dict[str, Any]]:
        
        download_info = f"""[bold cyan]Platform:[/bold cyan] [yellow]Beeg[/yellow]
[bold cyan]URL:[/bold cyan] [blue]{url[:60]}...[/blue]"""
        
        self._print_panel(download_info, title="▸ Beeg Download", border_style="orange1")
        
        # Reset fallback flag
        self.use_fallback = False
        
        if interactive:
            self._print_rich("[cyan]⌕ Fetching available qualities...[/cyan]")
            qualities = self._get_available_qualities(url)
            if qualities:
                quality = self._display_qualities(qualities)
        
        self._print_rich(f"[cyan]⌕ Selected quality: {quality}[/cyan]")
        
        # Use fallback method if SSL issues were detected or yt-dlp is not available
        if self.use_fallback or not YT_DLP_AVAILABLE:
            return self._download_video_fallback(url, quality, output_format)
        
        # Try yt-dlp first
        result = self._download_video(url, quality, output_format)
        
        # If yt-dlp failed due to SSL, try fallback
        if result is None and CURL_AVAILABLE:
            self._print_rich("[yellow]⚠ Trying fallback download method...[/yellow]")
            return self._download_video_fallback(url, quality, output_format)
        
        return result
    
    def _download_video_fallback(self, url: str, quality: str = "best",
                                  output_format: str = None) -> Optional[Dict[str, Any]]:
        """Download video using API + curl/ffmpeg fallback method"""
        video_id = self.extract_video_id(url)
        if not video_id:
            self._print_rich("[red]✗ Could not extract video ID from URL[/red]")
            return None
        
        self._print_rich("[cyan]⌕ Using fallback download method...[/cyan]")
        
        # Fetch video info from API
        api_data = self._fetch_video_info_api(video_id)
        if not api_data:
            self._print_rich("[red]✗ Could not fetch video information from API[/red]")
            return None
        
        # Get video URL for selected quality
        video_info = self._get_video_url_from_api(api_data, quality)
        if not video_info:
            self._print_rich("[red]✗ Could not find video URL in API response[/red]")
            return None
        
        title = video_info['title']
        duration = video_info['duration']
        video_url = video_info['video_url']
        selected_quality = video_info['quality']
        is_hls = video_info['is_hls']
        
        # Display video info
        duration_str = f"{duration // 60}:{duration % 60:02d}" if duration else "Unknown"
        info_display = f"""[bold]Title:[/bold] {title}
[bold]Duration:[/bold] {duration_str}
[bold]Quality:[/bold] {selected_quality}"""
        
        self._print_panel(info_display, title="📹 Video Info", border_style="green")
        
        # Prepare output path
        output_dir = self.downloader.output_dir if hasattr(self.downloader, 'output_dir') else Path.home() / "Downloads"
        safe_title = sanitize_filename(title)[:100]
        ext = 'mp4'
        output_path = output_dir / f"{safe_title}.{ext}"
        
        # Ensure output directory exists
        output_dir.mkdir(parents=True, exist_ok=True)
        
        self._print_rich("[cyan]⬇ Starting download...[/cyan]")
        
        success = False
        
        # Try yt-dlp first for HLS (better TLS handling)
        if is_hls and YT_DLP_AVAILABLE:
            success = self._download_hls_with_ytdlp(video_url, output_path, title)
        
        # Try ffmpeg for HLS streams
        if not success and is_hls:
            success = self._download_with_ffmpeg(video_url, output_path, title)
        
        # Try segment-based download (curl + ffmpeg merge)
        if not success and is_hls and CURL_AVAILABLE:
            success = self._download_hls_segments(video_url, output_path, title)
        
        if not success:
            # Try direct download with curl
            success = self._download_with_curl(video_url, output_path, title)
        
        if success:
            file_size = output_path.stat().st_size / (1024 * 1024)  # MB
            self._print_rich(f"[green]✓ Successfully downloaded: {title}[/green]")
            self._print_rich(f"[green]  📁 Saved to: {output_path}[/green]")
            self._print_rich(f"[green]  📦 Size: {file_size:.1f} MB[/green]")
            
            return {
                'title': title,
                'duration': duration,
                'url': url,
                'output_path': str(output_path),
                'success': True
            }
        else:
            self._print_rich("[red]✗ Failed to download video[/red]")
            return None
    
    def _download_video(self, url: str, quality: str = "best",
                        output_format: str = None) -> Optional[Dict[str, Any]]:
        """Download video using yt-dlp"""
        if not YT_DLP_AVAILABLE:
            return None
        
        try:
            ydl_opts = self._get_ydl_opts(quality, output_format)
            
            self._print_rich("[cyan]⌕ Extracting video information...[/cyan]")
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                
                if not info:
                    self._print_rich("[red]✗ Could not extract video information[/red]")
                    return None
                
                title = info.get('title', 'Unknown')
                duration = info.get('duration', 0)
                
                duration_str = f"{duration // 60}:{duration % 60:02d}" if duration else "Unknown"
                video_info = f"""[bold]Title:[/bold] {title}
[bold]Duration:[/bold] {duration_str}"""
                
                self._print_panel(video_info, title="📹 Video Info", border_style="green")
                
                self._print_rich("[cyan]⬇ Starting download...[/cyan]")
                ydl.download([url])
                
                self._print_rich(f"[green]✓ Successfully downloaded: {title}[/green]")
                
                return {
                    'title': title,
                    'duration': duration,
                    'url': url,
                    'success': True
                }
                
        except Exception as e:
            error_str = str(e).lower()
            if 'ssl' in error_str or 'eof' in error_str or 'connection' in error_str or 'tls' in error_str:
                self._print_rich(f"[yellow]⚠ SSL/Connection error: {str(e)[:100]}[/yellow]")
                self.use_fallback = True
            else:
                self._print_rich(f"[red]✗ Error downloading video: {str(e)}[/red]")
            return None
    
    def search_and_download(self, url: str, interactive: bool = True) -> Optional[Dict[str, Any]]:
        if not self.is_beeg_url(url):
            self._print_rich(f"[red]Error: Not a valid Beeg URL[/red]")
            return None
        
        return self.download(url, quality="best", interactive=interactive)
