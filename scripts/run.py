#!/usr/bin/env python

import os
import sys
import subprocess
import platform
import time

def is_windows_store_python():
    """Check if Python is from Windows Store."""
    if platform.system() != "Windows":
        return False
    
    # Check if python is installed in WindowsApps
    return "WindowsApps" in sys.executable

def setup_environment():
    """Setup virtual environment if it doesn't exist and install dependencies."""
    print("Checking environment...")
    
    # Determine OS-specific commands
    python_cmd = "python" if platform.system() == "Windows" else "python3"
    venv_dir = "venv"
    
    # Check if Windows Store Python (which has limitations)
    if is_windows_store_python():
        print("Detected Windows Store Python installation.")
        print("This version has restrictions on creating virtual environments.")
        print("Recommended: Use windows_setup.bat instead.")
        print("Attempting to continue without virtual environment...")
        
        # Install packages directly
        try:
            subprocess.run([python_cmd, "-m", "pip", "install", "-r", "requirements.txt"])
            
            # Install critical packages explicitly
            for pkg in ["xhtml2pdf", "reportlab", "weasyprint"]:
                try:
                    subprocess.run([python_cmd, "-m", "pip", "install", pkg])
                except:
                    print(f"Warning: Could not install {pkg}")
                    
            return python_cmd
        except Exception as e:
            print(f"Error: {e}")
            print("Please try running windows_setup.bat instead.")
            sys.exit(1)
    
    # Set up paths for regular Python
    if platform.system() == "Windows":
        pip_cmd = os.path.join(venv_dir, "Scripts", "pip")
        venv_python_cmd = os.path.join(venv_dir, "Scripts", "python")
    else:
        pip_cmd = os.path.join(venv_dir, "bin", "pip")
        venv_python_cmd = os.path.join(venv_dir, "bin", "python")
    
    # Check if virtual environment exists
    venv_exists = os.path.exists(venv_dir)
    if not venv_exists:
        print("Creating virtual environment...")
        try:
            subprocess.run([python_cmd, "-m", "venv", venv_dir], check=True)
        except subprocess.CalledProcessError:
            print("Error: Failed to create virtual environment.")
            print("If you're using Python from Windows Store, try windows_setup.bat instead.")
            sys.exit(1)
        
        # Install dependencies (only if we created a new venv)
        print("Installing dependencies...")
        try:
            subprocess.run([pip_cmd, "install", "-r", "requirements.txt"], check=True)
        except subprocess.CalledProcessError as e:
            print("Error: Failed to install dependencies.")
            print("Please try manually running: venv\\Scripts\\pip install -r requirements.txt")
            sys.exit(1)
    
    # Check for critical missing packages that cause common errors
    critical_packages = ["xhtml2pdf", "reportlab", "weasyprint"]
    missing = []
    
    for pkg in critical_packages:
        # Fast check using subprocess - only runs if venv exists
        result = subprocess.run(
            [pip_cmd, "show", pkg],
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            missing.append(pkg)
    
    # Install any missing critical packages
    if missing:
        print("Installing missing critical packages:")
        for pkg in missing:
            print(f"Installing {pkg}...")
            subprocess.run([pip_cmd, "install", pkg])
    
    return venv_python_cmd

def check_env_file():
    """Check if .env file exists, create a default one if it doesn't."""
    if not os.path.exists(".env"):
        print("Creating default .env file...")
        with open(".env", "w") as f:
            f.write("# Database configuration\n")
            f.write("DATABASE_URL=sqlite:///database.db\n\n")
            f.write("# Security\n")
            f.write(f"SESSION_SECRET={os.urandom(24).hex()}\n")
            f.write(f"API_KEY={os.urandom(24).hex()}\n\n")
            f.write("# Application configuration\n")
            f.write("DEBUG=True\n")
        print("Default .env file created. Please update with your configuration as needed.")

def run_app(python_cmd):
    """Run the Flask application."""
    print("Starting the application...")
    subprocess.run([python_cmd, "main.py"])

def main():
    """Main entry point."""
    start_time = time.time()
    print("=== Time Registrator Application Starter ===")
    
    # Setup environment
    python_cmd = setup_environment()
    
    # Check for .env file
    check_env_file()
    
    # Run the application
    elapsed = time.time() - start_time
    print(f"Setup completed in {elapsed:.2f} seconds")
    run_app(python_cmd)

if __name__ == "__main__":
    main() 