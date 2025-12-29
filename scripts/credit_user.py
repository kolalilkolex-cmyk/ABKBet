#!/usr/bin/env python3
"""Manually credit a user's balance (for testing or admin adjustments)"""
import sqlite3
import os

db_path = os.path.join(os.path.dirname(__file__), 'instance', 'betting.db')
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("=" * 60)
print("MANUAL USER BALANCE CREDIT")
print("=" * 60)

# Get username
username = input("\nEnter username to credit: ").strip()

# Check if user exists
cursor.execute("SELECT id, username, balance FROM users WHERE username = ?", (username,))
result = cursor.fetchone()

if not result:
    print(f"❌ User '{username}' not found!")
    conn.close()
    exit(1)

user_id, username, current_balance = result
print(f"\n✅ Found user: {username}")
print(f"   Current balance: {current_balance} BTC")

# Get amount
try:
    amount = float(input("\nEnter amount to credit (BTC): "))
except ValueError:
    print("❌ Invalid amount!")
    conn.close()
    exit(1)

if amount <= 0:
    print("❌ Amount must be positive!")
    conn.close()
    exit(1)

# Confirm
print(f"\n⚠️  About to credit {amount} BTC to {username}")
print(f"   New balance will be: {current_balance + amount} BTC")
confirm = input("   Continue? (yes/no): ").lower()

if confirm != 'yes':
    print("❌ Cancelled")
    conn.close()
    exit(0)

# Update balance
new_balance = current_balance + amount
cursor.execute("UPDATE users SET balance = ? WHERE id = ?", (new_balance, user_id))

# Create transaction record
import uuid
tx_hash = f"MANUAL_{uuid.uuid4().hex[:8].upper()}"
cursor.execute("""
    INSERT INTO transactions (user_id, amount, transaction_type, status, tx_hash, payment_method, from_address)
    VALUES (?, ?, 'deposit', 'confirmed', ?, 'manual_credit', 'ADMIN')
""", (user_id, amount, tx_hash))

conn.commit()
conn.close()

print("\n✅ SUCCESS!")
print(f"   Credited: {amount} BTC")
print(f"   New balance: {new_balance} BTC")
print(f"   Transaction ID: {tx_hash}")
print("\n" + "=" * 60)
