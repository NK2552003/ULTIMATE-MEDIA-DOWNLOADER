#!/usr/bin/env python3
"""
Pornhub Handler Module
Handles downloading videos from Pornhub using yt-dlp with proper configuration
and fallback methods for various content types.
"""

import os
import re
import warnings
from pathlib import Path
from typing import Optional, Dict, Any, List
from urllib.parse import urlparse, urljoin, parse_qs

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


class PornhubHandler:
    """Handles Pornhub video downloads"""
    
    # Supported domains
    SUPPORTED_DOMAINS = [
        'pornhub.com',
        'pornhubpremium.com',
        'www.pornhub.com',
        'www.pornhubpremium.com',
    ]
    
    def __init__(self, downloader):
        """Initialize Pornhub handler with reference to main downloader
        
        Args:
            downloader: Reference to UltimateMediaDownloader instance
        """
        self.downloader = downloader
        self.console = Console() if RICH_AVAILABLE else None
        self.session = None
        
        # Initialize session with appropriate cookies
        if REQUESTS_AVAILABLE:
            self._init_session()
    
    def _init_session(self):
        """Initialize requests session with required cookies and headers"""
        self.session = requests.Session()
        
        # Set cookies to bypass age verification
        self.session.cookies.update({
            'age_verified': '1',
            'accessAgeDisclaimerPH': '1',
            'accessPH': '1',
        })
        
        # Set user agent
        self.session.headers.update({
            'User-Agent': self.downloader._get_random_user_agent() if hasattr(self.downloader, '_get_random_user_agent') else 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
        })
    
    @classmethod
    def is_pornhub_url(cls, url: str) -> bool:
        """Check if URL is a Pornhub URL
        
        Args:
            url: URL to check
            
        Returns:
            True if URL is from Pornhub
        """
        url_lower = url.lower()
        return any(domain in url_lower for domain in cls.SUPPORTED_DOMAINS)
    
    @classmethod
    def fix_url(cls, url: str) -> str:
        """Normalize Pornhub URL
        
        Args:
            url: Original URL
            
        Returns:
            Normalized URL
        """
        # Handle custom URL formats
        if 'pornhub_gif_' in url:
            url = f'https://www.pornhub.com/gif/{url.replace("pornhub_gif_", "")}'
        elif 'pornhub_album_' in url:
            url = f'https://www.pornhub.com/album/{url.replace("pornhub_album_", "")}'
        elif 'pornhub_' in url:
            url = f'https://www.pornhub.com/view_video.php?viewkey={url.replace("pornhub_", "")}'
        
        # Handle authentication redirect
        if '/authenticate/goToLoggedIn' in url:
            parsed = urlparse(url)
            params = parse_qs(parsed.query)
            if 'url' in params:
                url = urljoin(url, params['url'][0])
        
        return url
    
    def get_content_type(self, url: str) -> str:
        """Determine the type of Pornhub content from URL
        
        Args:
            url: Pornhub URL
            
        Returns:
            Content type: 'video', 'gif', 'album', 'photo', 'playlist', 'channel', 'model', 'pornstar', 'user'
        """
        url_lower = url.lower()
        
        if '/gif/' in url_lower:
            return 'gif'
        elif '/album/' in url_lower:
            return 'album'
        elif '/photo/' in url_lower:
            return 'photo'
        elif '/playlist/' in url_lower:
            return 'playlist'
        elif '/channels/' in url_lower:
            return 'channel'
        elif '/model/' in url_lower:
            return 'model'
        elif '/pornstar/' in url_lower:
            return 'pornstar'
        elif '/users/' in url_lower:
            return 'user'
        elif 'viewkey=' in url_lower or '/view_video' in url_lower or '/embed/' in url_lower:
            return 'video'
        else:
            return 'unknown'
    
    def extract_video_id(self, url: str) -> Optional[str]:
        """Extract video ID from Pornhub URL
        
        Args:
            url: Pornhub URL
            
        Returns:
            Video ID or None
        """
        # Match viewkey parameter
        match = re.search(r'viewkey=(\w+)', url, re.I)
        if match:
            return match.group(1)
        
        # Match embed URL
        match = re.search(r'/embed/(\w+)', url, re.I)
        if match:
            return match.group(1)
        
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
        """Download video from Pornhub
        
        Args:
            url: Pornhub video URL
            quality: Video quality (best, 1080p, 720p, 480p, etc.)
            output_format: Output format (mp4, etc.)
            interactive: Whether to prompt for options
            
        Returns:
            Dictionary with download info on success, None on failure
        """
        if not YT_DLP_AVAILABLE:
            self._print_rich("[red]Error: yt-dlp is required for Pornhub downloads[/red]")
            return None
        
        # Normalize URL
        url = self.fix_url(url)
        
        # Determine content type
        content_type = self.get_content_type(url)
        
        # Show download info panel
        download_info = f"""[bold cyan]Platform:[/bold cyan] [yellow]PORNHUB[/yellow]
[bold cyan]Content Type:[/bold cyan] [green]{content_type.upper()}[/green]
[bold cyan]Quality:[/bold cyan] [magenta]{quality}[/magenta]"""
        
        self._print_panel(download_info, title="▸ Pornhub Download", border_style="red")
        
        # Handle different content types
        if content_type == 'video' or content_type == 'gif':
            return self._download_video(url, quality, output_format)
        elif content_type in ['playlist', 'channel', 'model', 'pornstar', 'user']:
            return self._download_collection(url, content_type, quality, output_format, interactive)
        elif content_type == 'album':
            return self._download_album(url)
        elif content_type == 'photo':
            return self._download_photo(url)
        else:
            # Try video download as fallback
            self._print_rich(f"[yellow]Unknown content type, attempting video download...[/yellow]")
            return self._download_video(url, quality, output_format)
    
    def _get_ydl_opts(self, quality: str = "best", output_format: str = None) -> Dict[str, Any]:
        """Get yt-dlp options for Pornhub
        
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
            # Cookies for age verification
            'cookiefile': None,  # Will add browser cookies if needed
            'http_headers': {
                'User-Agent': self.session.headers.get('User-Agent') if self.session else 'Mozilla/5.0',
                'Cookie': 'age_verified=1; accessAgeDisclaimerPH=1; accessPH=1',
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
            if 'private' in error_msg.lower() or 'premium' in error_msg.lower():
                self._print_rich("[red]✗ This video requires a premium account or is private[/red]")
            elif 'removed' in error_msg.lower() or 'deleted' in error_msg.lower():
                self._print_rich("[red]✗ This video has been removed[/red]")
            else:
                self._print_rich(f"[red]✗ Download error: {error_msg}[/red]")
            return None
        except Exception as e:
            self._print_rich(f"[red]✗ Error downloading video: {str(e)}[/red]")
            return None
    
    def _download_collection(self, url: str, content_type: str, quality: str = "best",
                             output_format: str = None, interactive: bool = True) -> Optional[Dict[str, Any]]:
        """Download videos from a collection (playlist, channel, model, etc.)
        
        Args:
            url: Collection URL
            content_type: Type of collection
            quality: Video quality
            output_format: Output format
            interactive: Whether to prompt for options
            
        Returns:
            Download info dict or None
        """
        try:
            ydl_opts = self._get_ydl_opts(quality, output_format)
            ydl_opts['noplaylist'] = False  # Allow playlist extraction
            ydl_opts['playlistend'] = 50  # Limit to 50 videos by default
            
            # Extract collection info
            self._print_rich(f"[cyan]⌕ Extracting {content_type} information...[/cyan]")
            
            with yt_dlp.YoutubeDL({**ydl_opts, 'extract_flat': True}) as ydl:
                info = ydl.extract_info(url, download=False)
                
                if not info:
                    self._print_rich(f"[red]✗ Could not extract {content_type} information[/red]")
                    return None
                
                entries = info.get('entries', [])
                total_videos = len(entries) if entries else 0
                
                if total_videos == 0:
                    self._print_rich(f"[yellow]⚠ No videos found in this {content_type}[/yellow]")
                    return None
                
                collection_title = info.get('title', content_type.title())
                
                # Display collection info
                collection_info = f"""[bold]Title:[/bold] {collection_title}
