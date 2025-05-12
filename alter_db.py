import sqlite3
import os
from app import app
from models import Role, RoleEnum

def add_role_column():
    # Connect to the database
    conn = sqlite3.connect('instance/database.db')
    cursor = conn.cursor()
    
    # Check if the role table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='role'")
    role_table_exists = cursor.fetchone() is not None
    
    if not role_table_exists:
        # Create the role table
        cursor.execute('''
        CREATE TABLE role (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL UNIQUE,
            description TEXT
        )
        ''')
        print("Created role table")
        
        # Insert the default roles
        roles = [
            (1, RoleEnum.MEDEWERKER, "Regular Employee"),
            (2, RoleEnum.VERKOOP, "Sales Staff"),
            (3, RoleEnum.AFDELINGSHOOFD, "Department Head"),
            (4, RoleEnum.ADMIN, "System Administrator")
        ]
        cursor.executemany("INSERT INTO role VALUES (?, ?, ?)", roles)
        print("Added default roles")
    
    # Check if the user table has the role_id column
    cursor.execute("PRAGMA table_info('user')")
    columns = cursor.fetchall()
    has_role_id = any(col[1] == 'role_id' for col in columns)
    
    if not has_role_id:
        # SQLite doesn't support ALTER TABLE ADD COLUMN with foreign key constraints directly
        # So we need to create a new table and copy the data
        
        print("Adding role_id column to user table...")
        
        # Create a temporary table with the new schema
        cursor.execute('''
        CREATE TABLE user_new (
            id INTEGER PRIMARY KEY,
            username TEXT NOT NULL UNIQUE,
            email TEXT NOT NULL UNIQUE,
            password_hash TEXT,
            role_id INTEGER DEFAULT 1,
            is_active INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            medewerker_id INTEGER,
            FOREIGN KEY (role_id) REFERENCES role (id),
            FOREIGN KEY (medewerker_id) REFERENCES medewerker (id)
        )
        ''')
        
        # Copy data from the old table to the new one
        cursor.execute('''
        INSERT INTO user_new (id, username, email, password_hash, is_active, created_at, medewerker_id)
        SELECT id, username, email, password_hash, is_active, created_at, medewerker_id FROM user
        ''')
        
        # Drop the old table
        cursor.execute('DROP TABLE user')
        
        # Rename the new table to the original name
        cursor.execute('ALTER TABLE user_new RENAME TO user')
        
        # Recreate any indexes that were on the original table
        cursor.execute('CREATE INDEX idx_user_email ON user (email)')
        cursor.execute('CREATE INDEX idx_user_username ON user (username)')
        cursor.execute('CREATE INDEX idx_user_role ON user (role_id)')
        
        print("Successfully updated user table with role_id column")
    else:
        print("User table already has role_id column")
    
    # Commit and close
    conn.commit()
    conn.close()

# Run the function with app context
with app.app_context():
    add_role_column()
    print("Database schema update complete!")
