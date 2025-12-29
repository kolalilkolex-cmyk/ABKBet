import requests
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from run import create_app
from app.models import db, User

def register_and_make_admin(username, email, password):
    """Register a new user via API and make them admin"""
    
    # Step 1: Register via API
    try:
        response = requests.post(
            'http://127.0.0.1:5000/api/auth/register',
            json={
                'username': username,
                'email': email,
                'password': password
            },
            timeout=5
        )
        
        if response.status_code == 201:
            print(f"✓ User '{username}' registered successfully")
        elif response.status_code == 400:
            print(f"⚠ User '{username}' already exists, proceeding to make admin...")
        else:
            print(f"✗ Registration failed: {response.text}")
            return False
    except Exception as e:
        print(f"✗ Error registering user: {e}")
        return False
    
    # Step 2: Make them admin in database
    try:
        app = create_app()
        with app.app_context():
            user = User.query.filter_by(username=username).first()
            if not user:
                print(f"✗ User '{username}' not found in database")
                return False
            
            user.is_admin = True
            db.session.commit()
            print(f"✓ User '{username}' is now an admin!")
            return True
    except Exception as e:
        print(f"✗ Error making user admin: {e}")
        return False

if __name__ == '__main__':
    if len(sys.argv) != 4:
        print("\n" + "="*50)
        print("CREATE PERSONAL ADMIN USER")
        print("="*50)
        print("\nUsage: python scripts/create_my_admin.py <username> <email> <password>")
        print("\nExample: python scripts/create_my_admin.py admin admin@abkbet.com Admin123!")
        print()
        sys.exit(1)
    
    username = sys.argv[1]
    email = sys.argv[2]
    password = sys.argv[3]
    
    print("\n" + "="*50)
    print("CREATE PERSONAL ADMIN USER")
    print("="*50)
    print(f"\nCreating admin user: {username}")
    print(f"Email: {email}")
    print()
    
    success = register_and_make_admin(username, email, password)
    
    if success:
        print("\n✅ SUCCESS! You can now login at http://127.0.0.1:5000/admin with:")
        print(f"   Username: {username}")
        print(f"   Password: {password}")
        print()
    else:
        print("\n❌ Failed to create admin user")
        sys.exit(1)
