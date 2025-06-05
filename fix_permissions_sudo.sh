#!/bin/bash

echo "=== Fixing permissions with sudo privileges ==="

# Make this script executable first
chmod +x fix_permissions_sudo.sh

# Fix ownership of all files
echo "Setting ownership of files..."
sudo chown -R $USER:$USER .

# Make all script files executable
echo "Making scripts executable..."
sudo chmod +x *.sh
sudo chmod +x *.py

# Fix specific key files
sudo chmod +x start_production.sh
sudo chmod +x fix_werkzeug.py
sudo chmod +x wsgi.py
sudo chmod +x test_app.py
sudo chmod +x fix_permissions.sh

# Create necessary directories with proper permissions
echo "Setting up directories..."
sudo mkdir -p instance
sudo mkdir -p logs
sudo chmod -R 755 instance
sudo chmod -R 755 logs

# Check for and fix SELinux contexts if needed
if command -v sestatus &> /dev/null && sestatus | grep -q "enabled"; then
    echo "SELinux detected, fixing contexts..."
    sudo restorecon -Rv .
fi

echo "=== Permission fixes complete ==="
echo "Now try running: sudo ./start_production.sh" 