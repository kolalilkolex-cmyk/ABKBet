# Complete PythonAnywhere Deployment Guide
## Fresh Account Setup - Step by Step

**Date:** December 6, 2025
**Purpose:** Deploy ABKBet to new PythonAnywhere account for user testing

---

## 📋 Pre-Deployment Checklist

Before starting, make sure you have:
- ✅ New PythonAnywhere account created
- ✅ PythonAnywhere username (we'll need this)
- ✅ Verified email address
- ✅ Local project working correctly

---

## STEP 1: Get Your PythonAnywhere Username (1 minute)

1. Log in to https://www.pythonanywhere.com
2. Look at the top right corner - your username is displayed there
3. Your site URL will be: `https://YOUR-USERNAME.pythonanywhere.com`
4. **Write down your username here:** _________________

---

## STEP 2: Prepare Deployment Files (5 minutes)

We need to create a deployment package with all necessary files.

### Files to Include:
```
ABKBet/
├── app/                    (entire folder)
├── migrations/             (entire folder)
├── static/                 (entire folder)
├── templates/              (entire folder)
├── config.py
├── run.py
├── wsgi.py
├── requirements.txt
└── ADMIN_ACCESS.txt        (keep private!)
```

### Files to EXCLUDE (don't upload):
```
❌ __pycache__/
❌ *.pyc
❌ instance/               (will be created on server)
❌ logs/                   (will be created on server)
❌ venv/
❌ .env
❌ *.db (local database)
❌ pythonanywhere_*/       (old deployment folders)
```

---

## STEP 3: Create Deployment ZIP (2 minutes)

I'll help you create a clean deployment package. We'll run a PowerShell script to zip only the needed files.

**Run this in PowerShell:**

```powershell
cd C:\Users\HP\OneDrive\Documents\ABKBet

# Create a clean directory for deployment
$deployDir = "ABKBet_Deploy_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
New-Item -ItemType Directory -Path $deployDir -Force

# Copy essential files and folders
Copy-Item -Path "app" -Destination "$deployDir\app" -Recurse -Force
Copy-Item -Path "migrations" -Destination "$deployDir\migrations" -Recurse -Force
Copy-Item -Path "static" -Destination "$deployDir\static" -Recurse -Force
Copy-Item -Path "templates" -Destination "$deployDir\templates" -Recurse -Force
Copy-Item -Path "config.py" -Destination "$deployDir\" -Force
Copy-Item -Path "run.py" -Destination "$deployDir\" -Force
Copy-Item -Path "wsgi.py" -Destination "$deployDir\" -Force
Copy-Item -Path "requirements.txt" -Destination "$deployDir\" -Force

# Remove __pycache__ directories
Get-ChildItem -Path "$deployDir" -Include "__pycache__" -Recurse -Force | Remove-Item -Recurse -Force

# Create ZIP file
Compress-Archive -Path "$deployDir\*" -DestinationPath "ABKBet_Production.zip" -Force

Write-Host "✓ Deployment package created: ABKBet_Production.zip" -ForegroundColor Green
Write-Host "✓ Location: $(Get-Location)\ABKBet_Production.zip" -ForegroundColor Green
```

---

## STEP 4: Upload to PythonAnywhere (3 minutes)

### Option A: Upload via Files Tab (Recommended)

1. Go to PythonAnywhere Dashboard
2. Click **Files** tab
3. Click **Upload a file** button
4. Select `ABKBet_Production.zip`
5. Wait for upload to complete (progress bar)

### Option B: Upload via Bash Console

If zip is hosted online, you can use wget:
```bash
wget YOUR_DOWNLOAD_URL/ABKBet_Production.zip
```

---

## STEP 5: Extract Files (2 minutes)

1. On PythonAnywhere, open **Consoles** tab
2. Click **Bash** to start new console
3. Run these commands:

```bash
# Check current location
pwd
# Should show: /home/YOUR-USERNAME

# Create project directory
mkdir -p ABKBet
cd ABKBet

# Extract the uploaded zip
unzip ~/ABKBet_Production.zip

# Verify files extracted
ls -la
# You should see: app/ migrations/ static/ templates/ config.py run.py wsgi.py requirements.txt

# Clean up
rm ~/ABKBet_Production.zip
```

---

## STEP 6: Create Virtual Environment (3 minutes)

```bash
# Make sure you're in home directory
cd /home/YOUR-USERNAME

# Create virtual environment with Python 3.10
mkvirtualenv --python=/usr/bin/python3.10 abkbet_env

# Your prompt should now show (abkbet_env)
# If not, activate it:
workon abkbet_env

# Upgrade pip
pip install --upgrade pip

# Install dependencies
cd ABKBet
pip install -r requirements.txt

# This will take 2-3 minutes
```

**Expected output:** You should see all packages installing successfully.

---

## STEP 7: Set Up Database (3 minutes)

```bash
# Make sure you're in ABKBet directory
cd /home/YOUR-USERNAME/ABKBet

# Activate virtual environment if not already
workon abkbet_env

# Create instance directory
mkdir -p instance

# Create database and admin user
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
    print('✓ Admin user created: admin / admin123')
    print('✓ Test user created: testuser / test123')
EOF
```

**Expected output:**
```
✓ Database tables created
✓ Admin user created: admin / admin123
✓ Test user created: testuser / test123
```

---

## STEP 8: Configure Web App (5 minutes)

### 8.1 Create Web App

1. Go to **Web** tab on PythonAnywhere
2. Click **Add a new web app**
3. Click **Next** (for your domain)
4. Choose **Manual configuration** (NOT Flask!)
5. Select **Python 3.10**
6. Click **Next**

### 8.2 Configure WSGI File

1. On Web tab, scroll down to **Code** section
2. Click on the WSGI configuration file link (e.g., `/var/www/YOUR-USERNAME_pythonanywhere_com_wsgi.py`)
3. **DELETE ALL EXISTING CONTENT**
4. **Paste this EXACTLY** (replace YOUR-USERNAME with your actual username):

```python
import sys
import os

# Add project directory to path
project_home = '/home/YOUR-USERNAME/ABKBet'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Set environment variables
os.environ['FLASK_ENV'] = 'production'
os.environ['SECRET_KEY'] = 'your-secret-key-change-this-in-production-2024'
os.environ['JWT_SECRET_KEY'] = 'your-jwt-secret-key-change-this-2024'
os.environ['FOOTBALL_API_KEY'] = '8a0943a24d4c44f4f5d8a091f6348e9f'
os.environ['FOOTBALL_API_ENABLED'] = 'true'

# Import Flask app
from run import flask_app as application
```

5. Click **Save**

### 8.3 Set Virtual Environment

1. Scroll to **Virtualenv** section
2. Enter path: `/home/YOUR-USERNAME/.virtualenvs/abkbet_env`
3. Click checkmark ✓
4. Should show path in green

### 8.4 Configure Static Files

1. Scroll to **Static files** section
2. Click **Enter URL**: `/static/`
3. Click **Enter path**: `/home/YOUR-USERNAME/ABKBet/static/`
4. Click checkmark ✓

### 8.5 Reload Web App

1. Scroll to top of Web tab
2. Click big green **Reload** button
3. Wait 10 seconds

---

## STEP 9: Verify Deployment (5 minutes)

### 9.1 Check Error Log

1. On Web tab, click **Error log** link
2. Look for any red errors
3. Should see: "Application created with config: production"

### 9.2 Test Health Endpoint

In bash console:
```bash
curl https://YOUR-USERNAME.pythonanywhere.com/api/health
```

**Expected:** `{"status":"healthy"}`

### 9.3 Test in Browser

Open: `https://YOUR-USERNAME.pythonanywhere.com`

**Should see:** The ABKBet homepage

### 9.4 Test Login

1. Click Register or Login
2. Use test credentials:
   - Username: `testuser`
   - Password: `test123`
3. Should login successfully

### 9.5 Test Admin Access

1. Open: `https://YOUR-USERNAME.pythonanywhere.com/secure-admin-access-2024`
2. Login with:
   - Username: `admin`
   - Password: `admin123`
3. Should redirect to admin dashboard

---

## STEP 10: Add Sample Data (Optional - 5 minutes)

```bash
cd /home/YOUR-USERNAME/ABKBet
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
    print(f'✓ Added {len(matches)} sample matches')
EOF
```

---

## STEP 11: Configure Payment Methods (5 minutes)

```bash
cd /home/YOUR-USERNAME/ABKBet
workon abkbet_env

python << 'EOF'
from app import create_app, db
from app.models.payment_method import PaymentMethod

app = create_app('production')
with app.app_context():
    methods = [
        PaymentMethod(
            method_type='bitcoin',
            method_name='Bitcoin (BTC)',
            wallet_address='bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh',
            instructions='Send BTC to the wallet address above. Minimum deposit: 0.001 BTC',
            is_active=True
        ),
        PaymentMethod(
            method_type='bank_transfer',
            method_name='Bank Transfer',
            account_name='ABKBet Limited',
            account_number='1234567890',
            bank_name='Sample Bank',
            instructions='Use your username as reference when making transfer',
            is_active=True
        ),
        PaymentMethod(
            method_type='mobile_money',
            method_name='MTN Mobile Money',
            phone='+234-XXX-XXX-XXXX',
            instructions='Send to the number above with your username as reference',
            is_active=True
        )
    ]
    
    for method in methods:
        db.session.add(method)
    
    db.session.commit()
    print(f'✓ Added {len(methods)} payment methods')
    print('⚠️  Update with real payment details in admin panel!')
EOF
```

---

## 🎉 DEPLOYMENT COMPLETE!

### Your Live URLs:

- **Main Site:** `https://YOUR-USERNAME.pythonanywhere.com`
- **Admin Login:** `https://YOUR-USERNAME.pythonanywhere.com/secure-admin-access-2024`
- **Admin Dashboard:** `https://YOUR-USERNAME.pythonanywhere.com/admin`

### Test Accounts:

**Admin:**
- Username: `admin`
- Password: `admin123`

**Regular User:**
- Username: `testuser`
- Password: `test123`

---

## 🔧 Post-Deployment Tasks

### Immediate:

1. ✅ Change admin password (login → admin panel → users)
2. ✅ Update payment method details with real addresses
3. ✅ Test all features:
   - User registration
   - User login
   - Place bet
   - Deposit request
   - Withdrawal request
   - Admin approval workflows

### Before Real Production:

1. 📧 Configure email settings (SMTP)
2. 🔐 Change secret keys in WSGI file
3. 💳 Update payment methods with real details
4. 🎨 Update branding/logo if needed
5. 📱 Test on mobile devices
6. 🔒 Set up SSL certificate (PythonAnywhere provides this)

---

## 🐛 Troubleshooting

### Site shows error page:
1. Check error log (Web tab → Error log)
2. Look for specific error message
3. Common fix: Reload web app

### Import errors:
1. Make sure virtual environment is set correctly
2. Verify all packages installed: `pip list`

### Database errors:
1. Check database exists: `ls -la instance/`
2. Recreate if needed: Run Step 7 again

### Static files not loading:
1. Verify static files path on Web tab
2. Should be: `/home/YOUR-USERNAME/ABKBet/static/`

---

## 📞 Need Help?

If you encounter any issues:

1. **Check error log first** (most issues show here)
2. **Verify file paths** (common mistake is wrong username)
3. **Check virtual environment** is activated
4. **Reload web app** after any changes

**Share with me:**
- Your PythonAnywhere username
- Error log content (last 50 lines)
- What step you're on

I'll help you fix it!

---

## ✅ Final Checklist

- [ ] PythonAnywhere account created
- [ ] Project files uploaded
- [ ] Virtual environment created
- [ ] Dependencies installed
- [ ] Database created
- [ ] Admin user created
- [ ] Web app configured
- [ ] WSGI file configured
- [ ] Static files configured
- [ ] Site loads successfully
- [ ] User can register/login
- [ ] Admin can access dashboard
- [ ] Sample data added
- [ ] Payment methods configured

---

**Ready to deploy? Let's start with STEP 1!**

Tell me your PythonAnywhere username and we'll begin! 🚀
