"""Add reset_token and reset_token_expiry columns to users table"""
import sqlite3
import os

db_path = os.path.join('instance', 'betting.db')

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check if columns already exist
    cursor.execute("PRAGMA table_info(users)")
    columns = [column[1] for column in cursor.fetchall()]
    
    if 'reset_token' not in columns:
        print("Adding reset_token column...")
        cursor.execute("ALTER TABLE users ADD COLUMN reset_token VARCHAR(255)")
        print("✅ reset_token column added")
    else:
        print("ℹ️ reset_token column already exists")
    
    if 'reset_token_expiry' not in columns:
        print("Adding reset_token_expiry column...")
        cursor.execute("ALTER TABLE users ADD COLUMN reset_token_expiry DATETIME")
        print("✅ reset_token_expiry column added")
    else:
        print("ℹ️ reset_token_expiry column already exists")
    
    conn.commit()
    print("\n✅ Database migration completed successfully!")
    
except sqlite3.Error as e:
    print(f"❌ Error: {e}")
finally:
    if conn:
        conn.close()
