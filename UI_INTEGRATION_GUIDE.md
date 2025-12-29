# Deposit System UI Integration Guide

## Overview
This guide explains how to integrate the new deposit approval system UI into your existing templates.

## Files Created
- `DEPOSIT_FORM_NEW.html` - New user deposit form (2-step process)
- `ADMIN_DEPOSITS_NEW.html` - Admin approval panel
- `UI_INTEGRATION_GUIDE.md` - This guide

## Integration Steps

### Part 1: Update User Deposit Form (index.html)

**Location:** `templates/index.html` around lines 1909-1928

**Current Code to Replace:**
```html
<div class="payment-form">
    <h2 style="font-weight: 900; font-size: 22px; letter-spacing: 0.5px;">
        <i class="fas fa-money-bill-wave"></i> DEPOSIT FUNDS
    </h2>
    <form onsubmit="depositFunds(event)">
        <label for="depositMethod">Payment Method:</label>
        <select id="depositMethod" name="method" class="payment-input" required>
            <option value="">-- Select Payment Method --</option>
            <option value="bitcoin">Bitcoin (BTC)</option>
            <option value="skrill">Skrill</option>
            <option value="revolut">Revolut</option>
            <option value="eversend">Eversend</option>
        </select>

        <label for="depositAmount">Amount (USD):</label>
        <input type="number" id="depositAmount" name="amount" class="payment-input" step="0.01" min="10" placeholder="Enter amount in USD" required />

        <label for="depositReference">Transaction Reference:</label>
        <input type="text" id="depositReference" name="reference" class="payment-input" placeholder="Enter your transaction reference" required />

        <button type="submit" class="payment-button">
            <i class="fas fa-arrow-right"></i> Submit Deposit
        </button>
    </form>
    <div class="payment-result" id="depositResult"></div>
</div>
```

**Action:**
1. Open `templates/index.html`
2. Find the above section (search for "DEPOSIT FUNDS")
3. Replace the ENTIRE `<div class="payment-form">` section with the content from `DEPOSIT_FORM_NEW.html`

**What This Does:**
- Adds 2-step deposit process (select method → see payment details → submit)
- Displays payment addresses/accounts to users
- Shows instructions for each payment method
- Adds deposit history section
- Shows deposit status (pending/approved/rejected)

---

### Part 2: Update Admin Panel (admin2.html)

**Location:** `templates/admin2.html` around line 733

**Current Code to Replace:**
Search for the "Pending Deposits" section. It might look like:
```html
<div class="dashboard-section">
    <h3><i class="fas fa-money-check-alt"></i> Pending Deposits</h3>
    <div class="stat-number" id="pendingDeposits">0</div>
</div>
```

**Action:**
1. Open `templates/admin2.html`
2. Find the "Pending Deposits" section
3. Replace the ENTIRE section with the content from `ADMIN_DEPOSITS_NEW.html`

**What This Does:**
- Lists all deposit requests with filtering (pending/approved/rejected/all)
- Shows detailed deposit information (user, amount, method, reference, proof)
- Adds approve/reject buttons for pending deposits
- Auto-refreshes every 30 seconds
- Updates pending counter in real-time

---

### Part 3: Update Payment Configuration

**Location:** `config/payment_methods.py`

**Current State:** Contains placeholder addresses

**Action Required:**
Update the following with your REAL payment details:

```python
PAYMENT_METHODS = {
    'bitcoin': {
        'name': 'Bitcoin (BTC)',
        'enabled': True,
        'details': {
            'address': 'YOUR_REAL_BITCOIN_ADDRESS_HERE',  # ← UPDATE THIS
            'network': 'Bitcoin Mainnet',
            # ... rest of details
        },
        # ... rest of config
    },
    'bank_transfer': {
        'name': 'Bank Transfer',
        'enabled': True,
        'details': {
            'bank_name': 'YOUR_BANK_NAME',  # ← UPDATE THIS
            'account_name': 'YOUR_ACCOUNT_NAME',  # ← UPDATE THIS
            'account_number': 'YOUR_ACCOUNT_NUMBER',  # ← UPDATE THIS
            'routing_number': 'YOUR_ROUTING_NUMBER',  # ← UPDATE THIS
            'swift_code': 'YOUR_SWIFT_CODE',  # ← UPDATE THIS
        },
        # ... rest of config
    },
    'paypal': {
        'name': 'PayPal',
        'enabled': True,
        'details': {
            'email': 'your.real.paypal@email.com',  # ← UPDATE THIS
            # ... rest of details
        },
        # ... rest of config
    },
    'skrill': {
        'name': 'Skrill',
        'enabled': True,
        'details': {
            'email': 'your.real.skrill@email.com',  # ← UPDATE THIS
            # ... rest of details
        },
        # ... rest of config
    },
    'usdt': {
        'name': 'USDT (Tether)',
        'enabled': True,
        'details': {
            'address': 'YOUR_REAL_USDT_ADDRESS_HERE',  # ← UPDATE THIS
            'network': 'TRC20 (Tron)',
            # ... rest of details
        },
        # ... rest of config
    }
}
```

