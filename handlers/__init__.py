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

__all__ = [
    'SpotifyHandler',
    'AppleMusicHandler',
    'PornhubHandler',
    'XNXXHandler',
    'TumblrHandler',
    'XHamsterHandler',
]
