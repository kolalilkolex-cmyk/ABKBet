"""
Create payment_methods table for admin-managed deposit methods

This table stores the platform's payment receiving information that admins can update.
Users will see these methods when making deposits.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from app.models import db
from sqlalchemy import text

def upgrade():
    """Create payment_methods table"""
    app = create_app()
    
    with app.app_context():
        try:
            # Check if table already exists
            inspector = db.inspect(db.engine)
            tables = inspector.get_table_names()
            
            if 'payment_methods' in tables:
                print("Table 'payment_methods' already exists, skipping creation")
                return
            
            print("Creating payment_methods table...")
            
            # Create the table
            db.session.execute(text("""
                CREATE TABLE payment_methods (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    method_type VARCHAR(50) NOT NULL,
                    method_name VARCHAR(100) NOT NULL,
                    is_active BOOLEAN DEFAULT 1,
                    wallet_address VARCHAR(255),
                    account_name VARCHAR(255),
                    account_number VARCHAR(100),
                    bank_name VARCHAR(255),
                    swift_code VARCHAR(50),
                    email VARCHAR(255),
                    phone VARCHAR(50),
                    qr_code VARCHAR(500),
                    instructions TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    created_by INTEGER,
                    FOREIGN KEY (created_by) REFERENCES users(id)
                )
            """))
            
            db.session.commit()
            print("✓ payment_methods table created successfully")
            
            # Add some default payment methods
            print("\nAdding default payment methods...")
            
            default_methods = [
                {
                    'method_type': 'bitcoin',
                    'method_name': 'Bitcoin (BTC)',
                    'wallet_address': 'tb1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh',
                    'account_name': None,
                    'account_number': None,
                    'bank_name': None,
                    'instructions': 'Send BTC to the address above. Minimum deposit: 0.001 BTC'
                },
                {
                    'method_type': 'bank_transfer',
                    'method_name': 'Bank Transfer',
                    'wallet_address': None,
                    'account_name': 'ABKBet Limited',
                    'account_number': '1234567890',
                    'bank_name': 'Sample Bank',
                    'instructions': 'Use your username as reference when making bank transfers'
                }
            ]
            
            for method in default_methods:
                db.session.execute(text("""
                    INSERT INTO payment_methods 
                    (method_type, method_name, wallet_address, account_name, account_number, bank_name, instructions, is_active)
                    VALUES 
                    (:method_type, :method_name, :wallet_address, :account_name, :account_number, :bank_name, :instructions, 1)
                """), method)
            
            db.session.commit()
            print(f"✓ Added {len(default_methods)} default payment methods")
            
            print("\n" + "="*60)
            print("MIGRATION COMPLETE")
            print("="*60)
            print("\nYou can now:")
            print("1. View payment methods: GET /api/admin/payment-methods")
            print("2. Update methods via admin panel")
            print("3. Users can see active methods: GET /api/payment/methods")
            
        except Exception as e:
            print(f"Error during migration: {e}")
            db.session.rollback()
            raise

def downgrade():
    """Drop payment_methods table"""
    app = create_app()
    
    with app.app_context():
        try:
            print("Dropping payment_methods table...")
            db.session.execute(text("DROP TABLE IF EXISTS payment_methods"))
            db.session.commit()
            print("✓ payment_methods table dropped successfully")
            
        except Exception as e:
            print(f"Error during rollback: {e}")
            db.session.rollback()
            raise

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python create_payment_methods_table.py [upgrade|downgrade]")
        sys.exit(1)
    
    action = sys.argv[1]
    
    if action == 'upgrade':
        upgrade()
    elif action == 'downgrade':
        downgrade()
    else:
        print("Invalid action. Use 'upgrade' or 'downgrade'")
        sys.exit(1)
