"""
Smart SQLite migration to add USDT fields to payment_methods table
Automatically finds the database file
"""

import sqlite3
import os
import glob

# Possible database locations
possible_paths = [
    'instance/betting.db',  # Found via find command
    'instance/abkbet.db',
    'abkbet.db',
    '../instance/abkbet.db',
    '/home/ABKBet/ABKBet/instance/betting.db',
]

# Also search for any .db files
db_files = glob.glob('**/*.db', recursive=True)
possible_paths.extend(db_files)

# Find the database
DB_PATH = None
for path in possible_paths:
    if os.path.exists(path):
        DB_PATH = path
        break

if not DB_PATH:
    print("❌ Could not find database file!")
    print("\nSearched in:")
    for path in possible_paths[:4]:
        print(f"  - {path}")
    print(f"\nFound .db files:")
    for db in db_files:
        print(f"  - {db}")
    print("\nPlease run this command to find your database:")
    print("  find . -name '*.db' -type f")
    exit(1)

print(f"✓ Found database at: {DB_PATH}")
print("Adding USDT fields to payment_methods table...\n")

# Connect to database
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

try:
    # Check if payment_methods table exists
    cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name='payment_methods'
    """)
    
    if not cursor.fetchone():
        print("❌ payment_methods table doesn't exist!")
        print("\nExisting tables:")
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        for table in cursor.fetchall():
            print(f"  - {table[0]}")
        exit(1)
    
    print("✓ payment_methods table found")
    
    # Check current columns
    cursor.execute("PRAGMA table_info(payment_methods)")
    columns = [col[1] for col in cursor.fetchall()]
    
    changes_made = False
    
    # Add usdt_wallet_address if it doesn't exist
    if 'usdt_wallet_address' in columns:
        print("✓ usdt_wallet_address column already exists")
    else:
        cursor.execute("""
            ALTER TABLE payment_methods 
            ADD COLUMN usdt_wallet_address VARCHAR(255)
        """)
        print("✓ Added usdt_wallet_address column")
        changes_made = True
    
    # Add usdt_network if it doesn't exist
    cursor.execute("PRAGMA table_info(payment_methods)")
    columns = [col[1] for col in cursor.fetchall()]
    
    if 'usdt_network' in columns:
        print("✓ usdt_network column already exists")
    else:
        cursor.execute("""
            ALTER TABLE payment_methods 
            ADD COLUMN usdt_network VARCHAR(50)
        """)
        print("✓ Added usdt_network column")
        changes_made = True
    
    # Commit changes
    if changes_made:
        conn.commit()
        print("\n✅ Database migration complete!")
    else:
        print("\n✅ All columns already exist - no changes needed!")
    
    # Show all columns
    cursor.execute("PRAGMA table_info(payment_methods)")
    all_columns = [col[1] for col in cursor.fetchall()]
    
    print("\n📊 Current payment_methods columns:")
    for col in all_columns:
        marker = "🆕" if col in ['usdt_wallet_address', 'usdt_network'] else "  "
        print(f"{marker} {col}")
    
    print("\n✅ Done!")
    print("\nNext steps:")
    print("1. Go to Web tab in PythonAnywhere")
    print("2. Click 'Reload abkbet.pythonanywhere.com'")
    print("3. Clear browser cache (Ctrl+Shift+R)")
    print("4. Test USDT payment method creation")
    
except sqlite3.Error as e:
    print(f"\n❌ SQLite error: {e}")
    conn.rollback()
except Exception as e:
    print(f"\n❌ Error: {e}")
    conn.rollback()
finally:
    conn.close()
