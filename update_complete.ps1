# Complete Update Script - Including Premium Bookings
Write-Host "Creating COMPLETE update package with Premium Bookings..." -ForegroundColor Green

$updateFolder = "pythonanywhere_update_complete"
if (Test-Path $updateFolder) {
    Remove-Item $updateFolder -Recurse -Force
}

# Create folder structure
New-Item -ItemType Directory -Path "$updateFolder/app" -Force | Out-Null
New-Item -ItemType Directory -Path "$updateFolder/app/routes" -Force | Out-Null
New-Item -ItemType Directory -Path "$updateFolder/app/models" -Force | Out-Null
New-Item -ItemType Directory -Path "$updateFolder/static" -Force | Out-Null
New-Item -ItemType Directory -Path "$updateFolder/templates" -Force | Out-Null
New-Item -ItemType Directory -Path "$updateFolder/scripts" -Force | Out-Null

Write-Host "Copying ALL modified files including Premium Bookings..." -ForegroundColor Yellow

# Core fixes
Copy-Item -Path "app/__init__.py" -Destination "$updateFolder/app/" -Force
Copy-Item -Path "app/routes/bet_routes.py" -Destination "$updateFolder/app/routes/" -Force
Copy-Item -Path "app/routes/admin_routes.py" -Destination "$updateFolder/app/routes/" -Force
Copy-Item -Path "static/abkbet-client.js" -Destination "$updateFolder/static/" -Force
Copy-Item -Path "templates/index.html" -Destination "$updateFolder/templates/" -Force
Copy-Item -Path "requirements.txt" -Destination "$updateFolder/" -Force

# Premium Booking System
Copy-Item -Path "app/routes/premium_routes.py" -Destination "$updateFolder/app/routes/" -Force
Copy-Item -Path "app/models/premium_booking.py" -Destination "$updateFolder/app/models/" -Force
Copy-Item -Path "templates/premium_admin.html" -Destination "$updateFolder/templates/" -Force

# Database fix scripts
Copy-Item -Path "scripts/backfill_match_ids.py" -Destination "$updateFolder/scripts/" -Force
Copy-Item -Path "scripts/fix_selections.py" -Destination "$updateFolder/scripts/" -Force
Copy-Item -Path "scripts/resettle_bets.py" -Destination "$updateFolder/scripts/" -Force

# Create comprehensive update instructions
@"
# COMPLETE PythonAnywhere Update - All Features

## What's Included:

### Core Fixes:
✅ CORS configuration (app/__init__.py)
✅ Match linking fix (app/routes/bet_routes.py)
✅ Settlement logic fix - HOME/AWAY/DRAW/OVER/UNDER (app/routes/admin_routes.py)
✅ Match scores display in tickets (templates/index.html)
✅ Bet creation improvements (static/abkbet-client.js)
✅ Requirements fix (requirements.txt - numpy 1.26.4)

### NEW FEATURE - Premium Bookings:
✅ Premium booking code system (app/routes/premium_routes.py)
✅ Premium booking models (app/models/premium_booking.py)
✅ Premium admin interface (templates/premium_admin.html)
✅ Premium user interface (integrated in index.html)

### Database Fixes (Optional):
✅ Backfill match IDs for old bets
✅ Fix bet selections
✅ Re-settle incorrectly settled bets

## Update Steps:

### 1. BACKUP (CRITICAL!)
```bash
cd /home/Lilkolex/ABKBet
mkdir backup_before_update
cp -r app backup_before_update/
cp -r templates backup_before_update/
cp -r static backup_before_update/
cp requirements.txt backup_before_update/
```

### 2. Upload & Extract
- Upload ABKBet_Complete_Update_XXXXXX.zip to /home/Lilkolex/ABKBet/
```bash
cd /home/Lilkolex/ABKBet
unzip -o ABKBet_Complete_Update_*.zip
```

