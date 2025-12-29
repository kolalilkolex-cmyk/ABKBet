# Virtual Games - Compact UI with Auto-Play Integration Guide

## 🎯 What's Fixed

### 1. ✅ Betting Integration
- Virtual bets now properly add to the main betslip
- Uses existing betslip UI (no separate interface)
- Works with existing `placeBetslipBet()` function

### 2. ✅ Compact UI
- Grid layout (3 columns on desktop)
- Much smaller cards (320px width)
- No full-page takeover
- Professional, clean design

### 3. ✅ Auto-Play System
- **4-minute countdown** before each game starts
- **40-second live game** with auto-updating scores
- **Auto-finish** when game completes
- **Staggered leagues**: Each league offset by 80 seconds

### 4. ✅ Live Score Animation
- Scores update every 3 seconds during live games
- Flash animation when score changes
- Progress bar shows game progression
- Minute indicator (0' - 90')

## 📁 Files to Replace

### File 1: index.html (Virtual Tab Content)

**Find this section** (around line 1917-1970):
```html
<!-- Virtual Tab -->
<div class="tab-content" id="virtualContent" style="display: none;">
    <!-- Virtual League Tabs -->
    <div style="display: flex; gap: 10px; margin-bottom: 20px; flex-wrap: wrap;">
        <button id="vLeague1" class="filter-btn active" onclick="loadVirtualLeague(1)" style="flex: 1; min-width: 150px;">
            <i class="fas fa-trophy"></i> Premier League
        </button>
        <button id="vLeague2" class="filter-btn" onclick="loadVirtualLeague(2)" style="flex: 1; min-width: 150px;">
            <i class="fas fa-trophy"></i> La Liga
        </button>
        <button id="vLeague3" class="filter-btn" onclick="loadVirtualLeague(3)" style="flex: 1; min-width: 150px;">
            <i class="fas fa-trophy"></i> Serie A
        </button>
    </div>
    
    <!-- Virtual Games Container -->
    <div id="virtualGamesContainer" class="matches-grid">
        <div class="payment-form" style="text-align: center; padding: 60px 20px;">
            <div style="font-size: 64px; margin-bottom: 20px;">⚽</div>
            <h2 style="color: #60a5fa; margin-bottom: 10px;">Virtual Games</h2>
            <p style="color: #94a3b8; margin-bottom: 30px;">Fast-paced virtual football matches</p>
            <div class="loading-spinner">
                <i class="fas fa-spinner fa-spin"></i>
                <span>Loading games...</span>
            </div>
        </div>
    </div>
</div>
```

**Replace with:**
```html
<!-- Virtual Tab -->
<div class="tab-content" id="virtualContent" style="display: none;">
    <div class="virtual-compact-container">
        <!-- Virtual League Tabs -->
        <div class="virtual-league-tabs">
            <button id="vLeague1" class="virtual-league-tab active" onclick="showVirtualLeague(1)">
                <i class="fas fa-trophy"></i> Premier League
            </button>
            <button id="vLeague2" class="virtual-league-tab" onclick="showVirtualLeague(2)">
                <i class="fas fa-trophy"></i> La Liga
            </button>
            <button id="vLeague3" class="virtual-league-tab" onclick="showVirtualLeague(3)">
                <i class="fas fa-trophy"></i> Serie A
            </button>
        </div>
        
        <!-- Virtual Games Grid -->
        <div class="virtual-games-grid" id="virtualGamesContainer">
            <div style="grid-column: 1/-1; text-align: center; padding: 60px 20px;">
                <div style="font-size: 64px; margin-bottom: 20px;">⚽</div>
                <h2 style="color: #60a5fa; margin-bottom: 10px;">Virtual Games</h2>
                <p style="color: #94a3b8; margin-bottom: 30px;">Fast-paced virtual football matches</p>
                <div class="loading-spinner">
                    <i class="fas fa-spinner fa-spin"></i>
                    <span>Loading games...</span>
                </div>
            </div>
        </div>
    </div>
</div>
```

### File 2: index.html (Replace Virtual Games JavaScript)

**Find this section** (around line 8014-8170):
```javascript
<script>
    // Virtual Games JavaScript
    let currentVirtualLeague = null;
    let virtualGamesInterval = null;

    async function loadVirtualGames() {
        // ... existing code ...
    }
    
    async function loadVirtualLeague(leagueId) {
        // ... existing code ...
    }
    
    function addVirtualBet(game, market, selection, odd) {
        // ... existing code ...
    }
</script>
```

**Replace entire section with the content from:** `virtual_games_compact.html`

## 🚀 Quick Installation Steps

### Step 1: Copy Styles
1. Open `virtual_games_compact.html`
2. Copy everything between `<style>` and `</style>` tags
3. In `index.html`, find the `<style>` section (around line 100)
4. Paste at the end of the style section, before `</style>`

### Step 2: Replace HTML Structure
1. In `index.html`, find `<!-- Virtual Tab -->` (around line 1917)
2. Replace the entire virtual tab content with the new HTML from above

### Step 3: Replace JavaScript
1. In `index.html`, find the Virtual Games JavaScript section (around line 8014)
2. Delete everything from `// Virtual Games JavaScript` to the end of that script block
3. Paste the new JavaScript from `virtual_games_compact.html`

### Step 4: Hook into existing betslip
Find the `clearBetslip()` function (around line 5500) and update it to clear virtual bets too:

```javascript
function clearBetslip() {
    betslip = [];
    virtualSelectedBets = [];  // ADD THIS LINE
    updateBetslip();
    updateBetslipUI();  // ADD THIS LINE
}
```

Find the `placeBetslipBet()` function (around line 5600) and update to handle virtual bets:

```javascript
async function placeBetslipBet() {
    if (!client.token) {
        showMessage('Please log in to place bets', 'error');
        return;
    }
    
    const stake = parseFloat(document.getElementById('betslipStake').value);
    if (!stake || stake < 1) {
        showMessage('Please enter a valid stake (minimum $1)', 'error');
        return;
    }
    
    // Check if there are virtual bets
    if (virtualSelectedBets && virtualSelectedBets.length > 0) {
        try {
            const betData = {
                stake: stake,
                selections: virtualSelectedBets.map(bet => ({
                    game_id: bet.gameId,
                    market: '1X2',
                    selection: bet.selection,
                    odd: bet.odd
                }))
            };
            
            const response = await fetch('/api/virtual/bets', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${client.token}`
                },
                body: JSON.stringify(betData)
            });
            
            const data = await response.json();
            
            if (data.success) {
                showMessage(`Virtual bet placed successfully! Bet ID: ${data.bet_id}`, 'success');
                clearVirtualBetslip();
                await refreshUserBalance();
            } else {
                showMessage(data.error || 'Failed to place virtual bet', 'error');
            }
        } catch (error) {
            console.error('Error placing virtual bet:', error);
            showMessage('Error placing virtual bet', 'error');
        }
        return;
    }
    
    // ... rest of existing betslip code for regular bets ...
}
```

## 🎮 How It Works

### Game Flow
```
┌─────────────────┐
│  4 MIN COUNTDOWN │  ← Users can bet during this time
│  (240 seconds)  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   GAME STARTS   │  ← Auto-start when countdown reaches 0
│   (LIVE - 40s)  │
└────────┬────────┘
         │
         ├─► Score updates every 3 seconds
         ├─► Progress bar shows time
         ├─► Minute indicator (0'-90')
         │
         ▼
┌─────────────────┐
│  GAME FINISHES  │  ← Auto-finish after 40 seconds
│  (FULL TIME)    │
└─────────────────┘
```

### League Staggering
- **Premier League**: Starts at 0s, 280s, 560s, 840s...
- **La Liga**: Starts at 80s, 360s, 640s, 920s...
- **Serie A**: Starts at 160s, 440s, 720s, 1000s...

This ensures users always have games to bet on!

### Score Generation
- Random score updates every 3 seconds
- 30% chance of goal per update
- 50/50 chance for home/away
- Flash animation when score changes

## ✅ Testing Checklist

After integration:

- [ ] Virtual tab shows compact grid layout
- [ ] Three league tabs work correctly
- [ ] Games show 4-minute countdown
- [ ] Clicking odds adds to main betslip
- [ ] Betslip shows "Virtual League X" label
- [ ] Countdown decreases every second
- [ ] Game auto-starts at 0:00
- [ ] Live games show animated scores
- [ ] Progress bar moves during game
- [ ] Game auto-finishes after 40 seconds
- [ ] Different leagues have offset timing
- [ ] Can place virtual bets using main betslip
- [ ] Virtual bets clear when placed

## 📊 Configuration

You can adjust timing in `VIRTUAL_CONFIG`:

```javascript
const VIRTUAL_CONFIG = {
    COUNTDOWN_SECONDS: 240,        // Change countdown duration
    GAME_DURATION_SECONDS: 40,     // Change game length
    LEAGUE_OFFSET_SECONDS: 80,     // Change league stagger
    UPDATE_INTERVAL_MS: 1000,      // Timer update speed
    SCORE_UPDATE_INTERVAL_MS: 3000 // Score change frequency
};
```

## 🐛 Troubleshooting

**Issue:** "Betting functionality not available"
- **Fix:** Make sure `virtualSelectedBets` is defined globally
- Check that `updateBetslipUI()` function exists

**Issue:** Games don't auto-start
- **Fix:** Check browser console for errors
- Ensure `startVirtualUpdateLoop()` is called

**Issue:** Scores don't update
- **Fix:** Check `updateAllVirtualGames()` is running
- Verify `game.isLive` is set to true

**Issue:** All leagues start at same time
- **Fix:** Check `calculateCountdown()` applies league offset
- Verify `LEAGUE_OFFSET_SECONDS` is set correctly

## 📱 Mobile Responsive

The compact UI is fully responsive:
- Desktop: 3 columns
- Tablet: 2 columns
- Mobile: 1 column

Adjust in CSS:
```css
.virtual-games-grid {
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));  /* Change 280px for mobile */
}
```

## 🎯 Next Steps

After successful integration:

1. Upload `index.html` to PythonAnywhere
2. Reload web app
3. Test countdown and auto-play
4. Place test bets
5. Verify bet settlement (backend needed)

## 🔗 Backend Requirements

The compact UI expects these endpoints (already exist):
- `GET /api/virtual/leagues` - Get all leagues
- `GET /api/virtual/leagues/<id>/games` - Get league games
- `POST /api/virtual/bets` - Place virtual bet
- `POST /api/virtual/admin/games/<id>/finish` - Settle game (admin)

The auto-finish should trigger bet settlement on the backend!
