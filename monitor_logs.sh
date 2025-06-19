#!/bin/bash

# UrenRegistratie Log Monitor
# ==========================

# Set working directory to script location
cd "$(dirname "$0")"
echo "Working directory: $(pwd)"

# Make sure log directory exists
mkdir -p logs

# Check if app is running
if [ -f "gunicorn.pid" ] && ps -p $(cat gunicorn.pid) > /dev/null; then
    echo "✅ Application is running with PID: $(cat gunicorn.pid)"
else
    echo "⚠️ Application is NOT running!"
    if [ -f "gunicorn.pid" ]; then
        echo "   PID file exists but process is not active: $(cat gunicorn.pid)"
    else
        echo "   No PID file found"
    fi

    # Check for other gunicorn processes
    RUNNING_PIDS=$(pgrep -f "gunicorn.*wsgi:app" || echo "")
    if [ -n "$RUNNING_PIDS" ]; then
        echo "   But found other gunicorn processes running: $RUNNING_PIDS"
    fi
fi

# Display system resources
echo -e "\n== System Resources =="
echo "Memory usage:"
free -h

echo -e "\nDisk space:"
df -h .

echo -e "\n== Recent Log Entries =="

# Check if there are any log files
if [ ! -f "logs/error.log" ] && [ ! -f "logs/access.log" ] && [ ! -f "logs/startup.log" ]; then
    echo "No log files found in logs/ directory!"
    exit 1
fi

# Show the latest entries from error log
if [ -f "logs/error.log" ]; then
    echo -e "\n=== Last 20 entries from error.log ==="
    tail -n 20 logs/error.log
else
    echo "No error.log file found!"
fi

# Show the latest entries from startup log
if [ -f "logs/startup.log" ]; then
    echo -e "\n=== Last 20 entries from startup.log ==="
    tail -n 20 logs/startup.log
else
    echo "No startup.log file found!"
fi

# Show the latest entries from access log
if [ -f "logs/access.log" ]; then
    echo -e "\n=== Last 10 entries from access.log ==="
    tail -n 10 logs/access.log
else
    echo "No access.log file found!"
fi

echo -e "\nTo continuously monitor logs, run: tail -f logs/error.log logs/startup.log"
echo "To restart the application, run: ./restart.sh" 