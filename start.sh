#!/bin/bash

# Time Registrator startup script for Unix-like systems

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is not installed. Please install Python 3 and try again."
    exit 1
fi

# Run the Python starter script
python3 run.py 