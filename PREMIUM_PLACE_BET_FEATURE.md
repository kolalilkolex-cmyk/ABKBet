# 🎯 Premium Ticket "Place Bet" Feature

## ✨ What's New

Users can now **place bets directly** from premium ticket displays without manually selecting each game again!

### Before:
1. User checks premium code
2. Sees the games/selections
3. Has to manually go back to matches
4. Select each game individually
5. Place bet

### After:
1. User checks premium code
2. Sees the games/selections  
3. **Enters stake amount directly**
4. **Clicks "Place Bet Now" button**
5. ✅ Done!

---

## 🚀 Features Added

### 1. **Direct Bet Placement from Premium Code Check**
- After checking a premium code you own, you'll see a "Place Your Bet" section
- Enter your stake amount
- See real-time potential win calculation
- Click "Place Bet Now" to instantly bet on all selections

### 2. **Quick Bet from "My Premium Bookings"**
- In the "My Premium Bookings" tab
- Each purchased booking has a "Quick Bet" section in the details
- Enter stake → See potential win → Click Bet button
- All in one convenient location!

### 3. **Live Calculations**
- As you type the stake amount, potential winnings update automatically
- Shows total odds clearly
- Instant feedback on your bet

### 4. **Smart Validation**
- Minimum bet: $1.00
- Balance checking before bet placement
- Confirmation dialog shows all bet details
- Error handling for insufficient balance

### 5. **Automatic Ticket Display**
- After placing bet, automatically shows your bet ticket
- Includes booking code reference
- All selections linked to the premium booking

---

## 📦 Files Modified

1. **`app/routes/premium_routes.py`**
   - Added new endpoint: `POST /api/premium/place-bet/<code>`
   - Handles bet placement from premium selections
   - Validates purchase ownership
   - Deducts stake from balance
   - Creates bet record with all premium selections

2. **`templates/index.html`**
   - Added "Place Your Bet" section to premium code display (when user owns it)
   - Added "Quick Bet" feature to "My Premium Bookings" tab
   - Added `placePremiumBet()` function
   - Added `quickPlaceBet()` function  
   - Added `updatePremiumPotentialWin()` for real-time calculations
   - Added `updateQuickWin()` for quick bet calculations

---

## 🎮 How Users Use It

### Method 1: From Premium Code Check

1. Go to "Premium Bets" tab
2. Enter booking code
3. Click "Check Code"
4. If you own it, scroll down to "Place Your Bet" section
5. Enter stake amount (e.g., $10)
6. See potential win update automatically
7. Click "Place Bet Now"
8. Confirm in dialog
9. ✅ Bet placed! Ticket shows automatically

### Method 2: From My Premium Bookings

1. Go to "My Bookings" tab (inside Premium Bets)
2. Find a purchased booking
3. Click "View Selections & Place Bet" to expand
4. See all your selections
5. In the "Quick Bet" section at bottom:
   - Enter stake amount
   - See potential win calculation
   - Click "Bet" button
6. ✅ Done!

---

## 🔧 API Endpoint Details

### `POST /api/premium/place-bet/<code>`

**Authentication:** Required (JWT)

**Parameters:**
```json
{
  "stake_usd": 10.00
}
```

**Response (Success):**
```json
{
  "message": "Bet placed successfully! 🎉",
  "bet": {
    "id": 123,
    "event_description": "Brighton vs West Ham | Real Madrid vs Barcelona (+3 more)",
    "stake_usd": 10.00,
    "stake_btc": 0.000222,
    "odds": 125.5,
    "potential_payout_usd": 1255.00,
    "potential_payout_btc": 0.027889,
    "booking_code": "PREM-ABC123",
    "status": "pending",
    "created_at": "2025-12-07T10:30:00"
  },
  "new_balance_btc": 0.005000,
  "new_balance_usd": 225.00
}
```

**Validation:**
- ✅ User must own the booking (purchased it)
- ✅ Minimum stake: $1.00
- ✅ Sufficient balance check
- ✅ Booking must be active and not expired

