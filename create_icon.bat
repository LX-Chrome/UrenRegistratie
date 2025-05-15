@echo off
REM Script to create a Time Registrator desktop shortcut with embedded icon

echo === Creating Time Registrator Icon ===
echo This script will create a desktop shortcut with a custom clock icon.
echo.

REM Create icons directory if it doesn't exist
if not exist "%~dp0icons" mkdir "%~dp0icons"

REM Create the icon file using base64 encoding/decoding
echo Creating icon file...
echo.

REM The base64 encoded icon is embedded directly in the script
REM This is a small clock icon
set "icon_file=%~dp0icons\timer.ico"

REM Create a temporary PowerShell script to decode the base64 and create the icon
echo $iconBytes = [Convert]::FromBase64String('AAABAAEAEBAAAAEAIABoBAAAFgAAACgAAAAQAAAAIAAAAAEAIAAAAAAAQAQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA0tLS/9LS0v/S0tL/0tLS/9LS0v/S0tL/0tLS/9LS0v/S0tL/0tLS/9LS0v8AAAAAAAAAAAAAAAAAAAAA0tLS/9LS0v/S0tL/0tLS/9LS0v/S0tL/0tLS/9LS0v/S0tL/0tLS/9LS0v/S0tL/0tLS/wAAAAAAAAAA0tLS/9LS0v/S0tL/0tLS/9LS0v9lZWX/FRUV/xUVFf9lZWX/0tLS/9LS0v/S0tL/0tLS/9LS0v8AAAAA0tLS/9LS0v/S0tL/0tLS/2VlZf8VFRX/FRUV/xUVFf8VFRX/FRUV/2VlZf/S0tL/0tLS/9LS0v/S0tL/0tLS/9LS0v/S0tL/0tLS/xUVFf8VFRX/FRUV/xUVFf8VFRX/FRUV/xUVFf/S0tL/0tLS/9LS0v/S0tL/0tLS/9LS0v/S0tL/0tLS/xUVFf8VFRX/FRUV/xUVFf8VFRX/FRUV/xUVFf/S0tL/0tLS/9LS0v/S0tL/0tLS/9LS0v/S0tL/0tLS/xUVFf8VFRX/kZGR/9LS0v/S0tL/kZGR/xUVFf/S0tL/0tLS/9LS0v/S0tL/0tLS/9LS0v/S0tL/0tLS/xUVFf8VFRX/0tLS/9LS0v/S0tL/0tLS/xUVFf/S0tL/0tLS/9LS0v/S0tL/0tLS/9LS0v/S0tL/0tLS/xUVFf8VFRX/0tLS/9LS0v/S0tL/0tLS/xUVFf/S0tL/0tLS/9LS0v/S0tL/0tLS/9LS0v/S0tL/0tLS/xUVFf8VFRX/0tLS/9LS0v/S0tL/0tLS/xUVFf/S0tL/0tLS/9LS0v/S0tL/0tLS/9LS0v/S0tL/ZWVl/xUVFf8VFRX/kZGR/9LS0v/S0tL/kZGR/xUVFf9lZWX/0tLS/9LS0v/S0tL/0tLS/9LS0v/S0tL/FRUV/xUVFf8VFRX/FRUV/xUVFf8VFRX/FRUV/xUVFf8VFRX/0tLS/9LS0v/S0tL/0tLS/9LS0v9lZWX/FRUV/xUVFf8VFRX/FRUV/xUVFf8VFRX/FRUV/xUVFf9lZWX/0tLS/9LS0v/S0tL/0tLS/9LS0v/S0tL/ZWVl/xUVFf8VFRX/ZWVl/9LS0v/S0tL/0tLS/9LS0v/S0tL/0tLS/9LS0v/S0tL/AAAAAAAAAADS0tL/0tLS/9LS0v/S0tL/0tLS/9LS0v/S0tL/0tLS/9LS0v/S0tL/0tLS/wAAAAAAAAAAAAAAAAAAAADS0tL/0tLS/9LS0v/S0tL/0tLS/9LS0v/S0tL/0tLS/9LS0v/S0tL/AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA') > "%TEMP%\create_icon.ps1"
echo [System.IO.File]::WriteAllBytes('%icon_file%', $iconBytes) >> "%TEMP%\create_icon.ps1"

REM Run the PowerShell script to create the icon
powershell -ExecutionPolicy Bypass -File "%TEMP%\create_icon.ps1"
del "%TEMP%\create_icon.ps1"

REM Create a VBS script to generate the shortcut with the icon
echo Creating desktop shortcut...
(
echo Set oWS = WScript.CreateObject^("WScript.Shell"^)
echo sDesktop = oWS.SpecialFolders^("Desktop"^)
echo.
echo sLinkFile = sDesktop ^& "\Time Registrator.lnk"
echo Set oLink = oWS.CreateShortcut^(sLinkFile^)
echo oLink.TargetPath = "%~dp0start.bat"
echo oLink.WorkingDirectory = "%~dp0"
echo oLink.Description = "Time Registrator Application"
echo oLink.IconLocation = "%icon_file%"
echo oLink.Save
) > "%TEMP%\create_shortcut.vbs"

REM Create the shortcut
cscript //nologo "%TEMP%\create_shortcut.vbs"

REM Clean up
del "%TEMP%\create_shortcut.vbs"

echo.
echo Desktop shortcut created with a custom clock icon!
echo You can now start Time Registrator from your desktop.
echo.
echo Press any key to exit...
pause > nul 