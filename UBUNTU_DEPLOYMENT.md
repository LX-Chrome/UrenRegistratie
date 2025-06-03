# Ubuntu Deployment Guide for UrenRegistratie

This directory contains several scripts to help you deploy, manage, and monitor the UrenRegistratie application on an Ubuntu server.

## Available Scripts

### 1. `ubuntu_production_setup.sh`

Full production setup script that configures your Ubuntu server with all necessary components:

- Python, Nginx, and other dependencies
- Virtual environment setup
- Gunicorn as WSGI server
- Systemd service for automatic startup
- Nginx as reverse proxy

**Usage:**

```bash
chmod +x ubuntu_production_setup.sh
./ubuntu_production_setup.sh
```

### 2. `deploy_production.sh`

Quick deployment script for updates to an already configured server:

- Updates code from git repository
- Installs/updates dependencies
- Backs up the database
- Restarts services

**Usage:**

```bash
chmod +x deploy_production.sh
./deploy_production.sh
```

### 3. `db_manage.sh`

Database management utility for backup and restore operations:

**Usage:**

```bash
chmod +x db_manage.sh
./db_manage.sh [command]
```

**Commands:**

- `backup` - Create a new database backup
- `restore [file]` - Restore from backup (uses most recent if no file specified)
- `list` - List available backups
- `clean [days]` - Remove backups older than specified days (default: 30)
- `info` - Show database information

### 4. `monitor_logs.sh`

Utility to monitor different log sources:

**Usage:**

```bash
chmod +x monitor_logs.sh
./monitor_logs.sh [option]
```

**Options:**

- `app` - Monitor application logs (Gunicorn/systemd)
- `nginx` - Monitor Nginx access and error logs
- `all` - Monitor all logs (application + Nginx)
- `errors` - Monitor only error logs
- `clear` - Clear application log files

## Initial Deployment

For a fresh server, follow these steps:

1. Upload all scripts to your server
2. Make them executable:
   ```bash
   chmod +x *.sh
   ```
3. Run the full setup script:
   ```bash
   ./ubuntu_production_setup.sh
   ```
4. Check if everything is working:
   ```bash
   ./monitor_logs.sh all
   ```

## Updating the Application

When you need to update the application:

1. Run the deployment script:
   ```bash
   ./deploy_production.sh
   ```
2. Monitor logs for any errors:
   ```bash
   ./monitor_logs.sh errors
   ```

## Database Management

Regular database backups:

```bash
# Create a backup
./db_manage.sh backup

# List all backups
./db_manage.sh list

# Clean up old backups (older than 30 days)
./db_manage.sh clean 30
```

## Troubleshooting

If you encounter issues:

1. Check application logs:

   ```bash
   ./monitor_logs.sh app
   ```

2. Check Nginx logs:

   ```bash
   ./monitor_logs.sh nginx
   ```

3. Ensure all services are running:

   ```bash
   sudo systemctl status urenregistratie
   sudo systemctl status nginx
   ```

4. Restart services if needed:
   ```bash
   sudo systemctl restart urenregistratie
   sudo systemctl restart nginx
   ```

## Security Recommendations

1. Set up a firewall using UFW:

   ```bash
   sudo apt-get install ufw
   sudo ufw allow OpenSSH
   sudo ufw allow 'Nginx Full'
   sudo ufw enable
   ```

2. Configure SSL with Let's Encrypt:

   ```bash
   sudo apt-get install certbot python3-certbot-nginx
   sudo certbot --nginx -d yourdomain.com
   ```

3. Set up fail2ban to protect against brute force attacks:
   ```bash
   sudo apt-get install fail2ban
   ```

## Maintenance Tips

1. Regularly update your system:

   ```bash
   sudo apt-get update && sudo apt-get upgrade
   ```

2. Monitor disk space:

   ```bash
   df -h
   ```

3. Set up regular database backups with a cron job:

   ```bash
   crontab -e
   # Add this line to create daily backups at 2 AM:
   0 2 * * * cd /opt/urenregistratie && ./db_manage.sh backup
   ```

4. Clean up old logs periodically:
   ```bash
   ./monitor_logs.sh clear
   ```
