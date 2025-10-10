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
if errorlevel 1 (
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
if not errorlevel 1 (
    echo Using pipx for installation...
    pipx install -e . --force
    if errorlevel 1 (
        echo ERROR: pipx installation failed
        exit /b 1
    )
) else (
    echo pipx not found. Installing with pip...
    python -m pip install --user -e .
    if errorlevel 1 (
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

REM Check if umd command is available
where umd >nul 2>&1
if not errorlevel 1 (
    echo [OK] 'umd' command is available
) else (
    echo WARNING: 'umd' command not found in PATH
    echo.
    echo You may need to add Python Scripts to your PATH:
    echo.
    echo 1. Open System Properties ^> Environment Variables
    echo 2. Add these paths to your PATH variable:
    echo    %%APPDATA%%\Python\Python311\Scripts
    echo    %%USERPROFILE%%\AppData\Roaming\Python\Python311\Scripts
    echo.
    echo Or run this in PowerShell (as Administrator):
    echo    [Environment]::SetEnvironmentVariable("Path", $env:Path + ";%%APPDATA%%\Python\Python311\Scripts", "User")
    echo.
    echo After updating PATH, restart your terminal.
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
