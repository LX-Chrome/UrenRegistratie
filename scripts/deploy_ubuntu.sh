#!/bin/bash
#
# UrenRegistratie - Ubuntu Deployment Script
#
# This script automates the deployment of the UrenRegistratie application
# on Ubuntu Linux systems, setting up a production environment with systemd
# service and optional nginx configuration.
#

set -e  # Exit on any error

# Text formatting
BOLD="\e[1m"
GREEN="\e[32m"
YELLOW="\e[33m"
RED="\e[31m"
RESET="\e[0m"

# Default configuration
APP_USER="urenregistratie"
APP_GROUP="urenregistratie"
APP_PATH="/opt/urenregistratie"
VENV_PATH="/opt/urenregistratie/venv"
USE_NGINX=false
PYTHON_CMD="python3"
PORT=5000
HOST="0.0.0.0"
DEBUG=false

# Parse command line options
while [[ $# -gt 0 ]]; do
    key="$1"
    case $key in
        --nginx)
            USE_NGINX=true
            shift
            ;;
        --port)
            PORT="$2"
            shift 2
            ;;
        --path)
            APP_PATH="$2"
            VENV_PATH="$2/venv"
            shift 2
            ;;
        --user)
            APP_USER="$2"
            shift 2
            ;;
        --debug)
            DEBUG=true
            shift
            ;;
        --help)
            echo -e "${BOLD}UrenRegistratie Ubuntu Deployment Script${RESET}"
            echo "Usage: deploy_ubuntu.sh [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --nginx          Configure nginx as a reverse proxy"
            echo "  --port PORT      Specify the port to run on (default: 5000)"
            echo "  --path PATH      Installation path (default: /opt/urenregistratie)"
            echo "  --user USER      System user to run as (default: urenregistratie)"
            echo "  --debug          Enable debug mode"
            echo "  --help           Show this help message"
            exit 0
            ;;
        *)
            echo -e "${RED}Unknown option: $key${RESET}" >&2
            echo "Use --help for usage information."
            exit 1
            ;;
    esac
done

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check for root privileges
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}Error: This script must be run as root${RESET}"
    echo "Try: sudo $0 $*"
    exit 1
fi

echo -e "${BOLD}Starting UrenRegistratie deployment on Ubuntu${RESET}"
echo -e "Installation path: ${GREEN}$APP_PATH${RESET}"
echo -e "Service user: ${GREEN}$APP_USER${RESET}"
echo -e "Port: ${GREEN}$PORT${RESET}"
echo -e "Using nginx: ${GREEN}$USE_NGINX${RESET}"
echo -e "Debug mode: ${GREEN}$DEBUG${RESET}"
echo ""
echo -e "${YELLOW}Press Enter to continue or Ctrl+C to abort...${RESET}"
read -r

# Step 1: Update system and install dependencies
echo -e "\n${BOLD}Step 1: Installing system dependencies${RESET}"
apt-get update
apt-get install -y python3 python3-pip python3-venv python3-dev build-essential \
    libssl-dev libffi-dev sqlite3 git curl supervisor

# Step 2: Create user and group if they don't exist
echo -e "\n${BOLD}Step 2: Setting up system user${RESET}"
if ! id "$APP_USER" &>/dev/null; then
    groupadd "$APP_GROUP"
    useradd -m -g "$APP_GROUP" -s /bin/bash "$APP_USER"
    echo -e "${GREEN}User $APP_USER created${RESET}"
else
    echo -e "${YELLOW}User $APP_USER already exists, using existing user${RESET}"
fi

# Step 3: Create application directory
echo -e "\n${BOLD}Step 3: Creating application directory${RESET}"
mkdir -p "$APP_PATH"
cd "$(dirname "$0")/.."  # Navigate to project root
cp -R . "$APP_PATH"
chown -R "$APP_USER:$APP_GROUP" "$APP_PATH"

# Step 4: Create Python virtual environment
echo -e "\n${BOLD}Step 4: Setting up virtual environment${RESET}"
su - "$APP_USER" -c "cd $APP_PATH && $PYTHON_CMD -m venv $VENV_PATH"

