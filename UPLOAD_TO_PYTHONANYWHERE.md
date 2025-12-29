# 🚀 Virtual Games - PythonAnywhere Upload Checklist

## ✅ Files to Upload from Documents/ABKBet

Upload these 6 files to **PythonAnywhere** at path `/home/ABKBet/ABKBet/`:

### 1️⃣ Backend Files

| Local File | PythonAnywhere Path |
|------------|---------------------|
| `app\models\virtual_game.py` | `/home/ABKBet/ABKBet/app/models/virtual_game.py` |
| `app\services\virtual_game_service.py` | `/home/ABKBet/ABKBet/app/services/virtual_game_service.py` |
| `app\routes\virtual_game_routes.py` | `/home/ABKBet/ABKBet/app/routes/virtual_game_routes.py` |

### 2️⃣ Frontend Files

| Local File | PythonAnywhere Path |
|------------|---------------------|
| `templates\index.html` | `/home/ABKBet/ABKBet/templates/index.html` |
| `templates\admin.html` | `/home/ABKBet/ABKBet/templates/admin.html` |

### 3️⃣ Migration Script

| Local File | PythonAnywhere Path |
|------------|---------------------|
| `migrate_virtual_games.py` | `/home/ABKBet/ABKBet/migrate_virtual_games.py` |

---

## 📋 After Upload: Bash Console Commands

Open a **Bash console** on PythonAnywhere and run these commands:

### Step 1: Navigate & Activate
```bash
cd /home/ABKBet/ABKBet
source venv/bin/activate
```

### Step 2: Register Blueprint in run.py

**Option A: Use Web Editor (RECOMMENDED)**
1. Go to PythonAnywhere **Files** tab
2. Open `/home/ABKBet/ABKBet/run.py`
3. Find line with `from app.routes.premium_routes import premium_bp`
4. Add below it: `from app.routes.virtual_game_routes import virtual_game_bp`
5. Find line with `flask_app.register_blueprint(premium_bp)`
6. Add below it: `flask_app.register_blueprint(virtual_game_bp)`
7. Save file

**Option B: Use sed command**
```bash
# Add import
sed -i '/from app.routes.premium_routes import premium_bp/a from app.routes.virtual_game_routes import virtual_game_bp' run.py

# Add registration
sed -i '/flask_app.register_blueprint(premium_bp)/a flask_app.register_blueprint(virtual_game_bp)' run.py
```

### Step 3: Verify Blueprint Registration
```bash
grep "virtual_game_bp" run.py
```

Should show 2 lines:
```
from app.routes.virtual_game_routes import virtual_game_bp
flask_app.register_blueprint(virtual_game_bp)
```

### Step 4: Run Migration
```bash
python migrate_virtual_games.py
```

Expected output:
```
============================================================
Virtual Games Database Migration
============================================================

Creating virtual game tables...
✅ Virtual game tables created successfully!
Created tables: virtual_leagues, virtual_teams, virtual_games

============================================================
✅ Migration completed successfully!
============================================================
```

### Step 5: Verify Tables
```bash
python -c "from run import flask_app; from app.extensions import db; from app.models.virtual_game import VirtualLeague, VirtualTeam, VirtualGame; exec('with flask_app.app_context():\n    print(\"Leagues:\", VirtualLeague.query.count())\n    print(\"Teams:\", VirtualTeam.query.count())\n    print(\"Games:\", VirtualGame.query.count())')"
```

Expected output:
```
Leagues: 0
Teams: 0
Games: 0
```

### Step 6: Reload Web App
1. Go to PythonAnywhere **Web** tab
2. Click green **"Reload abkbet.pythonanywhere.com"** button
3. Wait for reload to complete

---

## 🧪 Testing After Deployment

### Test 1: Check API
```bash
curl https://abkbet.pythonanywhere.com/api/virtual/leagues
```

Should return:
```json
{"success":true,"leagues":[]}
```

### Test 2: Login to Admin Panel
1. Go to `https://abkbet.pythonanywhere.com/admin`
2. Click "Virtual Games" in sidebar
3. Should see empty leagues/games tables (not error)
4. Click **"Quick Setup (3 Leagues)"** button
5. Should see success message with leagues created

### Test 3: Check User Interface
1. Login as a regular user
2. Click "Virtual" tab
3. Should see 3 league tabs (Virtual Premier League, etc.)
4. Should see scheduled games with betting odds

---

## 🐛 If You See Errors

### Error: "JSON.parse: unexpected character"
**Cause:** Backend files not uploaded or blueprint not registered  
**Fix:** 
1. Verify all 6 files uploaded
2. Check blueprint registration in run.py
3. Reload web app

### Error: "ModuleNotFoundError: No module named 'app.models.virtual_game'"
**Cause:** Migration ran before files uploaded  
**Fix:**
1. Upload backend files first
2. Run migration again

### Error: "Table already exists"
**Cause:** Tables were created in previous attempt  
**Fix:** Tables exist, just reload web app and test

### Error: Admin page shows 500
**Cause:** Blueprint not registered  
**Fix:**
1. Check run.py has both lines added
2. Reload web app
3. Check error logs

---

## ✅ Success Checklist

- [ ] 6 files uploaded to PythonAnywhere
- [ ] Blueprint registered in run.py (2 lines added)
- [ ] Migration completed successfully
- [ ] Web app reloaded
- [ ] API returns `{"success":true,"leagues":[]}`
- [ ] Admin Virtual Games section loads without errors
- [ ] Quick Setup button works
- [ ] User Virtual tab shows leagues

---

## 🎮 Final Step: Populate Data

After everything works:

1. **Admin Login** → Virtual Games section
2. Click **"Quick Setup (3 Leagues)"**
3. Wait for confirmation: "Created 3 leagues, 24 teams, 12 games"
4. **Start Games** using Start button for each game
5. **Test Betting** on user side

---

**Current Status:** Ready to upload! All files prepared in `Documents/ABKBet` folder.
