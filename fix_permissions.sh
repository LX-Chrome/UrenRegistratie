#!/bin/bash

# Fix permissions script for UrenRegistratie
# =========================================

echo "Fixing permissions for UrenRegistratie..."

# Make all scripts executable
chmod +x *.sh 2>/dev/null || echo "Warning: Couldn't make all scripts executable"

# Create necessary directories with proper permissions
mkdir -p instance
mkdir -p static
mkdir -p static/js
mkdir -p static/css
mkdir -p logs
mkdir -p backups/files

# Create log files with correct permissions
touch logs/error.log logs/access.log logs/startup.log
chmod 666 logs/error.log logs/access.log logs/startup.log 2>/dev/null || echo "Warning: Couldn't set log file permissions"

# Database file permissions
if [ -f "instance/database.db" ]; then
    echo "Setting database file permissions..."
    chmod 666 instance/database.db 2>/dev/null || echo "Warning: Couldn't set database file permissions"
else
    echo "Creating empty database file..."
    touch instance/database.db
    chmod 666 instance/database.db 2>/dev/null || echo "Warning: Couldn't set database file permissions"
fi

# Check if we're running as root and fix ownership if needed
if [ "$EUID" -eq 0 ]; then
    # If running as root (e.g., with sudo), set ownership to www-data or current user
    if getent passwd www-data > /dev/null; then
        echo "Setting ownership to www-data..."
        chown -R www-data:www-data instance logs static
    else
        # Get the actual user if run with sudo
        ACTUAL_USER=$(who am i | awk '{print $1}')
        if [ -n "$ACTUAL_USER" ]; then
            echo "Setting ownership to $ACTUAL_USER..."
            chown -R $ACTUAL_USER:$ACTUAL_USER instance logs static
        fi
    fi
fi

echo "Permissions fixed successfully." 