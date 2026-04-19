#!/usr/bin/env python3
"""
File Manager Module
Handles file cleanup and management operations
"""

import os
import sys
from pathlib import Path


class FileManager:
    """Manages file operations including cleanup of intermediate files"""
    
    @staticmethod
    def cleanup_intermediate_files(output_dir, info, audio_only=False, output_format=None, keep_file=None):
        """Aggressively clean up intermediate files (thumbnails, .prefix, etc.) after download completes
        Args:
            output_dir: Output directory path
            info: Download info dictionary
            audio_only: Whether download was audio-only
            output_format: Output format used
            keep_file: File path to keep (don't delete)
        """
        try:
            if not info:
                return
            title = info.get('title', 'Unknown')
            uploader = info.get('uploader', 'Unknown')
            main_ext = output_format.lower() if output_format else ('mp3' if audio_only else 'mp4')
            main_filename_base = f"{uploader} - {title}"
            keep_file_path = Path(keep_file).resolve() if keep_file else None
            # Aggressive cleanup: all thumbnail, .prefix, and temp files
            intermediate_patterns = [
                '*.jpg', '*.jpeg', '*.png', '*.webp', '*.info.json', '*.description', '*.annotations.xml',
                '*.webm', '*.m4a', '*.part', '*.prefix', '*.tmp', '*.temp', '*.cache', '*.thm', '*.tbn', '*.bmp'
            ]
            if audio_only:
                intermediate_patterns.extend(['*.mp4', '*.mkv', '*.webm', '*.avi', '*.mov'])
            print("\n🧹 Aggressively cleaning up intermediate files...")
            cleaned_count = 0
            output_dir = Path(output_dir)
            for pattern in intermediate_patterns:
                for file_path in output_dir.glob(pattern):
                    if file_path.is_file():
                        file_name = file_path.name
                        # NEVER delete the file we want to keep
                        if keep_file_path and file_path.resolve() == keep_file_path:
                            continue
                        # Only delete if related to this download (by title or uploader or main file base)
                        if (main_filename_base in file_name or title in file_name or uploader in file_name):
                            try:
                                file_path.unlink()
                                cleaned_count += 1
                                print(f"  🗑️  Removed: {file_name}")
                            except Exception as e:
                                print(f"  ⚠  Could not remove {file_name}: {e}")
            if cleaned_count > 0:
                print(f"✓ Cleaned up {cleaned_count} intermediate file(s)")
            else:
                print("✓ No intermediate files to clean")
        except Exception as e:
            print(f"⚠  Cleanup error: {e}")
    
    @staticmethod
    @staticmethod
    def cleanup_intermediate_files(output_dir, info, audio_only=False, output_format=None, keep_file=None):
        """Aggressively clean up all intermediate files (thumbnails, .prefix, etc.) after download completes
        Args:
            output_dir: Output directory path
            info: Download info dictionary
            audio_only: Whether download was audio-only
            output_format: Output format used
            keep_file: File path to keep (don't delete)
        """
        try:
            if not info:
                return

            title = info.get('title', 'Unknown')
            uploader = info.get('uploader', 'Unknown')
            main_ext = output_format.lower() if output_format else ('mp3' if audio_only else 'mp4')
            main_filename_base = f"{uploader} - {title}"
            keep_file_path = Path(keep_file).resolve() if keep_file else None

            # Aggressive extensions and prefixes to remove
            thumbnail_exts = ['.jpg', '.jpeg', '.png', '.webp']
            prefix_exts = ['.info.json', '.description', '.annotations.xml', '.webm', '.m4a', '.part', '.temp', '.cache', '.nfo']
            # Remove video files if audio_only
            if audio_only:
                prefix_exts.extend(['.mp4', '.mkv', '.webm', '.avi', '.mov'])

            print("\n🧹 Aggressively cleaning up intermediate files...")
            cleaned_count = 0
            output_dir = Path(output_dir)

            # Remove all thumbnails and .prefix files with same base name
            for file_path in output_dir.iterdir():
                if not file_path.is_file():
                    continue
                file_name = file_path.name
                # NEVER delete the file we want to keep
                if keep_file_path and file_path.resolve() == keep_file_path:
                    continue

                # Remove thumbnails and .prefix files related to this download
                base_match = (main_filename_base in file_name or title in file_name)
                ext = file_path.suffix.lower()
                # Remove thumbnails
                if ext in thumbnail_exts and base_match:
                    try:
                        file_path.unlink()
                        cleaned_count += 1
                        print(f"  🗑️  Removed thumbnail: {file_name}")
                    except Exception as e:
                        print(f"  ⚠  Could not remove {file_name}: {e}")
                    continue
                # Remove .prefix files
                for pfx in prefix_exts:
                    if file_name.endswith(pfx) and base_match:
                        try:
                            file_path.unlink()
                            cleaned_count += 1
                            print(f"  🗑️  Removed: {file_name}")
                        except Exception as e:
                            print(f"  ⚠  Could not remove {file_name}: {e}")
                        break

            # Also remove any thumbnails with the same stem as the main file (e.g., song.mp3 → song.jpg/png/webp)
            if keep_file_path:
                stem = keep_file_path.stem
                for ext in thumbnail_exts:
                    thumb_path = keep_file_path.with_suffix(ext)
                    if thumb_path.exists():
                        try:
                            thumb_path.unlink()
                            cleaned_count += 1
                            print(f"  🗑️  Removed: {thumb_path.name}")
                        except Exception as e:
                            print(f"  ⚠  Could not remove {thumb_path.name}: {e}")

            if cleaned_count > 0:
                print(f"✓ Cleaned up {cleaned_count} intermediate file(s)")
            else:
                print("✓ No intermediate files to clean")
        except Exception as e:
            print(f"⚠  Cleanup error: {e}")
        """Clean directory by removing files with specified extensions
        
        Args:
            directory: Directory to clean
            extensions: List of extensions to remove (e.g., ['.json', '.jpg'])
            exclude_patterns: List of patterns to exclude
            
        Returns:
            Number of files removed
        """
        try:
            count = 0
            dir_path = Path(directory)
            
            if not extensions:
                extensions = ['.json', '.jpg', '.png', '.webp', '.part']
            
            if not exclude_patterns:
                exclude_patterns = []
            
            for file_path in dir_path.iterdir():
                if file_path.is_file():
                    # Check if file should be excluded
                    should_exclude = any(pattern in file_path.name for pattern in exclude_patterns)
                    if should_exclude:
                        continue
                    
                    # Check if file has one of the target extensions
                    if any(file_path.name.endswith(ext) for ext in extensions):
                        if FileManager.safe_delete_file(file_path):
                            count += 1
            
            return count
        except Exception as e:
            print(f"⚠  Error cleaning directory: {e}")
            return 0

    @staticmethod
    def remove_macos_quarantine(file_path):
        """Remove macOS quarantine attribute from a file if present.

        Returns:
            tuple(bool, str): (changed, message)
        """
        try:
            if sys.platform != 'darwin':
                return False, "not-macos"

            target = Path(file_path)
            if not target.exists() or not target.is_file():
                return False, "file-not-found"

            if not hasattr(os, 'listxattr') or not hasattr(os, 'removexattr'):
                return False, "xattr-not-supported"

            attrs = os.listxattr(str(target))
            quarantine_attr = 'com.apple.quarantine'

            if quarantine_attr not in attrs:
                return False, "no-quarantine-attribute"

            os.removexattr(str(target), quarantine_attr)
            return True, "quarantine-removed"
        except OSError as exc:
            return False, f"os-error: {exc}"
        except Exception as exc:
            return False, f"error: {exc}"

    @staticmethod
    def remove_windows_zone_identifier(file_path):
        """Remove Windows Mark-of-the-Web (Zone.Identifier) alternate data stream.

        Returns:
            tuple(bool, str): (changed, message)
        """
        try:
            if os.name != 'nt':
                return False, "not-windows"

            target = Path(file_path)
            if not target.exists() or not target.is_file():
                return False, "file-not-found"

            # On NTFS, internet zone metadata is stored in this ADS stream.
            zone_identifier_path = f"{target}:Zone.Identifier"
            try:
                os.remove(zone_identifier_path)
                return True, "zone-identifier-removed"
            except FileNotFoundError:
                return False, "no-zone-identifier"
            except OSError as exc:
                return False, f"os-error: {exc}"
        except Exception as exc:
            return False, f"error: {exc}"

    @staticmethod
    def remove_linux_download_markers(file_path):
        """Remove Linux desktop download origin xattrs when present.

        Returns:
            tuple(bool, str): (changed, message)
        """
        try:
            if sys.platform.startswith('linux') is False:
                return False, "not-linux"

            target = Path(file_path)
            if not target.exists() or not target.is_file():
                return False, "file-not-found"

            if not hasattr(os, 'listxattr') or not hasattr(os, 'removexattr'):
                return False, "xattr-not-supported"

            attrs = os.listxattr(str(target))
            marker_attrs = ['user.xdg.origin.url', 'user.xdg.referrer.url']
            removed_any = False

            for attr in marker_attrs:
                if attr in attrs:
                    os.removexattr(str(target), attr)
                    removed_any = True

            if removed_any:
                return True, "linux-download-markers-removed"

            return False, "no-linux-download-markers"
        except OSError as exc:
            return False, f"os-error: {exc}"
        except Exception as exc:
            return False, f"error: {exc}"

    @staticmethod
    def remove_platform_download_security_markers(file_path):
        """Remove OS-specific download security markers where possible.

        Returns:
            tuple(bool, str): (changed, message)
        """
        if sys.platform == 'darwin':
            return FileManager.remove_macos_quarantine(file_path)

        if os.name == 'nt':
            return FileManager.remove_windows_zone_identifier(file_path)

        if sys.platform.startswith('linux'):
            return FileManager.remove_linux_download_markers(file_path)

        return False, "unsupported-platform"
