#!/usr/bin/env python3
"""
Deployment Check Script - Run this on PythonAnywhere to diagnose issues
"""

import sys
import os

print("="*80)
print("DEPLOYMENT CHECK")
print("="*80)

# 1. Check Python version
print("\n1. Python Version:")
print(f"   {sys.version}")

# 2. Check current directory
print("\n2. Current Directory:")
print(f"   {os.getcwd()}")

# 3. Check sys.path
print("\n3. Python Path (sys.path):")
for path in sys.path:
    print(f"   - {path}")

# 4. Check if app can be imported
print("\n4. Import Test:")
try:
    from app import create_app
    print("   ✓ Successfully imported create_app")
except Exception as e:
    print(f"   ✗ Failed to import create_app: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# 5. Check if app can be created
print("\n5. App Creation Test:")
try:
    app = create_app('production')
    print("   ✓ Successfully created Flask app")
except Exception as e:
    print(f"   ✗ Failed to create app: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# 6. Check database
print("\n6. Database Check:")
try:
    from app import db
    from app.models import Match, User, Bet
    
    with app.app_context():
        # Check if tables exist
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        print(f"   Tables found: {', '.join(tables)}")
        
        # Count records
        match_count = Match.query.count()
        user_count = User.query.count()
        bet_count = Bet.query.count()
        
        print(f"   ✓ Matches: {match_count}")
        print(f"   ✓ Users: {user_count}")
        print(f"   ✓ Bets: {bet_count}")
        
except Exception as e:
    print(f"   ✗ Database error: {e}")
    import traceback
    traceback.print_exc()

# 7. Check config
print("\n7. Configuration Check:")
try:
    with app.app_context():
        print(f"   Database URI: {app.config.get('SQLALCHEMY_DATABASE_URI')}")
        print(f"   Secret Key Set: {'Yes' if app.config.get('SECRET_KEY') else 'No'}")
        print(f"   JWT Secret Set: {'Yes' if app.config.get('JWT_SECRET_KEY') else 'No'}")
except Exception as e:
    print(f"   ✗ Config error: {e}")

# 8. Check blueprints
print("\n8. Registered Blueprints:")
try:
    for blueprint_name, blueprint in app.blueprints.items():
        print(f"   - {blueprint_name}: {blueprint.url_prefix}")
except Exception as e:
    print(f"   ✗ Blueprint error: {e}")

# 9. Check routes
print("\n9. Sample Routes:")
try:
    routes = []
    for rule in app.url_map.iter_rules():
        routes.append(f"{rule.rule} -> {rule.endpoint}")
    
    # Show first 20 routes
    for route in sorted(routes)[:20]:
        print(f"   {route}")
    print(f"   ... and {len(routes) - 20} more routes")
except Exception as e:
    print(f"   ✗ Route error: {e}")

print("\n" + "="*80)
print("DEPLOYMENT CHECK COMPLETE")
print("="*80)
