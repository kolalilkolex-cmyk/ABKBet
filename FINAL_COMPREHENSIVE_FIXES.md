# 🎯 FINAL COMPREHENSIVE FIXES - Virtual Games

## Issues to Fix

### Issue 1: Virtual Games Reset on Page Load
**Problem:** When user clicks virtual tab, games always start from MD1 Race 1 instead of continuing
**Solution:** Load current race state from backend API

### Issue 2: Bet Placement Not Working
**Problem:** User can add bets to betslip but "Place Bet" button doesn't work for virtual games
**Solution:** Create `placeVirtualBetslip()` function and update bet placement endpoint

### Issue 3: Add Standings Table
**Problem:** Empty space on left side when on Virtual/Premium/My Bets tabs
**Solution:** Add season standings table showing current league positions

---

## Implementation Plan

### Part 1: Backend - Add Race State Tracking

#### New Endpoint: Get Current Race Info
Add to `virtual_game_routes.py`:

```python
@virtual_game_bp.route('/admin/leagues/<int:league_id>/race-info', methods=['GET'])
@jwt_required()
def get_league_race_info(league_id):
    """Get current race information for a league"""
    try:
        league = VirtualLeague.query.get(league_id)
        if not league:
            return jsonify({'success': False, 'message': 'League not found'}), 404
        
        # Get latest finished game to determine current race
        latest_game = VirtualGame.query.filter_by(
            league_id=league_id
        ).order_by(VirtualGame.scheduled_start.desc()).first()
        
        # Count total finished games to calculate race number
        finished_count = VirtualGame.query.filter_by(
            league_id=league_id,
            status='finished'
        ).count()
        
        # Each race has 10 games, so race_number = (finished_count // 10) + 1
        current_race = (finished_count // 10) + 1
        current_season = ((current_race - 1) // 38) + 1
        
        # Get current scheduled games
        current_games = VirtualGame.query.filter_by(
            league_id=league_id,
            status='scheduled'
        ).count()
        
        return jsonify({
            'success': True,
            'race_number': min(current_race, 38),
            'season_number': current_season,
            'finished_games': finished_count,
            'current_games': current_games,
            'total_races': 38
        }), 200
    except Exception as e:
        logger.error(f"[VirtualGame] Error getting race info: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500
```

### Part 2: Backend - Virtual Bet Placement

#### Add Virtual Bet Endpoint
Add to `virtual_game_routes.py`:

```python
@virtual_game_bp.route('/bets/place', methods=['POST'])
@jwt_required()
def place_virtual_bet():
    """Place a bet on virtual games"""
    try:
        user = User.query.get(get_jwt_identity())
        if not user:
            return jsonify({'success': False, 'message': 'User not found'}), 404
        
        data = request.get_json()
        amount = float(data.get('amount', 0))
        selections = data.get('selections', [])
        
        if amount <= 0:
            return jsonify({'success': False, 'message': 'Invalid bet amount'}), 400
        
        if not selections:
            return jsonify({'success': False, 'message': 'No selections provided'}), 400
        
        # Check user balance
        if user.balance < amount:
            return jsonify({'success': False, 'message': 'Insufficient balance'}), 400
        
        # Calculate total odds
        total_odds = 1.0
        for sel in selections:
            total_odds *= float(sel.get('odd', 1))
        
        potential_win = amount * total_odds
        
        # Create bet record (you'll need to create VirtualBet model)
        # For now, use the regular Bet model with a flag
        from app.models import Bet
        
        bet = Bet(
            user_id=user.id,
            amount=amount,
            potential_winnings=potential_win,
            total_odds=total_odds,
            bet_type='virtual',  # Add this field to Bet model
            status='pending'
        )
        
        # Deduct from balance
        user.balance -= amount
        
        db.session.add(bet)
        db.session.commit()
        
        logger.info(f"[VirtualBet] User {user.username} placed virtual bet: ${amount}, odds: {total_odds:.2f}")
        
        return jsonify({
            'success': True,
            'message': f'Bet placed! Potential win: ${potential_win:.2f}',
            'bet_id': bet.id,
            'new_balance': user.balance
        }), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"[VirtualBet] Error placing bet: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500
```

### Part 3: Frontend - State Persistence

Update `index.html` initialization to load race state:

