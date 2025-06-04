#!/bin/bash

# UrenRegistratie Production Start Script for Ubuntu
# =================================================

echo "Starting UrenRegistratie in production mode..."

# Check if the service is already running
if systemctl is-active --quiet urenregistratie; then
    echo "UrenRegistratie service is already running"
    echo "To restart: sudo systemctl restart urenregistratie"
    echo "To check status: sudo systemctl status urenregistratie"
    exit 0
fi

# Try to start the service if it exists
if systemctl list-unit-files | grep -q urenregistratie.service; then
    echo "Starting urenregistratie service..."
    sudo systemctl start urenregistratie
    echo "Service started. To check status: sudo systemctl status urenregistratie"
else
    # If service doesn't exist, run using gunicorn directly
    echo "Service not found, starting application directly..."
    
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
    
    # Start the application using gunicorn
    echo "Starting application with gunicorn..."
    gunicorn --workers 3 --bind 0.0.0.0:5000 main:app
fi 