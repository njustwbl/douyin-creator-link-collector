@echo off
setlocal
cd /d "%~dp0"
title CareerAgent PostgreSQL Restore

echo ============================================================
echo CareerAgent PostgreSQL Restore
echo ============================================================
echo Please close the CareerAgent main program before restoring.
echo The selected dump is first restored into a temporary database.
echo A safety backup is created before the live database is replaced.
echo.

where py >nul 2>nul
if errorlevel 1 (
  echo Python was not found. Please install Python 3.11 or 3.12.
  pause
  exit /b 1
)

py -3.11 -c "import sys" >nul 2>nul
if not errorlevel 1 (
  py -3.11 restore_postgres.py
  goto :after_run
)
py -3.12 -c "import sys" >nul 2>nul
if not errorlevel 1 (
  py -3.12 restore_postgres.py
  goto :after_run
)

echo WARNING: Python 3.11/3.12 was not found. Trying the default Python 3.
py -3 restore_postgres.py

:after_run
if errorlevel 1 (
  echo.
  echo Database restore failed or was cancelled. Read the message above.
  pause
  exit /b 1
)
echo.
echo Database restore completed and validated. Restart CareerAgent now.
pause
