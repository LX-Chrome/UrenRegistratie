#!/bin/bash

# UrenRegistratie Restart Script
# =============================

# Set working directory to script location
cd "$(dirname "$0")"
echo "Working directory: $(pwd)"

# Make sure the script is executable (helps after git pull)
chmod +x restart.sh

# Instead of trying to change permissions, just make sure directories exist
mkdir -p logs
mkdir -p instance
mkdir -p static/js
mkdir -p static/css

# Try to create log files if they don't exist (don't error if permission denied)
touch logs/error.log 2>/dev/null || true
touch logs/access.log 2>/dev/null || true

# Kill any existing gunicorn processes
echo "Stopping any existing gunicorn processes..."
pkill gunicorn 2>/dev/null || true
sleep 1

# Activate virtual environment - try multiple possible paths
if [ -f "venv/bin/activate" ]; then
    echo "Activating venv..."
    source venv/bin/activate
elif [ -f "../venv/bin/activate" ]; then
    echo "Activating venv from parent directory..."
    source ../venv/bin/activate
else
    echo "WARNING: No venv found, using system Python"
fi

# Check if gunicorn is installed
if ! command -v gunicorn >/dev/null 2>&1; then
    echo "Installing gunicorn..."
    pip install gunicorn
fi

# Try to check if the database file exists, but don't error if permission denied
if [ ! -f "instance/database.db" ] 2>/dev/null; then
    echo "Will try to create database tables on startup if needed..."
fi

# Start Gunicorn with error logging and debug mode
echo "Starting Gunicorn with error logging..."
if [ -f "venv/bin/gunicorn" ]; then
    ./venv/bin/gunicorn --workers 1 --log-level debug \
                        --bind 0.0.0.0:8000 wsgi:app 2>logs/error.log
else
    gunicorn --workers 1 --log-level debug \
             --bind 0.0.0.0:8000 wsgi:app 2>logs/error.log
fi 