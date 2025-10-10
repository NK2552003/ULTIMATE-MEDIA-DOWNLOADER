@echo off
REM =============================================================================
REM Ultimate Media Downloader - Environment Activation Script
REM Version: 2.0.0
REM Date: October 6, 2025
REM =============================================================================

echo ========================================================================
echo    Activating Ultimate Media Downloader Environment
echo ========================================================================
echo.

if exist "%~dp0venv\Scripts\activate.bat" (
    call "%~dp0venv\Scripts\activate.bat"
    echo [SUCCESS] Virtual environment activated
    echo.
    echo You can now run:
    echo   * python ultimate_downloader.py --help
    echo   * python ultimate_downloader.py ^<URL^>
    echo.
    echo To deactivate, type: deactivate
    echo.
) else (
    echo [ERROR] Virtual environment not found!
    echo Please run setup.bat first
    exit /b 1
)
