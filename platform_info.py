#!/usr/bin/env python3
"""
Platform Info Module
Displays information about supported platforms and services
"""

try:
    from rich.console import Console
    from rich.table import Table
    from rich import box
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False


class PlatformInfo:
    """Manages platform information and display"""
    
    # Supported platforms with metadata
    SUPPORTED_PLATFORMS = [
        {
            "name": "YouTube",
            "icon": "▶",
            "domains": "youtube.com, youtu.be",
            "content": "Videos, playlists, live streams",
            "note": "Supports 1080p+ downloads"
        },
        {
            "name": "Spotify",
            "icon": "♫",
            "domains": "spotify.com",
            "content": "Tracks, albums, playlists",
            "note": "Downloads via YouTube search + metadata"
        },
        {
            "name": "SoundCloud",
            "icon": "♫",
            "domains": "soundcloud.com",
            "content": "Tracks, playlists, uploads",
            "note": "Full quality available"
        },
        {
            "name": "Apple Music",
            "icon": "♪",
            "domains": "music.apple.com",
            "content": "Tracks, albums",
            "note": "Downloads via YouTube search + metadata"
        },
        {
            "name": "Instagram",
            "icon": "📸",
            "domains": "instagram.com",
            "content": "Videos, reels, IGTV",
            "note": "Posts and Stories supported"
        },
        {
            "name": "TikTok",
            "icon": "▭",
            "domains": "tiktok.com",
            "content": "Videos, user content",
            "note": "Without watermark available"
        },
        {
            "name": "Twitter/X",
            "icon": "◐",
            "domains": "twitter.com, x.com",
            "content": "Videos, media",
            "note": "Video tweets supported"
        },
        {
            "name": "Facebook",
            "icon": "📘",
            "domains": "facebook.com",
            "content": "Videos, live streams",
            "note": "Public videos only"
        },
        {
            "name": "Vimeo",
            "icon": "▶",
            "domains": "vimeo.com",
            "content": "Videos, private content",
            "note": "High quality available"
        },
        {
            "name": "Twitch",
            "icon": "▧",
            "domains": "twitch.tv",
            "content": "VODs, clips, streams",
            "note": "Live streams recordable"
        },
    ]
    
    def __init__(self, console=None):
        """Initialize Platform Info
        
        Args:
            console: Rich Console object (optional)
        """
        self.console = console if RICH_AVAILABLE else None
    
    def list_supported_platforms_rich(self):
        """Display supported platforms using Rich table
        
        Returns:
            Rich Table object
        """
        if not RICH_AVAILABLE or not self.console:
            return None
        
        table = Table(
            title="🌍 Supported Platforms",
            box=box.ROUNDED,
            border_style="cyan",
            header_style="bold magenta"
        )
        
        table.add_column("Platform", style="bold yellow", no_wrap=True)
        table.add_column("Domains", style="cyan")
        table.add_column("Content Types", style="green")
        table.add_column("Notes", style="dim")
        
        for platform in self.SUPPORTED_PLATFORMS:
            table.add_row(
                f"{platform['icon']} {platform['name']}",
                platform['domains'],
                platform['content'],
                platform.get('note', '')
            )
        
        return table
    
    def display_platforms_rich(self, total_sites=None):
        """Display platforms using Rich formatting
        
        Args:
            total_sites: Total number of supported sites
        """
        if not RICH_AVAILABLE or not self.console:
            self.display_platforms_plain(total_sites)
            return
        
        table = self.list_supported_platforms_rich()
        if table:
            self.console.print(table)
        
        if total_sites:
            self.console.print(f"\n[bold green]▤ Total supported sites: {total_sites} platforms[/bold green]")
        
        self.console.print("[yellow]→ Use --check-support <URL> to verify URL compatibility[/yellow]")
    
    def display_platforms_plain(self, total_sites=None):
        """Display platforms using plain text
        
        Args:
            total_sites: Total number of supported sites
        """
        print("\n🌍 SUPPORTED PLATFORMS")
        print("=" * 80)
        
        # Display header
        print(f"{'Platform':<15} | {'Domains':<30} | {'Content Types':<30}")
        print("-" * 80)
        
        for platform in self.SUPPORTED_PLATFORMS:
            print(
                f"{platform['icon']} {platform['name']:<12} | "
                f"{platform['domains']:<30} | "
                f"{platform['content']:<30}"
            )
        
        print("-" * 80)
        
        if total_sites:
            print(f"\n▤ Total supported sites: {total_sites} platforms")
        
        print("→ Use --check-support <URL> to verify if a specific URL is supported\n")
    
    def display_platform_details(self, platform_name):
        """Display detailed information about a specific platform
        
        Args:
            platform_name: Name of platform to display info for
        """
        platform = None
        for p in self.SUPPORTED_PLATFORMS:
            if p['name'].lower() == platform_name.lower():
                platform = p
                break
        
        if not platform:
            print(f"Platform '{platform_name}' not found")
            return
        
        if RICH_AVAILABLE and self.console:
            self.console.print(f"\n[bold cyan]{platform['icon']} {platform['name']}[/bold cyan]")
            self.console.print(f"[dim]─ * ─[/dim]")
            self.console.print(f"[yellow]Domains:[/yellow] {platform['domains']}")
            self.console.print(f"[green]Content:[/green] {platform['content']}")
            if platform.get('note'):
                self.console.print(f"[cyan]Note:[/cyan] {platform['note']}")
        else:
            print(f"\n{platform['icon']} {platform['name']}")
            print(f"Domains: {platform['domains']}")
            print(f"Content: {platform['content']}")
            if platform.get('note'):
                print(f"Note: {platform['note']}")
    
    @staticmethod
    def get_platform_by_domain(domain):
        """Get platform by domain name
        
        Args:
            domain: Domain string (e.g., 'youtube.com')
            
        Returns:
            Platform dictionary or None
        """
        for platform in PlatformInfo.SUPPORTED_PLATFORMS:
            if domain.lower() in platform['domains'].lower():
                return platform
        
        return None
    
    @staticmethod
    def get_all_domains():
        """Get list of all supported domains
        
        Returns:
            List of domain strings
        """
        domains = []
        for platform in PlatformInfo.SUPPORTED_PLATFORMS:
            # Split domains and add individually
            platform_domains = [d.strip() for d in platform['domains'].split(',')]
            domains.extend(platform_domains)
        
        return domains
    
    @staticmethod
    def get_platform_names():
        """Get list of all supported platform names
        
        Returns:
            List of platform names
        """
        return [p['name'] for p in PlatformInfo.SUPPORTED_PLATFORMS]
    
    def display_capabilities(self):
        """Display all capabilities and features"""
        if RICH_AVAILABLE and self.console:
            self.console.print("\n[bold cyan]📋 CAPABILITIES[/bold cyan]")
            self.console.print("[yellow]Video Downloads:[/yellow]")
            self.console.print("  • Download videos up to 4K quality")
            self.console.print("  • Extract audio from videos")
            self.console.print("  • Batch/Playlist downloads")
            self.console.print("  • Custom quality selection")
            
            self.console.print("\n[yellow]Audio Features:[/yellow]")
            self.console.print("  • Multiple audio formats (MP3, FLAC, WAV, M4A, OPUS)")
            self.console.print("  • Metadata embedding")
            self.console.print("  • Album art attachment")
            self.console.print("  • High-quality audio extraction")
            
            self.console.print("\n[yellow]Supported Formats:[/yellow]")
            self.console.print("  • Video: MP4, MKV, WEBM, AVI")
            self.console.print("  • Audio: MP3, FLAC, WAV, M4A, OPUS, AAC")
        else:
            print("\n📋 CAPABILITIES")
            print("Video Downloads:")
            print("  • Download videos up to 4K quality")
            print("  • Extract audio from videos")
            print("  • Batch/Playlist downloads")
            print("  • Custom quality selection")
            
            print("\nAudio Features:")
            print("  • Multiple audio formats (MP3, FLAC, WAV, M4A, OPUS)")
            print("  • Metadata embedding")
            print("  • Album art attachment")
            print("  • High-quality audio extraction")
            
            print("\nSupported Formats:")
            print("  • Video: MP4, MKV, WEBM, AVI")
            print("  • Audio: MP3, FLAC, WAV, M4A, OPUS, AAC")