```javascript
async function initVirtualGames() {
    if (virtualInitialized) return;
    virtualInitialized = true;
    try {
        const response = await fetch('/api/virtual/leagues');
        const data = await response.json();
        if (data.success && data.leagues.length > 0) {
            // Load race state for each league
            for (const league of data.leagues) {
                const raceInfo = await fetch(`/api/virtual/admin/leagues/${league.id}/race-info`, {
                    headers: {'Authorization': `Bearer ${localStorage.getItem('abkbet_token')}`}
                });
                const raceData = await raceInfo.json();
                
                if (raceData.success) {
                    virtualLeagueStates[league.id].raceNumber = raceData.race_number;
                    virtualLeagueStates[league.id].seasonNumber = raceData.season_number;
                }
                
                await loadVirtualLeagueGames(league.id, false);
            }
            startVirtualUpdateLoop();
            showVirtualLeague(1);
        }
    } catch (error) {
        console.error('Error initializing virtual games:', error);
    }
}
```

### Part 4: Frontend - Bet Placement Function

```javascript
async function placeVirtualBetslip() {
    if (virtualSelectedBets.length === 0) {
        showMessage('❌ No virtual bets selected', 'error');
        return;
    }
    
    const amountInput = document.getElementById('betslipAmount');
    const amount = parseFloat(amountInput?.value || 0);
    
    if (amount <= 0) {
        showMessage('❌ Please enter a valid bet amount', 'error');
        return;
    }
    
    const token = localStorage.getItem('abkbet_token');
    if (!token) {
        showMessage('❌ Please login to place bets', 'error');
        return;
    }
    
    try {
        const response = await fetch('/api/virtual/bets/place', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({
                amount: amount,
                selections: virtualSelectedBets.map(bet => ({
                    game_id: bet.gameId,
                    market: bet.market,
                    selection: bet.selection,
                    odd: bet.odd,
                    home_team: bet.home,
                    away_team: bet.away,
                    league_name: bet.leagueName
                }))
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            showMessage(`✅ ${data.message}`, 'success');
            // Clear betslip
            virtualSelectedBets = [];
            updateVirtualBetslipUI();
            amountInput.value = '';
            // Update balance display if exists
            if (window.updateBalance) updateBalance(data.new_balance);
        } else {
            showMessage(`❌ ${data.message}`, 'error');
        }
    } catch (error) {
        console.error('Error placing virtual bet:', error);
        showMessage('❌ Error placing bet. Please try again.', 'error');
    }
}
```

### Part 5: Frontend - Standings Table Component

Add HTML structure (in virtual games section):

```html
<!-- Add this before the games grid -->
<div class="virtual-standings-sidebar" id="virtualStandings" style="display: none;">
    <div style="background: #1e293b; border-radius: 12px; padding: 16px; margin-bottom: 16px;">
        <h3 style="color: #e2e8f0; font-size: 16px; font-weight: 700; margin-bottom: 12px; display: flex; align-items: center;">
            <i class="fas fa-trophy" style="color: #fbbf24; margin-right: 8px;"></i>
            Season Standings
        </h3>
        <div id="standingsTable"></div>
    </div>
</div>
```

Add JavaScript to generate standings:

