# Premium Booking - Balance-Based Access System

## Overview

Premium booking codes now use a **balance-based access system** instead of requiring separate purchases:
- **Users with $250+ balance**: Automatically see premium selections and can stake games directly
- **Users with < $250 balance**: See the booking code but selections are hidden until they deposit

**Key Change**: No payment deducted - access is purely based on having sufficient balance.

---

## How It Works

### Balance Requirement
- **Minimum Balance**: $250 USD equivalent
- **BTC Conversion**: 1 BTC = $45,000 USD (fixed rate)
- **Check Formula**: `user_balance_btc * 45000 >= 250`
- **Required BTC**: Minimum 0.00556 BTC to access premium features

### Access Levels

#### ✅ Eligible Users (Balance >= $250):
- See booking code
- See full match selections with teams, markets, and picks
- Can stake premium games directly
- **No payment required** - balance stays unchanged
- Can view and use premium selections anytime while balance remains >= $250
- Can place multiple bets on premium games

#### ❌ Restricted Users (Balance < $250):
- See booking code
- See match previews (match names and market types only)
- **Cannot see actual picks** (home/away/draw selections hidden)
- Cannot stake premium games
- Receive deposit prompt with exact amount needed
- Must deposit to unlock selections

---

## User Flow Scenarios

### Scenario 1: User with $300 Balance (Eligible)
```
1. User enters premium code: PRM1234567
2. System checks balance: $300 >= $250 ✓
3. Response:
   ✓ Booking code visible
   ✓ Full selections revealed
   ✓ Can stake games immediately
   ✓ No payment prompt
   ✓ Balance remains: $300
```

**What User Sees:**
```json
{
  "booking": {
    "code": "PRM1234567",
    "selections": [
      {
        "match": "Man United vs Liverpool",
        "market": "Full Time Result",
        "pick": "Away Win",  // ← VISIBLE
        "odds": 2.80
      },
      {
        "match": "Real Madrid vs Barcelona", 
        "market": "Over/Under 2.5",
        "pick": "Over 2.5",  // ← VISIBLE
        "odds": 1.85
      }
    ]
  },
  "has_access": true,
  "requires_deposit": false,
  "user_balance_usd": 300.00
}
```

### Scenario 2: User with $150 Balance (Restricted)
```
1. User enters premium code: PRM1234567
2. System checks balance: $150 < $250 ✗
3. Response:
   ✓ Booking code visible
   ✗ Selections hidden
   ✗ Cannot stake
   🔄 Deposit prompt: "Need $100 more"
```

**What User Sees:**
```json
{
  "booking": {
    "code": "PRM1234567",
    "matches_preview": [
      {
        "match": "Man United vs Liverpool",
        "market": "Full Time Result"
        // pick is HIDDEN
      },
      {
        "match": "Real Madrid vs Barcelona",
        "market": "Over/Under 2.5"
        // pick is HIDDEN
      }
    ]
  },
  "has_access": false,
  "requires_deposit": true,
  "user_balance_usd": 150.00,
  "minimum_balance_required": 250.00,
  "deposit_needed": 100.00
}
```

### Scenario 3: User Deposits and Reaches $250
```
1. User has $150 balance
2. User deposits $100
3. New balance: $250
4. System automatically grants access
5. User can now see and stake premium selections
6. No additional purchase needed
```

---

## API Endpoints

### Check Premium Code Access
```
GET /api/premium/check-code/<code>
Authorization: Bearer <jwt_token>
```

**Response for Eligible User ($250+):**
```json
{
  "booking": {
    "code": "PRM1234567",
    "name": "Weekend Acca Special",
    "selections": [
      {
        "match_id": 101,
        "home_team": "Chelsea",
        "away_team": "Arsenal",
        "market": "Full Time Result",
        "pick": "Home Win",
        "odds": 2.10
      }
    ],
    "total_odds": 12.50,
    "expires_at": "2025-12-10T18:00:00Z"
  },
  "has_access": true,
  "requires_deposit": false,
  "user_balance_usd": 300.00,
  "minimum_balance_required": 250.00,
  "deposit_needed": 0
}
```

**Response for Restricted User (<$250):**
```json
{
  "booking": {
    "code": "PRM1234567",
    "name": "Weekend Acca Special",
    "matches_preview": [
      {
        "match": "Chelsea vs Arsenal",
        "market": "Full Time Result"
      }
    ],
    "total_odds": "Hidden",
    "expires_at": "2025-12-10T18:00:00Z"
  },
  "has_access": false,
  "requires_deposit": true,
  "user_balance_usd": 150.00,
  "minimum_balance_required": 250.00,
  "deposit_needed": 100.00
}
```

