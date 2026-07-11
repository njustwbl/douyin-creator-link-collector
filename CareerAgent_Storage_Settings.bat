@echo off
setlocal
cd /d "%~dp0"
title CareerAgent Storage Settings

where py >nul 2>nul
if errorlevel 1 (
    echo Python was not found. Please install Python 3.11 or 3.12 first.
    pause
    exit /b 1
)

py -3.11 -c "import sys" >nul 2>nul
if not errorlevel 1 (
    py -3.11 configure_storage.py
    exit /b %errorlevel%
)

py -3.12 -c "import sys" >nul 2>nul
if not errorlevel 1 (
    py -3.12 configure_storage.py
    exit /b %errorlevel%
)

py -3 configure_storage.py
