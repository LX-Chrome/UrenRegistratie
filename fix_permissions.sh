#!/bin/bash

# Fix permissions for UrenRegistratie scripts
echo "Fixing permissions for executable scripts..."

# Make all shell scripts executable
chmod +x *.sh
chmod +x *.py

echo "Permission fix complete. You can now run:"
echo "./start_production.sh" 