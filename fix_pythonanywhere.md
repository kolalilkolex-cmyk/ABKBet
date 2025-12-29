# PythonAnywhere Deployment Fix Guide

## Current Issue
Login failing and matches not loading on lilkolex.pythonanywhere.com

## Root Causes
1. WSGI configuration may have wrong username
2. Database tables might not exist
3. Virtual environment might not have all dependencies
4. Static files might not be served correctly

## Step-by-Step Fix

### 1. Update WSGI Configuration
On PythonAnywhere Web tab, click on WSGI configuration file and ensure it has:

```python
import sys
import os

# Add your project directory to the sys.path
project_home = '/home/Lilkolex/ABKBet'
if project_home not in sys.path:
    sys.path = [project_home] + sys.path

# Load environment variables
from dotenv import load_dotenv
env_path = os.path.join(project_home, '.env')
load_dotenv(env_path)

# Set default environment variables
if not os.environ.get('SECRET_KEY'):
    os.environ['SECRET_KEY'] = 'change-this-to-a-random-secret-key-production-2024'
if not os.environ.get('FOOTBALL_API_KEY'):
    os.environ['FOOTBALL_API_KEY'] = '8a0943a24d4c44f4f5d8a091f6348e9f'
if not os.environ.get('FOOTBALL_API_ENABLED'):
    os.environ['FOOTBALL_API_ENABLED'] = 'true'
if not os.environ.get('FLASK_ENV'):
    os.environ['FLASK_ENV'] = 'production'

# Import Flask app
from run import flask_app as application
```

### 2. Check Virtual Environment
In PythonAnywhere Bash console:

```bash
cd /home/Lilkolex/ABKBet
source ~/venv/bin/activate

# Install/upgrade dependencies
pip install -r requirements.txt

# Verify key packages
pip list | grep -i flask
pip list | grep -i sqlalchemy
```

### 3. Create Database Tables
Run the check_deployment.py script:

```bash
cd /home/Lilkolex/ABKBet
source ~/venv/bin/activate
python check_deployment.py
```

If tables are missing, create them:

```bash
python -c "from app import create_app, db; app=create_app('production'); app.app_context().push(); db.create_all(); print('Tables created')"
```

Or use the update_db.py script:

```bash
cat > update_db.py << 'EOF'
from app import create_app, db
app = create_app('production')
with app.app_context():
    db.create_all()
    print('Database tables updated successfully')
EOF

python update_db.py
```

### 4. Verify Database File Permissions
```bash
ls -la /home/Lilkolex/ABKBet/instance/betting.db
chmod 664 /home/Lilkolex/ABKBet/instance/betting.db
```

### 5. Check Error Logs
On PythonAnywhere:
- Web tab -> Error log (click to view)
- Server log (click to view)

Look for:
- Import errors
- Database connection errors
- Missing environment variables

### 6. Test API Endpoints Directly
In Bash console:

```bash
cd /home/Lilkolex/ABKBet
source ~/venv/bin/activate

# Test if app can start
python -c "from run import flask_app; print('App created successfully')"

# Test matches endpoint
python -c "
from app import create_app, db
from app.models import Match
app = create_app('production')
with app.app_context():
    matches = Match.query.limit(5).all()
    print(f'Found {len(matches)} matches')
    for m in matches:
        print(f'  - {m.home_team} vs {m.away_team}')
"
```

### 7. Reload Web App
After all fixes:
- Go to Web tab on PythonAnywhere
- Click the green "Reload" button
- Wait 10 seconds
- Test site: https://lilkolex.pythonanywhere.com

### 8. Test in Browser Console
Open browser console (F12) and check:

```javascript
// Test if API is accessible
fetch('https://lilkolex.pythonanywhere.com/api/health')
  .then(r => r.json())
  .then(d => console.log('Health check:', d))
  .catch(e => console.error('Health check failed:', e))

// Test matches endpoint
fetch('https://lilkolex.pythonanywhere.com/api/bets/matches/manual')
  .then(r => r.json())
  .then(d => console.log('Matches:', d))
  .catch(e => console.error('Matches failed:', e))

// Test login
fetch('https://lilkolex.pythonanywhere.com/api/auth/login', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({username: 'admin', password: 'password'})
})
  .then(r => r.json())
  .then(d => console.log('Login:', d))
  .catch(e => console.error('Login failed:', e))
```

## Common Issues

### Issue: "No module named 'app'"
- Fix: Check WSGI file has correct path: `/home/Lilkolex/ABKBet`
- Fix: Verify virtual environment is selected in Web tab

### Issue: "No such table: matches"
- Fix: Run `db.create_all()` as shown in step 3

### Issue: "CORS errors"
- Fix: Already configured in `app/__init__.py` with wildcard origins

### Issue: "Static files not loading"
- Fix: In Web tab, set Static files:
  - URL: `/static/`
  - Directory: `/home/Lilkolex/ABKBet/static/`

### Issue: "500 Internal Server Error"
- Check error log in Web tab
- Most likely: missing environment variable or import error

## Quick Diagnostic Commands

```bash
# All-in-one diagnostic
cd /home/Lilkolex/ABKBet
source ~/venv/bin/activate
python check_deployment.py > deployment_check.log 2>&1
cat deployment_check.log

# Check if Flask can start
python -c "from run import flask_app; print('OK')" || echo "FAILED"

# Check database
python -c "from app import create_app, db; app=create_app('production'); app.app_context().push(); from app.models import User; print(f'Users: {User.query.count()}')"

# List all routes
python -c "from run import flask_app; print('\n'.join([str(rule) for rule in flask_app.url_map.iter_rules()]))" | head -30
```

## After Fixes Checklist
- [ ] WSGI file updated with correct username
- [ ] Virtual environment has all dependencies
- [ ] Database tables created (premium_bookings, premium_booking_purchases, etc.)
- [ ] Database file has correct permissions (664)
- [ ] Web app reloaded on PythonAnywhere
- [ ] Error log shows no errors
- [ ] Health endpoint responds: `/api/health`
- [ ] Matches endpoint works: `/api/bets/matches/manual`
- [ ] Login works: `/api/auth/login`
- [ ] Static files load correctly
