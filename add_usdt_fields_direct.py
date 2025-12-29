"""
Direct SQLite migration to add USDT fields to payment_methods table
This script connects directly to SQLite without needing Flask
"""

import sqlite3
import os

# Database path
DB_PATH = 'instance/abkbet.db'

if not os.path.exists(DB_PATH):
    print(f"❌ Database not found at: {DB_PATH}")
    print("Please make sure you're in the correct directory")
    exit(1)

print(f"📁 Found database at: {DB_PATH}")
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
        exit(1)
    
    print("✓ payment_methods table found")
    
    # Check if usdt_wallet_address column already exists
    cursor.execute("PRAGMA table_info(payment_methods)")
    columns = [col[1] for col in cursor.fetchall()]
    
    if 'usdt_wallet_address' in columns:
        print("✓ usdt_wallet_address column already exists")
    else:
        cursor.execute("""
            ALTER TABLE payment_methods 
            ADD COLUMN usdt_wallet_address VARCHAR(255)
        """)
        print("✓ Added usdt_wallet_address column")
    
    # Check if usdt_network column already exists
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
    
    # Commit changes
    conn.commit()
    
    # Verify columns were added
    cursor.execute("PRAGMA table_info(payment_methods)")
    all_columns = [col[1] for col in cursor.fetchall()]
    
    print("\n📊 Current payment_methods columns:")
    for col in all_columns:
        marker = "🆕" if col in ['usdt_wallet_address', 'usdt_network'] else "  "
        print(f"{marker} {col}")
    
    print("\n✅ Database migration complete!")
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
