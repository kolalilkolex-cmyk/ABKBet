"""
Add payment fields to users table

This migration adds payment/withdrawal information fields to the User model.
Run this after updating the User model in app/models/__init__.py
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from app.models import db
from sqlalchemy import text

def upgrade():
    """Add payment fields to users table"""
    app = create_app()
    
    with app.app_context():
        try:
            # Check if columns already exist before adding
            inspector = db.inspect(db.engine)
            existing_columns = [col['name'] for col in inspector.get_columns('users')]
            
            columns_to_add = [
                ('withdrawal_wallet', 'VARCHAR(255)'),
                ('bank_account_name', 'VARCHAR(255)'),
                ('bank_account_number', 'VARCHAR(100)'),
                ('bank_name', 'VARCHAR(255)'),
                ('paypal_email', 'VARCHAR(255)'),
                ('skrill_email', 'VARCHAR(255)'),
                ('usdt_wallet', 'VARCHAR(255)'),
                ('payment_notes', 'TEXT')
            ]
            
            for column_name, column_type in columns_to_add:
                if column_name not in existing_columns:
                    print(f"Adding column: {column_name}")
                    db.session.execute(text(f"ALTER TABLE users ADD COLUMN {column_name} {column_type}"))
                else:
                    print(f"Column {column_name} already exists, skipping")
            
            db.session.commit()
            print("✓ Payment fields migration completed successfully")
            
        except Exception as e:
            print(f"Error during migration: {e}")
            db.session.rollback()
            raise

def downgrade():
    """Remove payment fields from users table"""
    app = create_app()
    
    with app.app_context():
        try:
            columns_to_remove = [
                'withdrawal_wallet',
                'bank_account_name',
                'bank_account_number',
                'bank_name',
                'paypal_email',
                'skrill_email',
                'usdt_wallet',
                'payment_notes'
            ]
            
            for column_name in columns_to_remove:
                print(f"Removing column: {column_name}")
                db.session.execute(text(f"ALTER TABLE users DROP COLUMN IF EXISTS {column_name}"))
            
            db.session.commit()
            print("✓ Payment fields rollback completed successfully")
            
        except Exception as e:
            print(f"Error during rollback: {e}")
            db.session.rollback()
            raise

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python add_payment_fields.py [upgrade|downgrade]")
        sys.exit(1)
    
    action = sys.argv[1]
    
    if action == 'upgrade':
        upgrade()
    elif action == 'downgrade':
        downgrade()
    else:
        print("Invalid action. Use 'upgrade' or 'downgrade'")
        sys.exit(1)
