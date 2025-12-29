# Fresh PythonAnywhere Deployment - From Scratch

## Step 1: Clean Up Old Deployment (5 minutes)

### 1.1 Backup Database (IMPORTANT!)
```bash
# In PythonAnywhere Bash console
cd /home/Lilkolex

# Find your database
find . -name "*.db" -type f

# Backup the database
cp betting.db betting_backup_$(date +%Y%m%d).db
# OR if database is elsewhere:
cp instance/betting.db betting_backup_$(date +%Y%m%d).db

# Verify backup
ls -lh betting_backup_*.db
```

### 1.2 Delete Old Files
```bash
# Remove old application directory
cd /home/Lilkolex
rm -rf ABKBet
rm -rf ABKBet_old
rm -rf pythonanywhere_*

# Clean up old zip files (optional)
rm -f *.zip

# List remaining files
ls -la
```

---

## Step 2: Upload New Deployment Package (2 minutes)

### Option A: Upload via Files Tab (Easiest)
1. Go to **Files** tab on PythonAnywhere
2. Click **Upload a file**
3. Upload `ABKBet_Complete_Fixed_20251205_001946.zip`
4. Wait for upload to complete

### Option B: Upload via wget (if package is hosted online)
```bash
cd /home/Lilkolex
wget YOUR_URL/ABKBet_Complete_Fixed_20251205_001946.zip
```

---

## Step 3: Extract Files (1 minute)

```bash
cd /home/Lilkolex

# Create new directory
mkdir -p ABKBet

# Extract files
unzip ABKBet_Complete_Fixed_20251205_001946.zip -d ABKBet

# Verify extraction
cd ABKBet
ls -la

# You should see:
# app/ templates/ static/ migrations/ scripts/
# config.py run.py wsgi.py requirements.txt etc.
```

---

## Step 4: Set Up Virtual Environment (3 minutes)

### 4.1 Create Virtual Environment
```bash
cd /home/Lilkolex

# Create new virtual environment with Python 3.10
mkvirtualenv --python=/usr/bin/python3.10 abkbet_env

# The environment will automatically activate
# You should see (abkbet_env) in your prompt
```

### 4.2 Install Dependencies
```bash
cd /home/Lilkolex/ABKBet

# Upgrade pip first
pip install --upgrade pip

# Install all requirements
pip install -r requirements.txt

# Verify key packages
pip list | grep -i "flask\|sqlalchemy\|jwt"

# Should see:
# Flask                    2.3.3
# Flask-SQLAlchemy         3.0.5
# Flask-JWT-Extended       4.4.4
```

---

## Step 5: Set Up Database (2 minutes)

### 5.1 Create Instance Directory
```bash
cd /home/Lilkolex/ABKBet

# Create instance folder
mkdir -p instance

# Set permissions
chmod 755 instance
```

### 5.2 Restore or Create Database

**Option A: Restore from Backup**
```bash
# Copy your backup database
cp ~/betting_backup_*.db instance/betting.db

# Set permissions
chmod 664 instance/betting.db
```

**Option B: Create Fresh Database**
```bash
cd /home/Lilkolex/ABKBet

# Activate environment if not already active
workon abkbet_env

# Create all tables
python << 'EOF'
from app import create_app, db
from app.models import User
from app.utils.auth import hash_password

app = create_app('production')
with app.app_context():
    # Create all tables
    db.create_all()
    print('✓ All tables created')
    
    # Create admin user
    admin = User(
        username='admin',
        email='admin@abkbet.com',
        password_hash=hash_password('admin123'),
        balance=1000.0,
        is_admin=True,
        is_active=True
    )
    db.session.add(admin)
    
    # Create test user
    test_user = User(
        username='testuser',
        email='test@abkbet.com',
        password_hash=hash_password('test123'),
        balance=100.0,
        is_active=True
    )
    db.session.add(test_user)
    
    db.session.commit()
    print('✓ Admin and test users created')
    print('  Admin: admin / admin123')
    print('  Test: testuser / test123')
EOF
```

### 5.3 Verify Database
```bash
cd /home/Lilkolex/ABKBet
workon abkbet_env

python << 'EOF'
from app import create_app, db
from app.models import User, Match, Bet
from sqlalchemy import inspect

app = create_app('production')
with app.app_context():
    # List all tables
    inspector = inspect(db.engine)
    tables = inspector.get_table_names()
    print(f'✓ Tables: {", ".join(sorted(tables))}')
    
    # Count records
    print(f'✓ Users: {User.query.count()}')
    print(f'✓ Matches: {Match.query.count()}')
    print(f'✓ Bets: {Bet.query.count()}')
EOF
```

---

