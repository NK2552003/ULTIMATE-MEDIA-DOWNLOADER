@echo off
setlocal

set REPO_URL=https://codeberg.org/nk2552003/umd.git
set REPO_NAME=umd

echo.
echo ======================================
echo   Ultimate Media Downloader Installer
echo ======================================
echo.

where git >nul 2>nul
if errorlevel 1 (
    echo Git is not installed.
    echo Install Git from https://git-scm.com/download/win
    pause
    exit /b 1
)

if not exist "%REPO_NAME%" (
    echo Cloning repository...
    git clone %REPO_URL%
)

cd %REPO_NAME%
call scripts\install.bat