# ABKBet - Troubleshooting Guide

---

## ⚠️ **URGENT: Manual Matches Not Showing?**

### **Problem:** New matches created in admin panel don't appear on site

### **Root Cause:** Browser is showing cached (old) JavaScript/HTML

### **SOLUTION - Clear Browser Cache:**

#### **Quick Fix (Hard Refresh):**
1. Press **`Ctrl + F5`** (Windows) or **`Cmd + Shift + R`** (Mac)
2. This forces browser to reload everything

#### **Full Cache Clear:**
1. Press **`Ctrl + Shift + Delete`**
2. Select "Cached images and files"
3. Click "Clear data"
4. Refresh page

#### **Alternative: Use Incognito/Private Window**
- Opens with clean cache
- Navigate to `http://127.0.0.1:5000`
- Matches should appear immediately

### **Verify Matches Exist (PowerShell):**
```powershell
# Test API endpoint directly
Invoke-WebRequest -Uri "http://127.0.0.1:5000/api/bets/matches/manual" -UseBasicParsing
```

### **Expected Matches:**
1. Manchester United vs Liverpool (Premier League) - 2.1/3.4/3.2
2. Real Madrid vs Barcelona (La Liga) - 2.25/3.1/3.0
3. Bayern Munich vs Borussia Dortmund (Bundesliga) - 1.75/3.8/4.5

### **Where to Find Matches:**

**On Main Site:**
- Look for purple **"Manual Matches"** button (below "Explore Matches")
- Click it to open modal with all matches
- Click odds to add to betslip

**In Admin Panel:**
- Go to `/admin` and login as `alice`
- Click **"Manual Matches"** in left sidebar
- See table with all matches + Edit/Update/Delete buttons

---

## Common Issues & Solutions

### Installation Issues

#### 1. Python Not Found
**Problem:** "python: command not found" or "'python' is not recognized"

**Solution:**
- Install Python from https://www.python.org/
- Add Python to PATH during installation
- Restart terminal after installation
- Use `python --version` to verify

#### 2. Virtual Environment Won't Activate
**Problem:** Virtual environment scripts don't work

**Solution (Windows):**
```powershell
# Try alternative activation method
venv\Scripts\python.exe -m pip install -r requirements.txt
```

**Solution (Linux/Mac):**
```bash
# Ensure file is executable
chmod +x venv/bin/activate
source venv/bin/activate
```

#### 3. Pip Install Fails
**Problem:** "ERROR: Could not install packages"

**Solution:**
```bash
# Upgrade pip
python -m pip install --upgrade pip

# Try installing one by one
pip install Flask==2.3.3
pip install Flask-SQLAlchemy==3.0.5
# etc.

# If specific package fails, check internet connection
```

### Running the Application

#### 1. Port 5000 Already in Use
**Problem:** "Address already in use" error

**Solution (Windows):**
```powershell
# Find process using port 5000
netstat -ano | findstr :5000

# Kill the process
taskkill /PID <PID> /F
```

**Solution (Linux/Mac):**
```bash
# Find process using port 5000
lsof -i :5000

# Kill the process
kill -9 <PID>
```

Or change port in `run.py`:
```python
app.run(debug=True, host='0.0.0.0', port=5001)
```

#### 2. Import Errors
**Problem:** "ModuleNotFoundError: No module named 'flask'"

**Solution:**
- Ensure virtual environment is activated
- Reinstall requirements: `pip install -r requirements.txt`
- Verify you're in project directory

#### 3. Database Connection Error
**Problem:** "sqlite3.OperationalError: no such table"

**Solution:**
```bash
# Reinitialize database
python manage_db.py reset

# Or just init
python manage_db.py init
```

#### 4. Bitcoin Service Connection Issues
**Problem:** "Connection error" with Bitcoin service

**Solution:**
- Check internet connection
- Verify BITCOIN_NETWORK is set to 'testnet'
- Try different blockchain API endpoint
- Increase timeout in bitcoin_service.py

