#!/usr/bin/env python3
"""
Custom logging module for Ultimate Media Downloader
Provides quiet logging to suppress verbose output while showing important messages
"""

try:
    from rich.console import Console
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False


class QuietLogger:
    """Custom logger to suppress yt-dlp's verbose output"""
    
    def debug(self, msg):
        """Suppress debug messages"""
        pass
    
    def info(self, msg):
        """Only show important info messages"""
        if msg.startswith('[download]'):
            # Suppress download progress lines (we have our own)
            if 'Downloading' in msg and 'item' in msg:
                # Show "Downloading item X of Y" messages
                if RICH_AVAILABLE:
                    console = Console()
                    console.print(f"[dim cyan]{msg}[/dim cyan]")
                else:
                    print(msg)
        elif msg.startswith('[info]'):
            # Suppress info messages about downloading thumbnails, etc.
            pass
        elif 'Sleeping' in msg:
            # Suppress "Sleeping X seconds" messages
            pass
        else:
            # Show other important messages
            pass
    
    def warning(self, msg):
        """Show warnings"""
        if RICH_AVAILABLE:
            console = Console()
            console.print(f"[yellow]⚠[/yellow] {msg}")
        else:
            print(f"⚠ {msg}")
    
    def error(self, msg):
        """Show errors"""
        if RICH_AVAILABLE:
            console = Console()
            console.print(f"[bold red]✗[/bold red] {msg}")
        else:
            print(f"✗ {msg}")
