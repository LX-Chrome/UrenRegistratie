import os
import logging
import secrets
from flask import Flask, abort
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user
from sqlalchemy.orm import DeclarativeBase
from dotenv import load_dotenv  # Load environment variables from .env
from functools import wraps

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.DEBUG)

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)
app = Flask(__name__)

# Configuration
app.secret_key = os.environ.get("SESSION_SECRET", secrets.token_urlsafe(32))  # Generate a default secret key if missing
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///database.db")  # Default to SQLite
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
app.config["API_KEY"] = os.environ.get("API_KEY", secrets.token_urlsafe(32))  # Generate if missing

# Debug prints
print("Database URI:", app.config["SQLALCHEMY_DATABASE_URI"])
print("API Key:", app.config["API_KEY"])

# Initialize extensions
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Role-based access control decorators
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin():
            abort(403)  # Forbidden
        return f(*args, **kwargs)
    return decorated_function

def department_head_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_department_head():
            abort(403)  # Forbidden
        return f(*args, **kwargs)
    return decorated_function

def sales_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_sales():
            abort(403)  # Forbidden
        return f(*args, **kwargs)
    return decorated_function

def view_all_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.can_view_all():
            abort(403)  # Forbidden
        return f(*args, **kwargs)
    return decorated_function

def invoice_creation_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.can_create_invoices():
            abort(403)  # Forbidden
        return f(*args, **kwargs)
    return decorated_function

with app.app_context():
    import models  # noqa: F401
    from models import RoleEnum
    db.create_all()
    
    # Make RoleEnum available to all templates
    @app.context_processor
    def inject_role_enum():
        return {'RoleEnum': RoleEnum}