### 3. Update Database Schema (IMPORTANT for Premium Bookings!)
```bash
cd /home/Lilkolex/ABKBet
source venv/bin/activate

# Add premium booking tables to database
python -c "
from app import create_app, db
from app.models.premium_booking import PremiumBooking, PremiumBookingPurchase

app = create_app()
with app.app_context():
    db.create_all()
    print('Premium booking tables created!')
"
```

### 4. Update Requirements (if needed)
```bash
source venv/bin/activate
pip install -r requirements.txt --upgrade
```

### 5. Run Database Fixes (Optional - for old bets)
```bash
# Link old bets to matches
python scripts/backfill_match_ids.py

# Fix bet selections (from "1 picks" to actual selection)
python scripts/fix_selections.py

# Re-settle bets with corrected logic
python scripts/resettle_bets.py
```

### 6. Reload Web App
- Go to Web tab
- Click green "Reload" button
- Visit: https://Lilkolex.pythonanywhere.com

## New Premium Booking Feature:

### For Admins:
1. Go to /premium_admin
2. Create premium booking codes with match selections
3. Set price (default $250)
4. Users must pay to unlock selections

### For Users:
1. Click "Premium" tab
2. Enter premium code
3. Preview shows matches but hides selections
4. Pay $250 to unlock and view all picks

## Testing Checklist:

✅ Login/Register works
✅ Place a new bet - check match_id is set
✅ Settle a match - check HOME/AWAY/DRAW logic
✅ Check match scores show in tickets
✅ Test premium booking creation (admin)
✅ Test premium booking purchase (user)
✅ Verify Over/Under settlement works

## Rollback (if something breaks):
```bash
cd /home/Lilkolex/ABKBet
rm -rf app templates static requirements.txt
cp -r backup_before_update/* ./
# Then reload web app
```

## Support:
If you encounter issues:
1. Check error log: tail -f /var/log/Lilkolex.pythonanywhere.com.error.log
2. Check database was updated (step 3 above)
3. Verify all files were uploaded correctly
4. Ensure venv is activated when running Python commands
"@ | Out-File -FilePath "$updateFolder/COMPLETE_UPDATE_INSTRUCTIONS.txt" -Encoding UTF8

# Create zip file
$zipFile = "ABKBet_Complete_Update_$(Get-Date -Format 'yyyyMMdd_HHmmss').zip"
Compress-Archive -Path "$updateFolder/*" -DestinationPath $zipFile -Force

Write-Host ""
Write-Host "COMPLETE update package created: $zipFile" -ForegroundColor Green
Write-Host ""
Write-Host "Core Fixes:" -ForegroundColor Cyan
Write-Host "  - app/__init__.py (CORS)" -ForegroundColor White
Write-Host "  - app/routes/bet_routes.py (match linking)" -ForegroundColor White
Write-Host "  - app/routes/admin_routes.py (settlement logic)" -ForegroundColor White
Write-Host "  - static/abkbet-client.js (match_id)" -ForegroundColor White
Write-Host "  - templates/index.html (ticket display)" -ForegroundColor White
Write-Host "  - requirements.txt (numpy fix)" -ForegroundColor White
Write-Host ""
Write-Host "Premium Bookings:" -ForegroundColor Magenta
Write-Host "  - app/routes/premium_routes.py" -ForegroundColor White
Write-Host "  - app/models/premium_booking.py" -ForegroundColor White
Write-Host "  - templates/premium_admin.html" -ForegroundColor White
Write-Host ""
Write-Host "Database Fixes:" -ForegroundColor Yellow
Write-Host "  - scripts/backfill_match_ids.py" -ForegroundColor White
Write-Host "  - scripts/fix_selections.py" -ForegroundColor White
Write-Host "  - scripts/resettle_bets.py" -ForegroundColor White
Write-Host ""
Write-Host "IMPORTANT: Run database schema update after uploading!" -ForegroundColor Red
Write-Host "See COMPLETE_UPDATE_INSTRUCTIONS.txt for details" -ForegroundColor Yellow
Write-Host ""

Invoke-Item $updateFolder