```javascript
async function loadVirtualStandings(leagueId) {
    try {
        // In a real implementation, you'd have a backend endpoint
        // For now, calculate from games
        const games = virtualGames[leagueId] || [];
        const teams = {};
        
        // Calculate standings from finished games
        games.filter(g => g.status === 'finished').forEach(game => {
            // Initialize teams
            if (!teams[game.home_team]) teams[game.home_team] = {name: game.home_team, played: 0, won: 0, drawn: 0, lost: 0, gf: 0, ga: 0, pts: 0};
            if (!teams[game.away_team]) teams[game.away_team] = {name: game.away_team, played: 0, won: 0, drawn: 0, lost: 0, gf: 0, ga: 0, pts: 0};
            
            teams[game.home_team].played++;
            teams[game.away_team].played++;
            teams[game.home_team].gf += game.home_score;
            teams[game.home_team].ga += game.away_score;
            teams[game.away_team].gf += game.away_score;
            teams[game.away_team].ga += game.home_score;
            
            if (game.home_score > game.away_score) {
                teams[game.home_team].won++;
                teams[game.home_team].pts += 3;
                teams[game.away_team].lost++;
            } else if (game.home_score < game.away_score) {
                teams[game.away_team].won++;
                teams[game.away_team].pts += 3;
                teams[game.home_team].lost++;
            } else {
                teams[game.home_team].drawn++;
                teams[game.away_team].drawn++;
                teams[game.home_team].pts++;
                teams[game.away_team].pts++;
            }
        });
        
        // Sort by points, then goal difference
        const standings = Object.values(teams).sort((a, b) => {
            if (b.pts !== a.pts) return b.pts - a.pts;
            return (b.gf - b.ga) - (a.gf - a.ga);
        });
        
        // Render table
        const html = `
            <div style="max-height: 600px; overflow-y: auto;">
                <table style="width: 100%; font-size: 12px; border-collapse: collapse;">
                    <thead style="position: sticky; top: 0; background: #334155; z-index: 10;">
                        <tr style="color: #94a3b8; font-weight: 600;">
                            <th style="padding: 8px 4px; text-align: left;">#</th>
                            <th style="padding: 8px 4px; text-align: left;">Team</th>
                            <th style="padding: 8px 4px; text-align: center;">P</th>
                            <th style="padding: 8px 4px; text-align: center;">W</th>
                            <th style="padding: 8px 4px; text-align: center;">D</th>
                            <th style="padding: 8px 4px; text-align: center;">L</th>
                            <th style="padding: 8px 4px; text-align: center;">GD</th>
                            <th style="padding: 8px 4px; text-align: center; color: #fbbf24;">Pts</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${standings.map((team, idx) => {
                            const pos = idx + 1;
                            const posColor = pos <= 4 ? '#10b981' : pos <= 6 ? '#3b82f6' : pos >= 18 ? '#ef4444' : '#94a3b8';
                            return `
                                <tr style="border-bottom: 1px solid #334155;">
                                    <td style="padding: 8px 4px; color: ${posColor}; font-weight: 700;">${pos}</td>
                                    <td style="padding: 8px 4px; color: #e2e8f0; font-weight: 600;">${team.name}</td>
                                    <td style="padding: 8px 4px; text-align: center; color: #cbd5e1;">${team.played}</td>
                                    <td style="padding: 8px 4px; text-align: center; color: #10b981;">${team.won}</td>
                                    <td style="padding: 8px 4px; text-align: center; color: #fbbf24;">${team.drawn}</td>
                                    <td style="padding: 8px 4px; text-align: center; color: #ef4444;">${team.lost}</td>
                                    <td style="padding: 8px 4px; text-align: center; color: #cbd5e1;">${team.gf - team.ga}</td>
                                    <td style="padding: 8px 4px; text-align: center; color: #fbbf24; font-weight: 700;">${team.pts}</td>
                                </tr>
                            `;
                        }).join('')}
                    </tbody>
                </table>
            </div>
        `;
        
        document.getElementById('standingsTable').innerHTML = html;
        document.getElementById('virtualStandings').style.display = 'block';
    } catch (error) {
        console.error('Error loading standings:', error);
    }
}

// Call this when showing a league
function showVirtualLeague(leagueId) {
    document.querySelectorAll('.virtual-league-tab').forEach(btn => btn.classList.remove('active'));
    document.getElementById(`vLeague${leagueId}`)?.classList.add('active');
    renderVirtualGames(leagueId);
    loadVirtualStandings(leagueId);  // Add this line
}
```

---

## Summary of Changes

### Files to Update:

1. **app/routes/virtual_game_routes.py**
   - Add `get_league_race_info()` endpoint
   - Add `place_virtual_bet()` endpoint

2. **templates/index.html**
   - Update `initVirtualGames()` to load race state
   - Add `placeVirtualBetslip()` function
   - Add `loadVirtualStandings()` function
   - Add standings HTML component
   - Update `showVirtualLeague()` to load standings

### Expected Results:

✅ **Issue 1 Solved:** Virtual games continue from current race when page reloads
✅ **Issue 2 Solved:** Place Bet button works for virtual games
✅ **Issue 3 Solved:** Standings table shows on left side with live positions

---

## Testing Checklist

- [ ] Load page → Click Virtual → Should show current race (not always MD1)
- [ ] Add virtual bets to betslip → Click Place Bet → Should place successfully
- [ ] View standings table → Should show team positions with points
- [ ] Watch games finish → Standings should update automatically
- [ ] After race finishes → New race loads but standings persist

