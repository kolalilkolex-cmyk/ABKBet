import sqlite3
import os

# Get the database path
db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'instance', 'betting.db')

print(f"📂 Database: {db_path}")

# Connect to the database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    # Create booking_codes table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS booking_codes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code VARCHAR(10) UNIQUE NOT NULL,
            bet_data TEXT NOT NULL,
            created_by INTEGER,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            used_count INTEGER DEFAULT 0,
            FOREIGN KEY (created_by) REFERENCES users (id)
        );
    """)
    conn.commit()
    print("✓ Created booking_codes table")
    
    # Create index on code for faster lookups
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_booking_code ON booking_codes(code);
    """)
    conn.commit()
    print("✓ Created index on booking code")
    
    print("✅ Database migration completed!")
    
except sqlite3.Error as e:
    print(f"❌ Error: {e}")
finally:
    conn.close()
