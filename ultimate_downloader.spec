# -*- mode: python ; coding: utf-8 -*-

import os
import sys
from pathlib import Path

# Get the project root directory
project_root = Path(__file__).parent

a = Analysis(
    ['ultimate_downloader.py'],
    pathex=[str(project_root)],
    binaries=[],
    datas=[
        # Include config files
        (str(project_root / 'config.json'), '.'),
        # Include any other data files if needed
    ],
    hiddenimports=[
        # Core dependencies
        'yt_dlp',
        'requests',
        'rich',
        'colorama',
        'pyfiglet',
        'emoji',
        'halo',
        'mutagen',
        'PIL',
        'spotipy',
        'youtube_search_python',
        'spotdl',
        'cloudscraper',
        'httpx',
        'curl_cffi',
        'fake_useragent',
        'requests_html',
        'beautifulsoup4',
        'lxml',
        'selenium',
        'undetected_chromedriver',
        'webdriver_manager',
        'playwright',
        # Platform handlers
        'spotify_handler',
        'apple_music_handler',
        'youtube_scorer',
        'generic_downloader',
        # Utility modules
        'logger',
        'utils',
        'ui_components',
        'ui_display',
        'cli_args',
        'progress_display',
        'file_manager',
        'url_validator',
        'platform_info',
        'browser_utils',
        'platform_utils',
        'ui_utils',
        # Additional hidden imports for yt-dlp and related
        'yt_dlp.extractor',
        'yt_dlp.downloader',
        'yt_dlp.postprocessor',
        # Selenium and browser automation
        'selenium.webdriver',
        'selenium.webdriver.chrome',
        'selenium.webdriver.firefox',
        'undetected_chromedriver',
        # Mutagen formats
        'mutagen.flac',
        'mutagen.mp3',
        'mutagen.id3',
        'mutagen.mp4',
        'mutagen.wave',
        # Other potential hidden imports
        'urllib3',
        'concurrent.futures',
        'subprocess',
        'shutil',
        'pathlib',
        'datetime',
        'urllib.parse',
        'json',
        're',
        'threading',
        'signal',
        'warnings',
        'io',
        'argparse',
        'time',
        'os',
        'sys',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # Exclude unnecessary modules to reduce size
        'tkinter',
        'unittest',
        'pdb',
        'pydoc',
        'test',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='ultimate-downloader',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # Add icon if available
)