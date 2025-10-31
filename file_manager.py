#!/usr/bin/env python3
"""
File Manager Module
Handles file cleanup and management operations
"""

from pathlib import Path


class FileManager:
    """Manages file operations including cleanup of intermediate files"""
    
    @staticmethod
    def cleanup_intermediate_files(output_dir, info, audio_only=False, output_format=None, keep_file=None):
        """Clean up intermediate files (thumbnails, json, etc.) after download completes
        
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
            
            # Determine the main output file extension
            main_ext = output_format.lower() if output_format else ('mp3' if audio_only else 'mp4')
            main_filename_base = f"{uploader} - {title}"
            
            # Get the actual file we want to keep (absolute path)
            keep_file_path = Path(keep_file).resolve() if keep_file else None
            
            # List of intermediate file extensions to clean up
            intermediate_extensions = [
                '.jpg', '.jpeg', '.png', '.webp',  # Thumbnails
                '.info.json',  # Info JSON
                '.description',  # Description files
                '.annotations.xml',  # Annotations
                '.webm', '.m4a', '.part',  # Temp video/audio files
            ]
            
            # If audio_only, also remove video files that might remain
            if audio_only:
                intermediate_extensions.extend(['.mp4', '.mkv', '.webm', '.avi', '.mov'])
            
            print("\n🧹 Cleaning up intermediate files...")
            cleaned_count = 0
            
            # Convert to Path object if needed
            output_dir = Path(output_dir)
            
            # Search for and remove intermediate files
            for file_path in output_dir.iterdir():
                if file_path.is_file():
                    file_name = file_path.name
                    
                    # NEVER delete the file we want to keep
                    if keep_file_path and file_path.resolve() == keep_file_path:
                        continue
                    
                    # Check if this is an intermediate file related to our download
                    for ext in intermediate_extensions:
                        if file_name.endswith(ext):
                            # Make sure it's related to this download
                            if main_filename_base in file_name or title in file_name:
                                try:
                                    file_path.unlink()
                                    cleaned_count += 1
                                    print(f"  🗑️  Removed: {file_name}")
                                except Exception as e:
                                    print(f"  ⚠  Could not remove {file_name}: {e}")
                                break
            
            if cleaned_count > 0:
                print(f"✓ Cleaned up {cleaned_count} intermediate file(s)")
            else:
                print("✓ No intermediate files to clean")
                
        except Exception as e:
            print(f"⚠  Cleanup error: {e}")
    
    @staticmethod
    def get_file_size(file_path):
        """Get human-readable file size
        
        Args:
            file_path: Path to file
            
        Returns:
            Formatted size string
        """
        try:
            size = Path(file_path).stat().st_size
            
            if size >= 1024 * 1024 * 1024:  # GB
                return f"{size / (1024 * 1024 * 1024):.2f} GB"
            elif size >= 1024 * 1024:  # MB
                return f"{size / (1024 * 1024):.2f} MB"
            elif size >= 1024:  # KB
                return f"{size / 1024:.2f} KB"
            else:
                return f"{size} B"
        except Exception:
            return "Unknown"
    
    @staticmethod
    def ensure_directory(directory):
        """Ensure directory exists, create if it doesn't
        
        Args:
            directory: Directory path
            
        Returns:
            Path object
        """
        dir_path = Path(directory)
        dir_path.mkdir(parents=True, exist_ok=True)
        return dir_path
    
    @staticmethod
    def list_files_by_extension(directory, extension):
        """List all files with given extension in directory
        
        Args:
            directory: Directory to search
            extension: File extension (e.g., '.mp3')
            
        Returns:
            List of file paths
        """
        try:
            dir_path = Path(directory)
            return list(dir_path.glob(f"*{extension}"))
        except Exception:
            return []
    
    @staticmethod
    def safe_delete_file(file_path):
        """Safely delete a file with error handling
        
        Args:
            file_path: Path to file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            Path(file_path).unlink()
            return True
        except Exception as e:
            print(f"⚠  Could not delete {file_path}: {e}")
            return False
    
    @staticmethod
    def clean_directory(directory, extensions=None, exclude_patterns=None):
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
