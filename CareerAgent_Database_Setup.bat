@echo off
setlocal
cd /d "%~dp0"
title CareerAgent Database Setup

where py >nul 2>nul
if errorlevel 1 (
  echo Python was not found. Please install Python 3.11 or 3.12.
  pause
  exit /b 1
)

py -3.11 database_bootstrap.py 2>nul
if not errorlevel 1 goto :done
py -3.12 database_bootstrap.py 2>nul
if not errorlevel 1 goto :done
py -3 database_bootstrap.py

:done
if errorlevel 1 (
  echo.
  echo Database setup failed. Read the message above.
  pause
  exit /b 1
)
echo.
echo PostgreSQL + pgvector is ready.
pause
