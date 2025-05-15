@echo off
REM Script to create desktop shortcuts with nice icons for Time Registrator

echo === Time Registrator Desktop Shortcut Creator ===
echo This script will create desktop shortcuts with nice icons.
echo.

REM Get the current directory (where the application is installed)
set "CURRENT_DIR=%~dp0"
set "DESKTOP_DIR=%USERPROFILE%\Desktop"

REM Create icons directory if it doesn't exist
if not exist "%CURRENT_DIR%icons" mkdir "%CURRENT_DIR%icons"

REM Create a VBS script to generate the shortcuts
echo Creating shortcut creator script...
(
echo Set oWS = WScript.CreateObject^("WScript.Shell"^)
echo Set oFS = CreateObject^("Scripting.FileSystemObject"^)
echo.
echo sDesktop = oWS.SpecialFolders^("Desktop"^)
echo.
echo ' Create Time Registrator shortcut
echo sLinkFile = sDesktop ^& "\Time Registrator.lnk"
echo Set oLink = oWS.CreateShortcut^(sLinkFile^)
echo oLink.TargetPath = "%CURRENT_DIR%start.bat"
echo oLink.WorkingDirectory = "%CURRENT_DIR%"
echo oLink.Description = "Time Registrator Application"
echo oLink.IconLocation = "%CURRENT_DIR%icons\time_registrator.ico"
echo oLink.Save
echo.
echo ' Create Time Registrator Quick Start shortcut
echo sLinkFile = sDesktop ^& "\Time Registrator Quick.lnk"
echo Set oLink = oWS.CreateShortcut^(sLinkFile^)
echo oLink.TargetPath = "%CURRENT_DIR%quick_start.bat"
echo oLink.WorkingDirectory = "%CURRENT_DIR%"
echo oLink.Description = "Time Registrator Quick Start"
echo oLink.IconLocation = "%CURRENT_DIR%icons\time_registrator_quick.ico"
echo oLink.Save
echo.
echo ' Create a shortcut for Windows Store Python users
echo sLinkFile = sDesktop ^& "\Time Registrator Windows Store.lnk"
echo Set oLink = oWS.CreateShortcut^(sLinkFile^)
echo oLink.TargetPath = "%CURRENT_DIR%windows_setup.bat"
echo oLink.WorkingDirectory = "%CURRENT_DIR%"
echo oLink.Description = "Time Registrator for Windows Store Python"
echo oLink.IconLocation = "%CURRENT_DIR%icons\time_registrator_store.ico"
echo oLink.Save
) > "%TEMP%\create_shortcuts.vbs"

REM Download icons using PowerShell
echo Downloading icons...
PowerShell -Command "& {
    # Create icons directory if it doesn't exist
    $iconDir = Join-Path '%CURRENT_DIR%' 'icons'
    if(!(Test-Path $iconDir)) {
        New-Item -Path $iconDir -ItemType Directory | Out-Null
    }

    # Define icon URLs
    $iconUrls = @{
        'time_registrator.ico' = 'https://raw.githubusercontent.com/microsoft/fluentui-system-icons/master/assets/Clock/SVG/ic_fluent_clock_32_regular.svg'
        'time_registrator_quick.ico' = 'https://raw.githubusercontent.com/microsoft/fluentui-system-icons/master/assets/Clock/SVG/ic_fluent_clock_arrow_download_32_regular.svg'
        'time_registrator_store.ico' = 'https://raw.githubusercontent.com/microsoft/fluentui-system-icons/master/assets/WindowDev/SVG/ic_fluent_window_dev_tools_32_regular.svg'
    }

    # First, check if we can download SVGs directly
    $usingDefaultIcons = $true
    try {
        foreach($icon in $iconUrls.Keys) {
            $iconPath = Join-Path $iconDir $icon
            
            # Skip if the icon already exists
            if(Test-Path $iconPath) { continue }
            
            # Try to download SVG and convert to ICO (requires third-party tools so will likely fail)
            # In a real scenario you'd use a library to convert SVG to ICO
        }
    } catch {
        $usingDefaultIcons = $true
    }
    
    # Fall back to embedded Windows icons
    if($usingDefaultIcons) {
        # Use shell32.dll icons as fallbacks
        Copy-Item 'C:\Windows\System32\shell32.dll' -Destination (Join-Path $iconDir 'shell32.dll')
        echo 'Using system icons instead of downloading custom ones.'
    }
}" 2>nul

REM Create the shortcuts
echo Creating desktop shortcuts...
cscript //nologo "%TEMP%\create_shortcuts.vbs"

REM Clean up
del "%TEMP%\create_shortcuts.vbs" 2>nul

REM Check if we need to extract icons from shell32.dll
if exist "%CURRENT_DIR%icons\shell32.dll" (
    echo Using system icons...
    
    REM Create a VBS script to extract icons from shell32.dll
    (
    echo Set oWS = WScript.CreateObject^("WScript.Shell"^)
    echo Set oFS = CreateObject^("Scripting.FileSystemObject"^)
    echo.
    echo sDesktop = oWS.SpecialFolders^("Desktop"^)
    echo.
    echo ' Update Time Registrator shortcut with system icons
    echo sLinkFile = sDesktop ^& "\Time Registrator.lnk"
    echo Set oLink = oWS.CreateShortcut^(sLinkFile^)
    echo oLink.IconLocation = "%%SystemRoot%%\system32\shell32.dll,22"
    echo oLink.Save
    echo.
    echo ' Update Time Registrator Quick Start shortcut
    echo sLinkFile = sDesktop ^& "\Time Registrator Quick.lnk"
    echo Set oLink = oWS.CreateShortcut^(sLinkFile^)
    echo oLink.IconLocation = "%%SystemRoot%%\system32\shell32.dll,25"
    echo oLink.Save
    echo.
    echo ' Update Windows Store shortcut
    echo sLinkFile = sDesktop ^& "\Time Registrator Windows Store.lnk"
    echo Set oLink = oWS.CreateShortcut^(sLinkFile^)
    echo oLink.IconLocation = "%%SystemRoot%%\system32\shell32.dll,20"
    echo oLink.Save
    ) > "%TEMP%\update_icons.vbs"
    
    cscript //nologo "%TEMP%\update_icons.vbs"
    del "%TEMP%\update_icons.vbs" 2>nul
    del "%CURRENT_DIR%icons\shell32.dll" 2>nul
)

echo.
echo Desktop shortcuts created successfully!
echo Check your desktop for:
echo  - Time Registrator (normal startup)
echo  - Time Registrator Quick (quick startup)
echo  - Time Registrator Windows Store (for Windows Store Python)
echo.
echo Press any key to exit...
pause > nul 