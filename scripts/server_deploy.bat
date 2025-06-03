@echo off
REM Time Registrator Server Deployment script for Windows Server
REM This script sets up Time Registrator as a production service

echo === Time Registrator Windows Server Deployment ===
echo This script will set up Time Registrator as a production service
echo accessible across your network.
echo.

REM Check if running with administrator privileges
net session >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo ERROR: This script requires administrator privileges.
    echo Please right-click and select "Run as administrator"
    pause
    exit /b 1
)

REM Check if Python is installed
where python >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo ERROR: Python is not installed or not in your PATH.
    echo Please install Python from python.org
    pause
    exit /b 1
)

REM Create production environment
echo.
echo Creating production environment...
if not exist prod_env (
    echo Creating virtual environment for production...
    python -m venv prod_env
    if %ERRORLEVEL% neq 0 (
        echo ERROR: Failed to create virtual environment.
        pause
        exit /b 1
    )
)

REM Install dependencies in production environment
echo.
echo Installing production dependencies...
call prod_env\Scripts\activate.bat
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip install pdfkit
python -m pip install waitress

REM Ensure all critical packages are installed
for %%p in (flask flask-login flask-sqlalchemy reportlab waitress python-dotenv) do (
    python -m pip install %%p
)

REM Create production server script
echo.
echo Creating production server script...
echo from waitress import serve > production_server.py
echo import os >> production_server.py
echo from app import app >> production_server.py
echo import routes  # noqa: F401 >> production_server.py
echo import routes_invoices  # noqa: F401 >> production_server.py
echo import routes_reports  # noqa: F401 >> production_server.py
echo. >> production_server.py
echo if __name__ == "__main__": >> production_server.py
echo     # Get configuration from environment or use defaults >> production_server.py
echo     host = os.environ.get('HOST', '0.0.0.0') >> production_server.py
echo     port = int(os.environ.get('PORT', 8080)) >> production_server.py
echo     threads = int(os.environ.get('THREADS', 4)) >> production_server.py
echo. >> production_server.py
echo     # Print server information >> production_server.py
echo     print(f"Starting production server on {host}:{port}") >> production_server.py
echo     print("Access the application at:") >> production_server.py
echo     print(f"http://{host}:{port} (from this server)") >> production_server.py
echo     hostname = os.environ.get('SERVER_NAME', None) >> production_server.py
echo     if not hostname: >> production_server.py
echo         import socket >> production_server.py
echo         try: >> production_server.py
echo             hostname = socket.gethostname() >> production_server.py
echo             ip = socket.gethostbyname(hostname) >> production_server.py
echo             print(f"http://{ip}:{port} (from your network)") >> production_server.py
echo         except: >> production_server.py
echo             pass >> production_server.py
echo. >> production_server.py
echo     # Configure for PDF generation with ReportLab >> production_server.py
echo     try: >> production_server.py
echo         import reportlab >> production_server.py
echo         print("ReportLab is available for PDF generation") >> production_server.py
echo     except ImportError: >> production_server.py
echo         print("Warning: ReportLab module not found. Please install it for PDF export.") >> production_server.py
echo. >> production_server.py
echo     # Start production server with waitress >> production_server.py
echo     serve(app, host=host, port=port, threads=threads) >> production_server.py

REM Ensure .env file exists for production
echo.
echo Creating production .env file if not exists...
if not exist .env (
    echo # Database configuration > .env
    echo DATABASE_URL=sqlite:///database.db >> .env
    echo. >> .env
    echo # Security >> .env
    prod_env\Scripts\python -c "import os; print('SESSION_SECRET=' + os.urandom(24).hex())" >> .env
    prod_env\Scripts\python -c "import os; print('API_KEY=' + os.urandom(24).hex())" >> .env
    echo. >> .env
    echo # Production configuration >> .env
    echo DEBUG=False >> .env
    echo HOST=0.0.0.0 >> .env
    echo PORT=8080 >> .env
    echo THREADS=4 >> .env
)

REM Create Windows Service wrapper (using NSSM)
echo.
echo Creating Windows Service files...

