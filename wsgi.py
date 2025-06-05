from app import app
import routes  # noqa: F401
import routes_invoices  # noqa: F401
import routes_reports  # noqa: F401
import os
import sys

# Configure path for imports 
current_dir = os.path.dirname(os.path.abspath(__file__)) 
if current_dir not in sys.path: 
    sys.path.append(current_dir)

# Ensure database directory exists
os.makedirs('instance', exist_ok=True)

if __name__ == "__main__":
    # For local development only, not used by Gunicorn
    app.run(host='0.0.0.0', debug=True) 