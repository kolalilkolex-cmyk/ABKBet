import sqlite3
import os

# Get database path
db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'instance', 'betting.db')
print(f"📂 Database: {db_path}")

# Connect to database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    # Add booking_code column to bets table
    cursor.execute("""
        ALTER TABLE bets ADD COLUMN booking_code VARCHAR(10);
    """)
    print("✓ Added booking_code column to bets table")
    
    # Create index for faster lookups
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_bet_booking_code ON bets(booking_code);
    """)
    print("✓ Created index on booking_code")
    
    conn.commit()
    print("✅ Database migration completed!")
    
except sqlite3.OperationalError as e:
    if "duplicate column name" in str(e).lower():
        print("⚠️  Column already exists, skipping migration")
    else:
        print(f"❌ Error: {e}")
        raise
finally:
    conn.close()
