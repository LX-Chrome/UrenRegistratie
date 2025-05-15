#!/usr/bin/env python

"""
Debug server script for Time Registrator

This script helps identify and fix issues with server loading.
It attempts various fixes for common problems and provides detailed output.
"""

import os
import sys
import socket
import subprocess
import platform
import time

def check_port_availability(port=5000):
    """Check if the port is available or already in use."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)  # 2 second timeout
        result = sock.connect_ex(('127.0.0.1', port))
        sock.close()
        
        if result == 0:
            # Port is already in use
            return False
        else:
            # Port is available
            return True
    except Exception as e:
        print(f"Error checking port: {e}")
        return False

def find_available_port(start_port=5000, max_attempts=10):
    """Find an available port starting from start_port."""
    port = start_port
    attempts = 0
    
    while attempts < max_attempts:
        if check_port_availability(port):
            return port
        port += 1
        attempts += 1
    
    return None  # No available port found

def check_database_access():
    """Check if database file is accessible and not locked."""
    db_path = "database.db"
    if not os.path.exists(db_path):
        print("Database file not found. It will be created when the app starts.")
        return True
    
    try:
        # Try to open the database file to check if it's locked
        with open(db_path, 'r+b'):
            pass
        return True
    except IOError:
        return False

def check_host_resolves():
    """Check if the hostname resolves correctly."""
    try:
        hostname = socket.gethostname()
        ip = socket.gethostbyname(hostname)
        print(f"Hostname: {hostname}, IP: {ip}")
        return True
    except Exception as e:
        print(f"Hostname resolution error: {e}")
        return False

def run_debug_server(port=5000):
    """Run the Flask app in debug mode with extra output."""
    # Determine Python command
    if os.path.exists("venv"):
        if platform.system() == "Windows":
            python_cmd = os.path.join("venv", "Scripts", "python")
        else:
            python_cmd = os.path.join("venv", "bin", "python")
    else:
        python_cmd = "python"
    
    # Load the Flask app with explicit host binding and port
    print(f"Starting debug server on port {port}...")
    print("Press Ctrl+C to stop the server")
    print("=" * 40)
    
    try:
        # Use -u for unbuffered output to see logs immediately
        env = os.environ.copy()
        env["FLASK_DEBUG"] = "1"
        env["FLASK_ENV"] = "development"
        
        # Run main.py directly with explicit host and port
        subprocess.run([
            python_cmd, "-u", "main.py", 
            "--host=0.0.0.0", f"--port={port}", "--debug"
        ], env=env)
    except KeyboardInterrupt:
        print("\nServer stopped by user")
    except Exception as e:
        print(f"Error starting server: {e}")

def edit_main_py_for_debug():
    """Edit main.py to ensure it binds to all interfaces and accepts host/port parameters."""
    try:
        with open("main.py", "r") as f:
            content = f.read()
        
        # Only modify if it seems we need to
        if "if __name__ == \"__main__\":" in content and "app.run" in content:
            # Very simple modification - this assumes a standard structure
            if "host=" not in content or "port=" not in content or "0.0.0.0" not in content:
                updated_content = content.replace(
                    'if __name__ == "__main__":\n    app.run(', 
                    'if __name__ == "__main__":\n    import argparse\n    parser = argparse.ArgumentParser()\n    parser.add_argument("--host", default="0.0.0.0")\n    parser.add_argument("--port", type=int, default=5000)\n    parser.add_argument("--debug", action="store_true")\n    args = parser.parse_args()\n    app.run(host=args.host, port=args.port, debug=args.debug or '
                )
                
                if updated_content == content:  # If the above replace didn't work
                    updated_content = content.replace(
                        'if __name__ == "__main__":\n    app.run', 
                        'if __name__ == "__main__":\n    import argparse\n    parser = argparse.ArgumentParser()\n    parser.add_argument("--host", default="0.0.0.0")\n    parser.add_argument("--port", type=int, default=5000)\n    parser.add_argument("--debug", action="store_true")\n    args = parser.parse_args()\n    app.run'
                    )
                
                with open("main.py", "w") as f:
                    f.write(updated_content)
                print("Enhanced main.py for better network compatibility")
        
    except Exception as e:
        print(f"Warning: Could not update main.py: {e}")

def main():
    """Main debug function."""
    print("=" * 50)
    print("Time Registrator Debug Server")
    print("=" * 50)
    print("This script will help diagnose loading issues.")
    print("\nStarting diagnostics...\n")
    
    # Check port availability
    default_port = 5000
    print(f"Checking if port {default_port} is available...")
    if not check_port_availability(default_port):
        print(f"Port {default_port} is already in use!")
        new_port = find_available_port(default_port + 1)
        if new_port:
            print(f"Found available port: {new_port}")
            default_port = new_port
        else:
            print("Could not find an available port. Try closing other applications.")
            return
    else:
        print(f"Port {default_port} is available.")
    
    # Check database
    print("\nChecking database accessibility...")
    if check_database_access():
        print("Database is accessible.")
    else:
        print("Warning: Database appears to be locked or inaccessible.")
        print("This might cause issues. Try closing other instances of the application.")
    
    # Check hostname resolution
    print("\nChecking network configuration...")
    check_host_resolves()
    
    # Edit main.py if needed
    print("\nEnsuring main.py has proper network configuration...")
    edit_main_py_for_debug()
    
    print("\nStarting debug server...")
    print("Once the server starts, open your browser and navigate to:")
    print(f"http://localhost:{default_port}")
    print(f"http://127.0.0.1:{default_port}")
    print(f"http://<your-computer-ip>:{default_port}")
    
    # Run debug server
    time.sleep(2)  # Give the user time to read
    run_debug_server(default_port)

if __name__ == "__main__":
    main() 