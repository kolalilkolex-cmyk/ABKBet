# Premium Booking System - Balance Restrictions

## Overview
Premium booking codes are now restricted to users with low balances to encourage deposits.

## Restrictions

### 1. Balance Requirement: $250 Minimum
- **Eligibility:** Users must have **at least $250 USD** balance to access premium codes
- **Check:** System converts BTC balance to USD using rate: 1 BTC = $45,000 USD
- **Example:** 
  - User with 0.006 BTC = $270 USD → ✓ Can see and purchase premium codes
  - User with 0.005 BTC = $225 USD → ✗ Must deposit $25 more first

### 2. Hidden Selections Until Deposit
When a user pastes a premium code:
- **Balance >= $250:** User can see code and purchase (selections shown after purchase)
- **Balance < $250:** Selections are **hidden** - must deposit to reach $250 first
- **After purchase:** Full selections **revealed** (teams, markets, odds visible)
- **Purpose:** Encourages users to deposit before accessing premium picks

## User Flow

### Step 1: User Pastes Code
```
User enters premium code: PRM1234567
↓
System checks:
- Is code valid? ✓
- Is code active? ✓
- Is user balance >= $250? 
  → If YES: Show code, allow purchase
  → If NO: Hide selections, require deposit
- Has user purchased? ✗
```

### Step 2A: User with Balance >= $250 (Can Purchase)
User can see the premium code and purchase it immediately.

### Step 2B: User with Balance < $250 (Must Deposit First)
```json
{
  "booking_code": "PRM1234567",
  "total_odds": 15.8,
  "price_usd": 250.0,
  "num_selections": 5,
  "matches_preview": [
    {"match": "Manchester United vs Liverpool", "market": "Match Result"},
    {"match": "Real Madrid vs Barcelona", "market": "Over/Under 2.5"},
    ...
  ],
  "requires_deposit": true,
  "can_purchase": false,
  "has_access": false,
  "user_balance_usd": 100.00,
  "minimum_balance_required": 250.00,
  "deposit_needed": 150.00
}
```

**Note:** No selection details (home/away/over/under) or individual odds shown until balance reaches $250.

### Step 3: User Deposits
User deposits funds to reach minimum $250 balance.

### Step 4: User Purchases Code
```
POST /api/premium/purchase/PRM1234567
↓
System checks:
- Balance >= $250? ✓
- Deduct $250 from balance
- Grant access to selections
↓
Response: Full selections revealed
```

### Step 5: User Sees Full Selections (After Purchase)
```json
{
  "booking_code": "PRM1234567",
  "selections": [
    {
      "match": "Manchester United vs Liverpool",
      "match_id": 123,
      "market": "Match Result",
      "selection": "home",
      "odds": 2.20,
      "team": "Manchester United"
    },
    {
      "match": "Real Madrid vs Barcelona",
      "match_id": 124,
      "market": "Over/Under 2.5",
      "selection": "over2",
      "odds": 1.85
    },
    ...
  ],
  "has_access": true
}
```

## API Endpoints

### Check Premium Code
```bash
GET /api/premium/check-code/<code>
Authorization: Bearer <token>

# Response if balance >= $250 (can access and purchase)
{
  "booking": {
    "booking_code": "PRM1234567",
    "total_odds": 15.8,
    "price_usd": 250.0,
    "matches_preview": [...]  // Preview shown
  },
  "has_access": false,
  "requires_deposit": false,
  "can_purchase": true,
  "user_balance_usd": 300.50,
  "minimum_balance_required": 250.0,
  "deposit_needed": 0
}

# Response if balance < $250 (must deposit first)
{
  "booking": {
    "booking_code": "PRM1234567",
    "total_odds": 15.8,
    "price_usd": 250.0,
    "matches_preview": [...]  // Hidden selections
  },
  "has_access": false,
  "requires_deposit": true,
  "can_purchase": false,
  "user_balance_usd": 100.00,
  "minimum_balance_required": 250.0,
  "deposit_needed": 150.00
}

# Response if already purchased
{
  "booking": {
    "booking_code": "PRM1234567",
    "selections": [...]  // Full selections visible
  },
  "has_access": true,
  "requires_deposit": false
}
```

### Purchase Premium Code
```bash
POST /api/premium/purchase/<code>
Authorization: Bearer <token>

# Response if balance < $250 (must deposit first)
{
  "error": "You need at least $250 balance to purchase premium codes",
  "your_balance_usd": 100.00,
  "required_minimum_balance": 250.0,
  "deposit_needed": 150.00
}

# Response if balance >= $250 but insufficient for purchase price
{
  "error": "Insufficient balance",
  "required_usd": 250.0,
  "current_balance_usd": 100.00,
  "current_balance_btc": 0.00222
}

# Response if purchase successful
{
  "message": "Premium booking purchased successfully",
  "booking": {
    "selections": [...]  // Full selections now visible
  },
  "new_balance_btc": 0.00667
}
```

