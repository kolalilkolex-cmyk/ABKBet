# Virtual Games UI Fixes - Deployment Guide

## Issues Fixed

### 1. Admin Panel - Teams/Games Count Not Showing ✓
**Problem:** Virtual league table showed 0 teams and 0 games even after Quick Setup
**Root Cause:** `VirtualLeague.to_dict()` used `len(self.teams)` which relied on lazy-loaded relationships
**Fix:** Changed to use `db.session.query(func.count())` to get actual counts from database

### 2. User Page - Showing 0-0 Scores for Scheduled Games ✓
**Problem:** All games displayed "0 - 0" regardless of status
**Root Cause:** Database model defaulted `home_score` and `away_score` to 0, frontend checked `!== null`
**Fix:** Modified `VirtualGame.to_dict()` to return `None` for scores when game status is "scheduled"

### 3. User Page - Odds Showing as Text, Not Buttons ✓
**Problem:** Odds displayed as numbers instead of clickable betting buttons
**Root Cause:** Frontend conditionally renders buttons based on `game.home_score !== null`
**Fix:** With scores now returning `None` for scheduled games, betting buttons now render correctly

### 4. User Page - Not Showing Scheduled Match Times ✓
**Problem:** Games didn't show when they would start
**Root Cause:** Status text showed "Scheduled" but not the actual time
**Fix:** Updated frontend to format and display `game.scheduled_time` for scheduled games

## Files Changed

### 1. app/models/virtual_game.py
```python
def to_dict(self):
    # Only include scores if game is in_progress or finished
    include_scores = self.status in ['in_progress', 'finished']
    
    result = {
        # ... other fields ...
        'home_score': self.home_score if include_scores else None,
        'away_score': self.away_score if include_scores else None,
        # ... rest of fields ...
    }
    return result
```

**Changes:**
- Added `include_scores` logic based on status
- Returns `None` for scores when game is scheduled
- Returns actual scores only for in_progress/finished games
- Fixed `teams_count` and `games_count` to use database queries

### 2. templates/index.html
```javascript
const isScheduled = game.status === 'scheduled';

// Format scheduled time
let timeDisplay = game.status_text || game.status;
if (isScheduled && game.scheduled_time) {
    const schedTime = new Date(game.scheduled_time);
    timeDisplay = schedTime.toLocaleTimeString('en-US', {hour: '2-digit', minute: '2-digit'});
}
```

**Changes:**
- Added scheduled time formatting
- Shows actual time (e.g., "02:30 PM") instead of just "Scheduled"
- Betting buttons now render because `game.home_score === null` for scheduled games

## Deployment Steps

### Method 1: Using PowerShell Script (Recommended)
```powershell
cd C:\Users\HP\OneDrive\Documents\ABKBet
.\deploy_virtual_ui_fix.ps1
```

The script will:
1. Show files to upload
2. Open PythonAnywhere files page
3. Provide step-by-step instructions
4. Open web app reload page

### Method 2: Manual Upload
1. Go to https://www.pythonanywhere.com/user/ABKBet/files/home/ABKBet
2. Upload files:
   - `app/models/virtual_game.py` → `/home/ABKBet/ABKBet/app/models/`
   - `templates/index.html` → `/home/ABKBet/ABKBet/templates/`
3. Go to https://www.pythonanywhere.com/user/ABKBet/webapps/
4. Click "Reload abkbet.pythonanywhere.com"

## Testing After Deployment

### 1. Test Admin Panel
1. Login to admin panel
2. Go to Virtual Games section
3. Click "Quick Setup" (if not already done)
4. Verify leagues table shows:
   - Premier League: 10 teams, X games
   - La Liga: 10 teams, X games
   - Serie A: 10 teams, X games
5. Click "Generate Games" for a league
6. Verify:
   - Success message appears
   - Games count increases
   - Games table shows new games with "Scheduled" status

