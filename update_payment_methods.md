# Update All Payment Methods on PythonAnywhere

## Changes Made

### ✅ All Payment Methods Now Available

**Deposits (6 methods):**
1. ✅ Bitcoin (BTC)
2. ✅ Bank Transfer (8 Nigerian banks)
3. ✅ PayPal
4. ✅ Skrill
5. ✅ MTN Mobile Money
6. ✅ USDT (Tether)

**Withdrawals (6 methods):**
1. ✅ Bitcoin (BTC)
2. ✅ Bank Transfer
3. ✅ PayPal (NEWLY ADDED)
4. ✅ Skrill (NEWLY ADDED)
5. ✅ MTN Mobile Money
6. ✅ USDT (Tether)

## Files Updated

1. **`app/payment_methods.py`** - Added PayPal and Skrill to WITHDRAWAL_METHODS
2. **`templates/index.html`** - Added PayPal and Skrill to withdrawal dropdown and form handling

## Upload to PythonAnywhere

### Method 1: Using File Upload (Recommended)

1. Go to PythonAnywhere → **Files** tab
2. Navigate to `/home/ABKBet/ABKBet/app`
3. Click **Upload a file** → Upload `payment_methods.py`
4. Navigate to `/home/ABKBet/ABKBet/templates`
5. Click **Upload a file** → Upload `index.html`
6. Go to **Web** tab → Click **Reload** button

### Method 2: Using Bash Console

Open Bash console and run:

```bash
cd /home/ABKBet/ABKBet

# Backup current files
cp app/payment_methods.py app/payment_methods.py.backup
cp templates/index.html templates/index.html.backup

# Download updated files (if you have them uploaded somewhere)
# Or manually copy-paste the content using nano editor:

nano app/payment_methods.py
# Paste the updated content, then Ctrl+X, Y, Enter

nano templates/index.html
# Paste the updated content, then Ctrl+X, Y, Enter
```

### Method 3: Create Complete Update Package

I can create a ZIP file with all updated files for easy upload.

## After Upload

1. Go to **Web** tab
2. Click **Reload abkbet.pythonanywhere.com**
3. Test the new payment methods:
   - Visit: https://abkbet.pythonanywhere.com
   - Login with testuser/test123
   - Go to Withdrawals
   - You should now see all 6 methods including PayPal and Skrill

## Testing Checklist

### Deposits (All 6 should work)
- [ ] Bitcoin - Shows wallet address with copy button
- [ ] Bank Transfer - Shows Nigerian bank options
- [ ] PayPal - Shows PayPal email with copy button
- [ ] Skrill - Shows Skrill email with copy button
- [ ] MTN Mobile Money - Shows phone number with copy button
- [ ] USDT - Shows wallet address with copy button

### Withdrawals (All 6 should work)
- [ ] Bitcoin - Asks for wallet address
- [ ] Bank Transfer - Asks for bank details
- [ ] PayPal - Asks for PayPal email (NEWLY ADDED)
- [ ] Skrill - Asks for Skrill email (NEWLY ADDED)
- [ ] MTN Mobile Money - Asks for phone number
- [ ] USDT - Asks for wallet address

## Admin Panel Payment Methods

The admin can manage payment method details via the admin panel:

1. Login: https://abkbet.pythonanywhere.com/secure-admin-access-2024
2. Credentials: admin / admin123
3. Go to **Payment Methods** section
4. Update real payment details:
   - Bitcoin wallet address
   - USDT wallet address (TRC20 or ERC20)
   - PayPal email
   - Skrill email
   - Bank account details
   - Mobile Money number

## Current Payment Details (Sample Data)

These are placeholder values - update via admin panel:

- **Bitcoin**: tb1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh
- **USDT**: 0x1234567890123456789012345678901234567890 (TRC20)
- **PayPal**: payments@abkbet.com
- **Skrill**: payments@abkbet.com
- **Bank Transfer**: Sample Bank (1234567890)
- **MTN Mobile Money**: +1234567890

## Notes

- All 6 payment methods are now fully integrated for both deposits and withdrawals
- Users can choose any method based on their preference
- Admin approves all deposit and withdrawal requests manually
- Processing times vary: instant (banks), 10-30 min (crypto), 24-48h (withdrawals)
- Each method has min/max limits (configurable in payment_methods.py)