[bold]Videos:[/bold] {total_videos}
[bold]Type:[/bold] {content_type.title()}"""
                
                self._print_panel(collection_info, title=f"📁 {content_type.title()} Info", border_style="blue")
                
                if interactive:
                    # Ask user how many to download
                    try:
                        max_downloads = input(f"How many videos to download? (1-{total_videos}, default: 10): ").strip()
                        if max_downloads:
                            ydl_opts['playlistend'] = int(max_downloads)
                        else:
                            ydl_opts['playlistend'] = min(10, total_videos)
                    except (ValueError, KeyboardInterrupt):
                        ydl_opts['playlistend'] = min(10, total_videos)
                
                # Download the collection
                self._print_rich(f"[cyan]⬇ Downloading up to {ydl_opts['playlistend']} videos...[/cyan]")
                
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([url])
                
                self._print_rich(f"[green]✓ Successfully downloaded from: {collection_title}[/green]")
                
                return {
                    'title': collection_title,
                    'type': content_type,
                    'total_videos': total_videos,
                    'url': url,
                    'success': True
                }
                
        except Exception as e:
            self._print_rich(f"[red]✗ Error downloading {content_type}: {str(e)}[/red]")
            return None
    
    def _download_album(self, url: str) -> Optional[Dict[str, Any]]:
        """Download photos from an album
        
        Args:
            url: Album URL
            
        Returns:
            Download info dict or None
        """
        if not REQUESTS_AVAILABLE or not BS4_AVAILABLE:
            self._print_rich("[red]Error: requests and BeautifulSoup are required for album downloads[/red]")
            return None
        
        try:
            self._print_rich("[cyan]⌕ Extracting album information...[/cyan]")
            
            response = self.session.get(url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract album ID
            album_id_match = re.search(r'/album/(\d+)', url)
            album_id = album_id_match.group(1) if album_id_match else 'unknown'
            
            # Find title
            title_elem = soup.find('h1', class_='photoAlbumTitleV2')
            title = title_elem.text.strip() if title_elem else f'album_{album_id}'
            
            # Find photo blocks
            photo_blocks = soup.find_all('div', class_='photoAlbumListBlock')
            
            if not photo_blocks:
                self._print_rich("[yellow]⚠ No photos found in this album[/yellow]")
                return None
            
            # Create album directory
            output_dir = self.downloader.output_dir if hasattr(self.downloader, 'output_dir') else Path.home() / "Downloads"
            album_dir = output_dir / sanitize_filename(title)
            album_dir.mkdir(parents=True, exist_ok=True)
            
            self._print_panel(f"[bold]Title:[/bold] {title}\n[bold]Photos:[/bold] {len(photo_blocks)}", 
                            title="📷 Album Info", border_style="magenta")
            
            downloaded = 0
            for i, block in enumerate(photo_blocks, 1):
                try:
                    link = block.find('a')
                    if link and 'href' in link.attrs:
                        photo_url = urljoin(url, link['href'])
                        photo_info = self._download_photo(photo_url, album_dir)
                        if photo_info:
                            downloaded += 1
                            print(f"  [{i}/{len(photo_blocks)}] Downloaded")
                except Exception as e:
                    print(f"  [{i}/{len(photo_blocks)}] Failed: {str(e)}")
            
            self._print_rich(f"[green]✓ Downloaded {downloaded}/{len(photo_blocks)} photos from: {title}[/green]")
            
            return {
                'title': title,
                'type': 'album',
                'total_photos': len(photo_blocks),
                'downloaded': downloaded,
                'url': url,
                'success': True
            }
            
        except Exception as e:
            self._print_rich(f"[red]✗ Error downloading album: {str(e)}[/red]")
            return None
    
    def _download_photo(self, url: str, output_dir: Path = None) -> Optional[Dict[str, Any]]:
        """Download a single photo
        
        Args:
            url: Photo page URL
            output_dir: Output directory (optional)
            
        Returns:
            Download info dict or None
        """
        if not REQUESTS_AVAILABLE or not BS4_AVAILABLE:
            self._print_rich("[red]Error: requests and BeautifulSoup are required for photo downloads[/red]")
            return None
        
        try:
            if output_dir is None:
                output_dir = self.downloader.output_dir if hasattr(self.downloader, 'output_dir') else Path.home() / "Downloads"
            
            response = self.session.get(url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract photo ID
            photo_id_match = re.search(r'/photo/(\d+)', url)
            photo_id = photo_id_match.group(1) if photo_id_match else 'unknown'
            
            # Find the image section
            section = soup.find('div', id='photoImageSection')
            if not section:
                return None
            
            img = section.find('img')
            if not img or 'src' not in img.attrs:
                return None
            
            img_url = img['src']
            
            # Download the image
            img_response = self.session.get(img_url)
            img_response.raise_for_status()
            
            # Determine extension
            ext = '.jpg'
            if 'content-type' in img_response.headers:
                ct = img_response.headers['content-type']
                if 'png' in ct:
                    ext = '.png'
                elif 'gif' in ct:
                    ext = '.gif'
                elif 'webp' in ct:
                    ext = '.webp'
            
            # Save the image
            filename = f'photo_{photo_id}{ext}'
            filepath = output_dir / filename
            
            with open(filepath, 'wb') as f:
                f.write(img_response.content)
            
            return {
                'id': photo_id,
                'url': img_url,
                'filepath': str(filepath),
                'success': True
            }
            
        except Exception as e:
            return None
    
    def search_and_download(self, url: str, interactive: bool = True) -> Optional[Dict[str, Any]]:
        """Main entry point for downloading Pornhub content
        
        Args:
            url: Pornhub URL
            interactive: Whether to prompt for options
            
        Returns:
            Download info on success, None on failure
        """
        # Validate URL
        if not self.is_pornhub_url(url):
            self._print_rich(f"[red]Error: Not a valid Pornhub URL[/red]")
            return None
        
        # Download with default settings
        return self.download(url, quality="best", interactive=interactive)