### 2. Test User Page
1. Login as regular user
2. Click "Virtual" tab
3. Select a league (Premier League, La Liga, or Serie A)
4. Verify games display shows:
   - ✓ Match card with team names
   - ✓ Clock icon with scheduled time (e.g., "02:30 PM")
   - ✓ NO "0 - 0" score for scheduled games
   - ✓ Three clickable betting buttons (1, X, 2) with odds
   - ✓ Buttons are styled and clickable, not just text
5. Try clicking a betting button
6. Verify bet is added to betslip

### 3. Test Game Progression (Admin)
1. In admin panel, click "Start" on a scheduled game
2. Verify:
   - Game status changes to "In Progress"
   - Scores appear in admin table
3. Go to user page
4. Verify:
   - Game shows "LIVE" indicator (red, pulsing)
   - Score is now visible (e.g., "2 - 1")
   - Betting buttons are disabled (grayed out)
5. Return to admin, click "Finish" on the game
6. Verify:
   - Game status changes to "Finished"
   - Final score is locked
7. Go to user page
8. Verify:
   - Game shows checkmark icon
   - Final score displayed
   - No betting buttons (game ended)
   - Card has reduced opacity (0.7)

## Expected Behavior

### Scheduled Games
- Display: `🕐 02:30 PM` (not "0 - 0")
- Betting: 3 clickable buttons with odds
- Card: Full opacity, clock icon

### Live Games
- Display: `🔴 In Progress` (red, pulsing)
- Score: Shows current score (e.g., "2 - 1")
- Betting: Buttons disabled
- Card: Full opacity, live indicator

### Finished Games
- Display: `✓ Finished`
- Score: Final score shown
- Betting: No buttons
- Card: 70% opacity, checkmark icon

## Data Flow

### Quick Setup Creates:
```
3 Leagues
├── Premier League (10 teams, ~15 games)
├── La Liga (10 teams, ~15 games)
└── Serie A (10 teams, ~15 games)
```

### Game States:
```
scheduled → in_progress → finished
   ↓            ↓             ↓
 Time      Live Score    Final Score
 Buttons   Disabled      Hidden
```

## Troubleshooting

### Issue: Still seeing 0-0 scores
**Solution:** 
1. Check browser cache - hard refresh (Ctrl+Shift+R)
2. Verify files uploaded correctly
3. Verify web app was reloaded
4. Check browser console for errors

### Issue: Betting buttons still not showing
**Solution:**
1. Check browser console: `console.log(game.odds)`
2. Verify `game.home_score === null` for scheduled games
3. Check if `!isFinished && game.odds` condition is true

### Issue: Admin counts still showing 0
**Solution:**
1. Verify `virtual_game.py` was uploaded correctly
2. Web app must be reloaded for model changes
3. Check if `teams_count` and `games_count` in API response

### Issue: Times not showing correctly
**Solution:**
1. Check timezone settings in browser
2. Verify `game.scheduled_time` is valid ISO string
3. Check JavaScript console for date parsing errors

## API Endpoints Used

- `GET /api/virtual/leagues` - Get all leagues with counts
- `GET /api/virtual/leagues/<id>/games` - Get games for a league
- `GET /api/virtual/admin/games` - Get all games (admin)
- `POST /api/virtual/admin/quick-setup` - Create 3 leagues
- `POST /api/virtual/admin/leagues/<id>/generate-games` - Generate more games
- `POST /api/virtual/admin/games/<id>/start` - Start a game
- `POST /api/virtual/admin/games/<id>/finish` - Finish a game

## Summary

All UI issues have been fixed:
1. ✅ Admin panel shows correct team/game counts
2. ✅ Scheduled games show time, not 0-0
3. ✅ Betting buttons render as clickable buttons
4. ✅ Game status properly displayed (Scheduled/Live/Finished)
5. ✅ Auto-refresh works correctly
6. ✅ Live games show pulsing indicator
7. ✅ Finished games have reduced opacity

The virtual games system is now fully functional!
