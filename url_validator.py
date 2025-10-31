#!/usr/bin/env python3
"""
URL Validator Module
Handles URL validation and support checking
"""

import yt_dlp


class URLValidator:
    """Validates URLs and checks platform support"""
    
    def __init__(self, platform_configs=None):
        """Initialize URL validator
        
        Args:
            platform_configs: Dictionary of platform configurations
        """
        self.platform_configs = platform_configs or {}
    
    @staticmethod
    def is_valid_url(url):
        """Check if URL is valid
        
        Args:
            url: URL string to validate
            
        Returns:
            True if valid HTTP/HTTPS URL, False otherwise
        """
        if not url:
            return False
        
        url = url.strip()
        return url.startswith(('http://', 'https://'))
    
    def check_url_support(self, url, detect_platform_func=None, silent=False):
        """Check if URL is supported by any extractor
        
        Args:
            url: URL to check
            detect_platform_func: Function to detect platform from URL
            silent: Don't print information messages
            
        Returns:
            True if supported, False otherwise
        """
        try:
            # Detect platform if function provided
            platform = None
            if detect_platform_func:
                platform = detect_platform_func(url)
                if not silent:
                    print(f"◎ Detected platform: {platform.upper()}")
            
            # Treat Apple Music and Spotify as supported (handled via search/metadata)
            if platform in ("apple_music", "spotify"):
                if not silent:
                    print("✓ URL supported via enhanced handler (YouTube search + metadata)")
                return True
            
            # Try to extract info to check if URL is supported
            with yt_dlp.YoutubeDL({'quiet': True, 'no_warnings': True}) as ydl:
                try:
                    # Try to extract basic info without downloading
                    info = ydl.extract_info(url, download=False, process=False)
                    if info:
                        extractor_name = info.get('extractor', 'Unknown')
                        if not silent:
                            print(f"✓ URL supported by extractor: {extractor_name}")
                        
                        # Show basic info if available
                        if info.get('title') and not silent:
                            print(f"▶ Title: {info.get('title')}")
                        if info.get('uploader') and not silent:
                            print(f"◈ Uploader: {info.get('uploader')}")
                        
                        # Show platform-specific info
                        if platform and platform in self.platform_configs and not silent:
                            config = self.platform_configs[platform]
                            print(f"≡ Supported formats: {', '.join(config['formats'])}")
                            if 'note' in config:
                                print(f"▭ Note: {config['note']}")
                        
                        return True
                    else:
                        if not silent:
                            print("✗ URL not supported - no info extracted")
                        return False
                        
                except yt_dlp.DownloadError as e:
                    if "Unsupported URL" in str(e) or "No suitable extractor" in str(e):
                        if not silent:
                            print("✗ URL not supported by any extractor")
                            print(f"→ Tip: Try checking if the URL is correct and accessible")
                        return False
                    else:
                        # Other errors might still mean the URL is supported
                        if not silent:
                            print(f"⚠  URL might be supported but encountered error: {e}")
                        return True
                        
        except Exception as e:
            if not silent:
                print(f"✗ Error checking URL support: {e}")
                print("→ Tip: The URL might still work, try downloading it directly")
            return False
    
    @staticmethod
    def extract_video_id(url):
        """Extract video ID from URL if possible
        
        Args:
            url: URL string
            
        Returns:
            Video ID or None
        """
        try:
            # YouTube video ID
            if 'youtube.com' in url or 'youtu.be' in url:
                if 'v=' in url:
                    return url.split('v=')[1].split('&')[0]
                elif 'youtu.be/' in url:
                    return url.split('youtu.be/')[1].split('?')[0]
            
            # Spotify track ID
            if 'spotify.com' in url:
                if '/track/' in url:
                    return url.split('/track/')[1].split('?')[0]
            
            # TikTok video ID
            if 'tiktok.com' in url:
                if '/video/' in url:
                    return url.split('/video/')[1].split('?')[0]
        except Exception:
            pass
        
        return None
    
    @staticmethod
    def is_playlist_url(url):
        """Check if URL is a playlist
        
        Args:
            url: URL to check
            
        Returns:
            True if playlist, False otherwise
        """
        playlist_indicators = [
            'playlist',  # YouTube playlists
            'list=',     # YouTube playlist parameter
            'album',     # Spotify albums
            'mix',       # YouTube mixes/radios
            'RD',        # YouTube radio
        ]
        
        return any(indicator in url.lower() for indicator in playlist_indicators)
    
    @staticmethod
    def normalize_url(url):
        """Normalize URL for consistent handling
        
        Args:
            url: URL string
            
        Returns:
            Normalized URL
        """
        if not url:
            return None
        
        url = url.strip()
        
        # Add https:// if protocol missing
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        return url
    
    def get_url_info(self, url):
        """Get basic information about URL
        
        Args:
            url: URL to analyze
            
        Returns:
            Dictionary with URL information
        """
        info = {
            'url': url,
            'valid': self.is_valid_url(url),
            'is_playlist': self.is_playlist_url(url),
            'video_id': self.extract_video_id(url),
        }
        
        return info