## Step 6: Configure PythonAnywhere Web App (5 minutes)

### 6.1 Create Web App
1. Go to **Web** tab
2. Click **Add a new web app**
3. Choose **Manual configuration** (NOT Flask wizard!)
4. Select **Python 3.10**
5. Click **Next**

### 6.2 Configure WSGI File
1. On Web tab, click the **WSGI configuration file** link
2. **Delete ALL existing content**
3. **Paste this exactly:**

```python
import sys
import os

# Add project directory to Python path
project_home = '/home/Lilkolex/ABKBet'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Set environment variables
os.environ['FLASK_ENV'] = 'production'
os.environ['SECRET_KEY'] = 'your-production-secret-key-change-this'
os.environ['JWT_SECRET_KEY'] = 'your-jwt-secret-key-change-this'
os.environ['FOOTBALL_API_KEY'] = '8a0943a24d4c44f4f5d8a091f6348e9f'
os.environ['FOOTBALL_API_ENABLED'] = 'true'

# Import Flask application
from run import flask_app as application

# This is what PythonAnywhere uses
```

4. Click **Save**
5. Close the file

### 6.3 Configure Virtual Environment
1. On Web tab, scroll to **Virtualenv** section
2. Enter the path: `/home/Lilkolex/.virtualenvs/abkbet_env`
3. Click the **checkmark** button
4. Should show green text confirming the path

### 6.4 Configure Static Files
1. On Web tab, scroll to **Static files** section
2. Click **Enter URL** and enter: `/static/`
3. Click **Enter path** and enter: `/home/Lilkolex/ABKBet/static/`
4. Click the **checkmark** button

### 6.5 Reload Web App
1. Scroll to top of Web tab
2. Click the big green **Reload lilkolex.pythonanywhere.com** button
3. Wait 10 seconds for reload to complete

---

## Step 7: Verify Deployment (3 minutes)

### 7.1 Check Error Log
1. On Web tab, click **Error log** link
2. Look for any Python errors
3. Should see: `Application created with config: production`
4. Should NOT see any import errors or tracebacks

### 7.2 Check Server Log
1. On Web tab, click **Server log** link
2. Should see recent access logs
3. No 500 errors

### 7.3 Test Health Endpoint
In Bash console:
```bash
curl https://lilkolex.pythonanywhere.com/api/health
# Should return: {"status":"healthy"}
```

### 7.4 Test in Browser
Open browser and test:

**1. Homepage loads:**
- Visit: https://lilkolex.pythonanywhere.com
- Should see the betting interface

**2. Login works:**
- Username: `admin`
- Password: `admin123`
- Should successfully log in

**3. Check browser console (F12):**
```javascript
// Test matches endpoint
fetch('https://lilkolex.pythonanywhere.com/api/bets/matches/manual')
  .then(r => r.json())
  .then(d => console.log('Matches:', d))

// Test profile endpoint
const token = localStorage.getItem('abkbet_token');
fetch('https://lilkolex.pythonanywhere.com/api/auth/profile', {
  headers: {'Authorization': `Bearer ${token}`}
})
  .then(r => r.json())
  .then(d => console.log('Profile:', d))
```

---

## Step 8: Add Initial Data (Optional)

### 8.1 Add Sample Matches
Login as admin and go to admin panel:
- https://lilkolex.pythonanywhere.com/admin

Or use Python:
```bash
cd /home/Lilkolex/ABKBet
workon abkbet_env

python << 'EOF'
from app import create_app, db
from app.models import Match
from datetime import datetime, timedelta

app = create_app('production')
with app.app_context():
    # Add sample matches
    matches = [
        Match(
            home_team='Manchester United',
            away_team='Liverpool',
            league='Premier League',
            match_date=datetime.utcnow() + timedelta(hours=2),
            home_odds=2.20,
            draw_odds=3.30,
            away_odds=2.80,
            over25_odds=1.85,
            under25_odds=2.00,
            gg_odds=1.75,
            ng_odds=2.10,
            status='scheduled',
            is_manual=True
        ),
        Match(
            home_team='Real Madrid',
            away_team='Barcelona',
            league='La Liga',
            match_date=datetime.utcnow() + timedelta(hours=4),
            home_odds=1.95,
            draw_odds=3.50,
            away_odds=3.20,
            over25_odds=1.90,
            under25_odds=1.95,
            gg_odds=1.70,
            ng_odds=2.20,
            status='scheduled',
            is_manual=True
        )
    ]
    
    for match in matches:
        db.session.add(match)
    
    db.session.commit()
    print(f'✓ Added {len(matches)} sample matches')
EOF
```

---

## Troubleshooting

