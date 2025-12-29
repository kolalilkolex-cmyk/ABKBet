# Football API Integration Setup Guide

## Overview
This guide helps you integrate API-Football to fetch real matches and odds automatically.

## Free Tier Limits
- **100 requests per day**
- Resets every 24 hours
- Perfect for testing and small deployments

---

## Step 1: Get Your API Key

1. **Sign up** at https://www.api-football.com/
2. **Verify your email**
3. **Go to Dashboard**: https://dashboard.api-football.com/
4. **Copy your API Key** (it will look like: `abc123def456...`)

---

## Step 2: Configure Environment Variables

### Windows PowerShell:
```powershell
$env:FOOTBALL_API_KEY='your_api_key_here'
$env:FOOTBALL_API_ENABLED='true'
```

### Linux/Mac:
```bash
export FOOTBALL_API_KEY='your_api_key_here'
export FOOTBALL_API_ENABLED='true'
```

### Permanent Setup (Windows):
Add to your system environment variables:
1. Search "Environment Variables" in Windows
2. Click "New" under User Variables
3. Add `FOOTBALL_API_KEY` with your key
4. Add `FOOTBALL_API_ENABLED` with value `true`

---

## Step 3: Populate Initial Matches

Run this command to fetch upcoming matches (next 7 days):

```powershell
python scripts/populate_api_matches.py
```

**Expected output:**
```
API-Football Match Population Script
✓ API Key configured: abc123def4...
✓ API Enabled: true

Fetching upcoming matches (next 7 days)...
✓ Found 150 matches from API

Syncing matches to database...

Results:
  • New matches created: 150
  • Existing matches updated: 0
  • Total processed: 150

✓ Success! Matches are now available on your site
```

---

## Step 4: Start Odds Update Loop (Optional but Recommended)

This keeps odds updated automatically every 15 minutes:

```powershell
python scripts/update_odds_loop.py
```

**Expected output:**
```
API-Football Odds Update Loop
Updates odds every 15 minutes

✓ API Key configured
✓ Update interval: 15 minutes

Press Ctrl+C to stop

[Iteration 1] 2024-01-15 14:30:00
Checking for live matches...
  ✓ Live matches: 0 new, 5 updated
Updating odds for 45 matches...
  ✓ Updated: 45, Failed: 0

⏰ Next update in 15 minutes...
```

**To run in background:**
- Windows: Run in a separate PowerShell window
- Linux/Mac: `python scripts/update_odds_loop.py &`

---

## Step 5: Verify Integration

1. **Visit your site**: http://localhost:5000
2. **Check Matches tab**: You should see real matches from API
3. **Check odds**: Matches should have realistic odds (not 2.0/3.0/2.5)
4. **Look for live matches**: Any matches currently in progress

---

## Troubleshooting

### "API Key not configured"
- Make sure you set `FOOTBALL_API_KEY` environment variable
- Restart your terminal after setting environment variables
- Check spelling: `FOOTBALL_API_KEY` (all caps)

### "No matches found or API request failed"
- Verify your API key is correct (copy-paste from dashboard)
- Check your internet connection
- Try visiting https://v3.football.api-sports.io/status in browser with your key

### "Rate limit exceeded"
- You've used all 100 requests for today
- Wait 24 hours for reset
- Reduce update frequency (edit `UPDATE_INTERVAL` in update_odds_loop.py)

### Matches show default odds (2.0/3.0/2.5)
- Odds haven't been fetched yet
- Run `python scripts/update_odds_loop.py` to fetch odds
- Some matches may not have odds available from bookmakers yet

---

## API Request Budget Management

With **100 requests/day**, here's how to use them efficiently:

### Option 1: Conservative (Recommended for Testing)
- Populate matches: **1 request**
- Update odds every 30 minutes: **48 requests/day**
- Check live matches hourly: **24 requests/day**
- **Total: ~75 requests/day** ✓

### Option 2: Frequent Updates
- Update odds every 15 minutes: **96 requests/day**
- **Total: ~96 requests/day** ✓

### Option 3: Real-time (Uses all requests)
- Update odds every 10 minutes: **144 requests/day** ✗ **TOO MANY**

**Tip:** Start with Option 1, then adjust based on your needs

---

## What's Included

### Leagues Supported
The API covers **800+ leagues** worldwide, including:
- ⚽ Premier League (England)
- ⚽ La Liga (Spain)
- ⚽ Bundesliga (Germany)
- ⚽ Serie A (Italy)
- ⚽ Ligue 1 (France)
- ⚽ Champions League
- ⚽ Europa League
- ⚽ And many more...

### Data Fetched
- **Match details**: Teams, league, date/time
- **Live scores**: Updated in real-time
- **Match status**: Scheduled, Live (1H, HT, 2H), Finished
- **Betting odds**: 1X2, Over/Under, Both Teams Score, etc.

---

## Files Created

1. **`app/services/football_api_service.py`**
   - Core API service with all methods
   - Handles fetching matches, odds, syncing to database

2. **`scripts/populate_api_matches.py`**
   - One-time script to fetch initial matches
   - Run manually when you want to refresh match list

3. **`scripts/update_odds_loop.py`**
   - Background script to keep odds updated
   - Runs continuously, checks every 15 minutes

---

## Next Steps After Setup

1. **Test betting**: Place a bet on a real match
2. **Monitor live matches**: Watch scores update automatically
3. **Check odds changes**: See odds fluctuate over time
4. **Add more leagues**: Modify scripts to fetch specific leagues

---

## Advanced: Filter Specific Leagues

Edit `scripts/populate_api_matches.py` to fetch only specific leagues:

```python
# Instead of get_upcoming_matches(), use:
leagues = football_api.get_popular_leagues()
matches = football_api.get_today_matches(league_id=leagues['premier_league'])
```

Available leagues:
- `premier_league`: 39
- `la_liga`: 140
- `bundesliga`: 78
- `serie_a`: 135
- `ligue_1`: 61
- `champions_league`: 2

---

## Support

If you encounter issues:
1. Check API-Football status: https://status.api-football.com/
2. View API documentation: https://www.api-football.com/documentation-v3
3. Check your daily usage: Dashboard → Statistics

---

**🎉 That's it! Your site now has real football matches and odds!**
