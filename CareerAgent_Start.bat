@echo off
setlocal
cd /d "%~dp0"
title CareerAgent Collector

where py >nul 2>nul
if errorlevel 1 (
    echo =============================================
    echo Python was not found.
    echo Please install Python 3.11 or 3.12 and enable Add Python to PATH.
    echo =============================================
    pause
    exit /b 1
)

py -3 bootstrap.py
if errorlevel 1 (
    echo.
    echo CareerAgent failed to start. Check the error message above.
    pause
    exit /b 1
)