---

## 🎨 UI/UX Improvements

### Premium Code Display (After Purchase)
```
┌─────────────────────────────────────┐
│ ✅ You own this booking!            │
├─────────────────────────────────────┤
│ Booking Code: PREM-ABC123           │
│ Selections: 5  |  Total Odds: 125.5 │
├─────────────────────────────────────┤
│ 📋 Your Selections                  │
│ • Brighton vs West Ham              │
│   Match Winner: Brighton @ 1.54     │
│ • Real Madrid vs Barcelona          │
│   Match Winner: Real Madrid @ 2.10  │
│ ... (3 more)                        │
├─────────────────────────────────────┤
│ 💰 Place Your Bet                   │
│ Stake: [__10.00__] USD              │
│ Total Odds: 125.5  |  Win: $1255.00 │
│ [Place Bet Now] ←── NEW!            │
└─────────────────────────────────────┘
```

### My Premium Bookings Tab
```
┌─────────────────────────────────────┐
│ PREM-ABC123        Paid: $250.00    │
│ Purchased: Dec 7, 2025 10:00 AM     │
│ Selections: 5  |  Odds: 125.5       │
│                                     │
│ ▼ View Selections & Place Bet       │
│   • Brighton vs West Ham (1.54)     │
│   • Real Madrid vs Barcelona (2.10) │
│   ...                               │
│                                     │
│   🎯 Quick Bet                      │
│   Stake: [_10_] Win: $1255.00       │
│   [Bet] ←── NEW!                    │
└─────────────────────────────────────┘
```

---

## 📊 Benefits

✅ **Faster betting** - One-click bet placement  
✅ **Better UX** - No need to manually re-select games  
✅ **Less errors** - System ensures exact selections from booking  
✅ **Real-time feedback** - Instant win calculations  
✅ **Convenient** - Bet from multiple locations (code check OR my bookings)  
✅ **Professional** - Shows booking code on tickets for tracking  

---

## 🚀 Deployment to PythonAnywhere

### Upload Files:
1. **`app/routes/premium_routes.py`** → `/home/ABKBet/ABKBet/app/routes/`
2. **`templates/index.html`** → `/home/ABKBet/ABKBet/templates/`

### Reload Web App:
Go to Web tab → Click green "Reload" button

---

## ✅ Testing Checklist

After deployment, test:

- [ ] Check a premium code you own
- [ ] "Place Your Bet" section appears
- [ ] Enter stake amount → potential win updates
- [ ] Click "Place Bet Now" → bet created successfully
- [ ] Balance deducted correctly
- [ ] Bet ticket displays with booking code
- [ ] Go to "My Bookings" tab
- [ ] Expand a booking
- [ ] Quick Bet section appears
- [ ] Enter stake → click Bet → works
- [ ] Check bet in "My Bets" tab
- [ ] Booking code shows on bet ticket

---

## 🔍 Technical Details

**Bet Storage:**
- Bet record includes `booking_code` field
- Event description shows match names from premium selections
- All selections from booking are linked to the bet
- Bet status: "pending" (admin settles based on match results)

**Balance Handling:**
- Uses fixed BTC price: $45,000 (configurable in code)
- Stake deducted in BTC equivalent from user balance
- Real-time balance updates after bet placement

**Security:**
- JWT authentication required
- Ownership verification (must have purchased booking)
- Balance validation before bet placement
- Minimum bet enforcement ($1.00)

---

## 📝 Future Enhancements (Optional)

- [ ] Show bet history for specific premium bookings
- [ ] Multi-bet: bet on multiple bookings at once
- [ ] Favorites: save favorite bookings for quick access
- [ ] Push notifications when new premium bookings available
- [ ] Auto-bet: automatically bet when new premium booking matches criteria

---

**Status:** ✅ Ready to deploy  
**Package:** `premium_place_bet_feature.zip`  
**Priority:** High (major UX improvement)  
**Risk:** Low (isolated feature, no database schema changes)
