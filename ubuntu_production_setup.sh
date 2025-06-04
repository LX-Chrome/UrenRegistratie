#!/bin/bash

# Production Setup Script for UrenRegistratie on Ubuntu
# ====================================================

# Exit on error
set -e

echo "=== Starting UrenRegistratie Production Setup ==="

# Update system packages
echo "Updating system packages..."
sudo apt-get update
sudo apt-get upgrade -y

# Install required system packages
echo "Installing system dependencies..."
sudo apt-get install -y python3 python3-pip python3-venv nginx supervisor build-essential python3-dev

# Create a directory for the application if not exists
APP_DIR="/opt/urenregistratie"
echo "Creating application directory at $APP_DIR..."
sudo mkdir -p $APP_DIR
sudo chown $USER:$USER $APP_DIR

# Clone or copy the application
if [ ! -d "$APP_DIR/.git" ] && [ -d ".git" ]; then
    echo "Copying current repository to $APP_DIR..."
    rsync -av --exclude 'venv' --exclude '__pycache__' --exclude '.git' ./ $APP_DIR/
else
    echo "Setting up a fresh clone in $APP_DIR..."
    # If you're cloning from a private repository, you'll need to set up authentication
    git clone https://github.com/YourUsername/UrenRegistratie.git $APP_DIR || echo "Using existing files"
fi

# Navigate to app directory
cd $APP_DIR

# Create and activate a virtual environment
echo "Setting up Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating .env file with production settings..."
    cat > .env << EOF
FLASK_APP=main.py
FLASK_ENV=production
SECRET_KEY=$(python3 -c 'import secrets; print(secrets.token_hex(16))')
DATABASE_URL=sqlite:///$APP_DIR/instance/database.db
DEBUG=False
EOF
fi

# Create instance directory if it doesn't exist
mkdir -p instance

# Copy database backup if available
if [ -f "backups/database_backup_20250518_003442.db" ]; then
    echo "Restoring database from backup..."
    cp backups/database_backup_20250518_003442.db instance/database.db
else
    echo "No database backup found. A fresh database will be created on first run."
fi

# Create a production server file from template
if [ -f "production_server.py.template" ]; then
    echo "Creating production server configuration..."
    cp production_server.py.template production_server.py
fi

# Set up Gunicorn systemd service
echo "Setting up Gunicorn systemd service..."
sudo tee /etc/systemd/system/urenregistratie.service > /dev/null << EOF
[Unit]
Description=UrenRegistratie Gunicorn daemon
After=network.target

[Service]
User=$USER
Group=www-data
WorkingDirectory=$APP_DIR
Environment="PATH=$APP_DIR/venv/bin"
ExecStart=$APP_DIR/venv/bin/gunicorn --workers 3 --bind unix:$APP_DIR/urenregistratie.sock -m 007 main:app

[Install]
WantedBy=multi-user.target
EOF

# Set up Nginx configuration
echo "Setting up Nginx configuration..."
sudo tee /etc/nginx/sites-available/urenregistratie > /dev/null << EOF
server {
    listen 80;
    server_name _;  # Replace with your domain if available

    location / {
        include proxy_params;
        proxy_pass http://unix:$APP_DIR/urenregistratie.sock;
    }

    location /static {
        alias $APP_DIR/static;
    }
}
EOF

# Enable the site
sudo ln -sf /etc/nginx/sites-available/urenregistratie /etc/nginx/sites-enabled/

# Remove default nginx site if it exists
if [ -f /etc/nginx/sites-enabled/default ]; then
    sudo rm /etc/nginx/sites-enabled/default
fi

# Test Nginx configuration
sudo nginx -t

# Reload Nginx
sudo systemctl reload nginx

# Start and enable the Gunicorn service
echo "Starting Gunicorn service..."
sudo systemctl start urenregistratie
sudo systemctl enable urenregistratie

# Check status
echo "Checking service status..."
sudo systemctl status urenregistratie --no-pager

echo ""
echo "=== UrenRegistratie Production Setup Complete ==="
echo "Your application should now be running at http://your_server_ip"
echo ""
echo "To check application logs:"
echo "  sudo journalctl -u urenregistratie"
echo ""
echo "To restart the application:"
echo "  sudo systemctl restart urenregistratie"
echo ""
echo "To check Nginx logs:"
echo "  sudo tail -f /var/log/nginx/error.log"
echo "  sudo tail -f /var/log/nginx/access.log" 