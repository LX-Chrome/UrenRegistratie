#!/bin/bash

echo "=== Starting UrenRegistratie in minimal debug mode ==="

# Activate virtual environment
source venv/bin/activate || { echo "Failed to activate venv"; exit 1; }

# Run the debug test first
echo "Running import diagnosis..."
python debug_import.py

# If debug test passes, try a minimal Flask run
if [ $? -eq 0 ]; then
    echo "Debug test passed, trying direct Flask run..."
    export FLASK_APP=main.py
    export FLASK_ENV=development
    export FLASK_DEBUG=1
    
    # Run Flask directly
    python -c "from app import app; app.run(host='0.0.0.0', port=8000, debug=True)"
fi 