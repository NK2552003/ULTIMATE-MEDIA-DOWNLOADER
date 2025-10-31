#!/usr/bin/env python3
"""
UI Components for Ultimate Media Downloader
Provides modern, professional UI elements with Rich formatting
"""

import os

try:
    from rich.console import Console
    from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TimeRemainingColumn, DownloadColumn, TransferSpeedColumn
    from rich.panel import Panel
    from rich.table import Table
    from rich.text import Text
    from rich import box
    from rich.align import Align
    from rich.prompt import Prompt
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

try:
    from pyfiglet import Figlet
    PYFIGLET_AVAILABLE = True
except ImportError:
    PYFIGLET_AVAILABLE = False

try:
    from halo import Halo
    HALO_AVAILABLE = True
except ImportError:
    HALO_AVAILABLE = False


class Icons:
    """Modern 2D icon management with flat design emojis"""
    
    @staticmethod
    def get(name):
        """Get modern flat design icons"""
        icon_map = {
            # Status icons - using flat 2D style
            'success': '✓', 'error': '✗', 'warning': '⚠', 'info': 'ℹ', 'tip': '→',
            
            # Media icons - minimal flat design
            'video': '▶', 'audio': '♫', 'music': '♪', 'playlist': '≡', 'download': '↓',
            'folder': '▸', 'link': '⚲', 'search': '⌕',
            
            # Platform icons - recognizable symbols
            'youtube': '▶', 'spotify': '♪', 'soundcloud': '☁', 'instagram': '◉',
            'tiktok': '♪', 'twitter': '◐', 'facebook': 'f',
            
            # Progress icons
            'loading': '⟳', 'processing': '⚙', 'completed': '✓', 'failed': '✗',
            
            # Quality icons
            'hd': '⚡', 'quality': '★', 'format': '▭',
            
            # Action icons
            'start': '▸', 'stop': '■', 'pause': '⏸', 'play': '▶',
            
            # Statistics
            'stats': '▤', 'count': '#', 'time': '◷', 'speed': '⚡',
            
            # Social
            'like': '♥', 'views': '◉', 'channel': '◈',
            
            # Misc
            'world': '◎', 'book': '▭', 'target': '◎', 'sparkles': '✦',
            'fire': '◆', 'package': '▣', 'art': '◨', 'game': '▧', 'phone': '▭',
        }
        return icon_map.get(name, '•')


class Messages:
    """Centralized message templates with Rich formatting"""
    
    @staticmethod
    def success(text):
        return f"[bold green]{Icons.get('success')} {text}[/bold green]"
    
    @staticmethod
    def error(text):
        return f"[bold red]{Icons.get('error')} {text}[/bold red]"
    
    @staticmethod
    def warning(text):
        return f"[bold yellow]{Icons.get('warning')} {text}[/bold yellow]"
    
    @staticmethod
    def info(text):
        return f"[cyan]{Icons.get('info')} {text}[/cyan]"
    
    @staticmethod
    def tip(text):
        return f"[bold magenta]{Icons.get('tip')} {text}[/bold magenta]"
    
    @staticmethod
    def downloading(text):
        return f"[bold blue]{Icons.get('download')} {text}[/bold blue]"
    
    @staticmethod
    def searching(text):
        return f"[bold cyan]{Icons.get('search')} {text}[/bold cyan]"
    
    @staticmethod
    def processing(text):
        return f"[bold yellow]{Icons.get('processing')} {text}[/bold yellow]"
    
    @staticmethod
    def completed(text):
        return f"[bold green]{Icons.get('completed')} {text}[/bold green]"


