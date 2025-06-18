#!/bin/bash

# UrenRegistratie Permission Fix Script
# ===================================

echo "=== Fixing permissions for UrenRegistratie ==="

# Get current user
CURRENT_USER=$(whoami)
echo "Current user: $CURRENT_USER"

# Create necessary directories
echo "Creating directories..."
sudo mkdir -p logs
sudo mkdir -p instance
sudo mkdir -p static

# Set ownership
echo "Setting ownership..."
sudo chown -R $CURRENT_USER:$CURRENT_USER logs
sudo chown -R $CURRENT_USER:$CURRENT_USER instance
sudo chown -R $CURRENT_USER:$CURRENT_USER static
sudo chown -R $CURRENT_USER:$CURRENT_USER .git

# Set full permissions
echo "Setting permissions..."
sudo chmod -R 777 logs
sudo chmod -R 777 instance
sudo chmod -R 755 static
sudo chmod -R 775 .git

echo "=== Permissions fixed successfully ==="
echo "Now you can run: ./restart.sh" 