## Admin Features

### Creating Premium Codes
Admins can create codes with custom prices, but the $250 balance limit still applies to users:

```bash
POST /api/premium/admin/create-booking
Authorization: Bearer <admin_token>

{
  "selections": [
    {
      "match_id": 123,
      "match": "Manchester United vs Liverpool",
      "market": "Match Result",
      "selection": "home",
      "odds": 2.20
    }
  ],
  "description": "Premier League Special",
  "price_usd": 250.0,
  "expires_hours": 24
}
```

## Frontend Integration

### Display Logic

**User Balance < $250 (Locked State):**
```javascript
if (booking.requires_deposit && !booking.can_purchase) {
  // Show locked state - must deposit first
  showMatchPreview(booking.matches_preview);
  showDepositPrompt(`Deposit $${booking.deposit_needed} to unlock`);
  disablePurchaseButton();
  disableBettingOptions();
}
```

**User Balance >= $250 (Can Purchase):**
```javascript
if (!booking.has_access && booking.can_purchase) {
  // Show preview, allow purchase
  showMatchPreview(booking.matches_preview);
  enablePurchaseButton();
}
```

**After Purchase (Unlocked State):**
```javascript
if (booking.has_access) {
  // Show full selections
  showFullSelections(booking.selections);
  enableBettingWithSelections();
}
```

### Example UI Messages

**User with balance < $250:**
```
🔒 Deposit Required
You need at least $250 balance to access premium codes.
Your balance: $100.00
Deposit needed: $150.00

[Deposit Now]
```

**User with balance >= $250 (not purchased yet):**
```
🔒 Premium Selections Locked
Total Odds: 15.8x
Price: $250 USD

Matches included:
• Manchester United vs Liverpool - Match Result
• Real Madrid vs Barcelona - Over/Under 2.5
• ... 3 more matches

💰 Deposit $250 to unlock full selections
[Deposit Now] [Cancel]
```

**User with balance >= $250 (after purchase):**
```
✅ Premium Selections Unlocked
Total Odds: 15.8x

Full picks:
✓ Manchester United to WIN @ 2.20
✓ Over 2.5 Goals @ 1.85
✓ ... 3 more picks

[Place Bets] [View All Selections]
```

## Migration/Update

Run this script after deployment:
```bash
cd /home/Lilkolex/ABKBet
workon abkbet_env
python scripts/update_premium_restrictions.py
```

This will:
- Verify premium tables exist
- Check user balances
- Show who's eligible vs not eligible
- Confirm restrictions are active

## Testing

### Test Case 1: User with Low Balance (Must Deposit)
```bash
# User: newuser with 0.002 BTC ($90)
# Try to check premium code
curl -X GET https://lilkolex.pythonanywhere.com/api/premium/check-code/PRM1234567 \
  -H "Authorization: Bearer <token>"

# Expected: Code shown but locked, requires_deposit: true, deposit_needed: $160
```

### Test Case 2: User with Sufficient Balance (Can Purchase)
```bash
# User: testuser with 0.007 BTC ($315)
# Check premium code
curl -X GET https://lilkolex.pythonanywhere.com/api/premium/check-code/PRM1234567 \
  -H "Authorization: Bearer <token>"

# Expected: Preview shown, can_purchase: true, requires_deposit: false
```

### Test Case 3: User Deposits and Purchases
```bash
# 1. User deposits to reach $250+
# 2. Purchase code
curl -X POST https://lilkolex.pythonanywhere.com/api/premium/purchase/PRM1234567 \
  -H "Authorization: Bearer <token>"

# Expected: Success, full selections revealed
```

## Summary

✅ **Implemented Features:**
- Balance requirement: Users must have >= $250 to access premium codes
- Hidden selections: Locked until balance reaches $250 AND purchase made
- Deposit encouragement: Clear messaging showing exact amount needed
- Full reveal: After purchase, all selections visible

✅ **Protection Against:**
- Low-balance users accessing premium picks without depositing
- Revealing selections before payment
- Users bypassing minimum deposit requirements

✅ **User Experience:**
- Clear deposit prompts with exact amounts needed
- Preview of code details (odds, num selections)
- Smooth deposit → unlock → purchase → reveal flow
- Users with sufficient balance can purchase immediately
