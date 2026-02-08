import sqlite3
import os
import json
from db_config import DB_PATH

def run_migrations():
    print(f"Running migrations for {DB_PATH}...")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create migrations table if not exists to track applied migrations
    cursor.execute("CREATE TABLE IF NOT EXISTS _migrations (id TEXT PRIMARY KEY, applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)")
    
    migration_dir = "migrations"
    migrations = sorted([f for f in os.listdir(migration_dir) if f.endswith(".sql")])
    
    for migration in migrations:
        cursor.execute("SELECT id FROM _migrations WHERE id = ?", (migration,))
        if cursor.fetchone():
            print(f"Migration {migration} already applied. Skipping.")
            continue
            
        print(f"Applying migration {migration}...")
        with open(os.path.join(migration_dir, migration), 'r') as f:
            sql = f.read()
            try:
                cursor.executescript(sql)
                cursor.execute("INSERT INTO _migrations (id) VALUES (?)", (migration,))
                conn.commit()
                print(f"Successfully applied {migration}.")
            except Exception as e:
                conn.rollback()
                print(f"FAILED to apply {migration}: {str(e)}")
                break
                
    conn.close()
    print("Migration process complete.")

if __name__ == "__main__":
    run_migrations()
