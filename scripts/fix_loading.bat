@echo off
REM Fix loading issues script for Time Registrator

echo === Time Registrator Loading Issues Fixer ===
echo This script will fix common loading issues
echo.

REM Kill any existing Python processes that might be using port 5000
echo Checking for processes using port 5000...
for /f "tokens=5" %%a in ('netstat -aon ^| find ":5000" ^| find "LISTENING"') do (
    echo Found process with PID: %%a
    echo Attempting to terminate this process...
    taskkill /F /PID %%a
)

REM Check for a locked database
echo.
echo Checking for locked database...
if exist database.db (
    echo Database file exists, checking if it's accessible...
    copy database.db database.db.bak >nul 2>nul
    if %ERRORLEVEL% equ 0 (
        echo Database file is accessible.
        del database.db.bak >nul 2>nul
    ) else (
        echo Database appears to be locked. Attempting to fix...
        echo Renaming existing database to database.db.old
        if exist database.db.old del database.db.old
        ren database.db database.db.old
        echo Database will be recreated when you start the application.
    )
) else (
    echo No database file found. It will be created when you start the application.
)

REM Edit main.py to ensure it listens on all interfaces
echo.
echo Updating main.py for better network compatibility...
python -c "
import re
with open('main.py', 'r') as f:
    content = f.read()
if 'if __name__ == \"__main__\":' in content:
    # Replace the app.run line to ensure it listens on all interfaces
    new_content = re.sub(
        r'if __name__ == \"__main__\":(.*?)app\.run\((.*?)\)',
        'if __name__ == \"__main__\":\\1app.run(host=\"0.0.0.0\", port=5000, debug=True)',
        content, 
        flags=re.DOTALL
    )
    if new_content != content:
        with open('main.py', 'w') as f:
            f.write(new_content)
        print('Updated main.py to listen on all interfaces.')
    else:
        print('main.py already appears to be properly configured.')
else:
    print('Could not update main.py - structure different than expected.')
"

echo.
echo Fixes applied. Now try starting the application again using:
echo   1. windows_setup.bat (for Windows Store Python)
echo   2. start.bat (for regular Python)
echo.
echo If problems persist, try running debug_server.bat for more detailed diagnostics.
pause 