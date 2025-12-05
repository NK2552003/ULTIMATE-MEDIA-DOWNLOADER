"""
Utils package for Ultimate Media Downloader.
Contains utility modules for file management, UI components, progress display, etc.
"""

# Import from utils.py
from .utils import (
    sanitize_filename,
    format_bytes,
    format_duration,
    extract_video_id,
    detect_platform,
    is_playlist_url,
    load_config,
    save_config,
    ensure_directory,
    validate_url,
    clean_string,
    truncate_string
)

# Import from ui_components.py
from .ui_components import (
    Icons,
    Messages,
    ModernUI,
    RICH_AVAILABLE,
    PYFIGLET_AVAILABLE,
    HALO_AVAILABLE
)

# Import from progress_display.py
from .progress_display import ProgressDisplay, DurationFormatter

# Import from file_manager.py
from .file_manager import FileManager

# Import from url_validator.py
from .url_validator import URLValidator

# Import from browser_utils.py
from .browser_utils import (
    get_random_user_agent,
    get_browser_driver,
    format_duration as format_duration_util
)

# Import from platform_utils.py
from .platform_utils import (
    PLATFORM_CONFIGS,
    detect_platform as detect_platform_util,
    get_supported_sites,
    get_platform_config
)

# Import from ui_utils.py
from .ui_utils import RichConsoleWrapper

# Import from ui_display.py
from .ui_display import show_help_menu, create_banner

__all__ = [
    # utils.py
    'sanitize_filename',
    'format_bytes',
    'format_duration',
    'extract_video_id',
    'detect_platform',
    'is_playlist_url',
    'load_config',
    'save_config',
    'ensure_directory',
    'validate_url',
    'clean_string',
    'truncate_string',
    
    # ui_components.py
    'Icons',
    'Messages',
    'ModernUI',
    'RICH_AVAILABLE',
    'PYFIGLET_AVAILABLE',
    'HALO_AVAILABLE',
    
    # progress_display.py
    'ProgressDisplay',
    'DurationFormatter',
    
    # file_manager.py
    'FileManager',
    
    # url_validator.py
    'URLValidator',
    
    # browser_utils.py
    'get_random_user_agent',
    'get_browser_driver',
    'format_duration_util',
    
    # platform_utils.py
    'PLATFORM_CONFIGS',
    'detect_platform_util',
    'get_supported_sites',
    'get_platform_config',
    
    # ui_utils.py
    'RichConsoleWrapper',
    
    # ui_display.py
    'show_help_menu',
    'create_banner',
]
