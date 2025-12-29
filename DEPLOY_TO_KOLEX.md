# Deployment to PythonAnywhere - Kolex Account
**Username:** Kolex  
**URL:** https://kolex.pythonanywhere.com  
**Date:** December 6, 2025

---

## ✅ STEP 1: UPLOAD FILE (Already Done Locally!)

File created: **ABKBet_Production_Kolex.zip** (0.18 MB)  
Location: `C:\Users\HP\OneDrive\Documents\ABKBet\ABKBet_Production_Kolex.zip`

**Now upload to PythonAnywhere:**

1. Go to https://www.pythonanywhere.com
2. Login with your Kolex account
3. Click **Files** tab
4. Click **Upload a file** button
5. Select: `C:\Users\HP\OneDrive\Documents\ABKBet\ABKBet_Production_Kolex.zip`
6. Wait for upload (should be quick - only 0.18 MB)

✅ **Tell me when upload is complete!**

---

## STEP 2: OPEN BASH CONSOLE

1. Click **Consoles** tab
2. Click **Bash** (under "Start a new console")
3. A terminal will open

---

## STEP 3: EXTRACT FILES

**Copy and paste these commands into your Bash console:**

```bash
# Verify you're in the right place
pwd
# Should show: /home/Kolex

# Create project directory
mkdir -p ABKBet
cd ABKBet

# Extract the uploaded zip
unzip ~/ABKBet_Production_Kolex.zip

# Verify files extracted
ls -la

# You should see: app/ migrations/ static/ templates/ config.py run.py wsgi.py requirements.txt

# Clean up zip file
cd ~
rm ABKBet_Production_Kolex.zip

echo "✓ Files extracted successfully!"
```

✅ **Run these commands and tell me if you see all the folders!**

---

## STEP 4: CREATE VIRTUAL ENVIRONMENT

```bash
# Go to home directory
cd /home/Kolex

# Create Python 3.10 virtual environment
mkvirtualenv --python=/usr/bin/python3.10 abkbet_env

# Your prompt should now show (abkbet_env)
# If not, run: workon abkbet_env

# Upgrade pip
pip install --upgrade pip

# Install all dependencies
cd ABKBet
pip install -r requirements.txt
```

**This will take 2-3 minutes. You'll see packages installing.**

✅ **Tell me when installation completes!**

---

## STEP 5: CREATE DATABASE

```bash
# Make sure you're in ABKBet directory
cd /home/Kolex/ABKBet

# Make sure virtual environment is active
workon abkbet_env

# Create instance directory
mkdir -p instance

# Create database and users
python << 'EOF'
from app import create_app, db
from app.models import User
from app.utils.auth import hash_password

app = create_app('production')
with app.app_context():
    # Create all tables
    db.create_all()
    print('✓ Database tables created')
    
    # Create admin user
    admin = User(
        username='admin',
        email='admin@kolex.com',
        password_hash=hash_password('admin123'),
        balance=1000.0,
        is_admin=True,
        is_active=True
    )
    db.session.add(admin)
    
    # Create test user
    test_user = User(
        username='testuser',
        email='test@kolex.com',
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

**You should see:**
```
✓ Database tables created
✓ Admin user: admin / admin123
✓ Test user: testuser / test123
```

✅ **Tell me when you see this output!**

---

## STEP 6: CREATE WEB APP

1. Click **Web** tab in PythonAnywhere
2. Click **Add a new web app**
3. Click **Next** (to use kolex.pythonanywhere.com)
4. Choose **Manual configuration** (important!)
5. Select **Python 3.10**
6. Click **Next**

✅ **Tell me when web app is created!**

---

## STEP 7: CONFIGURE WSGI FILE

1. On **Web** tab, scroll to **Code** section
2. Click on WSGI file link (blue link that says `/var/www/kolex_pythonanywhere_com_wsgi.py`)
3. **DELETE EVERYTHING** in that file
4. **Paste this EXACT code:**

```python
import sys
import os

# Add project directory to path
project_home = '/home/Kolex/ABKBet'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Set environment variables
os.environ['FLASK_ENV'] = 'production'
os.environ['SECRET_KEY'] = 'kolex-secret-key-2024-change-later'
os.environ['JWT_SECRET_KEY'] = 'kolex-jwt-secret-2024-change-later'
os.environ['FOOTBALL_API_KEY'] = '8a0943a24d4c44f4f5d8a091f6348e9f'
os.environ['FOOTBALL_API_ENABLED'] = 'true'

# Import Flask app
from run import flask_app as application
```

5. Click **Save** (top right)

✅ **Tell me when WSGI file is saved!**

---

## STEP 8: SET VIRTUAL ENVIRONMENT

1. Still on **Web** tab
2. Scroll to **Virtualenv** section
3. In the text box, enter: `/home/Kolex/.virtualenvs/abkbet_env`
4. Click the **checkmark** button ✓
5. Path should appear in green

✅ **Tell me when virtualenv is set!**

---

## STEP 9: CONFIGURE STATIC FILES

1. Still on **Web** tab
2. Scroll to **Static files** section
3. Click **Enter URL** and type: `/static/`
4. Click **Enter path** and type: `/home/Kolex/ABKBet/static/`
5. Click checkmark ✓

✅ **Tell me when static files configured!**

---

## STEP 10: RELOAD WEB APP

1. Scroll to TOP of **Web** tab
2. Click big green **Reload kolex.pythonanywhere.com** button
3. Wait 10 seconds

✅ **Tell me when reload completes!**

---

## STEP 11: TEST YOUR SITE!

**Open in browser:** https://kolex.pythonanywhere.com

**You should see:** ABKBet homepage with betting interface

**Test login:**
- Username: `testuser`
- Password: `test123`

**Test admin:**
- Go to: https://kolex.pythonanywhere.com/secure-admin-access-2024
- Username: `admin`
- Password: `admin123`

---

## 🎉 IF EVERYTHING WORKS:

Congratulations! Your site is live at:
- **Main Site:** https://kolex.pythonanywhere.com
- **Admin Login:** https://kolex.pythonanywhere.com/secure-admin-access-2024

---

## ❌ IF YOU SEE ERRORS:

1. Go to **Web** tab
2. Click **Error log** (near bottom)
3. Copy the last 20 lines
4. Send them to me and I'll help fix it!

---

## OPTIONAL: Add Sample Data

If you want to add sample matches for testing:

```bash
cd /home/Kolex/ABKBet
workon abkbet_env

python << 'EOF'
from app import create_app, db
from app.models import Match
from datetime import datetime, timedelta

app = create_app('production')
with app.app_context():
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
    print(f'✓ Added {len(matches)} matches')
EOF
```

---

## 📝 QUICK REFERENCE

**Your URLs:**
- Site: https://kolex.pythonanywhere.com
- Admin: https://kolex.pythonanywhere.com/secure-admin-access-2024

**Test Accounts:**
- Admin: admin / admin123
- User: testuser / test123

**Important Paths:**
- Project: `/home/Kolex/ABKBet`
- Virtual Env: `/home/Kolex/.virtualenvs/abkbet_env`
- Database: `/home/Kolex/ABKBet/instance/betting.db`
- WSGI: `/var/www/kolex_pythonanywhere_com_wsgi.py`

---

**Ready? Start with uploading the ZIP file and let me know your progress!** 🚀
