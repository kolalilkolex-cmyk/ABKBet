"""
Add USDT wallet address and network fields to payment_methods table
Run this script to add the new columns to your existing database
"""

from app import create_app
from app.extensions import db

app = create_app()

with app.app_context():
    try:
        # Add usdt_wallet_address column
        db.engine.execute("""
            ALTER TABLE payment_methods 
            ADD COLUMN usdt_wallet_address VARCHAR(255);
        """)
        print("✓ Added usdt_wallet_address column")
    except Exception as e:
        print(f"usdt_wallet_address column might already exist or error: {e}")
    
    try:
        # Add usdt_network column
        db.engine.execute("""
            ALTER TABLE payment_methods 
            ADD COLUMN usdt_network VARCHAR(50);
        """)
        print("✓ Added usdt_network column")
    except Exception as e:
        print(f"usdt_network column might already exist or error: {e}")
    
    print("\n✓ Database migration complete!")
    print("You can now use USDT payment methods with wallet address and network type.")
