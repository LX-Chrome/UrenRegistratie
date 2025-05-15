#!/usr/bin/env python

"""
Dependency fixer for Time Registrator

This script checks for and installs missing dependencies that are
required by the Time Registrator application.
"""

import os
import sys
import subprocess
import platform

def fix_dependencies():
    """Check and install missing dependencies."""
    print("=== Time Registrator Dependency Fixer ===")
    
    # Determine OS-specific paths
    venv_dir = "venv"
    if platform.system() == "Windows":
        pip_cmd = os.path.join(venv_dir, "Scripts", "pip")
        python_cmd = os.path.join(venv_dir, "Scripts", "python")
    else:
        pip_cmd = os.path.join(venv_dir, "bin", "pip")
        python_cmd = os.path.join(venv_dir, "bin", "python")
    
    if not os.path.exists(pip_cmd):
        print(f"Error: Virtual environment not found at {venv_dir}")
        print("Please run 'python run.py' first to set up the environment.")
        sys.exit(1)
    
    # Most common missing packages that cause errors
    critical_packages = [
        "xhtml2pdf",
        "reportlab",
        "weasyprint"
    ]
    
    # Check and install each critical package
    missing_packages = []
    for package in critical_packages:
        print(f"Checking {package}...")
        result = subprocess.run(
            [pip_cmd, "show", package],
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            missing_packages.append(package)
    
    # Install only missing critical packages
    if missing_packages:
        print("\nInstalling missing critical packages:")
        for package in missing_packages:
            print(f"Installing {package}...")
            try:
                subprocess.run([pip_cmd, "install", package], check=True)
                print(f"Successfully installed {package}")
            except subprocess.CalledProcessError:
                print(f"Failed to install {package}.")
    else:
        print("\nAll critical packages are installed.")
    
    print("\nDependency check complete!")
    print("Try starting the application now.")

if __name__ == "__main__":
    fix_dependencies() 