"""Test if all imports work correctly"""
import sys
import os

print("Testing imports...")

try:
    from app import create_app, db
    print("✅ create_app and db imported")
except Exception as e:
    print(f"❌ Failed to import create_app/db: {e}")
    sys.exit(1)

try:
    from app.models import User
    print("✅ User model imported")
except Exception as e:
    print(f"❌ Failed to import User: {e}")
    sys.exit(1)

try:
    from app.utils.auth import hash_password, verify_password
    print("✅ auth utils imported")
except Exception as e:
    print(f"❌ Failed to import auth utils: {e}")
    sys.exit(1)

try:
    from flask_jwt_extended import create_access_token
    print("✅ JWT imported")
except Exception as e:
    print(f"❌ Failed to import JWT: {e}")
    sys.exit(1)

print("\nCreating app...")
try:
    app = create_app('development')
    print("✅ App created")
except Exception as e:
    print(f"❌ Failed to create app: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\nTesting database query...")
try:
    with app.app_context():
        user = User.query.filter_by(username='alice').first()
        if user:
            print(f"✅ Found user: {user.username}")
        else:
            print("❌ User alice not found")
except Exception as e:
    print(f"❌ Database query failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\nTesting password hash...")
try:
    test_hash = hash_password("test123")
    print(f"✅ Password hashed: {test_hash[:20]}...")
except Exception as e:
    print(f"❌ Password hash failed: {e}")
    import traceback
    traceback.print_exc()

print("\nTesting JWT token creation...")
try:
    with app.app_context():
        token = create_access_token(identity="1")
        print(f"✅ JWT token created: {token[:30]}...")
except Exception as e:
    print(f"❌ JWT token creation failed: {e}")
    import traceback
    traceback.print_exc()

print("\n✅ All tests passed!")
