@echo off
setlocal
cd /d "%~dp0"
title CareerAgent Code Check

where py >nul 2>nul
if not errorlevel 1 (
    py -3.11 -c "import sys" >nul 2>nul
    if not errorlevel 1 (
        py -3.11 tools\check_project.py
        goto :after_run
    )
    py -3.12 -c "import sys" >nul 2>nul
    if not errorlevel 1 (
        py -3.12 tools\check_project.py
        goto :after_run
    )
    py -3 tools\check_project.py
    goto :after_run
)

where python >nul 2>nul
if errorlevel 1 (
    echo Python was not found. Install Python 3.11 or 3.12 first.
    pause
    exit /b 1
)
python tools\check_project.py

:after_run
if errorlevel 1 (
    echo.
    echo Code checks failed. Review the output above.
    echo If Ruff or Pytest is missing, run:
    echo   python -m pip install -r requirements-dev.txt
    pause
    exit /b 1
)
echo.
echo Code checks completed. Review any skipped optional Node.js checks above.
pause
