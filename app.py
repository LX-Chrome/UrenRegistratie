import os
import logging
import secrets
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from sqlalchemy.orm import DeclarativeBase
from dotenv import load_dotenv  # Load environment variables from .env

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

with app.app_context():
    import models  # noqa: F401
    db.create_all()