**⚠️ CRITICAL:** Do NOT deploy to production until you update these addresses with real values!

---

### Part 4: Local Testing

**Step 1: Start the server**
```powershell
cd C:\Users\HP\OneDrive\Documents\ABKBet
python run.py
```

**Step 2: Test User Deposit Flow**
1. Open `http://localhost:5000` in browser
2. Register a new test user or login
3. Go to Wallet tab
4. Click "Deposit Funds"
5. Select a payment method (e.g., Bitcoin)
6. Verify payment details appear (address, instructions)
7. Enter amount (e.g., $50)
8. Enter a fake transaction reference (e.g., "test123")
9. Submit deposit request
10. Verify success message appears
11. Check "My Deposit Requests" section appears with status "PENDING"

**Step 3: Test Admin Approval Flow**
1. Open new browser tab (or incognito)
2. Login as admin (Lilkolex / Lilkolex@12345)
3. Click "Admin Panel" button
4. Go to "Deposit Management" section
5. Verify test deposit appears in "Pending" tab
6. Click "Approve" button
7. Confirm approval
8. Verify deposit moves to "Approved" tab
9. Go back to user tab
10. Check wallet balance updated
11. Check deposit status changed to "APPROVED"

**Step 4: Test Rejection**
1. Create another test deposit as user
2. In admin panel, click "Reject" button
3. Enter reason (e.g., "Invalid reference")
4. Verify deposit moves to "Rejected" tab
5. Check user sees rejection with admin note

---

### Part 5: Deploy to PythonAnywhere

**Option A: Upload Complete ZIP**

```powershell
# Create deployment package
cd C:\Users\HP\OneDrive\Documents\ABKBet
Compress-Archive -Path * -DestinationPath ABKBet_deposit_v2.zip -Force
```

Then:
1. Go to PythonAnywhere Files tab
2. Upload `ABKBet_deposit_v2.zip`
3. Open Bash console:
```bash
cd ~
unzip -o ABKBet_deposit_v2.zip
```

**Option B: Upload Individual Files (Faster)**

Upload only changed files:
1. `app/models/deposit.py` (NEW)
2. `app/routes/deposit_routes.py` (NEW)
3. `config/payment_methods.py` (NEW)
4. `templates/index.html` (MODIFIED)
5. `templates/admin2.html` (MODIFIED)
6. `scripts/create_deposit_table.py` (NEW)
7. `app/models/__init__.py` (MODIFIED)
8. `run.py` (MODIFIED)

**After Upload:**
1. Go to Web tab
2. Click "Reload" button

---

### Part 6: Create MySQL Table on PythonAnywhere

**Wait for CPU quota reset** (midnight UTC) then:

```bash
cd ~
source venv/bin/activate
export DATABASE_URL='mysql://Lilkolex:LilkolexK%4012345@Lilkolex.mysql.pythonanywhere-services.com/Lilkolex$betting'
python scripts/create_deposit_table.py
```

**Expected Output:**
```
✅ deposit_requests table created successfully!
```

**Verify Table Created:**
```bash
mysql -u Lilkolex -p
# Enter password: LilkolexK@12345
use Lilkolex$betting;
SHOW TABLES;
# Should see "deposit_requests" in list
DESCRIBE deposit_requests;
# Should show all columns
exit
```

---

### Part 7: Live Testing

