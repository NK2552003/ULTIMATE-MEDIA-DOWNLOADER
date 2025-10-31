@echo off
REM =============================================================================
REM Ultimate Media Downloader - Environment Activation Script
REM Version: 2.0.0
REM Date: October 2025
REM Description: Activates the virtual environment with all modules and deps
REM =============================================================================

echo ========================================================================
echo    Activating Ultimate Media Downloader Environment
echo ========================================================================
echo.

if exist "%~dp0venv\Scripts\activate.bat" (
    call "%~dp0venv\Scripts\activate.bat"
    echo [SUCCESS] Virtual environment activated
    echo.
    
    echo Loaded Core Modules:
    echo   - ultimate_downloader    (Main downloader engine)
    echo   - cli_args              (Command-line argument parser)
    echo   - ui_components         (UI component library)
    echo   - ui_display            (Display and formatting utilities)
    echo   - logger                (Logging and output system)
    echo   - utils                 (Utility functions)
    echo   - spotify_handler       (Spotify integration)
    echo   - apple_music_handler   (Apple Music support)
    echo   - youtube_scorer        (YouTube search scoring)
    echo   - generic_downloader    (Generic download handler)
    echo.
    
    echo You can now run:
    echo   * python ultimate_downloader.py --help        (Show help and options)
    echo   * python ultimate_downloader.py ^<URL^>         (Download from URL)
    echo   * python ultimate_downloader.py -i            (Interactive mode)
    echo   * python -m pytest                            (Run tests)
    echo.
    
    echo Supported Platforms:
    echo   - YouTube, YouTube Music
    echo   - Spotify (via YouTube search)
    echo   - Apple Music (with setup)
    echo   - Instagram, TikTok, Twitter
    echo   - SoundCloud, Bandcamp
    echo   - 1000+ other platforms (via yt-dlp)
    echo.
    
    echo To deactivate environment, type: deactivate
    echo.
) else (
    echo [ERROR] Virtual environment not found!
    echo Please run setup.bat first
    exit /b 1
)
