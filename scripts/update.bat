@echo off
REM Auto-Update Script for Ultimate Media Downloader (Windows)
REM This script checks for updates and installs the latest version

echo ========================================================
echo    Ultimate Media Downloader - Auto Update Script
echo ========================================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed. Please install Python 3.9 or higher.
    pause
    exit /b 1
)

REM Check if git is available
git --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [WARNING] Git is not installed. Installing from local directory instead...
    set USE_GIT=false
) else (
    set USE_GIT=true
)

echo [INFO] Checking current version...

REM Get current version
for /f "delims=" %%i in ('python -c "try:
    import ultimate_downloader
    print(ultimate_downloader.__version__)
except:
    print('0.0.0')" 2^>nul') do set CURRENT_VERSION=%%i

if "%CURRENT_VERSION%"=="" set CURRENT_VERSION=Not installed

echo    Current version: %CURRENT_VERSION%
echo.

echo [INFO] Updating Ultimate Media Downloader...
echo.

REM Update using pipx (matching installation method)
pipx --version >nul 2>&1
if %errorlevel% equ 0 (
    echo [INFO] Using pipx for update...
    
    REM Check for existing installation
    echo [INFO] Checking for existing installation...
    pipx list 2>nul | findstr /C:"ultimate-downloader" >nul
    if %errorlevel% equ 0 (
        echo [INFO] Removing previous installation...
        pipx uninstall ultimate-downloader
        
        REM Clean up leftover directories
        if exist "%USERPROFILE%\.local\pipx\venvs\ultimate-downloader" (
            echo [INFO] Cleaning up leftover files...
            rmdir /S /Q "%USERPROFILE%\.local\pipx\venvs\ultimate-downloader"
        )
        
        REM Remove command if it still exists
        if exist "%USERPROFILE%\.local\bin\umd.exe" (
            del /Q "%USERPROFILE%\.local\bin\umd.exe"
        )
        
        echo [SUCCESS] Old version completely removed
    ) else (
        echo [INFO] No previous installation found
    )
    
    REM Install fresh version
    echo [INFO] Installing new version...
    if "%USE_GIT%"=="true" (
        pipx install git+https://codeberg.org/nk2552003/umd.git
    ) else (
        set SCRIPT_DIR=%~dp0..
        if exist "%SCRIPT_DIR%\setup.py" (
            pipx install "%SCRIPT_DIR%"
        ) else (
            echo [ERROR] Unable to update: setup.py not in expected location
            pause
            exit /b 1
        )
    )
) else (
    echo [WARNING] pipx not found. Attempting pip installation...
    
    REM Uninstall old version first
    echo [INFO] Removing previous installation...
    python -m pip uninstall -y ultimate-downloader >nul 2>&1
    
    echo [SUCCESS] Old version removed
    echo [INFO] Installing new version...
    
    if "%USE_GIT%"=="true" (
        REM Try with --user flag first
        python -m pip install --user git+https://codeberg.org/nk2552003/umd.git
    ) else (
        REM Fallback: Try to upgrade from local directory
        set SCRIPT_DIR=%~dp0..
        if exist "%SCRIPT_DIR%\setup.py" (
            python -m pip install --user "%SCRIPT_DIR%"
        ) else (
            echo [ERROR] Unable to update: Git not found and setup.py not in expected location
            pause
            exit /b 1
        )
    )
)

REM Check if update was successful
if %errorlevel% equ 0 (
    echo.
    echo [SUCCESS] Update completed successfully!
    
    REM Get new version
    for /f "delims=" %%i in ('python -c "try:
    import ultimate_downloader
    print(ultimate_downloader.__version__)
except:
    print('Unknown')" 2^>nul') do set NEW_VERSION=%%i
    
    if not "%NEW_VERSION%"=="" (
        echo    New version: %NEW_VERSION%
    )
    
    echo.
    echo [INFO] You can now run 'umd' to use Ultimate Media Downloader
    echo.
) else (
    echo.
    echo [ERROR] Update failed. Please check the error messages above.
    echo.
    echo [TIP] Try running manually:
    echo    python -m pip install --upgrade git+https://codeberg.org/nk2552003/umd.git
    echo.
    pause
    exit /b 1
)

pause
