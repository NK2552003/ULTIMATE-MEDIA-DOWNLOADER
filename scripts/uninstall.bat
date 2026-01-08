@echo off
REM =============================================================================
REM Ultimate Media Downloader - Windows Uninstall Script
REM Version: 2.1.0
REM Date: January 2026
REM Removes the Ultimate Media Downloader installation
REM =============================================================================

setlocal enabledelayedexpansion

echo ======================================================================
echo   Ultimate Media Downloader - Uninstaller
echo ======================================================================
echo.

echo WARNING: This will remove the Ultimate Media Downloader installation.
echo Your downloaded files will NOT be deleted.
echo.
set /p CONTINUE="Continue? (y/n): "
if /i not "!CONTINUE!"=="y" (
    echo Uninstall cancelled.
    pause
    exit /b 0
)

echo.
echo [1/3] Uninstalling Python package...

REM Try pipx first
where pipx >nul 2>&1
if not errorlevel 1 (
    echo [OK] Using pipx to uninstall...
    pipx uninstall ultimate-downloader
    if errorlevel 0 goto pipx_success
)

REM Try pip
where python >nul 2>&1
if not errorlevel 1 (
    echo [OK] Using pip to uninstall...
    python -m pip uninstall -y ultimate-downloader
    if errorlevel 0 goto pip_success
    
    pip uninstall -y ultimate-downloader
    if errorlevel 0 goto pip_success
)

echo [WARNING] Package not found or already uninstalled
goto cleanup

:pipx_success
echo [OK] Package uninstalled via pipx
goto cleanup

:pip_success
echo [OK] Package uninstalled via pip
goto cleanup

:cleanup
echo.
echo [2/3] Removing virtual environment (if local setup)...

if exist "venv" (
    echo [OK] Removing virtual environment...
    rmdir /s /q venv
    echo [OK] Virtual environment removed
) else (
    echo [INFO] No local virtual environment found
)

echo.
echo [3/3] Removing activation scripts...

if exist "scripts\activate-env.bat" (
    del /q scripts\activate-env.bat
    echo [OK] Windows activation script removed
)

echo.
echo ======================================================================
echo   Uninstallation Complete
echo ======================================================================
echo.
echo [INFO] Modules removed:
echo   - ultimate_downloader    (Main downloader engine)
echo   - cli_args              (Command-line argument parser)
echo   - ui_components         (UI component library)
echo   - ui_display            (Display and formatting utilities)
echo   - logger                (Logging system)
echo   - utils                 (Utility functions)
echo   - youtube_scorer        (YouTube search scoring)
echo   - generic_downloader    (Generic download handler)
echo.
echo   Platform Handlers (handlers/):
echo   - spotify_handler       (Spotify integration)
echo   - apple_music_handler   (Apple Music support)
echo   - pornhub_handler       (Pornhub support)
echo   - xnxx_handler          (XNXX support)
echo   - tumblr_handler        (Tumblr support)
echo   - xhamster_handler      (xHamster support)
echo   - hianime_handler       (HiAnime support)
echo   - tiktok_handler        (TikTok support)
echo   - eporner_handler       (Eporner support)
echo   - hqporner_handler      (HQPorner support)
echo   - beeg_handler          (Beeg support)
echo   - linkedin_handler      (LinkedIn support)
echo   - reddit_handler        (Reddit support)
echo   - pinterest_handler     (Pinterest support)
echo   - jiosaavn_handler      (JioSaavn support)
echo   - gaana_handler         (Gaana support)
echo.
echo [INFO] Your downloaded files are still in: %%USERPROFILE%%\Downloads\UltimateDownloader
echo [INFO] To remove downloads too, run: rmdir /s /q "%%USERPROFILE%%\Downloads\UltimateDownloader"
echo.
pause
