"""
Quick script to fix match ordering on PythonAnywhere
Run this in PythonAnywhere bash console
"""

import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

print("=" * 60)
print("FIXING MATCH ORDERING")
print("=" * 60)

# Fix bet_routes.py
print("\n1. Fixing bet_routes.py...")
bet_routes_path = 'app/routes/bet_routes.py'

try:
    with open(bet_routes_path, 'r') as f:
        content = f.read()
    
    original_content = content
    
    # Replace all .desc() with .asc() for match_date ordering
    content = content.replace('.order_by(Match.match_date.desc())', '.order_by(Match.match_date.asc())')
    
    if content != original_content:
        with open(bet_routes_path, 'w') as f:
            f.write(content)
        print("   ✅ bet_routes.py updated")
    else:
        print("   ℹ️  bet_routes.py already correct")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Fix admin_routes.py
print("\n2. Fixing admin_routes.py...")
admin_routes_path = 'app/routes/admin_routes.py'

try:
    with open(admin_routes_path, 'r') as f:
        content = f.read()
    
    original_content = content
    
    # Replace all .desc() with .asc() for match ordering
    content = content.replace('.order_by(Match.created_at.desc())', '.order_by(Match.match_date.asc())')
    content = content.replace('.order_by(Match.match_date.desc())', '.order_by(Match.match_date.asc())')
    
    if content != original_content:
        with open(admin_routes_path, 'w') as f:
            f.write(content)
        print("   ✅ admin_routes.py updated")
    else:
        print("   ℹ️  admin_routes.py already correct")
except Exception as e:
    print(f"   ❌ Error: {e}")

print("\n" + "=" * 60)
print("✅ MATCH ORDERING FIX COMPLETE!")
print("=" * 60)
print("\nNow reload your web app:")
print("  • Go to Web tab in PythonAnywhere dashboard")
print("  • Click the green 'Reload' button")
print("\nOr run this command:")
print("  touch /var/www/abkbet_pythonanywhere_com_wsgi.py")
print("=" * 60)
