#!/usr/bin/env python

"""
Ultra-fast direct start script for Time Registrator.
This script skips ALL checks and simply starts the application.

Use only after verifying that everything works correctly.
"""

import os
import sys
import platform
import subprocess

def main():
    """Run the application with no checks."""
    # Determine path to Python in virtual environment
    venv_dir = "venv"
    if platform.system() == "Windows":
        python_cmd = os.path.join(venv_dir, "Scripts", "python")
    else:
        python_cmd = os.path.join(venv_dir, "bin", "python")
    
    # Start the application directly
    try:
        subprocess.run([python_cmd, "main.py"])
    except Exception as e:
        print(f"Error: {e}")
        print("If you have dependency issues, run fix_dependencies.py")
        sys.exit(1)

if __name__ == "__main__":
    main() 