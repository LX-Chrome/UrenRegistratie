import sqlite3
from app import app

def add_opdracht_columns():
    # Connect to the database
    conn = sqlite3.connect('instance/database.db')
    cursor = conn.cursor()
    
    # Check if the time_entry table has the opdracht_id column
    cursor.execute("PRAGMA table_info('time_entry')")
    columns = cursor.fetchall()
    time_entry_has_opdracht_id = any(col[1] == 'opdracht_id' for col in columns)
    
    # Check if the check_in table has the opdracht_id column
    cursor.execute("PRAGMA table_info('check_in')")
    columns = cursor.fetchall()
    check_in_has_opdracht_id = any(col[1] == 'opdracht_id' for col in columns)
    
    # Add opdracht_id column to time_entry table if it doesn't exist
    if not time_entry_has_opdracht_id:
        print("Adding opdracht_id column to time_entry table...")
        try:
            # SQLite ALTER TABLE to add the new column
            cursor.execute('ALTER TABLE time_entry ADD COLUMN opdracht_id INTEGER REFERENCES opdracht(id)')
            print("Successfully added opdracht_id column to time_entry table")
        except Exception as e:
            print(f"Error adding column to time_entry table: {e}")
    else:
        print("time_entry table already has opdracht_id column")
    
    # Add opdracht_id column to check_in table if it doesn't exist
    if not check_in_has_opdracht_id:
        print("Adding opdracht_id column to check_in table...")
        try:
            # SQLite ALTER TABLE to add the new column
            cursor.execute('ALTER TABLE check_in ADD COLUMN opdracht_id INTEGER REFERENCES opdracht(id)')
            print("Successfully added opdracht_id column to check_in table")
        except Exception as e:
            print(f"Error adding column to check_in table: {e}")
    else:
        print("check_in table already has opdracht_id column")
    
    # Commit and close
    conn.commit()
    conn.close()
    print("Database schema update complete!")

# Run the function with app context
with app.app_context():
    add_opdracht_columns() 