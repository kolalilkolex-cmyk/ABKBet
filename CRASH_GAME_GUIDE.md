# 🚀 ABKBet Crash Game - Complete Guide

## ✅ Installation Complete!

Your Crash/Aviator game has been successfully added to ABKBet! Here's what was created:

### 📁 Files Created/Modified:

1. **Backend**: `app/routes/crash_routes.py` - Game logic and API endpoints
2. **Frontend**: Updated `templates/index.html` - Game UI and JavaScript
3. **App**: Updated `run.py` - Registered crash game blueprint
4. **Automation**: `run_crash_game.py` - Auto-run script for game rounds

---

## 🎮 How the Crash Game Works

### For Players:
1. **Betting Phase** (5 seconds): Players place their bets
2. **Flying Phase**: Multiplier starts at 1.00x and increases
3. **Cash Out**: Players can cash out anytime to lock in winnings
4. **Crash**: Game randomly crashes - players who didn't cash out lose

### Game Features:
- ✅ **Provably Fair**: Uses cryptographic hashing for fairness
- ✅ **Real-time Multiplier**: Updates every 100ms
- ✅ **Smooth Animation**: Plane flies across screen
- ✅ **History Display**: Shows last 50 crash points
- ✅ **Mobile Responsive**: Works on all devices
- ✅ **Balance Integration**: Uses existing USD balance system

---

## 🚀 How to Run

### Option 1: Manual Testing (Development)

1. **Start your Flask server**:
   ```bash
   python run.py
   ```

2. **In another terminal, run the crash automation**:
   ```bash
   python run_crash_game.py
   ```

3. **Login and play**:
   - Go to http://127.0.0.1:5000
   - Login to your account
   - Click the **Crash** tab
   - Place your bet and try to cash out before it crashes!

### Option 2: Production Deployment

For production, you'll want to run the crash game automation as a background service.

#### On PythonAnywhere:

1. **Upload files**:
   - Upload `app/routes/crash_routes.py`
   - Upload updated `run.py`
   - Upload updated `templates/index.html`

2. **Reload your web app**

3. **Set up scheduled task** (PythonAnywhere Dashboard):
   - Add a new scheduled task
   - Run: `python3 /home/yourusername/ABKBet/run_crash_game.py`
   - However, this won't work well as scheduled tasks run once per day

4. **Better option - Use an always-on console**:
   - Open a Bash console in PythonAnywhere
   - Run: `python3 run_crash_game.py &`
   - This runs it in the background
   - Note: Free PythonAnywhere accounts have limited console time

#### On VPS/Dedicated Server:

1. **Install and run as systemd service**:

Create `/etc/systemd/system/abkbet-crash.service`:
```ini
[Unit]
Description=ABKBet Crash Game Automation
After=network.target

[Service]
Type=simple
User=your_user
WorkingDirectory=/path/to/ABKBet
ExecStart=/usr/bin/python3 /path/to/ABKBet/run_crash_game.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Then:
```bash
sudo systemctl daemon-reload
sudo systemctl enable abkbet-crash
sudo systemctl start abkbet-crash
sudo systemctl status abkbet-crash
```

---

## 🎨 Game Mechanics

### Multiplier Growth
- Starts at **1.00x**
- Grows exponentially: `1.00 * (1.0024 ^ (elapsed_time * 100))`
- Smooth, fast growth that can reach 100x, 1000x, or even higher!

### Crash Point Distribution
- **Most games**: Crash between 1.5x - 3.0x
- **Common**: 3x - 10x
- **Rare**: 10x - 50x
- **Very Rare**: 50x - 100x+
- **Ultra Rare**: 1000x+ 🌟

### House Edge
- **3% house edge**
- Fair and competitive
- Provably fair system ensures transparency

### Color Coding (History)
- 🔴 **Red** (< 2.0x): Low multiplier
- 🔵 **Blue** (2.0x - 5.0x): Medium multiplier
- 🟢 **Green** (5.0x - 10.0x): High multiplier
- 🟡 **Gold** (10.0x+): Mega multiplier (pulsing animation!)

---

## 📊 API Endpoints

### `GET /api/crash/status`
Get current game status
```json
{
  "game_id": 1735123456789,
  "status": "flying",
  "multiplier": 2.45,
  "player_count": 12,
  "history": [...]
}
```

### `POST /api/crash/bet`
Place a bet (requires JWT auth)
```json
{
  "amount": 10.00
}
```

### `POST /api/crash/cashout`
Cash out current bet (requires JWT auth)
```json
{
  "success": true,
  "multiplier": 2.45,
  "winnings": 24.50,
  "profit": 14.50
}
```

### `POST /api/crash/start`
Start the game (automation)

### `POST /api/crash/reset`
Reset for next round (automation)

---

## 🔧 Customization

### Change Game Speed
In `crash_routes.py`, line ~98:
```python
multiplier = 1.00 * (1.0024 ** (elapsed * 100))
```
- Increase `1.0024` = faster growth
- Decrease `1.0024` = slower growth

### Change House Edge
In `crash_routes.py`, line ~34:
```python
if random_value < 0.03:  # 3% house edge
    return 1.00
```

### Change Betting Phase Duration
In `run_crash_game.py`, line ~13:
```python
time.sleep(5)  # 5 second betting phase
```

### Change Colors/Styling
In `index.html`, search for `.crash-` classes and modify CSS

---

## 🐛 Troubleshooting

### "No active game to cash out from"
- The game has already crashed
- Try cashing out earlier next round

### "Betting is closed for this round"
- Game already started flying
- Wait for next round (5 seconds after crash)

### "Insufficient balance"
- Add funds to your wallet
- Or lower your bet amount

### Crash automation not running
- Check if `run_crash_game.py` is running
- Check server URL in the script matches your deployment
- Check server logs for errors

### Game stuck on "Waiting for next round"
- Automation script is not running
- Start `python run_crash_game.py`

---

## 📈 Future Enhancements (Optional)

1. **Auto Bet**: Let players set auto-bet with auto-cashout at specific multiplier
2. **Live Players**: Show who's betting and cashing out in real-time
3. **Chat**: Add live chat for players
4. **Leaderboard**: Biggest wins, highest multipliers
5. **Statistics**: Player win rate, average multiplier, etc.
6. **Sound Effects**: Add sounds for takeoff, cash out, crash
7. **Animation**: Better graphics/animations for the plane

---

## 🎉 You're Done!

Your crash game is ready! Players can now:
- ✅ Place bets during waiting phase
- ✅ Watch multiplier grow in real-time
- ✅ Cash out before crash to win
- ✅ View game history
- ✅ See other players betting

**Enjoy your new game! 🚀**

---

## 📞 Need Help?

If you encounter any issues:
1. Check browser console (F12) for JavaScript errors
2. Check Flask server logs for backend errors  
3. Make sure automation script is running
4. Verify all files were uploaded correctly

**Have fun and play responsibly!** 🎮
