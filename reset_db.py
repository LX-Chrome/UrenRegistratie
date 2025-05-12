import os
import sqlite3
from app import app, db
from models import Role, RoleEnum

# Remove the existing database
db_path = os.path.join('instance', 'database.db')
if os.path.exists(db_path):
    os.remove(db_path)
    print(f"Removed existing database at {db_path}")

# Create all tables fresh
with app.app_context():
    db.create_all()
    print("Created new database tables")
    
    # Add the default roles
    admin_role = Role(name=RoleEnum.ADMIN, description="System Administrator")
    dept_head_role = Role(name=RoleEnum.AFDELINGSHOOFD, description="Department Head")
    sales_role = Role(name=RoleEnum.VERKOOP, description="Sales Staff")
    employee_role = Role(name=RoleEnum.MEDEWERKER, description="Regular Employee")
    
    db.session.add_all([admin_role, dept_head_role, sales_role, employee_role])
    db.session.commit()
    print("Added default roles")
    
print("Database reset complete!")
