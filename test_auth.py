"""
Quick test script to verify login and admin authentication
"""
from app import create_app
from app.models import User
from app.utils.auth import verify_password

app = create_app()

with app.app_context():
    print("="*60)
    print("AUTHENTICATION TEST")
    print("="*60)
    
    # Test 1: Check if admin user exists
    admin = User.query.filter_by(username='admin').first()
    if admin:
        print(f"✓ Admin user exists (ID: {admin.id})")
        print(f"  - Email: {admin.email}")
        print(f"  - Is Admin: {admin.is_admin}")
        print(f"  - Is Active: {admin.is_active}")
    else:
        print("✗ Admin user not found")
    
    # Test 2: Check password verification
    if admin:
        # Test with common admin password
        test_password = 'admin123'
        if verify_password(admin.password_hash, test_password):
            print(f"✓ Password verification works")
        else:
            print(f"✗ Password verification failed")
    
    # Test 3: Check all users
    users = User.query.all()
    print(f"\n✓ Total users in database: {len(users)}")
    for u in users[:5]:  # Show first 5
        print(f"  - {u.username} (Admin: {u.is_admin}, Active: {u.is_active})")
    
    print("="*60)
    print("TEST COMPLETE")
    print("="*60)