class ModernUI:
    """Professional CLI UI with animations and modern design"""
    
    def __init__(self):
        self.console = Console() if RICH_AVAILABLE else None
        
    def clear_screen(self):
        """Clear terminal screen"""
        os.system('clear' if os.name == 'posix' else 'cls')
    
    def create_ascii_logo(self):
        """Create ASCII art logo"""
        return """
██████╗  ██████╗ ██╗    ██╗███╗   ██╗██╗      ██████╗  █████╗ ██████╗ ███████╗██████╗ 
██╔══██╗██╔═══██╗██║    ██║████╗  ██║██║     ██╔═══██╗██╔══██╗██╔══██╗██╔════╝██╔══██╗
██║  ██║██║   ██║██║ █╗ ██║██╔██╗ ██║██║     ██║   ██║███████║██║  ██║█████╗  ██████╔╝
██║  ██║██║   ██║██║███╗██║██║╚██╗██║██║     ██║   ██║██╔══██║██║  ██║██╔══╝  ██╔══██╗
██████╔╝╚██████╔╝╚███╔███╔╝██║ ╚████║███████╗╚██████╔╝██║  ██║██████╔╝███████╗██║  ██║
╚═════╝  ╚═════╝  ╚══╝╚══╝ ╚═╝  ╚═══╝╚══════╝ ╚═════╝ ╚═╝  ╚═╝╚═════╝ ╚══════╝╚═╝  ╚═╝
"""
    
    def show_welcome_banner(self):
        """Display professional welcome banner"""
        if not RICH_AVAILABLE or not self.console:
            return
        
        self.clear_screen()
        
        # Create gradient text for logo
        logo_text = Text()
        logo_lines = self.create_ascii_logo().strip().split('\n')
        
        for line in logo_lines:
            logo_text.append(line + '\n', style="bold cyan")
        
        # Create main panel
        content = Align.center(logo_text)
        
        panel = Panel(
            content,
            border_style="bright_cyan",
            box=box.DOUBLE,
            padding=(1, 2),
            title="[bold white]▶ ULTIMATE MEDIA DOWNLOADER[/bold white]",
            subtitle="[dim]v2.0 - Professional Edition[/dim]"
        )
        
        self.console.print(panel)
        
        # Feature highlights in columns
        features = Table.grid(padding=(0, 2))
        features.add_column(justify="center", style="cyan")
        features.add_column(justify="center", style="magenta")
        features.add_column(justify="center", style="green")
        features.add_column(justify="center", style="yellow")
        
        features.add_row(
            "▶ Video Downloads",
            "♪ Audio Extraction", 
            "▭ Social Media",
            "⚡ many Platforms"
        )
        
        self.console.print(Align.center(features))
        self.console.print()
    
    def show_interactive_banner(self):
        """Display interactive mode banner"""
        if not RICH_AVAILABLE or not self.console:
            print("\n▶ Ultimate Media Downloader - Interactive Mode")
            print("=" * 70)
            return
        
        # Title with gradient effect
        title = Text()
        title.append("▶  I N T E R A C T I V E   M O D E  ◀", style="bold yellow")
        
        # Create info table
        info_table = Table.grid(padding=(0, 2))
        info_table.add_column(style="cyan", justify="center")
        
        info_table.add_row("[bold white]Supported Platforms:[/bold white]")
        info_table.add_row("▶ YouTube     ♪ Spotify     ◉ Instagram")
        info_table.add_row("♫ SoundCloud  ▭ TikTok      ◐ Twitter")
        info_table.add_row("... and many more!")
        info_table.add_row("")
        info_table.add_row("[bold white]Quick Commands:[/bold white]")
        info_table.add_row("[yellow]help[/yellow]      - Show available commands")
        info_table.add_row("[yellow]platforms[/yellow] - List supported sites")
        info_table.add_row("[yellow]quit[/yellow]      - Exit application")
        
        panel = Panel(
            Align.center(info_table),
            title=title,
            border_style="bright_magenta",
            box=box.ROUNDED,
            padding=(1, 2)
        )
        
        self.console.print(panel)
        self.console.print()
    
    def show_spinner(self, text, spinner_type='dots'):
        """Create and return a spinner for loading states"""
        if HALO_AVAILABLE:
            return Halo(text=text, spinner=spinner_type, color='cyan')
        return None
    
    def success_message(self, message):
        """Display success message"""
        if self.console:
            self.console.print(f"\n[bold green]✓[/bold green] {message}", style="green")
        else:
            print(f"\n✓ {message}")
    
    def error_message(self, message):
        """Display error message"""
        if self.console:
            self.console.print(f"\n[bold red]✗[/bold red] {message}", style="red")
        else:
            print(f"\n✗ {message}")
    
    def info_message(self, message):
        """Display info message"""
        if self.console:
            self.console.print(f"[cyan]ℹ[/cyan] {message}")
        else:
            print(f"ℹ {message}")
    
    def warning_message(self, message, show_icon=True):
        """Display warning message"""
        if self.console:
            icon = "⚠ " if show_icon else ""
            self.console.print(f"[yellow]{icon}{message}[/yellow]")
        else:
            icon = "⚠ " if show_icon else ""
            print(f"{icon}{message}")
    
    def prompt_input(self, prompt_text, default=None):
        """Prompt user for input with styling"""
        if self.console and RICH_AVAILABLE:
            return Prompt.ask(f"[bold cyan]⚲[/bold cyan] {prompt_text}", default=default)
        else:
            user_input = input(f"⚲ {prompt_text}: ").strip()
            return user_input if user_input else default
    
    def create_download_progress(self):
        """Create a modern progress bar for downloads"""
        if RICH_AVAILABLE:
            return Progress(
                SpinnerColumn(spinner_name="dots"),
                TextColumn("[bold blue]{task.description}"),
                BarColumn(bar_width=40, style="cyan", complete_style="green"),
                TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
                DownloadColumn(),
                TransferSpeedColumn(),
                TimeRemainingColumn(),
                console=self.console,
                transient=False
            )
        return None
