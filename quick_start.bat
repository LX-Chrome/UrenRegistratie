@echo off
REM Wrapper batch file that redirects to scripts/quick_start.bat
echo Redirecting to scripts/quick_start.bat...
cd %~dp0
scripts\quick_start.bat %* 