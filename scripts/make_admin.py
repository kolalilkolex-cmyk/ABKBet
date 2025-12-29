"""Add is_admin field to users table"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.models import db, User
from run import create_app

def add_admin_field():
    """Add is_admin column to users table"""
    app = create_app()
    with app.app_context():
        try:
            # Try to add the column
            with db.engine.connect() as conn:
                conn.execute(db.text('ALTER TABLE users ADD COLUMN is_admin BOOLEAN DEFAULT 0'))
                conn.commit()
            print("✓ Added is_admin column to users table")
        except Exception as e:
            if 'duplicate column name' in str(e).lower() or 'already exists' in str(e).lower():
                print("✓ is_admin column already exists")
            else:
                print(f"Error: {e}")

def make_admin(username):
    """Make a user an admin"""
    app = create_app()
    with app.app_context():
        user = User.query.filter_by(username=username).first()
        if not user:
            print(f"✗ User '{username}' not found")
            return False
        
        user.is_admin = True
        db.session.commit()
        print(f"✓ User '{username}' is now an admin")
        return True

if __name__ == '__main__':
    print("=" * 50)
    print("ADMIN SETUP SCRIPT")
    print("=" * 50)
    
    # Add the column first
    add_admin_field()
    
    # Make a user admin
    if len(sys.argv) > 1:
        username = sys.argv[1]
        make_admin(username)
    else:
        print("\nUsage: python scripts/make_admin.py <username>")
        print("Example: python scripts/make_admin.py admin")
        
        # List existing users
        app = create_app()
        with app.app_context():
            users = User.query.all()
            if users:
                print("\nExisting users:")
                for u in users:
                    admin_status = "✓ ADMIN" if getattr(u, 'is_admin', False) else ""
                    print(f"  - {u.username} {admin_status}")
