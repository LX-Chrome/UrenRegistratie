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
    
    # Check if virtual environment exists
    venv_exists = os.path.exists(venv_dir)
    if not venv_exists:
        print("Creating virtual environment...")
        try:
            subprocess.run([python_cmd, "-m", "venv", venv_dir], check=True)
        except subprocess.CalledProcessError:
            print("Error: Failed to create virtual environment. Make sure Python is installed correctly.")
            sys.exit(1)
        
    # Activate virtual environment and install dependencies
    if platform.system() == "Windows":
        pip_cmd = os.path.join(venv_dir, "Scripts", "pip")
        python_cmd = os.path.join(venv_dir, "Scripts", "python")
    else:
        pip_cmd = os.path.join(venv_dir, "bin", "pip")
        python_cmd = os.path.join(venv_dir, "bin", "python")
    
    # Always update pip first
    print("Updating pip...")
    try:
        subprocess.run([pip_cmd, "install", "--upgrade", "pip"], check=True)
    except subprocess.CalledProcessError:
        print("Warning: Failed to update pip, but continuing with installation.")
    
    # Install or upgrade dependencies
    print("Installing dependencies...")
    try:
        # Use verbose output to show what's happening
        result = subprocess.run(
            [pip_cmd, "install", "-r", "requirements.txt", "--upgrade"], 
            check=True,
            capture_output=True,
            text=True
        )
        if "failed" in result.stderr.lower():
            print("Warning: Some packages failed to install.")
            print(result.stderr)
    except subprocess.CalledProcessError as e:
        print("Error: Failed to install dependencies.")
        print(e.stderr if e.stderr else "Unknown error")
        print("Please try manually running: venv\\Scripts\\pip install -r requirements.txt")
        sys.exit(1)
    
    # Verify key packages are installed
    print("Verifying key packages...")
    try:
        # Check for xhtml2pdf which was missing
        result = subprocess.run(
            [pip_cmd, "show", "xhtml2pdf"],
            capture_output=True,
            text=True
        )
        if "not found" in result.stderr.lower() or result.returncode != 0:
            print("Installing missing package: xhtml2pdf")
            subprocess.run([pip_cmd, "install", "xhtml2pdf"], check=True)
            
        # Check for other reported missing packages
        for pkg in ["reportlab", "weasyprint"]:
            result = subprocess.run(
                [pip_cmd, "show", pkg],
                capture_output=True,
                text=True
            )
            if "not found" in result.stderr.lower() or result.returncode != 0:
                print(f"Installing missing package: {pkg}")
                subprocess.run([pip_cmd, "install", pkg], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Warning: Failed to verify some packages. {e}")
        print("The application may not function correctly.")
    
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
    
    # Import the Flask app and run it
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