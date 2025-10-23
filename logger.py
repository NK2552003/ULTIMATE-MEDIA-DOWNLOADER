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
    
    def __init__(self):
        """Initialize logger with warning counter"""
        self.warning_count = 0
        self.error_count = 0
    
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
        """Count warnings silently instead of displaying them"""
        self.warning_count += 1
    
    def error(self, msg):
        """Count errors silently (only show critical errors)"""
        self.error_count += 1
        # Only show truly critical errors that stop execution
        if 'unable to download' in msg.lower() or 'no video formats' in msg.lower():
            if RICH_AVAILABLE:
                console = Console()
                console.print(f"[bold red]✗[/bold red] {msg}")
            else:
                print(f"✗ {msg}")
    
    def get_warning_count(self):
        """Get the total warning count"""
        return self.warning_count
    
    def get_error_count(self):
        """Get the total error count"""
        return self.error_count
    
    def print_summary(self):
        """Print summary of warnings and errors if any occurred"""
        if self.warning_count > 0 or self.error_count > 0:
            if RICH_AVAILABLE:
                console = Console()
                if self.warning_count > 0:
                    console.print(f"[dim yellow]⚠ {self.warning_count} warning(s) occurred during processing[/dim yellow]")
                if self.error_count > 0:
                    console.print(f"[dim red]✗ {self.error_count} error(s) occurred during processing[/dim red]")
            else:
                if self.warning_count > 0:
                    print(f"⚠ {self.warning_count} warning(s) occurred during processing")
                if self.error_count > 0:
                    print(f"✗ {self.error_count} error(s) occurred during processing")
