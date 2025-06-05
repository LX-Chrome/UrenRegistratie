#!/bin/bash

# UrenRegistratie Production Start Script for Ubuntu
# =================================================

echo "Starting UrenRegistratie in production mode..."

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Check if gunicorn is installed
if ! pip show gunicorn > /dev/null; then
    echo "Installing gunicorn..."
    pip install gunicorn
fi

# Clean up any previous error log
if [ -f "startup_error.log" ]; then
    rm startup_error.log
fi

# Make fix_werkzeug.py executable
chmod +x fix_werkzeug.py

# Run the Werkzeug fix script first
echo "Applying Werkzeug compatibility fix..."
python fix_werkzeug.py

# Start directly with detailed error reporting and only one worker
echo "Starting with basic Gunicorn configuration for debugging..."
export PYTHONUNBUFFERED=1
gunicorn --capture-output --log-level debug --workers 1 --timeout 120 --bind 0.0.0.0:8000 wsgi:app

# Check if the error log was created
if [ -f "startup_error.log" ]; then
    echo "Error log found. Displaying contents:"
    cat startup_error.log
fi 