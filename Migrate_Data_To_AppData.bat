@echo off
setlocal
cd /d "%~dp0"
title CareerAgent Storage Migration

echo Close CareerAgent before continuing.
echo This tool moves database, login state, models and media cache to AppData.
echo.
pause

where py >nul 2>nul
if errorlevel 1 (
  echo Python was not found.
  pause
  exit /b 1
)

py -3.11 migrate_to_lightweight.py 2>nul
if errorlevel 1 py -3.12 migrate_to_lightweight.py 2>nul
if errorlevel 1 py -3 migrate_to_lightweight.py

if errorlevel 1 (
  echo Migration failed. No files should be deleted manually.
  pause
  exit /b 1
)

echo.
echo Migration finished.
echo If you also want to move the Python CUDA runtime out of this folder,
echo delete the .venv folder and run CareerAgent_Start.bat once. It will redownload once.
pause
