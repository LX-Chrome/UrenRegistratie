import sqlite3

# Connect to the database
conn = sqlite3.connect('instance/database.db')
cursor = conn.cursor()

# Get list of tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
print("Tables in database:", [table[0] for table in tables])

# Check the structure of the user table
cursor.execute("PRAGMA table_info('user')")
columns = cursor.fetchall()
print("\nColumns in the user table:")
for col in columns:
    print(f"  {col[0]}: {col[1]} (type: {col[2]}, notnull: {col[3]}, default: {col[4]}, pk: {col[5]}")

# Check the structure of the time_entry table
cursor.execute("PRAGMA table_info('time_entry')")
columns = cursor.fetchall()
print("\nColumns in the time_entry table:")
for col in columns:
    print(f"  {col[0]}: {col[1]} (type: {col[2]}, notnull: {col[3]}, default: {col[4]}, pk: {col[5]}")

# Check if there are any entries in the user table
cursor.execute("SELECT COUNT(*) FROM user")
user_count = cursor.fetchone()[0]
print(f"\nNumber of users in the database: {user_count}")

if user_count > 0:
    # Show a sample user (without password)
    cursor.execute("SELECT id, username, email FROM user LIMIT 1")
    sample_user = cursor.fetchone()
    print(f"Sample user: id={sample_user[0]}, username={sample_user[1]}, email={sample_user[2]}")

# Check if there are any entries in the time_entry table
cursor.execute("SELECT COUNT(*) FROM time_entry")
entry_count = cursor.fetchone()[0]
print(f"\nNumber of time entries in the database: {entry_count}")

if entry_count > 0:
    # Show a sample time entry
    cursor.execute("SELECT id, date, hours, project FROM time_entry LIMIT 1")
    sample_entry = cursor.fetchone()
    print(f"Sample time entry: id={sample_entry[0]}, date={sample_entry[1]}, hours={sample_entry[2]}, project={sample_entry[3]}")

# Close the connection
conn.close()
