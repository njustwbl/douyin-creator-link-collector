@echo off
setlocal
cd /d "%~dp0"
title CareerAgent PostgreSQL Backup

where py >nul 2>nul
if errorlevel 1 (
  echo Python was not found. Please install Python 3.11 or 3.12.
  pause
  exit /b 1
)

py -3 backup_postgres.py
if errorlevel 1 (
  echo.
  echo Database backup failed. Read the message above.
  pause
  exit /b 1
)
echo.
echo Database backup completed.
pause
