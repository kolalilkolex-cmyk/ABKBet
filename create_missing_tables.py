"""
Create missing tables: withdrawal_requests and premium_booking_purchases
Run this if you're getting "no such table" errors
"""
from app import create_app, db
from sqlalchemy import text
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_missing_tables():
    """Create withdrawal_requests and premium_booking_purchases tables"""
    app = create_app('production')
    
    with app.app_context():
        print("\n" + "="*70)
        print("🔧 Creating Missing Database Tables")
        print("="*70 + "\n")
        
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        existing_tables = inspector.get_table_names()
        
        # Create withdrawal_requests table
        if 'withdrawal_requests' not in existing_tables:
            print("📋 Creating withdrawal_requests table...")
            try:
                db.session.execute(text("""
                    CREATE TABLE withdrawal_requests (
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
                print("   ✅ withdrawal_requests table created\n")
            except Exception as e:
                print(f"   ❌ Error creating withdrawal_requests: {e}\n")
                db.session.rollback()
        else:
            print("   ℹ️  withdrawal_requests table already exists\n")
        
        # Create premium_bookings table (if not exists)
        if 'premium_bookings' not in existing_tables:
            print("📋 Creating premium_bookings table...")
            try:
                db.session.execute(text("""
                    CREATE TABLE premium_bookings (
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
                print("   ✅ premium_bookings table created\n")
            except Exception as e:
                print(f"   ❌ Error creating premium_bookings: {e}\n")
                db.session.rollback()
        else:
            print("   ℹ️  premium_bookings table already exists\n")
        
        # Create premium_booking_purchases table
        if 'premium_booking_purchases' not in existing_tables:
            print("📋 Creating premium_booking_purchases table...")
            try:
                db.session.execute(text("""
                    CREATE TABLE premium_booking_purchases (
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
                print("   ✅ premium_booking_purchases table created\n")
            except Exception as e:
                print(f"   ❌ Error creating premium_booking_purchases: {e}\n")
                db.session.rollback()
        else:
            print("   ℹ️  premium_booking_purchases table already exists\n")
        
        # Verify all tables now exist
        print("🔍 Verifying tables...")
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        
        required = ['withdrawal_requests', 'premium_bookings', 'premium_booking_purchases']
        all_exist = True
        
        for table in required:
            if table in tables:
                print(f"   ✅ {table}")
            else:
                print(f"   ❌ {table} - STILL MISSING!")
                all_exist = False
        
        print("\n" + "="*70)
        if all_exist:
            print("✅ ALL TABLES CREATED SUCCESSFULLY!")
            print("="*70)
            print("\n🔄 Next Steps:")
            print("   1. Reload your web app")
            print("   2. Test withdrawals page (should work now)")
            print("   3. Test premium bookings page (should work now)")
            print("\n")
        else:
            print("⚠️  SOME TABLES STILL MISSING")
            print("="*70)
            print("\n   Try running: python -c \"from app import create_app, db; app=create_app('production'); app.app_context().push(); db.create_all()\"")
            print("\n")

if __name__ == '__main__':
    create_missing_tables()
