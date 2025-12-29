# PythonAnywhere Deployment Script
# This creates a zip file with all necessary files for deployment

Write-Host "Creating deployment package for PythonAnywhere..." -ForegroundColor Green

# Create deployment folder
$deployFolder = "pythonanywhere_deployment"
if (Test-Path $deployFolder) {
    Remove-Item $deployFolder -Recurse -Force
}
New-Item -ItemType Directory -Path $deployFolder | Out-Null

# Copy essential files and folders
Write-Host "Copying files..." -ForegroundColor Yellow

# Copy application folders
Copy-Item -Path "app" -Destination "$deployFolder/app" -Recurse -Force
Copy-Item -Path "templates" -Destination "$deployFolder/templates" -Recurse -Force
Copy-Item -Path "static" -Destination "$deployFolder/static" -Recurse -Force
Copy-Item -Path "migrations" -Destination "$deployFolder/migrations" -Recurse -Force

# Copy instance folder (excluding database)
New-Item -ItemType Directory -Path "$deployFolder/instance" -Force | Out-Null

# Copy root files
Copy-Item -Path "config.py" -Destination "$deployFolder/" -Force
Copy-Item -Path "run.py" -Destination "$deployFolder/" -Force
Copy-Item -Path "wsgi.py" -Destination "$deployFolder/" -Force
Copy-Item -Path "init_db.py" -Destination "$deployFolder/" -Force
Copy-Item -Path "requirements.txt" -Destination "$deployFolder/" -Force

# Create README for deployment
@"
# PythonAnywhere Deployment Instructions

## 1. Upload Files
Upload all files in this folder to: /home/YOUR_USERNAME/ABKBet/

## 2. Install Dependencies
In PythonAnywhere Bash console:
```bash
cd ~/ABKBet
python3.10 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## 3. Initialize Database
```bash
cd ~/ABKBet
source venv/bin/activate
python init_db.py
```

## 4. Configure WSGI
Edit your WSGI file at /var/www/YOUR_USERNAME_pythonanywhere_com_wsgi.py:
```python
import sys
import os

project_home = '/home/YOUR_USERNAME/ABKBet'
if project_home not in sys.path:
    sys.path = [project_home] + sys.path

os.environ['SECRET_KEY'] = 'your-secret-key-change-this'
os.environ['FOOTBALL_API_KEY'] = '8a0943a24d4c44f4f5d8a091f6348e9f'
os.environ['FOOTBALL_API_ENABLED'] = 'true'

from run import app as application
```

## 5. Reload Web App
Click "Reload" button on Web tab

## 6. Test Login/Register
Your site: https://YOUR_USERNAME.pythonanywhere.com

## Login/Register Fix Applied:
- CORS headers configured
- JWT token handling fixed
- Session management improved
- API endpoints corrected
"@ | Out-File -FilePath "$deployFolder/DEPLOYMENT_README.txt" -Encoding UTF8

# Create zip file
Write-Host "Creating zip file..." -ForegroundColor Yellow
$zipFile = "ABKBet_PythonAnywhere_Deployment_$(Get-Date -Format 'yyyyMMdd_HHmmss').zip"
Compress-Archive -Path "$deployFolder/*" -DestinationPath $zipFile -Force

Write-Host ""
Write-Host "Deployment package created: $zipFile" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. Go to pythonanywhere.com and login" -ForegroundColor White
Write-Host "2. Click Files and Upload the zip file" -ForegroundColor White
Write-Host "3. In Bash console: unzip the file" -ForegroundColor White
Write-Host "4. Follow instructions in DEPLOYMENT_README.txt" -ForegroundColor White
Write-Host ""
Write-Host "Opening deployment folder..." -ForegroundColor Yellow
Invoke-Item $deployFolder
