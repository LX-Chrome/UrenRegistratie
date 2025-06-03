from app import app, db
from models import User, Role

with app.app_context():
    print("\nList of users in the database:")
    users = User.query.all()
    for user in users:
        role = Role.query.filter_by(id=user.role_id).first() if user.role_id else None
        role_name = role.name if role else "None"
        print(f"  - ID: {user.id}, Username: {user.username}, Email: {user.email}, Role: {role_name}")
