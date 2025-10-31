#!/usr/bin/env python3
"""
UI utilities for Rich console output

This module provides utility functions for displaying formatted output
using the Rich library with fallback to plain print statements.
"""

from typing import List, Tuple, Optional

# Try to import Rich components
try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich import box
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    Console = None
    Panel = None
    Table = None
    box = None


class RichConsoleWrapper:
    """
    Wrapper for Rich console with fallback to plain print
    """
    
    def __init__(self):
        """Initialize the console wrapper"""
        self.console = Console() if RICH_AVAILABLE else None
    
    def print_rich(self, message: str, style: str = "bold cyan") -> None:
        """
        Print with Rich formatting if available, fallback to plain print
        
        Args:
            message (str): Message to print
            style (str): Rich style to apply (ignored if Rich not available)
        """
        if RICH_AVAILABLE and self.console:
            self.console.print(message, style=style)
        else:
            print(message)
    
    def print_panel(self, content: str, title: Optional[str] = None, 
                   style: str = "bold blue", border_style: str = "cyan") -> None:
        """
        Print a beautiful panel with Rich if available
        
        Args:
            content (str): Content to display in panel
            title (str, optional): Panel title
            style (str): Panel style
            border_style (str): Border style
        """
        if RICH_AVAILABLE and self.console:
            self.console.print(Panel(content, title=title, style=style, 
                                   border_style=border_style, box=box.ROUNDED))
        else:
            if title:
                print(f"\n{'='*60}")
                print(f"  {title}")
                print('='*60)
            print(content)
            print('='*60)
    
    def print_table(self, title: str, headers: List[str], rows: List[Tuple], 
                   style: str = "cyan") -> None:
        """
        Print a beautiful table with Rich if available
        
        Args:
            title (str): Table title
            headers (list): Column headers
            rows (list): Table rows
            style (str): Table style
        """
        if RICH_AVAILABLE and self.console:
            table = Table(title=title, box=box.ROUNDED, style=style)
            for header in headers:
                table.add_column(header, style="bold")
            for row in rows:
                table.add_row(*[str(cell) for cell in row])
            self.console.print(table)
        else:
            print(f"\n{title}")
            print("-" * 60)
            print(" | ".join(headers))
            print("-" * 60)
            for row in rows:
                print(" | ".join(str(cell) for cell in row))
            print("-" * 60)
    
    def is_rich_available(self) -> bool:
        """
        Check if Rich library is available
        
        Returns:
            bool: True if Rich is available, False otherwise
        """
        return RICH_AVAILABLE


# Convenience functions for standalone use
def print_rich(message: str, style: str = "bold cyan") -> None:
    """Standalone function to print with Rich formatting"""
    wrapper = RichConsoleWrapper()
    wrapper.print_rich(message, style)


def print_panel(content: str, title: Optional[str] = None, 
               style: str = "bold blue", border_style: str = "cyan") -> None:
    """Standalone function to print a panel"""
    wrapper = RichConsoleWrapper()
    wrapper.print_panel(content, title, style, border_style)


def print_table(title: str, headers: List[str], rows: List[Tuple], 
               style: str = "cyan") -> None:
    """Standalone function to print a table"""
    wrapper = RichConsoleWrapper()
    wrapper.print_table(title, headers, rows, style)
