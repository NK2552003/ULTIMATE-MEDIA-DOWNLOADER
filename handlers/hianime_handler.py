#!/usr/bin/env python3
"""
HiAnime Handler Module
Downloads anime by extracting info from HiAnime URLs and fetching streams from AllAnime API.
Uses AllAnime's GraphQL API which provides direct video URLs.
"""

import os
import re
import json
import time
import warnings
from pathlib import Path
from typing import Optional, Dict, Any, List, Tuple
from urllib.parse import urlparse, parse_qs, quote

warnings.filterwarnings('ignore')

try:
    import cloudscraper
    CLOUDSCRAPER_AVAILABLE = True
except ImportError:
    CLOUDSCRAPER_AVAILABLE = False

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

try:
    import yt_dlp
    YT_DLP_AVAILABLE = True
except ImportError:
    YT_DLP_AVAILABLE = False

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich.prompt import Prompt, Confirm
    from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, DownloadColumn, TransferSpeedColumn, TimeRemainingColumn
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

try:
    from utils.utils import sanitize_filename
except ImportError:
    def sanitize_filename(name):
        return re.sub(r'[<>:"/\\|?*]', '', name).strip()

# AllAnime API - Working GraphQL endpoint
ALLANIME_API = "https://api.allanime.day/api"
ALLANIME_REFERER = "https://allanime.to/"


