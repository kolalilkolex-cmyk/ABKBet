# Quick Start Guide - ABKBet Bitcoin Betting Platform

Get ABKBet up and running in 5 minutes!

## System Requirements

- Python 3.8 or higher
- pip (Python package manager)
- 200MB disk space
- Internet connection for Bitcoin network

## Installation (Windows)

### 1. Navigate to Project Directory

```powershell
cd c:\Users\HP\Documents\ABKBet
```

### 2. Run Setup Script

```powershell
.\setup.bat
```

This will:
- Create a Python virtual environment
- Install all dependencies
- Create a `.env` configuration file
- Initialize the database

### 3. Configure Environment

Edit `.env` file (created during setup):

```env
FLASK_ENV=development
FLASK_DEBUG=True
DATABASE_URL=sqlite:///betting.db
JWT_SECRET_KEY=your-secret-key-change-this
BITCOIN_NETWORK=testnet
```

### 4. Start the Application

```powershell
# Activate virtual environment
venv\Scripts\activate

# Run the application
python run.py
```

You should see:
```
WARNING in werkzeug: Running on http://127.0.0.1:5000
```

### 5. Access the Web Interface

Open your browser and go to:
```
http://localhost:5000/templates/index.html
```

## Installation (Linux/Mac)

### 1. Navigate to Project Directory

```bash
cd ~/Documents/ABKBet
# or wherever you extracted the project
```

### 2. Run Setup Script

```bash
chmod +x setup.sh
./setup.sh
```

### 3. Configure Environment

```bash
vi .env
# Edit the configuration as needed
```

### 4. Start the Application

```bash
# Activate virtual environment
source venv/bin/activate

# Run the application
python run.py
```

### 5. Access the Web Interface

Open browser to:
```
http://localhost:5000/templates/index.html
```

## First Steps

### 1. Register an Account

1. Go to http://localhost:5000/templates/index.html
2. Click "Register"
3. Fill in:
   - Username: `testuser`
   - Email: `test@example.com`
   - Password: `testpassword123`
4. Click "Register"

### 2. View Your Bitcoin Wallet

1. Click on "Wallet" tab
2. Your Bitcoin address is displayed
3. Use this address to receive Bitcoin payments

**For Testnet Testing:**
- Get testnet Bitcoin from: https://testnet-faucet.mempool.space/
- Send a small amount (0.001-0.1 BTC) to your address

### 3. Create Your First Bet

1. Wait for Bitcoin to arrive in your wallet
2. Click "Bets" tab
3. Fill in:
   - Bet Amount: `0.001`
   - Odds: `2.5`
   - Bet Type: `Sports`
   - Event Description: `Test bet`
4. Click "Place Bet"

### 4. Check Your Statistics

1. Click "Stats" tab
2. View your betting statistics
3. Track your win rate and ROI

## Testing Bitcoin Payments

### Using Bitcoin Testnet

1. **Get a testnet wallet:**
   - Download: https://github.com/bitcoin/bitcoin/releases (Bitcoin-Qt)
   - Or use online: https://testnet-faucet.mempool.space/

2. **Get testnet coins:**
   - Go to: https://testnet-faucet.mempool.space/
   - Enter your wallet address
   - Receive test Bitcoin

3. **Send to ABKBet:**
   - Copy your ABKBet wallet address from the Wallet tab
   - Send coins using your testnet wallet
   - Wait for confirmation

4. **Verify deposit:**
   - Check the Wallet tab
   - Balance should update after 1-2 minutes

## Testing with API

Use curl or Postman to test API endpoints:

### Register User

```bash
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "password123"
  }'
```

### Login

```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "password123"
  }'
```

Response includes `access_token` - save this for other requests.

### Get Wallet

```bash
curl -X GET http://localhost:5000/api/payment/wallet \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

### Create Bet

```bash
curl -X POST http://localhost:5000/api/bets \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 0.001,
    "odds": 2.5,
    "bet_type": "sports",
    "event_description": "Test bet"
  }'
```

### Get Balance

```bash
curl -X GET http://localhost:5000/api/payment/balance \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

## Database Management

### View Database

SQLite database is stored in `betting.db`

### Reset Database

```bash
python manage_db.py reset
```

This will clear all data and start fresh.

### Initialize Database

```bash
python manage_db.py init
```

## Troubleshooting

### Port Already in Use

If port 5000 is in use:

```bash
# Change port in run.py
app.run(debug=True, host='0.0.0.0', port=5001)

# Or find and kill the process
lsof -i :5000
kill -9 <PID>
```

### Bitcoin Connection Issues

1. Check internet connection
2. Verify `BITCOIN_NETWORK` is set to `testnet` for testing
3. Check blockchain explorer: https://testnet.blockexplorer.com/

### Virtual Environment Issues

```bash
# Remove and recreate venv
rm -rf venv
python -m venv venv
venv\Scripts\activate  # Windows
# or
source venv/bin/activate  # Linux/Mac

pip install -r requirements.txt
```

### Database Locked

```bash
# Close the application
# Delete betting.db
# Reinitialize
python manage_db.py init
```

## Next Steps

1. **Read the full documentation:**
   - [README.md](README.md) - Overview and features
   - [API_DOCUMENTATION.md](API_DOCUMENTATION.md) - Complete API reference
   - [DEPLOYMENT.md](DEPLOYMENT.md) - Production deployment

2. **Explore the code:**
   - `app/models/` - Database models
   - `app/services/` - Business logic
   - `app/routes/` - API endpoints

3. **Customize for your needs:**
   - Update betting types and odds calculations
   - Add more payment methods
   - Customize the frontend UI

4. **Deploy to production:**
   - Follow [DEPLOYMENT.md](DEPLOYMENT.md) guide
   - Set up HTTPS
   - Configure for mainnet Bitcoin

## Support

For issues or questions:

1. Check the [README.md](README.md) FAQ section
2. Review error logs in the terminal
3. Check SQLite database: `betting.db`
4. Test API endpoints with curl/Postman

## Security Note

**For Development Only:**
This setup uses SQLite and basic configuration. For production:

1. Use PostgreSQL
2. Generate strong JWT secret
3. Enable HTTPS
4. Implement rate limiting
5. Set up proper logging
6. Use environment variables for secrets
7. Implement 2FA authentication
8. Regular security audits

## Bitcoin Mainnet

To use real Bitcoin instead of testnet:

1. Set `BITCOIN_NETWORK=mainnet` in `.env`
2. Get real Bitcoin
3. Configure real Bitcoin private keys
4. Set up production database
5. Deploy to secure server

**⚠️ WARNING:** Handle real Bitcoin carefully! Start with small amounts to test.

## Common Commands

```bash
# Activate environment
venv\Scripts\activate

# Deactivate environment
deactivate

# Run application
python run.py

# Reset database
python manage_db.py reset

# Test Bitcoin integration
python test_bitcoin.py

# Run tests
pytest tests.py

# Start development server
python run.py

# Stop server
CTRL+C
```

---

**Ready to start betting? Register now and receive testnet Bitcoin to begin!** 🚀
