# UrenRegistratie

A time registration system for managing work hours, client assignments, and invoicing.

## Project Structure

```
UrenRegistratie/
├── app/                    # Main application package
│   ├── __init__.py         # Application factory
│   ├── models/             # Database models
│   │   ├── __init__.py
│   │   └── models.py
│   ├── routes/             # Route handlers
│   │   ├── __init__.py
│   │   ├── routes.py       # Main routes
│   │   ├── routes_invoices.py  # Invoice-related routes
│   │   └── routes_reports.py   # Report-related routes
│   └── utils/              # Utility functions
│       ├── __init__.py
│       └── auth_helpers.py # Authentication utilities
├── migrations/             # Database migrations
├── scripts/                # Utility scripts and batch files
│   ├── run.py              # Setup and run script
│   ├── quick_start.py      # Fast startup script
│   ├── direct_start.py     # Ultra-fast startup
│   ├── start.bat           # Windows startup script
│   ├── quick_start.bat     # Windows fast startup
│   └── ...                 # Other utility scripts
├── static/                 # Static files (CSS, JS, images)
├── templates/              # HTML templates
├── instance/               # Instance-specific data (e.g., database)
├── main.py                 # Application entry point
├── requirements.txt        # Dependencies
├── README.md               # This file
└── .env                    # Environment variables (not in repo)
```

A comprehensive web-based time tracking and project management application built with Flask. This application allows users to track their working hours, manage clients, projects, and employees, and generate detailed reports.

## Detailed Documentation

For comprehensive documentation about the Time Registrator application, please refer to the files in the `/docs` directory:

- **[Setup Guide](docs/SETUP.md)** - Detailed instructions for installing and configuring the application
- **[Capabilities Guide](docs/CAPABILITIES.md)** - Comprehensive overview of all features and functionality
- **[API Documentation](docs/API.md)** - Complete reference for the REST API endpoints and integration options
- **[GitHub Setup Guide](docs/GITHUB_SETUP.md)** - Instructions for setting up this repository on GitHub
- **[Test Report & Plan](docs/TEST_REPORT.md)** - Comprehensive test report and plan for the application
- **[Test Plan Template](docs/TEST_PLAN_TEMPLATE.md)** - Template for creating future test plans
- **[Improvement Log](docs/IMPROVEMENT_LOG.md)** - Log of all improvement proposals and their status

## Quick Start

The easiest way to start the application is using the provided scripts:

### First Time Setup:

For first-time setup, use these options:

#### For all platforms using Python directly:

```bash
# Clone the repository
git clone https://github.com/LX-Chrome/UrenRegistratie.git
cd UrenRegistratie

# Run the application (handles environment setup automatically)
python scripts/run.py
```

#### For Windows users:

Simply double-click on `scripts/start.bat` in the project folder.

#### For Unix/Linux/macOS users:

```bash
# Make the script executable (first time only)
chmod +x scripts/start.sh

# Run the application
./scripts/start.sh
```

### Fast Startup (After First Setup):

For faster startup after you've already set up the environment:

#### For all platforms using Python directly:

```bash
python scripts/quick_start.py
```

#### For Windows users:

Double-click on `scripts/quick_start.bat` in the project folder.

#### For Unix/Linux/macOS users:

```bash
chmod +x scripts/quick_start.sh  # First time only
./scripts/quick_start.sh
```

These quick start options skip environment checks and dependency installation, making startup much faster.

### Ultra-Fast Startup (For Experienced Users):

For the fastest possible startup with NO checks (use only after confirming everything works):

#### For all platforms using Python directly:

```bash
python scripts/direct_start.py
```

#### For Windows users:

Double-click on `scripts/direct_start.bat` in the project folder.

#### For Unix/Linux/macOS users:

```bash
chmod +x scripts/direct_start.sh  # First time only
./scripts/direct_start.sh
```

Warning: The ultra-fast options skip ALL checks and will fail if dependencies are missing.

### For VS Code users:

The repository includes pre-configured VS Code settings for easy development and execution:

1. Open the project folder in VS Code
2. Press F5 or click the Run and Debug icon in the sidebar
3. Select one of the following:
   - "Python: Setup & Run" - First time setup with environment checks
   - "Python: Time Registrator" - Direct execution if already set up
   - "Python: Quick Start" - Fast startup (after first setup)

