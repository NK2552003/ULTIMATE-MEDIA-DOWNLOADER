"""
Handlers package for Ultimate Media Downloader.
Contains platform-specific download handlers.
"""

from .spotify_handler import SpotifyHandler
from .jiosaavn_handler import JioSaavnHandler
from .gaana_handler import GaanaHandler
from .apple_music_handler import AppleMusicHandler
from .pornhub_handler import PornhubHandler
from .xnxx_handler import XNXXHandler
from .tumblr_handler import TumblrHandler
from .xhamster_handler import XHamsterHandler
from .hianime_handler import HiAnimeHandler

# Adult site handlers
from .eporner_handler import EpornerHandler
from .hqporner_handler import HQPornerHandler
from .beeg_handler import BeegHandler

# TikTok handler
from .tiktok_handler import TikTokHandler

# Social media handlers
from .linkedin_handler import LinkedInHandler
from .reddit_handler import RedditHandler
from .pinterest_handler import PinterestHandler
from .instagram_handler import InstagramHandler

# Wallpaper handler
from .four_k_wallpapers_handler import FourKWallpapersHandler

__all__ = [
    'SpotifyHandler',
    'JioSaavnHandler',
    'GaanaHandler',
    'AppleMusicHandler',
    'PornhubHandler',
    'XNXXHandler',
    'TumblrHandler',
    'XHamsterHandler',
    'HiAnimeHandler',
    # Adult site handlers
    'EpornerHandler',
    'HQPornerHandler',
    'BeegHandler',
    # TikTok handler
    'TikTokHandler',
    # Social media handlers
    'LinkedInHandler',
    'RedditHandler',
    'PinterestHandler',
    'InstagramHandler',
    # Wallpaper handler
    'FourKWallpapersHandler',
]
