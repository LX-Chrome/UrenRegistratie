@echo off
REM Fix missing dependencies for Time Registrator

echo This script will fix missing dependencies for Time Registrator
echo.

REM Check if Python is installed
where python >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo Python is not installed or not in your PATH. Please install Python and try again.
    pause
    exit /b 1
)

REM Run the dependency fixer script
python fix_dependencies.py

echo.
echo Dependency fixing complete. Now try starting the application with start.bat
pause 