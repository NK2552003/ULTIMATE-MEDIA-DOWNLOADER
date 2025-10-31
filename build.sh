#!/bin/bash
# Build script for testing PyInstaller locally

echo "Building Ultimate Media Downloader executable..."

# Install PyInstaller if not already installed
pip install pyinstaller

# Build the executable
pyinstaller ultimate_downloader.spec

echo "Build complete! Check the 'dist' directory for the executable."