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

# Start Gunicorn with full path if possible
if [ -f "venv/bin/gunicorn" ]; then
    echo "Starting Gunicorn using venv binary..."
    ./venv/bin/gunicorn --workers 1 --bind 0.0.0.0:8000 wsgi:app
else
    echo "Starting Gunicorn using PATH..."
    gunicorn --workers 1 --bind 0.0.0.0:8000 wsgi:app
fi 