# API Integration Guide

## Getting Started with Football APIs

### Option 1: API-Football (Recommended) ⭐

**Best for:** Comprehensive football data with live scores and odds

#### Setup Steps:

1. **Sign up for RapidAPI**
   - Go to https://rapidapi.com/
   - Create a free account

2. **Subscribe to API-Football**
   - Visit https://rapidapi.com/api-sports/api/api-football
   - Choose a plan:
     - **Free**: 100 requests/day (good for testing)
     - **Basic**: $10/month - 3,000 requests/day
     - **Pro**: $30/month - 10,000 requests/day
     - **Ultra**: $60/month - 30,000 requests/day

3. **Get your API Key**
   - After subscribing, go to the "Endpoints" tab
   - Copy your `X-RapidAPI-Key` from the code snippets

4. **Configure in .env**
   ```bash
   FOOTBALL_API_KEY=your-rapidapi-key-here
   FOOTBALL_API_ENABLED=true
   ```

5. **Test the API**
   ```bash
   curl --request GET \
     --url 'https://v3.football.api-sports.io/fixtures?live=all' \
     --header 'x-apisports-key: your-key-here'
   ```

#### Request Limits
- Free: 100 requests/day (~4/hour)
- Basic: 3,000/day (~125/hour)
- Pro: 10,000/day (~416/hour)

Our background tasks use approximately:
- Live matches: 2,880 requests/day (every 30s)
- Odds updates: 288 requests/day (every 5min)
- **Total: ~3,200 requests/day minimum**

**Recommendation:** Start with **Basic plan ($10/month)** for production

---

### Option 2: The Odds API

**Best for:** Betting odds from multiple bookmakers

#### Setup Steps:

1. **Sign up**
   - Go to https://the-odds-api.com/
   - Create account and get API key

2. **Choose Plan**
   - Free: 500 requests/month
   - Starter: $10/month - 5,000 requests
   - Pro: $25/month - 20,000 requests

3. **Configure**
   ```bash
   ODDS_API_KEY=your-odds-api-key
   ```

#### Integration Code
```python
# app/services/odds_api.py
import requests

class OddsAPIService:
    BASE_URL = "https://api.the-odds-api.com/v4"
    
    def __init__(self, api_key):
        self.api_key = api_key
    
    def get_odds(self, sport='soccer_epl'):
        endpoint = f"{self.BASE_URL}/sports/{sport}/odds"
        params = {
            'apiKey': self.api_key,
            'regions': 'uk,us,eu',
            'markets': 'h2h,spreads,totals'
        }
        response = requests.get(endpoint, params=params)
        return response.json()
```

---

### Option 3: SportMonks

**Best for:** Multiple sports with comprehensive statistics

#### Setup Steps:

1. **Sign up**
   - Go to https://www.sportmonks.com/
   - Create account

2. **Choose Plan**
   - Starter: €19/month
   - Professional: €49/month
   - Enterprise: Custom pricing

3. **Configure**
   ```bash
   SPORTMONKS_API_KEY=your-sportmonks-token
   ```

---

### Option 4: LiveScore API

**Enterprise-level solution**

1. **Contact Sales**
   - Visit https://www.livescore.com/en/api/
   - Request pricing quote

2. **Enterprise Features**
   - Real-time push notifications
   - 99.9% uptime SLA
   - Dedicated support
   - Custom data feeds

---

## Quick Start Guide

### 1. Install Dependencies
```bash
cd /path/to/ABKBet
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Setup Redis
```bash
# Ubuntu/Debian
sudo apt install redis-server
sudo systemctl start redis

# macOS
brew install redis
brew services start redis

# Windows
# Download from: https://github.com/microsoftarchive/redis/releases
```

### 3. Configure Environment
```bash
cp .env.example .env
nano .env
```

Add your API key:
```
FOOTBALL_API_KEY=your-api-key-here
FOOTBALL_API_ENABLED=true
REDIS_URL=redis://localhost:6379/0
```

### 4. Run Database Migrations
```bash
flask db upgrade
```

### 5. Start Celery Worker
```bash
# Terminal 1: Start Celery worker
celery -A celery_app worker --loglevel=info

# Terminal 2: Start Celery beat (scheduler)
celery -A celery_app beat --loglevel=info
```

### 6. Start Flask Application
```bash
# Terminal 3: Start Flask
python run.py
```

### 7. Test the Integration
```bash
# Check if matches are being fetched
curl http://localhost:5000/api/matches

