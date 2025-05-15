#!/usr/bin/env python

"""
Quick start script for Time Registrator that skips all environment checks
and just runs the application directly.

This is useful after you've already set up the environment once.
"""

import os
import sys
import platform
import subprocess
import importlib.util

def check_key_packages():
    """Check for key packages and suggest fixes if they're missing."""
    key_packages = ["xhtml2pdf", "reportlab", "weasyprint"]
    missing = []
    
    for package in key_packages:
        if importlib.util.find_spec(package) is None:
            missing.append(package)
    
    if missing:
        print("Warning: The following required packages are missing:")
        for pkg in missing:
            print(f"  - {pkg}")
        print("\nYou may encounter errors when running the application.")
        print("To fix this issue, run fix_dependencies.py or fix_dependencies.bat")
        
        user_input = input("\nDo you want to continue anyway? (y/n): ")
        if user_input.lower() != 'y':
            print("Exiting. Please run fix_dependencies.py to fix the issues.")
            sys.exit(1)

def main():
    """Run the application directly with minimal overhead."""
    # Determine path to Python in virtual environment
    venv_dir = "venv"
    if platform.system() == "Windows":
        python_cmd = os.path.join(venv_dir, "Scripts", "python")
    else:
        python_cmd = os.path.join(venv_dir, "bin", "python")
    
    # Check if venv exists
    if not os.path.exists(python_cmd):
        print("Virtual environment not found. Please run 'python run.py' first.")
        sys.exit(1)
    
    # Verify key packages
    check_key_packages()
    
    # Start the application with the virtual environment python
    print("Starting the application...")
    subprocess.run([python_cmd, "main.py"])

if __name__ == "__main__":
    main() 