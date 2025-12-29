#!/bin/bash
# Quick Fix Script for PythonAnywhere Deployment Issues

echo "=========================================="
echo "ABKBet PythonAnywhere Quick Fix"
echo "=========================================="

# Change to project directory
cd /home/Lilkolex/ABKBet || { echo "Error: Cannot find ABKBet directory"; exit 1; }

# Activate virtual environment
source ~/venv/bin/activate || { echo "Error: Cannot activate venv"; exit 1; }

echo ""
echo "Step 1: Checking Python and dependencies..."
python --version
pip list | grep -i "flask\|sqlalchemy\|jwt"

echo ""
echo "Step 2: Testing app import..."
python -c "from run import flask_app; print('✓ App imports successfully')" || {
    echo "✗ Failed to import app"
    echo "Checking for detailed error:"
    python -c "from run import flask_app" 2>&1
    exit 1
}

echo ""
echo "Step 3: Checking database tables..."
python << 'PYEOF'
from app import create_app, db
from sqlalchemy import inspect

app = create_app('production')
with app.app_context():
    inspector = inspect(db.engine)
    tables = inspector.get_table_names()
    print(f"Tables found: {len(tables)}")
    for table in sorted(tables):
        print(f"  - {table}")
    
    # Check if critical tables exist
    required_tables = ['users', 'matches', 'bets', 'transactions']
    missing = [t for t in required_tables if t not in tables]
    if missing:
        print(f"\n⚠ Missing critical tables: {', '.join(missing)}")
        print("Running db.create_all()...")
        db.create_all()
        print("✓ Tables created")
    else:
        print("\n✓ All critical tables exist")
PYEOF

echo ""
echo "Step 4: Verifying database data..."
python << 'PYEOF'
from app import create_app, db
from app.models import User, Match, Bet

app = create_app('production')
with app.app_context():
    user_count = User.query.count()
    match_count = Match.query.count()
    bet_count = Bet.query.count()
    
    print(f"Users: {user_count}")
    print(f"Matches: {match_count}")
    print(f"Bets: {bet_count}")
    
    # Show sample matches
    if match_count > 0:
        print("\nSample matches:")
        matches = Match.query.limit(3).all()
        for m in matches:
            print(f"  - {m.home_team} vs {m.away_team} ({m.status})")
    else:
        print("\n⚠ No matches found - you may need to add matches via admin panel")
PYEOF

echo ""
echo "Step 5: Testing API endpoints..."
python << 'PYEOF'
from run import flask_app

with flask_app.app_context():
    # List routes
    routes = [str(rule) for rule in flask_app.url_map.iter_rules()]
    
    # Check critical routes
    critical_routes = [
        '/api/auth/login',
        '/api/bets/matches/manual',
        '/api/admin/matches'
    ]
    
    print("Critical routes check:")
    for route in critical_routes:
        found = any(route in r for r in routes)
        status = "✓" if found else "✗"
        print(f"  {status} {route}")
    
    print(f"\nTotal routes registered: {len(routes)}")
PYEOF

echo ""
echo "Step 6: Checking file permissions..."
ls -lh instance/betting.db 2>/dev/null || echo "⚠ Database file not found at instance/betting.db"

echo ""
echo "=========================================="
echo "Fix Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Go to PythonAnywhere Web tab"
echo "2. Click the green 'Reload' button"
echo "3. Check the error log for any issues"
echo "4. Test the site: https://lilkolex.pythonanywhere.com"
echo ""
