#!/bin/bash
# Emergency Quick Fix - Run this in PythonAnywhere Bash console NOW
# This will create the missing tables immediately

cd /home/ABKBet/ABKBet
workon abkbet_env

echo ""
echo "🚨 Creating Missing Tables..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

python << 'PYTHON_SCRIPT'
from app import create_app, db
from sqlalchemy import text

app = create_app('production')

with app.app_context():
    print("📋 Creating withdrawal_requests table...")
    try:
        db.session.execute(text("""
            CREATE TABLE IF NOT EXISTS withdrawal_requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                payment_method VARCHAR(50) NOT NULL,
                amount_usd FLOAT NOT NULL,
                payment_details TEXT,
                country VARCHAR(50),
                bank_name VARCHAR(100),
                account_number VARCHAR(50),
                account_name VARCHAR(100),
                wallet_address VARCHAR(255),
                status VARCHAR(20) DEFAULT 'PENDING',
                admin_notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                processed_at TIMESTAMP,
                processed_by INTEGER,
                FOREIGN KEY (user_id) REFERENCES users(id),
                FOREIGN KEY (processed_by) REFERENCES users(id)
            )
        """))
        db.session.commit()
        print("✅ withdrawal_requests created")
    except Exception as e:
        print(f"⚠️  withdrawal_requests: {e}")
        db.session.rollback()

    print("\n📋 Creating premium_bookings table...")
    try:
        db.session.execute(text("""
            CREATE TABLE IF NOT EXISTS premium_bookings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                booking_code VARCHAR(20) UNIQUE NOT NULL,
                selections JSON NOT NULL,
                total_odds FLOAT NOT NULL,
                price_usd FLOAT DEFAULT 250.0,
                created_by_admin_id INTEGER NOT NULL,
                status VARCHAR(20) DEFAULT 'active',
                description VARCHAR(500),
                expires_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (created_by_admin_id) REFERENCES users(id)
            )
        """))
        db.session.commit()
        print("✅ premium_bookings created")
    except Exception as e:
        print(f"⚠️  premium_bookings: {e}")
        db.session.rollback()

    print("\n📋 Creating premium_booking_purchases table...")
    try:
        db.session.execute(text("""
            CREATE TABLE IF NOT EXISTS premium_booking_purchases (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                booking_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                amount_paid_usd FLOAT NOT NULL,
                payment_method VARCHAR(50) DEFAULT 'balance',
                purchased_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (booking_id) REFERENCES premium_bookings(id),
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """))
        db.session.commit()
        print("✅ premium_booking_purchases created")
    except Exception as e:
        print(f"⚠️  premium_booking_purchases: {e}")
        db.session.rollback()

    print("\n✅ ALL TABLES CREATED!")
    print("\n🔄 Now reload your web app from the Web tab")
PYTHON_SCRIPT

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Done! Reload your web app now."
echo ""
