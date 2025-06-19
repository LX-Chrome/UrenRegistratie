#!/bin/bash

# UrenRegistratie Restart Script - Enhanced for Ubuntu
# ===================================================

# Exit on error
set -e

# Set working directory to script location
cd "$(dirname "$0")"
echo "Working directory: $(pwd)"

# Make sure the script is executable
chmod +x restart.sh
chmod +x start_production.sh
chmod +x fix_permissions.sh

# Run the permissions fix script first
echo "Running fix_permissions.sh..."
./fix_permissions.sh

# Create required directories
mkdir -p logs
mkdir -p instance
mkdir -p static/js
mkdir -p static/css
mkdir -p backups/files

# Rotate log files if they're getting large (> 5MB)
for logfile in logs/error.log logs/access.log; do
    if [ -f "$logfile" ] && [ $(stat -c%s "$logfile" 2>/dev/null || echo 0) -gt 5000000 ]; then
        echo "Rotating $logfile..."
        timestamp=$(date +%Y%m%d_%H%M%S)
        mv "$logfile" "${logfile}.${timestamp}"
    fi
done

# Touch log files to ensure they exist with proper permissions
touch logs/error.log logs/access.log
chmod 666 logs/error.log logs/access.log

# Kill any existing gunicorn processes
echo "Stopping any existing gunicorn processes..."
pkill -f "gunicorn.*wsgi:app" 2>/dev/null || echo "No gunicorn processes found"
sleep 2

# Double check - force kill if still running
if pgrep -f "gunicorn.*wsgi:app" > /dev/null; then
    echo "Force killing gunicorn processes..."
    pkill -9 -f "gunicorn.*wsgi:app" 2>/dev/null || echo "Failed to force kill"
    sleep 1
fi

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

# Run with nohup to keep running after terminal closes
echo "Starting Gunicorn with error logging..."
if [ -f "venv/bin/gunicorn" ]; then
    echo "Using venv gunicorn binary..."
    nohup ./venv/bin/gunicorn --workers 3 --timeout 120 --log-level info \
        --error-logfile logs/error.log --access-logfile logs/access.log \
        --bind 0.0.0.0:8000 wsgi:app > logs/startup.log 2>&1 &
else
    echo "Using system gunicorn..."
    nohup gunicorn --workers 3 --timeout 120 --log-level info \
        --error-logfile logs/error.log --access-logfile logs/access.log \
        --bind 0.0.0.0:8000 wsgi:app > logs/startup.log 2>&1 &
fi

# Save PID for reference
echo $! > gunicorn.pid
echo "Gunicorn started with PID: $(cat gunicorn.pid)"
echo "To check if it's running: ps -p $(cat gunicorn.pid)"
echo "To view logs: tail -f logs/error.log logs/access.log logs/startup.log"

# Wait a moment and check if it's still running
sleep 3
if ps -p $(cat gunicorn.pid) > /dev/null; then
    echo "Application successfully started!"
else
    echo "ERROR: Application failed to start! Check logs/error.log and logs/startup.log"
    tail -n 20 logs/error.log logs/startup.log
    exit 1
fi 