# Step 5: Install dependencies
echo -e "\n${BOLD}Step 5: Installing Python dependencies${RESET}"
su - "$APP_USER" -c "cd $APP_PATH && $VENV_PATH/bin/pip install --upgrade pip"
su - "$APP_USER" -c "cd $APP_PATH && $VENV_PATH/bin/pip install -r requirements.txt"

# Optional: Install additional production dependencies
su - "$APP_USER" -c "cd $APP_PATH && $VENV_PATH/bin/pip install gunicorn psycopg2-binary" || true

# Step 6: Create .env file if it doesn't exist
echo -e "\n${BOLD}Step 6: Setting up environment configuration${RESET}"
if [ ! -f "$APP_PATH/.env" ]; then
    echo -e "${YELLOW}Creating default .env file${RESET}"
    cat > "$APP_PATH/.env" << EOF
# Database configuration
DATABASE_URL=sqlite:///$APP_PATH/instance/database.db

# Security
SESSION_SECRET=$(openssl rand -hex 24)
API_KEY=$(openssl rand -hex 24)

# Application configuration
DEBUG=$DEBUG
PORT=$PORT
HOST=$HOST
EOF
    chown "$APP_USER:$APP_GROUP" "$APP_PATH/.env"
    chmod 600 "$APP_PATH/.env"
else
    echo -e "${YELLOW}.env file already exists, keeping existing configuration${RESET}"
fi

# Step 7: Create systemd service
echo -e "\n${BOLD}Step 7: Creating systemd service${RESET}"
cat > /etc/systemd/system/urenregistratie.service << EOF
[Unit]
Description=UrenRegistratie Time Tracking Application
After=network.target

[Service]
User=$APP_USER
Group=$APP_GROUP
WorkingDirectory=$APP_PATH
Environment="PATH=$VENV_PATH/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
ExecStart=$VENV_PATH/bin/gunicorn --workers 3 --bind $HOST:$PORT -m 007 'main:app'
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable urenregistratie.service
systemctl start urenregistratie.service

# Step 8: Configure nginx (optional)
if [ "$USE_NGINX" = true ]; then
    echo -e "\n${BOLD}Step 8: Configuring nginx${RESET}"
    
    # Install nginx if not installed
    if ! command_exists nginx; then
        apt-get install -y nginx
    fi
    
    # Create nginx config
    cat > /etc/nginx/sites-available/urenregistratie << EOF
server {
    listen 80;
    server_name _;
    
    location / {
        proxy_pass http://$HOST:$PORT;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
    
    location /static {
        alias $APP_PATH/static;
        expires 30d;
    }
    
    client_max_body_size 5M;
}
EOF
    
    # Enable site
    ln -sf /etc/nginx/sites-available/urenregistratie /etc/nginx/sites-enabled/
    
    # Test and restart nginx
    nginx -t && systemctl restart nginx
    
    # Configure firewall (if exists)
    if command_exists ufw; then
        ufw allow 'Nginx Full'
    fi
fi

# Step 9: Create admin user (optional)
echo -e "\n${BOLD}Step 9: Do you want to create an admin user? (y/n)${RESET}"
read -r create_admin
if [[ $create_admin =~ ^[Yy] ]]; then
    echo -e "${YELLOW}Running admin user creation script...${RESET}"
    su - "$APP_USER" -c "cd $APP_PATH && $VENV_PATH/bin/python scripts/create_admin_interactive.py"
fi

# Final status check
echo -e "\n${BOLD}Checking service status${RESET}"
systemctl status urenregistratie.service

echo -e "\n${BOLD}${GREEN}Deployment complete!${RESET}"
echo -e "UrenRegistratie has been deployed and is running as a service."

if [ "$USE_NGINX" = true ]; then
    echo -e "Access your application at http://your-server-ip/"
else
    echo -e "Access your application at http://your-server-ip:$PORT/"
fi

echo -e "\nUseful commands:"
echo -e "  ${YELLOW}sudo systemctl status urenregistratie${RESET} - Check service status"
echo -e "  ${YELLOW}sudo systemctl restart urenregistratie${RESET} - Restart the service"
echo -e "  ${YELLOW}sudo journalctl -u urenregistratie${RESET} - View service logs"
echo -e "  ${YELLOW}cd $APP_PATH && $VENV_PATH/bin/python scripts/create_admin_interactive.py${RESET} - Create admin user" 