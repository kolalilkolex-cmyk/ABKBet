"""Create withdrawal_requests table in the database"""

import sys
import os

# Add parent directory to path so we can import app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db
from app.models import User  # Import User model from __init__.py
from app.models.withdrawal_request import WithdrawalRequest

def create_withdrawal_table():
    """Create withdrawal_requests table"""
    app = create_app()
    
    with app.app_context():
        try:
            # Create table
            db.create_all()
            print("✅ Successfully created withdrawal_requests table!")
            
            # Verify table exists
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            
            if 'withdrawal_requests' in tables:
                print(f"✅ Verified: withdrawal_requests table exists")
                
                # Show columns
                columns = inspector.get_columns('withdrawal_requests')
                print(f"\nTable columns ({len(columns)}):")
                for col in columns:
                    print(f"  - {col['name']} ({col['type']})")
            else:
                print("❌ Warning: withdrawal_requests table not found after creation")
                
        except Exception as e:
            print(f"❌ Error creating withdrawal_requests table: {e}")
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    create_withdrawal_table()
