#!/bin/bash

# UrenRegistratie Error Diagnostic Tool
# ====================================

echo "=== UrenRegistratie Error Diagnostics ==="

# Set working directory
cd "$(dirname "$0")"
echo "Working directory: $(pwd)"

# Activate virtual environment
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
    echo "Virtual environment activated"
else
    echo "WARNING: No virtual environment found"
fi

# Check for Gunicorn logs
echo "Checking for Gunicorn error logs..."
if [ -f "logs/error.log" ]; then
    echo "Last 20 lines of Gunicorn error log:"
    tail -n 20 logs/error.log
else
    echo "No Gunicorn error log found"
fi

# Check for Flask logs
echo "Checking for Flask application errors..."
if [ -f "app.log" ]; then
    echo "Last 20 lines of Flask log:"
    tail -n 20 app.log
else
    echo "No Flask app.log found"
fi

# Check database
echo "Checking database..."
if [ -f "instance/database.db" ]; then
    echo "Database exists"
    # Check if database is readable
    sqlite3 instance/database.db "SELECT sqlite_version();" || echo "Error: Cannot read database"
else
    echo "WARNING: Database file not found in instance/database.db"
    # Check if we need to create the database
    echo "Attempting to create database..."
    python -c "from app import app, db; with app.app_context(): db.create_all()"
fi

# Check for permissions issues
echo "Checking permissions..."
ls -la instance/
ls -la static/

# Run the app in debug mode to see errors
echo "Do you want to run the app in debug mode to see errors? (y/n)"
read -r response
if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
    echo "Starting Flask in debug mode..."
    export FLASK_DEBUG=1
    export FLASK_APP=main.py
    python -c "from app import app; app.config['DEBUG'] = True; from routes import *; app.run(host='0.0.0.0', port=8000, debug=True)"
fi

echo "=== Diagnostics Complete ==="
echo "If you still see Internal Server Error, check the application code in routes.py" 