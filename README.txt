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

4. IF THE APPLICATION WON'T LOAD:
   - Double-click 'fix_loading.bat' (fixes common loading issues)
   - Double-click 'debug_server.bat' (for detailed diagnostics)

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

4. IF THE APPLICATION WON'T LOAD:
   - Run: python debug_server.py

------------------
HELP & TROUBLESHOOTING
------------------

1. Missing packages error:
   - Run fix_dependencies.bat (Windows) or python fix_dependencies.py (Mac/Linux)

2. venv creation errors (Windows):
   - You're likely using Windows Store Python; use windows_setup.bat instead

3. Application won't load (infinite loading):
   - Run fix_loading.bat to resolve common loading issues
   - Try using a different port by running debug_server.bat
   - Make sure no other application is using port 5000
   - Try accessing the app at http://localhost:5000 or http://127.0.0.1:5000

4. Other issues:
   - See full documentation in the docs folder 