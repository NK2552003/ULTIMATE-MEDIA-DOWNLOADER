#!/usr/bin/env python3
"""
Setup script for Ultimate Media Downloader
Installs the package as a CLI tool that can be run with a single command
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the long description from README
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8')

# Read requirements
requirements = []
with open('requirements.txt', 'r') as f:
    requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]

setup(
    name='ultimate-downloader',
    version='2.0.0',
    description='A powerful, feature-rich media downloader supporting 1000+ platforms',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='NK2552003',
    author_email='',
    url='https://github.com/NK2552003/ULTIMATE-MEDIA-DOWNLOADER',
    license='MIT',
    py_modules=[
        'ultimate_downloader',
        'logger',
        'utils',
        'ui_components',
        'ui_display',
        'cli_args',
        'youtube_scorer',
        'generic_downloader',
        'spotify_handler',
        'apple_music_handler',
        'progress_display',
        'file_manager',
        'url_validator',
        'platform_info',
        'browser_utils',
        'platform_utils',
        'ui_utils'
    ],
    install_requires=requirements,
    entry_points={
        'console_scripts': [
            'umd=ultimate_downloader:main',
        ],
    },
    python_requires='>=3.9',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Topic :: Multimedia :: Sound/Audio',
        'Topic :: Multimedia :: Video',
    ],
    keywords='youtube downloader spotify music video audio media instagram tiktok',
)
