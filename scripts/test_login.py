#!/usr/bin/env python3
"""Test login functionality"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app import create_app
from app.models import db, User
from app.utils.auth import verify_password

flask_app = create_app()

with flask_app.app_context():
    print("=" * 60)
    print("TESTING LOGIN FUNCTIONALITY")
    print("=" * 60)
    
    # Test with alice
    username = "alice"
    password = "alice123"
    
    print(f"\nTesting login for: {username}")
    
    # Find user
    user = User.query.filter_by(username=username).first()
    
    if not user:
        print(f"❌ User '{username}' not found in database")
    else:
        print(f"✅ User found: {user.username}")
        print(f"   Email: {user.email}")
        print(f"   Balance: {user.balance} BTC")
        print(f"   Active: {user.is_active}")
        print(f"   Password hash: {user.password_hash[:50]}...")
        
        # Test password verification
        print(f"\nTesting password verification...")
        try:
            is_valid = verify_password(user.password_hash, password)
            if is_valid:
                print(f"✅ Password verification SUCCESS")
                print(f"✅ Login should work!")
            else:
                print(f"❌ Password verification FAILED")
                print(f"   The password '{password}' does not match the stored hash")
        except Exception as e:
            print(f"❌ Error during password verification: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "=" * 60)
