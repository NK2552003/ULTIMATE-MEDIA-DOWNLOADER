#!/usr/bin/env python3
"""
4K Wallpapers Handler Module
Handles downloading wallpapers from 4kwallpapers.com
Supports browsing by new/popular/featured/collections/categories and search.
Downloads wallpapers in parallel with user-selected resolutions.
"""

import os
import re
import time
import random
import warnings
import threading
from pathlib import Path
from typing import Optional, Dict, Any, List, Tuple
from urllib.parse import urlparse, urljoin, quote_plus
from concurrent.futures import ThreadPoolExecutor, as_completed
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
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich.progress import (
        Progress, SpinnerColumn, BarColumn, TextColumn,
        TimeRemainingColumn, DownloadColumn, TransferSpeedColumn,
        TaskID
    )
    from rich.text import Text
    from rich import box
    from rich.layout import Layout
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

# ─── Constants ────────────────────────────────────────────────────────────────

BASE_URL = "https://4kwallpapers.com"

BROWSE_SECTIONS = {
    '1': {'name': 'Home / Featured',   'url': f'{BASE_URL}/'},
    '2': {'name': 'Recently Added',    'url': f'{BASE_URL}/recent/'},
    '3': {'name': 'Browse by Tag',     'url': None},   # sub-menu (live tags)
    '4': {'name': 'Categories',        'url': None},   # sub-menu
    '5': {'name': 'Search',            'url': None},   # search
    '0': {'name': 'Exit',              'url': None},
}

CATEGORIES = [
    ('Abstract',        f'{BASE_URL}/abstract/'),
    ('Animals',         f'{BASE_URL}/animals/'),
    ('Anime',           f'{BASE_URL}/anime/'),
    ('Architecture',    f'{BASE_URL}/architecture/'),
    ('Bikes',           f'{BASE_URL}/bikes/'),
    ('Black / Dark',    f'{BASE_URL}/black-dark/'),
    ('Cars',            f'{BASE_URL}/cars/'),
    ('Celebrations',    f'{BASE_URL}/celebrations/'),
    ('Cute',            f'{BASE_URL}/cute/'),
    ('Fantasy',         f'{BASE_URL}/fantasy/'),
    ('Flowers',         f'{BASE_URL}/flowers/'),
    ('Food',            f'{BASE_URL}/food/'),
    ('Games',           f'{BASE_URL}/games/'),
    ('Graphics / CGI',  f'{BASE_URL}/graphics-cgi/'),
    ('Minimal',         f'{BASE_URL}/minimal/'),
    ('Movies',          f'{BASE_URL}/movies/'),
    ('Music',           f'{BASE_URL}/music/'),
    ('Nature',          f'{BASE_URL}/nature/'),
    ('People',          f'{BASE_URL}/people/'),
    ('Quotes',          f'{BASE_URL}/quotes/'),
    ('Science Fiction', f'{BASE_URL}/sci-fi/'),
    ('Space',           f'{BASE_URL}/space/'),
    ('Sports',          f'{BASE_URL}/sports/'),
    ('Technology',      f'{BASE_URL}/technology/'),
    ('Television',      f'{BASE_URL}/television/'),
    ('World',           f'{BASE_URL}/world/'),
]

# Common desktop/monitor resolutions to try when constructing download URLs
COMMON_RESOLUTIONS = [
    ('12K',  '12288x6912'),
    ('8K',   '7680x4320'),
    ('5K',   '5120x2880'),
    ('4K',   '3840x2160'),
    ('QHD',  '2560x1440'),
    ('FHD',  '1920x1080'),
    ('HD',   '1280x720'),
]

USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 14_3) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.3 Safari/605.1.15',
]


# ─── Handler Class ────────────────────────────────────────────────────────────

