# Add Sample Data to PythonAnywhere

## ✅ COMPLETED
- Database tables created
- Payment methods added (Bitcoin, Bank Transfer, MTN Mobile Money)

## 🎯 NEXT: Add Sample Matches

### Step 1: Upload Script
1. Go to PythonAnywhere → **Files**
2. Navigate to: `/home/ABKBet/ABKBet`
3. Click **Upload a file**
4. Upload: `add_sample_matches.py` (from your local project)

### Step 2: Run Script
Open **Bash console** and run:
```bash
cd /home/ABKBet/ABKBet
workon abkbet_env
python add_sample_matches.py
```

Expected output:
```
✓ Successfully added 5 sample matches

Matches added:
  • Manchester United vs Liverpool (English Premier League)
    Date: 2025-12-08 XX:XX UTC
    Odds: 2.10 / 3.40 / 3.20
  ...
```

### Step 3: Verify
Visit: https://abkbet.pythonanywhere.com/api/matches/upcoming

Should see 5 matches with:
- Premier League: Man United vs Liverpool
- La Liga: Real Madrid vs Barcelona  
- Bundesliga: Bayern Munich vs Borussia Dortmund
- Serie A: Juventus vs AC Milan
- Ligue 1: PSG vs Marseille

## 🧪 TESTING CHECKLIST

Once matches are added, test these features:

### User Features
- [ ] Register new account
- [ ] Login with testuser/test123
- [ ] View upcoming matches
- [ ] Place single bet
- [ ] Place multi-bet (accumulator)
- [ ] Request deposit (Bitcoin, Bank, Mobile Money)
- [ ] Check bet history
- [ ] Request withdrawal

### Admin Features
- [ ] Login at: https://abkbet.pythonanywhere.com/secure-admin-access-2024
- [ ] Credentials: admin / admin123
- [ ] View all users
- [ ] View all bets
- [ ] Approve/reject deposit requests
- [ ] Approve/reject withdrawal requests
- [ ] Manage payment methods
- [ ] Update match results

## 📊 Current Status

**Live URL:** https://abkbet.pythonanywhere.com  
**Admin URL:** https://abkbet.pythonanywhere.com/secure-admin-access-2024

**Database Tables:** ✅ All created
- users
- matches
- bets
- deposits
- withdrawals
- payment_methods
- withdrawal_requests
- premium_booking_purchases

**Payment Methods:** ✅ Active
1. Bitcoin (BTC) - tb1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh
2. Bank Transfer - Sample Bank (1234567890)
3. MTN Mobile Money - +1234567890

**Test Accounts:**
- User: testuser / test123
- Admin: admin / admin123

## 🔧 Update Real Payment Details

When ready for production, update payment details:

1. Login to admin panel
2. Go to **Payment Methods** section
3. Edit each method:
   - **Bitcoin**: Update wallet address to your real BTC address
   - **Bank Transfer**: Update bank name, account number, account name
   - **MTN Mobile Money**: Update phone number to real MTN number

## 📝 Notes

- All features are now functional
- Sample data is for testing only
- Replace payment details before accepting real deposits
- Admin URL is hidden from public (no footer link)
- Mobile money integrated for both deposits and withdrawals
