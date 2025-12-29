# 🚀 Complete Update Package for ABKBet

## Package Contents (50 KB)

📦 **`abkbet_complete_update.zip`** includes:

1. ✅ `app/payment_methods.py` - All 6 payment methods for deposits & withdrawals
2. ✅ `templates/index.html` - Updated frontend with PayPal/Skrill withdrawal forms
3. ✅ `add_sample_matches.py` - Script to add 5 test matches

## 📤 Upload to PythonAnywhere

### Step 1: Upload Package

1. Go to PythonAnywhere → **Files** tab
2. Navigate to: `/home/ABKBet/ABKBet`
3. Click **Upload a file**
4. Select: `abkbet_complete_update.zip` (50 KB)
5. Wait for upload to complete

### Step 2: Upload Deployment Script

1. Still in `/home/ABKBet/ABKBet`
2. Click **Upload a file** again
3. Select: `deploy_complete_update.sh`

### Step 3: Run Deployment

Open **Bash console** and run:

```bash
cd /home/ABKBet/ABKBet
bash deploy_complete_update.sh
```

The script will:
- ✅ Backup your current files
- ✅ Extract the update package
- ✅ Verify all files are present
- ✅ Add 5 sample matches automatically
- ✅ Show completion message

### Step 4: Reload Web App

1. Go to **Web** tab
2. Click **Reload abkbet.pythonanywhere.com**
3. Done! ✅

## 🎯 What Gets Updated

### Payment Methods (Backend + Frontend)
- ✅ All 6 methods available for deposits
- ✅ All 6 methods available for withdrawals
- ✅ PayPal withdrawal form (email input)
- ✅ Skrill withdrawal form (email input)
- ✅ USDT already included (was missing before)

### Sample Matches (5 matches)
1. **Premier League**: Manchester United vs Liverpool
2. **La Liga**: Real Madrid vs Barcelona
3. **Bundesliga**: Bayern Munich vs Borussia Dortmund
4. **Serie A**: Juventus vs AC Milan
5. **Ligue 1**: Paris Saint-Germain vs Marseille

All matches scheduled 2-6 days from now with realistic odds.

## 🧪 Testing After Update

### Test Deposits (All 6 Methods)
1. Login: testuser / test123
2. Go to **Deposits** tab
3. Select each method and verify:
   - ✅ Bitcoin - Shows wallet address
   - ✅ Bank Transfer - Shows bank list (Nigeria)
   - ✅ PayPal - Shows PayPal email
   - ✅ Skrill - Shows Skrill email
   - ✅ Mobile Money - Shows phone number
   - ✅ USDT - Shows wallet address

### Test Withdrawals (All 6 Methods)
1. Go to **Withdrawals** tab
2. Select each method and verify form fields:
   - ✅ Bitcoin - Asks for wallet address
   - ✅ Bank Transfer - Asks for bank details
   - ✅ PayPal - Asks for PayPal email ← **NEW**
   - ✅ Skrill - Asks for Skrill email ← **NEW**
   - ✅ Mobile Money - Asks for phone number
   - ✅ USDT - Asks for wallet address

### Test Betting
1. Go to **Matches** section
2. Should see 5 upcoming matches
3. Click on any match to place bet
4. Test single bet and multi-bet (accumulator)

### Test Admin Panel
1. Login: https://abkbet.pythonanywhere.com/secure-admin-access-2024
2. Credentials: admin / admin123
3. View pending deposit/withdrawal requests
4. Approve/reject requests
5. Update payment method details in Payment Methods section

## 📁 Files in Your Local Folder

```
ABKBet/
├── abkbet_complete_update.zip          ← Upload this
├── deploy_complete_update.sh           ← Upload this
├── add_sample_matches.py               ← Included in ZIP
├── app/payment_methods.py              ← Included in ZIP
├── templates/index.html                ← Included in ZIP
└── update_payment_methods.md           ← Reference docs
```

## ⚠️ Important Notes

- The deployment script automatically adds sample matches
- Backups are created with timestamp (e.g., `.backup.20251206_211900`)
- If script fails, check the error message
- You can manually extract the ZIP if needed: `unzip -o abkbet_complete_update.zip`

## 🔧 Manual Extraction (If Needed)

If the script doesn't work, manually extract:

```bash
cd /home/ABKBet/ABKBet
unzip -o abkbet_complete_update.zip
workon abkbet_env
python add_sample_matches.py
```

Then reload web app from Web tab.

## ✅ Success Indicators

After deployment, you should see:

1. **Bash console output:**
   ```
   ✓ Successfully added 5 sample matches
   
   Matches added:
     • Manchester United vs Liverpool (English Premier League)
     • Real Madrid vs Barcelona (Spanish La Liga)
     ...
   ```

2. **API test:**
   - Visit: https://abkbet.pythonanywhere.com/api/matches/upcoming
   - Should return 5 matches

3. **User interface:**
   - All 6 payment methods visible in dropdowns
   - Matches section shows 5 matches
   - Withdrawal forms work for PayPal/Skrill

## 🆘 Troubleshooting

**Problem:** Script not found  
**Solution:** Make sure you uploaded both `abkbet_complete_update.zip` AND `deploy_complete_update.sh`

**Problem:** Permission denied  
**Solution:** Run: `chmod +x deploy_complete_update.sh` then try again

**Problem:** "workon: command not found"  
**Solution:** Run: `source ~/.virtualenvs/abkbet_env/bin/activate` then `python add_sample_matches.py`

**Problem:** Matches already exist  
**Solution:** That's fine! The script will skip adding duplicates

**Problem:** 500 errors after update  
**Solution:** Check error log in Web tab, make sure you reloaded the web app

---

**Ready to deploy?** Just upload the 2 files and run the script! 🚀
