@echo off
REM Time Registrator startup script for Windows

REM Check if Python is installed
where python >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo Python is not installed or not in your PATH. Please install Python and try again.
    pause
    exit /b 1
)

REM Run the Python starter script
python run.py
pause 