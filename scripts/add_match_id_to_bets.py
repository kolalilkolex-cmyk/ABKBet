import sqlite3
import os

# Get the database path
db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'instance', 'betting.db')

print(f"📂 Database: {db_path}")

# Connect to the database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    # Add match_id column to bets table
    cursor.execute("""
        ALTER TABLE bets ADD COLUMN match_id INTEGER;
    """)
    conn.commit()
    print("✓ Added match_id column to bets table")
    print("✅ Database migration completed!")
    
except sqlite3.OperationalError as e:
    if "duplicate column name" in str(e).lower():
        print("⚠️  Column match_id already exists")
    else:
        print(f"❌ Error: {e}")
finally:
    conn.close()
