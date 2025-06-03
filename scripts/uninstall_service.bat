@echo off 
echo Uninstalling Time Registrator service... 
if not exist nssm.exe ( 
    echo NSSM not found. Please download NSSM from nssm.cc and place nssm.exe in this directory. 
    pause 
    exit /b 1 
) 
nssm stop TimeRegistrator 
nssm remove TimeRegistrator confirm 
echo Service removed. 
pause 
