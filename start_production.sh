#!/bin/bash

# Simple UrenRegistratie Production Starter
# ========================================

# Activate virtual environment
source venv/bin/activate 2>/dev/null || echo "Note: Could not find/activate venv"

# Start Gunicorn directly with minimal options
echo "Starting Gunicorn server on port 8000..."
gunicorn --workers 1 --bind 0.0.0.0:8000 wsgi:app

# If you need to stop it, run: pkill gunicorn 