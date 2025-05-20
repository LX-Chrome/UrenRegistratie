#!/usr/bin/env python

"""
Database migration script to update foreign key constraints in factuur table.
This allows for deletion of clients (klanten) even when they have associated invoices.
"""

import os
import sys
import sqlite3
from datetime import datetime

DATABASE_PATH = 'database.db'

def get_current_datetime():
    """Get current datetime in format for logging"""
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

def backup_database():
    """Create a backup of the database before making changes"""
    backup_path = f"database_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
    
    # Copy the database file
    try:
        import shutil
        shutil.copy2(DATABASE_PATH, backup_path)
        print(f"[{get_current_datetime()}] Database backed up to {backup_path}")
        return True
    except Exception as e:
        print(f"[{get_current_datetime()}] Error backing up database: {e}")
        return False

def update_factuur_constraints():
    """Update the foreign key constraints in the factuur table"""
    print(f"[{get_current_datetime()}] Starting constraint update on factuur table...")
    
    # Connect to the database
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    try:
        # Enable foreign keys
        cursor.execute("PRAGMA foreign_keys = ON;")
        
        # Start transaction
        cursor.execute("BEGIN TRANSACTION;")
        
        # Get all data from the factuur table
        cursor.execute("SELECT * FROM factuur;")
        factuur_data = cursor.fetchall()
        
        # Get the column names
        cursor.execute("PRAGMA table_info(factuur);")
        columns = cursor.fetchall()
        column_names = [column[1] for column in columns]
        
        print(f"[{get_current_datetime()}] Creating temporary table...")
        
        # Create a temporary table with the same structure
        cursor.execute("CREATE TABLE factuur_temp AS SELECT * FROM factuur WHERE 0;")
        
        # Drop the original table
        cursor.execute("DROP TABLE factuur;")
        
        print(f"[{get_current_datetime()}] Recreating factuur table with CASCADE constraint...")
        
        # Create the factuur table with the CASCADE constraint
        cursor.execute("""
        CREATE TABLE factuur (
            id INTEGER PRIMARY KEY,
            factuur_nummer VARCHAR(50) UNIQUE NOT NULL,
            klant_id INTEGER NOT NULL,
            opdracht_id INTEGER,
            datum DATE NOT NULL,
            vervaldatum DATE NOT NULL,
            btw_percentage FLOAT DEFAULT 21.0,
            subtotaal FLOAT NOT NULL,
            btw_bedrag FLOAT NOT NULL,
            totaal FLOAT NOT NULL,
            betaald BOOLEAN DEFAULT 0,
            betaaldatum DATE,
            betalingsvoorwaarden VARCHAR(500) DEFAULT 'Betaling binnen 30 dagen',
            notities TEXT,
            creator_id INTEGER NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (klant_id) REFERENCES klant (id) ON DELETE CASCADE,
            FOREIGN KEY (opdracht_id) REFERENCES opdracht (id),
            FOREIGN KEY (creator_id) REFERENCES user (id)
        );
        """)
        
        # Create indexes
        cursor.execute("CREATE INDEX idx_factuur_nummer ON factuur (factuur_nummer);")
        cursor.execute("CREATE INDEX idx_factuur_klant ON factuur (klant_id);")
        cursor.execute("CREATE INDEX idx_factuur_datum ON factuur (datum);")
        cursor.execute("CREATE INDEX idx_factuur_betaald ON factuur (betaald);")
        
        # Reinsert all data
        if factuur_data:
            placeholders = ", ".join(["?" for _ in range(len(column_names))])
            insert_sql = f"INSERT INTO factuur ({', '.join(column_names)}) VALUES ({placeholders})"
            
            print(f"[{get_current_datetime()}] Restoring {len(factuur_data)} invoice records...")
            cursor.executemany(insert_sql, factuur_data)
        
        # Drop the temporary table
        cursor.execute("DROP TABLE factuur_temp;")
        
        # Commit the transaction
        conn.commit()
        print(f"[{get_current_datetime()}] Factuur table constraints updated successfully!")
        
    except Exception as e:
        # Rollback in case of error
        conn.rollback()
        print(f"[{get_current_datetime()}] Error updating factuur table: {e}")
        return False
    finally:
        conn.close()
    
    return True

def main():
    """Main function to run the migration"""
    print(f"[{get_current_datetime()}] Starting database migration for factuur constraints...")
    
    # Check if database file exists
    if not os.path.exists(DATABASE_PATH):
        print(f"[{get_current_datetime()}] Error: Database file '{DATABASE_PATH}' not found!")
        return False
    
    # Backup the database
    if not backup_database():
        print(f"[{get_current_datetime()}] Migration aborted - backup failed")
        return False
    
    # Update the constraints
    if not update_factuur_constraints():
        print(f"[{get_current_datetime()}] Migration failed")
        return False
    
    print(f"[{get_current_datetime()}] Migration completed successfully")
    print("You should now be able to delete clients (klanten) even if they have associated invoices.")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