### For PyCharm users:

The repository includes pre-configured PyCharm run configurations:

1. Open the project folder in PyCharm
2. The run configurations should be automatically loaded
3. Click the Run button and select one of the following:
   - "Setup and Run" - First time setup with environment checks
   - "Time Registrator" - Direct execution if already set up
   - "Quick Start" - Fast startup (after first setup)

These scripts will:

1. Create a virtual environment if needed
2. Install all dependencies
3. Create a default .env file if missing
4. Start the application

### Troubleshooting

If you encounter errors about missing packages such as `xhtml2pdf`, `reportlab`, or other dependencies, you can fix them using:

#### For Windows users:

```bash
# Simply run the dependency fixer batch file
fix_dependencies.bat
```

#### For all platforms using Python directly:

```bash
python fix_dependencies.py
```

These scripts will check for and install any missing dependencies required by the application.

### Windows Store Python Users:

If you're using Python from the Windows Store (check if Python is installed in the WindowsApps folder), you might encounter issues with virtual environments. Use these special scripts instead:

```bash
# For first-time setup and running
windows_setup.bat

# For subsequent startups
windows_direct_start.bat
```

These scripts bypass virtual environment creation and work with the restrictions of Windows Store Python.

## Features

### User Management

- User registration and authentication
- User profile management
- Role-based access control

### Time Tracking

- Log working hours with project association
- Real-time check-ins and status updates (working, break, done)
- Daily/weekly/monthly time summaries
- Project-based time tracking

### Client Management

- Add and manage clients/customers
- Store detailed client information
- Track client-specific projects
- Client relationship history

### Project Management

- Create and manage projects/assignments
- Link projects to specific clients
- Track project status and deadlines
- Store project requirements and descriptions

### Employee Management

- Maintain employee records
- Track employee skills and office locations
- Associate employees with specific projects
- Monitor employee workload

### Reporting and Analytics

- Generate comprehensive reports (time, project, client, employee)
- Export data in multiple formats (PDF, Excel, CSV)
- Custom date range filtering
- Data visualization dashboards

### Data Import/Export

- Batch import time entries
- Export filtered data sets
- Integration-ready API endpoints

## Tech Stack

- **Backend**: Python 3.11+ with Flask web framework
- **Database**: SQLAlchemy ORM with SQLite/PostgreSQL
- **Frontend**: Bootstrap 5, HTML5, CSS3, JavaScript
- **Authentication**: Flask-Login
- **Data Processing**: pandas
- **Export Functionality**: pdfkit, XlsxWriter, openpyxl
- **Security**: Werkzeug security for password hashing
- **Environment Configuration**: python-dotenv

## Quick Installation

For a quick installation, follow these steps:

```bash
# Clone the repository
git clone https://github.com/LX-Chrome/UrenRegistratie.git
cd time-registrator

# Set up virtual environment
python -m venv venv
venv\Scripts\activate  # On Windows
source venv/bin/activate  # On macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Set up environment variables (create .env file)
# Start the application
flask run
```

For detailed setup instructions, see the [Setup Guide](docs/SETUP.md).

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Deployment

### Ubuntu Linux Deployment

For deploying on an Ubuntu server (16.04 or newer), you can use the included deployment script:

```bash
# Make the script executable
chmod +x deploy_ubuntu.sh

# Run the deployment script (with sudo privileges)
sudo ./deploy_ubuntu.sh
```

The deployment script will:

1. Install required system dependencies
2. Create a dedicated system user for the application
3. Set up a Python virtual environment
4. Install Python dependencies
5. Create a systemd service for automatic startup
6. Optionally configure nginx as a reverse proxy

Additional options:

```bash
# Deploy with nginx as a reverse proxy
sudo ./deploy_ubuntu.sh --nginx

# Use a custom port
sudo ./deploy_ubuntu.sh --port 8080

# Specify custom installation path
sudo ./deploy_ubuntu.sh --path /var/www/urenregistratie

# Show all options
./deploy_ubuntu.sh --help
```

After deployment, the application will be running as a systemd service and will automatically start on system boot.
