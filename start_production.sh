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
if [ ! -x "wsgi.py" ]; then
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

# Check for required packages
REQUIRED_PACKAGES=("xhtml2pdf" "reportlab")
MISSING_PACKAGES=()

for pkg in "${REQUIRED_PACKAGES[@]}"; do
    if ! pip show $pkg > /dev/null 2>&1; then
        MISSING_PACKAGES+=($pkg)
    fi
done

# Install missing packages
if [ ${#MISSING_PACKAGES[@]} -gt 0 ]; then
    echo "Missing required packages: ${MISSING_PACKAGES[*]}"
    echo "Installing dependencies..."
    
    # Ensure reportlab is downgraded to compatible version
    pip install reportlab==3.6.12 || { echo "Failed to install reportlab"; exit 1; }
    
    # Install xhtml2pdf with specific version
    pip install xhtml2pdf==0.2.11 || { echo "Failed to install xhtml2pdf"; exit 1; }
    
    # Install other required packages
    pip install -r requirements.txt || { echo "Failed to install requirements"; exit 1; }
fi

# Check if gunicorn is installed
if ! pip show gunicorn > /dev/null; then
    echo "Installing gunicorn..."
    pip install gunicorn || { echo "Failed to install gunicorn. Try with sudo."; exit 1; }
fi

# Clean up any previous error log
if [ -f "startup_error.log" ]; then
    rm startup_error.log
fi

# First test if wsgi.py works directly
echo "Testing WSGI module directly..."
python wsgi.py &
WSGI_PID=$!

# Give it a moment to start
sleep 3

# Check if it's still running
if kill -0 $WSGI_PID 2>/dev/null; then
    echo "WSGI module works! Stopping test process..."
    kill $WSGI_PID
    
    # Start with Gunicorn
    echo "Starting with Gunicorn..."
    mkdir -p logs
    
    # Try running with Gunicorn
    echo "Starting Gunicorn server..."
    gunicorn --capture-output --log-level debug --workers 1 --timeout 120 \
             --bind 0.0.0.0:8000 --error-logfile logs/error.log \
             --access-logfile logs/access.log wsgi:app
else
    echo "WSGI module failed to start. Check logs for errors."
    # Check if the error log was created
    if [ -f "startup_error.log" ]; then
        echo "Error log found. Displaying contents:"
        cat startup_error.log
    fi
fi

# Check Gunicorn logs as well
if [ -f "logs/error.log" ]; then
    echo "Gunicorn error log:"
    tail -n 20 logs/error.log
fi 