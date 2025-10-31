#!/usr/bin/env python3
"""
Browser utilities and user agent management

This module provides utilities for browser automation, user agent rotation,
and duration formatting.
"""

import random
from typing import Optional


def get_random_user_agent() -> str:
    """
    Get a random user agent to avoid detection
    
    Returns:
        str: A randomly selected user agent string
    """
    user_agents = [
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 Edg/130.0.0.0',
    ]
    return random.choice(user_agents)


def get_browser_driver() -> Optional[object]:
    """
    Get or create browser driver for enhanced scraping
    
    Note: Returns None as browser automation is unreliable across platforms.
    Use enhanced HTTP scraping instead.
    
    Returns:
        None: Browser automation is not used in this implementation
    """
    # Skip browser automation - it's unreliable across platforms
    # Use enhanced HTTP scraping instead
    return None


def format_duration(seconds: Optional[int]) -> str:
    """
    Format duration in seconds to human-readable format
    
    Args:
        seconds (int/float): Duration in seconds
        
    Returns:
        str: Formatted duration (e.g., "1:23:45" or "1:23")
    """
    if seconds is None:
        return "Unknown"
    
    seconds = int(seconds)
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    
    if hours > 0:
        return f"{hours}:{minutes:02d}:{secs:02d}"
    else:
        return f"{minutes}:{secs:02d}"
