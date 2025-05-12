import sqlite3

# Connect to the database
conn = sqlite3.connect('instance/database.db')
cursor = conn.cursor()

# Drop the temporary table if it exists from a previous attempt
cursor.execute("DROP TABLE IF EXISTS time_entry_new")

# Create a new time_entry table with the correct schema
cursor.execute('''
CREATE TABLE time_entry_new (
    id INTEGER PRIMARY KEY,
    date DATE NOT NULL,
    hours FLOAT NOT NULL,
    description VARCHAR(500) NOT NULL,
    project VARCHAR(100) NOT NULL,
    user_id INTEGER NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    is_billable BOOLEAN DEFAULT 1,
    hourly_rate FLOAT,
    invoice_id INTEGER,
    FOREIGN KEY(user_id) REFERENCES user(id) ON DELETE CASCADE,
    FOREIGN KEY(invoice_id) REFERENCES factuur(id)
)
''')

# Copy existing data, setting default values for new columns
cursor.execute('''
INSERT INTO time_entry_new (id, date, hours, description, project, user_id, created_at, is_billable, hourly_rate, invoice_id)
SELECT id, date, hours, description, project, user_id, created_at, 1, NULL, NULL FROM time_entry
''')

# Check if the data was transferred correctly
cursor.execute("SELECT COUNT(*) FROM time_entry_new")
new_count = cursor.fetchone()[0]
cursor.execute("SELECT COUNT(*) FROM time_entry")
old_count = cursor.fetchone()[0]

if new_count == old_count:
    print(f"Successfully transferred {new_count} time entries to the new table.")
    
    # Rename tables to complete the migration
    cursor.execute("DROP TABLE time_entry")
    cursor.execute("ALTER TABLE time_entry_new RENAME TO time_entry")
    
    # Create indexes on the new time_entry table
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_time_entry_user_date ON time_entry (user_id, date)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_time_entry_project ON time_entry (project)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_time_entry_invoice ON time_entry (invoice_id)")
    
    print("Migration completed successfully!")
else:
    print(f"WARNING: Time entry count mismatch - old table: {old_count}, new table: {new_count}")
    print("Migration aborted. Please check your data.")
    conn.rollback()

# Commit changes and close connection
conn.commit()
conn.close()
