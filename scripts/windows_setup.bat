@echo off
REM Windows Setup Script for Time Registrator
REM This script handles Windows Store Python installations and venv creation issues

echo === Time Registrator Windows Setup Script ===
echo This script will set up the environment and install dependencies
echo.

REM Check if Python is installed
where python >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo Error: Python is not installed or not in your PATH.
    echo Please install Python from python.org (NOT from Windows Store).
    echo.
    echo Go to https://www.python.org/downloads/ to download Python.
    pause
    exit /b 1
)

REM Detect if Python is from Windows Store
python -c "import sys; print(sys.executable)" > python_path.txt
findstr /C:"WindowsApps" python_path.txt >nul
if %ERRORLEVEL% equ 0 (
    echo Detected Windows Store Python installation.
    echo This version has restrictions that prevent creating virtual environments.
    echo.
    echo We'll try an alternative approach...
    goto WindowsStoreApproach
) else (
    echo Standard Python installation detected.
    goto StandardApproach
)

:WindowsStoreApproach
echo Creating virtual environment without using the venv module...
echo.

REM Try using pip directly to install packages
echo Installing required packages directly...
python -m pip install --upgrade pip
python -m pip install flask flask-login flask-sqlalchemy python-dotenv
python -m pip install xhtml2pdf reportlab weasyprint
python -m pip install -r requirements.txt

echo.
echo Creating .env file if missing...
if not exist .env (
    echo # Database configuration > .env
    echo DATABASE_URL=sqlite:///database.db >> .env
    echo. >> .env
    echo # Security >> .env
    python -c "import os; print('SESSION_SECRET=' + os.urandom(24).hex())" >> .env
    python -c "import os; print('API_KEY=' + os.urandom(24).hex())" >> .env
    echo. >> .env
    echo # Application configuration >> .env
    echo DEBUG=True >> .env
    echo .env file created.
)

echo.
echo Starting the application...
python main.py
goto :eof

:StandardApproach
echo Setting up virtual environment...
if not exist venv (
    python -m venv venv
    if %ERRORLEVEL% neq 0 (
        echo Failed to create virtual environment.
        echo Trying alternative approach...
        goto WindowsStoreApproach
    )
)

echo.
echo Installing dependencies...
call venv\Scripts\activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

echo.
echo Checking for critical packages...
python -m pip show xhtml2pdf >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo Installing missing critical package: xhtml2pdf
    python -m pip install xhtml2pdf
)

python -m pip show reportlab >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo Installing missing critical package: reportlab
    python -m pip install reportlab
)

python -m pip show weasyprint >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo Installing missing critical package: weasyprint
    python -m pip install weasyprint
)

echo.
echo Creating .env file if missing...
if not exist .env (
    echo # Database configuration > .env
    echo DATABASE_URL=sqlite:///database.db >> .env
    echo. >> .env
    echo # Security >> .env
    python -c "import os; print('SESSION_SECRET=' + os.urandom(24).hex())" >> .env
    python -c "import os; print('API_KEY=' + os.urandom(24).hex())" >> .env
    echo. >> .env
    echo # Application configuration >> .env
    echo DEBUG=True >> .env
    echo .env file created.
)

echo.
echo Starting the application...
python main.py
goto :eof 