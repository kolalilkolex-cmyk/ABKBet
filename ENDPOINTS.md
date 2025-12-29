# API Endpoints Quick Reference

## Base URL
```
http://localhost:5000/api
```

## Authentication Endpoints

| Method | Endpoint | Auth | Purpose |
|--------|----------|------|---------|
| POST | `/auth/register` | ❌ | Register new user |
| POST | `/auth/login` | ❌ | Login user |
| GET | `/auth/profile` | ✅ | Get user profile |
| POST | `/auth/change-password` | ✅ | Change password |

## Payment Endpoints

| Method | Endpoint | Auth | Purpose |
|--------|----------|------|---------|
| GET | `/payment/wallet` | ✅ | Get wallet info |
| GET | `/payment/balance` | ✅ | Get BTC balance |
| POST | `/payment/deposit` | ✅ | Record deposit |
| POST | `/payment/withdraw` | ✅ | Initiate withdrawal |
| GET | `/payment/transactions` | ✅ | Transaction history |
| GET | `/payment/fee-estimate` | ❌ | Current network fees |

## Betting Endpoints

| Method | Endpoint | Auth | Purpose |
|--------|----------|------|---------|
| POST | `/bets` | ✅ | Create bet |
| GET | `/bets/{id}` | ✅ | Get bet details |
| GET | `/bets/user/all` | ✅ | Get all user bets |
| GET | `/bets/active` | ✅ | Get active bets |
| GET | `/bets/statistics` | ✅ | Get statistics |
| POST | `/bets/{id}/cancel` | ✅ | Cancel bet |

## Admin Endpoints

| Method | Endpoint | Auth | Purpose |
|--------|----------|------|---------|
| POST | `/admin/bets/{id}/settle` | ✅ | Settle bet |
| GET | `/admin/users` | ✅ | List users |
| GET | `/admin/users/{id}` | ✅ | User details |
| GET | `/admin/transactions` | ✅ | List transactions |
| GET | `/admin/statistics` | ✅ | Platform stats |

## Webhook Endpoints

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/webhook/transaction-confirmation` | Transaction confirmation |
| POST | `/webhook/block-confirmation` | Block confirmation |

## Health Check

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/health` | Check server status |

---

## Example Usage

### Register
```bash
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "player1",
    "email": "player@example.com",
    "password": "password123"
  }'
```

### Login
```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "player1",
    "password": "password123"
  }'
```

### Get Wallet (requires token)
```bash
curl -X GET http://localhost:5000/api/payment/wallet \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Create Bet
```bash
curl -X POST http://localhost:5000/api/bets \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 0.01,
    "odds": 2.5,
    "bet_type": "sports",
    "event_description": "Manchester United vs Liverpool"
  }'
```

## Query Parameters

### Get User Bets
```
GET /bets/user/all?status=active
```
Status options: `active`, `won`, `lost`, `cancelled`, `pending`

### Get Transactions
```
GET /payment/transactions?limit=50
```
- `limit` - Number of transactions to return (default: 50)

### List Admin Users
```
GET /admin/users?page=1&per_page=20
```
- `page` - Page number (default: 1)
- `per_page` - Items per page (default: 20)

### List Admin Transactions
```
GET /admin/transactions?page=1&per_page=50&status=confirmed
```
- `page` - Page number (default: 1)
- `per_page` - Items per page (default: 50)
- `status` - Filter by status (pending/confirmed/failed/cancelled)

## Authentication Header

For all endpoints marked with ✅:
```
Authorization: Bearer {your_jwt_token}
```

Example:
```bash
curl -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc..." \
  http://localhost:5000/api/auth/profile
```

## Response Format

### Success Response
```json
{
  "data": {...},
  "message": "Success message"
}
```

### Error Response
```json
{
  "message": "Error message"
}
```

## Status Codes

- `200` - OK
- `201` - Created
- `400` - Bad Request
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Not Found
- `409` - Conflict
- `500` - Internal Server Error

## Total Endpoints Summary

- **Auth**: 4 endpoints
- **Payment**: 6 endpoints
- **Betting**: 6 endpoints
- **Admin**: 5 endpoints
- **Webhooks**: 2 endpoints
- **System**: 1 endpoint (health check)

**Total: 24 main endpoints**

---

For detailed documentation, see `API_DOCUMENTATION.md`
