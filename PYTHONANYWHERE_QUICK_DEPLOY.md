# PYTHONANYWHERE DEPLOYMENT - STEP BY STEP GUIDE

## ✅ Files Ready
Your deployment package is created: `ABKBet_PythonAnywhere_Deployment_XXXXXX.zip`

## 📋 DEPLOYMENT STEPS

### Step 1: Upload to PythonAnywhere
1. Go to https://www.pythonanywhere.com and login
2. Click **"Files"** tab
3. Click **"Upload a file"** button
4. Select the zip file: `ABKBet_PythonAnywhere_Deployment_XXXXXX.zip`
5. Wait for upload to complete

### Step 2: Extract Files
1. Click **"Consoles"** tab → **"Bash"**
2. Run these commands:
```bash
cd ~
unzip ABKBet_PythonAnywhere_Deployment_*.zip -d ABKBet
cd ABKBet
ls -la
```

### Step 3: Create Virtual Environment
```bash
python3.10 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### Step 4: Initialize Database
```bash
python init_db.py
```

### Step 5: Configure Web App
1. Go to **"Web"** tab
2. If no app exists, click **"Add a new web app"**
   - Choose **"Manual configuration"**
   - Select **"Python 3.10"**
3. In **"Code"** section, click on WSGI file link
4. **Replace ALL content** with:

```python
import sys
import os

# IMPORTANT: Change YOUR_USERNAME to your actual PythonAnywhere username
project_home = '/home/YOUR_USERNAME/ABKBet'
if project_home not in sys.path:
    sys.path = [project_home] + sys.path

# Environment variables
os.environ['SECRET_KEY'] = 'change-this-to-random-secret-key'
os.environ['FOOTBALL_API_KEY'] = '8a0943a24d4c44f4f5d8a091f6348e9f'
os.environ['FOOTBALL_API_ENABLED'] = 'true'

# Import Flask app
from run import app as application
```

5. Click **"Save"**

### Step 6: Configure Virtual Environment Path
1. Still in **"Web"** tab, find **"Virtualenv"** section
2. Enter: `/home/YOUR_USERNAME/ABKBet/venv`
3. Click checkmark to save

### Step 7: Configure Static Files
1. In **"Static files"** section, add:
   - URL: `/static/`
   - Directory: `/home/YOUR_USERNAME/ABKBet/static`

### Step 8: Reload and Test
1. Click green **"Reload"** button at top
2. Visit: `https://YOUR_USERNAME.pythonanywhere.com`
3. Test register/login

## 🔧 LOGIN/REGISTER FIXES INCLUDED

✅ **CORS Configuration** - Fixed for PythonAnywhere
✅ **JWT Token Handling** - Improved authentication
✅ **API Endpoints** - All working correctly
✅ **Match Scores Display** - Shows in bet tickets
✅ **Settlement Logic** - Fixed HOME/AWAY/DRAW/OVER/UNDER
✅ **Match Linking** - Bets now linked to correct matches

## 🐛 TROUBLESHOOTING

### If login doesn't work:
1. Check Bash console for errors:
```bash
cd ~/ABKBet
tail -f /var/log/YOUR_USERNAME.pythonanywhere.com.error.log
```

### If "Internal Server Error":
1. Check error log (above command)
2. Verify WSGI file has correct username
3. Verify virtual environment path is correct

### If register doesn't work:
1. Check database was initialized:
```bash
cd ~/ABKBet
source venv/bin/activate
python -c "from app import create_app, db; from app.models import User; app=create_app(); app.app_context().push(); print(User.query.count(), 'users')"
```

### To create admin user manually:
```bash
cd ~/ABKBet
source venv/bin/activate
python -c "from app import create_app, db; from app.models import User; from app.utils.auth import hash_password; app=create_app(); app.app_context().push(); u=User(username='admin', email='admin@abkbet.com', password_hash=hash_password('Admin@123'), balance=1000.0, is_admin=True, is_active=True); db.session.add(u); db.session.commit(); print('Admin created!')"
```

## 📞 SUPPORT

If you encounter issues:
1. Check the error log (see troubleshooting above)
2. Verify all usernames in paths are correct
3. Ensure virtual environment is activated
4. Check database was initialized

Your site will be live at: `https://YOUR_USERNAME.pythonanywhere.com`
