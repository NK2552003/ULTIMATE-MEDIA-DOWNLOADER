#!/usr/bin/env python3
"""
Progress Display Module
Handles download progress visualization and formatting
"""

import os


class ProgressDisplay:
    """Manages download progress display with ANSI colors and formatting"""
    
    @staticmethod
    def format_speed(speed):
        """Format download speed to human-readable format
        
        Args:
            speed: Speed in bytes/second
            
        Returns:
            Formatted speed string (e.g., "5.2MB/s" or "512KB/s")
        """
        if not speed:
            return "---KB/s"
        
        if speed > 1024 * 1024:  # MB/s
            return f"{speed/1024/1024:.1f}MB/s"
        else:  # KB/s
            return f"{speed/1024:.0f}KB/s"
    
    @staticmethod
    def format_eta(eta):
        """Format estimated time to human-readable format
        
        Args:
            eta: Estimated time in seconds
            
        Returns:
            Formatted ETA string (e.g., "2h30m" or "45s")
        """
        if not eta:
            return "--:--"
        
        if eta > 3600:  # Hours
            return f"{eta//3600}h{(eta%3600)//60:02d}m"
        elif eta > 60:  # Minutes
            return f"{eta//60}m{eta%60:02d}s"
        else:  # Seconds
            return f"{eta:2.0f}s"
    
    @staticmethod
    def format_size(bytes_value):
        """Format bytes to human-readable size
        
        Args:
            bytes_value: Size in bytes
            
        Returns:
            Formatted size string (e.g., "256.5MB")
        """
        return f"{bytes_value / 1024 / 1024:.1f}MB"
    
    @staticmethod
    def create_progress_bar(percent, bar_length=30):
        """Create a progress bar with ANSI colors
        
        Args:
            percent: Percentage complete (0-100)
            bar_length: Length of the progress bar
            
        Returns:
            Formatted progress bar string
        """
        filled_length = int(bar_length * percent / 100)
        bar = '━' * filled_length + '░' * (bar_length - filled_length)
        return bar
    
    @staticmethod
    def progress_hook(d):
        """Enhanced progress hook for download status with better formatting and Rich support
        
        Args:
            d: Download status dictionary from yt-dlp
        """
        if d['status'] == 'downloading':
            if 'total_bytes' in d and d['total_bytes']:
                percent = d['downloaded_bytes'] / d['total_bytes'] * 100
                speed = d.get('speed', 0)
                eta = d.get('eta', 0)
                
                # Format speed and ETA
                speed_str = ProgressDisplay.format_speed(speed)
                eta_str = ProgressDisplay.format_eta(eta)
                
                # Calculate downloaded size with better formatting
                downloaded_mb = d['downloaded_bytes'] / 1024 / 1024
                total_mb = d['total_bytes'] / 1024 / 1024
                
                # Create progress bar
                bar = ProgressDisplay.create_progress_bar(percent)
                
                # Use ANSI color codes for compatibility
                # Yellow ▼, Green %, Cyan progress/sizes, Magenta speed, Blue ETA
                progress_line = (
                    f"\r\033[1;33m▼\033[0m "  # Yellow ▼
                    f"\033[1;32m{percent:5.1f}%\033[0m "  # Green %
                    f"[\033[36m{bar[:int(30*percent/100)]}\033[0m"  # Cyan filled
                    f"\033[2;37m{bar[int(30*percent/100):]}\033[0m] "  # Dim white empty
                    f"\033[1;36m{downloaded_mb:6.1f}/{total_mb:6.1f}MB\033[0m "  # Cyan sizes
                    f"| \033[1;35m{speed_str:>10}\033[0m "  # Magenta speed
                    f"| ETA: \033[1;34m{eta_str}\033[0m"  # Blue ETA
                )
                
                print(progress_line, end="", flush=True)
            else:
                # Fallback for unknown total size
                downloaded_mb = d.get('downloaded_bytes', 0) / 1024 / 1024
                speed = d.get('speed', 0)
                speed_str = ProgressDisplay.format_speed(speed)
                
                # Use ANSI colors
                progress_line = (
                    f"\r\033[1;33m▼\033[0m "  # Yellow ▼
                    f"Downloaded: \033[1;36m{downloaded_mb:6.1f}MB\033[0m "  # Cyan size
                    f"| \033[1;35m{speed_str:>10}\033[0m"  # Magenta speed
                )
                
                print(progress_line, end="", flush=True)
                
        elif d['status'] == 'finished':
            filename = os.path.basename(d['filename'])
            # Clear the progress line completely before printing completion
            print("\r" + " " * 120, end="\r", flush=True)
            print(f"\033[1;32m✓\033[0m Download complete: \033[32m{filename}\033[0m")
            
        elif d['status'] == 'error':
            error_msg = d.get('error', 'Unknown error')
            print("\r" + " " * 120, end="\r", flush=True)
            print(f"\033[1;31m✗\033[0m Download error: \033[31m{error_msg}\033[0m")
            
        elif d['status'] == 'processing':
            # Processing happens quickly, no need to show
            pass


class DurationFormatter:
    """Formats time durations to human-readable format"""
    
    @staticmethod
    def format_duration(seconds):
        """Format duration in human readable format
        
        Args:
            seconds: Duration in seconds (int, string, or None)
            
        Returns:
            Formatted duration string (e.g., "1h 30m 45s")
        """
        if not seconds or seconds == 'Unknown':
            return "Unknown"
        
        try:
            seconds = int(seconds)
            hours = seconds // 3600
            minutes = (seconds % 3600) // 60
            secs = seconds % 60
            
            if hours > 0:
                return f"{hours}h {minutes}m {secs}s"
            elif minutes > 0:
                return f"{minutes}m {secs}s"
            else:
                return f"{secs}s"
        except (ValueError, TypeError):
            return "Unknown"
    
    @staticmethod
    def format_duration_short(seconds):
        """Format duration in short format
        
        Args:
            seconds: Duration in seconds
            
        Returns:
            Short formatted string (e.g., "1:30:45")
        """
        if not seconds or seconds == 'Unknown':
            return "00:00"
        
        try:
            seconds = int(seconds)
            hours = seconds // 3600
            minutes = (seconds % 3600) // 60
            secs = seconds % 60
            
            if hours > 0:
                return f"{hours}:{minutes:02d}:{secs:02d}"
            else:
                return f"{minutes}:{secs:02d}"
        except (ValueError, TypeError):
            return "00:00"
