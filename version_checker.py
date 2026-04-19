#!/usr/bin/env python3
"""
Version Checker and Auto-Updater for Ultimate Media Downloader
Automatically checks for updates and updates the application if needed
"""

import os
import sys
import subprocess
import platform
import json
import requests
from pathlib import Path
from packaging import version
import time

__version__ = "1.0.0"

class VersionChecker:
    """Handles version checking and auto-update functionality"""
    
    def __init__(self):
        self.current_version = None
        self.latest_version = None

     
        self.repo = "nk2552003/umd"
        self.api_url = f"https://codeberg.org/api/v1/repos/{self.repo}/releases/latest"

        self.system = platform.system()
        self.cache_file = Path.home() / ".umd_version_cache.json"
        self.cache_duration = 3600  # Check once per hour
        
    def get_current_version(self):
        """Get the current installed version from the actual installed umd command"""
        try:
            # Method 1: Check pipx installations first (most reliable)
            try:
                result = subprocess.run(['pipx', 'list'], capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    import re
                    for line in result.stdout.split('\n'):
                        if 'ultimate-downloader' in line.lower() or 'ultimate_downloader' in line.lower() or 'umd' in line.lower():
                            version_match = re.search(r'(\d+\.\d+\.\d+)', line.lower())
                            if version_match:
                                self.current_version = version_match.group(1)
                                return self.current_version
            except:
                pass
            
            # Method 2: Try running umd --version command
            import shutil
            umd_path = shutil.which('umd')
            
            if umd_path:
                try:
                    result = subprocess.run(['umd', '--version'], capture_output=True, text=True, timeout=3)
                    if result.returncode == 0 and result.stdout.strip():
                        import re
                        version_match = re.search(r'(\d+\.\d+\.\d+)', result.stdout.strip())
                        if version_match:
                            self.current_version = version_match.group(1)
                            return self.current_version
                except subprocess.TimeoutExpired:
                    pass
                except:
                    pass
            
            # Method 3: Try to import ultimate_downloader
            original_path = sys.path.copy()
            sys.path = [p for p in sys.path if not p.startswith(str(Path(__file__).parent))]
            
            try:
                import ultimate_downloader
                self.current_version = ultimate_downloader.__version__
                sys.path = original_path
                return self.current_version
            except:
                sys.path = original_path
                
        except Exception:
            pass
        
        self.current_version = "0.0.0"
        return self.current_version
    
    def get_latest_version(self):
        """Get the latest version from Codeberg releases"""
        try:
            # Check cache first
            if self._is_cache_valid():
                cached_data = self._read_cache()
                self.latest_version = cached_data.get('latest_version')
                return self.latest_version
            
            # Fetch from Codeberg
            response = requests.get(self.api_url, timeout=10)
            if response.status_code == 200:
                data = response.json()

                # Safe handling (in case releases not configured)
                tag = data.get('tag_name') or data.get('name') or ""
                self.latest_version = tag.lstrip('v') if tag else self.current_version
                
                self._write_cache({'latest_version': self.latest_version, 'timestamp': time.time()})
                return self.latest_version
        except Exception:
            if self._is_cache_valid():
                cached_data = self._read_cache()
                self.latest_version = cached_data.get('latest_version', self.current_version)
            else:
                self.latest_version = self.current_version
            return self.latest_version
    
    def _is_cache_valid(self):
        """Check if cache is still valid"""
        if not self.cache_file.exists():
            return False
        
        try:
            data = self._read_cache()
            timestamp = data.get('timestamp', 0)
            return (time.time() - timestamp) < self.cache_duration
        except:
            return False
    
    def _read_cache(self):
        """Read cached version data"""
        try:
            with open(self.cache_file, 'r') as f:
                return json.load(f)
        except:
            return {}
    
    def _write_cache(self, data):
        """Write version data to cache"""
        try:
            with open(self.cache_file, 'w') as f:
                json.dump(data, f)
        except:
            pass
    
    def is_update_available(self):
        """Check if an update is available"""
        try:
            current = version.parse(self.current_version)
            latest = version.parse(self.latest_version)
            return latest > current
        except:
            return False
    
    def update_application(self):
        """Update the application to the latest version"""
        try:
            print(f"\nUpdating Ultimate Media Downloader from v{self.current_version} to v{self.latest_version}...")
            
            install_dir = Path(__file__).parent
            
            if self.system == "Windows":
                update_script = install_dir / "scripts" / "update.bat"
                if update_script.exists():
                    result = subprocess.run([str(update_script)], shell=True, capture_output=True, text=True)
                else:
                    try:
                        subprocess.run(["pipx", "uninstall", "ultimate-downloader"], capture_output=True)
                        result = subprocess.run([
                            "pipx", "install",
                            f"git+https://codeberg.org/{self.repo}.git"
                        ], capture_output=True, text=True)
                    except:
                        subprocess.run([sys.executable, "-m", "pip", "uninstall", "-y", "ultimate-downloader"], capture_output=True)
                        result = subprocess.run([
                            sys.executable, "-m", "pip", "install", "--user",
                            f"git+https://codeberg.org/{self.repo}.git"
                        ], capture_output=True, text=True)
            else:
                update_script = install_dir / "scripts" / "update.sh"
                if update_script.exists():
                    result = subprocess.run(["bash", str(update_script)], capture_output=True, text=True)
                else:
                    try:
                        subprocess.run(["pipx", "uninstall", "ultimate-downloader"], capture_output=True)
                        result = subprocess.run([
                            "pipx", "install",
                            f"git+https://codeberg.org/{self.repo}.git"
                        ], capture_output=True, text=True)
                    except:
                        subprocess.run([sys.executable, "-m", "pip", "uninstall", "-y", "ultimate-downloader"], capture_output=True)
                        result = subprocess.run([
                            sys.executable, "-m", "pip", "install", "--user",
                            f"git+https://codeberg.org/{self.repo}.git"
                        ], capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"Successfully updated to v{self.latest_version}")
                if self.cache_file.exists():
                    self.cache_file.unlink()
                return True
            else:
                print(f"❌ Update failed: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"Update failed: {str(e)}")
            return False
    
    def check_and_update(self, auto_update=True):
        """Check for updates and optionally auto-update"""
        try:
            self.get_current_version()
            self.get_latest_version()
            
            if self.is_update_available():
                print(f"\nNew version available: v{self.latest_version} (current: v{self.current_version})")
                
                if auto_update:
                    user_input = input("Would you like to update now? (Y/n): ").strip().lower()
                    if user_input in ['', 'y', 'yes']:
                        success = self.update_application()
                        if success:
                            print("\n✨ Update complete! Please restart the application.")
                            print("Run 'umd' again to use the latest version.\n")
                            sys.exit(0)
                        else:
                            print("\nContinuing with current version...\n")
                    else:
                        print("\nUpdate skipped. You can update later by running:\n")
                        print(f"pip install --upgrade git+https://codeberg.org/{self.repo}.git\n")
                else:
                    print(f"ℹ To update, run: pip install --upgrade git+https://codeberg.org/{self.repo}.git\n")
            else:
                pass
                
        except Exception:
            pass

def check_for_updates(auto_update=True):
    """Main function to check for updates"""
    checker = VersionChecker()
    checker.check_and_update(auto_update=auto_update)

if __name__ == "__main__":
    check_for_updates()