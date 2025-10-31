"""
UI Display functions for Ultimate Media Downloader
Contains functions for displaying help menus, banners, and other UI elements
"""

from ui_components import ModernUI, Icons

try:
    from rich.console import Console
    from rich.table import Table
    from rich import box
    from rich.panel import Panel
    from rich.align import Align
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False


def show_help_menu(ui):
    """Display help menu with modern styling"""
    if ui.console and RICH_AVAILABLE:
        help_table = Table(title="[bold cyan]▭ COMMAND REFERENCE[/bold cyan]",
                          box=box.ROUNDED, border_style="cyan", show_header=True)

        help_table.add_column("Command", style="yellow", justify="left")
        help_table.add_column("Aliases", style="dim", justify="left")
        help_table.add_column("Description", style="white", justify="left")

        help_table.add_row("help", "h", "Show this help menu")
        help_table.add_row("platforms", "p", "List all supported platforms")
        help_table.add_row("clear", "cls", "Clear the screen")
        help_table.add_row("quit", "exit, q", "Exit the application")
        help_table.add_row("[URL]", "-", "Paste any media URL to download")

        ui.console.print()
        ui.console.print(help_table)
        ui.console.print()
    else:
        print("\n" + "=" * 70)
        print("▭ COMMAND REFERENCE")
        print("=" * 70)
        print("  help, h          - Show this help menu")
        print("  platforms, p     - List all supported platforms")
        print("  clear, cls       - Clear the screen")
        print("  quit, exit, q    - Exit the application")
        print("  [URL]            - Paste any media URL to download")
        print("=" * 70 + "\n")


def create_banner():
    """Create a beautiful banner using Rich"""
    ui = ModernUI()

    if RICH_AVAILABLE and ui.console:
        # Create feature table
        feature_grid = Table.grid(padding=(0, 2))
        feature_grid.add_column(justify="center", style="cyan")
        feature_grid.add_column(justify="center", style="magenta")
        feature_grid.add_column(justify="center", style="green")
        feature_grid.add_column(justify="center", style="yellow")

        feature_grid.add_row("▶ Videos", "♪ Music", "▭ Social", "⚡ Fast")

        panel = Panel(
            Align.center(feature_grid),
            title="[bold white]▶ ULTIMATE MEDIA DOWNLOADER[/bold white]",
            subtitle="[dim]Professional Edition[/dim]",
            border_style="bright_cyan",
            box=box.DOUBLE,
            padding=(1, 2)
        )

        ui.console.print(panel)
    else:
        print("=" * 70)
        print("▶ ULTIMATE MEDIA DOWNLOADER")
        print("=" * 70)
