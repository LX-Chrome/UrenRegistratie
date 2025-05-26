from app import db
from flask_migrate import Migrate, MigrateCommand

def upgrade():
    # Add opdracht_id column to time_entry table
    db.engine.execute('ALTER TABLE time_entry ADD COLUMN opdracht_id INTEGER REFERENCES opdracht(id)')
    
    # Add opdracht_id column to check_in table if it doesn't exist
    db.engine.execute('ALTER TABLE check_in ADD COLUMN opdracht_id INTEGER REFERENCES opdracht(id)')

def downgrade():
    # Remove opdracht_id column from time_entry table
    db.engine.execute('ALTER TABLE time_entry DROP COLUMN opdracht_id')
    
    # Remove opdracht_id column from check_in table
    db.engine.execute('ALTER TABLE check_in DROP COLUMN opdracht_id') 