class FourKWallpapersHandler:
    """
    Handler for 4kwallpapers.com
    Supports browsing new/popular/featured/collections/categories and search,
    with parallel wallpaper downloads at user-selected resolutions.
    """

    def __init__(self, downloader=None):
        self.downloader = downloader
        self.console = Console() if RICH_AVAILABLE else None
        self.session = self._create_session()

        # Output directory – nested inside main downloader output
        if downloader and hasattr(downloader, 'output_dir'):
            self.output_dir = Path(downloader.output_dir) / 'Wallpapers'
        else:
            self.output_dir = Path.home() / 'Downloads' / 'UltimateDownloader' / 'Wallpapers'
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Thread lock for print safety during parallel downloads
        self._print_lock = threading.Lock()

    # ─── Session ──────────────────────────────────────────────────────────────

    def _create_session(self):
        """Create a resilient requests (or cloudscraper) session."""
        if not REQUESTS_AVAILABLE:
            return None

        if CLOUDSCRAPER_AVAILABLE:
            # Use default cloudscraper settings — adding browser/platform args can
            # trigger Cloudflare challenges on some sites (mismatched TLS fingerprint)
            session = cloudscraper.create_scraper()
        else:
            session = requests.Session()
            retry = Retry(total=4, backoff_factor=1.5,
                          status_forcelist=[429, 500, 502, 503, 504])
            adapter = HTTPAdapter(max_retries=retry)
            session.mount('http://', adapter)
            session.mount('https://', adapter)

        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'DNT': '1',
            'Upgrade-Insecure-Requests': '1',
        })
        return session

    # ─── Printing helpers ─────────────────────────────────────────────────────

    def _print(self, message: str):
        """Thread-safe rich/plain print."""
        with self._print_lock:
            if RICH_AVAILABLE and self.console:
                self.console.print(message)
            else:
                cleaned = re.sub(r'\[/?[^\]]+\]', '', message)
                print(cleaned)

    def _print_header(self, title: str, subtitle: str = ''):
        """Print a styled header panel."""
        if RICH_AVAILABLE and self.console:
            content = f"[bold cyan]{title}[/bold cyan]"
            if subtitle:
                content += f"\n[dim]{subtitle}[/dim]"
            self.console.print(Panel.fit(content, border_style='cyan'))
        else:
            print()
            print('=' * 60)
            print(f'  {title}')
            if subtitle:
                print(f'  {subtitle}')
            print('=' * 60)

    # ─── HTTP helpers ─────────────────────────────────────────────────────────

    def _get_html(self, url: str, timeout: int = 20) -> Optional[str]:
        """Fetch URL and return HTML text, or None on failure."""
        if not self.session:
            self._print('[red]✗ requests is not available[/red]')
            return None
        try:
            resp = self.session.get(url, timeout=timeout)
            resp.raise_for_status()
            return resp.text
        except Exception:
            return None

    # ─── Scraping helpers ─────────────────────────────────────────────────────

    def _parse_wallpaper_listing(self, html: str) -> List[Dict]:
        """
        Parse a listing page HTML and return a list of wallpaper dicts:
          {title, url, thumbnail, id, category_slug, base_slug}
        """
        if not BS4_AVAILABLE:
            self._print('[red]✗ beautifulsoup4 is not installed – cannot parse page[/red]')
            return []

        soup = BeautifulSoup(html, 'html.parser')
        wallpapers: List[Dict] = []
        seen: set = set()

        for a_tag in soup.find_all('a', href=True):
            href = a_tag['href']

            # Only wallpaper detail pages: /category/title-ID.html
            # simpler check: must be from 4kwallpapers.com, end with -NNN.html
            if not ('4kwallpapers.com/' in href and href.endswith('.html')):
                continue
            if not re.search(r'-\d+\.html$', href):
                continue
            # Skip navigation pages like /collections-packs/, /most-popular ..., etc.
            # that don't have a wallpaper ID slug
            path = urlparse(href).path
            path_parts = [p for p in path.strip('/').split('/') if p]
            if len(path_parts) < 2:
                continue

            if href in seen:
                continue
            seen.add(href)

            img = a_tag.find('img')
            title = ''
            thumb = ''
            wall_id = ''

            if img:
                title = (img.get('alt') or '').strip()
                # Try src first, then data-src (lazy load)
                thumb = img.get('src', '') or img.get('data-src', '')
                m = re.search(r'/(\d+)\.\w+$', str(thumb))
                if m:
                    wall_id = m.group(1)

            if not title:
                title = (a_tag.get('title') or a_tag.get_text(' ', strip=True)).strip()

            if not wall_id:
                m = re.search(r'-(\d+)\.html$', href)
                if m:
                    wall_id = m.group(1)

            if not title or not wall_id:
                continue

            # category is path_parts[0], full page slug is path_parts[-1] sans .html
            category_slug = path_parts[0]
            page_slug = path_parts[-1].replace('.html', '')
            # Remove trailing "-ID" to get the base name slug
            base_slug = re.sub(r'-\d+$', '', page_slug)

            wallpapers.append({
                'title':         title,
                'url':           href,
                'thumbnail':     thumb,
                'id':            wall_id,
                'category_slug': category_slug,
                'base_slug':     base_slug,
            })

        return wallpapers

    def _parse_download_links(self, html: str) -> List[Dict]:
        """
        Extract download links from a wallpaper detail page.
        Returns list of dicts: {url, resolution, label, fmt}
        """
        if not BS4_AVAILABLE:
            return []

        soup = BeautifulSoup(html, 'html.parser')
        links: List[Dict] = []
        seen: set = set()

        for a_tag in soup.find_all('a', href=True):
            href = a_tag['href']
            if '/images/wallpapers/' not in href:
                continue
            if href in seen:
                continue
            seen.add(href)

            # Extract resolution from URL (pattern: ...NNNNxNNNN-ID.ext)
            m = re.search(r'(\d{3,5}x\d{3,5})', href)
            resolution = m.group(1) if m else 'Unknown'

            ext = href.rsplit('.', 1)[-1].lower() if '.' in href else 'jpg'
            label = a_tag.get_text(' ', strip=True) or f'{resolution} {ext.upper()}'

            links.append({
                'url':        href if href.startswith('http') else f'{BASE_URL}{href}',
                'resolution': resolution,
                'label':      label,
                'fmt':        ext,
            })

        # Sort by pixel count (largest first)
        links.sort(key=lambda x: self._res_pixels(x['resolution']), reverse=True)
        return links

    # ─── Public fetch methods ─────────────────────────────────────────────────

    def fetch_listing(self, url: str) -> List[Dict]:
        """Fetch and parse a wallpaper listing page."""
        html = self._get_html(url)
        if not html:
            return []
        return self._parse_wallpaper_listing(html)

    def fetch_wallpaper_details(self, wall: Dict) -> List[Dict]:
        """
        Return download links for a wallpaper.
        First tries scraping the detail page; falls back to URL construction.
        """
        html = self._get_html(wall['url'])
        if html:
            links = self._parse_download_links(html)
            if links:
                return links

        # Fallback: construct download URLs for standard resolutions
        return self._construct_download_urls(wall)

    def _construct_download_urls(self, wall: Dict) -> List[Dict]:
        """
        Construct probable download URLs from known site patterns without
        fetching the detail page.
        """
        base_slug = wall.get('base_slug', '')
        wall_id   = wall.get('id', '')
        if not base_slug or not wall_id:
            return []

        links = []
        for label, res in COMMON_RESOLUTIONS:
            url = f'{BASE_URL}/images/wallpapers/{base_slug}-{res}-{wall_id}.png'
            links.append({
                'url':        url,
                'resolution': res,
                'label':      f'Download in {label} ({res})',
                'fmt':        'png',
            })
        return links

    def fetch_popular_tags(self) -> List[Dict]:
        """
        Scrape popular/trending tag links from the 4kwallpapers.com homepage.
        Each tag is a slug-based category page like /anime/, /cars/, /8k/, etc.
        Returns list of {name, url} dicts.
        """
        html = self._get_html(BASE_URL + '/')
        if not html or not BS4_AVAILABLE:
            return []

        soup = BeautifulSoup(html, 'html.parser')
        tags: List[Dict] = []
        seen: set = set()

        for a_tag in soup.find_all('a', href=True):
            href = a_tag['href'].rstrip('/')
            # Tag/category link: one path component, no .html, no image path
            if '4kwallpapers.com' not in href:
                continue
            if 'images' in href or href.endswith('.html'):
                continue
            # Normalize to trailing slash form
            normalized = href.rstrip('/') + '/'
            path = urlparse(normalized).path
            path_parts = [p for p in path.strip('/').split('/') if p]
            # Accept only single-component paths (top-level tags)
            if len(path_parts) != 1:
                continue
            if normalized in seen:
                continue
            seen.add(normalized)

            name = a_tag.get_text(' ', strip=True).strip()
            if not name:
                name = path_parts[0].replace('-', ' ').title()
            if name:
                tags.append({'name': name, 'url': normalized})

        return tags

    # Keep old name as alias for backward compatibility
    def fetch_collections(self) -> List[Dict]:
        return self.fetch_popular_tags()

    def search_wallpapers(self, query: str) -> List[Dict]:
        """Search 4kwallpapers.com for wallpapers matching query."""
        # Working search URL: https://4kwallpapers.com/search/?q=<query>
        search_url = f'{BASE_URL}/search/?q={quote_plus(query)}'
        return self.fetch_listing(search_url)

    # ─── Download helpers ─────────────────────────────────────────────────────

    def _res_pixels(self, resolution: str) -> int:
        """Convert 'WxH' string to pixel count."""
        try:
            w, h = resolution.lower().split('x')
            return int(w) * int(h)
        except Exception:
            return 0

    def _best_link(self, links: List[Dict]) -> Optional[Dict]:
        """Return the link with the highest resolution."""
        if not links:
            return None
        return max(links, key=lambda x: self._res_pixels(x['resolution']))

    def _find_link_for_resolution(self, links: List[Dict], target: str) -> Optional[Dict]:
        """Find a link matching target resolution, or fall back to best."""
        for link in links:
            if link['resolution'] == target:
                return link
        return self._best_link(links)

    def download_single(self, url: str, title: str, resolution: str) -> Optional[str]:
        """
        Download one wallpaper.  Returns the saved file path or None.
        """
        if not self.session:
            return None

        safe_title = sanitize_filename(title)[:80]
        ext = url.rsplit('.', 1)[-1].lower() if '.' in url else 'jpg'
        filename = f'{safe_title}_{resolution}.{ext}'
        filepath = self.output_dir / filename

        if filepath.exists():
            return str(filepath)

        try:
            resp = self.session.get(url, stream=True, timeout=60)
            resp.raise_for_status()

            with open(filepath, 'wb') as fh:
                for chunk in resp.iter_content(chunk_size=65536):
                    if chunk:
                        fh.write(chunk)

            return str(filepath)

        except Exception as exc:
            # Clean up partial file
            try:
                filepath.unlink(missing_ok=True)
            except Exception:
                pass
            return None

    def download_parallel(
        self,
        tasks: List[Tuple[str, str, str]],  # (url, title, resolution)
        max_workers: int = 5
    ) -> Tuple[List[str], List[str]]:
        """
        Download wallpapers in parallel.
        Returns (successful_paths, failed_titles).
        """
        successful: List[str] = []
        failed: List[str] = []
        done_count = [0]

        def _worker(task):
            url, title, resolution = task
            result = self.download_single(url, title, resolution)
            done_count[0] += 1
            prog = done_count[0]
            total = len(tasks)
            if result:
                self._print(
                    f'[green]  ✓ [{prog}/{total}][/green] {title[:50]} '
                    f'[dim]({resolution})[/dim]'
                )
                return result
            else:
                self._print(
                    f'[red]  ✗ [{prog}/{total}][/red] Failed: {title[:50]}'
                )
                return None

        if RICH_AVAILABLE and self.console:
            with Progress(
                SpinnerColumn(),
                TextColumn('[bold cyan]{task.description}'),
                BarColumn(),
                TextColumn('[progress.percentage]{task.percentage:>3.0f}%'),
                TimeRemainingColumn(),
                console=self.console,
                transient=True,
            ) as progress:
                task_id = progress.add_task(
                    f'Downloading {len(tasks)} wallpapers…', total=len(tasks)
                )
                with ThreadPoolExecutor(max_workers=max_workers) as ex:
                    futures = {ex.submit(_worker, t): t for t in tasks}
                    for future in as_completed(futures):
                        progress.advance(task_id)
                        result = future.result()
                        if result:
                            successful.append(result)
                        else:
                            failed.append(futures[future][1])
        else:
            print(f'\n⟳ Downloading {len(tasks)} wallpapers in parallel…')
            with ThreadPoolExecutor(max_workers=max_workers) as ex:
                futures = {ex.submit(_worker, t): t for t in tasks}
                for future in as_completed(futures):
                    result = future.result()
                    if result:
                        successful.append(result)
                    else:
                        failed.append(futures[future][1])

        return successful, failed

    # ─── Interactive helpers ───────────────────────────────────────────────────

    def _display_wallpaper_list(self, wallpapers: List[Dict], section_name: str):
        """Pretty-print a numbered list of wallpapers."""
        if RICH_AVAILABLE and self.console:
            table = Table(
                title=f'[bold cyan]{section_name}[/bold cyan] — [dim]{len(wallpapers)} wallpapers shown[/dim]',
                box=box.SIMPLE_HEAVY,
                show_header=True,
                header_style='bold magenta',
            )
            table.add_column('#',     style='cyan',  width=4, justify='right')
            table.add_column('Title', style='white', no_wrap=False)
            for i, w in enumerate(wallpapers, 1):
                table.add_row(str(i), w['title'])
            self.console.print()
            self.console.print(table)
        else:
            print(f'\n{"─"*70}')
            print(f'  {section_name.upper()}  ({len(wallpapers)} wallpapers)')
            print(f'{"─"*70}')
            for i, w in enumerate(wallpapers, 1):
                print(f'  {i:>3}. {w["title"]}')
            print(f'{"─"*70}')

    def _ask_int(self, prompt: str, lo: int, hi: int, default: int) -> int:
        """Ask user for an integer in [lo, hi]."""
        while True:
            try:
                raw = input(f'{prompt} [{lo}-{hi}, default {default}]: ').strip()
                if not raw:
                    return default
                val = int(raw)
                if lo <= val <= hi:
                    return val
                self._print(f'[yellow]⚠  Please enter a number between {lo} and {hi}[/yellow]')
            except (ValueError, EOFError):
                return default
            except KeyboardInterrupt:
                return default

    def _ask_resolution(self, all_links_per_wall: List[List[Dict]]) -> Optional[str]:
        """
        Collect all unique resolutions from fetched detail links, display
        them and return the user's choice (or None for 'best available').
        """
        resolution_set: set = set()
        for links in all_links_per_wall:
            for link in links:
                if link['resolution'] and link['resolution'] != 'Unknown':
                    resolution_set.add(link['resolution'])

        if not resolution_set:
            # No links found; let caller handle fallback
            return None

        sorted_res = sorted(
            resolution_set,
            key=self._res_pixels,
            reverse=True,
        )

        if RICH_AVAILABLE and self.console:
            table = Table(
                title='[bold cyan]Available Resolutions[/bold cyan]',
                box=box.SIMPLE,
                show_header=True,
                header_style='bold magenta',
            )
            table.add_column('#',           style='cyan',  width=4, justify='right')
            table.add_column('Resolution',  style='green')
            table.add_column('Pixels',      style='dim',   justify='right')
            for i, res in enumerate(sorted_res, 1):
                pixels = self._res_pixels(res)
                mp = f'{pixels / 1_000_000:.1f} MP'
                table.add_row(str(i), res, mp)
            # Add "Best available" as last option
            table.add_row(str(len(sorted_res) + 1), 'Best Available (auto)', '—')
            self.console.print()
            self.console.print(table)
        else:
            print('\nAvailable Resolutions:')
            for i, res in enumerate(sorted_res, 1):
                print(f'  {i}. {res}')
            print(f'  {len(sorted_res) + 1}. Best Available (auto)')

        choice = self._ask_int(
            'Select resolution',
            1, len(sorted_res) + 1,
            default=1,
        )

        if choice == len(sorted_res) + 1:
            return None          # Best available
        return sorted_res[choice - 1]

    # ─── Core flow: display list → pick count → fetch details → pick res → download ──

    def _run_listing_flow(self, section_name: str, listing_url: str):
        """
        Full interactive flow for any listing/category/collection/search
        results page.
        """
        self._print(f'\n[bold cyan]⟳ Fetching {section_name} wallpapers…[/bold cyan]')
        wallpapers = self.fetch_listing(listing_url)

        if not wallpapers:
            self._print(f'[red]✗ No wallpapers found for "{section_name}".[/red]')
            self._print('[dim]The page layout may have changed or the URL returned no results.[/dim]')
            return

        # Show up to 40 results initially
        display = wallpapers[:40]
        self._display_wallpaper_list(display, section_name)

        # Ask how many to download
        count = self._ask_int(
            'How many wallpapers do you want to download?',
            1, len(display),
            default=min(10, len(display)),
        )

        selected = display[:count]

        # Fetch download links for each selected wallpaper
        self._print(
            f'\n[bold cyan]⟳ Fetching available resolutions for {count} wallpaper(s)…[/bold cyan]'
        )
        all_links: List[List[Dict]] = []
        for idx, wall in enumerate(selected, 1):
            self._print(
                f'[dim]  [{idx}/{count}] {wall["title"][:60]}[/dim]'
            )
            links = self.fetch_wallpaper_details(wall)
            all_links.append(links)
            time.sleep(0.25)   # polite crawl delay

        # Let user pick resolution
        chosen_resolution = self._ask_resolution(all_links)

        # Build download task list
        tasks: List[Tuple[str, str, str]] = []
        for wall, links in zip(selected, all_links):
            if not links:
                self._print(f'[yellow]  ⊘ No download links for: {wall["title"][:50]}[/yellow]')
                continue

            if chosen_resolution is None:
                link = self._best_link(links)
            else:
                link = self._find_link_for_resolution(links, chosen_resolution)

            if link:
                tasks.append((link['url'], wall['title'], link['resolution']))
            else:
                self._print(f'[yellow]  ⊘ No suitable link for: {wall["title"][:50]}[/yellow]')

        if not tasks:
            self._print('[red]✗ No downloadable wallpapers found.[/red]')
            return

        # Summary & confirm
        self._print(f'\n[bold white]Download Summary:[/bold white]')
        self._print(f'  Wallpapers : [cyan]{len(tasks)}[/cyan]')
        self._print(
            f'  Resolution : [cyan]{"Best available" if chosen_resolution is None else chosen_resolution}[/cyan]'
        )
        self._print(f'  Output dir : [cyan]{self.output_dir}[/cyan]')

        confirm = input('\nProceed with download? (y/n) [y]: ').strip().lower() or 'y'
        if confirm not in ('y', 'yes'):
            self._print('[yellow]Download cancelled.[/yellow]')
            return

        # Download
        successful, failed = self.download_parallel(tasks, max_workers=5)

        # Final report
        self._print(f'\n[bold green]✦ Download Complete! ✦[/bold green]')
        self._print(f'[green]  ✓ Successful: {len(successful)}[/green]')
        if failed:
            self._print(f'[red]  ✗ Failed   : {len(failed)}[/red]')
        self._print(f'[cyan]  Saved to   : {self.output_dir}[/cyan]')

    # ─── Interactive menus ─────────────────────────────────────────────────────

    def _menu_categories(self):
        """Show categories sub-menu."""
        self._print_header('CATEGORIES', 'Choose a category to browse')
        for i, (name, _) in enumerate(CATEGORIES, 1):
            self._print(f'  [cyan]{i:>2}.[/cyan] {name}')
        self._print(f'  [cyan] 0.[/cyan] Back')

        choice = input('\nSelect category: ').strip()
        if choice == '0':
            return

        try:
            idx = int(choice) - 1
            if 0 <= idx < len(CATEGORIES):
                name, url = CATEGORIES[idx]
                self._run_listing_flow(name, url)
            else:
                self._print('[yellow]Invalid selection.[/yellow]')
        except (ValueError, IndexError):
            self._print('[yellow]Invalid input.[/yellow]')

    def _menu_tags(self):
        """Show popular tags sub-menu (live from homepage)."""
        self._print(f'\n[bold cyan]⟳ Loading popular tags from 4kwallpapers.com…[/bold cyan]')
        tags = self.fetch_popular_tags()

        if not tags:
            self._print('[red]✗ Could not load tags. Try again later.[/red]')
            return

        self._print_header(
            f'POPULAR TAGS  ({len(tags)} found)',
            'Browse wallpapers by trending tag'
        )
        for i, tag in enumerate(tags, 1):
            self._print(f'  [cyan]{i:>3}.[/cyan] {tag["name"]}')
        self._print(f'  [cyan]  0.[/cyan] Back')

        try:
            choice = int(input(f'\nSelect tag (0-{len(tags)}): ').strip())
            if choice == 0:
                return
            if 1 <= choice <= len(tags):
                tag = tags[choice - 1]
                self._run_listing_flow(tag['name'], tag['url'])
            else:
                self._print('[yellow]Invalid selection.[/yellow]')
        except (ValueError, KeyboardInterrupt):
            self._print('[yellow]Invalid input.[/yellow]')

    def _menu_search(self, query: str = ''):
        """Search wallpapers interactively."""
        if not query:
            query = input('Enter search keyword(s): ').strip()
        if not query:
            return

        search_url = f'{BASE_URL}/search/?q={quote_plus(query)}'
        self._run_listing_flow(f'Search: "{query}"', search_url)

    # ─── URL entry-point (pasting a 4kwallpapers.com URL directly) ───────────────

    def handle_url(self, url: str):
        """
        Handle a 4kwallpapers.com URL entered in interactive mode.

        • Specific wallpaper page  (…/category/title-NNN.html)
            → fetch download links, pick resolution, download
        • Category / tag page  (…/anime/ , …/space/ , etc.)
            → run_listing_flow for that page
        • Search results page  (…/search/?q=…)
            → run_listing_flow for the search
        • Homepage  (https://4kwallpapers.com/)
            → launch interactive_browse()
        """
        parsed_path = urlparse(url).path.strip('/')
        query_string = urlparse(url).query

        # ── Specific wallpaper detail page
        if re.search(r'-\d+\.html$', url):
            path_parts = [p for p in parsed_path.split('/') if p]
            page_slug  = path_parts[-1].replace('.html', '') if path_parts else ''
            m_id = re.search(r'-(\d+)$', page_slug)
            wall_id   = m_id.group(1) if m_id else ''
            base_slug = re.sub(r'-\d+$', '', page_slug)
            category  = path_parts[0] if len(path_parts) >= 2 else 'wallpapers'

            # Build a minimal wall dict from the URL
            wall = {
                'title':         base_slug.replace('-', ' ').title(),
                'url':           url,
                'thumbnail':     f'{BASE_URL}/images/walls/thumbs/{wall_id}.jpg' if wall_id else '',
                'id':            wall_id,
                'category_slug': category,
                'base_slug':     base_slug,
            }

            self._print(f'\n[bold cyan]⟳ Fetching download links…[/bold cyan]')
            links = self.fetch_wallpaper_details(wall)

            if not links:
                self._print('[red]✗ Could not fetch download links for this wallpaper.[/red]')
                return

            chosen_resolution = self._ask_resolution([links])
            if chosen_resolution is None:
                link = self._best_link(links)
            else:
                link = self._find_link_for_resolution(links, chosen_resolution)

            if not link:
                self._print('[red]✗ No suitable download link found.[/red]')
                return

            self._print(f'\n[bold white]Download Summary:[/bold white]')
            self._print(f'  Title      : [cyan]{wall["title"]}[/cyan]')
            self._print(f'  Resolution : [cyan]{link["resolution"]}[/cyan]')
            self._print(f'  Output dir : [cyan]{self.output_dir}[/cyan]')

            confirm = input('\nProceed with download? (y/n) [y]: ').strip().lower() or 'y'
            if confirm not in ('y', 'yes'):
                return

            result = self.download_single(link['url'], wall['title'], link['resolution'])
            if result:
                self._print(f'[bold green]✓ Saved: {result}[/bold green]')
            else:
                self._print('[red]✗ Download failed.[/red]')
            return

        # ── Search results page
        if 'search' in parsed_path:
            import re as _re
            from urllib.parse import parse_qs
            params = parse_qs(urlparse(url).query)
            query  = params.get('q', params.get('search', ['']))[0]
            section_name = f'Search: "{query}"' if query else 'Search Results'
            self._run_listing_flow(section_name, url)
            return

        # ── Category / tag page (any other non-root path)
        if parsed_path:
            # Humanise the slug: 'sci-fi' → 'Sci Fi'
            slug = parsed_path.split('/')[0]
            section_name = slug.replace('-', ' ').title()
            self._run_listing_flow(section_name, url if url.endswith('/') else url + '/')
            return

        # ── Fallback: homepage → full interactive menu
        self.interactive_browse()

    def interactive_browse(self, search_query: str = ''):
        """
        Entry-point for interactive wallpaper mode.
        If search_query is provided, jumps directly to search.
        """
        # If launched with a search query (umd --wallpaper-search "…"), skip main menu
        if search_query:
            self._menu_search(search_query)
            return

        self._print_header(
            '🖼  4K WALLPAPERS DOWNLOADER',
            'Browse & download stunning 4K wallpapers from 4kwallpapers.com'
        )

        while True:
            self._print('\n[bold white]MAIN MENU[/bold white]')
            self._print('  [cyan]1.[/cyan] Home / Featured')
            self._print('  [cyan]2.[/cyan] Recently Added')
            self._print('  [cyan]3.[/cyan] Browse by Tag  (trending)')
            self._print('  [cyan]4.[/cyan] Categories')
            self._print('  [cyan]5.[/cyan] Search')
            self._print('  [cyan]0.[/cyan] Exit')

            try:
                choice = input('\nYour choice: ').strip()
            except (EOFError, KeyboardInterrupt):
                break

            if choice == '0':
                break
            elif choice == '1':
                self._run_listing_flow('Home / Featured', f'{BASE_URL}/')
            elif choice == '2':
                self._run_listing_flow('Recently Added', f'{BASE_URL}/recent/')
            elif choice == '3':
                self._menu_tags()
            elif choice == '4':
                self._menu_categories()
            elif choice == '5':
                self._menu_search()
            else:
                self._print('[yellow]Invalid choice. Please try again.[/yellow]')

        self._print('[dim]Exiting wallpaper downloader.[/dim]')
