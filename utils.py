#!/usr/bin/env python3
"""
Utility functions for Ultimate Media Downloader
Provides common helper functions used across the application
"""

import os
import re
import json
import warnings
from pathlib import Path
from urllib.parse import urlparse, parse_qs

# Suppress warnings
warnings.filterwarnings('ignore')


def sanitize_filename(filename):
    """
    Sanitize filename by removing or replacing invalid characters
    
    Args:
        filename (str): Original filename
        
    Returns:
        str: Sanitized filename safe for all operating systems
    """
    # Remove or replace invalid characters
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    
    # Remove control characters
    filename = ''.join(char for char in filename if ord(char) >= 32)
    
    # Trim whitespace and dots from ends
    filename = filename.strip('. ')
    
    # Limit length (255 is max for most filesystems, leave room for extension)
    max_length = 200
    if len(filename) > max_length:
        filename = filename[:max_length]
    
    return filename


def format_bytes(bytes_value):
    """
    Format bytes into human-readable format
    
    Args:
        bytes_value (int): Number of bytes
        
    Returns:
        str: Formatted string (e.g., "10.5 MB")
    """
    if bytes_value is None:
        return "Unknown"
    
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_value < 1024.0:
            return f"{bytes_value:.2f} {unit}"
        bytes_value /= 1024.0
    return f"{bytes_value:.2f} PB"


def format_duration(seconds):
    """
    Format duration in seconds to human-readable format
    
    Args:
        seconds (int): Duration in seconds
        
    Returns:
        str: Formatted duration (e.g., "1:23:45")
    """
    if seconds is None:
        return "Unknown"
    
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    
    if hours > 0:
        return f"{hours}:{minutes:02d}:{secs:02d}"
    else:
        return f"{minutes}:{secs:02d}"


def detect_platform(url):
    """
    Detect the platform/service from a URL
    
    Args:
        url (str): URL to analyze
        
    Returns:
        str: Platform name (e.g., 'youtube', 'spotify', 'soundcloud')
    """
    url_lower = url.lower()
    
    # YouTube
    if 'youtube.com' in url_lower or 'youtu.be' in url_lower:
        return 'youtube'
    
    # Spotify
    if 'spotify.com' in url_lower:
        return 'spotify'
    
    # SoundCloud
    if 'soundcloud.com' in url_lower:
        return 'soundcloud'
    
    # Apple Music
    if 'music.apple.com' in url_lower or 'itunes.apple.com' in url_lower:
        return 'apple_music'
    
    # Instagram
    if 'instagram.com' in url_lower:
        return 'instagram'
    
    # TikTok
    if 'tiktok.com' in url_lower:
        return 'tiktok'
    
    # Twitter/X
    if 'twitter.com' in url_lower or 'x.com' in url_lower:
        return 'twitter'
    
    # Facebook
    if 'facebook.com' in url_lower or 'fb.watch' in url_lower:
        return 'facebook'
    
    # Vimeo
    if 'vimeo.com' in url_lower:
        return 'vimeo'
    
    # Dailymotion
    if 'dailymotion.com' in url_lower:
        return 'dailymotion'
    
    # Twitch
    if 'twitch.tv' in url_lower:
        return 'twitch'
    
    return 'generic'


def is_playlist_url(url):
    """
    Check if URL is a playlist/album URL
    
    Args:
        url (str): URL to check
        
    Returns:
        bool: True if URL appears to be a playlist
    """
    url_lower = url.lower()
    
    # YouTube playlists
    if 'youtube.com' in url_lower and ('playlist' in url_lower or 'list=' in url_lower):
        return True
    
    # Spotify playlists/albums
    if 'spotify.com' in url_lower and ('playlist' in url_lower or 'album' in url_lower):
        return True
    
    # SoundCloud playlists
    if 'soundcloud.com' in url_lower and '/sets/' in url_lower:
        return True
    
    # Apple Music playlists/albums
    if 'music.apple.com' in url_lower and ('playlist' in url_lower or 'album' in url_lower):
        return True
    
    return False


def extract_video_id(url):
    """
    Extract video ID from various video platform URLs
    
    Args:
        url (str): Video URL
        
    Returns:
        str or None: Video ID if found
    """
    # YouTube
    if 'youtube.com' in url or 'youtu.be' in url:
        parsed = urlparse(url)
        if 'youtu.be' in url:
            return parsed.path[1:]
        elif 'youtube.com' in url:
            query = parse_qs(parsed.query)
            return query.get('v', [None])[0]
    
    return None


def load_config(config_path='config.json'):
    """
    Load configuration from JSON file
    
    Args:
        config_path (str): Path to config file
        
    Returns:
        dict: Configuration dictionary
    """
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {}
    return {}


def save_config(config, config_path='config.json'):
    """
    Save configuration to JSON file
    
    Args:
        config (dict): Configuration dictionary
        config_path (str): Path to config file
    """
    try:
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=4)
    except Exception as e:
        print(f"Error saving config: {e}")


def ensure_directory(path):
    """
    Ensure directory exists, create if it doesn't
    
    Args:
        path (str or Path): Directory path
        
    Returns:
        Path: Path object of the directory
    """
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_file_extension(filename):
    """
    Get file extension from filename
    
    Args:
        filename (str): Filename
        
    Returns:
        str: File extension without dot
    """
    return Path(filename).suffix.lstrip('.')


def validate_url(url):
    """
    Validate if string is a valid URL
    
    Args:
        url (str): URL to validate
        
    Returns:
        bool: True if valid URL
    """
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False


def clean_string(text):
    """
    Clean string by removing extra whitespace and special characters
    
    Args:
        text (str): Text to clean
        
    Returns:
        str: Cleaned text
    """
    if not text:
        return ""
    
    # Remove extra whitespace
    text = ' '.join(text.split())
    
    # Remove zero-width characters
    text = text.replace('\u200b', '').replace('\u200c', '').replace('\u200d', '')
    
    return text.strip()


def truncate_string(text, max_length=50, suffix='...'):
    """
    Truncate string to maximum length
    
    Args:
        text (str): Text to truncate
        max_length (int): Maximum length
        suffix (str): Suffix to add when truncated
        
    Returns:
        str: Truncated text
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix
