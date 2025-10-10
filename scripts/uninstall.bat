@echo off
REM =============================================================================
REM Ultimate Media Downloader - Windows Uninstall Script
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
echo [1/2] Uninstalling Python package...

REM Try pipx first
where pipx >nul 2>&1
if not errorlevel 1 (
    echo Using pipx to uninstall...
    pipx uninstall ultimate-downloader
) else (
    REM Try with pip
    echo Using pip to uninstall...
    python -m pip uninstall -y ultimate-downloader
    if errorlevel 1 (
        pip uninstall -y ultimate-downloader
        if errorlevel 1 (
            echo WARNING: Package not found or already uninstalled
        )
    )
)

echo [OK] Package uninstalled

echo.
echo [2/2] Cleanup complete

echo.
echo ======================================================================
echo   Uninstallation Complete
echo ======================================================================
echo.
echo Your downloaded files are still in: %%USERPROFILE%%\Downloads\UltimateDownloader
echo.
pause
