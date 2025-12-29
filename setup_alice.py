#!/usr/bin/env python3
"""Setup alice as regular user"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app import create_app
from app.models import db, User
from werkzeug.security import generate_password_hash

flask_app = create_app()

with flask_app.app_context():
    # Check if alice exists
    alice = User.query.filter_by(username='alice').first()
    
    if alice:
        print(f"✅ User 'alice' already exists")
        print(f"   Username: {alice.username}")
        print(f"   Email: {alice.email}")
        print(f"   Balance: {alice.balance} BTC")
        print(f"   Is Admin: {alice.is_admin}")
        
        # Set a known password for testing
        alice.password = generate_password_hash('alice123')
        alice.is_admin = False  # Make sure alice is a regular user
        db.session.commit()
        print(f"\n✅ Password reset to: alice123")
        print(f"✅ Set as regular user (not admin)")
    else:
        # Create alice user
        alice = User(
            username='alice',
            email='alice@example.com',
            password=generate_password_hash('alice123'),
            balance=0.001,  # Give some starting balance
            is_admin=False  # Regular user, not admin
        )
        db.session.add(alice)
        db.session.commit()
        print(f"✅ User 'alice' created successfully")
        print(f"   Username: alice")
        print(f"   Email: alice@example.com")
        print(f"   Password: alice123")
        print(f"   Balance: 0.001 BTC")
        print(f"   Is Admin: False")
    
    print("\n" + "="*50)
    print("LOGIN DETAILS:")
    print("="*50)
    print("Username: alice")
    print("Password: alice123")
    print("="*50)
    print("\nYou can now login at: http://localhost:5000")
