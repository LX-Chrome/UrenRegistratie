#!/bin/bash

# UrenRegistratie Restart Fixed Script
# ===================================
# This version includes critical fixes for dashboard issues

set -e
echo "Starting UrenRegistratie with dashboard fixes..."

# Set working directory to script location
cd "$(dirname "$0")"
echo "Working directory: $(pwd)"

# Make scripts executable
chmod +x *.sh *.py 2>/dev/null || echo "Could not make all scripts executable"

# Stop any running processes
echo "Stopping any existing gunicorn processes..."
pkill -f "gunicorn.*wsgi:app" 2>/dev/null || echo "No gunicorn processes found"
sleep 2

# Run the fix permissions script
echo "Running fix_permissions.sh..."
./fix_permissions.sh || echo "Warning: fix_permissions.sh had issues"

# Create necessary directories
mkdir -p logs
mkdir -p instance
mkdir -p static/js
mkdir -p static/css
mkdir -p backups/files

# Apply dashboard fixes
echo "Applying dashboard template fixes..."
python3 quick_dashboard_fix.py || echo "Warning: Could not run dashboard fix script"

# Activate virtual environment
if [ -f "venv/bin/activate" ]; then
    echo "Activating venv..."
    source venv/bin/activate
elif [ -f "../venv/bin/activate" ]; then
    echo "Activating venv from parent directory..."
    source ../venv/bin/activate
else
    echo "WARNING: No venv found, using system Python"
fi

# Make sure gunicorn is installed
if ! command -v gunicorn >/dev/null 2>&1; then
    echo "Installing gunicorn..."
    pip install gunicorn
fi

# Explicitly set PYTHONPATH to include current directory
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
echo "Set PYTHONPATH to include current directory: $PYTHONPATH"

# Create simple wsgi test to check if modules can be imported
echo "Testing imports..."
python3 -c "import os, sys; sys.path.insert(0, os.getcwd()); import app; from app import app; import routes; print('Import test successful!')" || echo "WARNING: Import test failed"

# Start Gunicorn with explicit logging and debug
echo "Starting Gunicorn with error logging..."
if [ -f "venv/bin/gunicorn" ]; then
    echo "Using venv gunicorn binary..."
    nohup ./venv/bin/gunicorn --workers 1 --timeout 120 --log-level debug \
        --error-logfile logs/error.log --access-logfile logs/access.log \
        --bind 0.0.0.0:8000 wsgi:app > logs/startup.log 2>&1 &
else
    echo "Using system gunicorn..."
    nohup gunicorn --workers 1 --timeout 120 --log-level debug \
        --error-logfile logs/error.log --access-logfile logs/access.log \
        --bind 0.0.0.0:8000 wsgi:app > logs/startup.log 2>&1 &
fi

# Save PID for reference
echo $! > gunicorn.pid
echo "Gunicorn started with PID: $(cat gunicorn.pid)"

# Wait a moment and check if it's running
sleep 5
if ps -p $(cat gunicorn.pid) > /dev/null; then
    echo "Application successfully started!"
    echo "Check logs with: tail -f logs/error.log logs/startup.log"
    echo "Access the application at: http://SERVER_IP:8000"
else
    echo "ERROR: Application failed to start! Checking logs..."
    tail -n 50 logs/error.log logs/startup.log
    echo "Please run these commands to diagnose issues:"
    echo "  python3 diagnose_wsgi.py"
    echo "  cat logs/error.log"
    exit 1
fi 