### Legacy Purchase Endpoint (Now Balance Check)
```
POST /api/premium/purchase/<code>
Authorization: Bearer <jwt_token>
```

**Success Response (Balance >= $250):**
```json
{
  "message": "Access granted - you can now view and stake this premium booking",
  "booking": {
    "code": "PRM1234567",
    "selections": [...]
  },
  "has_access": true,
  "user_balance_usd": 300.00,
  "note": "No payment required - access is based on your balance"
}
```

**Insufficient Balance Response:**
```json
{
  "error": "Insufficient balance to access premium bookings",
  "message": "Please deposit funds to reach the minimum balance requirement",
  "required_minimum_balance": 250.00,
  "your_balance_usd": 150.00,
  "deposit_needed": 100.00,
  "has_access": false
}
```

---

## Frontend Integration

### 1. Check Code on Paste
```javascript
async function checkPremiumCode(code) {
  const token = localStorage.getItem('abkbet_token');
  
  const response = await fetch(`/api/premium/check-code/${code}`, {
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });
  
  const data = await response.json();
  
  if (data.has_access) {
    // User has $250+ - show full selections
    displayPremiumSelections(data.booking.selections);
    enableStakingButtons();
  } else if (data.requires_deposit) {
    // User has < $250 - show deposit prompt
    showDepositPrompt(data.deposit_needed, data.user_balance_usd);
    displayMatchPreviews(data.booking.matches_preview);
    disableStakingButtons();
  }
}
```

### 2. Display Logic
```javascript
function displayPremiumSelections(selections) {
  selections.forEach(selection => {
    const html = `
      <div class="premium-selection">
        <h4>${selection.home_team} vs ${selection.away_team}</h4>
        <p><strong>Market:</strong> ${selection.market}</p>
        <p><strong>Pick:</strong> ${selection.pick}</p>  <!-- VISIBLE -->
        <p><strong>Odds:</strong> ${selection.odds}</p>
        <button onclick="stakePremiumGame(${selection.match_id}, '${selection.pick}')">
          Stake This Game
        </button>
      </div>
    `;
    container.innerHTML += html;
  });
}

function displayMatchPreviews(previews) {
  previews.forEach(preview => {
    const html = `
      <div class="premium-preview">
        <h4>${preview.match}</h4>
        <p><strong>Market:</strong> ${preview.market}</p>
        <p class="locked">🔒 Pick hidden - deposit to unlock</p>
      </div>
    `;
    container.innerHTML += html;
  });
}
```

### 3. Deposit Prompt
```javascript
function showDepositPrompt(depositNeeded, currentBalance) {
  const message = `
    <div class="deposit-prompt">
      <h3>💰 Deposit Required</h3>
      <p>You need at least $250 balance to access premium selections.</p>
      <p><strong>Your Balance:</strong> $${currentBalance.toFixed(2)}</p>
      <p><strong>Deposit Needed:</strong> $${depositNeeded.toFixed(2)}</p>
      <button onclick="redirectToDeposit()">Deposit Now</button>
    </div>
  `;
  showModal(message);
}
```

### 4. Real-Time Balance Updates
```javascript
// After deposit completion, recheck access
async function onDepositComplete() {
  const code = getCurrentPremiumCode();
  
  // Refresh user profile to get new balance
  await fetchUserProfile();
  
  // Recheck premium code access
  await checkPremiumCode(code);
  
  // If balance now >= $250, selections will automatically show
}
```

---

## Admin Panel Integration

