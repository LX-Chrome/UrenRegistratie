@echo off
setlocal enabledelayedexpansion

echo.
echo UrenRegistratie Admin Account Creator
echo ====================================
echo.

:username_prompt
set /p username="Enter username: "
if "!username!"=="" (
    echo Username cannot be empty!
    goto username_prompt
)

:email_prompt
set /p email="Enter email: "
if "!email!"=="" (
    echo Email cannot be empty!
    goto email_prompt
)

:password_prompt
set /p password="Enter password: "
if "!password!"=="" (
    echo Password cannot be empty!
    goto password_prompt
)

:confirm_prompt
set /p confirm="Confirm password: "
if not "!password!"=="!confirm!" (
    echo Passwords do not match! Please try again.
    goto password_prompt
)

echo.
echo Creating admin account with the following details:
echo Username: !username!
echo Email: !email!
echo.

set /p proceed="Proceed? (y/n): "
if /i not "!proceed!"=="y" (
    echo Operation cancelled.
    goto end
)

echo.
echo Running Python script to create admin account...
python create_admin_interactive.py "!username!" "!email!" "!password!"

:end
echo.
echo Press any key to exit...
pause > nul
