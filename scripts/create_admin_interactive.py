from app import app, db
from models import User, Role, RoleEnum
import getpass
import sys

def create_admin_user(username, email, password):
    """Create a new admin user"""
    with app.app_context():
        # Check if the admin role exists
        admin_role = Role.query.filter_by(name=RoleEnum.ADMIN).first()
        if not admin_role:
            print("Admin role not found. Creating admin role...")
            admin_role = Role(name=RoleEnum.ADMIN, description="System Administrator")
            db.session.add(admin_role)
            db.session.commit()
            print(f"Created admin role with ID: {admin_role.id}")
            
        # Check if username already exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            print(f"User with username '{username}' already exists.")
            choice = input("Do you want to update this user to an admin? (y/n): ")
            if choice.lower() == 'y':
                existing_user.role_id = admin_role.id
                existing_user.set_password(password)
                db.session.commit()
                print(f"Updated user '{username}' to admin role with new password.")
                return True
            else:
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
    print("\nCreate a new admin user for UrenRegistratie")
    print("-----------------------------------------")
    
    # Check if arguments are provided
    if len(sys.argv) == 4:
        # Use command line arguments
        username = sys.argv[1]
        email = sys.argv[2]
        password = sys.argv[3]
        print(f"Using provided username: {username}")
        print(f"Using provided email: {email}")
        print("Using provided password: ***********")
    else:
        # Interactive mode
        username = input("Enter username: ")
        email = input("Enter email: ")
        password = getpass.getpass("Enter password: ")
        confirm_password = getpass.getpass("Confirm password: ")
        
        if password != confirm_password:
            print("Passwords do not match!")
            sys.exit(1)
    
    success = create_admin_user(username, email, password)
    if success:
        print("\nAdmin user creation completed successfully.")
    else:
        print("\nAdmin user creation failed.")
