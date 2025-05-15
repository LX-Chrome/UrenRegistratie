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
    if not os.path.exists(venv_dir):
        print("Creating virtual environment...")
        subprocess.run([python_cmd, "-m", "venv", venv_dir])
        
        # Activate virtual environment and install dependencies
        if platform.system() == "Windows":
            pip_cmd = os.path.join(venv_dir, "Scripts", "pip")
            python_cmd = os.path.join(venv_dir, "Scripts", "python")
        else:
            pip_cmd = os.path.join(venv_dir, "bin", "pip")
            python_cmd = os.path.join(venv_dir, "bin", "python")
        
        # Install dependencies only on first run
        print("Installing dependencies (first time only)...")
        subprocess.run([pip_cmd, "install", "-r", "requirements.txt"])
    else:
        # Get python command from existing venv
        if platform.system() == "Windows":
            python_cmd = os.path.join(venv_dir, "Scripts", "python")
        else:
            python_cmd = os.path.join(venv_dir, "bin", "python")
            
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