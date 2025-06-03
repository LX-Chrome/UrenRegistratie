@echo off
REM Wrapper batch file that redirects to scripts/start.bat
echo Redirecting to scripts/start.bat...
cd %~dp0
scripts\start.bat %* 