### Database Issues

#### 1. Database Locked
**Problem:** "database is locked" error

**Solution:**
```bash
# Stop the application
# Delete betting.db
# Reinitialize
python manage_db.py init

# Restart application
python run.py
```

#### 2. Wrong Database URL
**Problem:** Connection to PostgreSQL fails

**Solution:**
- Check DATABASE_URL format in .env
- Verify PostgreSQL is running
- Check credentials are correct
- Format: `postgresql://user:password@localhost/dbname`

#### 3. Migration Issues
**Problem:** "Column does not exist" errors

**Solution:**
```bash
# Reset database
python manage_db.py reset

# Then reinit
python manage_db.py init
```

### Web Interface Issues

#### 1. Cannot Access Web Interface
**Problem:** Cannot open http://localhost:5000

**Solution:**
- Verify app is running (check terminal)
- Check if port 5000 is correct
- Try http://127.0.0.1:5000
- Try http://localhost:5000/templates/index.html
- Check browser console for errors (F12)

#### 2. JavaScript Errors in Browser
**Problem:** Console shows JavaScript errors

**Solution:**
- Open browser console (F12)
- Check the exact error message
- Verify abkbet-client.js is in static/ folder
- Check network tab for failed requests
- Ensure Flask is serving static files correctly

#### 3. CORS Errors
**Problem:** "No 'Access-Control-Allow-Origin' header"

**Solution:**
- CORS is already enabled in run.py
- Clear browser cache
- Try incognito/private window
- Verify correct API base URL

### Bitcoin Integration Issues

#### 1. Wallet Address Generation Fails
**Problem:** Bitcoin address not generated

**Solution:**
- Ensure 'bit' library is installed: `pip install bit`
- Try restarting application
- Check bitcoin_service.py has no syntax errors
- Verify BITCOIN_NETWORK is set correctly

#### 2. Fee Estimation Fails
**Problem:** Cannot get Bitcoin fees

**Solution:**
- Check internet connection
- Verify bitcoinfees.earn.com is accessible
- Try different blockchain service
- Return default fees if API fails

#### 3. Transaction Verification Always Fails
**Problem:** Deposits are not verified

**Solution:**
- Ensure correct Bitcoin address in wallet
- Verify transaction is on correct network (testnet/mainnet)
- Check transaction on blockchain explorer
- Allow more time for confirmations
- Check CONFIRMATION_REQUIRED setting

### API Issues

#### 1. 401 Unauthorized Error
**Problem:** JWT token not working

**Solution:**
- Ensure Authorization header is present
- Format: `Authorization: Bearer YOUR_TOKEN`
- Token may have expired (30 days default)
- Login again to get new token
- Check JWT_SECRET_KEY is configured

#### 2. 400 Bad Request
**Problem:** API returns validation error

**Solution:**
- Check required fields in request body
- Verify JSON format is correct
- Check data types (amount should be float, etc.)
- Use API_DOCUMENTATION.md to verify request format

#### 3. 500 Internal Server Error
**Problem:** "Internal server error" from server

**Solution:**
- Check terminal for error details
- Verify database is working
- Check all environment variables are set
- Restart application
- Check file permissions
- Review code for syntax errors

### Bitcoin Testnet Issues

#### 1. Cannot Get Testnet Bitcoin
**Problem:** Testnet faucet not working

**Solution:**
- Try different faucet: https://testnet-faucet.mempool.space/
- Or: https://bitcoinfaucet.uo1.net/
- Wait between requests (usually 1 hour)
- Use testnet wallet from Bitcoin Core

#### 2. Transactions Taking Too Long
**Problem:** Bitcoin not showing up in wallet

**Solution:**
- Check at https://testnet.blockexplorer.com/
- Wait for at least 1 confirmation
- Verify correct Bitcoin address
- Disable adblocker if using faucet
- Try resending transaction

