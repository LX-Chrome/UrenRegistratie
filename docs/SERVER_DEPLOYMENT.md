# Windows Server Deployment Guide

This guide provides detailed instructions for deploying Time Registrator on Windows Server 2016 as a production service accessible across your network.

## Prerequisites

- Windows Server 2016 (or newer)
- Python 3.8+ installed
- Administrator access on the server
- NSSM (Non-Sucking Service Manager) for running as a Windows Service

## Deployment Options

There are two main deployment options:

1. **Quick deployment with server_deploy.bat** (Recommended)
2. **Manual deployment** (For advanced users)

## Option 1: Quick Deployment

### Step 1: Prepare the Environment

1. Copy the entire Time Registrator application directory to your Windows Server
2. Open Command Prompt as Administrator
3. Navigate to the application directory

### Step 2: Run the Deployment Script

1. Run `server_deploy.bat` as Administrator:

   ```
   server_deploy.bat
   ```

2. This script will:
   - Create a production virtual environment
   - Install all required dependencies including Waitress (production WSGI server)
   - Create a production server script
   - Generate necessary service installation files

### Step 3: Test the Production Server

1. Run `start_production.bat` to test the production server:

   ```
   start_production.bat
   ```

2. Access the application at:

   - http://localhost:8080 (from the server)
   - http://YOUR-SERVER-IP:8080 (from other computers)

3. Verify that the application works as expected

### Step 4: Install as a Windows Service

1. Download NSSM from [nssm.cc/download](http://nssm.cc/download)
2. Extract and place `nssm.exe` in the application directory
3. Run `install_service.bat` as Administrator:

   ```
   install_service.bat
   ```

4. The service will be installed as "Time Registrator"
5. Start the service using:
   - Services Management Console (services.msc)
   - Or run: `nssm start TimeRegistrator`

### Step 5: Configure Firewall

1. Open port 8080 in Windows Firewall by running as Administrator:
   ```
   netsh advfirewall firewall add rule name="Time Registrator" dir=in action=allow protocol=TCP localport=8080
   ```

## Option 2: Manual Deployment

### Step 1: Create a Production Environment

1. Create a virtual environment:

   ```
   python -m venv prod_env
   ```

2. Activate the environment:

   ```
   prod_env\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install --upgrade pip
   pip install -r requirements.txt
   pip install waitress
   ```

### Step 2: Create a Production Server Script

Create a file named `production_server.py` with the following content:

```python
from waitress import serve
import os
from app import app
import routes  # noqa: F401
import routes_invoices  # noqa: F401
import routes_reports  # noqa: F401

if __name__ == "__main__":
    # Get configuration from environment or use defaults
    host = os.environ.get('HOST', '0.0.0.0')
    port = int(os.environ.get('PORT', 8080))
    threads = int(os.environ.get('THREADS', 4))

    # Print server information
    print(f"Starting production server on {host}:{port}")
    print("Access the application at:")
    print(f"http://{host}:{port} (from this server)")

    # Try to get server IP for network access
    import socket
    try:
        hostname = socket.gethostname()
        ip = socket.gethostbyname(hostname)
        print(f"http://{ip}:{port} (from your network)")
    except:
        pass

    # Start production server with waitress
    serve(app, host=host, port=port, threads=threads)
```

### Step 3: Create a Production .env File

Create or update the `.env` file with production settings:

```
# Database configuration
DATABASE_URL=sqlite:///database.db

# Security (use different random values)
SESSION_SECRET=your_secure_random_key_here
API_KEY=your_secure_api_key_here

# Production configuration
DEBUG=False
HOST=0.0.0.0
PORT=8080
THREADS=4
```

### Step 4: Create a Service Wrapper Batch File

Create a file named `run_production.bat` with the following content:

```batch
@echo off
cd /d "%~dp0"
call prod_env\Scripts\activate.bat
prod_env\Scripts\python production_server.py
```

### Step 5: Install as a Windows Service using NSSM

1. Download and extract NSSM
2. Open Command Prompt as Administrator
3. Navigate to the NSSM directory
4. Run the following commands:

```
nssm install TimeRegistrator "[FULL_PATH_TO_APP]\run_production.bat"
nssm set TimeRegistrator DisplayName "Time Registrator"
nssm set TimeRegistrator Description "Time tracking and project management application"
nssm set TimeRegistrator AppDirectory "[FULL_PATH_TO_APP]"
nssm set TimeRegistrator Start SERVICE_AUTO_START
```

5. Start the service:

```
nssm start TimeRegistrator
```

### Step 6: Configure Firewall

Open port 8080 in Windows Firewall:

```
netsh advfirewall firewall add rule name="Time Registrator" dir=in action=allow protocol=TCP localport=8080
```

## Advanced Configuration

### Database Configuration

For a production environment, you might want to use a more robust database:

#### PostgreSQL

1. Install PostgreSQL on your server
2. Create a database and user
3. Update the `.env` file:
   ```
   DATABASE_URL=postgresql://username:password@localhost/database_name
   ```

#### SQLite with Optimized Settings

For better performance with SQLite:

```
DATABASE_URL=sqlite:///database.db?cache=shared&journal_mode=wal&synchronous=normal
```

### Reverse Proxy with IIS (Optional)

For better security and performance, you can use IIS as a reverse proxy:

1. Install URL Rewrite and Application Request Routing modules for IIS
2. Create a new IIS website
3. Configure URL Rewrite rules to forward requests to your application running on port 8080

## Troubleshooting

### Service Won't Start

1. Check the application logs
2. Run the application manually to see error messages:
   ```
   prod_env\Scripts\activate
   python production_server.py
   ```

### Application Not Accessible from Network

1. Verify the server is listening on all interfaces:

   ```
   netstat -an | find ":8080"
   ```

   Should show `0.0.0.0:8080`

2. Check Windows Firewall settings
3. Test local access first (http://localhost:8080)

### Database Issues

1. Check file permissions on the database.db file
2. Try creating a new database by renaming the old one

## Maintenance

### Updating the Application

1. Stop the service:

   ```
   nssm stop TimeRegistrator
   ```

2. Update the application files
3. Start the service:
   ```
   nssm start TimeRegistrator
   ```

### Backing Up

Regularly back up the following:

1. The database file (database.db)
2. The .env file with your configuration
3. Any customized application files

## Security Considerations

1. Use HTTPS in production (configure in IIS if using as reverse proxy)
2. Keep SESSION_SECRET and API_KEY secure and unique
3. Consider network isolation for the database if using an external database server
4. Regularly update all dependencies:
   ```
   prod_env\Scripts\activate
   pip install --upgrade -r requirements.txt
   ```
