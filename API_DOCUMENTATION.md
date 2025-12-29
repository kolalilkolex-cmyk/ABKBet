# API Documentation

## Authentication Endpoints

### Register User
**POST** `/api/auth/register`

Register a new user account.

**Request Body:**
```json
{
  "username": "player1",
  "email": "player1@example.com",
  "password": "secure_password"
}
```

**Response (201):**
```json
{
  "message": "User registered successfully",
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "id": 1,
    "username": "player1",
    "email": "player1@example.com"
  }
}
```

### Login
**POST** `/api/auth/login`

Login with username and password.

**Request Body:**
```json
{
  "username": "player1",
  "password": "secure_password"
}
```

**Response (200):**
```json
{
  "message": "Login successful",
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "id": 1,
    "username": "player1",
    "email": "player1@example.com",
    "balance": 0.5
  }
}
```

### Get Profile
**GET** `/api/auth/profile`

Get current user's profile information.

**Headers:**
```
Authorization: Bearer {access_token}
```

**Response (200):**
```json
{
  "user": {
    "id": 1,
    "username": "player1",
    "email": "player1@example.com",
    "balance": 0.5,
    "created_at": "2024-01-15T10:30:00",
    "wallet": {
      "bitcoin_address": "1A1z7agoat2LWMVQ6QEyJDGM2T1PmYq77X"
    }
  }
}
```

### Change Password
**POST** `/api/auth/change-password`

Change user password.

**Headers:**
```
Authorization: Bearer {access_token}
```

**Request Body:**
```json
{
  "current_password": "old_password",
  "new_password": "new_password"
}
```

**Response (200):**
```json
{
  "message": "Password changed successfully"
}
```

## Payment Endpoints

### Get Wallet
**GET** `/api/payment/wallet`

Get user's Bitcoin wallet information.

**Headers:**
```
Authorization: Bearer {access_token}
```

**Response (200):**
```json
{
  "wallet": {
    "bitcoin_address": "1A1z7agoat2LWMVQ6QEyJDGM2T1PmYq77X",
    "total_received": 0.5,
    "total_sent": 0.0,
    "created_at": "2024-01-15T10:30:00"
  }
}
```

### Get Balance
**GET** `/api/payment/balance`

Get current Bitcoin balance.

**Headers:**
```
Authorization: Bearer {access_token}
```

**Response (200):**
```json
{
  "balance": 0.5,
  "currency": "BTC"
}
```

### Deposit
**POST** `/api/payment/deposit`

Record a Bitcoin deposit transaction.

**Headers:**
```
Authorization: Bearer {access_token}
```

**Request Body:**
```json
{
  "tx_hash": "e3bf3d07d4b0375638d5f1db5cb15050eb9e0480ecb429e38750b2eb4ceced16",
  "amount": 0.05
}
```

**Response (200):**
```json
{
  "message": "Deposit processed successfully",
  "balance": 0.55
}
```

### Withdraw
**POST** `/api/payment/withdraw`

Initiate a Bitcoin withdrawal.

**Headers:**
```
Authorization: Bearer {access_token}
```

**Request Body:**
```json
{
  "to_address": "1A1z7agoat2LWMVQ6QEyJDGM2T1PmYq77Y",
  "amount": 0.1
}
```

**Response (200):**
```json
{
  "message": "Withdrawal initiated",
  "balance": 0.45
}
```

### Get Transactions
**GET** `/api/payment/transactions?limit=50`

Get user's transaction history.

**Headers:**
```
Authorization: Bearer {access_token}
```

**Query Parameters:**
- `limit` (optional, default: 50) - Number of transactions to return

**Response (200):**
```json
{
  "transactions": [
    {
      "id": 1,
      "tx_hash": "e3bf3d07d4b0375638d5f1db5cb15050eb9e0480ecb429e38750b2eb4ceced16",
      "amount": 0.05,
      "type": "deposit",
      "status": "confirmed",
      "confirmations": 3,
      "from_address": "1A1z7agoat2LWMVQ6QEyJDGM2T1PmYq77X",
      "to_address": "1A1z7agoat2LWMVQ6QEyJDGM2T1PmYq77Y",
      "created_at": "2024-01-15T10:30:00"
    }
  ]
}
```

### Get Fee Estimate
**GET** `/api/payment/fee-estimate`

Get current Bitcoin network fees.

**Response (200):**
```json
{
  "fees": {
    "slow": 0.0001,
    "standard": 0.0002,
    "fast": 0.0003
  },
  "unit": "BTC"
}
```

## Betting Endpoints

### Create Bet
**POST** `/api/bets`

Create a new bet.

**Headers:**
```
Authorization: Bearer {access_token}
```

**Request Body:**
```json
{
  "amount": 0.01,
  "odds": 2.5,
  "bet_type": "sports",
  "event_description": "Manchester United vs Liverpool - Home Win"
}
```

**Response (201):**
```json
{
  "message": "Bet created successfully",
  "bet": {
    "id": 1,
    "amount": 0.01,
    "odds": 2.5,
    "potential_payout": 0.025,
    "bet_type": "sports",
    "status": "active",
    "created_at": "2024-01-15T10:30:00"
  }
}
```

