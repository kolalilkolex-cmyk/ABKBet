# Complete PythonAnywhere Deployment - All Files
Write-Host "Creating COMPLETE deployment package with ALL files..." -ForegroundColor Green

$deployFolder = "pythonanywhere_complete"
if (Test-Path $deployFolder) {
    Remove-Item $deployFolder -Recurse -Force
}

Write-Host "Copying all files and folders..." -ForegroundColor Yellow

# Copy ALL application folders
Copy-Item -Path "app" -Destination "$deployFolder/app" -Recurse -Force
Copy-Item -Path "templates" -Destination "$deployFolder/templates" -Recurse -Force
Copy-Item -Path "static" -Destination "$deployFolder/static" -Recurse -Force
Copy-Item -Path "migrations" -Destination "$deployFolder/migrations" -Recurse -Force

# Copy instance folder structure (without database)
New-Item -ItemType Directory -Path "$deployFolder/instance" -Force | Out-Null

# Copy root files
Copy-Item -Path "config.py" -Destination "$deployFolder/" -Force
Copy-Item -Path "run.py" -Destination "$deployFolder/" -Force
Copy-Item -Path "wsgi.py" -Destination "$deployFolder/" -Force
Copy-Item -Path "init_db.py" -Destination "$deployFolder/" -Force
Copy-Item -Path "requirements.txt" -Destination "$deployFolder/" -Force

# Copy scripts folder
Copy-Item -Path "scripts" -Destination "$deployFolder/scripts" -Recurse -Force

# Create deployment instructions
@"
# Complete PythonAnywhere Deployment

## What's Included:
✅ Premium Booking System (admin + user)
✅ Match Score Display in Tickets
✅ Fixed Settlement Logic (HOME/AWAY/DRAW/OVER/UNDER)
✅ Bet-to-Match Linking
✅ CORS Configuration
✅ All Bug Fixes

## Deployment Steps for /home/Lilkolex:

### Step 1: BACKUP YOUR CURRENT DATABASE (IMPORTANT!)
```bash
cd /home/Lilkolex
cp ABKBet/instance/abkbet.db abkbet_backup_$(date +%Y%m%d_%H%M%S).db
```

### Step 2: Upload and Extract
1. Upload: ABKBet_Complete_XXXXXX.zip to /home/Lilkolex/
2. In Bash console:
```bash
cd /home/Lilkolex
# Rename old folder as backup
mv ABKBet ABKBet_backup_$(date +%Y%m%d_%H%M%S)
# Extract new files
unzip ABKBet_Complete_*.zip -d ABKBet
cd ABKBet
```

### Step 3: Restore Your Database
```bash
cd /home/Lilkolex/ABKBet/instance
cp /home/Lilkolex/abkbet_backup_*.db ./abkbet.db
chmod 664 abkbet.db
```

### Step 4: Update Requirements (if needed)
```bash
cd /home/Lilkolex/ABKBet
source ../venv/bin/activate  # or wherever your venv is
pip install -r requirements.txt --upgrade
```

### Step 5: Run Database Migrations
```bash
cd /home/Lilkolex/ABKBet
source ../venv/bin/activate

# Add premium booking tables if they don't exist
python -c "from app import create_app, db; app=create_app(); app.app_context().push(); db.create_all(); print('Database updated!')"

# Optional: Run fix scripts for existing bets
python scripts/backfill_match_ids.py
python scripts/fix_selections.py
python scripts/resettle_bets.py
```

### Step 6: Reload Web App
- Go to Web tab on PythonAnywhere
- Click green "Reload" button
- Visit: https://Lilkolex.pythonanywhere.com

### Step 7: Test Everything
1. Login/Register
2. Place a bet and check it appears correctly
3. Admin panel → Create premium booking code
4. User → Enter premium code and purchase
5. Settle a match and verify correct win/loss

## New Features Available:

### Premium Booking System:
- Admin: /admin → Premium Bookings tab
- Users: Premium tab on main page
- Creates booking codes ($250 USD)
- Users can view match names but selections are hidden until purchased

### Enhanced Features:
- Match scores display in bet tickets
- Correct settlement for all bet types
- Improved ticket display
- Better bet tracking with match linking

## Rollback (if needed):
```bash
cd /home/Lilkolex
rm -rf ABKBet
mv ABKBet_backup_YYYYMMDD_HHMMSS ABKBet
# Reload web app
```

## Troubleshooting:

### Database errors:
```bash
cd /home/Lilkolex/ABKBet
source ../venv/bin/activate
python init_db.py  # Re-initialize (WARNING: erases data)
# Or restore backup: cp ~/abkbet_backup_*.db instance/abkbet.db
```

### Missing tables:
```bash
python -c "from app import create_app, db; app=create_app(); app.app_context().push(); db.create_all()"
```

### Check logs:
```bash
tail -f /var/log/Lilkolex.pythonanywhere.com.error.log
```
"@ | Out-File -FilePath "$deployFolder/DEPLOYMENT_INSTRUCTIONS.txt" -Encoding UTF8

# Create zip file
$zipFile = "ABKBet_Complete_$(Get-Date -Format 'yyyyMMdd_HHmmss').zip"
Compress-Archive -Path "$deployFolder/*" -DestinationPath $zipFile -Force

Write-Host ""
Write-Host "Complete deployment package created: $zipFile" -ForegroundColor Green
Write-Host ""
Write-Host "Includes:" -ForegroundColor Cyan
Write-Host "  ✓ Premium Booking System" -ForegroundColor White
Write-Host "  ✓ All Bug Fixes" -ForegroundColor White
Write-Host "  ✓ Match Score Display" -ForegroundColor White
Write-Host "  ✓ Settlement Logic Fixes" -ForegroundColor White
Write-Host "  ✓ CORS Configuration" -ForegroundColor White
Write-Host "  ✓ Database Scripts" -ForegroundColor White
Write-Host ""
Write-Host "IMPORTANT: Backup your database first!" -ForegroundColor Red
Write-Host "See DEPLOYMENT_INSTRUCTIONS.txt in the zip" -ForegroundColor Yellow
Write-Host ""

Invoke-Item $deployFolder
