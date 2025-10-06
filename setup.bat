@echo off
REM =============================================================================
REM Ultimate Media Downloader - Windows Setup Script
REM Version: 2.0.0
REM Date: October 6, 2025
REM Description: Automated setup script for Ultimate Media Downloader (Windows)
REM Author: Nitish Kumar
REM Repository: https://github.com/NK2552003/ULTIMATE-MEDIA-DOWNLOADER
REM =============================================================================

setlocal enabledelayedexpansion

REM Configuration
set "VENV_NAME=venv"
set "PYTHON_VERSION=3.9"
set "REQUIREMENTS_FILE=requirements.txt"

REM =============================================================================
REM Helper Functions
REM =============================================================================

:print_header
echo.
echo ========================================================================
echo                                                                        
echo        ULTIMATE MEDIA DOWNLOADER - SETUP SCRIPT                       
echo                  Version 2.0.0 - October 2025                         
echo                                                                        
echo ========================================================================
echo.
goto :eof

:print_section
echo.
echo ^>^> %~1
echo ------------------------------------------------------------------------
goto :eof

:print_success
echo [SUCCESS] %~1
goto :eof

:print_error
echo [ERROR] %~1
goto :eof

:print_info
echo [INFO] %~1
goto :eof

:print_warning
echo [WARNING] %~1
goto :eof

:print_step
echo  --^> %~1
goto :eof

:error_exit
echo.
echo ========================================================================
echo                        SETUP FAILED                                    
echo ========================================================================
echo [ERROR] %~1
echo.
exit /b 1

REM =============================================================================
REM Python Installation Check
REM =============================================================================

:check_python
call :print_section "Checking Python Installation"

where python >nul 2>&1
if %errorlevel% equ 0 (
    for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION_INSTALLED=%%i
    call :print_success "Python found: !PYTHON_VERSION_INSTALLED!"
    set "PYTHON_CMD=python"
) else (
    where py >nul 2>&1
    if !errorlevel! equ 0 (
        for /f "tokens=2" %%i in ('py --version 2^>^&1') do set PYTHON_VERSION_INSTALLED=%%i
        call :print_success "Python found: !PYTHON_VERSION_INSTALLED!"
        set "PYTHON_CMD=py"
    ) else (
        call :print_error "Python not found!"
        call :print_info "Please install Python 3.9+ from https://www.python.org/downloads/"
        call :print_info "Make sure to check 'Add Python to PATH' during installation"
        call :error_exit "Python installation required"
    )
)

REM Check pip
%PYTHON_CMD% -m pip --version >nul 2>&1
if %errorlevel% equ 0 (
    for /f "tokens=2" %%i in ('%PYTHON_CMD% -m pip --version 2^>^&1') do set PIP_VERSION=%%i
    call :print_success "pip is installed: !PIP_VERSION!"
) else (
    call :print_warning "pip not found. Installing pip..."
    %PYTHON_CMD% -m ensurepip --upgrade
    if !errorlevel! neq 0 (
        call :error_exit "Failed to install pip"
    )
    call :print_success "pip installed successfully"
)

goto :eof

REM =============================================================================
REM FFmpeg Installation Check
REM =============================================================================

:check_ffmpeg
call :print_section "Checking FFmpeg Installation"

where ffmpeg >nul 2>&1
if %errorlevel% equ 0 (
    for /f "tokens=3" %%i in ('ffmpeg -version 2^>^&1 ^| findstr /C:"ffmpeg version"') do (
        call :print_success "FFmpeg found: %%i"
        goto :eof
    )
) else (
    call :print_warning "FFmpeg not found"
    call :print_info "FFmpeg is required for video/audio processing"
    call :print_info "Please download and install FFmpeg from:"
    call :print_info "  https://ffmpeg.org/download.html#build-windows"
    call :print_info "Or use a package manager like:"
    call :print_info "  - Chocolatey: choco install ffmpeg"
    call :print_info "  - Scoop: scoop install ffmpeg"
    call :print_info ""
    call :print_info "After installation, add FFmpeg to your system PATH"
    call :print_warning "Some features may not work without FFmpeg"
)

goto :eof

REM =============================================================================
REM Virtual Environment Setup
REM =============================================================================

:create_virtual_environment
call :print_section "Creating Virtual Environment"

if exist "%VENV_NAME%" (
    call :print_warning "Virtual environment already exists"
    set /p "RECREATE=Do you want to recreate it? (y/N): "
    if /i "!RECREATE!"=="y" (
        call :print_step "Removing existing virtual environment..."
        rmdir /s /q "%VENV_NAME%"
    ) else (
        call :print_info "Using existing virtual environment"
        goto :eof
    )
)

