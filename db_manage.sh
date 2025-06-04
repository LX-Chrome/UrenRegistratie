#!/bin/bash

# Database Management and Backup Script for UrenRegistratie
# ========================================================

# Function to display usage
show_usage() {
  echo "UrenRegistratie Database Management Script"
  echo ""
  echo "Usage: $0 [command]"
  echo ""
  echo "Commands:"
  echo "  backup         Create a new database backup"
  echo "  restore [file] Restore database from backup file (or most recent if not specified)"
  echo "  list           List available backups"
  echo "  clean [days]   Remove backups older than specified days (default: 30)"
  echo "  info           Show database information"
  echo ""
  exit 1
}

# Set paths
APP_DIR=$(pwd)
BACKUP_DIR="${APP_DIR}/backups"
INSTANCE_DIR="${APP_DIR}/instance"
DB_FILE="${INSTANCE_DIR}/database.db"
DATE_FORMAT=$(date +%Y%m%d_%H%M%S)

# Check if instance directory exists
if [ ! -d "$INSTANCE_DIR" ]; then
  mkdir -p "$INSTANCE_DIR"
fi

# Check if backup directory exists
if [ ! -d "$BACKUP_DIR" ]; then
  mkdir -p "$BACKUP_DIR"
fi

# Backup database
backup_db() {
  if [ -f "$DB_FILE" ]; then
    BACKUP_FILE="${BACKUP_DIR}/database_backup_${DATE_FORMAT}.db"
    echo "Creating backup: $BACKUP_FILE"
    cp "$DB_FILE" "$BACKUP_FILE"
    echo "Backup completed successfully!"
    echo "File: $BACKUP_FILE"
    echo "Size: $(du -h "$BACKUP_FILE" | cut -f1)"
  else
    echo "Error: Database file not found at $DB_FILE"
    exit 1
  fi
}

# Restore database
restore_db() {
  local source_file="$1"
  
  # If no file specified, use the most recent backup
  if [ -z "$source_file" ]; then
    source_file=$(find "$BACKUP_DIR" -name "database_backup_*.db" | sort -r | head -n1)
    if [ -z "$source_file" ]; then
      echo "Error: No backup files found in $BACKUP_DIR"
      exit 1
    fi
  fi
  
  # Check if source file exists
  if [ ! -f "$source_file" ]; then
    echo "Error: Backup file not found: $source_file"
    exit 1
  fi
  
  # Create a backup of current database first
  if [ -f "$DB_FILE" ]; then
    SAFETY_BACKUP="${BACKUP_DIR}/database_before_restore_${DATE_FORMAT}.db"
    echo "Creating safety backup before restore: $SAFETY_BACKUP"
    cp "$DB_FILE" "$SAFETY_BACKUP"
  fi
  
  # Restore the database
  echo "Restoring database from: $source_file"
  cp "$source_file" "$DB_FILE"
  echo "Database restored successfully!"
}

# List available backups
list_backups() {
  echo "Available database backups:"
  echo "--------------------------"
  if [ -d "$BACKUP_DIR" ]; then
    find "$BACKUP_DIR" -name "database_backup_*.db" -printf "%TY-%Tm-%Td %TH:%TM:%TS %p %s bytes\n" | sort -r
  else
    echo "No backup directory found."
  fi
}

# Clean old backups
clean_backups() {
  local days=${1:-30}
  echo "Removing backups older than $days days..."
  
  if [ -d "$BACKUP_DIR" ]; then
    find "$BACKUP_DIR" -name "database_backup_*.db" -type f -mtime +$days -delete -print
    echo "Cleanup completed."
  else
    echo "No backup directory found."
  fi
}

# Show database info
show_db_info() {
  if [ -f "$DB_FILE" ]; then
    echo "Database information:"
    echo "--------------------"
    echo "Path: $DB_FILE"
    echo "Size: $(du -h "$DB_FILE" | cut -f1)"
    echo "Last modified: $(stat -c '%y' "$DB_FILE")"
    
    # Check if sqlite3 is installed
    if command -v sqlite3 &> /dev/null; then
      echo ""
      echo "Database structure:"
      echo "------------------"
      sqlite3 "$DB_FILE" ".tables"
      echo ""
      echo "Row counts:"
      echo "----------"
      for table in $(sqlite3 "$DB_FILE" ".tables"); do
        count=$(sqlite3 "$DB_FILE" "SELECT COUNT(*) FROM $table;")
        echo "$table: $count rows"
      done
    else
      echo ""
      echo "Install sqlite3 for more database information:"
      echo "sudo apt-get install sqlite3"
    fi
  else
    echo "Database file not found at: $DB_FILE"
  fi
}

# Main script logic
case "$1" in
  backup)
    backup_db
    ;;
  restore)
    restore_db "$2"
    ;;
  list)
    list_backups
    ;;
  clean)
    clean_backups "$2"
    ;;
  info)
    show_db_info
    ;;
  *)
    show_usage
    ;;
esac 