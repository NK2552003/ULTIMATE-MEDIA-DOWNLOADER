#!/usr/bin/env bash

set -e

REPO_URL="https://codeberg.org/nk2552003/umd.git"
REPO_NAME="umd"

echo "🚀 Ultimate Media Downloader Installer"
echo

# Check Git
if ! command -v git >/dev/null 2>&1; then
    echo "❌ Git is not installed."
    echo "Please install Git and try again."
    exit 1
fi

# Clone repository if it doesn't already exist
if [ ! -d "$REPO_NAME" ]; then
    echo "📦 Cloning repository..."
    git clone "$REPO_URL"
else
    echo "📂 Repository already exists."
fi

cd "$REPO_NAME"

chmod +x scripts/install.sh
exec ./scripts/install.sh