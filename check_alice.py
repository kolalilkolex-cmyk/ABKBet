#!/usr/bin/env python3
"""Check alice user in database"""
import sqlite3
import os
from werkzeug.security import generate_password_hash

# Database path
db_path = os.path.join(os.path.dirname(__file__), 'instance', 'betting.db')

if not os.path.exists(db_path):
    print(f"❌ Database not found at: {db_path}")
    exit(1)

# Connect to database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Check if alice exists
cursor.execute("SELECT id, username, email, balance, is_admin FROM users WHERE username = ?", ('alice',))
result = cursor.fetchone()

if result:
    user_id, username, email, balance, is_admin = result
    print(f"✅ User 'alice' found in database")
    print(f"   ID: {user_id}")
    print(f"   Username: {username}")
    print(f"   Email: {email}")
    print(f"   Balance: {balance} BTC")
    print(f"   Is Admin: {'Yes' if is_admin else 'No'}")
    
    # Update password to a known value
    new_password_hash = generate_password_hash('alice123')
    cursor.execute("UPDATE users SET password_hash = ?, is_admin = 0 WHERE username = ?", 
                   (new_password_hash, 'alice'))
    conn.commit()
    print(f"\n✅ Password reset to: alice123")
    print(f"✅ Set as regular user (not admin)")
else:
    print(f"❌ User 'alice' not found")
    print(f"\n💡 Creating alice user...")
    
    # Create alice
    password_hash = generate_password_hash('alice123')
    cursor.execute("""
        INSERT INTO users (username, email, password_hash, balance, is_admin, is_active)
        VALUES (?, ?, ?, ?, ?, ?)
    """, ('alice', 'alice@example.com', password_hash, 0.001, 0, 1))
    conn.commit()
    
    print(f"✅ User 'alice' created")
    print(f"   Username: alice")
    print(f"   Email: alice@example.com")
    print(f"   Password: alice123")
    print(f"   Balance: 0.001 BTC")

conn.close()

print("\n" + "="*50)
print("ALICE LOGIN DETAILS:")
print("="*50)
print("Username: alice")
print("Password: alice123")
print("="*50)
print("\nYou can login at: http://localhost:5000")
print("\nTo register a NEW user:")
print("1. Go to http://localhost:5000")
print("2. Click 'Register' or sign up")
print("3. Fill in your details")
print("4. Registration is open to anyone!")
