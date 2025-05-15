from app import app, db
from models import User, Role, RoleEnum
import getpass

def create_admin_user(username, email, password):
    """Create a new admin user"""
    with app.app_context():
        # Check if the admin role exists
        admin_role = Role.query.filter_by(name=RoleEnum.ADMIN).first()
        if not admin_role:
            print("Admin role not found. Please run reset_db.py first to set up roles.")
            return False
            
        # Check if username already exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            print(f"User with username '{username}' already exists.")
            return False
            
        # Check if email already exists
        existing_email = User.query.filter_by(email=email).first()
        if existing_email:
            print(f"User with email '{email}' already exists.")
            return False
        
        # Create new admin user
        new_admin = User(
            username=username,
            email=email,
            role_id=admin_role.id,
            is_active=True
        )
        new_admin.set_password(password)
        
        # Add to database
        db.session.add(new_admin)
        db.session.commit()
        
        print(f"Admin user '{username}' created successfully!")
        return True

if __name__ == "__main__":
    print("Create a new admin user for UrenRegistratie")
    print("-----------------------------------------")
    
    username = input("Enter username: ")
    email = input("Enter email: ")
    password = getpass.getpass("Enter password: ")
    confirm_password = getpass.getpass("Confirm password: ")
    
    if password != confirm_password:
        print("Passwords do not match!")
    else:
        create_admin_user(username, email, password)
