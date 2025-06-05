#!/bin/bash

# UrenRegistratie Production Start Script for Ubuntu
# =================================================

echo "Starting UrenRegistratie in production mode..."

# Check if running as root (sudo)
if [ "$EUID" -ne 0 ]; then
    echo "Note: You are not running with sudo. If you encounter permission issues, try: sudo ./start_production.sh"
fi

# Create necessary directories
mkdir -p instance logs

# Fix permissions for script files if needed
if [ ! -x "fix_werkzeug.py" ] || [ ! -x "wsgi.py" ]; then
    echo "Fixing script permissions..."
    chmod +x *.py
    chmod +x *.sh
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv || { echo "Failed to create venv. Try with sudo."; exit 1; }
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate || { echo "Failed to activate venv. Check permissions."; exit 1; }

# Check if gunicorn is installed
if ! pip show gunicorn > /dev/null; then
    echo "Installing gunicorn..."
    pip install gunicorn || { echo "Failed to install gunicorn. Try with sudo."; exit 1; }
fi

# Clean up any previous error log
if [ -f "startup_error.log" ]; then
    rm startup_error.log
fi

# Run the Werkzeug fix script first
echo "Applying Werkzeug compatibility fix..."
python fix_werkzeug.py || { echo "Failed to run fix_werkzeug.py. Check permissions."; exit 1; }

# Start directly with detailed error reporting and only one worker
echo "Starting with basic Gunicorn configuration for debugging..."
export PYTHONUNBUFFERED=1

# Create logs directory for Gunicorn
mkdir -p logs

# Try running with Gunicorn
echo "Starting Gunicorn..."
gunicorn --capture-output --log-level debug --workers 1 --timeout 120 \
         --bind 0.0.0.0:8000 --error-logfile logs/error.log \
         --access-logfile logs/access.log wsgi:app

# Check if the error log was created
if [ -f "startup_error.log" ]; then
    echo "Error log found. Displaying contents:"
    cat startup_error.log
fi

# Check Gunicorn logs as well
if [ -f "logs/error.log" ]; then
    echo "Gunicorn error log:"
    tail -n 20 logs/error.log
fi 