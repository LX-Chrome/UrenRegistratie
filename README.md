# Time Registrator

A comprehensive web-based time tracking and project management application built with Flask. This application allows users to track their working hours, manage clients, projects, and employees, and generate detailed reports.

## Detailed Documentation

For comprehensive documentation about the Time Registrator application, please refer to the files in the `/docs` directory:

- **[Setup Guide](docs/SETUP.md)** - Detailed instructions for installing and configuring the application
- **[Capabilities Guide](docs/CAPABILITIES.md)** - Comprehensive overview of all features and functionality
- **[API Documentation](docs/API.md)** - Complete reference for the REST API endpoints and integration options
- **[GitHub Setup Guide](docs/GITHUB_SETUP.md)** - Instructions for setting up this repository on GitHub

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