#### 3. Wrong Network Selected
**Problem:** Testnet transaction not found

**Solution:**
- Verify .env has `BITCOIN_NETWORK=testnet`
- Restart application after changing
- Check transaction on correct explorer
- Use mainnet explorer for mainnet transactions

### Performance Issues

#### 1. Application Slow to Load
**Problem:** Long wait times when accessing app

**Solution:**
- Check internet connection
- Verify database is working
- Reduce number of transactions loaded
- Use pagination for large datasets
- Check system resources (CPU, RAM)

#### 2. Bets Not Creating Fast Enough
**Problem:** Slow bet creation

**Solution:**
- Check database connection
- Verify no heavy background tasks
- Check API response times
- Optimize database queries
- Use production configuration

### Security Issues

#### 1. JWT Secret Key Warning
**Problem:** Using default secret key

**Solution:**
```bash
# Generate strong key
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Update .env with the generated key
JWT_SECRET_KEY=your_generated_key_here
```

#### 2. Bitcoin Private Key Exposure
**Problem:** Private keys visible in logs

**Solution:**
- Never log private keys
- Use encrypted storage (production)
- Restrict file permissions
- Use environment variables
- Keep backups secure

### Debugging Tips

#### 1. Enable Debug Mode
```python
# In config.py set:
FLASK_DEBUG = True

# In run.py:
app.run(debug=True)
```

#### 2. Check Terminal Output
- Application logs appear in terminal
- Look for error messages and stack traces
- Copy error message into search engine

#### 3. Use Browser Developer Tools
- Press F12 to open console
- Check Network tab for API calls
- Check Application tab for stored data
- Check for JavaScript errors

#### 4. Log to File
```python
# Add logging to understand issues
import logging
logging.basicConfig(filename='app.log', level=logging.DEBUG)
logger = logging.getLogger(__name__)
logger.info("Message here")
```

#### 5. Test API with curl
```bash
# Test endpoints directly
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"test","email":"test@test.com","password":"pass"}'
```

### Help Resources

1. **Can't find solution?**
   - Check FILE_INDEX.md for code location
   - Review code comments
   - Check test files for examples

2. **Still stuck?**
   - Read DEPLOYMENT.md for production setup
   - Review API_DOCUMENTATION.md for endpoints
   - Check README.md for features

3. **Need to reset everything?**
   ```bash
   # Remove virtual environment
   rm -rf venv
   
   # Remove database
   rm betting.db
   
   # Run setup again
   ./setup.bat  # Windows
   ./setup.sh   # Linux/Mac
   ```

## Quick Fixes Checklist

- [ ] Verify Python version (3.8+)
- [ ] Activate virtual environment
- [ ] Run setup script
- [ ] Check .env file configuration
- [ ] Restart application
- [ ] Clear browser cache
- [ ] Check internet connection
- [ ] Verify database initialized
- [ ] Check Bitcoin network setting
- [ ] Look at terminal error messages

## When All Else Fails

1. **Complete Reset:**
   ```bash
   # Windows
   rmdir /s venv
   del betting.db
   .\setup.bat
   python run.py
   
   # Linux/Mac
   rm -rf venv betting.db
   ./setup.sh
   python run.py
   ```

2. **Verify Installation:**
   ```bash
   python --version
   pip --version
   pip list  # Should show Flask, SQLAlchemy, etc.
   ```

3. **Test Basic Functionality:**
   - Visit http://localhost:5000/api/health
   - Should return `{"status": "healthy"}`

4. **Review Logs:**
   - Terminal output
   - Check for error stack traces
   - Look at timestamp of errors

5. **Seek Help:**
   - Google the error message
   - Check GitHub issues
   - Review documentation again
   - Try alternative approaches

---

**Most issues are resolved by:**
1. Checking internet connection
2. Resetting everything
3. Reading error messages carefully
4. Checking documentation
5. Verifying configuration

**Good luck! The application is solid - most issues are environment-related.** 🚀
