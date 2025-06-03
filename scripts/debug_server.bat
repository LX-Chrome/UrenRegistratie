@echo off
REM Debug server starter for Time Registrator
REM This will help diagnose loading issues

echo Starting debug server for Time Registrator...
echo This will help diagnose why the application won't load.
echo.

REM Check if Python is installed
where python >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo Error: Python is not installed or not in your PATH.
    pause
    exit /b 1
)

REM Run the debug server script
python debug_server.py

pause 