# IMMEDIATE ACTION PLAN - Fix PythonAnywhere Login & Match Loading

## Problem Summary
- Login fails on lilkolex.pythonanywhere.com
- Error: "Error loading matches: Error: Error fetching matches"
- Frontend loads but API calls fail

## Most Likely Causes (In Order)
1. **WSGI configuration has wrong username** (was YOUR_USERNAME, needs Lilkolex)
2. **Database tables don't exist** (need to run db.create_all())
3. **Virtual environment not configured** in Web tab
4. **Import error** preventing app from starting

## 3-Minute Quick Fix

### 1. Update WSGI File (2 minutes)
**Location:** PythonAnywhere Web tab -> WSGI configuration file link

Replace line 9 with:
```python
project_home = '/home/Lilkolex/ABKBet'
```

Save the file.

### 2. Check Virtual Environment (30 seconds)
**Location:** PythonAnywhere Web tab -> Virtualenv section

Should show: `/home/Lilkolex/venv`

If empty or different, type `/home/Lilkolex/venv` and click checkmark.

### 3. Reload App (30 seconds)
Click the big green **"Reload"** button on Web tab.

### 4. Test (30 seconds)
Visit: https://lilkolex.pythonanywhere.com

If still broken, check Error log (link on Web tab) and proceed to full fix below.

---

## Full Fix (If Quick Fix Doesn't Work)

### Option A: Use Bash Console (Recommended)

```bash
# 1. Navigate and activate environment
cd /home/Lilkolex/ABKBet
source ~/venv/bin/activate

# 2. Test if app imports
python -c "from run import flask_app; print('App OK')" || echo "IMPORT FAILED"

# 3. If import failed, check error:
python -c "from run import flask_app" 2>&1 | tail -20

# 4. Install/update dependencies if needed
pip install --upgrade -r requirements.txt

# 5. Create database tables
python << 'EOF'
from app import create_app, db
app = create_app('production')
with app.app_context():
    db.create_all()
    print('Tables created')
EOF

# 6. Verify
python -c "from app import create_app, db; from app.models import Match; app=create_app('production'); app.app_context().push(); print(f'Matches in DB: {Match.query.count()}')"
```

After running these, reload the web app and test.

### Option B: Upload New Package

1. **Upload** `ABKBet_Complete_Fixed_20251205_001946.zip` to PythonAnywhere
2. **Extract:**
   ```bash
   cd /home/Lilkolex
   mv ABKBet ABKBet_old_backup
   unzip ABKBet_Complete_Fixed_20251205_001946.zip -d ABKBet
   cd ABKBet
   ```
3. **Run quick fix script:**
   ```bash
   source ~/venv/bin/activate
   bash quick_fix.sh
   ```
4. **Reload** web app
5. **Test** site

---

## Diagnostic Commands

If you need to troubleshoot further:

```bash
# Check current WSGI path
grep "project_home" /var/www/lilkolex_pythonanywhere_com_wsgi.py

# Check if venv has Flask
source ~/venv/bin/activate
pip list | grep -i flask

# Check database file
ls -lh /home/Lilkolex/ABKBet/instance/betting.db

# List all tables
python -c "from app import create_app, db; from sqlalchemy import inspect; app=create_app('production'); app.app_context().push(); print(inspect(db.engine).get_table_names())"

# Check routes
python -c "from run import flask_app; print('\n'.join(sorted([str(r) for r in flask_app.url_map.iter_rules() if 'auth' in str(r) or 'bets' in str(r)])))"
```

---

## Expected Results After Fix

✓ **Health endpoint works:**
```bash
curl https://lilkolex.pythonanywhere.com/api/health
# Should return: {"status":"healthy"}
```

✓ **Matches endpoint works:**
```bash
curl https://lilkolex.pythonanywhere.com/api/bets/matches/manual
# Should return: {"matches":[...]}
```

✓ **Login works:**
```bash
curl -X POST https://lilkolex.pythonanywhere.com/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"testpass"}'
# Should return: {"message":"Invalid credentials"} (which means endpoint is working)
```

✓ **Browser console shows no errors**

✓ **Can login and see matches**

---

## If Still Not Working

**Check Error Log:**
Web tab -> Click "Error log" link -> Look for most recent error

**Common errors and fixes:**

| Error | Fix |
|-------|-----|
| `No module named 'app'` | Fix WSGI file path |
| `No module named 'flask'` | Install requirements in venv |
| `No such table: users` | Run db.create_all() |
| `unable to open database` | Create instance folder, set permissions |
| `CORS error` | Already fixed in code, just reload |

**Share the error log output** if you're still stuck - it will show exactly what's wrong.

---

## Files Included in New Package

- `wsgi.py` - Fixed with correct username (Lilkolex)
- `check_deployment.py` - Comprehensive diagnostic tool
- `quick_fix.sh` - Automated fix script
- `ERROR_FIX_GUIDE.md` - Detailed troubleshooting
- `fix_pythonanywhere.md` - Step-by-step instructions
- All app files with latest fixes

---

## Next Steps After Login Works

1. **Add matches** via admin panel
2. **Test bet placement** and settlement
3. **Test premium booking system**
4. **Verify match scores** display correctly
5. **Check that settlement logic** handles HOME/AWAY/DRAW correctly

The core bugs (settlement, match linking, selection storage) are already fixed in the code. Once the deployment is working, everything should function properly.
