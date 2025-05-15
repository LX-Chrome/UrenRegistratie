import os
from app import app, db
from models import Role, User, CheckIn, Klant, Medewerker, Opdracht, Werkzaamheid, Factuur, TimeEntry

def clear_all_test_data():
    """
    Remove all test data from the database while preserving the database structure
    and the basic roles needed for the application to function.
    """
    with app.app_context():
        # Delete data in reverse order of dependency to avoid foreign key constraint errors
        print("Deleting all time entries...")
        TimeEntry.query.delete()
        
        print("Deleting all invoices...")
        Factuur.query.delete()
        
        print("Deleting all work activities...")
        Werkzaamheid.query.delete()
        
        print("Deleting all assignments/projects...")
        Opdracht.query.delete()
        
        print("Deleting all clients...")
        Klant.query.delete()
        
        print("Deleting all check-ins...")
        CheckIn.query.delete()
        
        print("Deleting all employees...")
        Medewerker.query.delete()
        
        print("Deleting all users except admin if it exists...")
        # Optionally keep admin or some system users
        # If you want to keep the admin user, uncomment the line below and comment the User.query.delete() line
        # User.query.filter(User.username != 'admin').delete()
        User.query.delete()
        
        # Roles will be preserved - they are system settings
        
        # Commit the changes
        db.session.commit()
        print("All test data has been cleared from the database!")
        print("Note: Database structure and roles have been preserved.")

if __name__ == "__main__":
    clear_all_test_data()
