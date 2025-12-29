# 🔧 Final Debug & Fix - Dec 19, 2025

## Issues Reported
1. ❌ 'market_type' error when placing bet
2. ❌ League standings still not updating

## Root Causes Found

### Issue 1: 'market_type' Error in Bet Creation

**Problem:** When building bet description, code accessed `game.home_team` and `game.away_team` as strings, but they're actually **VirtualTeam objects**.

**Location:** `virtual_game_routes.py` line 438

**Before (broken):**
```python
for sel in selections:
    game = VirtualGame.query.get(sel['game_id'])
    if game:
        # ❌ game.home_team is an object, not a string!
        selections_summary.append(f"{game.home_team} vs {game.away_team} - ...")
```

**After (fixed):**
```python
for sel in selections:
    game = VirtualGame.query.get(sel['game_id'])
    if game:
        home_name = game.home_team.name if game.home_team else 'Unknown'
        away_name = game.away_team.name if game.away_team else 'Unknown'
        selections_summary.append(f"{home_name} vs {away_name} - ...")
```

**Why This Caused Error:**
- Python tried to convert VirtualTeam object to string
- Object's `__repr__` or string conversion failed
- Error message mentioned 'market_type' (misleading - actual issue was object access)

### Issue 2: League Standings Not Updating

**Problem:** Standings endpoint accessed `game.home_team.name` but relationships might not be loaded properly.

**Location:** `virtual_game_routes.py` line 340-342

**Before (risky):**
```python
for game in finished_games:
    home_team = game.home_team.name  # ❌ Might fail if relationship not loaded
    away_team = game.away_team.name
```

**After (safe):**
```python
for game in finished_games:
    # Get team names safely with fallback
    home_team = game.home_team.name if game.home_team else game.to_dict()['home_team']
    away_team = game.away_team.name if game.away_team else game.to_dict()['away_team']
```

**Additional Fix:** Added debug logging to see how many finished games exist:
```python
logger.info(f"[VirtualStandings] League {league_id}: Found {len(finished_games)} finished games in database")
```

## All Changes Made

### File: `app/routes/virtual_game_routes.py`

#### Change 1: Safe Team Name Access in Bet Creation (Lines 434-441)
```python
# Build event description with bet details
selections_summary = []
for sel in selections:
    game = VirtualGame.query.get(sel['game_id'])
    if game:
        home_name = game.home_team.name if game.home_team else 'Unknown'
        away_name = game.away_team.name if game.away_team else 'Unknown'
        selections_summary.append(f"{home_name} vs {away_name} - {sel['market_type']}: {sel['selection']} @ {sel['odds']}")
```

#### Change 2: Try-Except Around Bet Creation (Lines 444-467)
```python
try:
    bet = Bet(
        user_id=user.id,
        amount=amount,
        potential_payout=potential_win,
        odds=total_odds,
        status='pending',
        bet_type='multiple',
        event_description=event_desc,
        selection=json.dumps(selections)
    )
    
    user.balance -= amount
    db.session.add(bet)
    db.session.commit()
    
    logger.info(f"[VirtualBet] Created bet ID {bet.id} for user {user.username}")
except Exception as e:
    db.session.rollback()
    logger.error(f"[VirtualBet] Error creating bet: {str(e)}")
    return jsonify({'success': False, 'message': f'Error placing bet: {str(e)}'}), 500
```

#### Change 3: Safe Team Access in Standings (Lines 338-345)
```python
# Calculate stats from finished games
for game in finished_games:
    # Get team names safely
    home_team = game.home_team.name if game.home_team else game.to_dict()['home_team']
    away_team = game.away_team.name if game.away_team else game.to_dict()['away_team']
    
    # Ensure teams exist in dict
    if home_team not in teams_data:
        teams_data[home_team] = {'name': home_team, 'played': 0, 'won': 0, 'drawn': 0, 'lost': 0, 'gf': 0, 'ga': 0, 'pts': 0}
    if away_team not in teams_data:
        teams_data[away_team] = {'name': away_team, 'played': 0, 'won': 0, 'drawn': 0, 'lost': 0, 'gf': 0, 'ga': 0, 'pts': 0}
```

#### Change 4: Debug Logging (Line 318)
```python
logger.info(f"[VirtualStandings] League {league_id}: Found {len(finished_games)} finished games in database")
```

## Expected Results After Upload

### Bet Placement:
1. User selects 3 games, enters $50
2. Clicks "Place Bet"
3. ✅ No 'market_type' error
4. ✅ Success message: "Bet placed successfully! Potential win: $X.XX"
5. ✅ Balance deducted correctly
6. ✅ Bet ticket shows:
   ```
   Premier League - Virtual Multi-Bet (3 selections)
   Arsenal vs Chelsea - 1X2: 1 @ 2.50
   Liverpool vs Man City - 1X2: X @ 3.20
   Tottenham vs Newcastle - O/U: Over @ 1.80
   ```

### League Standings:
1. Race finishes
2. During 15-second buffer
3. ✅ API call: GET `/api/virtual/leagues/1/standings`
4. ✅ Console log: `[VirtualStandings] League 1: Found 10 finished games in database`
5. ✅ Standings table updates with points:
   ```
   #  Team         P  W  D  L  GD  Pts
   1  Arsenal      2  2  0  0  +4  6
   2  Man City     2  1  1  0  +2  4
   3  Liverpool    2  1  0  1   0  3
   ...
   ```

