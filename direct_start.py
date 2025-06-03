#!/usr/bin/env python
"""
Wrapper script for direct start.
This redirects to scripts/direct_start.py for backwards compatibility.
"""

import sys
import os
import subprocess

def main():
    """Run the direct start script in the scripts directory"""
    script_path = os.path.join('scripts', 'direct_start.py')
    
    # Check if the script exists
    if not os.path.exists(script_path):
        print(f"Error: Script not found at {script_path}")
        print("Make sure you're running this from the project root directory.")
        sys.exit(1)
    
    # Pass all command line arguments to the actual script
    cmd = [sys.executable, script_path] + sys.argv[1:]
    
    try:
        result = subprocess.run(cmd)
        sys.exit(result.returncode)
    except KeyboardInterrupt:
        print("\nInterrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"Error executing {script_path}: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 