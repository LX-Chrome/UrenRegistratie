import sys
from app import app, db
from models import User, Role, RoleEnum

def update_user_role(email, role_name):
    # Validate role name
    valid_roles = [role.value for role in RoleEnum]
    if role_name.lower() not in [r.lower() for r in valid_roles]:
        print(f"Error: '{role_name}' is not a valid role. Valid roles are: {', '.join(valid_roles)}")
        return False
    
    # Get standardized role name (with correct casing)
    role_name = next(r for r in valid_roles if r.lower() == role_name.lower())
    
    # Find the user by email
    with app.app_context():
        user = User.query.filter_by(email=email).first()
        
        if not user:
            print(f"Error: No user found with email '{email}'")
            return False
        
        # Get the role by name
        role = Role.query.filter_by(name=role_name).first()
        
        if not role:
            print(f"Error: Role '{role_name}' not found in database. Creating it now...")
            # Create the role if it doesn't exist
            role = Role(name=role_name, description=f"{role_name.capitalize()} role")
            db.session.add(role)
            db.session.commit()
            role = Role.query.filter_by(name=role_name).first()
        
        # Update user's role
        old_role_id = user.role_id
        old_role = Role.query.filter_by(id=old_role_id).first() if old_role_id else None
        old_role_name = old_role.name if old_role else "None"
        
        user.role_id = role.id
        db.session.commit()
        
        print(f"User '{user.username}' ({email}) role updated successfully:")
        print(f"  - Old role: {old_role_name}")
        print(f"  - New role: {role_name}")
        print(f"  - Role ID: {role.id}")
        
        # Verify the update was successful
        updated_user = User.query.filter_by(email=email).first()
        if updated_user.role_id == role.id:
            print("Database update confirmed.")
        else:
            print("Warning: Update may not have been saved correctly.")
        
        return True

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python update_user_role.py <email> <role>")
        print("Available roles: admin, verkoop, afdelingshoofd, medewerker")
        sys.exit(1)
    
    email = sys.argv[1]
    role = sys.argv[2]
    
    success = update_user_role(email, role)
    if not success:
        sys.exit(1)