REM Create batch file to run the service
echo @echo off > run_production.bat
echo cd /d "%~dp0" >> run_production.bat
echo call prod_env\Scripts\activate.bat >> run_production.bat
echo prod_env\Scripts\python production_server.py >> run_production.bat

REM Create NSSM installation script
echo @echo off > install_service.bat
echo echo Installing Time Registrator as a Windows Service... >> install_service.bat
echo. >> install_service.bat
echo REM Check for NSSM >> install_service.bat
echo if not exist nssm.exe ( >> install_service.bat
echo     echo NSSM not found. Please download NSSM from nssm.cc and place nssm.exe in this directory. >> install_service.bat
echo     pause >> install_service.bat
echo     exit /b 1 >> install_service.bat
echo ) >> install_service.bat
echo. >> install_service.bat
echo nssm install TimeRegistrator "%~dp0run_production.bat" >> install_service.bat
echo nssm set TimeRegistrator DisplayName "Time Registrator" >> install_service.bat
echo nssm set TimeRegistrator Description "Time tracking and project management application" >> install_service.bat
echo nssm set TimeRegistrator AppDirectory "%~dp0" >> install_service.bat
echo nssm set TimeRegistrator Start SERVICE_AUTO_START >> install_service.bat
echo. >> install_service.bat
echo echo Service installed. You can now start it with: >> install_service.bat
echo echo   nssm start TimeRegistrator >> install_service.bat
echo echo. >> install_service.bat
echo echo Or use Windows Services Management Console to start/stop the service. >> install_service.bat
echo pause >> install_service.bat

REM Create uninstall service script
echo @echo off > uninstall_service.bat
echo echo Uninstalling Time Registrator service... >> uninstall_service.bat
echo if not exist nssm.exe ( >> uninstall_service.bat
echo     echo NSSM not found. Please download NSSM from nssm.cc and place nssm.exe in this directory. >> uninstall_service.bat
echo     pause >> uninstall_service.bat
echo     exit /b 1 >> uninstall_service.bat
echo ) >> uninstall_service.bat
echo nssm stop TimeRegistrator >> uninstall_service.bat
echo nssm remove TimeRegistrator confirm >> uninstall_service.bat
echo echo Service removed. >> uninstall_service.bat
echo pause >> uninstall_service.bat

REM Create a quick start script for production testing
echo @echo off > start_production.bat
echo echo Starting Time Registrator in production mode (for testing)... >> start_production.bat
echo echo. >> start_production.bat
echo echo This will start the server on port 8080. To access it: >> start_production.bat
echo echo   http://localhost:8080 >> start_production.bat
echo echo   http://YOUR-SERVER-IP:8080 (from other computers) >> start_production.bat
echo echo. >> start_production.bat
echo echo Press Ctrl+C to stop the server >> start_production.bat
echo echo. >> start_production.bat
echo call prod_env\Scripts\activate.bat >> start_production.bat
echo prod_env\Scripts\python production_server.py >> start_production.bat
echo pause >> start_production.bat

echo.
echo =====================================================================
echo DEPLOYMENT PREPARATION COMPLETE
echo =====================================================================
echo.
echo To complete the deployment:
echo.
echo 1. Test the production server:
echo    - Run "start_production.bat"
echo    - Access http://localhost:8080 in your browser
echo    - Make sure everything works as expected
echo.
echo 2. To install as a Windows Service:
echo    - Download NSSM from http://nssm.cc/download
echo    - Place nssm.exe in this directory
echo    - Run "install_service.bat" as administrator
echo    - Start the service using Windows Services or "nssm start TimeRegistrator"
echo.
echo 3. For firewall configuration:
echo    - Make sure port 8080 is open in Windows Firewall
echo    - Run this command as administrator:
echo      netsh advfirewall firewall add rule name="Time Registrator" dir=in action=allow protocol=TCP localport=8080
echo.
echo 4. To access from other computers:
echo    - Use http://YOUR-SERVER-IP:8080
echo    - Or http://YOUR-SERVER-NAME:8080
echo.
pause 