#!/usr/bin/env python3
"""
Platform detection and configuration management

This module provides platform detection utilities and stores platform-specific
configurations for supported media platforms.
"""

import re
from typing import Dict, List, Any, Optional


# Platform-specific configurations
PLATFORM_CONFIGS = {
    'youtube': {
        'extractors': ['youtube', 'youtu.be'],
        'formats': ['mp4', 'webm', 'mp3', 'wav', 'flac']
    },
    'spotify': {
        'extractors': ['spotify'],
        'formats': ['mp3', 'wav', 'flac'],
        'note': 'Spotify tracks will be searched on YouTube for download'
    },
    'jiosaavn': {
        'extractors': ['jiosaavn', 'saavn'],
        'formats': ['mp3', 'wav', 'flac'],
        'note': 'JioSaavn tracks will be searched on YouTube for download'
    },
    'gaana': {
        'extractors': ['gaana'],
        'formats': ['mp3', 'wav', 'flac'],
        'note': 'Gaana tracks will be searched on YouTube for download'
    },
    'soundcloud': {
        'extractors': ['soundcloud'],
        'formats': ['mp3', 'wav', 'flac']
    },
    'apple_music': {
        'extractors': ['apple', 'itunes'],
        'formats': ['mp3', 'wav', 'flac'],
        'note': 'Apple Music tracks will be searched on YouTube for download'
    },
    'pornhub': {
        'extractors': ['pornhub', 'pornhubpremium'],
        'formats': ['mp4', 'webm'],
        'note': 'Pornhub videos, GIFs, albums, and channels'
    },
    'xnxx': {
        'extractors': ['xnxx'],
        'formats': ['mp4', 'webm'],
        'note': 'XNXX videos from xnxx.com, xnxx.dev, xnxx.tv'
    },
    'tumblr': {
        'extractors': ['tumblr'],
        'formats': ['jpg', 'png', 'gif', 'mp4'],
        'note': 'Tumblr blogs - images and videos'
    },
    'xhamster': {
        'extractors': ['xhamster'],
        'formats': ['mp4', 'webm', 'jpg', 'png'],
        'note': 'xHamster videos, channels, and photo galleries'
    },
    'hianime': {
        'extractors': ['hianime', 'aniwatch', 'zoro'],
        'formats': ['mp4', 'mkv'],
        'note': 'HiAnime.to anime streaming - episodes and series'
    },
    # New adult site configurations
    'eporner': {
        'extractors': ['eporner'],
        'formats': ['mp4', 'webm'],
        'note': 'Eporner videos with quality selection'
    },
    'hqporner': {
        'extractors': ['hqporner'],
        'formats': ['mp4', 'webm'],
        'note': 'HQPorner HD videos'
    },
    'beeg': {
        'extractors': ['beeg'],
        'formats': ['mp4', 'webm'],
        'note': 'Beeg videos'
    },
    # TikTok platform
    'tiktok': {
        'extractors': ['tiktok'],
        'formats': ['mp4'],
        'note': 'TikTok videos with watermark removal option'
    },
    # Social media platforms
    'linkedin': {
        'extractors': ['linkedin'],
        'formats': ['mp4', 'jpg', 'png'],
        'note': 'LinkedIn posts and user profiles - videos and images'
    },
    'reddit': {
        'extractors': ['reddit'],
        'formats': ['mp4', 'jpg', 'png', 'gif'],
        'note': 'Reddit posts and user content - videos, images, and GIFs'
    },
    'pinterest': {
        'extractors': ['pinterest'],
        'formats': ['jpg', 'png', 'mp4'],
        'note': 'Pinterest pins, boards, and user profiles - images and videos'
    },
    'generic': {
        'extractors': ['generic'],
        'formats': ['mp4', 'mp3', 'wav']
    }
}