### Get Bet
**GET** `/api/bets/{id}`

Get details of a specific bet.

**Headers:**
```
Authorization: Bearer {access_token}
```

**Response (200):**
```json
{
  "bet": {
    "id": 1,
    "amount": 0.01,
    "odds": 2.5,
    "potential_payout": 0.025,
    "bet_type": "sports",
    "event_description": "Manchester United vs Liverpool - Home Win",
    "status": "active",
    "result": null,
    "settled_payout": null,
    "created_at": "2024-01-15T10:30:00",
    "settled_at": null
  }
}
```

### Get User Bets
**GET** `/api/bets/user/all?status=active`

Get all bets for the user.

**Headers:**
```
Authorization: Bearer {access_token}
```

**Query Parameters:**
- `status` (optional) - Filter by status: active, won, lost, cancelled, pending

**Response (200):**
```json
{
  "bets": [
    {
      "id": 1,
      "amount": 0.01,
      "odds": 2.5,
      "potential_payout": 0.025,
      "status": "active",
      "result": null,
      "created_at": "2024-01-15T10:30:00"
    }
  ]
}
```

### Get Active Bets
**GET** `/api/bets/active`

Get all active bets for the user.

**Headers:**
```
Authorization: Bearer {access_token}
```

**Response (200):**
```json
{
  "active_bets": [
    {
      "id": 1,
      "amount": 0.01,
      "odds": 2.5,
      "potential_payout": 0.025,
      "bet_type": "sports",
      "event_description": "Manchester United vs Liverpool - Home Win",
      "created_at": "2024-01-15T10:30:00"
    }
  ]
}
```

### Get Statistics
**GET** `/api/bets/statistics`

Get betting statistics for the user.

**Headers:**
```
Authorization: Bearer {access_token}
```

**Response (200):**
```json
{
  "statistics": {
    "total_bets": 10,
    "won_bets": 6,
    "lost_bets": 4,
    "active_bets": 2,
    "total_wagered": 0.1,
    "total_payout": 0.15,
    "win_rate": 60.0,
    "roi": 50.0
  }
}
```

### Cancel Bet
**POST** `/api/bets/{id}/cancel`

Cancel an active bet.

**Headers:**
```
Authorization: Bearer {access_token}
```

**Response (200):**
```json
{
  "message": "Bet cancelled successfully",
  "balance": 0.5
}
```

## Admin Endpoints

### Settle Bet
**POST** `/api/admin/bets/{id}/settle`

Settle a bet (admin only).

**Headers:**
```
Authorization: Bearer {admin_token}
```

**Request Body:**
```json
{
  "result": "win",
  "payout": 0.025
}
```

**Response (200):**
```json
{
  "message": "Bet settled successfully",
  "bet": {
    "id": 1,
    "result": "win",
    "settled_payout": 0.025
  }
}
```

### List Users
**GET** `/api/admin/users?page=1&per_page=20`

Get all users (admin only).

**Headers:**
```
Authorization: Bearer {admin_token}
```

**Query Parameters:**
- `page` (optional, default: 1) - Page number
- `per_page` (optional, default: 20) - Users per page

**Response (200):**
```json
{
  "users": [
    {
      "id": 1,
      "username": "player1",
      "email": "player1@example.com",
      "balance": 0.5,
      "created_at": "2024-01-15T10:30:00"
    }
  ],
  "total": 100,
  "pages": 5,
  "current_page": 1
}
```

### Get User Details
**GET** `/api/admin/users/{id}`

Get detailed user information (admin only).

**Headers:**
```
Authorization: Bearer {admin_token}
```

**Response (200):**
```json
{
  "user": {
    "id": 1,
    "username": "player1",
    "email": "player1@example.com",
    "balance": 0.5,
    "created_at": "2024-01-15T10:30:00",
    "statistics": {
      "total_bets": 10,
      "won_bets": 6,
      "lost_bets": 4,
      "active_bets": 2,
      "total_wagered": 0.1,
      "total_payout": 0.15,
      "win_rate": 60.0,
      "roi": 50.0
    }
  }
}
```

## Error Responses

All errors follow this format:

```json
{
  "message": "Error description"
}
```

### Common HTTP Status Codes

- `200 OK` - Successful request
- `201 Created` - Resource created
- `400 Bad Request` - Invalid request parameters
- `401 Unauthorized` - Missing or invalid authentication
- `403 Forbidden` - User doesn't have permission
- `404 Not Found` - Resource not found
- `409 Conflict` - Resource already exists
- `500 Internal Server Error` - Server error

## Rate Limiting

Currently no rate limiting is implemented. Production deployments should add:
- Request throttling per user
- IP-based limits
- WebSocket connection limits

## Authentication

All protected endpoints require JWT authentication via the `Authorization` header:

```
Authorization: Bearer {access_token}
```

Tokens expire after 30 days (configurable in config.py).

## CORS

CORS is enabled for all `/api/*` endpoints from all origins in development.

For production, restrict CORS origins in `run.py`:
```python
CORS(app, resources={r"/api/*": {"origins": "https://yourdomain.com"}})
```
