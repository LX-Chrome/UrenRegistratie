#!/bin/bash

echo "=== Installing UrenRegistratie Dependencies ==="

# Activate virtual environment
if [ -d "venv" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
else
    echo "Creating new virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    pip install --upgrade pip
fi

# Install specific packages that are required
echo "Installing reportlab (PDF libraries)..."
pip install reportlab==3.6.12

echo "Installing xhtml2pdf..."
pip install xhtml2pdf==0.2.11

echo "Installing other dependencies..."
pip install -r requirements.txt

# Check if xhtml2pdf was installed
if pip show xhtml2pdf > /dev/null; then
    echo "✅ xhtml2pdf installed successfully"
else
    echo "❌ Error: xhtml2pdf installation failed"
fi

echo "=== Dependency installation complete ===" 