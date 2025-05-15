@echo off
REM Quick start Time Registrator (fast, assumes already set up)

REM Check if venv exists
if not exist venv\ (
    echo Virtual environment not found.
    echo Please run 'python run.py' first to set up the environment.
    pause
    exit /b 1
)

REM Start the application using the virtual environment
echo Starting the application...
venv\Scripts\python quick_start.py

REM If there was an error, suggest running the fix_dependencies script
if %ERRORLEVEL% neq 0 (
    echo.
    echo There was an error starting the application.
    echo If you're missing dependencies, try running fix_dependencies.bat
    pause
) 