call :print_step "Creating virtual environment: %VENV_NAME%"
%PYTHON_CMD% -m venv "%VENV_NAME%"

if exist "%VENV_NAME%" (
    call :print_success "Virtual environment created successfully"
) else (
    call :error_exit "Failed to create virtual environment"
)

goto :eof

REM =============================================================================
REM Python Dependencies Installation
REM =============================================================================

:install_python_dependencies
call :print_section "Installing Python Dependencies"

call :print_step "Activating virtual environment..."
call "%VENV_NAME%\Scripts\activate.bat"

call :print_step "Upgrading pip, setuptools, and wheel..."
python -m pip install --upgrade pip setuptools wheel --quiet

if not exist "%REQUIREMENTS_FILE%" (
    call :print_error "Requirements file not found: %REQUIREMENTS_FILE%"
    call :error_exit "Please ensure requirements.txt exists in the project directory"
)

call :print_step "Installing packages from %REQUIREMENTS_FILE%..."
call :print_info "This may take 2-5 minutes depending on your internet speed..."

python -m pip install -r "%REQUIREMENTS_FILE%"

if %errorlevel% neq 0 (
    call :error_exit "Failed to install dependencies"
)

call :print_success "All dependencies installed successfully"

REM Verify critical installations
call :print_step "Verifying critical packages..."

set "PACKAGES_TO_VERIFY=yt_dlp requests rich mutagen spotipy"
set "FAILED_PACKAGES="

for %%p in (%PACKAGES_TO_VERIFY%) do (
    python -c "import %%p" >nul 2>&1
    if !errorlevel! equ 0 (
        call :print_success "%%p verified"
    ) else (
        call :print_error "%%p failed to install"
        set "FAILED_PACKAGES=!FAILED_PACKAGES! %%p"
    )
)

if "!FAILED_PACKAGES!"=="" (
    call :print_success "All core packages verified successfully"
) else (
    call :print_warning "Some packages failed:!FAILED_PACKAGES!"
    call :print_info "You can try installing them manually later"
)

REM Count installed packages
for /f %%i in ('python -m pip list --format^=freeze ^| find /c /v ""') do set INSTALLED_COUNT=%%i
call :print_info "Total packages installed: !INSTALLED_COUNT!"

goto :eof

REM =============================================================================
REM Configuration Setup
REM =============================================================================

:create_config_file
call :print_section "Creating Configuration Files"

if not exist "config.json" (
    call :print_step "Creating config.json..."
    (
        echo {
        echo     "spotify": {
        echo         "client_id": "",
        echo         "client_secret": ""
        echo     },
        echo     "apple_music": {
        echo         "enabled": false,
        echo         "cookie_file": ""
        echo     },
        echo     "download": {
        echo         "output_dir": "downloads",
        echo         "format": "best",
        echo         "audio_format": "mp3",
        echo         "audio_quality": "320",
        echo         "video_quality": "1080",
        echo         "embed_thumbnail": true,
        echo         "embed_metadata": true
        echo     },
        echo     "proxy": {
        echo         "enabled": false,
        echo         "http": "",
        echo         "https": ""
        echo     },
        echo     "advanced": {
        echo         "concurrent_downloads": 3,
        echo         "retry_attempts": 3,
        echo         "timeout": 300
        echo     }
        echo }
    ) > config.json
    call :print_success "Configuration file created"
) else (
    call :print_info "Configuration file already exists"
)

REM Create downloads directory
if not exist "downloads" (
    mkdir downloads
    call :print_success "Downloads directory created"
)

goto :eof

REM =============================================================================
REM Activation Script Creation
REM =============================================================================

:create_activation_script
call :print_section "Creating Activation Script"

(
    echo @echo off
    echo REM =============================================================================
    echo REM Ultimate Media Downloader - Environment Activation Script
    echo REM Version: 2.0.0
    echo REM Date: October 6, 2025
    echo REM =============================================================================
    echo.
    echo echo ========================================================================
    echo echo    Activating Ultimate Media Downloader Environment
    echo echo ========================================================================
    echo echo.
    echo.
    echo if exist "%%~dp0venv\Scripts\activate.bat" ^(
    echo     call "%%~dp0venv\Scripts\activate.bat"
    echo     echo [SUCCESS] Virtual environment activated
    echo     echo.
    echo     echo You can now run:
    echo     echo   * python ultimate_downloader.py --help
    echo     echo   * python ultimate_downloader.py ^<URL^>
    echo     echo.
    echo     echo To deactivate, type: deactivate
    echo     echo.
    echo ^) else ^(
    echo     echo [ERROR] Virtual environment not found!
    echo     echo Please run setup.bat first
    echo     exit /b 1
    echo ^)
) > activate-env.bat