# Check WebSocket connection
# Open browser console at http://localhost:5000
# Socket.IO should connect automatically
```

---

## Background Tasks Explained

### Task 1: Fetch Live Matches (Every 30 seconds)
```python
# Runs: 2,880 times/day
# API Calls: 2,880/day (one per execution)
# Purpose: Update live scores in real-time
```

### Task 2: Update Match Odds (Every 5 minutes)
```python
# Runs: 288 times/day
# API Calls: 288/day (for ~50 matches)
# Purpose: Keep betting odds up-to-date
```

### Task 3: Fetch Upcoming Matches (Every hour)
```python
# Runs: 24 times/day
# API Calls: 24/day
# Purpose: Add new matches to the system
```

### Task 4: Settle Finished Matches (Every 2 minutes)
```python
# Runs: 720 times/day
# API Calls: 0 (uses local data)
# Purpose: Automatically settle bets
```

**Total API Usage:** ~3,200 requests/day

---

## Cost Comparison

### Monthly Costs

| Service | Plan | Requests | Price | Best For |
|---------|------|----------|-------|----------|
| API-Football | Basic | 3,000/day | $10 | Starting out |
| API-Football | Pro | 10,000/day | $30 | Growing site |
| The Odds API | Starter | 5,000/month | $10 | Odds only |
| SportMonks | Starter | Varies | €19 | Multi-sport |
| LiveScore | Enterprise | Unlimited | Custom | Large scale |

### Optimization Tips

1. **Cache Frequently Accessed Data**
   ```python
   # Use Redis to cache match data
   redis_client.setex(f'match:{match_id}', 300, json.dumps(match_data))
   ```

2. **Batch API Requests**
   ```python
   # Fetch multiple matches in one request
   matches = api.get_fixtures(league_ids=[39, 140, 135])
   ```

3. **Adjust Update Intervals**
   ```python
   # Reduce frequency during low-traffic hours
   if hour >= 22 or hour <= 6:
       schedule = 300.0  # 5 minutes instead of 30 seconds
   ```

4. **Smart Polling**
   ```python
   # Only update matches that are actually live
   if match.status in ['1H', '2H', 'HT']:
       update_match(match)
   ```

---

## Testing Without API Key

For development without an API key:

1. **Use Mock Data**
   ```bash
   FOOTBALL_API_ENABLED=false
   ```

2. **Create Sample Matches**
   ```bash
   python scripts/create_sample_data.py
   ```

3. **Manual Match Creation**
   ```python
   # In Python shell
   from app.models.game_pick import GamePick
   from app import db
   
   match = GamePick(
       match_name="Manchester United vs Liverpool",
       league="Premier League",
       home_team="Manchester United",
       away_team="Liverpool",
       kick_off_time=datetime.utcnow(),
       odds_home=2.5,
       odds_draw=3.2,
       odds_away=2.8
   )
   db.session.add(match)
   db.session.commit()
   ```

---

## Monitoring API Usage

### Check Remaining Requests
```python
# app/services/football_api.py

def check_api_status(self):
    response = requests.get(
        f"{self.BASE_URL}/status",
        headers=self.headers
    )
    data = response.json()
    return {
        'requests_remaining': data['requests']['remaining'],
        'requests_limit': data['requests']['limit_day']
    }
```

### Log API Calls
```python
import logging

logger.info(f"API Call: {endpoint} - Remaining: {remaining_requests}")
```

### Set Up Alerts
```python
if remaining_requests < 100:
    send_alert_email("API quota running low!")
```

---

## Troubleshooting

### Error: "Too Many Requests (429)"
**Solution:** You've exceeded your API quota
- Upgrade your plan
- Reduce polling frequency
- Implement caching

### Error: "Unauthorized (401)"
**Solution:** Invalid API key
- Check your .env file
- Verify key is correct
- Re-subscribe if expired

### Error: "No Data Returned"
**Solution:** API endpoint might have changed
- Check API documentation
- Verify endpoint URLs
- Test with curl/Postman

### Celery Tasks Not Running
**Solution:** Redis not running or misconfigured
```bash
# Check Redis
redis-cli ping  # Should return PONG

# Check Celery logs
celery -A celery_app worker --loglevel=debug
```

---

## Support & Resources

- **API-Football Docs:** https://www.api-football.com/documentation-v3
- **The Odds API Docs:** https://the-odds-api.com/liveapi/guides/v4/
- **Celery Docs:** https://docs.celeryq.dev/
- **Flask-SocketIO Docs:** https://flask-socketio.readthedocs.io/

---

## Next Steps

1. ✅ Get API key from API-Football
2. ✅ Configure .env file
3. ✅ Install Redis
4. ✅ Start Celery workers
5. ✅ Test live match updates
6. ✅ Monitor API usage
7. ✅ Deploy to production
