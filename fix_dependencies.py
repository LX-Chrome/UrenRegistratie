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
    
    # Required packages that might be missing
    required_packages = [
        "xhtml2pdf",
        "reportlab",
        "weasyprint",
        "pdfkit",
        "Pillow",
        "flask-login",
        "flask-sqlalchemy",
        "python-dotenv"
    ]
    
    # Update pip first
    print("Updating pip...")
    subprocess.run([pip_cmd, "install", "--upgrade", "pip"])
    
    # Check and install each package
    missing_packages = []
    for package in required_packages:
        print(f"Checking {package}...")
        result = subprocess.run(
            [pip_cmd, "show", package],
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            missing_packages.append(package)
    
    # Install missing packages
    if missing_packages:
        print("\nThe following packages are missing and will be installed:")
        for package in missing_packages:
            print(f"  - {package}")
        
        for package in missing_packages:
            print(f"\nInstalling {package}...")
            try:
                subprocess.run([pip_cmd, "install", package], check=True)
                print(f"Successfully installed {package}")
            except subprocess.CalledProcessError:
                print(f"Failed to install {package}. Please install manually.")
    else:
        print("\nAll required packages are already installed.")
    
    # Install all requirements to be safe
    print("\nReinstalling all requirements to ensure consistency...")
    subprocess.run([pip_cmd, "install", "-r", "requirements.txt", "--upgrade"])
    
    print("\nDependency check complete!")
    print("If you still have issues, try running the application with 'python run.py'")

if __name__ == "__main__":
    fix_dependencies() 