# Specific Fix for Login and Match Loading Errors

## Your Current Errors

```
Login failed. Error loading matches: Error: Error fetching matches
request https://lilkolex.pythonanywhere.com/static/abkbet-client.js?v=2:59
```

## Root Cause Analysis

The error is happening because:
1. The frontend is successfully loading but API calls are failing
2. This suggests the Flask app is not running or routes are not registered
3. Most likely cause: WSGI configuration error or missing dependencies

## Immediate Fix Steps

### Step 1: Upload Fixed Files
You have a new deployment package: `ABKBet_Fixed_20251205_001756.zip`

Upload this to PythonAnywhere:
```bash
# On PythonAnywhere Bash console
cd /home/Lilkolex
wget YOUR_FILE_URL/ABKBet_Fixed_20251205_001756.zip
# OR use the Files tab to upload

# Backup current deployment
mv ABKBet ABKBet_backup_old

# Extract new files
unzip ABKBet_Fixed_20251205_001756.zip -d ABKBet
cd ABKBet
```

### Step 2: Update WSGI Configuration
Go to Web tab -> Click on WSGI configuration file

Replace the ENTIRE content with:

```python
import sys
import os

# Add project directory to path
project_home = '/home/Lilkolex/ABKBet'
if project_home not in sys.path:
    sys.path = [project_home] + sys.path

# Load environment variables
from dotenv import load_dotenv
env_path = os.path.join(project_home, '.env')
load_dotenv(env_path)

# Set environment variables
os.environ.setdefault('SECRET_KEY', 'your-secret-key-here-change-in-production')
os.environ.setdefault('FLASK_ENV', 'production')
os.environ.setdefault('FOOTBALL_API_KEY', '8a0943a24d4c44f4f5d8a091f6348e9f')
os.environ.setdefault('FOOTBALL_API_ENABLED', 'true')

# Import and configure app
from run import flask_app as application

# This makes the app available to PythonAnywhere
```

Click Save, then close the file.

### Step 3: Run Diagnostic Script
In Bash console:

```bash
cd /home/Lilkolex/ABKBet
source ~/venv/bin/activate

# Make script executable
chmod +x quick_fix.sh

# Run it
bash quick_fix.sh
```

This will:
- ✓ Check if app can be imported
- ✓ Verify database tables exist
- ✓ Create missing tables if needed
- ✓ Check if routes are registered
- ✓ Test database connections

### Step 4: Install Missing Dependencies (if needed)
```bash
cd /home/Lilkolex/ABKBet
source ~/venv/bin/activate
pip install --upgrade -r requirements.txt
```

### Step 5: Verify Database
```bash
cd /home/Lilkolex/ABKBet
source ~/venv/bin/activate

# Check if database is accessible
python -c "
from app import create_app, db
from app.models import Match, User
app = create_app('production')
with app.app_context():
    print(f'Users: {User.query.count()}')
    print(f'Matches: {Match.query.count()}')
"
```

If you see "No such table" error, create tables:

```bash
python << 'EOF'
from app import create_app, db
app = create_app('production')
with app.app_context():
    db.create_all()
    print('All tables created successfully')
EOF
```

### Step 6: Check Virtual Environment in Web Tab
1. Go to Web tab
2. Under "Virtualenv" section
3. Make sure it shows: `/home/Lilkolex/venv`
4. If not, enter that path and click the checkmark

### Step 7: Reload Web App
1. Web tab -> Click green "Reload" button
2. Wait 10 seconds
3. Click "Error log" link to check for errors

### Step 8: Test Endpoints

In your browser console (F12):

```javascript
// Test 1: Health check
fetch('https://lilkolex.pythonanywhere.com/api/health')
  .then(r => r.json())
  .then(d => console.log('Health:', d))
  .catch(e => console.error('Health failed:', e))

// Test 2: Matches (this is what's failing)
fetch('https://lilkolex.pythonanywhere.com/api/bets/matches/manual')
  .then(r => r.json())
  .then(d => console.log('Matches:', d))
  .catch(e => console.error('Matches failed:', e))

// Test 3: Login
fetch('https://lilkolex.pythonanywhere.com/api/auth/login', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({username: 'testuser', password: 'testpass'})
})
  .then(r => r.json())
  .then(d => console.log('Login response:', d))
  .catch(e => console.error('Login failed:', e))
```

## Common Causes and Solutions

### Cause 1: WSGI file points to wrong directory
**Symptom:** "No module named 'app'" or "No module named 'run'"
**Solution:** Update WSGI file as shown in Step 2 above

### Cause 2: Virtual environment not set correctly
**Symptom:** "No module named 'flask'" or import errors
**Solution:** 
- Web tab -> Set virtualenv to `/home/Lilkolex/venv`
- Reinstall requirements: `pip install -r requirements.txt`

### Cause 3: Database tables don't exist
**Symptom:** "no such table: matches" or "no such table: users"
**Solution:** Run `db.create_all()` as shown in Step 5

### Cause 4: Database file not accessible
**Symptom:** "unable to open database file"
**Solution:**
```bash
mkdir -p /home/Lilkolex/ABKBet/instance
chmod 755 /home/Lilkolex/ABKBet/instance
# If database file exists elsewhere, copy it:
cp /home/Lilkolex/betting.db /home/Lilkolex/ABKBet/instance/
chmod 664 /home/Lilkolex/ABKBet/instance/betting.db
```

### Cause 5: Old Python bytecode cached
**Symptom:** Changes not taking effect after reload
**Solution:**
```bash
cd /home/Lilkolex/ABKBet
find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null
find . -name "*.pyc" -delete
```

## Verification Checklist

After completing all steps, verify:

- [ ] WSGI file has correct path: `/home/Lilkolex/ABKBet`
- [ ] Virtual environment is set: `/home/Lilkolex/venv`
- [ ] Requirements installed: `pip list | grep Flask` shows Flask 2.3.3
- [ ] Database exists: `ls -lh instance/betting.db` shows file
- [ ] Tables created: Check with `python check_deployment.py`
- [ ] App imports: `python -c "from run import flask_app; print('OK')"`
- [ ] Error log is clean (no Python errors)
- [ ] Server log shows app startup
- [ ] Health endpoint works: `/api/health` returns `{"status":"healthy"}`
- [ ] Matches endpoint works: `/api/bets/matches/manual` returns matches
- [ ] Login endpoint works: `/api/auth/login` accepts credentials

## Still Not Working?

If after all these steps it still doesn't work:

1. **Check the error log:**
   - Web tab -> Error log link
   - Look for the most recent error
   - Share the error message

2. **Check the server log:**
   - Web tab -> Server log link  
   - Look for startup messages
   - Should see "Application created with config: production"

3. **Run the check_deployment.py script:**
   ```bash
   cd /home/Lilkolex/ABKBet
   source ~/venv/bin/activate
   python check_deployment.py
   ```
   Share the output.

4. **Test app manually:**
   ```bash
   python -c "from run import flask_app; print([str(r) for r in flask_app.url_map.iter_rules() if 'bets' in str(r)])"
   ```
   This should show the /api/bets/* routes.
