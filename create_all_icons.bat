@echo off
REM Script to create desktop shortcuts for all Time Registrator versions with distinct icons

echo === Creating Time Registrator Desktop Icons ===
echo This script will create desktop shortcuts for all versions with distinct icons.
echo.

REM Create icons directory if it doesn't exist
if not exist "%~dp0icons" mkdir "%~dp0icons"

REM Create icon files by using resource icons from Windows
echo Creating icon files...

REM Standard Time Registrator icon - Use the Clock icon from imageres.dll
copy "C:\Windows\System32\imageres.dll" "%TEMP%\imageres.dll" >nul 2>&1
if exist "%TEMP%\imageres.dll" (
    REM Create VBS script to extract an icon
    echo Set objShell = CreateObject^("Shell.Application"^) > "%TEMP%\extract_icon1.vbs"
    echo Set objFolder = objShell.Namespace^("%TEMP%"^) >> "%TEMP%\extract_icon1.vbs"
    echo Set objFolderItem = objFolder.ParseName^("imageres.dll"^) >> "%TEMP%\extract_icon1.vbs"
    echo objFolderItem.InvokeVerb^("Extract"^) >> "%TEMP%\extract_icon1.vbs"
    
    cscript //nologo "%TEMP%\extract_icon1.vbs"
    del "%TEMP%\extract_icon1.vbs" >nul 2>&1
    del "%TEMP%\imageres.dll" >nul 2>&1
    
    REM Use a system icon as fallback
    echo Set oWS = WScript.CreateObject^("WScript.Shell"^) > "%TEMP%\create_shortcuts.vbs"
    echo sDesktop = oWS.SpecialFolders^("Desktop"^) >> "%TEMP%\create_shortcuts.vbs"
    echo. >> "%TEMP%\create_shortcuts.vbs"
    
    REM Standard Time Registrator shortcut
    echo sLinkFile = sDesktop ^& "\Time Registrator.lnk" >> "%TEMP%\create_shortcuts.vbs"
    echo Set oLink = oWS.CreateShortcut^(sLinkFile^) >> "%TEMP%\create_shortcuts.vbs"
    echo oLink.TargetPath = "%~dp0start.bat" >> "%TEMP%\create_shortcuts.vbs"
    echo oLink.WorkingDirectory = "%~dp0" >> "%TEMP%\create_shortcuts.vbs"
    echo oLink.Description = "Time Registrator Application" >> "%TEMP%\create_shortcuts.vbs"
    echo oLink.IconLocation = "%%SystemRoot%%\System32\shell32.dll,23" >> "%TEMP%\create_shortcuts.vbs"
    echo oLink.Save >> "%TEMP%\create_shortcuts.vbs"
    echo. >> "%TEMP%\create_shortcuts.vbs"
    
    REM Quick Start shortcut
    echo sLinkFile = sDesktop ^& "\Time Registrator - Quick.lnk" >> "%TEMP%\create_shortcuts.vbs"
    echo Set oLink = oWS.CreateShortcut^(sLinkFile^) >> "%TEMP%\create_shortcuts.vbs"
    echo oLink.TargetPath = "%~dp0quick_start.bat" >> "%TEMP%\create_shortcuts.vbs"
    echo oLink.WorkingDirectory = "%~dp0" >> "%TEMP%\create_shortcuts.vbs"
    echo oLink.Description = "Time Registrator Quick Start" >> "%TEMP%\create_shortcuts.vbs"
    echo oLink.IconLocation = "%%SystemRoot%%\System32\shell32.dll,25" >> "%TEMP%\create_shortcuts.vbs"
    echo oLink.Save >> "%TEMP%\create_shortcuts.vbs"
    echo. >> "%TEMP%\create_shortcuts.vbs"
    
    REM Direct Start shortcut
    echo sLinkFile = sDesktop ^& "\Time Registrator - Direct.lnk" >> "%TEMP%\create_shortcuts.vbs"
    echo Set oLink = oWS.CreateShortcut^(sLinkFile^) >> "%TEMP%\create_shortcuts.vbs"
    echo oLink.TargetPath = "%~dp0direct_start.bat" >> "%TEMP%\create_shortcuts.vbs"
    echo oLink.WorkingDirectory = "%~dp0" >> "%TEMP%\create_shortcuts.vbs"
    echo oLink.Description = "Time Registrator Direct Start" >> "%TEMP%\create_shortcuts.vbs"
    echo oLink.IconLocation = "%%SystemRoot%%\System32\shell32.dll,137" >> "%TEMP%\create_shortcuts.vbs"
    echo oLink.Save >> "%TEMP%\create_shortcuts.vbs"
    echo. >> "%TEMP%\create_shortcuts.vbs"
    
    REM Windows Store Python version shortcut
    echo sLinkFile = sDesktop ^& "\Time Registrator - Windows Store.lnk" >> "%TEMP%\create_shortcuts.vbs"
    echo Set oLink = oWS.CreateShortcut^(sLinkFile^) >> "%TEMP%\create_shortcuts.vbs"
    echo oLink.TargetPath = "%~dp0windows_setup.bat" >> "%TEMP%\create_shortcuts.vbs"
    echo oLink.WorkingDirectory = "%~dp0" >> "%TEMP%\create_shortcuts.vbs"
    echo oLink.Description = "Time Registrator for Windows Store Python" >> "%TEMP%\create_shortcuts.vbs"
    echo oLink.IconLocation = "%%SystemRoot%%\System32\shell32.dll,20" >> "%TEMP%\create_shortcuts.vbs"
    echo oLink.Save >> "%TEMP%\create_shortcuts.vbs"
    
    echo Creating shortcuts...
    cscript //nologo "%TEMP%\create_shortcuts.vbs"
    del "%TEMP%\create_shortcuts.vbs" >nul 2>&1
) else (
    echo Could not access system icons. Using alternative method...
    
    REM Use PowerShell to create shortcuts
    echo Creating shortcuts with default icons...
    powershell -Command "& {
        $WshShell = New-Object -ComObject WScript.Shell
        
        # Standard Time Registrator shortcut
        $Shortcut = $WshShell.CreateShortcut([System.IO.Path]::Combine($WshShell.SpecialFolders.Item('Desktop'), 'Time Registrator.lnk'))
        $Shortcut.TargetPath = '%~dp0start.bat'
        $Shortcut.WorkingDirectory = '%~dp0'
        $Shortcut.Description = 'Time Registrator Application'
        $Shortcut.IconLocation = '%SystemRoot%\System32\shell32.dll,23'
        $Shortcut.Save()
        
        # Quick Start shortcut
        $Shortcut = $WshShell.CreateShortcut([System.IO.Path]::Combine($WshShell.SpecialFolders.Item('Desktop'), 'Time Registrator - Quick.lnk'))
        $Shortcut.TargetPath = '%~dp0quick_start.bat'
        $Shortcut.WorkingDirectory = '%~dp0'
        $Shortcut.Description = 'Time Registrator Quick Start'
        $Shortcut.IconLocation = '%SystemRoot%\System32\shell32.dll,25'
        $Shortcut.Save()
        
        # Direct Start shortcut
        $Shortcut = $WshShell.CreateShortcut([System.IO.Path]::Combine($WshShell.SpecialFolders.Item('Desktop'), 'Time Registrator - Direct.lnk'))
        $Shortcut.TargetPath = '%~dp0direct_start.bat'
        $Shortcut.WorkingDirectory = '%~dp0'
        $Shortcut.Description = 'Time Registrator Direct Start'
        $Shortcut.IconLocation = '%SystemRoot%\System32\shell32.dll,137'
        $Shortcut.Save()
        
        # Windows Store Python version shortcut
        $Shortcut = $WshShell.CreateShortcut([System.IO.Path]::Combine($WshShell.SpecialFolders.Item('Desktop'), 'Time Registrator - Windows Store.lnk'))
        $Shortcut.TargetPath = '%~dp0windows_setup.bat'
        $Shortcut.WorkingDirectory = '%~dp0'
        $Shortcut.Description = 'Time Registrator for Windows Store Python'
        $Shortcut.IconLocation = '%SystemRoot%\System32\shell32.dll,20'
        $Shortcut.Save()
    }" >nul 2>&1
)

echo.
echo Desktop shortcuts created with nice icons!
echo Check your desktop for:
echo  - Time Registrator (standard startup)
echo  - Time Registrator - Quick (faster startup)
echo  - Time Registrator - Direct (fastest startup)
echo  - Time Registrator - Windows Store (for Windows Store Python)
echo.
echo Press any key to exit...
pause > nul 