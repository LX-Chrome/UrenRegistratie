# Time Registrator - Detailed Setup Guide

This document provides comprehensive instructions for setting up, configuring, and deploying the Time Registrator application.

## Table of Contents
- [Development Environment Setup](#development-environment-setup)
- [Database Configuration Options](#database-configuration-options)
- [Advanced Configuration](#advanced-configuration)
- [Production Deployment](#production-deployment)
- [Security Considerations](#security-considerations)
- [Upgrading and Maintenance](#upgrading-and-maintenance)
- [Troubleshooting](#troubleshooting)

## Development Environment Setup

### Prerequisites
- Python 3.11+ 
- Pip package manager
- Git
- (Optional) PostgreSQL or MySQL for production deployments
- (Optional) wkhtmltopdf for PDF generation

### Detailed Installation Steps

#### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/time-registrator.git
cd time-registrator
```

#### 2. Set Up Virtual Environment
It's recommended to use a virtual environment to isolate dependencies:

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows
venv\Scripts\activate
# On macOS/Linux
source venv/bin/activate
```

#### 3. Install Dependencies
Install all required Python packages:

```bash
pip install -r requirements.txt
```

For PDF generation with pdfkit, you'll need to install wkhtmltopdf:
- **Windows**: Download from https://wkhtmltopdf.org/downloads.html
- **macOS**: `brew install wkhtmltopdf`
- **Linux**: `sudo apt-get install wkhtmltopdf` or equivalent

#### 4. Environment Configuration
Create a `.env` file in the root directory with the following variables:

```
# Database configuration
DATABASE_URL=sqlite:///database.db

# Security
SESSION_SECRET=your_secure_random_string
API_KEY=your_api_key_for_external_integrations

# Optional: Email configuration for notifications
MAIL_SERVER=smtp.example.com
MAIL_PORT=587
MAIL_USERNAME=your_email@example.com
MAIL_PASSWORD=your_email_password
MAIL_USE_TLS=True
MAIL_DEFAULT_SENDER=your_email@example.com

# Optional: Application configuration
DEBUG=True  # Set to False in production
TIMEZONE=UTC  # Your preferred timezone
```

#### 5. Initialize the Database
The database will be automatically created when you first start the application:

```bash
flask run
```

#### 6. Create an Admin User
Create an administrator account with:

```bash
flask create-admin --username admin --email admin@example.com --password securepassword
```

## Database Configuration Options

### SQLite (Default - Development)
The simplest configuration using SQLite, suitable for development:
```
DATABASE_URL=sqlite:///database.db
```

### PostgreSQL (Recommended for Production)
For production environments, PostgreSQL provides better performance and reliability:

1. Install PostgreSQL and create a database:
```bash
# Example on Ubuntu/Debian
sudo apt install postgresql postgresql-contrib
sudo -u postgres psql
CREATE DATABASE timeregistrator;
CREATE USER timeapp WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE timeregistrator TO timeapp;
```

2. Update your `.env` file:
```
DATABASE_URL=postgresql://timeapp:secure_password@localhost/timeregistrator
```

### MySQL
If you prefer MySQL:

1. Install MySQL and create a database:
```bash
# Example on Ubuntu/Debian
sudo apt install mysql-server
sudo mysql
CREATE DATABASE timeregistrator;
CREATE USER 'timeapp'@'localhost' IDENTIFIED BY 'secure_password';
GRANT ALL PRIVILEGES ON timeregistrator.* TO 'timeapp'@'localhost';
FLUSH PRIVILEGES;
```

2. Update your `.env` file:
```
DATABASE_URL=mysql://timeapp:secure_password@localhost/timeregistrator
```

## Advanced Configuration

### Custom Authentication Integration
Time Registrator can be integrated with external authentication systems:

1. Edit `app.py` to add your authentication provider
2. Modify the login routes in `routes.py`
3. Update environment variables with any required authentication credentials

### Email Notifications
Configure the application to send email notifications:

1. Set up email environment variables in your `.env` file
2. Test email functionality with:
```bash
flask test-email --recipient test@example.com
```

### Application Logging
Configure custom logging for better debugging and monitoring:

1. Create a `logging.conf` file in the root directory
2. Set logging levels and handlers according to your needs
3. Reference this configuration in `app.py`

Example logging configuration:
```python
# In app.py
import logging.config
logging.config.fileConfig('logging.conf')
```

### Custom Export Templates
Customize the PDF and Excel export templates:

1. Navigate to `services/templates/`
2. Modify the HTML templates for PDF exports
3. Update the Excel template generators in `export_service.py`

## Production Deployment

### Using Gunicorn and Nginx

#### 1. Install Gunicorn
```bash
pip install gunicorn
```

#### 2. Create a systemd Service File
Create `/etc/systemd/system/time-registrator.service`:

```
[Unit]
Description=Time Registrator application
After=network.target

[Service]
User=www-data
WorkingDirectory=/path/to/time-registrator
ExecStart=/path/to/time-registrator/venv/bin/gunicorn --workers 3 --bind unix:time-registrator.sock -m 007 app:app
Restart=always

[Install]
WantedBy=multi-user.target
```

#### 3. Configure Nginx
Create `/etc/nginx/sites-available/time-registrator`:

```
server {
    listen 80;
    server_name timeregistrator.yourdomain.com;

    location / {
        include proxy_params;
        proxy_pass http://unix:/path/to/time-registrator/time-registrator.sock;
    }
    
    location /static {
        alias /path/to/time-registrator/static;
    }
}
```

#### 4. Enable and Start Services
```bash
sudo ln -s /etc/nginx/sites-available/time-registrator /etc/nginx/sites-enabled
sudo systemctl start time-registrator
sudo systemctl enable time-registrator
sudo systemctl restart nginx
```

### Docker Deployment
For containerized deployment:

1. Create a `Dockerfile` in the project root:
```Dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV DATABASE_URL=postgres://postgres:postgres@db/timeregistrator
ENV SESSION_SECRET=your_secure_random_string
ENV API_KEY=your_api_key

EXPOSE 5000

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
```

2. Create a `docker-compose.yml` file:
```yaml
version: '3'

services:
  web:
    build: .
    ports:
      - "5000:5000"
    depends_on:
      - db
    environment:
      - DATABASE_URL=postgres://postgres:postgres@db/timeregistrator
      - SESSION_SECRET=your_secure_random_string
      - API_KEY=your_api_key
    volumes:
      - ./:/app

  db:
    image: postgres:13
    environment:
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=postgres
      - POSTGRES_DB=timeregistrator
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

3. Deploy with Docker Compose:
```bash
docker-compose up -d
```

## Security Considerations

### Password Policy
Implement a strong password policy:

1. Edit the user registration and password reset functions in `routes.py`
2. Add password complexity requirements (length, special characters, etc.)
3. Consider implementing password expiration

### API Security
Secure the API endpoints:

1. Use HTTPS for all API communications
2. Rotate API keys regularly
3. Implement rate limiting for API calls

### Data Protection
Protect sensitive information:

1. Ensure all personal data is properly encrypted
2. Implement proper access controls
3. Set up regular database backups
4. Consider data anonymization for exports

## Upgrading and Maintenance

### Database Migrations
When updating the data model:

1. Create a migration script to update the database schema
2. Test migrations in a staging environment before production
3. Back up the database before applying migrations

### Version Upgrades
To upgrade the application:

1. Pull the latest changes from the repository
2. Install any new dependencies
3. Apply database migrations if necessary
4. Restart the application services

## Troubleshooting

### Common Issues and Solutions

#### Database Connection Problems
- **Issue**: Unable to connect to the database
- **Solution**: 
  - Check if the database server is running
  - Verify connection string format in `.env`
  - Ensure network connectivity to the database server
  - Check user permissions

#### PDF Generation Failures
- **Issue**: PDF exports not working
- **Solution**:
  - Verify wkhtmltopdf is installed and in PATH
  - Check if the HTML templates exist and are valid
  - Try running wkhtmltopdf from command line to verify functionality

#### Authentication Issues
- **Issue**: Unable to log in or register
- **Solution**:
  - Check user database entries
  - Verify email configurations if confirmation is required
  - Clear browser cookies and cache
  - Reset user password if necessary

#### Performance Problems
- **Issue**: Slow application response
- **Solution**:
  - Optimize database queries
  - Add database indexes for frequently queried fields
  - Increase server resources
  - Consider caching strategies

### Logging and Debugging
For advanced troubleshooting:

1. Enable DEBUG mode in your `.env` file
2. Check application logs in the console or log files
3. Use database tools to inspect table structures and data

### Getting Support
If you encounter issues not covered in this guide:

1. Check the GitHub repository issues page
2. Search the documentation for similar problems
3. Reach out to the community via the project's discussion forum
4. Consider opening a new issue with detailed information about your problem 