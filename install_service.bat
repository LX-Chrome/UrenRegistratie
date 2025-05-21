@echo off 
echo Installing Time Registrator as a Windows Service... 
 
REM Check for NSSM 
if not exist nssm.exe ( 
    echo NSSM not found. Please download NSSM from nssm.cc and place nssm.exe in this directory. 
    pause 
    exit /b 1 
) 
 
nssm install TimeRegistrator "C:\Users\Administrator\Documents\GitHub\UrenRegistratie\run_production.bat" 
nssm set TimeRegistrator DisplayName "Time Registrator" 
nssm set TimeRegistrator Description "Time tracking and project management application" 
nssm set TimeRegistrator AppDirectory "C:\Users\Administrator\Documents\GitHub\UrenRegistratie\" 
nssm set TimeRegistrator Start SERVICE_AUTO_START 
 
echo Service installed. You can now start it with: 
echo   nssm start TimeRegistrator 
echo. 
echo Or use Windows Services Management Console to start/stop the service. 
pause 
