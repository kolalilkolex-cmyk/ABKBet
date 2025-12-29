# PythonAnywhere Update Script - Only Modified Files
Write-Host "Creating update package with ONLY modified files..." -ForegroundColor Green

$updateFolder = "pythonanywhere_update"
if (Test-Path $updateFolder) {
    Remove-Item $updateFolder -Recurse -Force
}

# Create folder structure
New-Item -ItemType Directory -Path "$updateFolder/app" -Force | Out-Null
New-Item -ItemType Directory -Path "$updateFolder/app/routes" -Force | Out-Null
New-Item -ItemType Directory -Path "$updateFolder/static" -Force | Out-Null
New-Item -ItemType Directory -Path "$updateFolder/templates" -Force | Out-Null
New-Item -ItemType Directory -Path "$updateFolder/scripts" -Force | Out-Null

Write-Host "Copying modified files..." -ForegroundColor Yellow

# Copy only the files we modified
Copy-Item -Path "app/__init__.py" -Destination "$updateFolder/app/" -Force
Copy-Item -Path "app/routes/bet_routes.py" -Destination "$updateFolder/app/routes/" -Force
Copy-Item -Path "app/routes/admin_routes.py" -Destination "$updateFolder/app/routes/" -Force
Copy-Item -Path "static/abkbet-client.js" -Destination "$updateFolder/static/" -Force
Copy-Item -Path "templates/index.html" -Destination "$updateFolder/templates/" -Force
Copy-Item -Path "requirements.txt" -Destination "$updateFolder/" -Force

# Copy the backfill scripts in case they're needed
Copy-Item -Path "scripts/backfill_match_ids.py" -Destination "$updateFolder/scripts/" -Force
Copy-Item -Path "scripts/fix_selections.py" -Destination "$updateFolder/scripts/" -Force
Copy-Item -Path "scripts/resettle_bets.py" -Destination "$updateFolder/scripts/" -Force

# Create update instructions
@"
# PythonAnywhere Update Instructions

## Files Included:
- app/__init__.py (CORS fix)
- app/routes/bet_routes.py (match linking fix)
- app/routes/admin_routes.py (settlement logic fix)
- static/abkbet-client.js (match_id parameter)
- templates/index.html (bet creation & display fix)
- requirements.txt (numpy version fix)
- scripts/* (optional database fix scripts)

## Update Steps:

### 1. Backup Current Files (IMPORTANT!)
In PythonAnywhere Bash console:
```bash
cd /home/Lilkolex/ABKBet
mkdir backup_$(date +%Y%m%d)
cp app/__init__.py backup_$(date +%Y%m%d)/
cp app/routes/bet_routes.py backup_$(date +%Y%m%d)/
cp app/routes/admin_routes.py backup_$(date +%Y%m%d)/
cp static/abkbet-client.js backup_$(date +%Y%m%d)/
cp templates/index.html backup_$(date +%Y%m%d)/
cp requirements.txt backup_$(date +%Y%m%d)/
```

### 2. Upload Update Package
- Go to Files tab
- Upload: ABKBet_Update_XXXXXX.zip
- Extract:
```bash
cd /home/Lilkolex/ABKBet
unzip ABKBet_Update_*.zip -o
```

### 3. Update Requirements (if needed)
```bash
cd /home/Lilkolex/ABKBet
source venv/bin/activate
pip install -r requirements.txt --upgrade
```

### 4. Run Database Fixes (OPTIONAL - only if you have old bets with issues)
```bash
cd /home/Lilkolex/ABKBet
source venv/bin/activate

# Link bets to matches
python scripts/backfill_match_ids.py

# Fix bet selections
python scripts/fix_selections.py

# Re-settle bets with corrected logic
python scripts/resettle_bets.py
```

### 5. Reload Web App
- Go to Web tab
- Click green "Reload" button
- Visit: https://Lilkolex.pythonanywhere.com

## What's Fixed:

✅ CORS configuration for API access
✅ Bet creation now stores match_id correctly
✅ Settlement logic fixed (HOME/AWAY/DRAW/OVER/UNDER)
✅ Match scores display in tickets
✅ Bet selections stored correctly (not "1 picks")
✅ Ticket display improved (selection first, score with match)

## Testing:

1. Login to your site
2. Place a new bet
3. Check that match score shows when bet is settled
4. Verify HOME/AWAY/DRAW bets settle correctly
5. Check Over/Under bets work properly

## Rollback (if needed):
```bash
cd /home/Lilkolex/ABKBet
cp backup_YYYYMMDD/* ./ -r
# Then reload web app
```
"@ | Out-File -FilePath "$updateFolder/UPDATE_INSTRUCTIONS.txt" -Encoding UTF8

# Create zip file
$zipFile = "ABKBet_Update_$(Get-Date -Format 'yyyyMMdd_HHmmss').zip"
Compress-Archive -Path "$updateFolder/*" -DestinationPath $zipFile -Force

Write-Host ""
Write-Host "Update package created: $zipFile" -ForegroundColor Green
Write-Host ""
Write-Host "Files included:" -ForegroundColor Cyan
Write-Host "  - app/__init__.py" -ForegroundColor White
Write-Host "  - app/routes/bet_routes.py" -ForegroundColor White
Write-Host "  - app/routes/admin_routes.py" -ForegroundColor White
Write-Host "  - static/abkbet-client.js" -ForegroundColor White
Write-Host "  - templates/index.html" -ForegroundColor White
Write-Host "  - requirements.txt" -ForegroundColor White
Write-Host "  - scripts/* (optional fixes)" -ForegroundColor White
Write-Host ""
Write-Host "Next: Upload to PythonAnywhere Files tab" -ForegroundColor Yellow
Write-Host ""

Invoke-Item $updateFolder
