# Deployment to PythonAnywhere - ABKBet Account
**Username:** ABKBet  
**URL:** https://abkbet.pythonanywhere.com  
**Date:** December 6, 2025

---

## ✅ STEP 1: UPLOAD FILE

File ready: **ABKBet_Production_Kolex.zip** (0.18 MB)  
Location: `C:\Users\HP\OneDrive\Documents\ABKBet\ABKBet_Production_Kolex.zip`

**Upload to PythonAnywhere:**

1. Go to https://www.pythonanywhere.com
2. Login with your **ABKBet** account
3. Click **Files** tab
4. Click **Upload a file** button
5. Select: `C:\Users\HP\OneDrive\Documents\ABKBet\ABKBet_Production_Kolex.zip`
6. Wait for upload

✅ **Tell me when upload is complete!**

---

## STEP 2: EXTRACT FILES

1. Click **Consoles** tab
2. Click **Bash**
3. Run these commands:

```bash
pwd
mkdir -p ABKBet
cd ABKBet
unzip ~/ABKBet_Production_Kolex.zip
ls -la
cd ~
rm ABKBet_Production_Kolex.zip
echo "✓ Files extracted!"
```

✅ **Tell me when you see the folders!**

---

## STEP 3: CREATE VIRTUAL ENVIRONMENT

```bash
cd /home/ABKBet
mkvirtualenv --python=/usr/bin/python3.10 abkbet_env
pip install --upgrade pip
cd ABKBet
pip install -r requirements.txt
```

Wait 2-3 minutes for installation.

✅ **Tell me when you see (abkbet_env) in your prompt!**

---

## STEP 4: CREATE DATABASE

```bash
mkdir -p instance
python << 'EOF'
from app import create_app, db
from app.models import User
from app.utils.auth import hash_password

app = create_app('production')
with app.app_context():
    db.create_all()
    print('✓ Database tables created')
    
    admin = User(
        username='admin',
        email='admin@abkbet.com',
        password_hash=hash_password('admin123'),
        balance=1000.0,
        is_admin=True,
        is_active=True
    )
    db.session.add(admin)
    
    test_user = User(
        username='testuser',
        email='test@abkbet.com',
        password_hash=hash_password('test123'),
        balance=100.0,
        is_active=True
    )
    db.session.add(test_user)
    
    db.session.commit()
    print('✓ Admin user: admin / admin123')
    print('✓ Test user: testuser / test123')
EOF
```

✅ **Tell me when you see the success messages!**

---

## STEP 5: CREATE WEB APP

1. Go to **Web** tab
2. Click **Add a new web app**
3. Click **Next**
4. Choose **Manual configuration**
5. Select **Python 3.10**
6. Click **Next**

✅ **Tell me when done!**

---

## STEP 6: CONFIGURE WSGI FILE

1. On **Web** tab, find **Code** section
2. Click the WSGI file link: `/var/www/abkbet_pythonanywhere_com_wsgi.py`
3. **DELETE EVERYTHING**
4. **Paste this:**

```python
import sys
import os

# Add project directory to path
project_home = '/home/ABKBet/ABKBet'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Set environment variables
os.environ['FLASK_ENV'] = 'production'
os.environ['SECRET_KEY'] = 'abkbet-secret-key-2024-change-later'
os.environ['JWT_SECRET_KEY'] = 'abkbet-jwt-secret-2024-change-later'
os.environ['FOOTBALL_API_KEY'] = '8a0943a24d4c44f4f5d8a091f6348e9f'
os.environ['FOOTBALL_API_ENABLED'] = 'true'

# Import Flask app
from run import flask_app as application
```

5. Click **Save**

✅ **Tell me when saved!**

---

## STEP 7: SET VIRTUAL ENVIRONMENT

1. On **Web** tab, scroll to **Virtualenv** section
2. Enter: `/home/ABKBet/.virtualenvs/abkbet_env`
3. Click checkmark ✓

✅ **Tell me when you see it in green!**

---

## STEP 8: CONFIGURE STATIC FILES

1. Still on **Web** tab
2. Find **Static files** section
3. URL: `/static/`
4. Path: `/home/ABKBet/ABKBet/static/`
5. Click checkmark ✓

✅ **Tell me when done!**

---

## STEP 9: RELOAD WEB APP

1. Scroll to TOP of **Web** tab
2. Click big green **Reload abkbet.pythonanywhere.com** button
3. Wait 10 seconds

✅ **Tell me when reloaded!**

---

## STEP 10: TEST YOUR SITE! 🎉

**Open:** https://abkbet.pythonanywhere.com

**Test login:**
- Username: `testuser`
- Password: `test123`

**Test admin:**
- Go to: https://abkbet.pythonanywhere.com/secure-admin-access-2024
- Username: `admin`
- Password: `admin123`

---

## 🎉 YOUR LIVE SITE:

- **Main:** https://abkbet.pythonanywhere.com
- **Admin:** https://abkbet.pythonanywhere.com/secure-admin-access-2024

---

## ❌ IF ERRORS:

Check **Error log** on Web tab and send me last 20 lines!

---

**Ready? Start by uploading the ZIP file!** 🚀