1. Visit `https://lilkolex.pythonanywhere.com`
2. Register new test user
3. Test deposit flow (select Bitcoin)
4. Verify payment address displays
5. Submit test deposit
6. Login as admin
7. Approve deposit
8. Verify balance updated

---

## Troubleshooting

### Issue: Payment details not showing
**Cause:** Payment method not enabled or invalid ID
**Fix:** Check `config/payment_methods.py` - ensure `'enabled': True`

### Issue: "Method not found" error
**Cause:** Frontend using wrong payment method ID
**Fix:** Check dropdown values match config keys exactly (bitcoin, bank_transfer, paypal, skrill, usdt)

### Issue: Approve button does nothing
**Cause:** API endpoint not registered
**Fix:** Verify `run.py` has `flask_app.register_blueprint(deposit_bp)`

### Issue: 404 on /api/deposit/*
**Cause:** Blueprint not registered or wrong URL prefix
**Fix:** Check `run.py` line 65 has `flask_app.register_blueprint(deposit_bp)`

### Issue: Database error on approve
**Cause:** deposit_requests table doesn't exist in MySQL
**Fix:** Run `create_deposit_table.py` on PythonAnywhere

### Issue: Balance not updating after approval
**Cause:** BTC conversion logic issue
**Fix:** Check `deposit_routes.py` line ~140 - conversion rate is 1 BTC = $50,000

### Issue: Admin can't see pending deposits
**Cause:** Token issue or permission error
**Fix:** Verify admin user has `is_admin=True` in database

---

## Features Overview

### User Features
- ✅ Select from 5 payment methods
- ✅ See payment details (addresses, accounts)
- ✅ See min/max deposit limits
- ✅ See processing time estimates
- ✅ View step-by-step instructions
- ✅ Copy payment details to clipboard
- ✅ Submit transaction reference/proof
- ✅ View deposit history
- ✅ See deposit status (pending/approved/rejected)
- ✅ See admin rejection reason if rejected

### Admin Features
- ✅ View all deposit requests
- ✅ Filter by status (pending/approved/rejected/all)
- ✅ See user details for each request
- ✅ See transaction reference and proof
- ✅ Approve deposits (auto-credits balance)
- ✅ Reject deposits with reason
- ✅ View processing history
- ✅ Auto-refresh every 30 seconds
- ✅ Real-time counters

---

## Security Notes

1. **Never commit payment addresses to public repos**
2. **Update placeholder addresses before production**
3. **Verify payment references match actual transactions**
4. **Keep admin passwords secure**
5. **Review deposits carefully before approval**
6. **Check transaction confirmations for crypto**

---

## Next Steps After Integration

1. ✅ Update payment addresses in config
2. ✅ Test complete flow locally
3. ✅ Deploy to PythonAnywhere
4. ✅ Create MySQL table
5. ✅ Test live site
6. ⏳ Enable/disable payment methods as needed
7. ⏳ Adjust min/max deposit limits
8. ⏳ Update BTC conversion rate (or implement live rates)
9. ⏳ Add email notifications (optional)
10. ⏳ Monitor deposits daily

---

## Files Reference

**Backend:**
- `app/models/deposit.py` - DepositRequest model
- `app/routes/deposit_routes.py` - 8 API endpoints
- `config/payment_methods.py` - Payment method configurations
- `scripts/create_deposit_table.py` - Database migration

**Frontend:**
- `templates/index.html` - User deposit form (Wallet tab)
- `templates/admin2.html` - Admin approval panel

**Modified:**
- `app/models/__init__.py` - Added DepositRequest import
- `run.py` - Registered deposit_bp blueprint

---

## Support

If you encounter issues:
1. Check server logs: `logs/abkbet.log`
2. Check browser console for JavaScript errors
3. Verify database table exists: `SELECT * FROM deposit_requests LIMIT 1;`
4. Test API endpoints directly with curl/Postman
5. Review `DEPOSIT_SYSTEM_GUIDE.md` for API documentation

---

## Summary

Your deposit system is now complete with:
- ✅ Professional 2-step deposit flow
- ✅ Manual admin approval workflow
- ✅ 5 payment methods supported
- ✅ Real-time status tracking
- ✅ Clean, modern UI
- ✅ Full error handling
- ✅ Auto-refresh functionality

**Just integrate the UI files and update payment addresses to go live!**
