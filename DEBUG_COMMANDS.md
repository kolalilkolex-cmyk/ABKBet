# 🔍 DEBUG COMMANDS - Fix "Something went wrong" Error

## Step 1: Check Error Logs (MOST IMPORTANT)

Open PythonAnywhere Bash Console and run:

```bash
cd /home/Lilkolex/ABKBet

# Check the error log (last 50 lines)
tail -n 50 /var/log/Lilkolex.pythonanywhere.com.error.log
```

**Look for:**
- `ImportError` - Missing import or wrong module name
- `SyntaxError` - Typo in Python code
- `AttributeError` - Missing function or variable
- `NameError` - Undefined variable

---

## Step 2: Verify Files Were Uploaded

```bash
cd /home/Lilkolex/ABKBet

# Check if files exist and their sizes
ls -lh app/services/virtual_game_service.py
ls -lh app/routes/virtual_game_routes.py
ls -lh templates/admin.html
ls -lh templates/index.html
```

**Expected sizes (approximately):**
- virtual_game_service.py: ~18-20 KB
- virtual_game_routes.py: ~20-22 KB
- admin.html: ~120-130 KB
- index.html: ~280-300 KB

---

## Step 3: Test Python Imports

```bash
cd /home/Lilkolex/ABKBet
source venv/bin/activate

# Test if virtual game imports work
python -c "from app.services.virtual_game_service import VirtualGameService; print('✅ Service OK')"

# Test if routes import works
python -c "from app.routes.virtual_game_routes import virtual_game_bp; print('✅ Routes OK')"

# Test if models work
python -c "from app.models.virtual_game import VirtualLeague, VirtualTeam, VirtualGame; print('✅ Models OK')"
```

---

## Step 4: Check Python Syntax

```bash
cd /home/Lilkolex/ABKBet

# Check for syntax errors
python -m py_compile app/services/virtual_game_service.py
python -m py_compile app/routes/virtual_game_routes.py
```

If no output = good. If error = syntax problem.

---

## Step 5: Check Flask App

```bash
cd /home/Lilkolex/ABKBet
source venv/bin/activate

# Test if Flask app loads
python -c "from run import flask_app; print('Blueprints:', list(flask_app.blueprints.keys()))"
```

**Should show:** `['auth', 'main', 'admin', 'premium', 'virtual_game', ...]`

---

## Common Errors & Quick Fixes

### Error: "ImportError: cannot import name 'virtual_game_bp'"

**Fix:**
```bash
# Check if routes file exists
cat app/routes/virtual_game_routes.py | head -20

# If empty or wrong, re-upload the file
```

### Error: "AttributeError: module 'app.services.virtual_game_service' has no attribute 'clear_all_games'"

**Fix:** Old version of file uploaded. Re-upload `virtual_game_service.py`

### Error: "SyntaxError" in admin.html

**Fix:** Re-upload `admin.html`

### Error: "NameError: name 'virtual_game_service' is not defined"

**Fix:** Missing import in routes. Check line 12-15 of `virtual_game_routes.py`

---

## Quick Fix: Restore & Retry

If you're not sure what went wrong:

```bash
cd /home/Lilkolex/ABKBet

# 1. Remove the problematic files (if you have backups)
# mv app/services/virtual_game_service.py app/services/virtual_game_service.py.broken
# mv app/routes/virtual_game_routes.py app/routes/virtual_game_routes.py.broken

# 2. Re-upload ONLY these 2 files first:
#    - app/services/virtual_game_service.py
#    - app/routes/virtual_game_routes.py

# 3. Test imports
python -c "from app.services.virtual_game_service import VirtualGameService; from app.routes.virtual_game_routes import virtual_game_bp; print('✅ OK')"

# 4. If OK, reload web app on PythonAnywhere Web tab

# 5. Then upload admin.html and index.html
```

---

## Emergency Rollback

If nothing works, restore old versions:

```bash
cd /home/Lilkolex/ABKBet

# If you made backups
cp app/services/virtual_game_service.py.backup app/services/virtual_game_service.py
cp app/routes/virtual_game_routes.py.backup app/routes/virtual_game_routes.py
cp templates/admin.html.backup templates/admin.html
cp templates/index.html.backup templates/index.html

# Reload web app
# Then check if admin works
```

---

## What to Send Me

Run this command and copy the output:

```bash
cd /home/Lilkolex/ABKBet
tail -n 30 /var/log/Lilkolex.pythonanywhere.com.error.log
```

This will show me the exact error so I can provide specific fix.

---

## Likely Issues

Based on "Something went wrong" error:

1. **Most Likely:** Syntax error in one of the Python files
2. **Very Likely:** Import error - file not uploaded or wrong location
3. **Possible:** Missing function in service file
4. **Possible:** Blueprint not registered in run.py

**Next Steps:**
1. Run Step 1 (check error log) - This is CRITICAL
2. Copy the error message
3. Share it with me
4. I'll provide exact fix

---

## Quick Health Check

Run this one command to check everything:

```bash
cd /home/Lilkolex/ABKBet
source venv/bin/activate

echo "=== CHECKING FILES ==="
ls -lh app/services/virtual_game_service.py app/routes/virtual_game_routes.py 2>&1

echo -e "\n=== CHECKING IMPORTS ==="
python -c "
try:
    from app.services.virtual_game_service import VirtualGameService
    print('✅ Service import OK')
except Exception as e:
    print('❌ Service import FAIL:', e)

try:
    from app.routes.virtual_game_routes import virtual_game_bp
    print('✅ Routes import OK')
except Exception as e:
    print('❌ Routes import FAIL:', e)
" 2>&1

echo -e "\n=== CHECKING ERROR LOG ==="
tail -n 20 /var/log/Lilkolex.pythonanywhere.com.error.log
```

**Copy ALL the output and send it to me.**