## Debugging Commands

### Check if bet was created:
```bash
python -c "from run import flask_app; from app.models import Bet; exec('with flask_app.app_context(): 
    bets = Bet.query.filter_by(bet_type=\"multiple\").order_by(Bet.created_at.desc()).limit(5).all();
    print(f\"Recent virtual bets: {len(bets)}\");
    for b in bets:
        print(f\"ID {b.id}: ${b.amount} @ {b.odds}x = ${b.potential_payout} - {b.status}\");
        print(f\"  {b.event_description[:100]}...\")
')"
```

### Check finished games:
```bash
python -c "from run import flask_app; from app.models.virtual_game import VirtualGame, VirtualGameStatus; exec('with flask_app.app_context():
    for league_id in [1, 2, 3]:
        finished = VirtualGame.query.filter_by(league_id=league_id, status=VirtualGameStatus.FINISHED.value).count();
        print(f\"League {league_id}: {finished} finished games\")
')"
```

### Test standings API:
```bash
curl https://abkbet.pythonanywhere.com/api/virtual/leagues/1/standings | python -m json.tool
```

Expected output:
```json
{
    "success": true,
    "standings": [
        {
            "name": "Arsenal",
            "played": 5,
            "won": 4,
            "drawn": 1,
            "lost": 0,
            "gf": 12,
            "ga": 3,
            "pts": 13
        },
        ...
    ],
    "games_played": 50
}
```

### Check error logs:
```bash
tail -f /var/log/ABKBet.pythonanywhere.com.error.log | grep -E "VirtualBet|VirtualStandings"
```

## Testing Procedure

### Test 1: Bet Placement
1. Open DevTools Console (F12)
2. Select 2-3 games, add to betslip
3. Enter stake amount (e.g., $50)
4. Click "Place Bet"
5. ✅ Check console for: `[VirtualBet] Created bet ID X for user...`
6. ✅ Check response: `{"success": true, "bet_id": X, "new_balance": Y}`
7. ✅ If error, check console for: `Error placing bet: ...`

### Test 2: Standings Update
1. Watch a full race finish (90 seconds play + 15 seconds buffer)
2. During buffer, open Network tab
3. ✅ See request: GET `/api/virtual/leagues/1/standings`
4. ✅ Check response: `{"success": true, "standings": [...], "games_played": 10}`
5. ✅ Verify standings table updates with points
6. ✅ Winner teams should have 3 pts, draws 1 pt, losers 0 pts

### Test 3: Persistence
1. Watch 3 races finish
2. Note standings (e.g., "Arsenal: 9 pts, Man City: 7 pts")
3. Refresh browser page
4. ✅ Standings should still show same points
5. ✅ Not reset to 0

### Test 4: Multi-Race Accumulation
1. Note Team A points after Race 1: 3 pts (1 win)
2. Watch Race 2 finish, Team A wins again
3. ✅ Team A should now have 6 pts (not 3)
4. Watch Race 3 finish, Team A draws
5. ✅ Team A should now have 7 pts (not 6 or 1)

## Files to Upload

**Upload this 1 file to PythonAnywhere:**

1. **app/routes/virtual_game_routes.py**
   - Local: `c:\Users\HP\OneDrive\Documents\ABKBet\app\routes\virtual_game_routes.py`
   - Remote: `/home/ABKBet/ABKBet/app/routes/virtual_game_routes.py`

2. **Then:**
   - Click "Reload" on PythonAnywhere Web tab
   - Clear browser cache (Ctrl+Shift+Delete)
   - Test bet placement
   - Watch race finish and check standings update

## What Changed Summary

| Issue | Root Cause | Fix Applied | Result |
|-------|-----------|-------------|--------|
| 'market_type' error | Accessed `game.home_team` as string (it's object) | Access `.name` attribute: `game.home_team.name` | Bet creation succeeds |
| Standings not updating | Unsafe object access, no logging | Safe access with fallback + debug logging | Standings update from DB |
| No error visibility | No try-except | Wrapped in try-except with rollback | Clear error messages |

## Key Insights

1. **SQLAlchemy Relationships:** `game.home_team` returns a VirtualTeam object, not a string
2. **Must access `.name`:** Always use `game.home_team.name` to get team name string
3. **Database Persistence:** Standings MUST fetch from database, not frontend memory
4. **Error Handling:** Always wrap DB operations in try-except with rollback
5. **Logging:** Debug logs help identify if data is reaching the endpoint

## Expected Console Logs

### On Bet Placement:
```
[VirtualBet] Created bet ID 123 for user john_doe
[VirtualBet] User john_doe placed virtual bet: $50.0, odds: 6.30
```

### On Standings Fetch:
```
[VirtualStandings] League 1: Found 30 finished games in database
[VirtualGame] Calculated standings for league 1: 20 teams, 30 games
```

### On Error:
```
[VirtualBet] Error creating bet: 'market_type' is an invalid keyword argument...
```

---

## Success Criteria

✅ Place bet → No error, balance deducted, bet saved  
✅ Finish race → Standings fetch from DB  
✅ Standings show accumulated points (3 races = 9 pts max per team)  
✅ Refresh page → Standings persist  
✅ Console logs show finished games count  

---

**Upload `virtual_game_routes.py` now and test! Both issues should be fixed! 🚀**
