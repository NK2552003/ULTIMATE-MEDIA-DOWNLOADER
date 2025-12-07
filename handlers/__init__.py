"""
Handlers package for Ultimate Media Downloader.
Contains platform-specific download handlers.
"""

from .spotify_handler import SpotifyHandler
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

__all__ = [
    'SpotifyHandler',
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
]
