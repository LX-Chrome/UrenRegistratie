@echo off
REM Simple script to create a desktop shortcut with a nice icon for start.bat

echo === Creating Time Registrator Desktop Icon ===
echo.

REM Create a VBS script to generate the shortcut
echo Creating shortcut...
(
echo Set oWS = WScript.CreateObject^("WScript.Shell"^)
echo sDesktop = oWS.SpecialFolders^("Desktop"^)
echo.
echo sLinkFile = sDesktop ^& "\Time Registrator.lnk"
echo Set oLink = oWS.CreateShortcut^(sLinkFile^)
echo oLink.TargetPath = "%~dp0start.bat"
echo oLink.WorkingDirectory = "%~dp0"
echo oLink.Description = "Time Registrator Application"
echo oLink.IconLocation = "C:\Windows\System32\shell32.dll,22"
echo oLink.Save
) > "%TEMP%\create_shortcut.vbs"

REM Create the shortcut
cscript //nologo "%TEMP%\create_shortcut.vbs"

REM Clean up
del "%TEMP%\create_shortcut.vbs"

echo.
echo Desktop shortcut created!
echo You can now start Time Registrator from your desktop.
echo.
echo Press any key to exit...
pause > nul 