import sqlite3
import os

# Get database path
db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'instance', 'betting.db')
print(f"📂 Database: {db_path}")

# Connect to database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    # Add cashout_value column to bets table
    cursor.execute("""
        ALTER TABLE bets ADD COLUMN cashout_value FLOAT;
    """)
    print("✓ Added cashout_value column to bets table")
    
    # Add is_cashed_out column
    cursor.execute("""
        ALTER TABLE bets ADD COLUMN is_cashed_out BOOLEAN DEFAULT 0;
    """)
    print("✓ Added is_cashed_out column to bets table")
    
    # Add cashed_out_at column
    cursor.execute("""
        ALTER TABLE bets ADD COLUMN cashed_out_at DATETIME;
    """)
    print("✓ Added cashed_out_at column to bets table")
    
    conn.commit()
    print("✅ Database migration completed!")
    
except sqlite3.OperationalError as e:
    if "duplicate column name" in str(e).lower():
        print("⚠️  Columns already exist, skipping migration")
    else:
        print(f"❌ Error: {e}")
        raise
finally:
    conn.close()
