# ABKBet - Bitcoin Betting Platform

A full-featured betting platform built with Python Flask that accepts Bitcoin as payment method. Users can place bets, deposit/withdraw Bitcoin, and track their betting history.

## Features

### Core Features
- **User Authentication**: JWT-based authentication with secure password hashing
- **Email Notifications**: Automated emails for registration and password changes
- **Bitcoin Wallet Integration**: Automatic wallet creation for each user
- **Bitcoin Payments**: Deposit and withdrawal support with transaction verification
- **Betting System**: Create bets with custom odds and track results
- **User Statistics**: Win rate, ROI, and betting history tracking
- **Admin Panel**: Manage bets, users, and transactions

### Bitcoin Integration
- Generate unique Bitcoin addresses for each user
- Verify transactions on blockchain
- Track confirmations
- Fee estimation
- Support for Bitcoin testnet and mainnet

### API Endpoints

#### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login user
- `GET /api/auth/profile` - Get user profile
- `POST /api/auth/change-password` - Change password

#### Payments
- `GET /api/payment/wallet` - Get wallet information
- `GET /api/payment/balance` - Get BTC balance
- `POST /api/payment/deposit` - Record deposit
- `POST /api/payment/withdraw` - Initiate withdrawal
- `GET /api/payment/transactions` - Transaction history
- `GET /api/payment/fee-estimate` - Bitcoin network fees

#### Betting
- `POST /api/bets` - Create new bet
- `GET /api/bets/<id>` - Get bet details
- `GET /api/bets/user/all` - Get all user bets
- `GET /api/bets/active` - Get active bets
- `GET /api/bets/statistics` - Get user statistics
- `POST /api/bets/<id>/cancel` - Cancel bet

#### Admin
- `POST /api/admin/bets/<id>/settle` - Settle bet
- `GET /api/admin/users` - List all users
- `GET /api/admin/users/<id>` - Get user details
- `GET /api/admin/transactions` - List transactions
- `GET /api/admin/statistics` - Platform statistics

## Installation

### Prerequisites
- Python 3.8+
- pip
- Bitcoin wallet (for testing on testnet)

### Setup Steps

1. **Clone and navigate to project**
```bash
cd c:\Users\HP\Documents\ABKBet
```

2. **Create virtual environment**
```bash
python -m venv venv
venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment**
```bash
copy .env.example .env
```

Edit `.env` with your settings:
```
FLASK_ENV=development
DATABASE_URL=sqlite:///betting.db
JWT_SECRET_KEY=your-secret-key-here
BITCOIN_NETWORK=testnet
```

5. **Run application**
```bash
python run.py
```

Server will start at `http://localhost:5000`

## Project Structure

```
ABKBet/
├── app/
│   ├── models/
│   │   └── __init__.py          # Database models (User, Bet, Wallet, Transaction)
│   ├── services/
│   │   ├── bitcoin_service.py   # Bitcoin blockchain operations
│   │   ├── payment_service.py   # Deposit/withdrawal logic
│   │   └── betting_service.py   # Bet creation and settlement
│   ├── routes/
│   │   ├── auth_routes.py       # Authentication endpoints
│   │   ├── payment_routes.py    # Payment endpoints
│   │   ├── bet_routes.py        # Betting endpoints
│   │   └── admin_routes.py      # Admin endpoints
│   ├── utils/
│   │   ├── auth.py              # Password hashing utilities
│   │   └── decorators.py        # JWT and auth decorators
│   └── __init__.py
├── templates/                    # HTML templates (future)
├── static/                       # Static files (CSS, JS)
├── config.py                     # Configuration management
├── run.py                        # Application entry point
├── requirements.txt              # Python dependencies
└── README.md                     # This file
```

## Usage Examples

### Register User
```bash
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "player1",
    "email": "player1@example.com",
    "password": "secure_password"
  }'
```

### Get Wallet Address
```bash
curl -X GET http://localhost:5000/api/payment/wallet \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### Create Bet
```bash
curl -X POST http://localhost:5000/api/bets \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "amount": 0.01,
    "odds": 2.5,
    "bet_type": "sports",
    "event_description": "Manchester United vs Liverpool"
  }'
```

### Deposit Bitcoin
```bash
curl -X POST http://localhost:5000/api/payment/deposit \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "tx_hash": "abc123def456...",
    "amount": 0.05
  }'
```

## Database Models

### User
- id, username (unique), email (unique)
- password_hash, balance (BTC)
- created_at, updated_at, is_active
- Relationships: wallet, bets, transactions

### Wallet
- id, user_id, bitcoin_address (unique)
- private_key_encrypted, total_received, total_sent
- created_at, updated_at

### Transaction
- id, user_id, tx_hash (unique)
- amount, transaction_type (deposit/withdrawal)
- status (pending/confirmed/failed/cancelled)
- confirmations, from_address, to_address
- fee, created_at, confirmed_at

### Bet
- id, user_id, amount, odds
- potential_payout, bet_type, event_description
- status (pending/active/won/lost/cancelled)
- result, settled_payout
- created_at, settled_at, expires_at

## Security Features

- JWT-based authentication with token expiration
- Password hashing with Werkzeug
- CORS configuration
- SQL injection prevention (SQLAlchemy ORM)
- Secure Bitcoin address generation
- Private key encryption (recommended for production)
- Transaction verification with blockchain confirmation

## Production Deployment

For production deployment:

1. **Use PostgreSQL** instead of SQLite
2. **Set strong JWT_SECRET_KEY**
3. **Enable HTTPS**
4. **Use environment-based configuration**
5. **Implement rate limiting**
6. **Set up monitoring and logging**
7. **Use Gunicorn as WSGI server**:
   ```bash
   gunicorn -w 4 -b 0.0.0.0:5000 run:app
   ```

## Testing

Run tests with:
```bash
pytest tests/
```

## Bitcoin Integration Details

### Network Options
- **Testnet**: For development and testing (use test BTC)
- **Mainnet**: Production (use real BTC)

### Address Generation
Uses the `bit` library for secure Bitcoin address generation. Each user gets a unique address.

### Transaction Verification
- Queries BlockExplorer or similar service
- Verifies confirmation count
- Validates amount received
- Tracks transaction status

### Fee Estimation
Fetches current Bitcoin network fees from bitcoinfees.earn.com

## Troubleshooting

### Bitcoin connection issues
- Verify network setting (testnet vs mainnet)
- Check API rate limits
- Use different blockchain API if primary is down

### Database issues
- Delete `betting.db` to reset database
- Check DATABASE_URL in `.env`
- Ensure write permissions in directory

### JWT token issues
- Verify JWT_SECRET_KEY is set
- Check token expiration (30 days default)
- Ensure Authorization header format: `Bearer TOKEN`

## Future Enhancements

- [ ] Web UI dashboard
- [ ] Mobile app
- [ ] Multiple cryptocurrency support (Ethereum, etc.)
- [ ] Advanced betting types
- [ ] Live odds updates
- [ ] Bonus/promotion system
- [ ] Two-factor authentication
- [ ] Affiliate system
- [ ] Live chat support
- [ ] Automated bet settlement

## License

MIT License - feel free to use and modify

## Support

For issues or questions, please create an issue in the repository.

---

**Built with Python Flask, SQLAlchemy, and Bitcoin integration** ⚡
