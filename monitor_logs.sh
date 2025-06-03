#!/bin/bash

# Log Monitoring Script for UrenRegistratie
# ========================================

# Function to display usage
show_usage() {
  echo "UrenRegistratie Log Monitoring Script"
  echo ""
  echo "Usage: $0 [option]"
  echo ""
  echo "Options:"
  echo "  app       Monitor application logs (Gunicorn/systemd)"
  echo "  nginx     Monitor Nginx access and error logs"
  echo "  all       Monitor all logs (application + Nginx)"
  echo "  errors    Monitor only error logs"
  echo "  clear     Clear application log files"
  echo ""
  exit 1
}

# Check if the terminal supports colors
if [ -t 1 ]; then
  RED='\033[0;31m'
  GREEN='\033[0;32m'
  YELLOW='\033[0;33m'
  BLUE='\033[0;34m'
  CYAN='\033[0;36m'
  NC='\033[0m' # No Color
else
  RED=''
  GREEN=''
  YELLOW=''
  BLUE=''
  CYAN=''
  NC=''
fi

# Monitor application logs
monitor_app() {
  echo -e "${CYAN}Monitoring application logs...${NC}"
  echo -e "${YELLOW}Press Ctrl+C to stop${NC}"
  
  # Check if running as a systemd service
  if systemctl list-unit-files | grep -q urenregistratie.service; then
    sudo journalctl -u urenregistratie -f
  else
    # If not using systemd, check for local log files
    LOG_DIR="./logs"
    if [ -d "$LOG_DIR" ]; then
      # Find the newest log file
      LATEST_LOG=$(find "$LOG_DIR" -name "*.log" -type f -printf '%T@ %p\n' | sort -nr | head -1 | cut -d' ' -f2-)
      if [ -n "$LATEST_LOG" ]; then
        tail -f "$LATEST_LOG"
      else
        echo -e "${RED}No log files found in $LOG_DIR${NC}"
        exit 1
      fi
    else
      echo -e "${RED}No log directory found. Application may not be logging to files.${NC}"
      echo -e "${YELLOW}Try using the 'all' option to monitor system logs${NC}"
      exit 1
    fi
  fi
}

# Monitor Nginx logs
monitor_nginx() {
  echo -e "${CYAN}Monitoring Nginx logs...${NC}"
  echo -e "${YELLOW}Press Ctrl+C to stop${NC}"
  
  # Check if Nginx is installed
  if ! command -v nginx &> /dev/null; then
    echo -e "${RED}Nginx does not appear to be installed${NC}"
    exit 1
  fi
  
  # Check if access logs exist
  if [ -f "/var/log/nginx/access.log" ] && [ -f "/var/log/nginx/error.log" ]; then
    # Use multitail if available
    if command -v multitail &> /dev/null; then
      sudo multitail -cS nginx /var/log/nginx/access.log -cS nginx_error /var/log/nginx/error.log
    else
      echo -e "${YELLOW}For better viewing, install multitail: sudo apt-get install multitail${NC}"
      echo -e "${BLUE}=== Nginx Access Log ===${NC}"
      sudo tail -f /var/log/nginx/access.log &
      PID_ACCESS=$!
      echo -e "${RED}=== Nginx Error Log ===${NC}"
      sudo tail -f /var/log/nginx/error.log &
      PID_ERROR=$!
      
      # Wait for Ctrl+C
      trap "kill $PID_ACCESS $PID_ERROR; exit 0" INT
      wait
    fi
  else
    echo -e "${RED}Nginx log files not found at expected locations:${NC}"
    echo -e "  /var/log/nginx/access.log"
    echo -e "  /var/log/nginx/error.log"
    exit 1
  fi
}

# Monitor error logs only
monitor_errors() {
  echo -e "${CYAN}Monitoring error logs only...${NC}"
  echo -e "${YELLOW}Press Ctrl+C to stop${NC}"
  
  # Application errors (systemd)
  if systemctl list-unit-files | grep -q urenregistratie.service; then
    sudo journalctl -u urenregistratie -p err -f &
    PID_APP=$!
  fi
  
  # Nginx errors
  if [ -f "/var/log/nginx/error.log" ]; then
    sudo tail -f /var/log/nginx/error.log &
    PID_NGINX=$!
  fi
  
  # Wait for Ctrl+C
  trap "kill $PID_APP $PID_NGINX 2>/dev/null; exit 0" INT
  wait
}

# Monitor all logs
monitor_all() {
  echo -e "${CYAN}Monitoring all logs...${NC}"
  echo -e "${YELLOW}Press Ctrl+C to stop${NC}"
  
  # If multitail is available, use it for better display
  if command -v multitail &> /dev/null; then
    if systemctl list-unit-files | grep -q urenregistratie.service; then
      sudo multitail -cS systemd -l "journalctl -u urenregistratie -f" \
        -cS nginx /var/log/nginx/access.log \
        -cS nginx_error /var/log/nginx/error.log
    else
      sudo multitail -cS nginx /var/log/nginx/access.log \
        -cS nginx_error /var/log/nginx/error.log
    fi
  else
    # Start multiple tails in background
    echo -e "${YELLOW}For better viewing, install multitail: sudo apt-get install multitail${NC}"
    
    # Application logs
    if systemctl list-unit-files | grep -q urenregistratie.service; then
      echo -e "${GREEN}=== Application Logs (journalctl) ===${NC}"
      sudo journalctl -u urenregistratie -f &
      PID_APP=$!
    fi
    
    # Nginx logs
    if [ -f "/var/log/nginx/access.log" ]; then
      echo -e "${BLUE}=== Nginx Access Log ===${NC}"
      sudo tail -f /var/log/nginx/access.log &
      PID_ACCESS=$!
    fi
    
    if [ -f "/var/log/nginx/error.log" ]; then
      echo -e "${RED}=== Nginx Error Log ===${NC}"
      sudo tail -f /var/log/nginx/error.log &
      PID_ERROR=$!
    fi
    
    # Wait for Ctrl+C
    trap "kill $PID_APP $PID_ACCESS $PID_ERROR 2>/dev/null; exit 0" INT
    wait
  fi
}

# Clear logs
clear_logs() {
  echo -e "${YELLOW}Clearing application logs...${NC}"
  
  # Clear systemd logs
  if systemctl list-unit-files | grep -q urenregistratie.service; then
    echo "Clearing systemd journal logs for urenregistratie service..."
    sudo journalctl --vacuum-time=1d --unit=urenregistratie
  fi
  
  # Clear local log files
  LOG_DIR="./logs"
  if [ -d "$LOG_DIR" ]; then
    echo "Clearing local log files..."
    find "$LOG_DIR" -name "*.log" -type f -exec truncate -s 0 {} \;
  fi
  
  echo -e "${GREEN}Log files cleared.${NC}"
}

# Main script logic
case "$1" in
  app)
    monitor_app
    ;;
  nginx)
    monitor_nginx
    ;;
  errors)
    monitor_errors
    ;;
  all)
    monitor_all
    ;;
  clear)
    clear_logs
    ;;
  *)
    show_usage
    ;;
esac 