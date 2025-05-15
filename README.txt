TIME REGISTRATOR QUICK START GUIDE
===================================

IMPORTANT FOR WINDOWS USERS: 
If you're using Python from the Windows Store (installed from Microsoft Store), 
you MUST use the special startup scripts. If you get errors about "WindowsApps", 
this applies to you!

------------------
WINDOWS USERS
------------------

1. FIRST-TIME SETUP:

   NORMAL PYTHON (from python.org):
   - Double-click 'start.bat'

   WINDOWS STORE PYTHON:
   - Double-click 'windows_setup.bat'

2. SUBSEQUENT STARTUPS (faster):

   NORMAL PYTHON:
   - Double-click 'quick_start.bat' (with basic checks)
   - Double-click 'direct_start.bat' (fastest, no checks)

   WINDOWS STORE PYTHON:
   - Double-click 'windows_direct_start.bat'

3. FIXING DEPENDENCY ISSUES:
   - Double-click 'fix_dependencies.bat'

------------------
MAC/LINUX USERS
------------------

1. FIRST-TIME SETUP:
   - Open Terminal in this folder
   - Run: chmod +x start.sh
   - Run: ./start.sh

2. SUBSEQUENT STARTUPS (faster):
   - Run: ./quick_start.sh (with basic checks)
   - Run: ./direct_start.sh (fastest, no checks)

3. FIXING DEPENDENCY ISSUES:
   - Run: python fix_dependencies.py

------------------
HELP & TROUBLESHOOTING
------------------

1. Missing packages error:
   - Run fix_dependencies.bat (Windows) or python fix_dependencies.py (Mac/Linux)

2. venv creation errors (Windows):
   - You're likely using Windows Store Python; use windows_setup.bat instead

3. Other issues:
   - See full documentation in the docs folder 