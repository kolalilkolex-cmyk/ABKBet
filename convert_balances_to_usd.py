#!/usr/bin/env python3
"""
Convert user balances from BTC to USD
Run this ONCE after deploying USD system updates
"""

import sqlite3
import os

def convert_balances():
    """Convert all user balances from BTC to USD"""
    
    BTC_PRICE_USD = 45000.0
    
    # Connect directly to database
    db_path = os.path.join(os.path.dirname(__file__), 'instance', 'betting.db')
    if not os.path.exists(db_path):
        print(f"❌ Database not found at: {db_path}")
        print("Make sure you're running this from the ABKBet directory")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        print("\n" + "="*60)
        print("CONVERTING USER BALANCES FROM BTC TO USD")
        print("="*60 + "\n")
        
        # First, check what tables exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        print("Available tables:", [t[0] for t in tables])
        
        # Try different possible table names
        user_table = None
        for table_name in ['users', 'user', 'User', 'Users']:
            try:
                cursor.execute(f"SELECT id, username, balance FROM {table_name} LIMIT 1")
                user_table = table_name
                print(f"✓ Found user table: {table_name}\n")
                break
            except sqlite3.OperationalError:
                continue
        
        if not user_table:
            print("❌ Could not find user table!")
            print("Available tables:", [t[0] for t in tables])
            return
        
        # Get all users
        cursor.execute(f"SELECT id, username, balance FROM {user_table}")
        users = cursor.fetchall()
        
        converted_count = 0
        total_usd_before = 0
        total_usd_after = 0
        
        for user_id, username, old_balance in users:
            old_balance = old_balance or 0.0
            
            # Only convert if balance looks like BTC (small number > 0)
            # BTC values are typically 0.00001 to 0.1
            # USD values are typically 10 to 10000
            if 0 < old_balance < 1:
                # This looks like BTC, convert to USD
                new_balance = old_balance * BTC_PRICE_USD
                cursor.execute(f"UPDATE {user_table} SET balance = ? WHERE id = ?", (new_balance, user_id))
                converted_count += 1
                total_usd_after += new_balance
                
                print(f"✓ {username:20} | {old_balance:12.8f} BTC → ${new_balance:10.2f} USD")
            else:
                # Already in USD or zero balance
                total_usd_before += old_balance
                if old_balance > 0:
                    print(f"  {username:20} | ${old_balance:10.2f} USD (already converted)")
        
        # Commit changes
        conn.commit()
        
        print("\n" + "="*60)
        print("CONVERSION COMPLETE")
        print("="*60)
        print(f"Total users processed: {len(users)}")
        print(f"Users converted: {converted_count}")
        print(f"Users already in USD: {len(users) - converted_count}")
        print(f"Total balance after conversion: ${total_usd_after + total_usd_before:,.2f} USD")
        print("\n✓ All balances now in USD!")
        print("\nNext steps:")
        print("1. Reload your web app in PythonAnywhere")
        print("2. Test deposits and withdrawals")
        print("3. Verify balance displays correctly\n")
        
    except Exception as e:
        print(f"\n❌ ERROR during conversion: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

if __name__ == '__main__':
    convert_balances()