class HiAnimeHandler:
    """
    HiAnime Handler - Downloads anime using AllAnime API.
    """
    
    SUPPORTED_DOMAINS = [
        'hianime.to', 'hianime.sx', 'hianime.mn',
        'aniwatch.to', 'zoro.to', 'kaido.to',
    ]
    
    def __init__(self, downloader):
        self.downloader = downloader
        self.console = Console() if RICH_AVAILABLE else None
        self.scraper = self._init_scraper()
    
    def _init_scraper(self):
        """Initialize HTTP client"""
        if CLOUDSCRAPER_AVAILABLE:
            scraper = cloudscraper.create_scraper(
                browser={'browser': 'chrome', 'platform': 'darwin', 'desktop': True}
            )
        elif REQUESTS_AVAILABLE:
            scraper = requests.Session()
        else:
            return None
        
        scraper.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json',
            'Accept-Language': 'en-US,en;q=0.9',
            'Referer': ALLANIME_REFERER,
            'Origin': 'https://allanime.to',
        })
        return scraper
    
    @classmethod
    def is_hianime_url(cls, url: str) -> bool:
        """Check if URL is a HiAnime URL"""
        return any(domain in url.lower() for domain in cls.SUPPORTED_DOMAINS)
    
    def _status(self, message: str, style: str = None):
        """Print status message"""
        if RICH_AVAILABLE and self.console:
            self.console.print(message, style=style) if style else self.console.print(message)
        else:
            print(re.sub(r'\[.*?\]', '', str(message)))
    
    def _extract_from_hianime_url(self, url: str) -> Dict[str, Any]:
        """Extract anime name from HiAnime URL"""
        info = {'anime_name': None, 'anime_slug': None}
        
        parsed = urlparse(url)
        match = re.search(r'/watch/([^?/]+)', parsed.path)
        if match:
            slug = match.group(1)
            info['anime_slug'] = slug
            name = re.sub(r'-\d+$', '', slug)
            info['anime_name'] = name.replace('-', ' ').title()
        
        return info
    
    def _decode_allanime_url(self, encoded: str) -> str:
        """Decode AllAnime's encoded URLs"""
        if not encoded.startswith('--'):
            return encoded
        
        encoded = encoded[2:]
        result = []
        key = 56
        
        for i in range(0, len(encoded), 2):
            try:
                byte = int(encoded[i:i+2], 16)
                result.append(chr(byte ^ key))
            except:
                break
        
        return ''.join(result)
    
    def _search_allanime(self, anime_name: str) -> List[Dict[str, Any]]:
        """Search for anime on AllAnime"""
        results = []
        
        query = """
        query($search: SearchInput, $limit: Int, $page: Int, $translationType: VaildTranslationTypeEnumType) {
            shows(search: $search, limit: $limit, page: $page, translationType: $translationType) {
                edges {
                    _id
                    name
                    englishName
                    availableEpisodes
                }
            }
        }
        """
        
        variables = {
            "search": {"query": anime_name},
            "limit": 10,
            "page": 1,
            "translationType": "sub"
        }
        
        try:
            params = {'query': query, 'variables': json.dumps(variables)}
            response = self.scraper.get(ALLANIME_API, params=params, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                shows = data.get('data', {}).get('shows', {}).get('edges', [])
                
                for show in shows:
                    results.append({
                        'id': show.get('_id'),
                        'name': show.get('name', ''),
                        'english_name': show.get('englishName', ''),
                        'episodes': show.get('availableEpisodes', {}),
                    })
        except Exception:
            pass
        
        return results
    
    def _get_episode_sources(self, show_id: str, episode_num: str, translation: str = "sub") -> List[Dict[str, Any]]:
        """Get streaming sources for a specific episode"""
        sources = []
        
        query = """
        query($showId: String!, $translationType: VaildTranslationTypeEnumType!, $episodeString: String!) {
            episode(showId: $showId, translationType: $translationType, episodeString: $episodeString) {
                episodeString
                sourceUrls
            }
        }
        """
        
        variables = {
            "showId": show_id,
            "translationType": translation,
            "episodeString": episode_num
        }
        
        try:
            params = {'query': query, 'variables': json.dumps(variables)}
            response = self.scraper.get(ALLANIME_API, params=params, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                episode = data.get('data', {}).get('episode', {})
                if episode:
                    source_urls = episode.get('sourceUrls', [])
                    
                    for source in source_urls:
                        source_url = source.get('sourceUrl', '')
                        if source_url.startswith('--'):
                            source_url = self._decode_allanime_url(source_url)
                        
                        sources.append({
                            'url': source_url,
                            'name': source.get('sourceName', 'Unknown'),
                            'type': source.get('type', 'unknown'),
                            'priority': source.get('priority', 0),
                        })
        except Exception:
            pass
        
        sources.sort(key=lambda x: x.get('priority', 0), reverse=True)
        return sources
    
    def _download_with_progress(self, url: str, output_file: Path, episode_info: str = "") -> bool:
        """Download video with rich progress bar"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
                'Referer': ALLANIME_REFERER,
            }
            
            response = self.scraper.get(url, headers=headers, stream=True, timeout=60)
            
            if response.status_code != 200:
                return False
            
            total_size = int(response.headers.get('content-length', 0))
            
            if RICH_AVAILABLE and self.console:
                with Progress(
                    SpinnerColumn(),
                    TextColumn("[bold blue]{task.description}"),
                    BarColumn(bar_width=40),
                    "[progress.percentage]{task.percentage:>3.1f}%",
                    "•",
                    DownloadColumn(),
                    "•",
                    TransferSpeedColumn(),
                    "•",
                    TimeRemainingColumn(),
                    console=self.console,
                    transient=False
                ) as progress:
                    task = progress.add_task(episode_info or "Downloading", total=total_size)
                    
                    with open(output_file, 'wb') as f:
                        for chunk in response.iter_content(chunk_size=32768):
                            if chunk:
                                f.write(chunk)
                                progress.update(task, advance=len(chunk))
            else:
                downloaded = 0
                with open(output_file, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=32768):
                        if chunk:
                            f.write(chunk)
                            downloaded += len(chunk)
                            if total_size > 0:
                                percent = (downloaded / total_size) * 100
                                print(f"\r{episode_info} - {percent:.1f}%", end='', flush=True)
                print()
            
            return output_file.exists() and output_file.stat().st_size > 0
                    
        except Exception:
            return False
    
    def _download_with_yt_dlp(self, url: str, output_dir: Path, title: str, 
                               quality: str = "best", referer: str = None) -> bool:
        """Download video using yt-dlp"""
        if not YT_DLP_AVAILABLE:
            return False
        
        if quality == "best" or quality == "1080":
            fmt = "bestvideo+bestaudio/best"
        else:
            height = int(quality) if quality.isdigit() else 720
            fmt = f"bestvideo[height<={height}]+bestaudio/best[height<={height}]/best"
        
        outtmpl = str(output_dir / f'{sanitize_filename(title)}.%(ext)s')
        
        ydl_opts = {
            'format': fmt,
            'outtmpl': outtmpl,
            'merge_output_format': 'mp4',
            'nocheckcertificate': True,
            'geo_bypass': True,
            'retries': 5,
            'quiet': True,
            'no_warnings': True,
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
                'Referer': referer or ALLANIME_REFERER,
            },
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                return ydl.download([url]) == 0
        except Exception:
            return False
    
    def _try_download_episode(self, sources: List[Dict], output_dir: Path, 
                               anime_title: str, episode_num: str, quality: str) -> Optional[Path]:
        """Try to download episode from available sources. Returns file path on success."""
        file_title = f"{anime_title} - Episode {episode_num}"
        episode_info = f"Episode {episode_num}"
        
        # Priority order: direct MP4 sources first (usually best quality)
        # Yt-mp4/Vid-mp4 from fast4speed provide reliable 1080p
        priority_sources = ['Yt-mp4', 'Vid-mp4', 'Luf-Mp4', 'S-mp4', 'Mp4', 'Default']
        
        def get_priority(s):
            name = s.get('name', '')
            # Also consider API priority
            api_priority = s.get('priority', 0)
            if name in priority_sources:
                return (priority_sources.index(name), -api_priority)
            return (100, -api_priority)
        
        sources.sort(key=get_priority)
        
        for source in sources:
            url = source.get('url', '')
            source_type = source.get('type', '')
            
            if not url:
                continue
            
            if source_type == 'player' and 'fast4speed' in url:
                output_file = output_dir / f'{sanitize_filename(file_title)}.mp4'
                if self._download_with_progress(url, output_file, episode_info):
                    return output_file
            
            if self._download_with_yt_dlp(url, output_dir, file_title, quality):
                # Find the downloaded file
                for ext in ['mp4', 'mkv', 'webm']:
                    output_file = output_dir / f'{sanitize_filename(file_title)}.{ext}'
                    if output_file.exists():
                        return output_file
                return output_dir  # Return dir if file not found but download succeeded
        
        return None
    
    def _select_anime(self, results: List[Dict], anime_name: str) -> Optional[Dict]:
        """Let user select anime from search results"""
        if not results:
            return None
        
        anime_lower = anime_name.lower().strip()
        
        # Exact match
        for r in results:
            name_lower = r.get('name', '').lower().strip()
            eng_name = (r.get('english_name') or '').lower().strip()
            if anime_lower == name_lower or anime_lower == eng_name:
                if len(name_lower) >= len(anime_lower):
                    return r
        
        # Show selection menu
        self._status("\n[bold cyan]Select anime:[/bold cyan]")
        for i, r in enumerate(results[:8], 1):
            name = r.get('name', 'Unknown')
            eps = r.get('episodes', {})
            sub_eps = eps.get('sub', 0) if isinstance(eps, dict) else 0
            self._status(f"  [cyan]{i}.[/cyan] {name} [dim]({sub_eps} episodes)[/dim]")
        self._status(f"  [cyan]0.[/cyan] Cancel")
        
        if RICH_AVAILABLE:
            choice = Prompt.ask("Select", default="1")
        else:
            choice = input("\nSelect [1]: ").strip() or "1"
        
        try:
            idx = int(choice)
            if 1 <= idx <= min(8, len(results)):
                return results[idx - 1]
        except:
            pass
        
        return None
    
    def _prompt_download_mode(self, total_episodes: int) -> Tuple[str, List[int]]:
        """Ask user what to download"""
        self._status(f"\n[bold cyan]Download Options:[/bold cyan] [dim](Total: {total_episodes} episodes)[/dim]")
        self._status("  [cyan]1.[/cyan] Single Episode")
        self._status("  [cyan]2.[/cyan] Range of Episodes (e.g., 1-12)")
        self._status("  [cyan]3.[/cyan] Entire Season")
        self._status("  [cyan]0.[/cyan] Cancel")
        
        if RICH_AVAILABLE:
            choice = Prompt.ask("Select mode", choices=["0", "1", "2", "3"], default="1")
        else:
            choice = input("\nSelect mode [1]: ").strip() or "1"
        
        if choice == "0":
            return "cancel", []
        
        elif choice == "1":
            if RICH_AVAILABLE:
                ep_str = Prompt.ask("Episode number", default="1")
            else:
                ep_str = input("Episode number [1]: ").strip() or "1"
            
            try:
                ep = int(ep_str)
                if 1 <= ep <= total_episodes:
                    return "single", [ep]
                self._status(f"[yellow]Episode must be between 1 and {total_episodes}[/yellow]")
            except:
                self._status("[yellow]Invalid episode number[/yellow]")
            return "cancel", []
        
        elif choice == "2":
            if RICH_AVAILABLE:
                range_str = Prompt.ask("Enter range (e.g., 1-12)", default="1-12")
            else:
                range_str = input("Enter range (e.g., 1-12): ").strip() or "1-12"
            
            match = re.match(r'(\d+)\s*-\s*(\d+)', range_str)
            if match:
                start, end = int(match.group(1)), int(match.group(2))
                start = max(1, start)
                end = min(total_episodes, end)
                if start <= end:
                    return "range", list(range(start, end + 1))
            
            self._status("[yellow]Invalid range format[/yellow]")
            return "cancel", []
        
        elif choice == "3":
            if RICH_AVAILABLE:
                confirm = Confirm.ask(f"Download all {total_episodes} episodes?", default=False)
            else:
                confirm = input(f"Download all {total_episodes} episodes? [y/N]: ").strip().lower() == 'y'
            
            if confirm:
                return "season", list(range(1, total_episodes + 1))
        
        return "cancel", []
    
    def _prompt_quality(self) -> str:
        """Prompt for video quality"""
        self._status("\n[bold cyan]Quality:[/bold cyan]")
        self._status("  [cyan]1.[/cyan] Best Available (1080p)")
        self._status("  [dim]    Note: Quality depends on source availability[/dim]")
        
        if RICH_AVAILABLE:
            choice = Prompt.ask("Select", choices=["1"], default="1")
        else:
            choice = input("\nSelect [1]: ").strip() or "1"
        
        return "best"
    
    def _prompt_translation(self, available_eps: Dict) -> Tuple[str, int]:
        """Prompt for SUB or DUB"""
        sub_count = available_eps.get('sub', 0) if isinstance(available_eps, dict) else 0
        dub_count = available_eps.get('dub', 0) if isinstance(available_eps, dict) else 0
        
        if sub_count > 0 and dub_count > 0:
            self._status("\n[bold cyan]Audio:[/bold cyan]")
            self._status(f"  [cyan]1.[/cyan] SUB [dim]({sub_count} episodes)[/dim]")
            self._status(f"  [cyan]2.[/cyan] DUB [dim]({dub_count} episodes)[/dim]")
            
            if RICH_AVAILABLE:
                choice = Prompt.ask("Select", choices=["1", "2"], default="1")
            else:
                choice = input("\nSelect [1]: ").strip() or "1"
            
            if choice == "2":
                return "dub", dub_count
            return "sub", sub_count
        
        elif dub_count > 0:
            return "dub", dub_count
        
        return "sub", sub_count

    def search_and_download(self, url: str, interactive: bool = True) -> Optional[Dict[str, Any]]:
        """Main download method"""
        
        # Extract info from URL
        info = self._extract_from_hianime_url(url)
        anime_name = info.get('anime_name', 'Unknown')
        
        self._status(f"\n[bold]Searching:[/bold] {anime_name}")
        
        # Search AllAnime
        results = self._search_allanime(anime_name)
        
        if not results:
            simple_name = anime_name.split(':')[0].split('(')[0].strip()
            results = self._search_allanime(simple_name)
        
        if not results:
            self._status("[red]✗ Could not find anime[/red]")
            return None
        
        # Select anime
        selected = self._select_anime(results, anime_name)
        if not selected:
            self._status("[yellow]Cancelled[/yellow]")
            return None
        
        show_id = selected.get('id')
        anime_title = selected.get('name', anime_name)
        available_eps = selected.get('episodes', {})
        
        self._status(f"\n[green]✓[/green] [bold]{anime_title}[/bold]")
        
        # Prompt for translation (SUB/DUB)
        translation, total_episodes = self._prompt_translation(available_eps)
        
        if total_episodes == 0:
            self._status("[red]✗ No episodes available[/red]")
            return None
        
        # Prompt for download mode
        mode, episodes = self._prompt_download_mode(total_episodes)
        
        if mode == "cancel" or not episodes:
            self._status("[yellow]Cancelled[/yellow]")
            return None
        
        # Prompt for quality
        quality = self._prompt_quality()
        
        # Setup output directory
        output_dir = getattr(self.downloader, 'output_dir', None) or Path.home() / "Downloads"
        if isinstance(output_dir, str):
            output_dir = Path(output_dir)
        anime_dir = output_dir / sanitize_filename(anime_title)
        anime_dir.mkdir(parents=True, exist_ok=True)
        
        # Show summary
        ep_display = f"Episode {episodes[0]}" if len(episodes) == 1 else f"Episodes {episodes[0]}-{episodes[-1]}"
        quality_display = "Best (1080p)" if quality == "best" else f"{quality}p"
        
        self._status(f"\n[bold cyan]Download Summary:[/bold cyan]")
        self._status(f"  Anime: {anime_title}")
        self._status(f"  {ep_display} ({translation.upper()})")
        self._status(f"  Quality: {quality_display}")
        self._status(f"  Output: {anime_dir}\n")
        
        # Download episodes
        success_count = 0
        failed_episodes = []
        
        for i, ep_num in enumerate(episodes, 1):
            ep_str = str(ep_num)
            
            if len(episodes) > 1:
                self._status(f"[bold cyan]({i}/{len(episodes)})[/bold cyan] Episode {ep_num}")
            
            sources = self._get_episode_sources(show_id, ep_str, translation)
            
            if not sources:
                alt_trans = "dub" if translation == "sub" else "sub"
                sources = self._get_episode_sources(show_id, ep_str, alt_trans)
            
            if not sources:
                self._status(f"  [red]✗ No sources found[/red]")
                failed_episodes.append(ep_num)
                continue
            
            result = self._try_download_episode(sources, anime_dir, anime_title, ep_str, quality)
            if result:
                # Show file size if available
                if isinstance(result, Path) and result.is_file():
                    size_mb = result.stat().st_size / 1024 / 1024
                    self._status(f"  [green]✓ Downloaded[/green] [dim]({size_mb:.1f} MB)[/dim]")
                else:
                    self._status(f"  [green]✓ Downloaded[/green]")
                success_count += 1
            else:
                self._status(f"  [red]✗ Failed[/red]")
                failed_episodes.append(ep_num)
        
        # Summary
        self._status("")
        if success_count == len(episodes):
            self._status(f"[bold green]✓ All {success_count} episode(s) downloaded![/bold green]")
        elif success_count > 0:
            self._status(f"[yellow]Downloaded {success_count}/{len(episodes)} episodes[/yellow]")
            if failed_episodes:
                self._status(f"[red]Failed: {', '.join(map(str, failed_episodes))}[/red]")
        else:
            self._status("[red]✗ Download failed[/red]")
            return None
        
        return {
            'success': True,
            'anime': anime_title,
            'episodes': episodes,
            'downloaded': success_count,
            'failed': failed_episodes,
            'quality': quality,
            'translation': translation,
            'output_dir': str(anime_dir)
        }
    
    def download(self, url: str, quality: str = "best", interactive: bool = True) -> Optional[Dict[str, Any]]:
        """Alias for search_and_download"""
        return self.search_and_download(url, interactive=interactive)
