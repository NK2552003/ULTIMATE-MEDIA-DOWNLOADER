#!/usr/bin/env python3
"""
Generate all favicon/icon sizes from umd_logo.png using only stdlib (no PIL fallback to sips on macOS).
Run: python3 scripts/generate_favicons.py
"""
import subprocess
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
SOURCE = os.path.join(PROJECT_ROOT, "public", "umd_logo.png")
ICONS_DIR = os.path.join(PROJECT_ROOT, "public", "icons")

os.makedirs(ICONS_DIR, exist_ok=True)

SIZES = [16, 32, 48, 72, 96, 128, 144, 152, 180, 192, 256, 384, 512]

def resize_with_sips(src, dst, size):
    """Use macOS sips to resize."""
    import shutil
    shutil.copy(src, dst)
    result = subprocess.run(
        ["sips", "-z", str(size), str(size), dst],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        print(f"  ✗ sips failed for {size}x{size}: {result.stderr}")
        return False
    return True

def try_with_imagemagick(src, dst, size):
    """Try ImageMagick convert."""
    result = subprocess.run(
        ["convert", src, "-resize", f"{size}x{size}", dst],
        capture_output=True, text=True
    )
    return result.returncode == 0

print(f"Generating favicons from: {SOURCE}")
print(f"Output directory: {ICONS_DIR}\n")

for size in SIZES:
    dst = os.path.join(ICONS_DIR, f"icon-{size}x{size}.png")
    
    # Use macOS sips (always available on macOS)
    success = resize_with_sips(SOURCE, dst, size)
    
    if success:
        print(f"  ✓ icon-{size}x{size}.png")
    else:
        print(f"  ✗ FAILED icon-{size}x{size}.png")

# Also copy 32x32 as favicon.ico equivalent (PNG named favicon)
import shutil
shutil.copy(os.path.join(ICONS_DIR, "icon-32x32.png"), os.path.join(PROJECT_ROOT, "public", "favicon.png"))
shutil.copy(os.path.join(ICONS_DIR, "icon-180x180.png"), os.path.join(PROJECT_ROOT, "public", "apple-touch-icon.png"))
shutil.copy(os.path.join(ICONS_DIR, "icon-192x192.png"), os.path.join(PROJECT_ROOT, "public", "android-chrome-192x192.png"))
shutil.copy(os.path.join(ICONS_DIR, "icon-512x512.png"), os.path.join(PROJECT_ROOT, "public", "android-chrome-512x512.png"))
shutil.copy(os.path.join(ICONS_DIR, "icon-32x32.png"), os.path.join(PROJECT_ROOT, "public", "favicon-32x32.png"))
shutil.copy(os.path.join(ICONS_DIR, "icon-16x16.png"), os.path.join(PROJECT_ROOT, "public", "favicon-16x16.png"))

print("\n✓ Done! Special copies:")
print("  → favicon.png (32x32)")
print("  → apple-touch-icon.png (180x180)")
print("  → android-chrome-192x192.png")
print("  → android-chrome-512x512.png")
print("  → favicon-32x32.png")
print("  → favicon-16x16.png")
