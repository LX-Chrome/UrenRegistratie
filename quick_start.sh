#!/bin/bash

# Quick start Time Registrator (fast, assumes already set up)

# Check if venv exists
if [ ! -d "venv" ]; then
    echo "Virtual environment not found."
    echo "Please run 'python run.py' first to set up the environment."
    exit 1
fi

# Start the application using the virtual environment
echo "Starting the application..."
./venv/bin/python quick_start.py

# If there was an error, suggest running the fix_dependencies script
if [ $? -ne 0 ]; then
    echo ""
    echo "There was an error starting the application."
    echo "If you're missing dependencies, try running:"
    echo "python fix_dependencies.py"
fi 