### Issue: "No module named 'app'"
**Fix:**
```bash
cd /home/Lilkolex/ABKBet
workon abkbet_env
python -c "import sys; print('\n'.join(sys.path))"
# Should see /home/Lilkolex/ABKBet in the path
```
Check WSGI file has correct path.

### Issue: "No module named 'flask'"
**Fix:**
```bash
workon abkbet_env
pip install -r requirements.txt
```

### Issue: "unable to open database file"
**Fix:**
```bash
cd /home/Lilkolex/ABKBet
ls -la instance/betting.db
# If file doesn't exist, run Step 5.2 again
chmod 664 instance/betting.db
```

### Issue: 500 Error on webpage
**Fix:** Check error log on Web tab for specific error message.

### Issue: Static files not loading (CSS/JS)
**Fix:** Verify Static files configuration on Web tab:
- URL: `/static/`
- Path: `/home/Lilkolex/ABKBet/static/`

---

## Quick Verification Script

Run this to verify everything is working:

```bash
cd /home/Lilkolex/ABKBet
workon abkbet_env

python << 'EOF'
import sys
print("="*60)
print("DEPLOYMENT VERIFICATION")
print("="*60)

# 1. Import test
try:
    from run import flask_app
    print("✓ App imports successfully")
except Exception as e:
    print(f"✗ App import failed: {e}")
    sys.exit(1)

# 2. Database test
from app import create_app, db
from app.models import User, Match, Bet

app = create_app('production')
with app.app_context():
    try:
        user_count = User.query.count()
        match_count = Match.query.count()
        bet_count = Bet.query.count()
        print(f"✓ Database accessible")
        print(f"  - Users: {user_count}")
        print(f"  - Matches: {match_count}")
        print(f"  - Bets: {bet_count}")
    except Exception as e:
        print(f"✗ Database error: {e}")
        sys.exit(1)

# 3. Routes test
routes = [str(r) for r in flask_app.url_map.iter_rules()]
critical_routes = [
    '/api/health',
    '/api/auth/login',
    '/api/bets/matches/manual'
]
print(f"✓ Routes registered: {len(routes)}")
for route in critical_routes:
    if any(route in r for r in routes):
        print(f"  ✓ {route}")
    else:
        print(f"  ✗ {route} MISSING")

print("="*60)
print("VERIFICATION COMPLETE")
print("="*60)
print("\nNext steps:")
print("1. Reload web app on Web tab")
print("2. Visit: https://lilkolex.pythonanywhere.com")
print("3. Login with: admin / admin123")
EOF
```

---

## Complete Checklist

- [ ] Backed up old database
- [ ] Deleted old files
- [ ] Uploaded new deployment package
- [ ] Extracted files to /home/Lilkolex/ABKBet
- [ ] Created virtual environment (abkbet_env)
- [ ] Installed requirements.txt
- [ ] Created/restored database
- [ ] Created database tables
- [ ] Configured WSGI file
- [ ] Set virtual environment path
- [ ] Configured static files
- [ ] Reloaded web app
- [ ] Checked error log (no errors)
- [ ] Tested health endpoint
- [ ] Tested login in browser
- [ ] Added sample matches
- [ ] Verified all features work

---

## Expected URLs After Deployment

| URL | Purpose |
|-----|---------|
| https://lilkolex.pythonanywhere.com | Main site |
| https://lilkolex.pythonanywhere.com/admin | Admin panel |
| https://lilkolex.pythonanywhere.com/premium_admin | Premium booking admin |
| https://lilkolex.pythonanywhere.com/api/health | Health check |
| https://lilkolex.pythonanywhere.com/api/bets/matches/manual | Match list |

---

## Post-Deployment Testing

1. **User Registration:**
   - Create new account
   - Verify email validation
   - Check starting balance

2. **Betting:**
   - Place single bet
   - Place multi bet
   - Check bet appears in "My Bets"

3. **Match Scores:**
   - Admin: Add match result
   - Verify score shows in user's bet ticket
   - Check settlement is correct (HOME/AWAY/DRAW logic)

4. **Premium Booking:**
   - Admin: Create booking code
   - User: Purchase booking
   - Verify selections unlock

5. **Balance:**
   - Check balance updates after bet
   - Check balance updates after settlement
   - Check balance updates after premium purchase

---

## Support

If you encounter issues:

1. Check error log (Web tab)
2. Run verification script above
3. Check that virtual environment is activated
4. Verify database file exists and is accessible
5. Test individual endpoints with curl

Database location: `/home/Lilkolex/ABKBet/instance/betting.db`
Virtual environment: `/home/Lilkolex/.virtualenvs/abkbet_env`
WSGI file: `/var/www/lilkolex_pythonanywhere_com_wsgi.py`
