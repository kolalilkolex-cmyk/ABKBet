"""
Complete Fix Script for ABKBet Deployment
Fixes:
1. Seeds all 6 payment methods to database
2. Adds sample matches for testing
3. Verifies all tables exist
"""
from app import create_app, db
from app.models.payment_method import PaymentMethod
from app.models import Match
from datetime import datetime, timedelta
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fix_all_issues():
    """Run all fixes"""
    app = create_app('production')
    
    with app.app_context():
        print("\n" + "="*70)
        print("🔧 ABKBet Complete Fix Script")
        print("="*70 + "\n")
        
        # Fix 1: Seed all 6 payment methods
        print("📦 STEP 1: Seeding Payment Methods...")
        print("-"*70)
        
        payment_methods = [
            {
                'method_type': 'bitcoin',
                'method_name': 'Bitcoin (BTC)',
                'wallet_address': 'tb1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh',
                'instructions': 'Send BTC to the address above. Minimum deposit: 0.001 BTC. Include your username in the transaction note.',
                'is_active': True
            },
            {
                'method_type': 'usdt',
                'method_name': 'USDT (Tether)',
                'wallet_address': 'TRC20: TXYZabcdef123456789',
                'instructions': 'Send USDT (TRC20 network) to the address above. Make sure to use TRC20 network only. Minimum: 10 USDT.',
                'is_active': True
            },
            {
                'method_type': 'bank_transfer',
                'method_name': 'Bank Transfer',
                'account_name': 'ABKBet Limited',
                'account_number': '1234567890',
                'bank_name': 'Sample Bank',
                'swift_code': 'SAMPNG01',
                'instructions': 'Transfer to the bank account above. Use your username as the reference. Available for Nigerian banks.',
                'is_active': True
            },
            {
                'method_type': 'paypal',
                'method_name': 'PayPal',
                'email': 'payments@abkbet.com',
                'instructions': 'Send payment to the PayPal email above. Add your username in the payment note. Minimum: $10 USD.',
                'is_active': True
            },
            {
                'method_type': 'skrill',
                'method_name': 'Skrill',
                'email': 'payments@abkbet.com',
                'instructions': 'Send payment to the Skrill email above. Add your username in the payment note. Minimum: $10 USD.',
                'is_active': True
            },
            {
                'method_type': 'mobile_money',
                'method_name': 'MTN Mobile Money',
                'phone': '+1234567890',
                'instructions': 'Send Mobile Money to the phone number above. Use your username as reference. MTN network only.',
                'is_active': True
            }
        ]
        
        added_count = 0
        updated_count = 0
        
        for method_data in payment_methods:
            existing = PaymentMethod.query.filter_by(
                method_type=method_data['method_type']
            ).first()
            
            if existing:
                # Update existing
                existing.method_name = method_data['method_name']
                existing.wallet_address = method_data.get('wallet_address')
                existing.account_name = method_data.get('account_name')
                existing.account_number = method_data.get('account_number')
                existing.bank_name = method_data.get('bank_name')
                existing.swift_code = method_data.get('swift_code')
                existing.email = method_data.get('email')
                existing.phone = method_data.get('phone')
                existing.instructions = method_data['instructions']
                existing.is_active = method_data['is_active']
                existing.updated_at = datetime.utcnow()
                
                print(f"  ✓ Updated: {method_data['method_name']}")
                updated_count += 1
            else:
                # Create new
                new_method = PaymentMethod(
                    method_type=method_data['method_type'],
                    method_name=method_data['method_name'],
                    wallet_address=method_data.get('wallet_address'),
                    account_name=method_data.get('account_name'),
                    account_number=method_data.get('account_number'),
                    bank_name=method_data.get('bank_name'),
                    swift_code=method_data.get('swift_code'),
                    email=method_data.get('email'),
                    phone=method_data.get('phone'),
                    instructions=method_data['instructions'],
                    is_active=method_data['is_active']
                )
                db.session.add(new_method)
                print(f"  ✓ Added: {method_data['method_name']}")
                added_count += 1
        
        db.session.commit()
        print(f"\n  Summary: {added_count} added, {updated_count} updated")
        print(f"  ✅ Total: {added_count + updated_count} payment methods\n")
        
        # Fix 2: Add sample matches
        print("🎮 STEP 2: Adding Sample Matches...")
        print("-"*70)
        
        existing_matches = Match.query.count()
        if existing_matches > 0:
            print(f"  ℹ️  {existing_matches} matches already exist, skipping...")
        else:
            now = datetime.utcnow()
            matches = [
                Match(
                    league='English Premier League',
                    home_team='Manchester United',
                    away_team='Liverpool',
                    match_date=now + timedelta(days=2, hours=3),
                    home_odds=2.10,
                    draw_odds=3.40,
                    away_odds=3.20,
                    status='scheduled'
                ),
                Match(
                    league='Spanish La Liga',
                    home_team='Real Madrid',
                    away_team='Barcelona',
                    match_date=now + timedelta(days=3, hours=5),
                    home_odds=2.25,
                    draw_odds=3.30,
                    away_odds=3.00,
                    status='scheduled'
                ),
                Match(
                    league='German Bundesliga',
                    home_team='Bayern Munich',
                    away_team='Borussia Dortmund',
                    match_date=now + timedelta(days=4, hours=2),
                    home_odds=1.85,
                    draw_odds=3.60,
                    away_odds=4.20,
                    status='scheduled'
                ),
                Match(
                    league='Italian Serie A',
                    home_team='Juventus',
                    away_team='AC Milan',
                    match_date=now + timedelta(days=5, hours=4),
                    home_odds=2.40,
                    draw_odds=3.20,
                    away_odds=2.90,
                    status='scheduled'
                ),
                Match(
                    league='French Ligue 1',
                    home_team='Paris Saint-Germain',
                    away_team='Marseille',
                    match_date=now + timedelta(days=6, hours=3),
                    home_odds=1.65,
                    draw_odds=3.80,
                    away_odds=5.50,
                    status='scheduled'
                )
            ]
            
            for match in matches:
                db.session.add(match)
                print(f"  ✓ Added: {match.home_team} vs {match.away_team}")
            
            db.session.commit()
            print(f"\n  ✅ Added {len(matches)} sample matches\n")
        
        # Fix 3: Create missing tables and verify
        print("🗄️  STEP 3: Creating Missing Tables...")
        print("-"*70)
        
        from sqlalchemy import inspect, text
        inspector = inspect(db.engine)
        existing_tables = inspector.get_table_names()
        
        # Create withdrawal_requests if missing
        if 'withdrawal_requests' not in existing_tables:
            print("  📋 Creating withdrawal_requests table...")
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
                print("     ✓ Created")
            except Exception as e:
                print(f"     ⚠️  Error: {e}")
                db.session.rollback()
        else:
            print("  ✓ withdrawal_requests (exists)")
        
        # Create premium_bookings if missing
        if 'premium_bookings' not in existing_tables:
            print("  📋 Creating premium_bookings table...")
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
                print("     ✓ Created")
            except Exception as e:
                print(f"     ⚠️  Error: {e}")
                db.session.rollback()
        else:
            print("  ✓ premium_bookings (exists)")
        
        # Create premium_booking_purchases if missing
        if 'premium_booking_purchases' not in existing_tables:
            print("  📋 Creating premium_booking_purchases table...")
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
                print("     ✓ Created")
            except Exception as e:
                print(f"     ⚠️  Error: {e}")
                db.session.rollback()
        else:
            print("  ✓ premium_booking_purchases (exists)")
        
        # Verify all required tables
        print("\n  🔍 Verifying all tables...")
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        
        required_tables = [
            'users',
            'matches',
            'bets',
            'payment_methods',
            'deposits',
            'withdrawal_requests',
            'premium_bookings',
            'premium_booking_purchases'
        ]
        
        all_good = True
        for table in required_tables:
            if table in tables:
                print(f"     ✓ {table}")
            else:
                print(f"     ❌ {table} - MISSING!")
                all_good = False
        
        if not all_good:
            print("\n  ⚠️  Some tables are still missing!")
        else:
            print("\n  ✅ All required tables exist\n")
        
        # Summary
        print("="*70)
        print("✅ FIX COMPLETE!")
        print("="*70)
        print("\n📊 Status:")
        print(f"  • Payment Methods: {PaymentMethod.query.count()} active")
        print(f"  • Sample Matches: {Match.query.count()} total")
        print(f"  • Database Tables: {'All present' if all_good else 'Some missing'}")
        print("\n🔄 Next Steps:")
        print("  1. Reload your web app on PythonAnywhere")
        print("  2. Test admin panel → Payment Methods (should see all 6)")
        print("  3. Test user deposits/withdrawals (all 6 methods)")
        print("  4. Check matches page (should see 5 matches)")
        print("\n")

if __name__ == '__main__':
    fix_all_issues()
