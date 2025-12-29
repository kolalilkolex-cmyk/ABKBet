#!/usr/bin/env python3
"""List all registered users"""
import sqlite3
import os

db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'instance', 'betting.db')
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("=" * 100)
print("ALL REGISTERED USERS")
print("=" * 100)

cursor.execute("""
    SELECT id, username, email, balance, created_at, is_active 
    FROM users 
    ORDER BY created_at DESC
""")

users = cursor.fetchall()

if not users:
    print("\n❌ No users found in database")
else:
    print(f"\nTotal Users: {len(users)}\n")
    print(f"{'ID':<5} {'Username':<20} {'Email':<30} {'Balance':<12} {'Status':<10} {'Created'}")
    print("-" * 100)
    
    for user in users:
        user_id, username, email, balance, created_at, is_active = user
        status = "✅ Active" if is_active else "❌ Inactive"
        print(f"{user_id:<5} {username:<20} {email:<30} {balance:<12.6f} {status:<10} {created_at}")

conn.close()

print("\n" + "=" * 100)
print("\n✅ User data is stored permanently in: instance/betting.db")
print("✅ Users can login anytime with their username/password")
print("\nTo test:")
print("1. Register a new user on the website")
print("2. Run this script to see them in the database")
print("3. Login with the same credentials - it will work!")
