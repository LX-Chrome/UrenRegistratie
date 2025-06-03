from app import app, db
from models import User, Role, RoleEnum

# Admin user credentials
ADMIN_USERNAME = "admin"
ADMIN_EMAIL = "admin@example.com"
ADMIN_PASSWORD = "Admin123!"  # You should change this password after login

with app.app_context():
    # Check if the admin role exists
    admin_role = Role.query.filter_by(name=RoleEnum.ADMIN).first()
    if not admin_role:
        print("Admin role not found. Running setup...")
        admin_role = Role(name=RoleEnum.ADMIN, description="System Administrator")
        db.session.add(admin_role)
        db.session.commit()
        print(f"Created admin role with ID: {admin_role.id}")
    
    # Check if admin user already exists
    existing_user = User.query.filter_by(username=ADMIN_USERNAME).first()
    if existing_user:
        print(f"User '{ADMIN_USERNAME}' already exists. Setting admin role and updating password...")
        existing_user.role_id = admin_role.id
        existing_user.set_password(ADMIN_PASSWORD)
        db.session.commit()
        print(f"Updated user '{ADMIN_USERNAME}' to admin role with new password.")
    else:
        # Create new admin user
        new_admin = User(
            username=ADMIN_USERNAME,
            email=ADMIN_EMAIL,
            role_id=admin_role.id,
            is_active=True
        )
        new_admin.set_password(ADMIN_PASSWORD)
        
        # Add to database
        db.session.add(new_admin)
        db.session.commit()
        
        print(f"Admin user '{ADMIN_USERNAME}' created successfully with password: '{ADMIN_PASSWORD}'")
        print("Please change this password after logging in!")

print("Done!")
