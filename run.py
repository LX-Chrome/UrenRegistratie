#!/usr/bin/env python

import os
import sys
import subprocess
import platform
import time

def setup_environment():
    """Setup virtual environment if it doesn't exist and install dependencies."""
    print("Checking environment...")
    
    # Determine OS-specific commands
    python_cmd = "python" if platform.system() == "Windows" else "python3"
    venv_dir = "venv"
    
    # Set up paths
    if platform.system() == "Windows":
        pip_cmd = os.path.join(venv_dir, "Scripts", "pip")
        python_cmd = os.path.join(venv_dir, "Scripts", "python")
    else:
        pip_cmd = os.path.join(venv_dir, "bin", "pip")
        python_cmd = os.path.join(venv_dir, "bin", "python")
    
    # Check if virtual environment exists
    venv_exists = os.path.exists(venv_dir)
    if not venv_exists:
        print("Creating virtual environment...")
        try:
            subprocess.run([python_cmd, "-m", "venv", venv_dir], check=True)
        except subprocess.CalledProcessError:
            print("Error: Failed to create virtual environment. Make sure Python is installed correctly.")
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
    
    return python_cmd

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