# Supported sites list
SUPPORTED_SITES = [
    {'name': 'YouTube', 'description': 'YouTube videos, playlists, channels'},
    {'name': 'Spotify', 'description': 'Spotify tracks, albums, playlists (via YouTube search)'},
    {'name': 'JioSaavn', 'description': 'JioSaavn songs, albums, playlists (via YouTube search)'},
    {'name': 'Gaana', 'description': 'Gaana songs, albums, playlists (via YouTube search)'},
    {'name': 'SoundCloud', 'description': 'SoundCloud tracks and playlists'},
    {'name': 'TikTok', 'description': 'TikTok videos with watermark removal'},
    {'name': 'Instagram', 'description': 'Instagram posts, reels, IGTV'},
    {'name': 'Twitter', 'description': 'Twitter videos'},
    {'name': 'Facebook', 'description': 'Facebook videos'},
    {'name': 'Vimeo', 'description': 'Vimeo videos'},
    {'name': 'Twitch', 'description': 'Twitch VODs and clips'},
    {'name': 'Apple Music', 'description': 'Apple Music tracks (via YouTube search)'},
    {'name': 'Pornhub', 'description': 'Pornhub videos, GIFs, albums, channels, models'},
    {'name': 'XNXX', 'description': 'XNXX videos (xnxx.com, xnxx.dev, xnxx.tv)'},
    {'name': 'Tumblr', 'description': 'Tumblr blogs - images and videos'},
    {'name': 'xHamster', 'description': 'xHamster videos, channels, photo galleries'},
    {'name': 'HiAnime', 'description': 'HiAnime.to anime streaming (episodes, series)'},
    # New adult sites
    {'name': 'Eporner', 'description': 'Eporner HD videos with quality selection'},
    {'name': 'HQPorner', 'description': 'HQPorner HD videos'},
    {'name': 'Beeg', 'description': 'Beeg videos'},
    {'name': 'TikTok', 'description': 'TikTok videos with watermark removal'},
    # Social media platforms
    {'name': 'LinkedIn', 'description': 'LinkedIn posts and profiles - videos and images'},
    {'name': 'Reddit', 'description': 'Reddit posts and user content - videos, images, GIFs'},
    {'name': 'Pinterest', 'description': 'Pinterest pins, boards, and profiles - images and videos'},
    {'name': 'Generic', 'description': 'many other video and audio platforms'}
]


def detect_platform(url: str) -> str:
    """
    Detect the media platform from a given URL
    
    Args:
        url (str): The URL to analyze
        
    Returns:
        str: Platform name ('youtube', 'spotify', 'soundcloud', 'apple_music', 'pornhub', 'social_media', 'generic')
    """
    url_lower = url.lower()
    
    if any(domain in url_lower for domain in ['youtube.com', 'youtu.be', 'm.youtube.com']):
        return 'youtube'
    elif 'spotify.com' in url_lower:
        return 'spotify'
    elif any(domain in url_lower for domain in ['jiosaavn.com', 'jiosvn.com']):
        return 'jiosaavn'
    elif 'gaana.com' in url_lower:
        return 'gaana'
    elif 'soundcloud.com' in url_lower:
        return 'soundcloud'
    elif any(domain in url_lower for domain in ['music.apple.com', 'itunes.apple.com']):
        return 'apple_music'
    elif any(domain in url_lower for domain in ['pornhub.com', 'pornhubpremium.com']):
        return 'pornhub'
    elif any(domain in url_lower for domain in ['xnxx.com', 'xnxx.dev', 'xnxx.tv']) or re.search(r'xnxx\d*\.(com|dev|tv|es)', url_lower):
        return 'xnxx'
    elif 'tumblr.com' in url_lower:
        return 'tumblr'
    elif re.search(r'(xhamster|xhwebsite|xhofficial|xhlocal|xhopen|xhtotal|megaxh|xhwide|xhtab|xhtime)\d*\.', url_lower):
        return 'xhamster'
    elif any(domain in url_lower for domain in ['hianime.to', 'hianime.sx', 'hianime.mn', 'aniwatch.to', 'zoro.to', 'kaido.to']):
        return 'hianime'
    # New adult sites
    elif 'eporner.com' in url_lower:
        return 'eporner'
    elif 'hqporner.com' in url_lower:
        return 'hqporner'
    elif 'beeg.com' in url_lower:
        return 'beeg'
    # TikTok
    elif 'tiktok.com' in url_lower:
        return 'tiktok'
    # Social media platforms
    elif 'linkedin.com' in url_lower:
        return 'linkedin'
    elif any(domain in url_lower for domain in ['reddit.com', 'redd.it']):
        return 'reddit'
    elif any(domain in url_lower for domain in ['pinterest.com', 'pin.it']):
        return 'pinterest'
    elif any(domain in url_lower for domain in ['instagram.com', 'facebook.com', 'twitter.com', 'x.com']):
        return 'social_media'
    else:
        return 'generic'


def get_platform_config(platform: str) -> Dict[str, Any]:
    """
    Get configuration for a specific platform
    
    Args:
        platform (str): Platform name
        
    Returns:
        dict: Platform configuration or empty dict if not found
    """
    return PLATFORM_CONFIGS.get(platform, {})


def get_supported_sites() -> List[Dict[str, str]]:
    """
    Get list of all supported sites
    
    Returns:
        list: List of dictionaries with site info (name, description)
    """
    return SUPPORTED_SITES.copy()


def is_supported_platform(platform: str) -> bool:
    """
    Check if a platform is supported
    
    Args:
        platform (str): Platform name to check
        
    Returns:
        bool: True if platform is supported, False otherwise
    """
    return platform in PLATFORM_CONFIGS


def get_all_platform_names() -> List[str]:
    """
    Get all supported platform names
    
    Returns:
        list: List of platform names
    """
    return list(PLATFORM_CONFIGS.keys())