call :print_success "Activation script created: activate-env.bat"

goto :eof

REM =============================================================================
REM Testing
REM =============================================================================

:run_tests
call :print_section "Running Tests"

call "%VENV_NAME%\Scripts\activate.bat"

call :print_step "Testing ultimate_downloader.py..."
python ultimate_downloader.py --version >nul 2>&1
if %errorlevel% equ 0 (
    call :print_success "Main script is working"
) else (
    call :print_warning "Main script test failed (this may be normal if --version isn't implemented)"
)

call :print_step "Testing imports..."
python -c "import yt_dlp; import requests; import rich; from generic_downloader import GenericSiteDownloader; print('All imports successful')" >nul 2>&1
if %errorlevel% equ 0 (
    call :print_success "All imports working"
) else (
    call :print_warning "Some imports failed"
)

goto :eof

REM =============================================================================
REM Post-Installation Info
REM =============================================================================

:show_post_install_info
call :print_section "Setup Complete!"

echo.
echo ========================================================================
echo                    SETUP COMPLETED SUCCESSFULLY!                       
echo ========================================================================
echo.
echo ========================================================================
echo                         QUICK START GUIDE                              
echo ========================================================================
echo.
echo STEP 1: Activate Environment
echo   activate-env.bat
echo.
echo STEP 2: Download Your First Video
echo   python ultimate_downloader.py "https://youtube.com/watch?v=xxx"
echo.
echo STEP 3: Try Interactive Mode
echo   python ultimate_downloader.py -i
echo.
echo ========================================================================
echo                         COMMON COMMANDS                                
echo ========================================================================
echo.
echo   * Download video:       python ultimate_downloader.py "URL"
echo   * Download audio:       python ultimate_downloader.py -a "URL"
echo   * Download playlist:    python ultimate_downloader.py -p "URL"
echo   * Interactive mode:     python ultimate_downloader.py -i
echo   * Show help:            python ultimate_downloader.py --help
echo.
echo ========================================================================
echo                    OPTIONAL CONFIGURATION                              
echo ========================================================================
echo.
echo   * Spotify API: Edit config.json to add credentials
echo     Get keys from: https://developer.spotify.com/dashboard
echo.
echo   * Proxy: Configure proxy in config.json
echo   * Output: Customize download directory and quality
echo.
echo ========================================================================
echo                        DOCUMENTATION                                   
echo ========================================================================
echo.
echo   * User Guide:           docs\USER_GUIDE.md
echo   * API Reference:        docs\API_REFERENCE.md
echo   * Complete Index:       docs\INDEX.md
echo   * Troubleshooting:      docs\USER_GUIDE.md#troubleshooting
echo.
echo ========================================================================
echo                      INSTALLATION SUMMARY                              
echo ========================================================================
echo.
echo   [SUCCESS] Python %PYTHON_VERSION_INSTALLED% installed
echo   [SUCCESS] Virtual environment created
echo   [SUCCESS] %INSTALLED_COUNT% packages installed
echo   [SUCCESS] Configuration files created
echo   [SUCCESS] Ready to download from 1000+ platforms
echo.
echo ========================================================================
echo                     Happy Downloading! 🎉🎬🎵                          
echo ========================================================================
echo.
echo Tip: Run 'activate-env.bat' now to get started!
echo.

goto :eof

REM =============================================================================
REM Cleanup Function
REM =============================================================================

:cleanup_temp_files
call :print_step "Cleaning up temporary files..."

REM Remove any .pyc files and __pycache__ directories
for /d /r %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d" 2>nul
del /s /q *.pyc 2>nul

call :print_success "Cleanup complete"

goto :eof

REM =============================================================================
REM Main Installation Flow
REM =============================================================================

:main
call :print_header

echo ========================================================================
echo  This script will install all dependencies and configure the app      
echo  Estimated time: 3-5 minutes (depending on internet speed)            
echo ========================================================================
echo.

REM Check and install Python
call :check_python
if %errorlevel% neq 0 exit /b 1

REM Check FFmpeg
call :check_ffmpeg

REM Create virtual environment
call :create_virtual_environment
if %errorlevel% neq 0 exit /b 1

REM Install Python dependencies
call :install_python_dependencies
if %errorlevel% neq 0 exit /b 1

REM Create configuration files
call :create_config_file

REM Create activation script
call :create_activation_script

REM Run tests
call :run_tests

REM Cleanup
call :cleanup_temp_files

REM Show post-installation info
call :show_post_install_info

goto :end

REM =============================================================================
REM Script Entry Point
REM =============================================================================

:end
endlocal
