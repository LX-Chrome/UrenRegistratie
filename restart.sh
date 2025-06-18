#!/bin/bash

# UrenRegistratie Restart Script
# =============================

# Set working directory to script location
cd "$(dirname "$0")"
echo "Working directory: $(pwd)"

# Create logs directory if needed
mkdir -p logs
mkdir -p instance

# Kill any existing gunicorn processes
echo "Stopping any existing gunicorn processes..."
pkill gunicorn 2>/dev/null
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

# Check if database exists
if [ ! -f "instance/database.db" ]; then
    echo "Database not found, attempting to create..."
    python -c "from app import app, db; with app.app_context(): db.create_all()" || echo "Warning: Failed to create database"
fi

# Check permissions
echo "Setting permissions for instance directory..."
chmod -R 755 instance
chmod -R 755 static

# Start Gunicorn with full path if possible, with more logging
if [ -f "venv/bin/gunicorn" ]; then
    echo "Starting Gunicorn using venv binary with debug logging..."
    ./venv/bin/gunicorn --workers 1 --bind 0.0.0.0:8000 --log-level debug \
        --error-logfile logs/error.log --access-logfile logs/access.log \
        --capture-output --timeout 120 wsgi:app
else
    echo "Starting Gunicorn using PATH with debug logging..."
    gunicorn --workers 1 --bind 0.0.0.0:8000 --log-level debug \
        --error-logfile logs/error.log --access-logfile logs/access.log \
        --capture-output --timeout 120 wsgi:app
fi 