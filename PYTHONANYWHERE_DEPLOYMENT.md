# PythonAnywhere Deployment Guide

## Step 1: Sign Up for PythonAnywhere

1. Go to: https://www.pythonanywhere.com/registration/register/beginner/
2. Create a **free account** (Beginner plan)
3. Confirm your email
4. Login to your dashboard

## Step 2: Upload Your Code

### Option A: Using Git (Recommended)
1. Go to your PythonAnywhere dashboard
2. Click "Consoles" → "Bash"
3. Run these commands:
```bash
git clone https://github.com/YOUR_USERNAME/YOUR_REPO.git
cd YOUR_REPO
```

### Option B: Upload Files Manually
1. Click "Files" tab
2. Navigate to `/home/YOUR_USERNAME/`
3. Create folder: `ABKBet`
4. Upload all your files:
   - `app/` folder (all files)
   - `migrations/` folder
   - `templates/` folder
   - `static/` folder
   - `instance/` folder
   - `config.py`
   - `run.py`
   - `requirements.txt`

## Step 3: Set Up Virtual Environment

1. Go to "Consoles" → "Bash"
2. Run these commands:
```bash
cd ~/ABKBet
python3.10 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Step 4: Configure Database

1. In the Bash console:
```bash
cd ~/ABKBet
source venv/bin/activate
python init_db.py
```

## Step 5: Set Environment Variables

1. Go to "Web" tab
2. Scroll to "Environment variables" section
3. Add these:
   - `SECRET_KEY`: `your-secret-key-here`
   - `FOOTBALL_API_KEY`: `8a0943a24d4c44f4f5d8a091f6348e9f`
   - `FOOTBALL_API_ENABLED`: `true`

## Step 6: Create Web App

1. Click "Web" tab
2. Click "Add a new web app"
3. Choose "Manual configuration"
4. Select "Python 3.10"
5. Click "Next"

## Step 7: Configure WSGI File

1. In the "Web" tab, find "Code" section
2. Click on the WSGI configuration file link (e.g., `/var/www/YOUR_USERNAME_pythonanywhere_com_wsgi.py`)
3. **Replace ALL contents** with this:

```python
import sys
import os

# Add your project directory to the sys.path
project_home = '/home/YOUR_USERNAME/ABKBet'
if project_home not in sys.path:
    sys.path = [project_home] + sys.path

# Set environment variables
os.environ['SECRET_KEY'] = 'your-secret-key-here'
os.environ['FOOTBALL_API_KEY'] = '8a0943a24d4c44f4f5d8a091f6348e9f'
os.environ['FOOTBALL_API_ENABLED'] = 'true'

# Import Flask app
from run import app as application
```

**IMPORTANT**: Replace `YOUR_USERNAME` with your actual PythonAnywhere username!

4. Click "Save"

## Step 8: Configure Virtual Environment

1. Still in "Web" tab
2. Find "Virtualenv" section
3. Enter path: `/home/YOUR_USERNAME/ABKBet/venv`
4. Click the checkmark

## Step 9: Set Working Directory

1. In "Web" tab, find "Code" section
2. Set "Working directory" to: `/home/YOUR_USERNAME/ABKBet`

## Step 10: Configure Static Files

1. In "Web" tab, scroll to "Static files" section
2. Add mapping:
   - URL: `/static/`
   - Directory: `/home/YOUR_USERNAME/ABKBet/static/`

## Step 11: Reload Web App

1. Scroll to top of "Web" tab
2. Click the big green **"Reload"** button
3. Wait for it to finish

## Step 12: Access Your Site

Your site will be available at:
**`https://YOUR_USERNAME.pythonanywhere.com`**

## Troubleshooting

### Check Error Logs
1. Go to "Web" tab
2. Click on error log link
3. Check for any errors

### Common Issues

**Import Error:**
- Make sure virtualenv path is correct
- Verify all packages installed: `pip list`

**Database Error:**
- Run `python init_db.py` in Bash console
- Check database file permissions

**Static Files Not Loading:**
- Verify static files path in Web tab
- Check file permissions

### Reload After Changes
Always click "Reload" button after:
- Changing code
- Installing packages
- Modifying WSGI file
- Updating environment variables

## Updating Your Site

When you make changes:

1. Upload new files (or `git pull`)
2. If requirements changed:
```bash
source venv/bin/activate
pip install -r requirements.txt
```
3. Click "Reload" in Web tab

## Populate API Matches

After deployment, populate matches:
```bash
cd ~/ABKBet
source venv/bin/activate
python scripts/populate_api_matches.py
```

## Database Location

Your SQLite database will be at:
`/home/YOUR_USERNAME/ABKBet/instance/betting.db`

## Free Plan Limits

- 512 MB disk space
- 100 seconds CPU time per day
- One web app
- Always-on (24/7!)

## Going Live

Your site is now accessible 24/7 at:
**`https://YOUR_USERNAME.pythonanywhere.com`**

Share this URL with anyone - they can access your betting site anytime!

---

**Need Help?**
- PythonAnywhere Forums: https://www.pythonanywhere.com/forums/
- Documentation: https://help.pythonanywhere.com/