### Update Premium Booking Creation
```javascript
// No price field needed anymore - access is balance-based
function createPremiumBooking(data) {
  const booking = {
    name: data.name,
    selections: data.selections,
    expires_at: data.expiresAt,
    // price_usd: removed - no longer needed
    status: 'active'
  };
  
  return fetch('/api/premium/admin/create', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${adminToken}`
    },
    body: JSON.stringify(booking)
  });
}
```

### Analytics Update
```javascript
// Track access by balance level instead of purchases
async function getPremiumAnalytics() {
  const response = await fetch('/api/premium/admin/analytics', {
    headers: {'Authorization': `Bearer ${adminToken}`}
  });
  
  const data = await response.json();
  
  // New metrics:
  // - eligible_users: Users with $250+ balance
  // - restricted_users: Users with < $250 balance
  // - code_views: How many times codes were checked
  // - access_grants: How many users saw selections
  
  displayAnalytics(data);
}
```

---

## Database Considerations

### PremiumBookingPurchase Table
- **Status**: Table still exists but is no longer actively used
- **Legacy Data**: Previous purchase records remain for historical reporting
- **Future**: Can be removed in a future migration if not needed

### Code Changes
- `price_usd` field in `PremiumBooking` model is now optional/unused
- Access logic moved from purchase check to balance check
- No database writes when users access premium codes (read-only operation)

---

## Testing Checklist

### Test Case 1: User with Exactly $250
- [ ] Can see booking code
- [ ] Can see full selections
- [ ] Can stake games
- [ ] No deposit prompt

### Test Case 2: User with $249.99
- [ ] Can see booking code
- [ ] Cannot see selections (only previews)
- [ ] Cannot stake games
- [ ] Sees deposit prompt: "$0.01 needed"

### Test Case 3: User with $500
- [ ] Can see booking code
- [ ] Can see full selections
- [ ] Can stake multiple games
- [ ] Balance remains $500 (no deduction)

### Test Case 4: User Deposits from $200 to $250
- [ ] Initially sees only previews
- [ ] After deposit, automatically sees full selections
- [ ] Can stake without refresh
- [ ] No additional steps required

### Test Case 5: Balance Drops Below $250
- [ ] If user balance drops to $240 after bet settlement
- [ ] Should lose access to new premium code selections
- [ ] Existing bet slips remain valid
- [ ] Must deposit to regain access

---

## Migration from Purchase-Based System

### What Changed
1. **Removed**: Payment deduction from user balance
2. **Removed**: Purchase record creation (PremiumBookingPurchase)
3. **Changed**: Access check from "has purchased?" to "balance >= $250?"
4. **Added**: Automatic access grant when balance reaches threshold
5. **Simplified**: No "purchase" button - just "stake game" directly

### Backwards Compatibility
- `/api/premium/purchase/<code>` endpoint still exists
- Now returns immediate access for $250+ users without payment
- Frontend can continue using purchase endpoint or switch to check-code
- No breaking changes to existing API structure

### User Communication
**Old Message**: "Purchase this premium booking for $250"
**New Message**: "Access premium selections with $250+ balance"

**Old Flow**: Check code → Purchase → Pay $250 → See selections
**New Flow**: Check code → Balance verified → See selections (if $250+)

---

## Support & Troubleshooting

### Issue: User has $250 but still can't see selections
**Check**:
1. BTC conversion rate is correct (45000)
2. Balance is in BTC, not USD in database
3. Formula: `balance_btc * 45000 >= 250`
4. Minimum BTC required: 0.00556

### Issue: Selections show for user with $240
**Check**:
1. Verify check_premium_code logic
2. Ensure condition is `>=` not `>`
3. Check for rounding errors in USD conversion

### Issue: User balance changed but access didn't update
**Solution**:
- Frontend should refresh balance before checking premium codes
- Call `/api/auth/profile` to get latest balance
- Then call `/api/premium/check-code/<code>` with updated balance

---

## Future Enhancements

### Potential Features
1. **Dynamic Balance Tiers**
   - $250: Standard premium access
   - $500: VIP premium with higher odds
   - $1000: Exclusive premium codes

2. **Balance Alerts**
   - Notify users when balance drops below $250
   - Remind users to deposit to maintain premium access

3. **Premium Loyalty**
   - Users who maintain $250+ for 30 days get bonus codes
   - Reward consistent high-balance users

4. **Temporary Access**
   - Allow 24-hour premium trial for users with $100-$249
   - Encourage deposits through limited access

---

## Summary

### Key Points
- ✅ No payment required to access premium codes
- ✅ Access based purely on $250 minimum balance
- ✅ Selections automatically visible when balance >= $250
- ✅ Users can stake premium games multiple times
- ✅ Balance not deducted for viewing premium selections
- ✅ Simpler flow: just deposit and stake

### Balance Requirements
- **Minimum USD**: $250
- **Minimum BTC**: ~0.00556 BTC (at $45,000 per BTC)
- **Check Frequency**: Every time user checks a premium code
- **Access Duration**: Unlimited while balance >= $250
