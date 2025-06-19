#!/bin/bash

<<<<<<< HEAD
# Fix permissions for UrenRegistratie scripts
echo "Fixing permissions for executable scripts..."

# Make all shell scripts executable
chmod +x *.sh
chmod +x *.py

echo "Permission fix complete. You can now run:"
echo "./start_production.sh" 
=======
# Fix permissions script for UrenRegistratie
# =========================================

echo "Fixing permissions for UrenRegistratie..."

# Make all scripts executable
chmod +x *.sh

# Instead of changing permissions of directories, create them if they don't exist
mkdir -p instance
mkdir -p static
mkdir -p static/js
mkdir -p static/css
mkdir -p logs

# Create log files with correct permissions
touch logs/error.log
touch logs/access.log
chmod 666 logs/error.log logs/access.log

# Create an empty database file if it doesn't exist
if [ ! -f "instance/database.db" ]; then
    echo "Creating empty database file..."
    touch instance/database.db
    chmod 666 instance/database.db
fi

echo "Permissions fixed. Now run: ./restart.sh" 
>>>>>>> d067c1de0aa545f98a34b8b16ae0e1629cfa91c8
