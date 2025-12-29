# 🔧 Debugging Deployment Error

## Error: "Something went wrong" on PythonAnywhere

This usually means there's a Python error preventing the app from starting. Here's how to fix it:

---

## 🔍 Step 1: Check Error Logs

### Option A: Via PythonAnywhere Dashboard
1. Go to **Web** tab
2. Scroll down to **Log files** section
3. Click on **Error log** (red link)
4. Look at the **last 20-30 lines** for the actual error

### Option B: Via Files Tab
1. Go to **Files** tab
2. Navigate to `/var/log/`
3. Open your error log file (usually `yourusername.pythonanywhere.com.error.log`)

---

## 🚨 Common Errors & Fixes

### Error 1: ImportError (Blueprint Registration)
```
ImportError: cannot import name 'dice_bp' from 'app.routes.dice_routes'
```

**Fix**: Check that all route files have the blueprint export at the bottom:

**dice_routes.py** should have:
```python
dice_bp = Blueprint('dice', __name__)
# ... routes ...
```

**run.py** should import:
```python
from app.routes.dice_routes import dice_bp
from app.routes.mines_routes import mines_bp
from app.routes.plinko_routes import plinko_bp
```

---

### Error 2: SyntaxError
```
SyntaxError: invalid syntax (line X)
```

**Fix**: This means there's a typo in one of the Python files. The error will tell you:
- Which file
- Which line number
- What the problem is

Common issues:
- Missing colons `:` at end of function definitions
- Mismatched parentheses/brackets
- Incorrect indentation

---

### Error 3: ModuleNotFoundError
```
ModuleNotFoundError: No module named 'secrets'
```

**Fix**: Missing import. Add to top of file:
```python
import secrets
import hashlib
```

---

### Error 4: Database Connection Error
```
sqlalchemy.exc.OperationalError: unable to open database file
```

**Fix**: Database path issue. Check `config.py`:
```python
SQLALCHEMY_DATABASE_URI = 'sqlite:///abkbet.db'
# NOT: 'sqlite:////full/path/to/abkbet.db'
```

---

## 🛠️ Quick Fix Checklist

### 1. Verify All Files Uploaded
Go to **Files** tab and confirm these exist:
- ✅ `app/routes/dice_routes.py`
- ✅ `app/routes/mines_routes.py`
- ✅ `app/routes/plinko_routes.py`
- ✅ `run.py` (updated)
- ✅ `templates/index.html` (updated)

### 2. Check run.py Blueprint Registration
Make sure `run.py` has these lines (around line 49-74):

```python
# Import game blueprints
from app.routes.crash_routes import crash_bp
from app.routes.dice_routes import dice_bp
from app.routes.mines_routes import mines_bp
from app.routes.plinko_routes import plinko_bp

# Register game blueprints
app.register_blueprint(crash_bp, url_prefix='/api/crash')
app.register_blueprint(dice_bp, url_prefix='/api/dice')
app.register_blueprint(mines_bp, url_prefix='/api/mines')
app.register_blueprint(plinko_bp, url_prefix='/api/plinko')
```

### 3. Verify Blueprint Definitions
Each route file should end with:

**dice_routes.py:**
```python
dice_bp = Blueprint('dice', __name__)
```

**mines_routes.py:**
```python
mines_bp = Blueprint('mines', __name__)
```

**plinko_routes.py:**
```python
plinko_bp = Blueprint('plinko', __name__)
```

---

## 🔄 If Blueprint Variable Names Don't Match

### Problem
If the route files use different variable names, you'll get import errors.

### Solution
Check each route file. Look at the **VERY LAST LINE** or near the top for:

```python
# Could be named:
bp = Blueprint('dice', __name__)  # ❌ Wrong variable name
dice_bp = Blueprint('dice', __name__)  # ✅ Correct
dice_blueprint = Blueprint('dice', __name__)  # ❌ Wrong
```

### If They Use Different Names
**Option 1** (Recommended): Change the import in run.py to match:
```python
# If dice_routes.py has: bp = Blueprint('dice', __name__)
from app.routes.dice_routes import bp as dice_bp
from app.routes.mines_routes import bp as mines_bp
from app.routes.plinko_routes import bp as plinko_bp
```

**Option 2**: Edit each route file to use consistent names (dice_bp, mines_bp, plinko_bp)

---

## 📝 Step-by-Step Debug Process

### 1. Get the Error Message
- Open error log
- Copy the **last error** (bottom of file)
- Look for lines starting with `Traceback` or `Error:`

### 2. Identify the Problem File
The error will show something like:
```
File "/home/username/mysite/app/routes/dice_routes.py", line 45
```

This tells you:
- **File**: dice_routes.py
- **Line**: 45

### 3. Check That Line
- Go to Files tab
- Open the file
- Jump to that line number
- Look for syntax errors

### 4. Common Fixes
- **Missing colon**: Add `:` at end of `def` or `if` statements
- **Wrong indentation**: Use 4 spaces consistently
- **Unclosed brackets**: Count `(` and `)`, `{` and `}`, `[` and `]`
- **Missing import**: Add import at top of file

### 5. Save & Reload
- Save the fixed file
- Go to **Web** tab
- Click green **Reload** button
- Check site again

---

## 🎯 Most Likely Issue

Based on the files we created, the most common issue is:

### Blueprint Variable Name Mismatch

The route files I created define blueprints like this:
```python
# At the TOP of each file (after imports)
dice_bp = Blueprint('dice', __name__)
```

But if they're defined at the **bottom**, they might use just `bp`:
```python
bp = Blueprint('dice', __name__)
```

**Quick Fix**: Check the actual variable names in each route file, then update run.py accordingly.

---

## 🆘 If You Still Need Help

**Send me these 3 things:**

1. **Last 30 lines of error log** (copy from error log file)
2. **First 10 lines of dice_routes.py** (to see how blueprint is defined)
3. **Lines 45-75 of run.py** (to see blueprint imports/registration)

With this info, I can give you the exact fix!

---

## 🚀 After Fixing

Once the error is fixed:
1. Click **Reload** on Web tab
2. Clear browser cache (Ctrl+Shift+R)
3. Visit site
4. Login
5. Test all 4 games (Crash, Dice, Mines, Plinko)

---

## 💡 Pro Tip

Before uploading in the future:
1. Test locally first (`python run.py`)
2. Check for syntax errors
3. Verify all imports work
4. Then upload to PythonAnywhere

This catches most errors before deployment!
