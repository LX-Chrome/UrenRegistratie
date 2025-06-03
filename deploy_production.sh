#!/bin/bash

# Quick Deployment Script for UrenRegistratie on Ubuntu
# ====================================================

echo "=== Starting UrenRegistratie Quick Deployment ==="

# Create logs directory if doesn't exist
mkdir -p logs

# Stop the existing service if it's running
if systemctl is-active --quiet urenregistratie; then
    echo "Stopping existing service..."
    sudo systemctl stop urenregistratie
fi

# Pull latest changes if this is a git repository
if [ -d ".git" ]; then
    echo "Updating from git repository..."
    git pull
fi

# Activate virtual environment or create if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install/update dependencies
echo "Updating dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Backup the database
if [ -f "instance/database.db" ]; then
    echo "Backing up database..."
    mkdir -p backups
    cp instance/database.db "backups/database_backup_$(date +%Y%m%d_%H%M%S).db"
fi

# Run database migrations if they exist
if [ -d "migrations" ]; then
    echo "Running database migrations..."
    flask db upgrade
fi

# Restart the service
if systemctl list-unit-files | grep -q urenregistratie.service; then
    echo "Restarting service..."
    sudo systemctl restart urenregistratie
else
    echo "Service not found. If you need to set up the service, run ubuntu_production_setup.sh instead."
fi

# Reload Nginx if it's installed
if command -v nginx >/dev/null 2>&1; then
    echo "Reloading Nginx..."
    sudo systemctl reload nginx
fi

echo ""
echo "=== UrenRegistratie Quick Deployment Complete ==="
echo "If this is your first deployment, consider running the full ubuntu_production_setup.sh script" 