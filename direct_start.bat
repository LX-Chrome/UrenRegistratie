@echo off
REM Wrapper batch file that redirects to scripts/direct_start.bat
echo Redirecting to scripts/direct_start.bat...
cd %~dp0
scripts\direct_start.bat %* 