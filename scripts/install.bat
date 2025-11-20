@echo off
REM =============================================================================
REM Ultimate Media Downloader - Windows Installation Script
REM Installs the package locally so you can run it with just 'umd'
REM =============================================================================

setlocal enabledelayedexpansion

echo ======================================================================
echo   Ultimate Media Downloader - Windows Installation
echo ======================================================================
echo.

REM Get the directory where the script is located
set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%.."

echo [1/5] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH.
    echo Please install Python 3.9 or higher from https://www.python.org/
    echo Make sure to check "Add Python to PATH" during installation.
    echo.
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo [OK] Python %PYTHON_VERSION% found

echo.
echo [2/5] Checking FFmpeg installation...
ffmpeg -version >nul 2>&1
if %errorlevel% neq 0 (
    echo WARNING: FFmpeg is not installed.
    echo FFmpeg is required for audio conversion and video processing.
    echo.
    echo To install FFmpeg:
    echo   Option 1: Using Chocolatey - choco install ffmpeg
    echo   Option 2: Using Scoop - scoop install ffmpeg
    echo   Option 3: Manual - Download from https://ffmpeg.org/download.html
    echo.
    set /p CONTINUE="Continue anyway? (y/n): "
    if /i not "!CONTINUE!"=="y" exit /b 1
) else (
    echo [OK] FFmpeg found
)

echo.
echo [3/5] Installing Python package...

REM Check if pipx is available
where pipx >nul 2>&1
if %errorlevel% equ 0 (
    echo Using pipx for installation...
    pipx install -e . --force
    if %errorlevel% neq 0 (
        echo ERROR: pipx installation failed
        exit /b 1
    )
) else (
    echo pipx not found. Installing with pip...
    python -m pip install --user -e .
    if %errorlevel% neq 0 (
        echo ERROR: Failed to install package
        echo.
        echo You can install pipx first for better isolation:
        echo   python -m pip install --user pipx
        echo   python -m pipx ensurepath
        echo.
        echo Then restart this script.
        pause
        exit /b 1
    )
)

echo [OK] Package installed successfully

echo.
echo [4/5] Verifying installation...

REM Try to detect the Python user scripts directory and create a launcher for 'umd'
for /f "delims=" %%S in ('python -c "import sysconfig;print(sysconfig.get_path('scripts'))"') do set "SCRIPTS_DIR=%%S"
if defined SCRIPTS_DIR (
    echo Detected Python scripts directory: %SCRIPTS_DIR%
    if exist "%SCRIPTS_DIR%" (
        echo Creating launcher 'umd.cmd' in %SCRIPTS_DIR%...
        > "%SCRIPTS_DIR%\umd.cmd" echo @echo off
        >> "%SCRIPTS_DIR%\umd.cmd" echo python -m ultimate_downloader %*
        echo [OK] Created launcher: %SCRIPTS_DIR%\umd.cmd
    ) else (
        echo Note: Python scripts directory does not exist: %SCRIPTS_DIR%
    )
) else (
    echo Could not detect Python scripts directory automatically.
)

REM Check if umd command is available in PATH
where umd >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] 'umd' command is available
) else (
    echo WARNING: 'umd' command not found in PATH
    echo.
    echo You may need to add the Python Scripts directory to your PATH.
    echo To find the correct directory, run:
    echo   python -c "import sysconfig;print(sysconfig.get_path('scripts'))"
    echo Then add that path to your PATH environment variable and restart your terminal.
    echo.
)

echo.
echo [5/5] Creating downloads directory...
set "DOWNLOADS_DIR=%USERPROFILE%\Downloads\UltimateDownloader"
if not exist "%DOWNLOADS_DIR%" mkdir "%DOWNLOADS_DIR%"
echo [OK] Downloads directory created: %DOWNLOADS_DIR%

echo.
echo ======================================================================
echo   Installation Complete! 🎉
echo ======================================================================
echo.
echo Core Modules Installed:
echo   - ultimate_downloader    (Main downloader engine)
echo   - browser_utils          (Browser and user agent utilities)
echo   - platform_utils         (Platform detection and configuration)
echo   - ui_utils               (Rich console output utilities)
echo   - cli_args              (Command-line argument parser)
echo   - ui_components         (UI component library)
echo   - ui_display            (Display and formatting utilities)
echo   - logger                (Logging system)
echo   - utils                 (Utility functions)
echo   - spotify_handler       (Spotify integration)
echo   - apple_music_handler   (Apple Music support)
echo   - youtube_scorer        (YouTube search scoring)
echo   - generic_downloader    (Generic download handler)
echo.
echo Usage:
echo   umd ^<URL^>                    # Download media from URL
echo   umd                          # Start interactive mode
echo   umd ^<URL^> --audio-only       # Download audio only
echo   umd ^<URL^> --quality 1080p    # Download specific quality
echo   umd --help                   # Show all options
echo.
echo Downloads will be saved to:
echo   %DOWNLOADS_DIR%
echo.
echo If 'umd' command is not found, restart your terminal or add Python Scripts to PATH.
echo For more information, see README.md or run: umd --help
echo ======================================================================
echo.
pause
