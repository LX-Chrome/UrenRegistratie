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
    
    # Start the application with the virtual environment python
    subprocess.run([python_cmd, "main.py"])

if __name__ == "__main__":
    main() 