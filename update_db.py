import sqlite3

# Connect to the database
conn = sqlite3.connect('instance/database.db')
cursor = conn.cursor()

# Drop the user_new table if it exists from a previous attempt
cursor.execute("DROP TABLE IF EXISTS user_new")

# Create a new user table with the correct schema
cursor.execute('''
CREATE TABLE user_new (
    id INTEGER PRIMARY KEY,
    username VARCHAR(64) NOT NULL UNIQUE, 
    email VARCHAR(120) NOT NULL UNIQUE,
    password_hash VARCHAR(256),
    role_id INTEGER DEFAULT 1,
    is_active BOOLEAN DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    medewerker_id INTEGER,
    FOREIGN KEY(role_id) REFERENCES role(id),
    FOREIGN KEY(medewerker_id) REFERENCES medewerker(id)
)
''')

# Copy existing data, setting default values for new columns
cursor.execute('''
INSERT INTO user_new (id, username, email, password_hash, created_at, role_id, is_active, medewerker_id)
SELECT id, username, email, password_hash, created_at, 1, 1, NULL FROM user
''')

# Check if the data was transferred correctly
cursor.execute("SELECT COUNT(*) FROM user_new")
new_count = cursor.fetchone()[0]
cursor.execute("SELECT COUNT(*) FROM user")
old_count = cursor.fetchone()[0]

if new_count == old_count:
    print(f"Successfully transferred {new_count} users to the new table.")
    
    # Rename tables to complete the migration
    cursor.execute("DROP TABLE user")
    cursor.execute("ALTER TABLE user_new RENAME TO user")
    
    # Create indexes on the new user table
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_user_email ON user (email)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_user_username ON user (username)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_user_role ON user (role_id)")
    
    print("Migration completed successfully!")
else:
    print(f"WARNING: User count mismatch - old table: {old_count}, new table: {new_count}")
    print("Migration aborted. Please check your data.")
    conn.rollback()

# Commit changes and close connection
conn.commit()
conn.close()
