import os
from app import app, db
from models import TimeEntry, Medewerker, User
from datetime import datetime, timedelta
import time

def test_database_persistence():
    """
    Test if database changes persist after creation, modification, and deletion.
    This script verifies that:
    1. New data is saved properly to the database
    2. Modified data is updated in the database
    3. Deleted data is properly removed from the database
    """
    print("Starting database persistence test...")
    
    with app.app_context():
        # 1. CREATE TEST - Create a test employee
        print("\n=== Testing CREATE persistence ===")
        
        # Create a unique test employee 
        test_email = f"test_{int(time.time())}@persistence.test"
        test_employee = Medewerker(
            voornaam="Test",
            achternaam="Persistence",
            geboortedatum=datetime.now().date(),
            functie="Test Subject",
            werkmail=test_email,
            kantoorruimte="TEST-001"
        )
        
        # Add and commit to database
        db.session.add(test_employee)
        db.session.commit()
        
        # Get the ID of the created record
        employee_id = test_employee.id
        print(f"Created test employee with ID: {employee_id} and email: {test_email}")
        
        # Verify employee was created by fetching from database
        fetched_employee = Medewerker.query.filter_by(werkmail=test_email).first()
        if fetched_employee and fetched_employee.id == employee_id:
            print("✅ CREATE Test: Employee successfully persisted in database")
        else:
            print("❌ CREATE Test: Employee NOT found in database after creation")
            return
            
        # 2. UPDATE TEST - Modify the test employee
        print("\n=== Testing UPDATE persistence ===")
        
        # Change employee data
        new_kantoorruimte = "TEST-002-UPDATED"
        fetched_employee.kantoorruimte = new_kantoorruimte
        db.session.commit()
        print(f"Updated employee {employee_id} kantoorruimte to: {new_kantoorruimte}")
        
        # Fetch again to verify changes were saved
        updated_employee = Medewerker.query.get(employee_id)
        if updated_employee and updated_employee.kantoorruimte == new_kantoorruimte:
            print("✅ UPDATE Test: Employee changes successfully persisted")
        else:
            print("❌ UPDATE Test: Employee changes NOT persisted")
            
        # 3. DELETE TEST - Remove the test employee
        print("\n=== Testing DELETE persistence ===")
        
        # Delete the employee
        db.session.delete(updated_employee)
        db.session.commit()
        print(f"Deleted employee with ID: {employee_id}")
        
        # Verify deletion
        deleted_check = Medewerker.query.get(employee_id)
        if deleted_check is None:
            print("✅ DELETE Test: Employee successfully removed from database")
        else:
            print("❌ DELETE Test: Employee still exists in database after deletion")
            
        print("\nDatabase persistence test completed.")

if __name__ == "__main__":
    test_database_persistence() 