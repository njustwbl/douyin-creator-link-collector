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

py -3.11 -c "import sys" >nul 2>nul
if not errorlevel 1 (
  py -3.11 backup_postgres.py
  goto :after_run
)
py -3.12 -c "import sys" >nul 2>nul
if not errorlevel 1 (
  py -3.12 backup_postgres.py
  goto :after_run
)

echo WARNING: Python 3.11/3.12 was not found. Trying the default Python 3.
py -3 backup_postgres.py

:after_run
if errorlevel 1 (
  echo.
  echo Database backup failed. Read the message above.
  pause
  exit /b 1
)
echo.
echo Database backup completed.
pause
